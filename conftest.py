"""
Pytest configuration - MUST run before any app imports
"""
import os
import sys
from pathlib import Path

os.environ['DB_PORT'] = '5432'
os.environ['DB_USER'] = 'test_user'
os.environ['DB_PASSWORD'] = 'test_password'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_NAME'] = 'test_db'
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_SERVICE_ROLE'] = 'test-key'
os.environ['CHROMA_API_KEY'] = 'test-chroma-key'
os.environ['CHROMA_TENANT_KEY'] = 'test-tenant-key'

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
