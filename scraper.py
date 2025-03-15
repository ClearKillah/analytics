import aiohttp
import asyncio
import json
import logging
from datetime import datetime, timedelta
import random
from fake_useragent import UserAgent
import traceback
import ssl

class TelegramAnalytics:
    def __init__(self, api_token=None):
        self.api_token = api_token
        self.session = None
        self.user_agent = UserAgent()
        logging.info("Using mock data instead of API calls due to Cloudflare protection")
        
    async def get_top_channels(self):
        """Return mock data for top 20 channels"""
        logging.info("Returning mock data for top 20 channels")
        
        # Sample channel data with extensive metrics
        channels = [
            {
                'name': 'Telegram News',
                'username': 'telegram',
                'subscribers': '1,245,678',
                'growth_24h': '+1,234',
                'growth_7d': '+15,678',
                'err': '4.75',
                'category': 'Новости',
                'post_frequency': '3-5 в день',
                'monetization': 'Высокая',
                'competition': 'Высокая',
                'avg_views': '320,000',
                'avg_forwards': '5,600',
                'content_type': 'Текст + фото'
            },
            {
                'name': 'Durov\'s Channel',
                'username': 'durov',
                'subscribers': '875,432',
                'growth_24h': '+956',
                'growth_7d': '+8,742',
                'err': '6.20',
                'category': 'Технологии',
                'post_frequency': '1-2 в неделю',
                'monetization': 'Высокая',
                'competition': 'Низкая',
                'avg_views': '510,000',
                'avg_forwards': '12,300',
                'content_type': 'Текст'
            },
            {
                'name': 'Бизнес Инсайдер',
                'username': 'businessinsider',
                'subscribers': '678,123',
                'growth_24h': '+785',
                'growth_7d': '+5,640',
                'err': '3.85',
                'category': 'Бизнес',
                'post_frequency': '4-6 в день',
                'monetization': 'Высокая',
                'competition': 'Средняя',
                'avg_views': '180,000',
                'avg_forwards': '3,400',
                'content_type': 'Текст + фото + видео'
            },
            {
                'name': 'IT Новости',
                'username': 'technews',
                'subscribers': '542,876',
                'growth_24h': '+643',
                'growth_7d': '+4,120',
                'err': '4.30',
                'category': 'Технологии',
                'post_frequency': '3 в день',
                'monetization': 'Средняя',
                'competition': 'Высокая',
                'avg_views': '145,000',
                'avg_forwards': '2,800',
                'content_type': 'Текст + фото'
            },
            {
                'name': 'Криптовалюты',
                'username': 'crypto_daily',
                'subscribers': '498,765',
                'growth_24h': '+890',
                'growth_7d': '+6,540',
                'err': '5.10',
                'category': 'Криптовалюты',
                'post_frequency': '7-10 в день',
                'monetization': 'Высокая',
                'competition': 'Высокая',
                'avg_views': '110,000',
                'avg_forwards': '2,100',
                'content_type': 'Текст + графики'
            },
            {
                'name': 'Психология Жизни',
                'username': 'psychology',
                'subscribers': '452,340',
                'growth_24h': '+342',
                'growth_7d': '+2,450',
                'err': '3.45',
                'category': 'Психология',
                'post_frequency': '2 в день',
                'monetization': 'Средняя',
                'competition': 'Средняя',
                'avg_views': '93,000',
                'avg_forwards': '4,200',
                'content_type': 'Текст + инфографика'
            },
            {
                'name': 'Мемы',
                'username': 'memes_daily',
                'subscribers': '423,678',
                'growth_24h': '+1,234',
                'growth_7d': '+8,760',
                'err': '7.80',
                'category': 'Развлечения',
                'post_frequency': '10-15 в день',
                'monetization': 'Средняя',
                'competition': 'Очень высокая',
                'avg_views': '87,000',
                'avg_forwards': '6,500',
                'content_type': 'Фото + видео'
            },
            {
                'name': 'Здоровый Образ Жизни',
                'username': 'health_lifestyle',
                'subscribers': '387,450',
                'growth_24h': '+376',
                'growth_7d': '+2,340',
                'err': '3.90',
                'category': 'Здоровье',
                'post_frequency': '2-3 в день',
                'monetization': 'Высокая',
                'competition': 'Средняя',
                'avg_views': '72,000',
                'avg_forwards': '1,900',
                'content_type': 'Текст + фото + видео'
            },
            {
                'name': 'Путешествия',
                'username': 'travel_world',
                'subscribers': '356,780',
                'growth_24h': '+245',
                'growth_7d': '+1,870',
                'err': '4.20',
                'category': 'Путешествия',
                'post_frequency': '1-2 в день',
                'monetization': 'Высокая',
                'competition': 'Средняя',
                'avg_views': '68,000',
                'avg_forwards': '1,600',
                'content_type': 'Фото + видео'
            },
            {
                'name': 'Кулинария',
                'username': 'cooking',
                'subscribers': '345,210',
                'growth_24h': '+321',
                'growth_7d': '+2,140',
                'err': '5.30',
                'category': 'Еда',
                'post_frequency': '3 в день',
                'monetization': 'Высокая',
                'competition': 'Средняя',
                'avg_views': '83,000',
                'avg_forwards': '3,100',
                'content_type': 'Текст + фото + видео'
            },
            {
                'name': 'Fashion News',
                'username': 'fashion',
                'subscribers': '334,560',
                'growth_24h': '+187',
                'growth_7d': '+1,340',
                'err': '3.75',
                'category': 'Мода',
                'post_frequency': '4-5 в день',
                'monetization': 'Высокая',
                'competition': 'Высокая',
                'avg_views': '61,000',
                'avg_forwards': '1,200',
                'content_type': 'Фото + видео'
            },
            {
                'name': 'Образование',
                'username': 'education',
                'subscribers': '321,450',
                'growth_24h': '+165',
                'growth_7d': '+1,120',
                'err': '2.90',
                'category': 'Образование',
                'post_frequency': '1-2 в день',
                'monetization': 'Средняя',
                'competition': 'Низкая',
                'avg_views': '48,000',
                'avg_forwards': '950',
                'content_type': 'Текст + инфографика'
            },
            {
                'name': 'Спорт',
                'username': 'sports_news',
                'subscribers': '312,780',
                'growth_24h': '+432',
                'growth_7d': '+3,210',
                'err': '4.65',
                'category': 'Спорт',
                'post_frequency': '5-7 в день',
                'monetization': 'Высокая',
                'competition': 'Высокая',
                'avg_views': '73,000',
                'avg_forwards': '2,300',
                'content_type': 'Текст + фото + видео'
            },
            {
                'name': 'Искусство',
                'username': 'art_daily',
                'subscribers': '287,650',
                'growth_24h': '+98',
                'growth_7d': '+745',
                'err': '3.10',
                'category': 'Искусство',
                'post_frequency': '1-2 в день',
                'monetization': 'Низкая',
                'competition': 'Низкая',
                'avg_views': '34,000',
                'avg_forwards': '780',
                'content_type': 'Фото + текст'
            },
            {
                'name': 'Музыка',
                'username': 'music_trends',
                'subscribers': '276,340',
                'growth_24h': '+187',
                'growth_7d': '+1,320',
                'err': '4.40',
                'category': 'Музыка',
                'post_frequency': '3-4 в день',
                'monetization': 'Средняя',
                'competition': 'Высокая',
                'avg_views': '52,000',
                'avg_forwards': '1,600',
                'content_type': 'Аудио + текст'
            },
            {
                'name': 'Наука',
                'username': 'science_news',
                'subscribers': '265,780',
                'growth_24h': '+123',
                'growth_7d': '+870',
                'err': '3.20',
                'category': 'Наука',
                'post_frequency': '2 в день',
                'monetization': 'Низкая',
                'competition': 'Низкая',
                'avg_views': '43,000',
                'avg_forwards': '1,100',
                'content_type': 'Текст + фото'
            },
            {
                'name': 'Финансы',
                'username': 'finance',
                'subscribers': '254,320',
                'growth_24h': '+210',
                'growth_7d': '+1,540',
                'err': '3.85',
                'category': 'Финансы',
                'post_frequency': '3 в день',
                'monetization': 'Высокая',
                'competition': 'Средняя',
                'avg_views': '47,000',
                'avg_forwards': '980',
                'content_type': 'Текст + графики'
            },
            {
                'name': 'Маркетинг',
                'username': 'marketing',
                'subscribers': '243,670',
                'growth_24h': '+176',
                'growth_7d': '+1,230',
                'err': '4.10',
                'category': 'Маркетинг',
                'post_frequency': '2 в день',
                'monetization': 'Высокая',
                'competition': 'Средняя',
                'avg_views': '38,000',
                'avg_forwards': '850',
                'content_type': 'Текст + инфографика'
            },
            {
                'name': 'Книги',
                'username': 'books',
                'subscribers': '232,450',
                'growth_24h': '+87',
                'growth_7d': '+610',
                'err': '3.40',
                'category': 'Литература',
                'post_frequency': '1-2 в день',
                'monetization': 'Низкая',
                'competition': 'Низкая',
                'avg_views': '31,000',
                'avg_forwards': '720',
                'content_type': 'Текст + фото'
            },
            {
                'name': 'Кино и Сериалы',
                'username': 'movies',
                'subscribers': '221,890',
                'growth_24h': '+154',
                'growth_7d': '+1,080',
                'err': '4.50',
                'category': 'Развлечения',
                'post_frequency': '3-4 в день',
                'monetization': 'Средняя',
                'competition': 'Высокая',
                'avg_views': '42,000',
                'avg_forwards': '1,300',
                'content_type': 'Текст + фото + видео'
            }
        ]
        
        return channels
            
    async def get_best_posts(self):
        """Return mock data for best posts"""
        logging.info("Returning mock data for best posts")
        
        # Sample posts data - 15 posts from different channels (mix of popular and less popular)
        posts = [
            {
                'channel': 'Telegram News',
                'channel_size': 'Крупный (1.2M+)',
                'views': '500,000',
                'forwards': '12,345',
                'link': 'https://t.me/telegram/123',
                'topic': 'Анонс новых функций',
                'engagement': 'Высокий'
            },
            {
                'channel': 'Durov\'s Channel',
                'channel_size': 'Крупный (800K+)',
                'views': '450,000',
                'forwards': '10,500',
                'link': 'https://t.me/durov/456',
                'topic': 'Приватность данных',
                'engagement': 'Высокий'
            },
            {
                'channel': 'Crypto News',
                'channel_size': 'Средний (450K+)',
                'views': '320,000',
                'forwards': '8,200',
                'link': 'https://t.me/crypto_news/789',
                'topic': 'Биткоин',
                'engagement': 'Высокий'
            },
            {
                'channel': 'Психология Жизни',
                'channel_size': 'Средний (450K+)',
                'views': '210,000',
                'forwards': '5,600',
                'link': 'https://t.me/psychology/567',
                'topic': 'Саморазвитие',
                'engagement': 'Средний'
            },
            {
                'channel': 'IT Jobs',
                'channel_size': 'Малый (120K+)',
                'views': '95,000',
                'forwards': '4,200',
                'link': 'https://t.me/it_jobs/234',
                'topic': 'Вакансии в IT',
                'engagement': 'Высокий'
            },
            {
                'channel': 'Кулинария',
                'channel_size': 'Средний (340K+)',
                'views': '180,000',
                'forwards': '3,800',
                'link': 'https://t.me/cooking/678',
                'topic': 'Рецепты',
                'engagement': 'Средний'
            },
            {
                'channel': 'Маркетинг',
                'channel_size': 'Малый (240K+)',
                'views': '87,000',
                'forwards': '2,100',
                'link': 'https://t.me/marketing/345',
                'topic': 'Инструменты маркетинга',
                'engagement': 'Средний'
            },
            {
                'channel': 'Мемы',
                'channel_size': 'Средний (420K+)',
                'views': '270,000',
                'forwards': '7,300',
                'link': 'https://t.me/memes_daily/901',
                'topic': 'Мемы',
                'engagement': 'Высокий'
            },
            {
                'channel': 'Книжный клуб',
                'channel_size': 'Малый (150K+)',
                'views': '71,000',
                'forwards': '1,600',
                'link': 'https://t.me/books/432',
                'topic': 'Обзор книги',
                'engagement': 'Средний'
            },
            {
                'channel': 'Travel Tips',
                'channel_size': 'Средний (350K+)',
                'views': '134,000',
                'forwards': '2,900',
                'link': 'https://t.me/travel_world/567',
                'topic': 'Путешествия',
                'engagement': 'Средний'
            },
            {
                'channel': 'Music Channel',
                'channel_size': 'Малый (180K+)',
                'views': '67,000',
                'forwards': '1,400',
                'link': 'https://t.me/music_trends/234',
                'topic': 'Новые релизы',
                'engagement': 'Средний'
            },
            {
                'channel': 'Tech Insights',
                'channel_size': 'Малый (90K+)',
                'views': '38,000',
                'forwards': '3,100',
                'link': 'https://t.me/tech_insights/123',
                'topic': 'Искусственный интеллект',
                'engagement': 'Высокий'
            },
            {
                'channel': 'Здоровье и Фитнес',
                'channel_size': 'Средний (380K+)',
                'views': '145,000',
                'forwards': '2,200',
                'link': 'https://t.me/health_lifestyle/678',
                'topic': 'Фитнес',
                'engagement': 'Средний'
            },
            {
                'channel': 'Фондовый рынок',
                'channel_size': 'Малый (220K+)',
                'views': '83,000',
                'forwards': '1,900',
                'link': 'https://t.me/finance/456',
                'topic': 'Инвестиции',
                'engagement': 'Средний'
            },
            {
                'channel': 'Новый стартап',
                'channel_size': 'Малый (50K+)',
                'views': '42,000',
                'forwards': '3,700',
                'link': 'https://t.me/startup_news/123',
                'topic': 'Инновации',
                'engagement': 'Высокий'
            }
        ]
        
        return posts
            
    async def get_niche_analysis(self):
        """Return mock data for niche analysis"""
        logging.info("Returning mock data for niche analysis")
        
        # Sample niche data
        niches = {
            'News': {
                'avg_err': 5.2,
                'growth_rate': 3.1,
                'monetization': 'High',
                'competition': 'High'
            },
            'Entertainment': {
                'avg_err': 4.8,
                'growth_rate': 2.7,
                'monetization': 'High',
                'competition': 'Medium'
            },
            'Technology': {
                'avg_err': 3.9,
                'growth_rate': 2.3,
                'monetization': 'Medium',
                'competition': 'Medium'
            },
            'Education': {
                'avg_err': 2.5,
                'growth_rate': 1.8,
                'monetization': 'Low',
                'competition': 'Low'
            }
        }
        
        return niches
            
    async def get_current_trends(self):
        """Return mock data for current trends"""
        logging.info("Returning mock data for current trends")
        
        # Sample trends data
        trends = {
            'top_topics': [
                {'name': 'Искусственный интеллект', 'growth': '+210%', 'posts_count': 1240},
                {'name': 'Криптовалюты', 'growth': '+180%', 'posts_count': 980},
                {'name': 'Здоровый образ жизни', 'growth': '+150%', 'posts_count': 870},
                {'name': 'Удаленная работа', 'growth': '+120%', 'posts_count': 760},
                {'name': 'Инвестиции', 'growth': '+110%', 'posts_count': 720}
            ],
            'growing_formats': [
                {'format': 'Короткие видео', 'growth': '+250%'},
                {'format': 'Опросы', 'growth': '+180%'},
                {'format': 'Инфографика', 'growth': '+140%'},
                {'format': 'Аудиосообщения', 'growth': '+120%'},
                {'format': 'Интерактивные элементы', 'growth': '+90%'}
            ],
            'audience_interests': [
                {'interest': 'Образовательный контент', 'share': '28%'},
                {'interest': 'Развлекательный контент', 'share': '24%'},
                {'interest': 'Новостной контент', 'share': '19%'},
                {'interest': 'Финансовый контент', 'share': '16%'},
                {'interest': 'Развитие и карьера', 'share': '13%'}
            ]
        }
        
        return trends
        
    async def get_new_channels_stats(self):
        """Return mock data for new channels statistics"""
        logging.info("Returning mock data for new channels statistics")
        
        # Sample new channels statistics
        new_channels = {
            'total_created_24h': 1240,
            'by_category': [
                {'category': 'Технологии', 'count': 285, 'share': '23%'},
                {'category': 'Криптовалюты', 'count': 218, 'share': '17.6%'},
                {'category': 'Образование', 'count': 186, 'share': '15%'},
                {'category': 'Развлечения', 'count': 174, 'share': '14%'},
                {'category': 'Бизнес', 'count': 152, 'share': '12.3%'},
                {'category': 'Здоровье', 'count': 98, 'share': '7.9%'},
                {'category': 'Другие', 'count': 127, 'share': '10.2%'}
            ],
            'growth_rate': '+15.3%',
            'avg_initial_posts': 3.5,
            'avg_growth_first_week': '+127 подписчиков',
            'survival_rate': '43%'  # Процент каналов, продолжающих публикации после первой недели
        }
        
        return new_channels
            
    async def close(self):
        """Close the session if it exists"""
        if self.session:
            await self.session.close()
            self.session = None 