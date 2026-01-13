"""
Docstring for app_config
"""
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("supabase_username")
DB_PASSWORD = os.getenv("supabase_password")
DB_HOST = os.getenv("supabase_host")
DB_PORT = os.getenv("supabase_port")
DB_NAME = os.getenv("supabase_db")
SUPABASE_KEY = os.getenv("supabase_key")
SUPABASE_SECRET = os.getenv("supabase_secret")
SUPABASE_SERVICE_ROLE = os.getenv("supabase_service_role")
SUPABASE_URL = os.getenv("supabase_url")
