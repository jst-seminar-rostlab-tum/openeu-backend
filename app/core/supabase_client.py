import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]

# instantiate directly
supabase: Client = create_client(url, key)




