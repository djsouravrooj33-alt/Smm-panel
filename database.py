import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# টেবিল স্ট্রাকচার (Supabase SQL Editor-এ একবার রান করবেন):
# CREATE TABLE users (user_id BIGINT PRIMARY KEY, balance INT DEFAULT 0);
# CREATE TABLE admins (user_id BIGINT PRIMARY KEY);
# CREATE TABLE accounts (id SERIAL PRIMARY KEY, phone TEXT, password TEXT, session_data TEXT);
# CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT); -- upi_pic, upi_id

def get_balance(user_id: int) -> int:
    res = supabase.table("users").select("balance").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]["balance"]
    supabase.table("users").insert({"user_id": user_id, "balance": 0}).execute()
    return 0

def add_balance(user_id: int, amount: int):
    current = get_balance(user_id)
    supabase.table("users").update({"balance": current + amount}).eq("user_id", user_id).execute()

def is_admin(user_id: int, owner_id: int) -> bool:
    if user_id == owner_id:
        return True
    res = supabase.table("admins").select("user_id").eq("user_id", user_id).execute()
    return len(res.data) > 0

def add_admin(user_id: int):
    supabase.table("admins").insert({"user_id": user_id}).execute()

def get_accounts():
    return supabase.table("accounts").select("*").execute().data

def add_account(phone, password, session_data=""):
    supabase.table("accounts").insert({"phone": phone, "password": password, "session_data": session_data}).execute()

def remove_account(phone, password):
    supabase.table("accounts").delete().eq("phone", phone).eq("password", password).execute()

def get_setting(key: str):
    res = supabase.table("settings").select("value").eq("key", key).execute()
    return res.data[0]["value"] if res.data else None

def set_setting(key: str, value: str):
    supabase.table("settings").upsert({"key": key, "value": value}).execute()
