"""
Docstring for app_config
"""
import os
from dotenv import load_dotenv

load_dotenv()

# SQL DB CONFIGURATION
DB_USER = os.getenv("supabase_username", "postgres")
DB_PASSWORD = os.getenv("supabase_password", "password")
DB_HOST = os.getenv("supabase_host", "localhost")
DB_PORT = os.getenv("supabase_port", "5432")
DB_NAME = os.getenv("supabase_db", "database")
SUPABASE_KEY = os.getenv("supabase_key", "key")
SUPABASE_SECRET = os.getenv("supabase_secret", "secret")
SUPABASE_SERVICE_ROLE = os.getenv("supabase_service_role", "service_role")
SUPABASE_URL = os.getenv("supabase_url", "url")

# S3 CONFIGURATION
AWS_ACCESS_KEY_ID = os.getenv("aws_access_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("aws_secret_access_key")
AWS_REGION = os.getenv("aws_region")

# CHROMA CONFIGURATION
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT_KEY = os.getenv("CHROMA_TENANT_KEY")
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")

# OPENAI CONFIGURATION
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
