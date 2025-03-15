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

# Если токены не найдены в переменных окружения, используем дефолтные значения
if not TELEGRAM_TOKEN:
    TELEGRAM_TOKEN = "7355185058:AAHL9oH7eArRZQCaUlRATsUTiWox1sOnJBk"
    logger.warning("TELEGRAM_BOT_TOKEN not found in environment variables. Using default value.")

if not TELEMETR_TOKEN:
    TELEMETR_TOKEN = "DHS93aTkpSFAVc88TZiESbWvNuvsftsO"
    logger.warning("TELEMETR_TOKEN not found in environment variables. Using default value.")

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
        # For Railway, continue anyway
        return None

def release_lock(lock_file):
    """Release the lock file"""
    if lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
            lock_file.close()
            if os.path.exists(LOCK_FILE):
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
        reply_markup = get_main_menu_keyboard()
        await update.message.reply_text(
            "👋 Добро пожаловать в Telegram Analytics Bot!\n\n"
            "В связи с ограничениями API, мы показываем демо-данные.\n\n"
            "Выберите опцию:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in start command: {traceback.format_exc()}")
        await update.message.reply_text(
            "❌ Извините, произошла ошибка при запуске бота.\n"
            "Пожалуйста, попробуйте позже или свяжитесь с поддержкой, если проблема сохраняется."
        )
        return ConversationHandler.END

def get_main_menu_keyboard():
    """Get main menu keyboard markup"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Топ-20 каналов", callback_data='top_50'),
            InlineKeyboardButton("🔥 15 лучших постов", callback_data='best_posts')
        ],
        [
            InlineKeyboardButton("📈 Анализ ниш", callback_data='niche_analysis'),
            InlineKeyboardButton("📱 Новые каналы", callback_data='new_channels')
        ],
        [
            InlineKeyboardButton("🚀 Советы по созданию", callback_data='channel_advice'),
            InlineKeyboardButton("🔍 Текущие тренды", callback_data='trends')
        ],
        [
            InlineKeyboardButton("⏰ Оптимальное время постинга", callback_data='posting_time'),
            InlineKeyboardButton("📝 Идеи для контента", callback_data='content_ideas')
        ],
        [
            InlineKeyboardButton("🔎 Анализ конкурентов", callback_data='competitor_analysis'),
            InlineKeyboardButton("📋 Контент-стратегия", callback_data='content_strategy')
        ],
        [
            InlineKeyboardButton("📊 Сводка за 24ч", callback_data='overall_24h'),
            InlineKeyboardButton("📰 Топовые новости", callback_data='top_news')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_button():
    """Get back button keyboard markup"""
    keyboard = [[InlineKeyboardButton("◀️ Назад в меню", callback_data='back_to_menu')]]
    return InlineKeyboardMarkup(keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back_to_menu':
        reply_markup = get_main_menu_keyboard()
        await query.message.edit_text(
            "👋 Добро пожаловать в Telegram Analytics Bot!\n\n"
            "В связи с ограничениями API, мы показываем демо-данные.\n\n"
            "Выберите опцию:",
            reply_markup=reply_markup
        )
        return
    
    if query.data == 'top_50':
        await get_top_channels(update, context)
    elif query.data == 'best_posts':
        await get_best_posts(update, context)
    elif query.data == 'niche_analysis':
        await get_niche_analysis(update, context)
    elif query.data.startswith('niche_'):
        await show_niche_details(update, context)
    elif query.data == 'channel_advice':
        await get_channel_advice(update, context)
    elif query.data == 'trends':
        await get_current_trends(update, context)
    elif query.data == 'new_channels':
        await get_new_channels_stats(update, context)
    elif query.data == 'posting_time':
        await get_optimal_posting_time(update, context)
    elif query.data == 'content_ideas':
        await get_content_ideas(update, context)
    elif query.data == 'competitor_analysis':
        await get_competitor_analysis(update, context)
    elif query.data == 'content_strategy':
        await get_content_strategy(update, context)
    elif query.data == 'overall_24h':
        await get_overall_24h(update, context)
    elif query.data == 'top_news':
        await get_top_news(update, context)

async def get_top_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get top 20 channels"""
    try:
        # Show loading message
        message = await update.callback_query.message.edit_text(
            "🔄 Загружаем топ-20 каналов...\n"
            "Пожалуйста, подождите..."
        )
        
        analytics_instance = await get_analytics()
        channels = await analytics_instance.get_top_channels()
        
        if not channels:
            await message.edit_text(
                "😕 Извините, не удалось получить данные о каналах.\n\n"
                "Пожалуйста, попробуйте позже.",
                reply_markup=get_back_button()
            )
            return
            
        # Format the response for all channels
        response = "📊 Топ-20 Telegram каналов:\n\n"
        
        for i, channel in enumerate(channels, 1):
            response += (
                f"{i}. {channel['name']} (@{channel['username']})\n"
                f"👥 {channel['subscribers']} подписчиков\n"
                f"📈 Рост: {channel['growth_24h']} (24ч) | {channel['growth_7d']} (7д)\n"
                f"📊 ERR: {channel['err']}% | 👁 {channel['avg_views']} просмотров\n"
                f"📋 Категория: {channel['category']} | 📝 Контент: {channel['content_type']}\n"
                f"📢 Частота постов: {channel['post_frequency']} | 💰 Монетизация: {channel['monetization']}\n"
                f"🔄 Репосты: {channel['avg_forwards']} | 🏆 Конкуренция: {channel['competition']}\n\n"
            )
            
        # Add back button
        await add_back_button(message, response)
            
    except Exception as e:
        logger.error(f"Error getting top channels: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при получении данных.\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=get_back_button()
        )

async def add_back_button(message, text):
    """Add back button to the message"""
    # Split long messages if needed
    if len(text) > 4096:
        parts = []
        for x in range(0, len(text), 4096):
            if x == 0:
                parts.append(text[:4096])
            else:
                parts.append(text[x:x+4096])
                
        for i, part in enumerate(parts):
            if i == 0:
                await message.edit_text(part)
            else:
                sent = await message.reply_text(part)
                if i == len(parts) - 1:
                    await sent.reply_text("Вернуться в главное меню:", reply_markup=get_back_button())
    else:
        await message.edit_text(text, reply_markup=get_back_button())

async def get_best_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get best posts of the day"""
    try:
        # Show loading message
        message = await update.callback_query.message.edit_text(
            "🔄 Загружаем 15 лучших постов...\n"
            "Пожалуйста, подождите..."
        )
        
        analytics_instance = await get_analytics()
        posts = await analytics_instance.get_best_posts()
        
        if not posts:
            await message.edit_text(
                "😕 Извините, не удалось получить данные о лучших постах.\n\n"
                "Пожалуйста, попробуйте позже.",
                reply_markup=get_back_button()
            )
            return
            
        # Format the response with enhanced info
        response = "🔥 Сегодняшние 15 лучших постов:\n\n"
        for i, post in enumerate(posts[:15], 1):
            response += (
                f"{i}. {post['channel']} ({post['channel_size']})\n"
                f"📝 Тема: {post['topic']}\n"
                f"👁 {post['views']} просмотров | 🔄 {post['forwards']} репостов\n"
                f"❤️ {post.get('likes', 'н/д')} лайков | 💬 {post.get('comments', 'н/д')} комментариев\n"
                f"📊 Вовлеченность: {post['engagement']}\n"
                f"⏰ Опубликовано: {post.get('post_date', 'Сегодня')} в {post.get('post_time', 'н/д')}\n"
                f"💡 Краткое содержание: {post.get('summary', 'Недоступно')}\n"
                f"🔗 {post['link']}\n\n"
            )
            
        # Add back button
        await add_back_button(message, response)
            
    except Exception as e:
        logger.error(f"Error getting best posts: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при получении данных.\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=get_back_button()
        )

async def get_niche_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get niche analysis"""
    try:
        # Show loading message
        message = await update.callback_query.message.edit_text(
            "🔄 Анализируем ниши Telegram-каналов...\n"
            "Пожалуйста, подождите..."
        )
        
        analytics_instance = await get_analytics()
        niches = await analytics_instance.get_niche_analysis()
        
        if not niches:
            await message.edit_text(
                "😕 Извините, не удалось получить данные о нишах.\n\n"
                "Пожалуйста, попробуйте позже.",
                reply_markup=get_back_button()
            )
            return
            
        # Создаем клавиатуру с нишами для выбора
        keyboard = []
        row = []
        for i, niche in enumerate(niches.keys()):
            row.append(InlineKeyboardButton(niche, callback_data=f'niche_{i}'))
            if (i + 1) % 2 == 0 or i == len(niches) - 1:
                keyboard.append(row)
                row = []
        
        keyboard.append([InlineKeyboardButton("◀️ Назад в меню", callback_data='back_to_menu')])
        
        # Сохраняем данные о нишах в контексте
        context.user_data['niches'] = niches
        context.user_data['niches_list'] = list(niches.keys())
            
        # Отображаем общую информацию и кнопки для выбора ниши
        response = "📈 Анализ ниш Telegram-каналов:\n\n"
        response += "Выберите нишу для детального анализа:\n"
        
        await message.edit_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
            
    except Exception as e:
        logger.error(f"Error getting niche analysis: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при анализе ниш.\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=get_back_button()
        )

async def show_niche_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed information about a specific niche"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Получаем индекс выбранной ниши
        niche_index = int(query.data.split('_')[1])
        niches = context.user_data.get('niches', {})
        niches_list = context.user_data.get('niches_list', [])
        
        if not niches or niche_index >= len(niches_list):
            await query.message.edit_text(
                "😕 Извините, информация о нише не найдена.\n\n"
                "Пожалуйста, попробуйте позже.",
                reply_markup=get_back_button()
            )
            return
        
        # Получаем данные о выбранной нише
        niche_name = niches_list[niche_index]
        niche_data = niches[niche_name]
        
        # Форматируем подробную информацию о нише
        response = f"📊 Детальный анализ ниши: {niche_name}\n\n"
        
        response += "📈 Основные метрики:\n"
        response += f"• ERR: {niche_data['avg_err']}%\n"
        response += f"• Рост: {niche_data['growth_rate']}%\n"
        response += f"• Монетизация: {niche_data['monetization']}\n"
        response += f"• Конкуренция: {niche_data['competition']}\n\n"
        
        response += "👥 Аудитория:\n"
        response += f"• Возраст: {niche_data['audience']['возраст']}\n"
        response += f"• Интересы: {niche_data['audience']['интересы']}\n"
        response += f"• Активность: {niche_data['audience']['активность']}\n\n"
        
        response += "💡 Показатели вовлеченности:\n"
        response += f"• Просмотры/подписчики: {niche_data['engagement_metrics']['просмотры_к_подписчикам']}\n"
        response += f"• Репосты/просмотры: {niche_data['engagement_metrics']['репосты_к_просмотрам']}\n"
        response += f"• Комментарии/просмотры: {niche_data['engagement_metrics']['комментарии_к_просмотрам']}\n\n"
        
        response += "🚀 Рекомендации по контенту:\n"
        for i, rec in enumerate(niche_data['content_recommendations'], 1):
            response += f"{i}. {rec}\n"
        response += f"\n⏰ Оптимальное время постинга: {niche_data['optimal_posting_time']}\n\n"
        
        # Создаем клавиатуру с кнопками для возврата
        keyboard = [
            [InlineKeyboardButton("◀️ Назад к списку ниш", callback_data='niche_analysis')],
            [InlineKeyboardButton("◀️ Назад в меню", callback_data='back_to_menu')]
        ]
            
        await query.message.edit_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
            
    except Exception as e:
        logger.error(f"Error showing niche details: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при отображении деталей ниши.\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=get_back_button()
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
                "Пожалуйста, попробуйте позже.",
                reply_markup=get_back_button()
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
        
        # Add back button
        await add_back_button(message, response)
            
    except Exception as e:
        logger.error(f"Error getting channel advice: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при анализе данных.\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=get_back_button()
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
                "Пожалуйста, попробуйте позже.",
                reply_markup=get_back_button()
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
            
        # Add back button
        await add_back_button(message, response)
            
    except Exception as e:
        logger.error(f"Error getting trends: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при анализе трендов.\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=get_back_button()
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
                "Пожалуйста, попробуйте позже.",
                reply_markup=get_back_button()
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
            
        # Add back button
        await add_back_button(message, response)
            
    except Exception as e:
        logger.error(f"Error getting new channels stats: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при получении статистики.\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=get_back_button()
        )

async def get_overall_24h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get overall statistics for the last 24 hours"""
    try:
        # Show loading message
        message = await update.callback_query.message.edit_text(
            "🔄 Собираем общую сводку за последние 24 часа...\n"
            "Пожалуйста, подождите..."
        )
        
        analytics_instance = await get_analytics()
        # Получаем данные из разных методов
        top_channels = await analytics_instance.get_top_channels()
        best_posts = await analytics_instance.get_best_posts()
        trends = await analytics_instance.get_current_trends()
        new_channels = await analytics_instance.get_new_channels_stats()
        
        if not all([top_channels, best_posts, trends, new_channels]):
            await message.edit_text(
                "😕 Извините, не удалось получить полную сводку.\n\n"
                "Пожалуйста, попробуйте позже.",
                reply_markup=get_back_button()
            )
            return
            
        # Форматируем общую сводку
        response = "📊 Общая сводка за последние 24 часа:\n\n"
        
        # Статистика по каналам
        top_channel = top_channels[0]
        response += "🏆 Лидеры роста:\n"
        response += f"• Топ канал: {top_channel['name']} (@{top_channel['username']})\n"
        response += f"• Рост: {top_channel['growth_24h']} подписчиков\n"
        response += f"• ERR: {top_channel['err']}%\n\n"
        
        # Статистика по постам
        top_post = best_posts[0]
        response += "📝 Лучший пост:\n"
        response += f"• Канал: {top_post['channel']}\n"
        response += f"• Тема: {top_post['topic']}\n"
        response += f"• Просмотры: {top_post['views']}\n"
        response += f"• Репосты: {top_post['forwards']}\n\n"
        
        # Статистика по трендам
        response += "🔥 Горячие тренды:\n"
        for i, topic in enumerate(trends['top_topics'][:3], 1):
            response += f"• {topic['name']} (рост активности: {topic['growth']})\n"
        response += "\n"
        
        # Статистика по новым каналам
        response += "🆕 Новые каналы:\n"
        response += f"• Создано за 24ч: {new_channels['total_created_24h']}\n"
        response += f"• Самая популярная ниша: {new_channels['by_category'][0]['category']}\n\n"
        
        # Общая активность
        response += "📈 Общая активность в Telegram:\n"
        # Здесь можно добавить расчетные данные на основе имеющейся информации
        response += "• Рост общего количества просмотров: +15.7%\n"
        response += "• Рост активности пользователей: +8.3%\n"
        response += "• Средний ERR по всем каналам: 2.4%\n"
        
        # Add back button
        await add_back_button(message, response)
            
    except Exception as e:
        logger.error(f"Error getting overall stats: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при получении общей сводки.\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=get_back_button()
        )

async def get_top_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get top 10 popular news"""
    try:
        # Show loading message
        message = await update.callback_query.message.edit_text(
            "🔄 Собираем топ-10 самых популярных новостей...\n"
            "Пожалуйста, подождите..."
        )
        
        analytics_instance = await get_analytics()
        best_posts = await analytics_instance.get_best_posts()
        
        if not best_posts:
            await message.edit_text(
                "😕 Извините, не удалось получить топовые новости.\n\n"
                "Пожалуйста, попробуйте позже.",
                reply_markup=get_back_button()
            )
            return
            
        # Фильтруем посты, оставляя только новостные (на основе темы)
        news_posts = [post for post in best_posts if 'новост' in post['topic'].lower() 
                      or 'news' in post['topic'].lower() 
                      or 'событи' in post['topic'].lower()]
        
        # Если новостей не найдено, берем все посты
        if not news_posts:
            news_posts = best_posts
        
        # Форматируем топ-10 новостей
        response = "📰 Топ-10 самых популярных новостей:\n\n"
        
        for i, post in enumerate(news_posts[:10], 1):
            response += (
                f"{i}. {post['channel']}\n"
                f"📝 {post['topic']}\n"
                f"👁 {post['views']} просмотров\n"
                f"🔄 {post['forwards']} репостов\n"
                f"💬 Краткое содержание: {post.get('summary', 'Недоступно')}\n"
                f"🔗 {post['link']}\n\n"
            )
            
        # Add back button
        await add_back_button(message, response)
            
    except Exception as e:
        logger.error(f"Error getting top news: {traceback.format_exc()}")
        await update.callback_query.message.edit_text(
            "❌ Извините, произошла ошибка при получении топовых новостей.\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=get_back_button()
        )

async def cleanup():
    """Cleanup resources"""
    if analytics:
        await analytics.close()

def main():
    """Start the bot"""
    lock_file = acquire_lock()
    
    try:
        logger.info(f"Starting bot with token: {TELEGRAM_TOKEN[:10]}... and Telemetr token: {TELEMETR_TOKEN[:5]}...")
        
        # Print more debug info
        print(f"Starting bot on {datetime.now()} with token: {TELEGRAM_TOKEN}")
        print(f"Using Telemetr token: {TELEMETR_TOKEN}")
        
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
            logger.info("Bot polling started")
            print("Bot polling started successfully!")
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                close_loop=False
            )
        except Exception as e:
            logger.error(f"Error running bot: {traceback.format_exc()}")
            print(f"ERROR RUNNING BOT: {str(e)}")
        finally:
            # Cleanup resources
            asyncio.get_event_loop().run_until_complete(cleanup())
            
    finally:
        # Always release the lock when the program exits
        release_lock(lock_file)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error in main: {traceback.format_exc()}")
        print(f"FATAL ERROR: {str(e)}")
        sys.exit(1) 