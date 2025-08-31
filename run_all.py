#!/usr/bin/env python3
"""
LotusHealth - Main Runner Script
Chạy tất cả các service và khởi tạo database
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

class LotusHealthRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docker_compose_file = self.project_root / "docker-compose-postgres.yml"
        self.services = []
        self.is_running = False
        
    def print_banner(self):
        """In banner khởi động"""
        print("🏥" * 50)
        print("🏥                    LOTUSHEALTH                    🏥")
        print("🏥              Healthcare AI Platform               🏥")
        print("🏥" * 50)
        print()
        
    def check_prerequisites(self):
        """Kiểm tra các yêu cầu cần thiết"""
        print("🔍 Kiểm tra yêu cầu hệ thống...")
        
        # Kiểm tra Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker: {result.stdout.strip()}")
            else:
                print("❌ Docker không được cài đặt hoặc không chạy")
                return False
        except FileNotFoundError:
            print("❌ Docker không được cài đặt")
            return False
            
        # Kiểm tra Docker Compose
        try:
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker Compose: {result.stdout.strip()}")
            else:
                print("❌ Docker Compose không hoạt động")
                return False
        except FileNotFoundError:
            print("❌ Docker Compose không được cài đặt")
            return False
            
        # Kiểm tra file docker-compose
        if not self.docker_compose_file.exists():
            print(f"❌ Không tìm thấy file: {self.docker_compose_file}")
            return False
        else:
            print(f"✅ Docker Compose file: {self.docker_compose_file}")
            
        # Kiểm tra environment variables
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                
        if missing_vars:
            print(f"⚠️  Thiếu environment variables: {', '.join(missing_vars)}")
            print("   Tạo file .env với các biến cần thiết")
            return False
        else:
            print("✅ Environment variables đã được cấu hình")
            
        return True
        
    def start_services(self):
        """Khởi động tất cả services"""
        print("\n🚀 Khởi động LotusHealth services...")
        
        try:
            # Dừng services cũ nếu có
            print("🛑 Dừng services cũ...")
            subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 'down'], 
                         capture_output=True)
            
            # Xóa volumes cũ nếu cần
            if input("\n🗑️  Xóa dữ liệu cũ? (y/N): ").lower() == 'y':
                print("🗑️  Xóa volumes...")
                subprocess.run(['docker-compose', '-f', str(self.docker_compose_file), 'down', '-v'], 
                             capture_output=True)
            
            # Build và khởi động services
            print("🔨 Building services...")
            build_result = subprocess.run([
                'docker-compose', '-f', str(self.docker_compose_file), 'build'
            ], capture_output=True, text=True)
            
            if build_result.returncode != 0:
                print(f"❌ Build failed: {build_result.stderr}")
                return False
                
            print("✅ Build completed successfully")
            
            # Khởi động services
            print("🚀 Starting services...")
            subprocess.run([
                'docker-compose', '-f', str(self.docker_compose_file), 'up', '-d'
            ])
            
            print("✅ Services started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start services: {e}")
            return False
            
    def wait_for_services(self):
        """Chờ các services khởi động hoàn tất"""
        print("\n⏳ Chờ services khởi động...")
        
        services_to_check = [
            ('PostgreSQL', 'postgres', 5432),
            ('Redis', 'redis', 6379),
            ('ChromaDB', 'chromadb', 8001),
            ('Auth Service', 'auth-service', 8001),
            ('Clinic Service', 'clinic-service', 8002),
            ('AI Service', 'ai-service', 8000),
            ('API Gateway', 'api-gateway', 8003),
            ('Frontend', 'frontend', 80)
        ]
        
        for service_name, container_name, port in services_to_check:
            print(f"   🔍 Kiểm tra {service_name}...")
            
            # Chờ container khởi động
            max_wait = 60  # 60 giây
            waited = 0
            
            while waited < max_wait:
                try:
                    # Kiểm tra container status
                    result = subprocess.run([
                        'docker-compose', '-f', str(self.docker_compose_file), 
                        'ps', container_name
                    ], capture_output=True, text=True)
                    
                    if 'Up' in result.stdout:
                        print(f"   ✅ {service_name} đã sẵn sàng")
                        break
                    else:
                        time.sleep(2)
                        waited += 2
                        
                except Exception as e:
                    time.sleep(2)
                    waited += 2
                    
            if waited >= max_wait:
                print(f"   ⚠️  {service_name} chưa sẵn sàng sau {max_wait}s")
                
        print("✅ Tất cả services đã được kiểm tra")
        
    def show_service_status(self):
        """Hiển thị trạng thái các services"""
        print("\n📊 Trạng thái services:")
        
        try:
            result = subprocess.run([
                'docker-compose', '-f', str(self.docker_compose_file), 'ps'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print("❌ Không thể lấy trạng thái services")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
    def show_access_info(self):
        """Hiển thị thông tin truy cập"""
        print("\n🌐 Thông tin truy cập:")
        print("   🏥 Frontend: http://localhost")
        print("   🔗 API Gateway: http://localhost:8003")
        print("   📚 API Documentation: http://localhost:8003/docs")
        print("   🗄️  PostgreSQL: localhost:5432")
        print("   🤖 ChromaDB: http://localhost:8001")
        print("   ⚡ Redis: localhost:6379")
        
        print("\n🔑 Demo Accounts:")
        print("   👨‍💼 Admin: admin / admin123")
        print("   👨‍⚕️  Doctor: dr.smith / doctor123")
        print("   👩‍⚕️  Nurse: nurse.jones / nurse123")
        print("   👩‍💼 Receptionist: receptionist.wilson / receptionist123")
        
    def show_logs(self):
        """Hiển thị logs của services"""
        print("\n📋 Logs của services:")
        
        services = ['postgres', 'auth-service', 'clinic-service', 'ai-service', 'api-gateway']
        
        for service in services:
            print(f"\n🔍 Logs của {service}:")
            try:
                result = subprocess.run([
                    'docker-compose', '-f', str(self.docker_compose_file), 
                    'logs', '--tail=5', service
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(result.stdout)
                else:
                    print(f"   Không thể lấy logs của {service}")
                    
            except Exception as e:
                print(f"   Error: {e}")
                
    def stop_services(self):
        """Dừng tất cả services"""
        print("\n🛑 Dừng services...")
        
        try:
            subprocess.run([
                'docker-compose', '-f', str(self.docker_compose_file), 'down'
            ])
            print("✅ Services đã được dừng")
            
        except Exception as e:
            print(f"❌ Error stopping services: {e}")
            
    def run_interactive(self):
        """Chạy chế độ tương tác"""
        self.is_running = True
        
        while self.is_running:
            print("\n" + "="*50)
            print("🏥 LotusHealth Control Panel")
            print("="*50)
            print("1. 🔍 Kiểm tra trạng thái services")
            print("2. 📋 Xem logs")
            print("3. 🔄 Restart services")
            print("4. 🛑 Dừng services")
            print("5. 🌐 Mở frontend trong browser")
            print("6. 📚 Mở API docs trong browser")
            print("7. 🗄️  Kiểm tra database")
            print("0. 🚪 Thoát")
            print("="*50)
            
            choice = input("Chọn tùy chọn (0-7): ").strip()
            
            if choice == '1':
                self.show_service_status()
            elif choice == '2':
                self.show_logs()
            elif choice == '3':
                print("🔄 Restarting services...")
                self.stop_services()
                time.sleep(2)
                self.start_services()
                self.wait_for_services()
            elif choice == '4':
                self.stop_services()
                self.is_running = False
            elif choice == '5':
                print("🌐 Mở frontend...")
                subprocess.run(['open', 'http://localhost'])  # macOS
            elif choice == '6':
                print("📚 Mở API docs...")
                subprocess.run(['open', 'http://localhost:8003/docs'])  # macOS
            elif choice == '7':
                self.check_database()
            elif choice == '0':
                print("👋 Tạm biệt!")
                self.is_running = False
            else:
                print("❌ Lựa chọn không hợp lệ")
                
    def check_database(self):
        """Kiểm tra kết nối database"""
        print("\n🗄️  Kiểm tra database...")
        
        try:
            # Kiểm tra PostgreSQL
            result = subprocess.run([
                'docker-compose', '-f', str(self.docker_compose_file), 
                'exec', 'postgres', 'pg_isready', '-U', 'postgres'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PostgreSQL: Sẵn sàng")
            else:
                print("❌ PostgreSQL: Không sẵn sàng")
                
            # Kiểm tra ChromaDB
            import requests
            try:
                response = requests.get('http://localhost:8001/api/v1/heartbeat', timeout=5)
                if response.status_code == 200:
                    print("✅ ChromaDB: Sẵn sàng")
                else:
                    print("❌ ChromaDB: Không sẵn sàng")
            except:
                print("❌ ChromaDB: Không thể kết nối")
                
            # Kiểm tra Redis
            try:
                result = subprocess.run([
                    'docker-compose', '-f', str(self.docker_compose_file), 
                    'exec', 'redis', 'redis-cli', 'ping'
                ], capture_output=True, text=True)
                
                if 'PONG' in result.stdout:
                    print("✅ Redis: Sẵn sàng")
                else:
                    print("❌ Redis: Không sẵn sàng")
            except:
                print("❌ Redis: Không thể kết nối")
                
        except Exception as e:
            print(f"❌ Error checking database: {e}")
            
    def signal_handler(self, signum, frame):
        """Xử lý signal để dừng services"""
        print("\n\n🛑 Nhận signal dừng...")
        self.stop_services()
        sys.exit(0)
        
    def run(self):
        """Chạy chính của ứng dụng"""
        self.print_banner()
        
        # Đăng ký signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Kiểm tra prerequisites
        if not self.check_prerequisites():
            print("\n❌ Không thể khởi động do thiếu yêu cầu")
            return
            
        # Khởi động services
        if not self.start_services():
            print("\n❌ Không thể khởi động services")
            return
            
        # Chờ services khởi động
        self.wait_for_services()
        
        # Hiển thị thông tin truy cập
        self.show_access_info()
        
        # Chạy chế độ tương tác
        self.run_interactive()

def main():
    """Main function"""
    runner = LotusHealthRunner()
    runner.run()

if __name__ == "__main__":
    main()
