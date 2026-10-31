import json
from instagrapi import Client
from database import get_accounts, supabase

def get_client_for_account(account: dict):
    """
    account dict-এ 'phone' ফিল্ডে username বা phone — যেকোনো একটি থাকতে পারে।
    instagrapi-র login() দুটোই হ্যান্ডেল করে।
    """
    cl = Client()
    if account.get("session_data"):
        try:
            cl.load_settings(json.loads(account["session_data"]))
        except Exception:
            pass

    username_or_phone = account["phone"]
    password = account["password"]

    cl.login(username_or_phone, password)

    # নতুন session Supabase-এ সেভ (বারবার লগইন এড়াতে)
    new_session = json.dumps(cl.get_settings())
    supabase.table("accounts").update(
        {"session_data": new_session}
    ).eq("id", account["id"]).execute()

    return cl

def do_follow(target_username: str, count: int):
    accounts = get_accounts()
    done = 0
    for acc in accounts:
        if done >= count:
            break
        try:
            cl = get_client_for_account(acc)
            user_id = cl.user_id_from_username(target_username)
            cl.user_follow(user_id)
            done += 1
        except Exception:
            continue
    return done

def do_like(post_url: str, count: int):
    accounts = get_accounts()
    done = 0
    for acc in accounts:
        if done >= count:
            break
        try:
            cl = get_client_for_account(acc)
            media_pk = cl.media_pk_from_url(post_url)
            cl.media_like(media_pk)
            done += 1
        except Exception:
            continue
    return done

def do_comment(post_url: str, comment_text: str, count: int):
    accounts = get_accounts()
    done = 0
    for acc in accounts:
        if done >= count:
            break
        try:
            cl = get_client_for_account(acc)
            media_pk = cl.media_pk_from_url(post_url)
            cl.media_comment(media_pk, comment_text)
            done += 1
        except Exception:
            continue
    return done
