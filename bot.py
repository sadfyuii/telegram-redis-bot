import requests
import redis
import time
from threading import Thread

TELEGRAM_TOKEN = "8734791588:AAH3FCV8VF9VK0YcyRkkhf446g8kv-11yMo"
URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

last_update_id = 0

def send_message(chat_id, text):
    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": text})

def handle_message(message):
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    text = message.get('text', '')
    
    if text == '/start':
        send_message(chat_id, "Bot is ready! Send me any message.")
    elif text == '/last':
        last = redis_client.get(f"user:{user_id}:last")
        if last:
            send_message(chat_id, f"Last message: {last}")
        else:
            send_message(chat_id, "No messages yet")
    else:
        redis_client.set(f"user:{user_id}:last", text)
        send_message(chat_id, f"Saved: {text}")

def poll_updates():
    global last_update_id
    while True:
        response = requests.get(f"{URL}/getUpdates", params={"offset": last_update_id + 1, "timeout": 30})
        if response.status_code == 200:
            updates = response.json().get('result', [])
            for update in updates:
                last_update_id = update['update_id']
                if 'message' in update:
                    handle_message(update['message'])
        time.sleep(1)

if __name__ == "__main__":
    print("Bot is running...")
    poll_updates()
