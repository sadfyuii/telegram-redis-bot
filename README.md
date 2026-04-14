cat > README.md << 'EOF'
# 🤖 Telegram Bot with Redis Storage

Telegram bot that saves user messages to Redis database.

## ✨ Features

- 💾 Save any text message to Redis
- 📦 Get last saved message (`/last`)
- 📜 Get last 10 messages (`/history`)
- 🗑️ Clear your data (`/clean`)
- 🎨 Interactive buttons (optional)

## 🛠️ Technologies

- Python 3
- Redis (Docker)
- Telegram Bot API

## 🚀 Quick Start

### 1. Clone repository
```bash
git clone https://github.com/YOUR_USERNAME/telegram-redis-bot.git
cd telegram-redis-bot
