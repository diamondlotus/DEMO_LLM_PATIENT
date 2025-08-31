import redis
import chromadb

# Redis short-term memory
redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

# ChromaDB long-term memory
chroma_client = chromadb.PersistentClient(path="/chroma")

def save_context(session_id, key, value):
    redis_client.hset(session_id, key, value)

def get_context(session_id, key):
    return redis_client.hget(session_id, key)

