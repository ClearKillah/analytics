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
        
        posts = [
            {
                'channel': 'IT and Programming',
                'channel_size': '450K subscribers',
                'topic': 'Новые технологии в AI',
                'views': '245,600',
                'forwards': '12,340',
                'engagement': '4.5%',
                'likes': '9,870',
                'comments': '1,234',
                'link': 'https://t.me/itprogramming/1234',
                'post_time': '09:30',
                'post_date': 'Today',
                'summary': 'Обзор последних достижений в области искусственного интеллекта, включая новые модели GPT-4o, Claude 3.7 и Gemini Pro.'
            },
            {
                'channel': 'Business Daily',
                'channel_size': '820K subscribers',
                'topic': 'Финансовая аналитика',
                'views': '196,800',
                'forwards': '8,970',
                'engagement': '3.8%',
                'likes': '7,640',
                'comments': '832',
                'link': 'https://t.me/businessdaily/5678',
                'post_time': '10:15',
                'post_date': 'Today',
                'summary': 'Анализ текущей ситуации на финансовых рынках, прогнозы по ключевым активам и рекомендации по инвестированию.'
            },
            {
                'channel': 'World News',
                'channel_size': '1.2M subscribers',
                'topic': 'Международные новости',
                'views': '732,150',
                'forwards': '23,456',
                'engagement': '5.2%',
                'likes': '18,734',
                'comments': '2,345',
                'link': 'https://t.me/worldnews/9012',
                'post_time': '08:45',
                'post_date': 'Today',
                'summary': 'Главные мировые новости: международные соглашения, политические события и главные заявления мировых лидеров.'
            },
            {
                'channel': 'Tech Reviews',
                'channel_size': '390K subscribers',
                'topic': 'Обзор iPhone 16',
                'views': '184,700',
                'forwards': '7,820',
                'engagement': '4.0%',
                'likes': '6,540',
                'comments': '987',
                'link': 'https://t.me/techreviews/3456',
                'post_time': '12:30',
                'post_date': 'Today',
                'summary': 'Подробный обзор нового iPhone 16: технические характеристики, тесты камеры, производительность и сравнение с конкурентами.'
            },
            {
                'channel': 'Crypto News',
                'channel_size': '570K subscribers',
                'topic': 'Анализ рынка криптовалют',
                'views': '218,500',
                'forwards': '9,760',
                'engagement': '4.2%',
                'likes': '8,230',
                'comments': '1,098',
                'link': 'https://t.me/cryptonews/7890',
                'post_time': '11:45',
                'post_date': 'Today',
                'summary': 'Текущее состояние рынка криптовалют, анализ Bitcoin и Ethereum, прогнозы по альткоинам и новости регулирования.'
            },
            {
                'channel': 'Health & Wellness',
                'channel_size': '630K subscribers',
                'topic': 'Новое исследование о питании',
                'views': '165,300',
                'forwards': '6,450',
                'engagement': '3.5%',
                'likes': '5,870',
                'comments': '734',
                'link': 'https://t.me/healthwellness/2345',
                'post_time': '14:15',
                'post_date': 'Today',
                'summary': 'Результаты нового исследования о влиянии питания на продолжительность жизни, ключевые рекомендации по здоровому питанию.'
            },
            {
                'channel': 'Science Today',
                'channel_size': '420K subscribers',
                'topic': 'Новое открытие в физике',
                'views': '142,800',
                'forwards': '5,930',
                'engagement': '3.4%',
                'likes': '4,760',
                'comments': '623',
                'link': 'https://t.me/sciencetoday/6789',
                'post_time': '13:00',
                'post_date': 'Today',
                'summary': 'Физики совершили прорыв в области квантовых вычислений. Описание открытия, его значение и потенциальное применение.'
            },
            {
                'channel': 'Travel Experiences',
                'channel_size': '480K subscribers',
                'topic': 'Скрытые места для отдыха',
                'views': '154,600',
                'forwards': '6,230',
                'engagement': '3.7%',
                'likes': '5,430',
                'comments': '687',
                'link': 'https://t.me/travelexperiences/9012',
                'post_time': '15:30',
                'post_date': 'Today',
                'summary': 'Подборка малоизвестных, но живописных мест для отдыха, советы по планированию поездки и оптимальному бюджету.'
            },
            {
                'channel': 'Movie Reviews',
                'channel_size': '350K subscribers',
                'topic': 'Анализ нового фильма',
                'views': '128,700',
                'forwards': '4,890',
                'engagement': '3.2%',
                'likes': '4,120',
                'comments': '543',
                'link': 'https://t.me/moviereviews/3456',
                'post_time': '16:45',
                'post_date': 'Today',
                'summary': 'Подробный разбор нового фильма: сюжет, актерская игра, работа режиссера, спецэффекты и музыкальное сопровождение.'
            },
            {
                'channel': 'Fashion Trends',
                'channel_size': '510K subscribers',
                'topic': 'Тренды сезона',
                'views': '175,400',
                'forwards': '7,340',
                'engagement': '3.8%',
                'likes': '6,230',
                'comments': '762',
                'link': 'https://t.me/fashiontrends/7890',
                'post_time': '10:00',
                'post_date': 'Today',
                'summary': 'Обзор главных модных тенденций нового сезона, советы по стилю и рекомендации по обновлению гардероба.'
            },
            {
                'channel': 'Gaming News',
                'channel_size': '680K subscribers',
                'topic': 'Анонс новой игры',
                'views': '312,500',
                'forwards': '15,670',
                'engagement': '4.6%',
                'likes': '12,340',
                'comments': '1,543',
                'link': 'https://t.me/gamingnews/2345',
                'post_time': '18:30',
                'post_date': 'Today',
                'summary': 'Подробности о новой игре от крупной студии: геймплей, графика, сюжет, дата выхода и системные требования.'
            },
            {
                'channel': 'Education Hub',
                'channel_size': '290K subscribers',
                'topic': 'Новые методы обучения',
                'views': '98,700',
                'forwards': '3,450',
                'engagement': '3.0%',
                'likes': '2,870',
                'comments': '365',
                'link': 'https://t.me/educationhub/6789',
                'post_time': '09:15',
                'post_date': 'Today',
                'summary': 'Обзор инновационных подходов к образованию, эффективность различных методик и рекомендации для педагогов и студентов.'
            },
            {
                'channel': 'Space Exploration',
                'channel_size': '340K subscribers',
                'topic': 'Новости с Марса',
                'views': '145,800',
                'forwards': '6,120',
                'engagement': '3.6%',
                'likes': '5,230',
                'comments': '643',
                'link': 'https://t.me/spaceexploration/9012',
                'post_time': '11:30',
                'post_date': 'Today',
                'summary': 'Последние данные с марсохода, новые фотографии поверхности планеты и планы будущих миссий на Марс.'
            },
            {
                'channel': 'Psychology Insights',
                'channel_size': '380K subscribers',
                'topic': 'Исследование поведения',
                'views': '124,600',
                'forwards': '4,950',
                'engagement': '3.3%',
                'likes': '4,230',
                'comments': '521',
                'link': 'https://t.me/psychologyinsights/3456',
                'post_time': '14:45',
                'post_date': 'Today',
                'summary': 'Результаты нового психологического исследования, объяснение паттернов поведения и практические советы для самосовершенствования.'
            },
            {
                'channel': 'Economic Analysis',
                'channel_size': '520K subscribers',
                'topic': 'Экономический прогноз',
                'views': '187,300',
                'forwards': '8,340',
                'engagement': '3.9%',
                'likes': '7,120',
                'comments': '856',
                'link': 'https://t.me/economicanalysis/7890',
                'post_time': '13:15',
                'post_date': 'Today',
                'summary': 'Подробный анализ экономической ситуации, прогнозы по росту ВВП, инфляции и изменениям на рынке труда.'
            },
        ]
        
        return posts
            
    async def get_niche_analysis(self):
        """Return mock data for niche analysis"""
        logging.info("Returning mock data for niche analysis")
        
        niches = {
            'Технологии и IT': {
                'avg_err': '4.3',
                'growth_rate': '8.5',
                'monetization': 'Высокая',
                'competition': 'Высокая',
                'engagement_metrics': {
                    'просмотры_к_подписчикам': '32%',
                    'репосты_к_просмотрам': '3.2%',
                    'комментарии_к_просмотрам': '1.5%'
                },
                'audience': {
                    'возраст': '25-45 лет',
                    'интересы': 'Программирование, гаджеты, инновации',
                    'активность': 'Высокая (преимущественно в рабочее время)'
                },
                'content_recommendations': [
                    'Обзоры новых технологий',
                    'Туториалы по программированию',
                    'Новости технологических компаний'
                ],
                'optimal_posting_time': '09:00 - 12:00, 17:00 - 19:00'
            },
            'Бизнес и финансы': {
                'avg_err': '3.8',
                'growth_rate': '6.2',
                'monetization': 'Высокая',
                'competition': 'Средняя',
                'engagement_metrics': {
                    'просмотры_к_подписчикам': '28%',
                    'репосты_к_просмотрам': '2.8%',
                    'комментарии_к_просмотрам': '1.2%'
                },
                'audience': {
                    'возраст': '30-55 лет',
                    'интересы': 'Инвестиции, предпринимательство, финансы',
                    'активность': 'Средняя (утром и вечером)'
                },
                'content_recommendations': [
                    'Финансовые советы',
                    'Анализ рынков',
                    'Истории успеха'
                ],
                'optimal_posting_time': '07:00 - 09:00, 19:00 - 21:00'
            },
            'Новости и СМИ': {
                'avg_err': '5.2',
                'growth_rate': '9.7',
                'monetization': 'Средняя',
                'competition': 'Очень высокая',
                'engagement_metrics': {
                    'просмотры_к_подписчикам': '45%',
                    'репосты_к_просмотрам': '4.5%',
                    'комментарии_к_просмотрам': '2.8%'
                },
                'audience': {
                    'возраст': 'Все возрастные группы',
                    'интересы': 'Текущие события, политика, общество',
                    'активность': 'Высокая (в течение всего дня)'
                },
                'content_recommendations': [
                    'Оперативные новости',
                    'Аналитические обзоры',
                    'Эксклюзивные репортажи'
                ],
                'optimal_posting_time': 'Равномерно в течение дня, пики: 07:00, 12:00, 18:00'
            },
            'Развлечения и хобби': {
                'avg_err': '3.5',
                'growth_rate': '7.8',
                'monetization': 'Средняя',
                'competition': 'Средняя',
                'engagement_metrics': {
                    'просмотры_к_подписчикам': '35%',
                    'репосты_к_просмотрам': '3.0%',
                    'комментарии_к_просмотрам': '2.2%'
                },
                'audience': {
                    'возраст': '18-35 лет',
                    'интересы': 'Развлечения, игры, творчество',
                    'активность': 'Высокая (вечер и выходные)'
                },
                'content_recommendations': [
                    'Развлекательный контент',
                    'Мастер-классы по хобби',
                    'Юмористические посты'
                ],
                'optimal_posting_time': '15:00 - 23:00, активнее в выходные'
            },
            'Здоровье и спорт': {
                'avg_err': '3.2',
                'growth_rate': '5.4',
                'monetization': 'Средняя',
                'competition': 'Средняя',
                'engagement_metrics': {
                    'просмотры_к_подписчикам': '27%',
                    'репосты_к_просмотрам': '2.3%',
                    'комментарии_к_просмотрам': '1.8%'
                },
                'audience': {
                    'возраст': '20-45 лет',
                    'интересы': 'Фитнес, здоровое питание, медицина',
                    'активность': 'Средняя (утро и вечер)'
                },
                'content_recommendations': [
                    'Советы по здоровому образу жизни',
                    'Тренировочные программы',
                    'Рецепты здорового питания'
                ],
                'optimal_posting_time': '06:00 - 08:00, 17:00 - 20:00'
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