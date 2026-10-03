from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

BG_DARK = RGBColor(0x0F, 0x0F, 0x1A)
BG_CARD = RGBColor(0x1A, 0x1A, 0x2E)
ACCENT = RGBColor(0x6C, 0x5C, 0xE7)
ACCENT2 = RGBColor(0xE0, 0x45, 0x5B)
TEXT_WHITE = RGBColor(0xF0, 0xF0, 0xF5)
TEXT_GRAY = RGBColor(0x94, 0x94, 0xA8)
GREEN = RGBColor(0x2E, 0xCC, 0x71)
ORANGE = RGBColor(0xF3, 0x9C, 0x12)
SCREENSHOT_BG = RGBColor(0x25, 0x25, 0x3A)

def set_bg(slide, color=BG_DARK):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_shape(slide, left, top, width, height, color, alpha=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def add_text(slide, left, top, width, height, text, size=18, bold=False, color=TEXT_WHITE, align=PP_ALIGN.LEFT, font_name='Calibri'):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = align
    return txBox

def add_bullet_text(slide, left, top, width, height, items, size=16, color=TEXT_WHITE, spacing=Pt(8)):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.name = 'Calibri'
        p.space_after = spacing
        p.level = 0
    return txBox

def add_accent_bar(slide, left, top, width=Inches(0.08), height=Inches(0.5), color=ACCENT):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def add_card(slide, left, top, width, height, title, body_lines, title_size=16, body_size=13):
    card = add_shape(slide, left, top, width, height, BG_CARD)
    add_accent_bar(slide, left + Inches(0.02), top + Inches(0.15), Inches(0.06), Inches(0.35), ACCENT)
    add_text(slide, left + Inches(0.2), top + Inches(0.1), width - Inches(0.3), Inches(0.4), title, size=title_size, bold=True)
    txBox = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.5), width - Inches(0.3), height - Inches(0.6))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(body_lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(body_size)
        p.font.color.rgb = TEXT_GRAY
        p.font.name = 'Calibri'
        p.space_after = Pt(4)
    return card

def add_phone_mockup(slide, left, top, width, height, label="\u0421\u043A\u0440\u0438\u043D\u0448\u043E\u0442 \u043F\u0440\u0438\u043B\u043E\u0436\u0435\u043D\u0438\u044F"):
    """Add a phone-shaped placeholder for screenshots"""
    # Phone body
    phone = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    phone.fill.solid()
    phone.fill.fore_color.rgb = SCREENSHOT_BG
    phone.line.color.rgb = RGBColor(0x3A, 0x3A, 0x50)
    phone.line.width = Pt(2)
    # Adjust corner radius
    phone.adjustments[0] = 0.08

    # Screen area (inner lighter rect)
    margin_w = width * 0.08
    margin_h = height * 0.06
    screen = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left + margin_w, top + margin_h,
        width - 2 * margin_w, height - 2 * margin_h
    )
    screen.fill.solid()
    screen.fill.fore_color.rgb = RGBColor(0x18, 0x18, 0x2A)
    screen.line.color.rgb = RGBColor(0x2A, 0x2A, 0x40)
    screen.line.width = Pt(1)
    screen.adjustments[0] = 0.04

    # Camera notch (small dot at top center)
    notch = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        left + width / 2 - Inches(0.04), top + Inches(0.08),
        Inches(0.08), Inches(0.08)
    )
    notch.fill.solid()
    notch.fill.fore_color.rgb = RGBColor(0x30, 0x30, 0x48)
    notch.line.fill.background()

    # Label text
    add_text(slide, left + Inches(0.1), top + height / 2 - Inches(0.15), width - Inches(0.2), Inches(0.3),
             label, size=11, color=TEXT_GRAY, align=PP_ALIGN.CENTER)

    # Bottom "home bar"
    home = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left + width / 2 - Inches(0.3), top + height - Inches(0.2),
        Inches(0.6), Inches(0.04)
    )
    home.fill.solid()
    home.fill.fore_color.rgb = RGBColor(0x3A, 0x3A, 0x50)
    home.line.fill.background()

    return phone

# ========== SLIDE 1: Title ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_shape(slide, Inches(0), Inches(0), prs.slide_width, prs.slide_height, RGBColor(0x15, 0x12, 0x2B))
add_shape(slide, Inches(5.8), Inches(2.8), Inches(1.7), Inches(0.06), ACCENT)
add_text(slide, Inches(1), Inches(1.2), Inches(11), Inches(1), 'DotaTrener', size=60, bold=True, align=PP_ALIGN.CENTER)
add_text(slide, Inches(1), Inches(2.0), Inches(11), Inches(0.8), 'Платформа для поиска тренеров и анализа матчей Dota 2', size=24, color=TEXT_GRAY, align=PP_ALIGN.CENTER)
add_text(slide, Inches(1), Inches(3.2), Inches(11), Inches(1), 'Fullstack-приложение: React Native (Expo) + Django REST Framework', size=18, color=ACCENT, align=PP_ALIGN.CENTER)
add_text(slide, Inches(1), Inches(4.5), Inches(11), Inches(1), 'Backend: Python / Django \u2022 Frontend: TypeScript / React Native\nStratz API \u2022 OpenDota API \u2022 Steam OpenID', size=16, color=TEXT_GRAY, align=PP_ALIGN.CENTER)
# Phone mockup on title
add_phone_mockup(slide, Inches(10.5), Inches(5.5), Inches(2.2), Inches(1.8), "Демо")

# ========== SLIDE 2: Overview ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'О проекте', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

add_card(slide, Inches(0.8), Inches(1.4), Inches(5.0), Inches(2.8),
    'Что такое DotaTrener?', [
        'Мобильное + Web-приложение для Dota 2 сообщества',
        'Маркетплейс услуг профессиональных тренеров',
        'Интеграция с API Dota 2 (Stratz, OpenDota, Steam)',
        'Аналитика матчей, героев, меты и билдов',
        'Встроенный мессенджер для игроков и тренеров',
        'Русскоязычный интерфейс и документация'
    ])

add_card(slide, Inches(6.2), Inches(1.4), Inches(5.0), Inches(2.8),
    'Ключевая проблема', [
        'Сложно найти квалифицированного тренера по Dota 2',
        'Нет единой платформы для анализа статистики и поиска тренера',
        'Разрозненные инструменты: Discord, Telegram, отдельные сайты',
        'Тренерам сложно находить клиентов и управлять услугами',
        'Нет встроенной аналитики матчей для оценки прогресса'
    ])

add_card(slide, Inches(0.8), Inches(4.6), Inches(7.0), Inches(2.2),
    'Технологии', [
        'Backend: Python 3.10+ / Django 4.2 / DRF / PostgreSQL / SQLite',
        'Frontend: React Native 0.85 / Expo 56 / TypeScript 6.0 / React 19',
        'APIs: Stratz GraphQL (основной), OpenDota REST (резервный), Steam Web API',
        'Auth: Steam OpenID + Email/Password + Token Authentication',
        'Deployment: WSGI/ASGI (Gunicorn), EAS Build (Expo)'
    ])

add_phone_mockup(slide, Inches(8.5), Inches(4.6), Inches(4.0), Inches(2.2), "\u0421\u043A\u0440\u0438\u043D \u0433\u043B\u0430\u0432\u043D\u043E\u0433\u043E \u044D\u043A\u0440\u0430\u043D\u0430")

# ========== SLIDE 3: Target Audience ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Целевая аудитория', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

add_card(slide, Inches(0.8), Inches(1.4), Inches(3.7), Inches(5.2),
    'Игроки (Players)', [
        'Русскоязычные игроки Dota 2 любого уровня',
        'Хотят улучшить навыки через профессиональный коучинг',
        'Ищут удобный каталог тренеров с фильтрацией',
        'Нуждаются в анализе своей статистики и матчей',
        'Используют: история матчей, билды героев, поиск тренера',
    ])

add_card(slide, Inches(4.8), Inches(1.4), Inches(3.7), Inches(5.2),
    'Тренеры (Coaches)', [
        'Опытные игроки Divine/Immortal ранга',
        'Хотят находить клиентов и монетизировать опыт',
        'Управление услугами (цена, описание, длительность)',
        'Загрузка видео-уроков (до 600 MB)',
        'Отзывы и рейтинг, подписка на сервис',
    ])

add_card(slide, Inches(8.8), Inches(1.4), Inches(3.7), Inches(5.2),
    'Администраторы (Admins)', [
        'Модерация заявок на становление тренером',
        'Управление пользователями через Django Admin',
        'Контроль качества услуг и контента',
        'Просмотр и управление всей платформой',
        'Одобрение/отклонение заявок тренеров',
    ])

# ========== SLIDE 4: Architecture ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Архитектура приложения', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

# Backend box
add_shape(slide, Inches(1.5), Inches(1.5), Inches(4.5), Inches(2.5), BG_CARD)
add_accent_bar(slide, Inches(1.52), Inches(1.6), Inches(0.06), Inches(0.35), ACCENT)
add_text(slide, Inches(1.8), Inches(1.5), Inches(4), Inches(0.4), 'Backend (Сервер)', size=20, bold=True)
add_bullet_text(slide, Inches(1.8), Inches(2.0), Inches(4), Inches(1.8), [
    'Django 4.2 + Django REST Framework',
    'Модели: Player, Coach, Match, Review',
    'Stratz Meta: HeroMeta, Builds, Items',
    'Steam OpenID + Email авторизация',
    'Кастомные middleware и permissions',
], size=14, color=TEXT_GRAY)

# Frontend box
add_shape(slide, Inches(7.3), Inches(1.5), Inches(4.5), Inches(2.5), BG_CARD)
add_accent_bar(slide, Inches(7.32), Inches(1.6), Inches(0.06), Inches(0.35), ACCENT2)
add_text(slide, Inches(7.6), Inches(1.5), Inches(4), Inches(0.4), 'Frontend (Клиент)', size=20, bold=True)
add_bullet_text(slide, Inches(7.6), Inches(2.0), Inches(4), Inches(1.8), [
    'React Native 0.85 + Expo 56',
    'Expo Router (файловая навигация)',
    'TypeScript, 30+ экранов',
    'Axios для API запросов',
    'SecureStore для токенов',
], size=14, color=TEXT_GRAY)

# External APIs box
add_shape(slide, Inches(1.5), Inches(4.4), Inches(10.3), Inches(2.5), BG_CARD)
add_accent_bar(slide, Inches(1.52), Inches(4.5), Inches(0.06), Inches(0.35), ORANGE)
add_text(slide, Inches(1.8), Inches(4.4), Inches(4), Inches(0.4), 'Внешние API', size=20, bold=True)
add_bullet_text(slide, Inches(1.8), Inches(4.9), Inches(9.5), Inches(1.8), [
    'Stratz GraphQL API \u2014 матчи, герои, мета-статистика, билды, предметы, способности',
    'OpenDota API \u2014 резервный источник данных для матчей и статистики героев',
    'Steam Web API \u2014 профили пользователей, аватарки, OpenID аутентификация',
], size=14, color=TEXT_GRAY)

# ========== SLIDE 5: Backend ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Backend: Django REST API', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

add_card(slide, Inches(0.8), Inches(1.4), Inches(3.7), Inches(5.3),
    'coaching \u2014 Основное приложение', [
        'REST API для игроков, тренеров и чатов',
        'Модели: Player, Coach, Match, Review, Mistake',
        'CoachService, CoachVideo, Conversation, Message',
        'Аутентификация: Steam OpenID + Email/Password',
        'DRF Token + привязка Steam и Stratz токена',
        'Загрузка аватаров и видео с валидацией файлов',
        'Подписка тренера и заявки на модерацию',
        'Публичный профиль игрока и rank icon endpoint',
    ])

add_card(slide, Inches(4.8), Inches(1.4), Inches(3.7), Inches(5.3),
    'stratz_meta \u2014 Данные Dota 2', [
        'Синхронизация с Stratz GraphQL API',
        'Модели: StratzPatch, HeroMeta, HeroBuild,',
        '  HeroEndgameLoadout',
        'API: patches, hero-meta, hero-builds',
        'Средние показатели: win/pick/ban rate, KDA, GPM, XPM',
        'Билды предметов и способностей по патчам',
        'Роли героев и endgame loadouts',
        'OpenDota как дополнительный источник данных',
    ])

add_card(slide, Inches(8.8), Inches(1.4), Inches(3.7), Inches(5.3),
    'Тестирование и инфраструктура', [
        'pytest + pytest-django',
        'Тесты для coaching и stratz_meta',
        'Django Admin для управления',
        'SQLite для локальной разработки и тестов',
        'WSGI/ASGI точки входа для сервера',
        'Seed и debug-скрипты для наполнения',
        '.env.example и settings_test.py',
    ])

# ========== SLIDE 6: Frontend ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Frontend: React Native (Expo)', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

add_card(slide, Inches(0.8), Inches(1.4), Inches(6.8), Inches(3.0),
    'Основные экраны приложения', [
        'Login / Register / Auth Callback \u2014 аутентификация',
        'Home / Profile \u2014 точка входа и настройки игрока',
        'Coaches / Coach Detail \u2014 каталог и профиль тренера',
        'Matches / Match Detail / Player \u2014 история и разбор матча',
        'Heroes / Hero Detail / Hero Meta \u2014 герои и мета',
        'Chat / Conversations \u2014 общение игрока и тренера',
        'My Services / Subscription \u2014 инструменты тренера',
        'Steam Link / Stratz Token \u2014 привязка аккаунтов и API',
        'Admin Applications \u2014 модерация заявок',
        'Expo Router + TypeScript + единая кодовая база для Web/Android',
    ], body_size=12)

add_phone_mockup(slide, Inches(8.5), Inches(1.4), Inches(4.0), Inches(5.3), "\u0421\u043A\u0440\u0438\u043D \u043F\u0440\u043E\u0444\u0438\u043B\u044F / \u0442\u0440\u0435\u043D\u0435\u0440\u043E\u0432")

# ========== SLIDE 7: Features - Match Analysis ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Функциональность: Анализ матчей', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

add_card(slide, Inches(0.8), Inches(1.4), Inches(5.0), Inches(2.8),
    'История матчей', [
        'Последние 20 матчей игрока',
        'KDA, GPM, XPM по каждому матчу',
        'Длительность и результат',
        'Выбранные герои и их аватарки',
        'Просмотр профиля любого игрока по Steam ID',
    ])

add_card(slide, Inches(6.2), Inches(1.4), Inches(5.0), Inches(2.8),
    'Детальный разбор матча', [
        'Все 10 игроков с героями',
        'Предметы с временными метками',
        'Способности и порядок их улучшения',
        'Выбранные таланты',
        'График нетворса и сравнение урона',
    ])

add_card(slide, Inches(0.8), Inches(4.6), Inches(5.0), Inches(2.2),
    'Источники данных', [
        'Stratz GraphQL \u2014 основной источник: матчи, игроки, статистика',
        'OpenDota REST \u2014 резервный источник',
        'Синхронизация данных о героях и кэширование JSON матчей',
        'Поддержка Divine/Immortal тир-листа',
    ])

add_phone_mockup(slide, Inches(6.2), Inches(4.6), Inches(5.0), Inches(2.2), "\u0421\u043A\u0440\u0438\u043D \u043C\u0430\u0442\u0447\u0430 / \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043A\u0438")

# ========== SLIDE 8: Features - Coaches & Heroes ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Функциональность: Тренеры и Герои', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

add_card(slide, Inches(0.8), Inches(1.4), Inches(5.2), Inches(5.3),
    'Тренерская платформа', [
        'Каталог тренеров с фильтрацией по рейтингу, цене, специализации',
        'Детальный профиль: био, рейтинг, верифицированный MMR',
        'Услуги тренера: создание/редактирование (название, описание, цена, длительность)',
        'Видео-уроки: загрузка до 600 MB (mp4, webm, ogg, mov, mkv)',
        'Отзывы и оценки 1-5 звезд с текстовыми комментариями',
        'Система подписки для активации тренерских привилегий',
        'Заявки на становление тренером с модерацией админом',
        'Социальные ссылки хранятся в JSON-профиле тренера',
    ], body_size=12)

add_card(slide, Inches(6.4), Inches(1.4), Inches(5.2), Inches(2.5),
    'Герои и мета', [
        'Каталог всех героев Dota 2 с атрибутами и ролями',
        'Мета-статистика: винрейт, пикрейт, банрейт, средние KDA/GPM/XPM',
        'Распределение по ролям (Pos 1-5)',
        'Билды предметов: стартовые, ранние, мид, поздние, эндгейм',
        'Билды способностей и выбор талантов на 10/15/20/25 с винрейтом',
        'Синхронизация данных через management команды',
    ], body_size=12)

add_phone_mockup(slide, Inches(6.4), Inches(4.2), Inches(5.2), Inches(2.5), "\u0421\u043A\u0440\u0438\u043D \u043A\u0430\u0442\u0430\u043B\u043E\u0433\u0430 \u0433\u0435\u0440\u043E\u0435\u0432")

# ========== SLIDE 9: Data Models ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Модели данных', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

add_card(slide, Inches(0.8), Inches(1.4), Inches(3.7), Inches(2.4),
    'coaching \u2014 Пользователи', [
        'Player: user, steam_account_id, steam_id_64,',
        '  stratz_token, MMR, favorite_role, avatar_url',
        'Coach: user, title, specialization, bio,',
        '  mmr_verified, social_links, rating',
        'Subscription: user, plan, started_at, expires_at',
        'CoachApplication: user, status, message, reviewed_at',
    ])

add_card(slide, Inches(4.8), Inches(1.4), Inches(3.7), Inches(2.4),
    'coaching \u2014 Контент', [
        'CoachService: coach, title, description,',
        '  price, duration_minutes, video',
        'CoachVideo: coach, title, file_url,',
        '  duration_seconds, price, view_count',
        'Review: match, coach, overall_score,',
        '  summary, status',
    ])

add_card(slide, Inches(8.8), Inches(1.4), Inches(3.7), Inches(2.4),
    'coaching \u2014 Коммуникация', [
        'Conversation: user, coach, service,',
        '  created_at, updated_at',
        'Message: conversation, sender, text,',
        '  created_at',
        'CoachReview: coach, reviewer, rating, text',
    ])

add_card(slide, Inches(0.8), Inches(4.2), Inches(11.7), Inches(2.5),
    'stratz_meta \u2014 Данные Dota 2', [
        'StratzPatch: version, release_date, is_current',
        'HeroMeta: hero, patch, source, win/pick/ban rate, avg stats, roles',
        'HeroBuild: hero_meta, build_type, sequence, pick_rate, win_rate, role',
        'HeroEndgameLoadout: hero_meta, 6 endgame slots, purchase times, games, win_rate',
    ])

add_phone_mockup(slide, Inches(5.5), Inches(6.2), Inches(2.0), Inches(1.0), "API \u0432 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0438")

# ========== SLIDE 10: Project Structure ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Структура проекта', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

add_card(slide, Inches(0.8), Inches(1.4), Inches(3.7), Inches(5.3),
    'DotaTrener/ (Backend)', [
        'DotaTrener/ \u2014 настройки Django и корневые URL',
        'coaching/ \u2014 models, views, serializers, auth, admin',
        'stratz_meta/ \u2014 meta API, services и sync-команды',
        'management/commands/ \u2014 seed и sync-утилиты',
        'media/ \u2014 пользовательские аватары и видео',
        '.env.example \u2014 шаблон переменных окружения',
    ])

add_card(slide, Inches(4.8), Inches(1.4), Inches(3.7), Inches(5.3),
    'client/ (Frontend)', [
        'app/ \u2014 Expo Router экраны',
        'auth, coaches, matches, chat, heroes, admin',
        'src/components/ \u2014 карточки и UI-компоненты',
        'src/lib/ \u2014 api.ts, theme.ts, rank-label.ts, token-storage',
        'src/types/ \u2014 типы матчей, героев и меты',
        'package.json / app.json / tsconfig.json',
    ])

add_card(slide, Inches(8.8), Inches(1.4), Inches(3.7), Inches(5.3),
    'Документация и инфраструктура', [
        'docs/ \u2014 комплект проектной документации',
        '6 markdown-разделов + итоговый .docx',
        'DotaTrener/tests/ \u2014 pytest наборы',
        'create_presentation.py \u2014 генерация презентации',
        'requirements-dev.txt \u2014 dev-зависимости',
        'DotaTrener_Presentation.pptx \u2014 итоговая презентация',
    ])

# ========== SLIDE 11: API Endpoints ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Ключевые API маршруты', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

left_col = [
    'POST /api/auth/register/ \u2014 регистрация',
    'POST /api/auth/login/ \u2014 вход по email',
    'GET /api/auth/steam/login/ \u2014 Steam OpenID',
    'GET /api/auth/steam/callback/ \u2014 callback Steam',
    'GET/PATCH /api/coaching/profile/ \u2014 профиль',
    'POST /api/coaching/link-steam/ \u2014 привязать Steam',
    'POST /api/coaching/set-stratz-token/ \u2014 токен',
    'POST /api/coaching/logout/ \u2014 выход',
    'POST /api/coaching/unbind-steam/ \u2014 отвязать Steam',
    'GET /api/coaching/player/{steam_id}/ \u2014 профиль',
    'GET /api/coaching/rank-icon/{medal}/{star}/ \u2014 иконка',
]
right_col = [
    'GET /api/coaching/my-matches/ \u2014 загрузить матчи',
    'GET /api/coaching/match/{match_id}/ \u2014 детали матча',
    'GET /api/coaching/coaches/ \u2014 каталог тренеров',
    'GET /api/coaching/coaches/{id}/ \u2014 карточка тренера',
    'GET/POST /api/coaching/my-services/ \u2014 услуги',
    'GET/POST /api/coaching/conversations/ \u2014 диалоги',
    'GET/POST /api/coaching/applications/ \u2014 модерация',
    'POST /api/coaching/subscribe/ \u2014 подписка',
    'GET /api/coaching/subscription/ \u2014 статус',
    'GET /api/stratz/hero-meta/ \u2014 мета героев',
    'GET /api/stratz/hero-builds/ \u2014 билды героев',
]

add_card(slide, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.4),
    'Аутентификация и пользователи', left_col, body_size=12)

add_card(slide, Inches(6.9), Inches(1.4), Inches(5.6), Inches(5.4),
    'Тренеры, услуги, матчи', right_col, body_size=12)

# ========== SLIDE 12: Auth Flow ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Аутентификация: Steam OpenID', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

add_card(slide, Inches(0.8), Inches(1.4), Inches(6.0), Inches(5.5),
    'Процесс авторизации через Steam', [
        '1. Пользователь нажимает "Войти через Steam"',
        '2. Перенаправление на login.steampowered.com',
        '3. Steam спрашивает подтверждение входа',
        '4. Успешный редирект обратно с параметрами',
        '5. Сервер валидирует OpenID атрибуты',
        '6. Получение Steam ID из Claimed Identifier',
        '7. Поиск/создание пользователя в БД',
        '8. Генерация DRF Token для сессии',
        '9. Редирект на клиент с токеном',
        '',
        'Дополнительно:',
        '\u2022 Email + пароль регистрация',
        '\u2022 Steam ID сохраняется при первой привязке',
        '\u2022 Имя пользователя из Steam профиля',
    ])

add_phone_mockup(slide, Inches(7.5), Inches(1.4), Inches(5.0), Inches(2.5), "\u042D\u043A\u0440\u0430\u043D \u0432\u0445\u043E\u0434\u0430")

add_card(slide, Inches(7.5), Inches(4.2), Inches(5.0), Inches(2.7),
    'Безопасность', [
        'Token Authentication (DRF)',
        'Токены хранятся в SecureStore (Expo)',
        'Проверка Steam OpenID сигнатуры',
        'Проверка прав доступа для coach/admin',
        'Валидация типов и размера файлов',
        'Привязка Steam выполняется однократно',
    ], body_size=13)

# ========== SLIDE 13: Sync & Data ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Синхронизация данных', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

add_card(slide, Inches(0.8), Inches(1.4), Inches(3.7), Inches(5.3),
    'Stratz GraphQL Client', [
        'Клиент в stratz_meta/services/stratz_client.py',
        'Профиль игрока и матчи по steamAccountId',
        'Мета героев, билды предметов и способностей',
        'Сопоставление героев с локальной БД',
        'Работа с персональным токеном пользователя',
        'Обработка ошибок внешнего API',
    ])

add_card(slide, Inches(4.8), Inches(1.4), Inches(3.7), Inches(5.3),
    'OpenDota REST Client', [
        'Дополнительный клиент в opendota_client.py',
        'Резервные данные для матчей и статистики',
        'Синхронизация меты через sync_opendota_meta',
        'Используется как fallback и для сверки данных',
        'REST-запросы через requests',
        'Обработка таймаутов и ошибок',
    ])

add_card(slide, Inches(8.8), Inches(1.4), Inches(3.7), Inches(5.3),
    'Management Commands', [
        'Команды для синхронизации и обслуживания:',
        'sync_stratz_meta, sync_items_abilities, load_heroes',
        'sync_opendota_meta, enrich_build_names',
        'fetch_player_matches, list_patches',
        'backfill_endgame_loadouts, test_stratz_api',
        'Запуск: python manage.py <команда>',
        'Используются по требованию и для наполнения БД',
    ])

# ========== SLIDE 14: Deployment ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Развёртывание и среда', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

add_card(slide, Inches(0.8), Inches(1.4), Inches(3.7), Inches(2.8),
    'Backend (Сервер)', [
        'Python 3.10+ / Django 4.2+',
        'WSGI/ASGI точки входа в проекте',
        'База данных настраивается через env',
        'SQLite для локальной разработки и тестов',
        'MEDIA_ROOT для аватаров и видео',
        'Настройки через .env.example',
        'settings_test.py для тестов',
    ])

add_card(slide, Inches(4.8), Inches(1.4), Inches(3.7), Inches(2.8),
    'Frontend (Клиент)', [
        'React Native / Expo 56',
        'EAS Build для сборки APK',
        'Expo Go для разработки',
        'React Native Web \u2014 веб-версия',
        'Android API 21+ (Android 5.0)',
        'Web: любой современный браузер',
        'iOS: сконфигурирован (app.json)',
    ])

add_card(slide, Inches(8.8), Inches(1.4), Inches(3.7), Inches(2.8),
    'CI и инструменты', [
        'pytest + pytest-django',
        'Тесты для coaching и stratz_meta',
        'Git для контроля версий',
        'requirements.txt и requirements-dev.txt',
        'Seed-скрипты для тестовых данных',
        'opencode.jsonc для AI-ассистента',
    ])

add_card(slide, Inches(0.8), Inches(4.6), Inches(11.7), Inches(2.2),
    'Конфигурация окружения (.env)', [
        'DJANGO_SECRET_KEY / DJANGO_DEBUG',
        'DJANGO_ALLOWED_HOSTS',
        'DB_NAME / DB_USER / DB_PASSWORD / DB_HOST / DB_PORT',
        'STRATZ_API_KEY / STRATZ_API_URL / STRATZ_REST_URL',
        'STRATZ_PATCH_VERSION / STRATZ_REQUEST_DELAY / STRATZ_BUILDS_TAKE',
    ])

# ========== SLIDE 15: Key Metrics ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.7), 'Ключевые характеристики', size=36, bold=True)
add_accent_bar(slide, Inches(0.8), Inches(1.0), Inches(1.2), Inches(0.05), ACCENT)

metrics = [
    ('Сервер', 'Django 4.2+', ACCENT),
    ('Клиент', 'Expo 56', ACCENT2),
    ('Экраны', '20+', GREEN),
    ('Внешние API', '3', ORANGE),
    ('Модели данных', '20+', ACCENT),
    ('Команды', '10+', GREEN),
    ('Платформы', 'Android + Web', ORANGE),
    ('Авторизация', 'Steam + Email', ACCENT2),
    ('Документация', '6 разделов', ACCENT),
    ('Язык UI', 'Русский', GREEN),
]

for i, (label, value, color) in enumerate(metrics):
    col = i % 5
    row = i // 5
    left = Inches(0.8 + col * 2.5)
    top = Inches(1.5 + row * 2.8)
    card = add_shape(slide, left, top, Inches(2.2), Inches(2.3), BG_CARD)
    add_accent_bar(slide, left + Inches(0.02), top + Inches(0.1), Inches(0.06), Inches(0.35), color)
    add_text(slide, left + Inches(0.15), top + Inches(0.1), Inches(1.9), Inches(0.4), value, size=28, bold=True, color=color, align=PP_ALIGN.CENTER)
    add_text(slide, left + Inches(0.15), top + Inches(0.8), Inches(1.9), Inches(1.2), label, size=14, color=TEXT_GRAY, align=PP_ALIGN.CENTER)

# ========== SLIDE 16: Conclusion ==========
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide)
add_shape(slide, Inches(0), Inches(0), prs.slide_width, prs.slide_height, RGBColor(0x15, 0x12, 0x2B))
add_shape(slide, Inches(5.8), Inches(3.0), Inches(1.7), Inches(0.06), ACCENT)
add_text(slide, Inches(1), Inches(1.5), Inches(11), Inches(1), 'DotaTrener', size=52, bold=True, align=PP_ALIGN.CENTER)
add_text(slide, Inches(1), Inches(2.3), Inches(11), Inches(0.6), 'Полноценная платформа для Dota 2 коучинга', size=22, color=TEXT_GRAY, align=PP_ALIGN.CENTER)
add_text(slide, Inches(1), Inches(3.4), Inches(11), Inches(1.5),
    'React Native (Expo) + Django REST Framework\n'
    'Stratz API \u2022 OpenDota API \u2022 Steam OpenID\n'
    'Android + Web \u2022 Русскоязычный интерфейс',
    size=18, color=TEXT_GRAY, align=PP_ALIGN.CENTER)

add_phone_mockup(slide, Inches(5.2), Inches(5.0), Inches(2.8), Inches(2.0), "Спасибо!")

add_text(slide, Inches(1), Inches(6.5), Inches(11), Inches(0.5), 'Спасибо за внимание!', size=28, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

prs.save('C:\\Users\\Sammo Soboi\\Documents\\GitHub\\DotaTrener\\DotaTrener_Presentation.pptx')
print('Presentation saved successfully!')
