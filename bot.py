import logging
import asyncio
from datetime import datetime
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from telegram.error import TimedOut, NetworkError, RetryAfter
from scraper import TelegramAnalytics
import traceback
import os
import sys
import fcntl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEMETR_TOKEN = os.getenv("TELEMETR_TOKEN")

# Initialize analytics
analytics = None

# Conversation states
WAITING_FOR_TOKEN = 1

# Process lock file
LOCK_FILE = "/tmp/telegram_analytics_bot.lock"

def acquire_lock():
    """Try to acquire a lock file to prevent multiple instances"""
    try:
        # Open or create lock file
        lock_file = open(LOCK_FILE, 'w')
        
        # Try to acquire an exclusive lock
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        # Keep the file handle open
        return lock_file
    except (IOError, OSError) as e:
        logger.error(f"Another instance is already running: {e}")
        return None

def release_lock(lock_file):
    """Release the lock file"""
    if lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
            lock_file.close()
            os.remove(LOCK_FILE)
        except (IOError, OSError) as e:
            logger.error(f"Error releasing lock: {e}")

async def get_analytics():
    """Get or create analytics instance"""
    global analytics
    if analytics is None:
        analytics = TelegramAnalytics(api_token=TELEMETR_TOKEN)
    return analytics

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the bot and show main menu"""
    try:
        # Show main menu
        keyboard = [
            [
                InlineKeyboardButton("📊 Top 20 Channels", callback_data='top_50'),
                InlineKeyboardButton("🔥 15 Best Posts", callback_data='best_posts')
            ],
            [
                InlineKeyboardButton("📈 Niche Analysis", callback_data='niche_analysis'),
                InlineKeyboardButton("📱 New Channels", callback_data='new_channels')
            ],
            [
                InlineKeyboardButton("🚀 Channel Creation Advice", callback_data='channel_advice'),
                InlineKeyboardButton("🔍 Current Trends", callback_data='trends')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "👋 Welcome to Telegram Analytics Bot!\n\n"
            "Due to API limitations, we're currently showing demo data.\n\n"
            "Choose an option:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in start command: {traceback.format_exc()}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong while starting the bot.\n"
            "Please try again later or contact support if the issue persists."
        )
        return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'top_50':
        await get_top_channels(update, context)
    elif query.data == 'best_posts':
        await get_best_posts(update, context)
    elif query.data == 'niche_analysis':
        await get_niche_analysis(update, context)
    elif query.data == 'channel_advice':
        await get_channel_advice(update, context)
    elif query.data == 'trends':
        await get_current_trends(update, context)
    elif query.data == 'new_channels':
        await get_new_channels_stats(update, context)

async def get_top_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get top 20 channels"""
    try:
        # Show loading message
        message = await update.callback_query.message.edit_text(
            "🔄 Fetching top 20 channels...\n"
            "Please wait..."
        )
        
        analytics_instance = await get_analytics()
        channels = await analytics_instance.get_top_channels()
        
        if not channels:
            await message.edit_text(
                "😕 Sorry, I couldn't fetch the channel data at the moment.\n\n"
                "This could be due to:\n"
                "• API maintenance\n"
                "• Temporary access restrictions\n"
                "• Network connectivity issues\n\n"
                "Please try again in a few minutes."
            )
            return
            
        # Format the response for all channels
        response = "📊 Top Telegram Channels:\n\n"
        
        for i, channel in enumerate(channels, 1):
            response += (
                f"{i}. {channel['name']} (@{channel['username']})\n"
                f"👥 {channel['subscribers']} подписчиков\n"
                f"📈 Рост: {channel['growth_24h']} (24ч) | {channel['growth_7d']} (7д)\n"
                f"📊 ERR: {channel['err']}% | 👁 Просмотры: {channel['avg_views']}\n"
                f"📚 Категория: {channel['category']}\n"
                f"📝 Частота постов: {channel['post_frequency']}\n"
                f"💰 Монетизация: {channel['monetization']} | 🥊 Конкуренция: {channel['competition']}\n"
                f"📄 Тип контента: {channel['content_type']}\n\n"
            )
            
        # Split long messages if needed
        if len(response) > 4096:
            parts = []
            for x in range(0, len(channels), 5):
                part_response = "📊 Top Telegram Channels (продолжение):\n\n"
                for i, channel in enumerate(channels[x:x+5], x+1):
                    part_response += (
                        f"{i}. {channel['name']} (@{channel['username']})\n"
                        f"👥 {channel['subscribers']} подписчиков\n"
                        f"📈 Рост: {channel['growth_24h']} (24ч) | {channel['growth_7d']} (7д)\n"
                        f"📊 ERR: {channel['err']}% | 👁 Просмотры: {channel['avg_views']}\n"
                        f"📚 Категория: {channel['category']}\n"
                        f"📝 Частота постов: {channel['post_frequency']}\n"
                        f"💰 Монетизация: {channel['monetization']} | 🥊 Конкуренция: {channel['competition']}\n"
                        f"📄 Тип контента: {channel['content_type']}\n\n"
                    )
                parts.append(part_response)
                
            for i, part in enumerate(parts):
                if i == 0:
                    await message.edit_text(part)
                else:
                    await message.reply_text(part)
        else:
            await message.edit_text(response)
            
    except Exception as e:
        logger.error(f"Error getting top channels: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Sorry, something went wrong while fetching the data.\n"
            "Please try again later."
        )

async def get_best_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get best posts of the day"""
    try:
        # Show loading message
        message = await update.callback_query.message.edit_text(
            "🔄 Fetching today's 15 best posts...\n"
            "Please wait..."
        )
        
        analytics_instance = await get_analytics()
        posts = await analytics_instance.get_best_posts()
        
        if not posts:
            await message.edit_text(
                "😕 Sorry, I couldn't fetch the best posts at the moment.\n\n"
                "This could be due to:\n"
                "• API maintenance\n"
                "• Temporary access restrictions\n"
                "• Network connectivity issues\n\n"
                "Please try again in a few minutes."
            )
            return
            
        # Format the response with enhanced info
        response = "🔥 Today's 15 Best Posts:\n\n"
        for i, post in enumerate(posts[:15], 1):
            response += (
                f"{i}. {post['channel']} {post['channel_size']}\n"
                f"📝 Тема: {post['topic']}\n"
                f"👁 {post['views']} просмотров\n"
                f"🔄 {post['forwards']} репостов\n"
                f"💯 Вовлеченность: {post['engagement']}\n"
                f"🔗 {post['link']}\n\n"
            )
            
        # Split long messages if needed
        if len(response) > 4096:
            parts = []
            for x in range(0, len(posts[:15]), 5):
                part_response = "🔥 Today's Best Posts (продолжение):\n\n"
                for i, post in enumerate(posts[x:x+5], x+1):
                    part_response += (
                        f"{i}. {post['channel']} {post['channel_size']}\n"
                        f"📝 Тема: {post['topic']}\n"
                        f"👁 {post['views']} просмотров\n"
                        f"🔄 {post['forwards']} репостов\n"
                        f"💯 Вовлеченность: {post['engagement']}\n"
                        f"🔗 {post['link']}\n\n"
                    )
                parts.append(part_response)
                
            for i, part in enumerate(parts):
                if i == 0:
                    await message.edit_text(part)
                else:
                    await message.reply_text(part)
        else:
            await message.edit_text(response)
            
    except Exception as e:
        logger.error(f"Error getting best posts: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Sorry, something went wrong while fetching the data.\n"
            "Please try again later."
        )

async def get_niche_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get niche analysis"""
    try:
        # Show loading message
        message = await update.callback_query.message.edit_text(
            "🔄 Analyzing channel niches...\n"
            "Please wait..."
        )
        
        analytics_instance = await get_analytics()
        niches = await analytics_instance.get_niche_analysis()
        
        if not niches:
            await message.edit_text(
                "😕 Sorry, I couldn't fetch the niche data at the moment.\n\n"
                "This could be due to:\n"
                "• API maintenance\n"
                "• Temporary access restrictions\n"
                "• Network connectivity issues\n\n"
                "Please try again in a few minutes."
            )
            return
            
        # Format the response
        response = "📈 Telegram Channel Niches Analysis:\n\n"
        for niche, stats in niches.items():
            response += (
                f"📊 {niche}\n"
                f"ERR: {stats['avg_err']}%\n"
                f"Growth Rate: {stats['growth_rate']}%\n"
                f"Monetization: {stats['monetization']}\n"
                f"Competition: {stats['competition']}\n\n"
            )
            
        # Split long messages if needed
        if len(response) > 4096:
            for x in range(0, len(response), 4096):
                if x == 0:
                    await message.edit_text(response[x:x+4096])
                else:
                    await message.reply_text(response[x:x+4096])
        else:
            await message.edit_text(response)
            
    except Exception as e:
        logger.error(f"Error getting niche analysis: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Sorry, something went wrong while fetching the data.\n"
            "Please try again later."
        )

async def get_channel_advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get channel creation advice"""
    try:
        # Show loading message
        message = await update.callback_query.message.edit_text(
            "🔄 Анализируем данные для рекомендаций...\n"
            "Пожалуйста, подождите..."
        )
        
        analytics_instance = await get_analytics()
        channels = await analytics_instance.get_top_channels()
        niches = await analytics_instance.get_niche_analysis()
        
        if not channels or not niches:
            await message.edit_text(
                "😕 Извините, не удалось получить данные для анализа.\n\n"
                "Пожалуйста, попробуйте позже."
            )
            return
        
        # Анализируем категории по ERR, росту и монетизации
        best_categories = []
        for channel in channels:
            cat = channel['category']
            err = float(channel['err'].replace('%', ''))
            growth = int(channel['growth_7d'].replace('+', '').replace(',', ''))
            monetization = channel['monetization']
            competition = channel['competition']
            
            score = 0
            if err > 4.5:
                score += 3
            elif err > 3.5:
                score += 2
            else:
                score += 1
                
            if growth > 5000:
                score += 3
            elif growth > 2000:
                score += 2
            else:
                score += 1
                
            if monetization == 'Высокая':
                score += 3
            elif monetization == 'Средняя':
                score += 2
            else:
                score += 1
                
            if competition == 'Низкая':
                score += 3
            elif competition == 'Средняя':
                score += 2
            else:
                score += 1
                
            best_categories.append({
                'category': cat,
                'score': score,
                'err': err,
                'growth': growth,
                'monetization': monetization,
                'competition': competition
            })
            
        # Сортируем по показателю и выбираем топ-5
        best_categories = sorted(best_categories, key=lambda x: x['score'], reverse=True)
        unique_categories = []
        for cat in best_categories:
            if cat['category'] not in [c['category'] for c in unique_categories]:
                unique_categories.append(cat)
                if len(unique_categories) >= 5:
                    break
        
        # Формируем рекомендации
        response = "🚀 Рекомендации по созданию Telegram канала:\n\n"
        
        response += "🏆 Наиболее перспективные ниши:\n\n"
        for i, cat in enumerate(unique_categories, 1):
            response += (
                f"{i}. {cat['category']}\n"
                f"   • ERR: {cat['err']}%\n"
                f"   • Недельный рост: +{cat['growth']}\n"
                f"   • Потенциал монетизации: {cat['monetization']}\n"
                f"   • Уровень конкуренции: {cat['competition']}\n\n"
            )
        
        # Анализ частоты постов
        post_freq = {}
        for channel in channels:
            cat = channel['category']
            freq = channel['post_frequency']
            if cat not in post_freq:
                post_freq[cat] = []
            post_freq[cat].append(freq)
        
        response += "📝 Оптимальная частота публикаций:\n\n"
        for cat in [c['category'] for c in unique_categories]:
            if cat in post_freq:
                response += f"• {cat}: {max(set(post_freq[cat]), key=post_freq[cat].count)}\n"
        
        response += "\n🎯 Общие рекомендации:\n\n"
        response += (
            "1. Выберите нишу с балансом между монетизацией и конкуренцией\n"
            "2. Поддерживайте регулярность публикаций\n"
            "3. Используйте разнообразные форматы контента\n"
            "4. Отслеживайте ERR (Engagement Rate) вашего канала\n"
            "5. Взаимодействуйте с аудиторией через опросы и ответы на комментарии\n"
            "6. Продвигайте канал через кросс-постинг в других каналах схожей тематики\n"
            "7. Публикуйте уникальный и полезный контент\n"
            "8. Оптимизируйте время публикаций на основе активности аудитории\n"
        )
        
        # Split long messages if needed
        if len(response) > 4096:
            for x in range(0, len(response), 4096):
                if x == 0:
                    await message.edit_text(response[x:x+4096])
                else:
                    await message.reply_text(response[x:x+4096])
        else:
            await message.edit_text(response)
            
    except Exception as e:
        logger.error(f"Error getting channel advice: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при анализе данных.\n"
            "Пожалуйста, попробуйте позже."
        )

async def get_current_trends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get current trends analysis"""
    try:
        # Show loading message
        message = await update.callback_query.message.edit_text(
            "🔄 Анализируем текущие тренды...\n"
            "Пожалуйста, подождите..."
        )
        
        analytics_instance = await get_analytics()
        trends = await analytics_instance.get_current_trends()
        
        if not trends:
            await message.edit_text(
                "😕 Извините, не удалось получить данные о трендах.\n\n"
                "Пожалуйста, попробуйте позже."
            )
            return
            
        # Format the response
        response = "🔍 Анализ текущих трендов в Telegram:\n\n"
        
        response += "📈 Самые популярные темы:\n"
        for i, topic in enumerate(trends['top_topics'], 1):
            response += (
                f"{i}. {topic['name']}\n"
                f"   • Рост активности: {topic['growth']}\n"
                f"   • Количество постов: {topic['posts_count']}\n\n"
            )
            
        response += "🚀 Растущие форматы контента:\n"
        for i, format_item in enumerate(trends['growing_formats'], 1):
            response += f"{i}. {format_item['format']} (рост: {format_item['growth']})\n"
        
        response += "\n📊 Интересы аудитории:\n"
        for i, interest in enumerate(trends['audience_interests'], 1):
            response += f"{i}. {interest['interest']} ({interest['share']})\n"
            
        response += "\n💡 Вывод: Наибольший рост показывают темы, связанные с "
        response += f"{trends['top_topics'][0]['name']} и {trends['top_topics'][1]['name']}, "
        response += f"а из форматов контента наиболее эффективны {trends['growing_formats'][0]['format']} "
        response += f"и {trends['growing_formats'][1]['format']}."
            
        # Split long messages if needed
        if len(response) > 4096:
            for x in range(0, len(response), 4096):
                if x == 0:
                    await message.edit_text(response[x:x+4096])
                else:
                    await message.reply_text(response[x:x+4096])
        else:
            await message.edit_text(response)
            
    except Exception as e:
        logger.error(f"Error getting trends: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при анализе трендов.\n"
            "Пожалуйста, попробуйте позже."
        )

async def get_new_channels_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get statistics about new channels"""
    try:
        # Show loading message
        message = await update.callback_query.message.edit_text(
            "🔄 Собираем статистику о новых каналах...\n"
            "Пожалуйста, подождите..."
        )
        
        analytics_instance = await get_analytics()
        stats = await analytics_instance.get_new_channels_stats()
        
        if not stats:
            await message.edit_text(
                "😕 Извините, не удалось получить статистику о новых каналах.\n\n"
                "Пожалуйста, попробуйте позже."
            )
            return
            
        # Format the response
        response = "📱 Статистика новых Telegram-каналов за 24 часа:\n\n"
        
        response += f"📊 Всего создано: {stats['total_created_24h']} каналов (рост {stats['growth_rate']})\n\n"
        
        response += "🔍 По категориям:\n"
        for category in stats['by_category']:
            response += f"• {category['category']}: {category['count']} ({category['share']})\n"
            
        response += f"\n📈 Показатели новых каналов:\n"
        response += f"• В среднем {stats['avg_initial_posts']} постов при запуске\n"
        response += f"• Средний рост за первую неделю: {stats['avg_growth_first_week']}\n"
        response += f"• Выживаемость: {stats['survival_rate']} каналов продолжают работу после первой недели\n\n"
        
        response += "💡 Топ-3 категории для создания канала сегодня:\n"
        for i in range(3):
            response += f"{i+1}. {stats['by_category'][i]['category']} ({stats['by_category'][i]['share']})\n"
            
        # Split long messages if needed
        if len(response) > 4096:
            for x in range(0, len(response), 4096):
                if x == 0:
                    await message.edit_text(response[x:x+4096])
                else:
                    await message.reply_text(response[x:x+4096])
        else:
            await message.edit_text(response)
            
    except Exception as e:
        logger.error(f"Error getting new channels stats: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при получении статистики.\n"
            "Пожалуйста, попробуйте позже."
        )

async def cleanup():
    """Cleanup resources"""
    if analytics:
        await analytics.close()

def main():
    # Try to acquire the lock
    lock_file = acquire_lock()
    if not lock_file:
        print("Error: Another instance of the bot is already running.")
        sys.exit(1)
        
    try:
        # Create application with increased timeout
        application = (
            Application.builder()
            .token(TELEGRAM_TOKEN)
            .read_timeout(30)
            .write_timeout(30)
            .connect_timeout(30)
            .build()
        )

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))

        # Start the bot with error handling
        try:
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                close_loop=False
            )
        except Exception as e:
            logger.error(f"Error running bot: {traceback.format_exc()}")
        finally:
            # Cleanup resources
            asyncio.get_event_loop().run_until_complete(cleanup())
            
    finally:
        # Always release the lock when the program exits
        release_lock(lock_file)

if __name__ == '__main__':
    main() 