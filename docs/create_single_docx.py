import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

def set_cell_shading(cell, color):
    shading = cell._element.get_or_add_tcPr()
    shading_elm = shading.makeelement(qn('w:shd'), {
        qn('w:fill'): color,
        qn('w:val'): 'clear'
    })
    shading.append(shading_elm)

def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(10)
                run.font.name = 'Times New Roman'
        set_cell_shading(cell, 'F97316')
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, row in enumerate(rows):
        for j, cell_text in enumerate(row):
            cell = table.rows[i + 1].cells[j]
            cell.text = str(cell_text)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(10)
                    run.font.name = 'Times New Roman'
            if i % 2 == 0:
                set_cell_shading(cell, 'F8FAFC')
    doc.add_paragraph()
    return table

doc = Document()

style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)

# ═══════════════════════════════════════════════════════════════
# ТИТУЛЬНАЯ СТРАНИЦА
# ═══════════════════════════════════════════════════════════════
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run('АВТОНОМНАЯ НЕКОММЕРЧЕСКАЯ ОРГАНИЗАЦИЯ ПРОФЕССИОНАЛЬНАЯ\nОБРАЗОВАТЕЛЬНАЯ ОРГАНИЗАЦИЯ МОСКОВСКИЙ МЕЖДУНАРОДНЫЙ КОЛЛЕДЖ\nЦИФРОВЫХ ТЕХНОЛОГИЙ «АКАДЕМИЯ ТОП»')
r.font.size = Pt(14)
r.bold = True
r.font.name = 'Times New Roman'

for _ in range(6):
    doc.add_paragraph()

t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run('Техническая документация\nк проекту\n«DotaTrener — платформа для поиска и взаимодействия с тренерами по Dota 2»')
r.font.size = Pt(16)
r.bold = True
r.font.name = 'Times New Roman'

for _ in range(4):
    doc.add_paragraph()

t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = t.add_run('Работа студента\nСамойлов Артём Дмитриевич\nОбучающегося 9/1-РПО-24/1')
r.font.size = Pt(14)
r.font.name = 'Times New Roman'

for _ in range(1):
    doc.add_paragraph()

t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = t.add_run('Руководитель проекта\nФедюнин Михаил Александрович')
r.font.size = Pt(14)
r.bold = True
r.font.name = 'Times New Roman'

for _ in range(4):
    doc.add_paragraph()

t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.LEFT
r = t.add_run('Работа допущена к защите «___» _________2024г\nПодпись руководителя проекта ___________________ (________________)')
r.font.size = Pt(14)
r.font.name = 'Times New Roman'

for _ in range(2):
    doc.add_paragraph()

t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run('г. Оренбург\n2025 г.')
r.font.size = Pt(14)
r.font.name = 'Times New Roman'

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# СОДЕРЖАНИЕ
# ═══════════════════════════════════════════════════════════════
t = doc.add_heading('СОДЕРЖАНИЕ', 0)
t.alignment = WD_ALIGN_PARAGRAPH.CENTER

toc = [
    'Часть 1. Техническое задание',
    'Часть 2. Пояснительная записка',
    'Часть 3. Описание программы',
    'Часть 4. Текст программы',
    'Часть 5. Руководство пользователя',
    'Часть 6. Руководство программиста',
]
for item in toc:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_before = Pt(4)
    for run in p.runs:
        run.font.size = Pt(13)
        run.font.name = 'Times New Roman'

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# ЧАСТЬ 1 — ТЕХНИЧЕСКОЕ ЗАДАНИЕ
# ═══════════════════════════════════════════════════════════════
h = doc.add_heading('ЧАСТЬ 1. ТЕХНИЧЕСКОЕ ЗАДАНИЕ', 1)
h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph()

h = doc.add_heading('1. Назначение и область применения программы', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Назначение программы', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('DotaTrener — это кроссплатформенное мобильное приложение (веб + Android), предназначенное для поиска, выбора и взаимодействия с тренерами по компьютерной игре Dota 2.')
doc.add_paragraph('Программа обеспечивает:')
doc.add_paragraph('• Автоматизированный подбор тренеров на основе рейтинга, специализации и стоимости услуг;')
doc.add_paragraph('• Просмотр статистики игроков (матчи, герой, KDA, GPM/XPM, нетворс);')
doc.add_paragraph('• Внутренний мессенджер для общения между игроком и тренером;')
doc.add_paragraph('• Управление услугами и видео-материалами для тренеров;')
doc.add_paragraph('• Интеграция со Steam API и Stratz API для получения данных о матчах.')

h = doc.add_heading('Область применения', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Программа предназначена для использования в сфере киберспортивного коучинга.')
doc.add_paragraph('Целевая аудитория:')
doc.add_paragraph('• Игроки Dota 2 — поиск тренеров для улучшения навыков;')
doc.add_paragraph('• Тренеры (коучи) — предоставление услуг по разбору матчей;')
doc.add_paragraph('• Администраторы — модерация заявок тренеров.')

h = doc.add_heading('Нормативные документы', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Документ', 'Описание'], [
    ['Техническое задание', 'Техническое задание'],
    ['Пояснительная записка', 'Пояснительная записка'],
    ['Описание программы', 'Описание программы'],
    ['Текст программы', 'Текст программы'],
    ['Руководство программиста', 'Руководство программиста'],
    ['Руководство пользователя', 'Руководство пользователя'],
])

h = doc.add_heading('2. Требования к функционалу', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Авторизация и аутентификация', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['ID', 'Требование', 'Приоритет'], [
    ['F-01', 'Аутентификация через Steam OpenID', 'Обязательное'],
    ['F-02', 'Сохранение токена авторизации на клиенте', 'Обязательное'],
    ['F-03', 'Получение профиля пользователя', 'Обязательное'],
])

h = doc.add_heading('Профиль игрока', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['ID', 'Требование', 'Приоритет'], [
    ['F-04', 'Отображение профиля (ник, Steam ID, MMR, ранг, аватар)', 'Обязательное'],
    ['F-05', 'Редактирование имени пользователя', 'Обязательное'],
    ['F-06', 'Загрузка и обрезка аватара (круглое кадрирование, 256×256)', 'Обязательное'],
    ['F-07', 'Привязка/отвязка аккаунта Steam', 'Обязательное'],
    ['F-08', 'Ввод и сохранение Stratz API токена', 'Обязательное'],
])

h = doc.add_heading('Просмотр матчей', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['ID', 'Требование', 'Приоритет'], [
    ['F-09', 'Список последних 20 матчей игрока', 'Обязательное'],
    ['F-10', 'Детальный просмотр матча (все игроки, статистика)', 'Обязательное'],
    ['F-11', 'График нетворса команд (Radiant vs Dire)', 'Обязательное'],
    ['F-12', 'Сравнение урона по героям и вышкам', 'Обязательное'],
    ['F-13', 'Просмотр сборок героев (билды)', 'Желательное'],
])

h = doc.add_heading('Тренеры', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['ID', 'Требование', 'Приоритет'], [
    ['F-17', 'Каталог тренеров с фильтрацией', 'Обязательное'],
    ['F-18', 'Страница тренера (аватар, описание, рейтинг)', 'Обязательное'],
    ['F-19', 'Список услуг тренера с ценами', 'Обязательное'],
    ['F-20', 'Список видео-обзоров тренера', 'Желательное'],
    ['F-21', 'Отзывы пользователей (1-5 звёзд)', 'Обязательное'],
    ['F-22', 'Отправка отзыва о тренере', 'Обязательное'],
])

h = doc.add_heading('Услуги тренера (для тренеров)', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['ID', 'Требование', 'Приоритет'], [
    ['F-23', 'Управление услугами (CRUD)', 'Обязательное'],
    ['F-24', 'Привязка видео к услуге', 'Желательное'],
    ['F-25', 'Активация/деактивация услуги', 'Обязательное'],
])

h = doc.add_heading('Видео тренера', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['ID', 'Требование', 'Приоритет'], [
    ['F-26', 'Загрузка видеофайлов (макс. 600 МБ)', 'Желательное'],
    ['F-27', 'Управление видео (CRUD)', 'Желательное'],
    ['F-28', 'Встроенный видеоплеер', 'Желательное'],
])

h = doc.add_heading('Чат (мессенджер)', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['ID', 'Требование', 'Приоритет'], [
    ['F-29', 'Создание беседы между игроком и тренером', 'Обязательное'],
    ['F-30', 'Список бесед с последним сообщением и непрочитанными', 'Обязательное'],
    ['F-31', 'Отправка и получение сообщений', 'Обязательное'],
    ['F-32', 'Отображение времени отправки сообщения', 'Обязательное'],
])

h = doc.add_heading('Заявки на становление тренером', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['ID', 'Требование', 'Приоритет'], [
    ['F-33', 'Отправка заявки с описанием опыта', 'Обязательное'],
    ['F-34', 'Просмотр статуса заявки', 'Обязательное'],
    ['F-35', 'Панель администратора для рассмотрения заявок', 'Обязательное'],
])

h = doc.add_heading('Нефункциональные требования', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['ID', 'Требование', 'Значение'], [
    ['NF-01', 'Время загрузки главного экрана', 'Не более 3 секунд'],
    ['NF-02', 'Поддержка платформ', 'Web, Android'],
    ['NF-03', 'Минимальная версия Android', '5.0 (API 21)'],
    ['NF-04', 'Язык интерфейса', 'Русский'],
    ['NF-05', 'Цветовая схема', 'Светлая тема (оранжевый #F97316)'],
])

h = doc.add_heading('3. Требования к надёжности', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['ID', 'Требование'], [
    ['R-01', 'Все запросы к API должны обрабатывать ошибки сети и HTTP-ошибки'],
    ['R-02', 'Пользователь должен получать сообщения об ошибках на русском языке'],
    ['R-03', 'При потере соединения данные должны кэшироваться'],
    ['R-04', 'Токен авторизации должен автоматически обновляться'],
    ['R-05', 'Индикатор загрузки должен отображаться при каждом запросе'],
    ['R-06', 'Пустые списки должны отображать информативное сообщение'],
    ['R-07', 'Кнопки должны блокироваться во время выполнения операции'],
])

h = doc.add_heading('4. Требования к оборудованию', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Серверное оборудование', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Параметр', 'Требование'], [
    ['Процессор', 'x86_64, 2+ ядра'],
    ['Оперативная память', '2 ГБ+'],
    ['Дисковое пространство', '20 ГБ+'],
    ['ОС сервера', 'Linux (Ubuntu 22.04 LTS)'],
    ['Web-сервер', 'Nginx (reverse proxy)'],
    ['База данных', 'SQLite / PostgreSQL'],
])

h = doc.add_heading('Клиентское оборудование', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Параметр', 'Требование'], [
    ['Устройства', 'Смартфоны Android, компьютеры (Web)'],
    ['ОС Android', '5.0+'],
    ['Браузер', 'Chrome 90+, Firefox 88+, Safari 14+, Edge 90+'],
    ['Разрешение экрана', 'от 320×568 px'],
])

h = doc.add_heading('5. Этапы разработки', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Этап', 'Содержание', 'Сроки'], [
    ['1. Проектирование', 'Архитектура, ER-диаграмма, API', '2 недели'],
    ['2. Backend', 'Django REST API, модели, эндпоинты', '3 недели'],
    ['3. Frontend', 'React Native UI, навигация', '3 недели'],
    ['4. Интеграция', 'Steam API, Stratz API', '2 недели'],
    ['5. Тестирование', 'Юзабилити, баг-фикс', '1 неделя'],
    ['6. Деплой', 'Настройка сервера, развертывание', '1 неделя'],
])

h = doc.add_heading('6. Порядок контроля и приёмки', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Приёмка программы осуществляется комиссией в составе:')
doc.add_paragraph('• Заказчик')
doc.add_paragraph('• Разработчик')
doc.add_paragraph('• Тестировщик')
doc.add_paragraph('')
p = doc.add_paragraph(); run = p.add_run('Критерии приёмки:'); run.bold = True
add_table(doc, ['Критерий', 'Требование'], [
    ['Работоспособность', 'Все функции работают без критических ошибок'],
    ['Производительность', 'Время загрузки не более 3 секунд'],
    ['Удобство использования', 'Успешное прохождение сценариев'],
    ['Безопасность', 'Авторизация через Steam работает корректно'],
])

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# ЧАСТЬ 2 — ПОЯСНИТЕЛЬНАЯ ЗАПИСКА
# ═══════════════════════════════════════════════════════════════
h = doc.add_heading('ЧАСТЬ 2. ПОЯСНИТЕЛЬНАЯ ЗАПИСКА', 1)
h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph()

h = doc.add_heading('1. Введение', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Актуальность', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Dota 2 — одна из самых популярных киберспортивных дисциплин в мире с более чем 700 000 активных игроков ежедневно. Большинство игроков стремятся улучшить свои навыки, но не имеют доступа к квалифицированному коучингу.')
doc.add_paragraph('DotaTrener решает эту проблему, предоставляя:')
doc.add_paragraph('• Автоматизированный подбор тренеров на основе игровой статистики;')
doc.add_paragraph('• Интеграцию со Steam API и Stratz API;')
doc.add_paragraph('• Внутренний мессенджер для общения;')
doc.add_paragraph('• Удобный инструмент для тренеров по продвижению услуг.')

h = doc.add_heading('Цель проекта', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Разработать кроссплатформенное мобильное приложение (Web + Android) для поиска и взаимодействия с тренерами по Dota 2.')

h = doc.add_heading('2. Назначение и область применения', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('DotaTrener — это программа для автоматизации процесса поиска и взаимодействия с тренерами по Dota 2.')
doc.add_paragraph('Область применения: киберспортивный коучинг.')

h = doc.add_heading('3. Описание алгоритмов программы', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Алгоритм авторизации через Steam', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Пользователь нажимает "Войти через Steam"')
doc.add_paragraph('2. Клиент перенаправляется на URL Steam OpenID')
doc.add_paragraph('3. Steam перенаправляет пользователя обратно с параметрами')
doc.add_paragraph('4. Сервер создаёт/обновляет профиль игрока')
doc.add_paragraph('5. Клиент сохраняет токен')
doc.add_paragraph('6. Пользователь перенаправляется на главный экран')

h = doc.add_heading('Алгоритм загрузки матчей', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Клиент отправляет GET /api/coaching/my-matches/')
doc.add_paragraph('2. Сервер проверяет наличие Stratz токена')
doc.add_paragraph('3. Сервер отправляет запрос к Stratz GraphQL API')
doc.add_paragraph('4. Сервер парсит ответ и формирует список матчей')
doc.add_paragraph('5. Сервер возвращает JSON клиенту')
doc.add_paragraph('6. Клиент отображает список')

h = doc.add_heading('Алгоритм отправки сообщения', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Пользователь вводит текст и нажимает "Отправить"')
doc.add_paragraph('2. Клиент отправляет POST /api/coaching/conversations/{id}/')
doc.add_paragraph('3. Сервер создаёт объект Message')
doc.add_paragraph('4. Сервер обновляет updated_at у Conversation')
doc.add_paragraph('5. Сервер возвращает созданный объект Message')
doc.add_paragraph('6. Клиент добавляет сообщение в список')

h = doc.add_heading('4. Описание структуры программы', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Архитектура приложения', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Приложение построено по архитектуре Client-Server:')
doc.add_paragraph('• Клиент: React Native (Expo) + TypeScript')
doc.add_paragraph('• Сервер: Django REST Framework + Python')
doc.add_paragraph('• База данных: SQLite (разработка) / PostgreSQL (продакшен)')
doc.add_paragraph('• Внешние API: Steam, Stratz, OpenDota')

h = doc.add_heading('Структура клиента', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('client/')
doc.add_paragraph('├── app/ — Экраны (Expo Router, 18 файлов)')
doc.add_paragraph('├── src/components/ — Переиспользуемые компоненты')
doc.add_paragraph('├── src/lib/ — Утилиты (API, тема, токены)')
doc.add_paragraph('├── src/hooks/ — Пользовательские хуки')
doc.add_paragraph('└── src/types/ — TypeScript-типы')

h = doc.add_heading('Структура сервера', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('DotaTrener/')
doc.add_paragraph('├── DotaTrener/ — Основной пакет Django')
doc.add_paragraph('├── coaching/ — Приложение coaching (модели, API)')
doc.add_paragraph('├── stratz_meta/ — Приложение Stratz')
doc.add_paragraph('└── manage.py — Управление Django')

h = doc.add_heading('5. Используемые технологии', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Технология', 'Версия', 'Назначение'], [
    ['React', '19.2.3', 'UI-библиотека'],
    ['React Native', '0.85.3', 'Кроссплатформенный UI'],
    ['Expo', '56.0.5', 'Фреймворк'],
    ['TypeScript', '6.0.3', 'Статическая типизация'],
    ['Axios', '1.16.1', 'HTTP-клиент'],
    ['Django', '4.2+', 'Web-фреймворк'],
    ['Django REST Framework', '3.14+', 'REST API'],
    ['Python', '3.10+', 'Язык программирования'],
    ['SQLite', '3.35+', 'База данных'],
])

h = doc.add_heading('6. Результаты тестирования', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Тест', 'Описание', 'Результат'], [
    ['T-01', 'Авторизация через Steam', 'Пройден'],
    ['T-02', 'Загрузка профиля', 'Пройден'],
    ['T-03', 'Просмотр списка матчей', 'Пройден'],
    ['T-04', 'Просмотр деталей матча', 'Пройден'],
    ['T-05', 'Каталог тренеров', 'Пройден'],
    ['T-06', 'Страница тренера', 'Пройден'],
    ['T-07', 'Отправка отзыва', 'Пройден'],
    ['T-08', 'Создание беседы', 'Пройден'],
    ['T-09', 'Отправка сообщения', 'Пройден'],
    ['T-10', 'Управление услугами', 'Пройден'],
])

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# ЧАСТЬ 3 — ОПИСАНИЕ ПРОГРАММЫ
# ═══════════════════════════════════════════════════════════════
h = doc.add_heading('ЧАСТЬ 3. ОПИСАНИЕ ПРОГРАММЫ', 1)
h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph()

h = doc.add_heading('1. Наименование программы', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('DotaTrener (сокращённо: Dota Trainer)')
doc.add_paragraph('Версия: 1.0.0')
doc.add_paragraph('Платформы: Web (React Native Web), Android')

h = doc.add_heading('2. Назначение программы', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('DotaTrener — это кроссплатформенное мобильное приложение для поиска, выбора и взаимодействия с тренерами по компьютерной игре Dota 2.')

h = doc.add_heading('3. Функции программы', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['№', 'Функция', 'Описание'], [
    ['1', 'Авторизация через Steam', 'Аутентификация через Steam OpenID'],
    ['2', 'Профиль игрока', 'Просмотр и редактирование профиля'],
    ['3', 'Просмотр матчей', 'Список последних 20 матчей'],
    ['4', 'Каталог тренеров', 'Поиск тренеров с фильтрацией'],
    ['5', 'Услуги тренера', 'Управление списком услуг (CRUD)'],
    ['6', 'Чат', 'Внутренний мессенджер'],
    ['7', 'Отзывы', 'Оставление отзывов (1-5 звёзд)'],
    ['8', 'Видео', 'Загрузка видео-обзоров'],
    ['9', 'Мета героев', 'Статистика по героям'],
    ['10', 'Администрирование', 'Рассмотрение заявок'],
])

h = doc.add_heading('4. Условия выполнения программы', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Аппаратные требования', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph(); run = p.add_run('Сервер:'); run.bold = True
doc.add_paragraph('• Процессор: x86_64, 2+ ядра')
doc.add_paragraph('• ОЗУ: 2 ГБ+')
doc.add_paragraph('• Диск: 20 ГБ+')
doc.add_paragraph('• Сеть: 100 Мбит/с+')

p = doc.add_paragraph(); run = p.add_run('Клиент:'); run.bold = True
doc.add_paragraph('• Устройства: компьютер (Web), смартфон (Android)')
doc.add_paragraph('• ОС: Windows 10+, macOS 10.14+, Android 5.0+')
doc.add_paragraph('• Браузер: Chrome 90+, Firefox 88+, Safari 14+')

h = doc.add_heading('Программные требования', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph(); run = p.add_run('Сервер:'); run.bold = True
doc.add_paragraph('• ОС: Linux (Ubuntu 22.04 LTS)')
doc.add_paragraph('• Python 3.10+')
doc.add_paragraph('• Django 4.2+')
doc.add_paragraph('• Nginx (reverse proxy)')

h = doc.add_heading('5. Входные и выходные данные', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Входные данные', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Данные', 'Источник', 'Формат'], [
    ['Данные Steam OpenID', 'Steam API', 'JSON'],
    ['Stratz API токен', 'Пользователь', 'Строка (JWT)'],
    ['Текст сообщения', 'Пользователь', 'Unicode'],
    ['Данные матча', 'Stratz GraphQL API', 'JSON'],
    ['Файл видео', 'Пользователь', 'MP4/WebM/MOV/MKV'],
    ['Аватар', 'Пользователь', 'JPEG/PNG'],
])

h = doc.add_heading('Выходные данные', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Данные', 'Назначение', 'Формат'], [
    ['Профиль игрока', 'Отображение на экране', 'JSON'],
    ['Список матчей', 'Просмотр статистики', 'JSON'],
    ['Список тренеров', 'Каталог', 'JSON'],
    ['Сообщения чата', 'Общение', 'JSON'],
    ['Список услуг', 'Управление', 'JSON'],
])

h = doc.add_heading('6. Интерфейсы взаимодействия', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Метод', 'URL', 'Описание'], [
    ['GET', '/api/coaching/profile/', 'Получение профиля'],
    ['PATCH', '/api/coaching/profile/', 'Обновление профиля'],
    ['GET', '/api/coaching/my-matches/', 'Список матчей'],
    ['GET', '/api/coaching/match/{id}/', 'Детали матча'],
    ['GET', '/api/coaching/coaches/', 'Список тренеров'],
    ['GET', '/api/coaching/coaches/{id}/', 'Детали тренера'],
    ['POST', '/api/coaching/become-coach/', 'Заявка на тренера'],
    ['GET', '/api/coaching/conversations/', 'Список бесед'],
    ['POST', '/api/coaching/conversations/', 'Создание беседы'],
    ['POST', '/api/coaching/conversations/{id}/', 'Отправка сообщения'],
    ['GET', '/api/coaching/my-services/', 'Список услуг'],
    ['POST', '/api/coaching/my-services/', 'Создание услуги'],
    ['PATCH', '/api/coaching/my-services/{id}/', 'Обновление услуги'],
    ['DELETE', '/api/coaching/my-services/{id}/', 'Удаление услуги'],
])

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# ЧАСТЬ 4 — ТЕКСТ ПРОГРАММЫ
# ═══════════════════════════════════════════════════════════════
h = doc.add_heading('ЧАСТЬ 4. ТЕКСТ ПРОГРАММЫ', 1)
h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph()

h = doc.add_heading('1. Общие сведения', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Язык программирования', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('• Frontend: TypeScript (React Native)')
doc.add_paragraph('• Backend: Python (Django)')

h = doc.add_heading('Объём исходного кода', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Компонент', 'Файлов', 'Строк кода'], [
    ['Frontend (client/app)', '18', '~3 500'],
    ['Frontend (client/src)', '12', '~800'],
    ['Backend (coaching)', '8', '~1 200'],
    ['Backend (DotaTrener)', '5', '~150'],
    ['Итого', '43', '~5 650'],
])

h = doc.add_heading('2. Описание модулей клиента', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('_layout.tsx — Корневой layout', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Инициализация навигации и токена авторизации.')
doc.add_paragraph('Объём: 9 строк.')
doc.add_paragraph('Функции: загрузка токена, настройка Stack-навигатора, установка фона экранов.')

h = doc.add_heading('index.tsx — Главный экран', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Главный экран с навигацией по разделам.')
doc.add_paragraph('Объём: 86 строк.')
doc.add_paragraph('Функции: загрузка статистики матчей, отображение карточек навигации, рекомендации по героям.')

h = doc.add_heading('profile.tsx — Профиль', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Просмотр и редактирование профиля пользователя.')
doc.add_paragraph('Объём: 492 строки.')
doc.add_paragraph('Функции: загрузка профиля, редактирование имени, загрузка аватара, привязка Steam, Stratz токен, заявка на тренера, соцсети.')

h = doc.add_heading('coaches.tsx — Каталог тренеров', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Список всех тренеров.')
doc.add_paragraph('Объём: 82 строки.')
doc.add_paragraph('Функции: загрузка списка, отображение аватара/имени/рейтинга, навигация.')

h = doc.add_heading('coach-detail.tsx — Страница тренера', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Детальная информация о тренере.')
doc.add_paragraph('Объём: 269 строк.')
doc.add_paragraph('Функции: профиль, соцсети, услуги, видео, отзывы, форма отзыва, начало беседы.')

h = doc.add_heading('matches.tsx — Список матчей', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Список последних 20 матчей.')
doc.add_paragraph('Объём: 151 строка.')
doc.add_paragraph('Функции: загрузка через Stratz API, отображение героя/результата/KDA/GPM/XPM, цветовая индикация.')

h = doc.add_heading('match-detail.tsx — Детали матча', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Детальный просмотр матча.')
doc.add_paragraph('Объём: 616 строк.')
doc.add_paragraph('Функции: все 10 игроков, график нетворса, сравнение урона, сборки героев.')

h = doc.add_heading('chat.tsx — Чат', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Экран чата с тренером.')
doc.add_paragraph('Объём: 102 строки.')
doc.add_paragraph('Функции: загрузка истории, отправка сообщений, автопрокрутка.')

h = doc.add_heading('conversations.tsx — Список бесед', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Список активных бесед.')
doc.add_paragraph('Объём: 69 строк.')
doc.add_paragraph('Функции: загрузка списка, последнее сообщение, непрочитанные, навигация.')

h = doc.add_heading('my-services.tsx — Услуги тренера', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: CRUD-операции с услугами и видео.')
doc.add_paragraph('Объём: 292 строки.')
doc.add_paragraph('Функции: список услуг, создание/редактирование/удаление, загрузка видео.')

h = doc.add_heading('Остальные экраны', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('• steam-link.tsx (58 строк) — Авторизация через Steam')
doc.add_paragraph('• stratz-token.tsx (71 строка) — Ввод Stratz API токена')
doc.add_paragraph('• admin-applications.tsx (99 строк) — Панель администратора')
doc.add_paragraph('• heroes/hero.tsx (17 строк) — Список героев')
doc.add_paragraph('• heroes/HeroMeta.tsx — Мета героев')
doc.add_paragraph('• heroes/HeroDetail.tsx — Детали героя')

h = doc.add_heading('3. Описание модулей сервера', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('coaching/models.py — Модели данных', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Определение моделей данных (ORM).')
doc.add_paragraph('Объём: 390 строк.')
doc.add_paragraph('Модели: Player, Coach, CoachReview, CoachVideo, CoachService, Conversation, Message, CoachApplication, Hero, Match, Item, Ability, MistakeCategory, Review, Mistake.')

h = doc.add_heading('coaching/views.py — API-представления', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Обработка HTTP-запросов.')
doc.add_paragraph('Объём: ~600 строк.')
doc.add_paragraph('Эндпоинты: profile, fetch_my_matches, match_detail, coach_list, coach_detail, conversations, my_services, become_coach, upload_avatar, upload_video, set_stratz_token.')

h = doc.add_heading('coaching/serializers.py — Сериализаторы', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Сериализация моделей Django в JSON.')
doc.add_paragraph('Объём: ~200 строк.')

h = doc.add_heading('coaching/auth_views.py — Авторизация', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Аутентификация через Steam OpenID.')
doc.add_paragraph('Объём: ~100 строк.')
doc.add_paragraph('Функции: SteamLoginView, SteamCallbackView, создание/обновление профиля.')

h = doc.add_heading('4. Вспомогательные утилиты', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('token-storage.ts', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Безопасное хранение токенов авторизации.')
doc.add_paragraph('Объём: 59 строк.')
doc.add_paragraph('Функции: initToken, saveToken, getToken, clearToken. Поддержка Web (localStorage) и Native (SecureStore).')

h = doc.add_heading('api.ts', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Конфигурация базового URL API.')
doc.add_paragraph('Объём: 6 строк.')
doc.add_paragraph('Константы: API_BASE, API_ROOT, API_HEROES, API_STRATZ_META.')

h = doc.add_heading('theme.ts', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Цвета и стили приложения.')
doc.add_paragraph('Объём: 37 строк.')
doc.add_paragraph('Цвета: bg (#FFFFFF), orange (#F97316), green (#10B981), red (#EF4444), blue (#3B82F6), purple (#8B5CF6).')

h = doc.add_heading('rank-label.ts', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Назначение: Утилиты для работы с рангами Dota 2.')
doc.add_paragraph('Объём: 21 строка.')
doc.add_paragraph('Функции: rankLabel (текстовое описание ранга), rankIconUrl (URL иконки ранга).')

h = doc.add_heading('5. Используемые библиотеки', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Frontend', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Библиотека', 'Назначение'], [
    ['react', 'UI-библиотека'],
    ['react-native', 'Кроссплатформенный UI'],
    ['expo', 'Фреймворк'],
    ['expo-router', 'Навигация'],
    ['axios', 'HTTP-клиент'],
    ['typescript', 'Статическая типизация'],
    ['react-native-web', 'Поддержка Web'],
    ['expo-secure-store', 'Безопасное хранение'],
])

h = doc.add_heading('Backend', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Библиотека', 'Назначение'], [
    ['django', 'Web-фреймворк'],
    ['djangorestframework', 'REST API'],
    ['requests', 'HTTP-клиент'],
    ['django-cors-headers', 'CORS'],
    ['python-dotenv', 'Переменные окружения'],
])

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# ЧАСТЬ 5 — РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ
# ═══════════════════════════════════════════════════════════════
h = doc.add_heading('ЧАСТЬ 5. РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ', 1)
h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph()

h = doc.add_heading('1. Введение', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Назначение программы', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('DotaTrener — это приложение для поиска и взаимодействия с тренерами по Dota 2.')
doc.add_paragraph('С помощью программы вы можете:')
doc.add_paragraph('• Найти тренера по рейтингу, цене и специализации;')
doc.add_paragraph('• Просматривать статистику своих матчей;')
doc.add_paragraph('• Общаться с тренерами через мессенджер;')
doc.add_paragraph('• Оставлять отзывы о тренерах.')

h = doc.add_heading('Системные требования', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph(); run = p.add_run('Для Web-версии:'); run.bold = True
doc.add_paragraph('• Браузер: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+')
doc.add_paragraph('• Подключение к интернету')
p = doc.add_paragraph(); run = p.add_run('Для Android:'); run.bold = True
doc.add_paragraph('• Версия Android: 5.0+')
doc.add_paragraph('• Подключение к интернету')

h = doc.add_heading('2. Установка и запуск', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Web-версия', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Откройте браузер')
doc.add_paragraph('2. Перейдите по адресу: http://83.222.16.188')
doc.add_paragraph('3. Приложение загрузится автоматически')

h = doc.add_heading('Android-версия', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Скачайте APK-файл установщика')
doc.add_paragraph('2. Откройте файл на устройстве Android')
doc.add_paragraph('3. Разрешите установку из неизвестных источников')
doc.add_paragraph('4. Нажмите "Установить"')
doc.add_paragraph('5. Нажмите "Открыть"')

h = doc.add_heading('3. Работа с программой', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Авторизация', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph(); run = p.add_run('Вход через Steam:'); run.bold = True
doc.add_paragraph('1. На главном экране нажмите "Аккаунт"')
doc.add_paragraph('2. Нажмите "Войти через Steam"')
doc.add_paragraph('3. Войдите в аккаунт Steam')
doc.add_paragraph('4. Подтвердите авторизацию')
doc.add_paragraph('5. Вы будете перенаправлены в приложение')

h = doc.add_heading('Профиль', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph(); run = p.add_run('Просмотр профиля:'); run.bold = True
doc.add_paragraph('1. Нажмите "Аккаунт"')
doc.add_paragraph('2. Вы увидите информацию о профиле')
p = doc.add_paragraph(); run = p.add_run('Редактирование имени:'); run.bold = True
doc.add_paragraph('1. Нажмите на поле с именем')
doc.add_paragraph('2. Введите новое имя')
doc.add_paragraph('3. Нажмите "Сохранить"')
p = doc.add_paragraph(); run = p.add_run('Загрузка аватара:'); run.bold = True
doc.add_paragraph('1. Нажмите на аватар или "Загрузить аватарку"')
doc.add_paragraph('2. Выберите файл изображения')
doc.add_paragraph('3. Обрежьте изображение')
doc.add_paragraph('4. Нажмите "Обрезать"')

h = doc.add_heading('Просмотр матчей', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Нажмите "Мои матчи"')
doc.add_paragraph('2. Просмотрите список матчей')
doc.add_paragraph('3. Нажмите на матч для деталей')

h = doc.add_heading('Каталог тренеров', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Нажмите "Тренеры"')
doc.add_paragraph('2. Просмотрите список тренеров')
doc.add_paragraph('3. Нажмите на тренера для подробностей')

h = doc.add_heading('Запись на услугу', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. На странице тренера выберите услугу')
doc.add_paragraph('2. Нажмите "Связаться"')
doc.add_paragraph('3. Автоматически создастся беседа')

h = doc.add_heading('Чат', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Нажмите "Аккаунт" → "Сообщения"')
doc.add_paragraph('2. Выберите беседу')
doc.add_paragraph('3. Введите текст и нажмите отправить')

h = doc.add_heading('Отзывы', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Перейдите на страницу тренера')
doc.add_paragraph('2. Выберите оценку (1-5 звёзд)')
doc.add_paragraph('3. Введите текст отзыва')
doc.add_paragraph('4. Нажмите "Отправить"')

h = doc.add_heading('Услуги тренера', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph(); run = p.add_run('Добавление услуги:'); run.bold = True
doc.add_paragraph('1. Перейдите в "Мои услуги"')
doc.add_paragraph('2. Нажмите "+ Добавить"')
doc.add_paragraph('3. Заполните форму')
doc.add_paragraph('4. Нажмите "Сохранить"')

h = doc.add_heading('Stratz API токен', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Перейдите на stratz.com/api')
doc.add_paragraph('2. Войдите через Steam')
doc.add_paragraph('3. Скопируйте токен')
doc.add_paragraph('4. В приложении: "Аккаунт" → "Stratz API токен"')
doc.add_paragraph('5. Вставьте токен и нажмите "Сохранить"')

h = doc.add_heading('4. Описание интерфейса', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Главный экран', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('• Заголовок: "DOTA TRENER"')
doc.add_paragraph('• Рекомендации по героям')
doc.add_paragraph('• Сводка матчей (победы, поражения, винрейт)')
doc.add_paragraph('• Кнопки навигации')

h = doc.add_heading('Профиль', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('• Аватар и имя пользователя')
doc.add_paragraph('• Steam ID')
doc.add_paragraph('• Ранг и MMR')
doc.add_paragraph('• Информация о тренере')
doc.add_paragraph('• Настройки')

h = doc.add_heading('Чат', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('• Заголовок с именем собеседника')
doc.add_paragraph('• Сообщения (ваши — справа, чужие — слева)')
doc.add_paragraph('• Время отправки')
doc.add_paragraph('• Поле ввода и кнопка отправки')

h = doc.add_heading('5. Возможные ошибки', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Ошибки авторизации', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Ошибка', 'Причина', 'Решение'], [
    ['"Не удалось войти через Steam"', 'Проблемы соединением', 'Проверьте подключение к интернету'],
    ['"Steam ID не найден"', 'Аккаунт не привязан', 'Привяжите Steam аккаунт'],
])

h = doc.add_heading('Ошибки загрузки данных', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Ошибка', 'Причина', 'Решение'], [
    ['"Ошибка загрузки"', 'Сервер недоступен', 'Подождите и повторите'],
    ['"Нет данных"', 'Stratz токен не установлен', 'Установите токен'],
    ['"Токен истёк"', 'Время жизни токена истекло', 'Войдите заново'],
])

h = doc.add_heading('Ошибки отправки', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Ошибка', 'Причина', 'Решение'], [
    ['"Не удалось отправить"', 'Проблемы с сетью', 'Проверьте подключение'],
    ['"Сообщение пустое"', 'Не введён текст', 'Введите текст'],
])

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# ЧАСТЬ 6 — РУКОВОДСТВО ПРОГРАММИСТА
# ═══════════════════════════════════════════════════════════════
h = doc.add_heading('ЧАСТЬ 6. РУКОВОДСТВО ПРОГРАММИСТА', 1)
h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph()

h = doc.add_heading('1. Структура проекта', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Общая структура', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('DotaTrener/')
doc.add_paragraph('├── client/ — Frontend (React Native + Expo)')
doc.add_paragraph('│   ├── app/ — Экраны (18 файлов)')
doc.add_paragraph('│   ├── src/ — Исходный код')
doc.add_paragraph('│   │   ├── components/ — Компоненты')
doc.add_paragraph('│   │   ├── lib/ — Утилиты')
doc.add_paragraph('│   │   ├── hooks/ — Хуки')
doc.add_paragraph('│   │   └── types/ — Типы')
doc.add_paragraph('│   ├── package.json')
doc.add_paragraph('│   └── tsconfig.json')
doc.add_paragraph('├── DotaTrener/ — Backend (Django)')
doc.add_paragraph('│   ├── DotaTrener/ — Основной пакет')
doc.add_paragraph('│   ├── coaching/ — Приложение coaching')
doc.add_paragraph('│   ├── stratz_meta/ — Приложение Stratz')
doc.add_paragraph('│   ├── manage.py')
doc.add_paragraph('│   └── requirements.txt')
doc.add_paragraph('└── docs/ — Документация')

h = doc.add_heading('Описание каталогов', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Каталог', 'Назначение'], [
    ['client/app/', 'Экраны приложения (Expo Router)'],
    ['client/src/components/', 'Переиспользуемые UI-компоненты'],
    ['client/src/lib/', 'Утилиты (API, тема, токены)'],
    ['DotaTrener/coaching/', 'Основное приложение Django'],
    ['DotaTrener/DotaTrener/', 'Конфигурация Django-проекта'],
])

h = doc.add_heading('2. Используемые библиотеки', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Frontend', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Библиотека', 'Версия', 'Назначение'], [
    ['React', '19.2.3', 'UI-библиотека'],
    ['React Native', '0.85.3', 'Кроссплатформенный UI'],
    ['Expo', '56.0.5', 'Фреймворк'],
    ['Expo Router', '56.2.7', 'Навигация'],
    ['Axios', '1.16.1', 'HTTP-клиент'],
    ['TypeScript', '6.0.3', 'Типизация'],
    ['React Native Web', '0.21.0', 'Поддержка Web'],
    ['Expo SecureStore', '56.0.4', 'Хранение данных'],
])

h = doc.add_heading('Backend', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_table(doc, ['Библиотека', 'Версия', 'Назначение'], [
    ['Python', '3.10+', 'Язык программирования'],
    ['Django', '4.2+', 'Web-фреймворк'],
    ['Django REST Framework', '3.14+', 'REST API'],
    ['Requests', '2.31+', 'HTTP-клиент'],
    ['django-cors-headers', '4.3+', 'CORS'],
])

h = doc.add_heading('3. Настройка окружения', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Требования к системе', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('• ОС: Windows 10+, macOS 10.14+, Ubuntu 20.04+')
doc.add_paragraph('• Node.js: 18.0+')
doc.add_paragraph('• Python: 3.10+')
doc.add_paragraph('• Git: 2.30+')
doc.add_paragraph('• Диск: 10 ГБ+')

h = doc.add_heading('Установка зависимостей', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph(); run = p.add_run('Клиент (Frontend):'); run.bold = True
doc.add_paragraph('git clone https://github.com/username/DotaTrener.git')
doc.add_paragraph('cd DotaTrener/client')
doc.add_paragraph('npm install')
doc.add_paragraph('npm run web')
doc.add_paragraph('')
p = doc.add_paragraph(); run = p.add_run('Сервер (Backend):'); run.bold = True
doc.add_paragraph('cd DotaTrener/DotaTrener')
doc.add_paragraph('python -m venv venv')
doc.add_paragraph('venv\\Scripts\\activate')
doc.add_paragraph('pip install -r ../requirements.txt')
doc.add_paragraph('python manage.py migrate')
doc.add_paragraph('python manage.py createsuperuser')
doc.add_paragraph('python manage.py runserver')

h = doc.add_heading('Переменные окружения', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Файл .env должен содержать:')
doc.add_paragraph('DEBUG=True')
doc.add_paragraph('SECRET_KEY=your-secret-key')
doc.add_paragraph('STEAM_API_KEY=your-steam-api-key')
doc.add_paragraph('STRATZ_API_TOKEN=your-stratz-token')

h = doc.add_heading('4. Сборка и модификация', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Сборка клиента', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph(); run = p.add_run('Web-версия:'); run.bold = True
doc.add_paragraph('cd client')
doc.add_paragraph('npm run web')
doc.add_paragraph('npx expo export --platform web')
doc.add_paragraph('')
p = doc.add_paragraph(); run = p.add_run('Android-версия:'); run.bold = True
doc.add_paragraph('cd client')
doc.add_paragraph('npm run android')
doc.add_paragraph('eas build --platform android --profile production')

h = doc.add_heading('Добавление нового экрана', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Создайте файл в client/app/')
doc.add_paragraph('2. Добавьте навигацию в client/app/index.tsx')
doc.add_paragraph('3. Импортируйте компоненты из @/lib/theme')

h = doc.add_heading('Добавление нового API-эндпоинта', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('1. Добавьте маршрут в coaching/urls.py')
doc.add_paragraph('2. Создайте представление в coaching/views.py')
doc.add_paragraph('3. Используйте на клиенте с помощью Axios')

h = doc.add_heading('5. Архитектура приложения', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Паттерн проектирования', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Приложение использует паттерн Model-View-Controller (MVC):')
doc.add_paragraph('• Model (Django ORM): coaching/models.py')
doc.add_paragraph('• View (Django REST): coaching/views.py')
doc.add_paragraph('• Controller (React Native): client/app/*.tsx')

h = doc.add_heading('Потоки данных', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Клиент (React) ↔ HTTP/JSON ↔ Сервер (Django) ↔ SQLite/PostgreSQL')
doc.add_paragraph('Сервер (Django) ↔ GraphQL ↔ Stratz API')

h = doc.add_heading('6. Тестирование', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER

h = doc.add_heading('Запуск тестов', 3)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph(); run = p.add_run('Backend:'); run.bold = True
doc.add_paragraph('cd DotaTrener')
doc.add_paragraph('python manage.py test')
doc.add_paragraph('python manage.py test coaching')
doc.add_paragraph('')
p = doc.add_paragraph(); run = p.add_run('Frontend:'); run.bold = True
doc.add_paragraph('cd client')
doc.add_paragraph('npm run lint')
doc.add_paragraph('npx tsc --noEmit')

h = doc.add_heading('7. Git Workflow', 2)

h.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Ветка для новой фичи:')
doc.add_paragraph('git checkout -b feature/new-feature')
doc.add_paragraph('git add .')
doc.add_paragraph('git commit -m "feat: add new feature"')
doc.add_paragraph('git push origin feature/new-feature')
doc.add_paragraph('')
doc.add_paragraph('Формат коммитов:')
doc.add_paragraph('• feat: — новая функциональность')
doc.add_paragraph('• fix: — исправление бага')
doc.add_paragraph('• docs: — документация')
doc.add_paragraph('• style: — форматирование')
doc.add_paragraph('• refactor: — рефакторинг')
doc.add_paragraph('• test: — тесты')
doc.add_paragraph('• chore: — сборка')

# ═══════════════════════════════════════════════════════════════
# СОХРАНЕНИЕ
# ═══════════════════════════════════════════════════════════════
output_path = 'C:/Users/Sammo Soboi/Documents/GitHub/DotaTrener/docs/DotaTrener_Документация.docx'
doc.save(output_path)
print(f"Файл сохранён: {output_path}")
