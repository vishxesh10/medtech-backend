#!/usr/bin/env python3
"""
Railway Deployment Setup Script
Automatically generates and displays all required environment variables
"""

import secrets
import json
import sys
from datetime import datetime

def generate_jwt_secret():
    """Generate a secure JWT secret key"""
    return secrets.token_urlsafe(32)

def generate_bearer_token():
    """Generate a secure API bearer token"""
    return secrets.token_urlsafe(24)

def main():
    print("\n" + "="*60)
    print("🚀 MedTech Backend - Railway Deployment Setup")
    print("="*60 + "\n")
    
    # Generate secrets
    jwt_secret = generate_jwt_secret()
    bearer_token = generate_bearer_token()
    
    # Environment variables for Railway
    env_vars = {
        "JWT_SECRET_KEY": {
            "value": jwt_secret,
            "required": True,
            "description": "Secret key for JWT token signing (CHANGE THIS!)"
        },
        "JWT_ALGORITHM": {
            "value": "HS256",
            "required": True,
            "description": "JWT algorithm"
        },
        "ACCESS_TOKEN_EXPIRE_MINUTES": {
            "value": "10080",
            "required": False,
            "description": "Token expiration (7 days default)"
        },
        "GEMINI_KEY": {
            "value": "",
            "required": True,
            "description": "Google Gemini API key (get from https://aistudio.google.com/apikey)"
        },
        "CORS_ALLOW_ORIGINS": {
            "value": '["https://your-frontend-domain.com"]',
            "required": False,
            "description": "Allowed frontend domains for CORS"
        },
        "HF_TOKEN": {
            "value": "",
            "required": False,
            "description": "Hugging Face token (optional)"
        },
        "API_BEARER_TOKEN": {
            "value": bearer_token,
            "required": False,
            "description": "Optional API bearer token for additional security"
        },
    }
    
    # Display variables
    print("📋 RAILWAY ENVIRONMENT VARIABLES")
    print("-" * 60)
    print("\nCopy these into Railway dashboard Variables section:\n")
    
    for i, (key, info) in enumerate(env_vars.items(), 1):
        required = "✅ REQUIRED" if info["required"] else "⚠️  Optional"
        print(f"{i}. {key} {required}")
        print(f"   Description: {info['description']}")
        if info["value"]:
            print(f"   Value: {info['value']}")
        else:
            print(f"   Value: <FILL IN MANUALLY>")
        print()
    
    # Generate files
    print("-" * 60)
    print("\n📁 GENERATED FILES:")
    print("-" * 60 + "\n")
    
    # .env.production
    env_production = f"""# MedTech Backend - Production Environment Variables for Railway
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# SECURITY WARNING: Keep these values secret! Never commit to git.

# ===== DATABASE =====
# IMPORTANT: Railway automatically sets this when you add PostgreSQL
# Do NOT set this manually - Railway will override it
# DATABASE_URL=postgresql+psycopg://...

# ===== JWT Configuration (CHANGE JWT_SECRET_KEY!) =====
JWT_SECRET_KEY={jwt_secret}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# ===== CORS Configuration =====
# Set to your actual frontend domain in production
CORS_ALLOW_ORIGINS=["https://your-frontend-domain.com"]

# ===== GEMINI API (REQUIRED) =====
# Get your free key from: https://aistudio.google.com/apikey
GEMINI_KEY=

# ===== Optional Variables =====
HF_TOKEN=
API_BEARER_TOKEN={bearer_token}

# ===== Application Info =====
APP_NAME=MedTech API
APP_DESCRIPTION=API for MedTech AI application
APP_VERSION=0.1.0
GEMINI_MODEL=gemini-2.5-flash
"""
    
    with open(".env.production", "w") as f:
        f.write(env_production)
    print("✅ Created .env.production")
    
    # JSON export for easy importing
    json_vars = {
        key: info["value"] 
        for key, info in env_vars.items() 
        if info["value"]
    }
    
    with open("railway-env-vars.json", "w") as f:
        json.dump(json_vars, f, indent=2)
    print("✅ Created railway-env-vars.json (for reference)")
    
    # Quick reference file
    quick_ref = f"""# QUICK REFERENCE - Railway Environment Variables

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Step-by-Step Setup:

1. Go to Railway.app dashboard
2. Create project from medtech-backend repo
3. Add PostgreSQL service (Railway auto-sets DATABASE_URL)
4. Go to Variables tab
5. Add these variables:

JWT_SECRET_KEY={jwt_secret}
CORS_ALLOW_ORIGINS=["https://your-frontend.vercel.app"]
GEMINI_KEY=<GET_FROM_https://aistudio.google.com/apikey>
HF_TOKEN=<OPTIONAL>
API_BEARER_TOKEN={bearer_token}

6. Enable auto-deploy on 'main' branch
7. Done! Backend will auto-deploy

## Important:
- JWT_SECRET_KEY: KEEP THIS SECRET! Don't share.
- GEMINI_KEY: Required for prescription extraction
- CORS_ALLOW_ORIGINS: Change to your actual frontend domain
- DATABASE_URL: Let Railway auto-generate this
"""
    
    with open("RAILWAY_QUICK_REF.txt", "w") as f:
        f.write(quick_ref)
    print("✅ Created RAILWAY_QUICK_REF.txt")
    
    print("\n" + "="*60)
    print("✨ Setup Complete!")
    print("="*60)
    print("\n📚 FILES CREATED:")
    print("  • .env.production - For local reference")
    print("  • railway-env-vars.json - JSON format variables")
    print("  • RAILWAY_QUICK_REF.txt - Quick reference guide")
    print("\n🔐 SECURITY REMINDER:")
    print("  • Never commit .env.production to git")
    print("  • JWT_SECRET_KEY shown above - use in Railway dashboard")
    print("  • Keep GEMINI_KEY secret")
    print("\n📖 Next: Read RAILWAY_SETUP.md for detailed instructions")
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
