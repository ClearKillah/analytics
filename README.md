# Telegram Analytics Bot

Бот для анализа статистики Telegram-каналов. Предоставляет данные о популярных каналах, лучших постах, трендах и рекомендации по созданию каналов.

## Функциональность

- **Top 20 Channels**: Показывает топ-20 Telegram-каналов с подробной статистикой
- **15 Best Posts**: Отображает 15 лучших постов в Telegram за сегодня
- **Niche Analysis**: Анализ различных ниш Telegram-каналов
- **New Channels**: Статистика о новых каналах, созданных за последние 24 часа
- **Channel Creation Advice**: Рекомендации по созданию нового Telegram-канала
- **Current Trends**: Анализ текущих трендов в Telegram

## Технологии

- Python 3.12
- python-telegram-bot
- Playwright (для взаимодействия с веб-страницами)
- pandas (для анализа данных)
- aiohttp (для асинхронных HTTP-запросов)

## Установка и запуск

### Локальный запуск

1. Клонировать репозиторий:
```
git clone https://github.com/your-username/telegram-analytics-bot.git
cd telegram-analytics-bot
```

2. Установить зависимости:
```
pip install -r requirements.txt
```

3. Создать файл `.env` в корне проекта и добавить переменные окружения:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEMETR_TOKEN=your_telemetr_token
```

4. Запустить бота:
```
python bot.py
```

### Деплой на Railway

1. Подключить репозиторий к Railway
2. Настроить переменные окружения в настройках проекта:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEMETR_TOKEN`
3. Railway автоматически установит зависимости и запустит бота

## Переменные окружения

- `TELEGRAM_BOT_TOKEN`: Токен вашего Telegram-бота (получить у [@BotFather](https://t.me/BotFather))
- `TELEMETR_TOKEN`: Токен для доступа к API Telemetr (необязателен для демо-режима)

## Features

- 📊 View top 50 Telegram channels with their statistics
- 🔥 Track best performing posts of the day
- 📈 Analyze different niches and their potential
- 💹 Get insights about channel growth and engagement rates

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. The bot token is already configured in the code.

3. Run the bot:
```bash
python bot.py
```

## Usage

1. Start the bot by sending `/start` command
2. Use the inline buttons to:
   - View top 50 channels
   - Check today's best posts
   - Analyze different niches

## Metrics Explained

- **ERR (Engagement Rate Ratio)**: Measures the engagement level of posts relative to the channel's subscriber count
- **Growth Rate**: The percentage increase in subscribers over 24 hours
- **Monetization Potential**: Calculated based on ERR and growth metrics
- **Competition Level**: Based on the number of active channels in the niche

## Notes

- The bot uses web scraping to gather data from TGStat
- All data is fetched in real-time
- Some requests might take a few seconds to process due to data gathering

## Troubleshooting

If you encounter any issues:
1. Make sure you have a stable internet connection
2. Check if TGStat website is accessible
3. Verify that all dependencies are installed correctly
4. Check the logs for any error messages 