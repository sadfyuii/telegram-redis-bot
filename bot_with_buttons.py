import requests
import redis
import time
import json

TELEGRAM_TOKEN = "8734791588:AAH3FCV8VF9VK0YcyRkkhf446g8kv-11yMo"
URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

last_update_id = 0

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(f"{URL}/sendMessage", json=data)

def send_buttons(chat_id):
    keyboard = {
        "keyboard": [
            [{"text": "📦 Last Message"}, {"text": "📜 History"}],
            [{"text": "🗑️ Clear"}, {"text": "❓ Help"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    send_message(chat_id, "Choose an option:", {"keyboard": keyboard, "resize_keyboard": True})

def remove_buttons(chat_id):
    keyboard = {
        "keyboard": [[]],
        "remove_keyboard": True
    }
    send_message(chat_id, "Keyboard removed", {"keyboard": keyboard, "remove_keyboard": True})

def handle_message(message):
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    text = message.get('text', '')
    
    if text == '/start':
        send_message(chat_id, "Bot is ready! Send me any message or use buttons below.")
        send_buttons(chat_id)
    
    elif text == '/last' or text == "📦 Last Message":
        last = redis_client.get(f"user:{user_id}:last")
        if last:
            send_message(chat_id, f"📦 Last message: {last}")
        else:
            send_message(chat_id, "❌ No messages yet")
    
    elif text == '/history' or text == "📜 History":
        history = redis_client.lrange(f"user:{user_id}:history", 0, -1)
        if history:
            messages = "\n".join([f"{i+1}. {msg}" for i, msg in enumerate(history)])
            send_message(chat_id, f"📜 Last {len(history)} messages:\n\n{messages}")
        else:
            send_message(chat_id, "❌ No history yet")
    
    elif text == '/clean' or text == "🗑️ Clear":
        redis_client.delete(f"user:{user_id}:last")
        redis_client.delete(f"user:{user_id}:history")
        send_message(chat_id, "🗑️ All your data cleared!")
    
    elif text == '/help' or text == "❓ Help":
        send_message(chat_id, "Commands:\n/last - last message\n/history - last 10 messages\n/clean - clear all data\n/hide - hide keyboard")
        send_buttons(chat_id)
    
    elif text == '/hide':
        remove_buttons(chat_id)
    
    else:
        redis_client.set(f"user:{user_id}:last", text)
        redis_client.lpush(f"user:{user_id}:history", text)
        redis_client.ltrim(f"user:{user_id}:history", 0, 9)
        send_message(chat_id, f"✅ Saved: {text[:50]}")

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
    print("Bot is running with buttons...")
    poll_updates()
