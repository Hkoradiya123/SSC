#!/usr/bin/env python
"""
SSC Project Setup Verification Script
Verifies that all required files and dependencies are in place
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description=""):
    """Check if a file exists"""
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    desc = f" - {description}" if description else ""
    print(f"{status} {file_path}{desc}")
    return exists

def check_directory_exists(dir_path, description=""):
    """Check if a directory exists"""
    exists = os.path.isdir(dir_path)
    status = "✅" if exists else "❌"
    desc = f" - {description}" if description else ""
    print(f"{status} {dir_path}{desc}")
    return exists

def verify_project_structure():
    """Verify the complete project structure"""
    
    print("\n" + "="*60)
    print("🔍 SSC PROJECT STRUCTURE VERIFICATION")
    print("="*60 + "\n")
    
    all_good = True
    
    # Root files
    print("📁 Root Directory Files:")
    all_good &= check_file_exists("README.md", "Main documentation")
    all_good &= check_file_exists("QUICK_START.md", "Quick start guide")
    all_good &= check_file_exists("API_DOCUMENTATION.md", "API docs")
    all_good &= check_file_exists("PROJECT_STRUCTURE.md", "Project structure")
    all_good &= check_file_exists("FEATURES_CHECKLIST.md", "Features list")
    all_good &= check_file_exists("docker-compose.yml", "Docker compose")
    all_good &= check_file_exists(".gitignore", "Git ignore")
    
    # Backend structure
    print("\n📦 Backend Files:")
    all_good &= check_directory_exists("backend", "Backend directory")
    all_good &= check_file_exists("backend/main.py", "FastAPI entry point")
    all_good &= check_file_exists("backend/requirements.txt", "Python dependencies")
    all_good &= check_file_exists("backend/.env", "Environment config")
    all_good &= check_file_exists("backend/.env.example", "Example env")
    all_good &= check_file_exists("backend/Dockerfile", "Docker config")
    all_good &= check_file_exists("backend/load_test_data.py", "Test data loader")
    
    # Backend app
    print("\n📂 Backend App Structure:")
    all_good &= check_directory_exists("backend/app", "App directory")
    all_good &= check_file_exists("backend/app/config.py", "Configuration")
    all_good &= check_file_exists("backend/app/database.py", "Database setup")
    
    # Models
    print("\n🗄️  Database Models:")
    all_good &= check_directory_exists("backend/app/models", "Models directory")
    all_good &= check_file_exists("backend/app/models/user.py", "User model")
    all_good &= check_file_exists("backend/app/models/payment.py", "Payment model")
    all_good &= check_file_exists("backend/app/models/performance_log.py", "Performance model")
    all_good &= check_file_exists("backend/app/models/notification.py", "Notification model")
    
    # Routes
    print("\n🛣️  API Routes:")
    all_good &= check_directory_exists("backend/app/routes", "Routes directory")
    all_good &= check_file_exists("backend/app/routes/auth.py", "Auth routes")
    all_good &= check_file_exists("backend/app/routes/players.py", "Player routes")
    all_good &= check_file_exists("backend/app/routes/premium.py", "Premium routes")
    all_good &= check_file_exists("backend/app/routes/performance.py", "Performance routes")
    all_good &= check_file_exists("backend/app/routes/dashboard.py", "Dashboard routes")
    all_good &= check_file_exists("backend/app/routes/admin.py", "Admin routes")
    
    # Schemas
    print("\n📋 Request/Response Schemas:")
    all_good &= check_directory_exists("backend/app/schemas", "Schemas directory")
    all_good &= check_file_exists("backend/app/schemas/user.py", "User schemas")
    all_good &= check_file_exists("backend/app/schemas/payment.py", "Payment schemas")
    all_good &= check_file_exists("backend/app/schemas/performance.py", "Performance schemas")
    all_good &= check_file_exists("backend/app/schemas/notification.py", "Notification schemas")
    
    # Utils
    print("\n🛠️  Utilities:")
    all_good &= check_directory_exists("backend/app/utils", "Utils directory")
    all_good &= check_file_exists("backend/app/utils/auth.py", "Auth utilities")
    all_good &= check_file_exists("backend/app/utils/premium.py", "Premium utilities")
    all_good &= check_file_exists("backend/app/utils/logger.py", "Logger utilities")
    
    # Middleware
    print("\n⚙️  Middleware:")
    all_good &= check_directory_exists("backend/app/middleware", "Middleware directory")
    all_good &= check_file_exists("backend/app/middleware/__init__.py", "Rate limiting & logging")
    all_good &= check_file_exists("backend/app/middleware/auth.py", "Auth middleware")
    
    # Frontend
    print("\n⚛️  Frontend Files:")
    all_good &= check_directory_exists("frontend", "Frontend directory")
    all_good &= check_file_exists("frontend/package.json", "Node dependencies")
    all_good &= check_file_exists("frontend/vite.config.js", "Vite config")
    all_good &= check_file_exists("frontend/index.html", "HTML template")
    all_good &= check_file_exists("frontend/.env", "Frontend env")
    all_good &= check_file_exists("frontend/.env.example", "Example env")
    all_good &= check_file_exists("frontend/Dockerfile", "Docker config")
    
    # Frontend src
    print("\n📂 Frontend Source Code:")
    all_good &= check_directory_exists("frontend/src", "Src directory")
    all_good &= check_file_exists("frontend/src/main.jsx", "React entry")
    all_good &= check_file_exists("frontend/src/App.jsx", "App component")
    
    # Components
    print("\n🧩 React Components:")
    all_good &= check_directory_exists("frontend/src/components", "Components dir")
    all_good &= check_file_exists("frontend/src/components/Navbar.jsx", "Navbar component")
    
    # Pages
    print("\n📄 React Pages:")
    all_good &= check_directory_exists("frontend/src/pages", "Pages dir")
    all_good &= check_file_exists("frontend/src/pages/Home.jsx", "Home page")
    all_good &= check_file_exists("frontend/src/pages/Auth.jsx", "Auth pages")
    all_good &= check_file_exists("frontend/src/pages/Dashboard.jsx", "Dashboard page")
    all_good &= check_file_exists("frontend/src/pages/Players.jsx", "Players page")
    all_good &= check_file_exists("frontend/src/pages/Profile.jsx", "Profile page")
    
    # Utils & Styles
    print("\n🎨 Frontend Utils & Styles:")
    all_good &= check_directory_exists("frontend/src/utils", "Utils dir")
    all_good &= check_file_exists("frontend/src/utils/api.js", "API service")
    all_good &= check_directory_exists("frontend/src/styles", "Styles dir")
    all_good &= check_file_exists("frontend/src/styles/global.css", "Global styles")
    all_good &= check_file_exists("frontend/src/styles/theme.js", "Theme config")
    
    return all_good

def print_summary():
    """Print project summary"""
    print("\n" + "="*60)
    print("📊 PROJECT SUMMARY")
    print("="*60 + "\n")
    
    print("✨ Complete SSC Application Created!")
    print("\n🔧 Backend (FastAPI):")
    print("  • 6 API route modules")
    print("  • 4 SQLAlchemy models")
    print("  • 4 Pydantic schema modules")
    print("  • Middleware for auth, rate limiting, logging")
    print("  • Utility functions for all features")
    
    print("\n⚛️  Frontend (React):")
    print("  • 5 main pages (Home, Auth, Dashboard, Players, Profile)")
    print("  • 1 reusable navbar component")
    print("  • CSS modules for styling")
    print("  • Axios API client")
    print("  • React Router v6 for navigation")
    
    print("\n📚 Documentation:")
    print("  • README.md (3000+ words)")
    print("  • API_DOCUMENTATION.md (2500+ words)")
    print("  • QUICK_START.md (setup guide)")
    print("  • PROJECT_STRUCTURE.md (architecture)")
    print("  • FEATURES_CHECKLIST.md (50+ features)")
    
    print("\n🎯 Core Features:")
    print("  • User registration & authentication")
    print("  • Player profiles & stats tracking")
    print("  • Performance logging system")
    print("  • Premium subscription (freemium model)")
    print("  • Dashboard with analytics")
    print("  • Leaderboards & rankings")
    print("  • Admin panel")
    print("  • Notifications system")
    print("  • Activity logging")
    print("  • Rate limiting")
    
    print("\n🚀 Next Steps:")
    print("  1. cd backend")
    print("  2. python -m venv venv && source venv/bin/activate")
    print("  3. pip install -r requirements.txt")
    print("  4. python load_test_data.py")
    print("  5. python -m uvicorn main:app --reload")
    print("\n  Then in another terminal:")
    print("  1. cd frontend")
    print("  2. npm install")
    print("  3. npm run dev")
    
    print("\n📖 See QUICK_START.md for detailed setup instructions")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    all_good = verify_project_structure()
    
    if all_good:
        print("\n✅ All project files verified successfully!\n")
        print_summary()
    else:
        print("\n⚠️  Some files are missing. Please check the above list.\n")
        sys.exit(1)
