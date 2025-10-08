import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("url")
key = os.getenv("key")

supabase: Client = create_client(url, key)