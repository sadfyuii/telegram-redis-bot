# 🤖 Telegram Bot with Redis + Web Admin Panel

Telegram bot that saves messages to Redis with a beautiful web dashboard.

## Features

- Save messages to Redis
- Get last message (`/last`)
- Get history (`/history`)
- Clear data (`/clean`)
- Interactive buttons
- Web admin panel with real-time stats
- REST API for data access

## Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/sadfyuii/telegram-redis-bot.git
cd telegram-redis-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
