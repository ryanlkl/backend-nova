"""
Docstring for app_config
"""
import os
from dotenv import load_dotenv

load_dotenv()

# SQL DB CONFIGURATION
DB_USER = os.getenv("supabase_username")
DB_PASSWORD = os.getenv("supabase_password")
DB_HOST = os.getenv("supabase_host")
DB_PORT = os.getenv("supabase_port")
DB_NAME = os.getenv("supabase_db")
SUPABASE_KEY = os.getenv("supabase_key")
SUPABASE_SECRET = os.getenv("supabase_secret")
SUPABASE_SERVICE_ROLE = os.getenv("supabase_service_role")
SUPABASE_URL = os.getenv("supabase_url")

# S3 CONFIGURATION
AWS_ACCESS_KEY_ID = os.getenv("aws_access_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("aws_secret_access_key")
AWS_REGION = os.getenv("aws_region")

# CHROMA CONFIGURATION
CHROMA_API_KEY = os.getenv("chroma_api_key")
CHROMA_TENANT_KEY = os.getenv("chroma_tenant_key")
CHROMA_HOST = os.getenv("chroma_host")
CHROMA_PORT = os.getenv("chroma_port")

# OPENAI CONFIGURATION
OPENAI_API_KEY = os.getenv("openai_api_key")
