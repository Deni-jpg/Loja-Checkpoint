import os
from supabase import create_client, Client

url: str = os.environ.get("https://myzgukyibcwevlnayxnm.supabase.co")
key: str = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im15emd1a3lpYmN3ZXZsbmF5eG5tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk5MTQwMDAsImV4cCI6MjA3NTQ5MDAwMH0.QqTGPMdThsP-skC6elLHSoI4bOGZgWDxp8L5rbEcwRI")
supabase: Client = create_client(url, key)