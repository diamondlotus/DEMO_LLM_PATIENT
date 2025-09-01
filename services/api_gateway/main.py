from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
import jwt
from typing import Optional
import os

app = FastAPI(title="LotusHealth API Gateway", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs (configurable via environment variables)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
CLINIC_SERVICE_URL = os.getenv("CLINIC_SERVICE_URL", "http://clinic-service:8002")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8000")  # Original AI service

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Should match auth service
ALGORITHM = "HS256"

# HTTP client
http_client = httpx.AsyncClient(timeout=30.0)

async def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return user info"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

async def get_current_user(request: Request) -> Optional[dict]:
    """Extract and verify user from request headers"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    return await verify_token(token)

async def forward_request(service_url: str, path: str, method: str, request: Request, user: Optional[dict] = None):
    """Forward request to appropriate microservice"""
    try:
        # Prepare headers
        headers = dict(request.headers)
        if user:
            headers["X-User-ID"] = user.get("sub", "")
            headers["X-User-Role"] = user.get("role", "")
        
        # Remove host header to avoid conflicts
        headers.pop("host", None)
        
        # Get request body if it exists
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
            except:
                pass
        
        # Make request to microservice
        url = f"{service_url}{path}"
        
        if method == "GET":
            response = await http_client.get(url, headers=headers, params=request.query_params)
        elif method == "POST":
            response = await http_client.post(url, headers=headers, content=body)
        elif method == "PUT":
            response = await http_client.put(url, headers=headers, content=body)
        elif method == "DELETE":
            response = await http_client.delete(url, headers=headers)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")
        
        return response
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check health of all microservices"""
    services_status = {}
    
    # Check auth service
    try:
        auth_response = await http_client.get(f"{AUTH_SERVICE_URL}/health")
        services_status["auth_service"] = "healthy" if auth_response.status_code == 200 else "unhealthy"
    except:
        services_status["auth_service"] = "unavailable"
    
    # Check clinic service
    try:
        clinic_response = await http_client.get(f"{CLINIC_SERVICE_URL}/health")
        services_status["clinic_service"] = "healthy" if clinic_response.status_code == 200 else "unhealthy"
    except:
        services_status["clinic_service"] = "unavailable"
    
    # Check AI service
    try:
        ai_response = await http_client.get(f"{AI_SERVICE_URL}/health")
        services_status["ai_service"] = "healthy" if ai_response.status_code == 200 else "unhealthy"
    except:
        services_status["ai_service"] = "unavailable"
    
    return {
        "status": "healthy",
        "service": "LotusHealth API Gateway",
        "services": services_status
    }

# Auth service routes
@app.post("/auth/{path:path}")
async def auth_service_proxy(path: str, request: Request):
    """Proxy requests to auth service"""
    return await forward_request(AUTH_SERVICE_URL, f"/{path}", request.method, request)

@app.get("/auth/{path:path}")
async def auth_service_get_proxy(path: str, request: Request):
    """Proxy GET requests to auth service"""
    return await forward_request(AUTH_SERVICE_URL, f"/{path}", "GET", request)

# Clinic service routes
@app.post("/clinic/{path:path}")
async def clinic_service_proxy(path: str, request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Proxy requests to clinic service (requires authentication)"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return await forward_request(CLINIC_SERVICE_URL, f"/{path}", request.method, request, user)

@app.get("/clinic/{path:path}")
async def clinic_service_get_proxy(path: str, request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Proxy GET requests to clinic service (requires authentication)"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return await forward_request(CLINIC_SERVICE_URL, f"/{path}", "GET", request, user)

@app.put("/clinic/{path:path}")
async def clinic_service_put_proxy(path: str, request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Proxy PUT requests to clinic service (requires authentication)"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return await forward_request(CLINIC_SERVICE_URL, f"/{path}", "PUT", request, user)

@app.delete("/clinic/{path:path}")
async def clinic_service_delete_proxy(path: str, request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Proxy DELETE requests to clinic service (requires authentication)"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return await forward_request(CLINIC_SERVICE_URL, f"/{path}", "DELETE", request, user)

# AI service routes (original multi-agent service)
@app.post("/ai/{path:path}")
async def ai_service_proxy(path: str, request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Proxy requests to AI service (requires authentication)"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return await forward_request(AI_SERVICE_URL, f"/{path}", request.method, request, user)

@app.get("/ai/{path:path}")
async def ai_service_get_proxy(path: str, request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Proxy GET requests to AI service (requires authentication)"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return await forward_request(AI_SERVICE_URL, f"/{path}", "GET", request, user)

# Root redirect to docs
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    print("🚀 API Gateway starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()
    print("🛑 API Gateway shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
