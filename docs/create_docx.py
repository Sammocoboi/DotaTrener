import os
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import re

def set_cell_shading(cell, color):
    shading = cell._element.get_or_add_tcPr()
    shading_elm = shading.makeelement(qn('w:shd'), {
        qn('w:fill'): color,
        qn('w:val'): 'clear'
    })
    shading.append(shading_elm)

def add_heading(doc, text, level):
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    return heading

def add_paragraph(doc, text, bold=False, italic=False, font_size=11):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(font_size)
    run.font.name = 'Times New Roman'
    return p

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

def create_doc1():
    doc = Document()
    
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    doc.add_paragraph()
    title = doc.add_heading('ТЕХНИЧЕСКОЕ ЗАДАНИЕ', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run('Техническое задание на разработку программного обеспечения\n«DotaTrener — платформа для поиска и взаимодействия с тренерами по Dota 2»')
    run.font.size = Pt(14)
    run.font.name = 'Times New Roman'
    
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = info.add_run('Шифр документа: ТЗ-DotaTrener-001\nВерсия: 1.0\nДата составления: 2026')
    run.font.size = Pt(11)
    run.font.name = 'Times New Roman'
    run.italic = True
    
    doc.add_page_break()
    
    add_heading(doc, '1. Назначение и область применения программы', 1)
    
    add_heading(doc, '1.1. Назначение программы', 2)
    add_paragraph(doc, 'DotaTrener — это кроссплатформенное мобильное приложение (веб + Android), предназначенное для поиска, выбора и взаимодействия с тренерами по компьютерной игре Dota 2. Программа обеспечивает:')
    add_paragraph(doc, '• Автоматизированный подбор тренеров на основе рейтинга, специализации и стоимости услуг;')
    add_paragraph(doc, '• Просмотр статистики игроков (матчи, герой, KDA, GPM/XPM, нетворс);')
    add_paragraph(doc, '• Внутренний мессенджер для общения между игроком и тренером;')
    add_paragraph(doc, '• Управление услугами и видео-материалами для тренеров;')
    add_paragraph(doc, '• Интеграция со Steam API и Stratz API для получения данных о матчах.')
    
    add_heading(doc, '1.2. Область применения', 2)
    add_paragraph(doc, 'Программа предназначена для использования в сфере киберспортивного коучинга. Целевая аудитория:')
    add_paragraph(doc, '• Игроки Dota 2 — поиск тренеров для улучшения навыков игры;')
    add_paragraph(doc, '• Тренеры (коучи) — предоставление услуг по разбору матчей, обучению, продвижению своих услуг;')
    add_paragraph(doc, '• Администраторы — модерация заявок тренеров.')
    
    add_heading(doc, '1.3. Нормативные документы', 2)
    add_table(doc, ['Документ', 'Описание'], [
        ['ГОСТ 19.201-78', 'Техническое задание. Требования к содержанию и оформлению'],
        ['ГОСТ 19.404-78', 'Пояснительная записка. Требования к содержанию и оформлению'],
        ['ГОСТ 19.402-78', 'Описание программы. Требования к содержанию и оформлению'],
        ['ГОСТ 19.401-78', 'Текст программы. Требования к содержанию и оформлению'],
        ['ГОСТ 19.504-78', 'Руководство программиста. Требования к содержанию и оформлению'],
        ['ГОСТ 19.505-78', 'Руководство пользователя. Требования к содержанию и оформлению'],
    ])
    
    add_heading(doc, '2. Требования к функционалу', 1)
    
    add_heading(doc, '2.1. Функциональные требования', 2)
    
    add_heading(doc, '2.1.1. Авторизация и аутентификация', 3)
    add_table(doc, ['ID', 'Требование', 'Приоритет'], [
        ['F-01', 'Аутентификация пользователя через Steam OpenID', 'Обязательное'],
        ['F-02', 'Сохранение токена авторизации на клиенте', 'Обязательное'],
        ['F-03', 'Получение профиля пользователя', 'Обязательное'],
    ])
    
    add_heading(doc, '2.1.2. Профиль игрока', 3)
    add_table(doc, ['ID', 'Требование', 'Приоритет'], [
        ['F-04', 'Отображение профиля: ник, Steam ID, MMR, ранг, аватар', 'Обязательное'],
        ['F-05', 'Редактирование имени пользователя', 'Обязательное'],
        ['F-06', 'Загрузка и обрезка аватара (круглое кадрирование, 256×256)', 'Обязательное'],
        ['F-07', 'Привязка/отвязка аккаунта Steam', 'Обязательное'],
        ['F-08', 'Ввод и сохранение Stratz API токена', 'Обязательное'],
    ])
    
    add_heading(doc, '2.1.3. Просмотр матчей', 3)
    add_table(doc, ['ID', 'Требование', 'Приоритет'], [
        ['F-09', 'Список последних 20 матчей игрока', 'Обязательное'],
        ['F-10', 'Детальный просмотр матча', 'Обязательное'],
        ['F-11', 'График нетворса команд', 'Обязательное'],
        ['F-12', 'Сравнение урона по героям и вышкам', 'Обязательное'],
        ['F-13', 'Просмотр сборок героев', 'Желательное'],
    ])
    
    add_heading(doc, '2.1.4. Тренеры', 3)
    add_table(doc, ['ID', 'Требование', 'Приоритет'], [
        ['F-17', 'Каталог тренеров с фильтрацией', 'Обязательное'],
        ['F-18', 'Страница тренера', 'Обязательное'],
        ['F-19', 'Список услуг тренера', 'Обязательное'],
        ['F-21', 'Отзывы пользователей', 'Обязательное'],
        ['F-22', 'Отправка отзыва', 'Обязательное'],
    ])
    
    add_heading(doc, '2.1.5. Чат (мессенджер)', 3)
    add_table(doc, ['ID', 'Требование', 'Приоритет'], [
        ['F-29', 'Создание беседы между игроком и тренером', 'Обязательное'],
        ['F-30', 'Список бесед с последним сообщением', 'Обязательное'],
        ['F-31', 'Отправка и получение сообщений', 'Обязательное'],
        ['F-32', 'Отображение времени отправки', 'Обязательное'],
    ])
    
    add_heading(doc, '2.2. Нефункциональные требования', 2)
    add_table(doc, ['ID', 'Требование', 'Значение'], [
        ['NF-01', 'Время загрузки главного экрана', 'Не более 3 секунд'],
        ['NF-02', 'Поддержка платформ', 'Web, Android'],
        ['NF-03', 'Минимальная версия Android', '5.0 (API 21)'],
        ['NF-04', 'Язык интерфейса', 'Русский'],
        ['NF-05', 'Цветовая схема', 'Светлая тема (оранжевый #F97316)'],
    ])
    
    add_heading(doc, '3. Требования к надёжности', 1)
    add_table(doc, ['ID', 'Требование'], [
        ['R-01', 'Все запросы к API должны обрабатывать ошибки сети и HTTP-ошибки'],
        ['R-02', 'Пользователь должен получать сообщения об ошибках на русском языке'],
        ['R-03', 'При потере соединения данные должны кэшироваться'],
        ['R-04', 'Токен авторизации должен автоматически обновляться'],
        ['R-05', 'Индикатор загрузки должен отображаться при каждом запросе'],
        ['R-06', 'Пустые списки должны отображать информативное сообщение'],
        ['R-07', 'Кнопки должны блокироваться во время выполнения операции'],
    ])
    
    add_heading(doc, '4. Требования к оборудованию', 1)
    
    add_heading(doc, '4.1. Серверное оборудование', 2)
    add_table(doc, ['Параметр', 'Требование'], [
        ['Процессор', 'x86_64, 2+ ядра'],
        ['Оперативная память', '2 ГБ+'],
        ['Дисковое пространство', '20 ГБ+'],
        ['ОС сервера', 'Linux (Ubuntu 22.04 LTS)'],
        ['Web-сервер', 'Nginx (reverse proxy)'],
        ['База данных', 'SQLite / PostgreSQL'],
    ])
    
    add_heading(doc, '4.2. Клиентское оборудование', 2)
    add_table(doc, ['Параметр', 'Требование'], [
        ['Устройства', 'Смартфоны Android, компьютеры (Web)'],
        ['ОС Android', '5.0+'],
        ['Браузер', 'Chrome 90+, Firefox 88+, Safari 14+, Edge 90+'],
        ['Разрешение экрана', 'от 320×568 px'],
    ])
    
    add_heading(doc, '5. Этапы разработки', 1)
    add_table(doc, ['Этап', 'Содержание', 'Сроки'], [
        ['1. Проектирование', 'Разработка архитектуры, ER-диаграмма, API', '2 недели'],
        ['2. Backend', 'Django REST API, модели, эндпоинты', '3 недели'],
        ['3. Frontend', 'React Native UI, навигация, компоненты', '3 недели'],
        ['4. Интеграция', 'Steam API, Stratz API, тестирование', '2 недели'],
        ['5. Тестирование', 'Юзабилити-тестирование, баг-фикс', '1 неделя'],
        ['6. Деплой', 'Настройка сервера, развертывание', '1 неделя'],
    ])
    
    add_heading(doc, '6. Порядок контроля и приёмки', 1)
    add_paragraph(doc, 'Приёмка программы осуществляется комиссией в составе:')
    add_paragraph(doc, '• Заказчик (представитель заказчика)')
    add_paragraph(doc, '• Разработчик (ведущий программист)')
    add_paragraph(doc, '• Тестировщик')
    
    add_paragraph(doc, '')
    add_paragraph(doc, 'Критерии приёмки:', bold=True)
    add_table(doc, ['Критерий', 'Требование'], [
        ['Работоспособность', 'Все функции работают без критических ошибок'],
        ['Производительность', 'Время загрузки не более 3 секунд'],
        ['Удобство использования', 'Успешное прохождение сценариев'],
        ['Безопасность', 'Авторизация через Steam работает корректно'],
    ])
    
    doc.save('C:/Users/Student/Documents/GitHub/DotaTrener/docs/1_техническое_задание.docx')

def create_doc2():
    doc = Document()
    
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    doc.add_paragraph()
    title = doc.add_heading('ПОЯСНИТЕЛЬНАЯ ЗАПИСКА', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run('к проекту\n«DotaTrener — платформа для поиска и взаимодействия с тренерами по Dota 2»')
    run.font.size = Pt(14)
    run.font.name = 'Times New Roman'
    
    doc.add_page_break()
    
    add_heading(doc, '1. Введение', 1)
    
    add_heading(doc, '1.1. Актуальность', 2)
    add_paragraph(doc, 'Dota 2 — одна из самых популярных киберспортивных дисциплин в мире с более чем 700 000 активных игроков ежедневно. Большинство игроков стремятся улучшить свои навыки, но не имеют доступа к квалифицированному коучингу.')
    add_paragraph(doc, 'DotaTrener решает эту проблему, предоставляя:')
    add_paragraph(doc, '• Автоматизированный подбор тренеров на основе игровой статистики;')
    add_paragraph(doc, '• Интеграцию со Steam API и Stratz API;')
    add_paragraph(doc, '• Внутренний мессенджер для общения;')
    add_paragraph(doc, '• Удобный инструмент для тренеров по продвижению услуг.')
    
    add_heading(doc, '1.2. Цель проекта', 2)
    add_paragraph(doc, 'Разработать кроссплатформенное мобильное приложение (Web + Android) для поиска и взаимодействия с тренерами по Dota 2.')
    
    add_heading(doc, '2. Назначение и область применения', 1)
    add_paragraph(doc, 'DotaTrener — это программа для автоматизации процесса поиска и взаимодействия с тренерами по Dota 2.')
    add_paragraph(doc, 'Область применения: киберспортивный коучинг.')
    
    add_heading(doc, '3. Описание алгоритмов программы', 1)
    
    add_heading(doc, '3.1. Алгоритм авторизации через Steam', 2)
    add_paragraph(doc, '1. Пользователь нажимает "Войти через Steam"')
    add_paragraph(doc, '2. Клиент перенаправляется на URL Steam OpenID')
    add_paragraph(doc, '3. Steam перенаправляет пользователя обратно с параметрами')
    add_paragraph(doc, '4. Сервер создаёт/обновляет профиль игрока')
    add_paragraph(doc, '5. Клиент сохраняет токен')
    add_paragraph(doc, '6. Пользователь перенаправляется на главный экран')
    
    add_heading(doc, '3.2. Алгоритм загрузки матчей', 2)
    add_paragraph(doc, '1. Клиент отправляет GET /api/coaching/my-matches/')
    add_paragraph(doc, '2. Сервер проверяет наличие Stratz токена')
    add_paragraph(doc, '3. Сервер отправляет запрос к Stratz GraphQL API')
    add_paragraph(doc, '4. Сервер парсит ответ и формирует список матчей')
    add_paragraph(doc, '5. Сервер возвращает JSON клиенту')
    add_paragraph(doc, '6. Клиент отображает список')
    
    add_heading(doc, '3.3. Алгоритм отправки сообщения', 2)
    add_paragraph(doc, '1. Пользователь вводит текст и нажимает "Отправить"')
    add_paragraph(doc, '2. Клиент отправляет POST /api/coaching/conversations/{id}/')
    add_paragraph(doc, '3. Сервер создаёт объект Message')
    add_paragraph(doc, '4. Сервер обновляет updated_at у Conversation')
    add_paragraph(doc, '5. Сервер возвращает созданный объект Message')
    add_paragraph(doc, '6. Клиент добавляет сообщение в список')
    
    add_heading(doc, '4. Описание структуры программы', 1)
    
    add_heading(doc, '4.1. Архитектура приложения', 2)
    add_paragraph(doc, 'Приложение построено по архитектуре Client-Server:')
    add_paragraph(doc, '• Клиент: React Native (Expo) + TypeScript')
    add_paragraph(doc, '• Сервер: Django REST Framework + Python')
    add_paragraph(doc, '• База данных: SQLite (разработка) / PostgreSQL (продакшен)')
    add_paragraph(doc, '• Внешние API: Steam, Stratz, OpenDota')
    
    add_heading(doc, '4.2. Структура клиента', 2)
    add_paragraph(doc, 'client/')
    add_paragraph(doc, '├── app/ — Экраны (Expo Router, 18 файлов)')
    add_paragraph(doc, '├── src/components/ — Переиспользуемые компоненты')
    add_paragraph(doc, '├── src/lib/ — Утилиты (API, тема, токены)')
    add_paragraph(doc, '├── src/hooks/ — Пользовательские хуки')
    add_paragraph(doc, '└── src/types/ — TypeScript-типы')
    
    add_heading(doc, '4.3. Структура сервера', 2)
    add_paragraph(doc, 'DotaTrener/')
    add_paragraph(doc, '├── DotaTrener/ — Основной пакет Django')
    add_paragraph(doc, '├── coaching/ — Приложение coaching (модели, API)')
    add_paragraph(doc, '├── stratz_meta/ — Приложение Stratz')
    add_paragraph(doc, '└── manage.py — Управление Django')
    
    add_heading(doc, '5. Используемые технологии', 1)
    add_table(doc, ['Технология', 'Версия', 'Назначение'], [
        ['React', '19.2.3', 'UI-библиотека'],
        ['React Native', '0.85.3', 'Кроссплатформенный UI'],
        ['Expo', '56.0.5', 'Фреймворк для React Native'],
        ['TypeScript', '6.0.3', 'Статическая типизация'],
        ['Axios', '1.16.1', 'HTTP-клиент'],
        ['Django', '4.2+', 'Web-фреймворк'],
        ['Django REST Framework', '3.14+', 'REST API'],
        ['Python', '3.10+', 'Язык программирования'],
        ['SQLite', '3.35+', 'База данных'],
    ])
    
    add_heading(doc, '6. Результаты тестирования', 1)
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
    
    doc.save('C:/Users/Student/Documents/GitHub/DotaTrener/docs/2_пояснительная_записка.docx')

def create_doc3():
    doc = Document()
    
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    doc.add_paragraph()
    title = doc.add_heading('ОПИСАНИЕ ПРОГРАММЫ', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run('«DotaTrener — платформа для поиска и взаимодействия с тренерами по Dota 2»')
    run.font.size = Pt(14)
    run.font.name = 'Times New Roman'
    
    doc.add_page_break()
    
    add_heading(doc, '1. Наименование программы', 1)
    add_paragraph(doc, 'DotaTrener (сокращённо: Dota Trainer)')
    add_paragraph(doc, 'Версия: 1.0.0')
    add_paragraph(doc, 'Платформы: Web (React Native Web), Android')
    
    add_heading(doc, '2. Назначение программы', 1)
    add_paragraph(doc, 'DotaTrener — это кроссплатформенное мобильное приложение для поиска, выбора и взаимодействия с тренерами по компьютерной игре Dota 2.')
    
    add_heading(doc, '3. Функции программы', 1)
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
    
    add_heading(doc, '4. Условия выполнения программы', 1)
    
    add_heading(doc, '4.1. Аппаратные требования', 2)
    add_paragraph(doc, 'Сервер:', bold=True)
    add_paragraph(doc, '• Процессор: x86_64, 2+ ядра')
    add_paragraph(doc, '• ОЗУ: 2 ГБ+')
    add_paragraph(doc, '• Диск: 20 ГБ+')
    add_paragraph(doc, '• Сеть: 100 Мбит/с+')
    
    add_paragraph(doc, 'Клиент:', bold=True)
    add_paragraph(doc, '• Устройства: компьютер (Web), смартфон (Android)')
    add_paragraph(doc, '• ОС: Windows 10+, macOS 10.14+, Android 5.0+')
    add_paragraph(doc, '• Браузер: Chrome 90+, Firefox 88+, Safari 14+')
    
    add_heading(doc, '4.2. Программные требования', 2)
    add_paragraph(doc, 'Сервер:', bold=True)
    add_paragraph(doc, '• ОС: Linux (Ubuntu 22.04 LTS)')
    add_paragraph(doc, '• Python 3.10+')
    add_paragraph(doc, '• Django 4.2+')
    add_paragraph(doc, '• Nginx (reverse proxy)')
    
    add_heading(doc, '5. Входные и выходные данные', 1)
    
    add_heading(doc, '5.1. Входные данные', 2)
    add_table(doc, ['Данные', 'Источник', 'Формат'], [
        ['Данные Steam OpenID', 'Steam API', 'JSON'],
        ['Stratz API токен', 'Пользователь', 'Строка (JWT)'],
        ['Текст сообщения', 'Пользователь', 'Unicode'],
        ['Данные матча', 'Stratz GraphQL API', 'JSON'],
        ['Файл видео', 'Пользователь', 'MP4/WebM/MOV/MKV'],
        ['Аватар', 'Пользователь', 'JPEG/PNG'],
    ])
    
    add_heading(doc, '5.2. Выходные данные', 2)
    add_table(doc, ['Данные', 'Назначение', 'Формат'], [
        ['Профиль игрока', 'Отображение на экране', 'JSON'],
        ['Список матчей', 'Просмотр статистики', 'JSON'],
        ['Список тренеров', 'Каталог', 'JSON'],
        ['Сообщения чата', 'Общение', 'JSON'],
        ['Список услуг', 'Управление', 'JSON'],
    ])
    
    add_heading(doc, '6. Интерфейсы взаимодействия', 1)
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
    
    doc.save('C:/Users/Student/Documents/GitHub/DotaTrener/docs/3_описание_программы.docx')

def create_doc4():
    doc = Document()
    
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    doc.add_paragraph()
    title = doc.add_heading('ТЕКСТ ПРОГРАММЫ', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run('«DotaTrener — платформа для поиска и взаимодействия с тренерами по Dota 2»')
    run.font.size = Pt(14)
    run.font.name = 'Times New Roman'
    
    doc.add_page_break()
    
    add_heading(doc, '1. Общие сведения о тексте программы', 1)
    
    add_heading(doc, '1.1. Язык программирования', 2)
    add_paragraph(doc, 'Программа разработана на следующих языках:')
    add_paragraph(doc, '• Frontend: TypeScript (React Native)')
    add_paragraph(doc, '• Backend: Python (Django)')
    
    add_heading(doc, '1.2. Объём исходного кода', 2)
    add_table(doc, ['Компонент', 'Файлов', 'Строк кода'], [
        ['Frontend (client/app)', '18', '~3 500'],
        ['Frontend (client/src)', '12', '~800'],
        ['Backend (coaching)', '8', '~1 200'],
        ['Backend (DotaTrener)', '5', '~150'],
        ['Итого', '43', '~5 650'],
    ])
    
    add_heading(doc, '2. Описание основных модулей', 1)
    
    add_heading(doc, '2.1. Клиентская часть', 2)
    
    add_heading(doc, '2.1.1. Корневой layout (_layout.tsx)', 3)
    add_paragraph(doc, 'Назначение: Инициализация навигации и токена авторизации')
    add_paragraph(doc, 'Объём: 9 строк')
    add_paragraph(doc, 'Функции:')
    add_paragraph(doc, '• Загрузка токена при запуске приложения')
    add_paragraph(doc, '• Настройка навигатора Stack')
    add_paragraph(doc, '• Установка фона экранов')
    
    add_heading(doc, '2.1.2. Главный экран (index.tsx)', 3)
    add_paragraph(doc, 'Назначение: Главный экран с навигацией по разделам')
    add_paragraph(doc, 'Объём: 86 строк')
    add_paragraph(doc, 'Функции:')
    add_paragraph(doc, '• Загрузка статистики матчей (wins, losses, winRate)')
    add_paragraph(doc, '• Отображение карточек навигации')
    add_paragraph(doc, '• Рекомендации по героям')
    
    add_heading(doc, '2.1.3. Профиль (profile.tsx)', 3)
    add_paragraph(doc, 'Назначение: Просмотр и редактирование профиля пользователя')
    add_paragraph(doc, 'Объём: 492 строки')
    add_paragraph(doc, 'Функции:')
    add_paragraph(doc, '• Загрузка профиля (user, player, coach, rank)')
    add_paragraph(doc, '• Редактирование имени пользователя')
    add_paragraph(doc, '• Загрузка и обрезка аватара (256×256)')
    add_paragraph(doc, '• Привязка Steam аккаунта')
    add_paragraph(doc, '• Управление Stratz API токеном')
    add_paragraph(doc, '• Отправка заявки на тренера')
    add_paragraph(doc, '• Управление социальными сетями')
    
    add_heading(doc, '2.1.4. Каталог тренеров (coaches.tsx)', 3)
    add_paragraph(doc, 'Назначение: Список всех тренеров')
    add_paragraph(doc, 'Объём: 82 строки')
    add_paragraph(doc, 'Функции:')
    add_paragraph(doc, '• Загрузка списка тренеров')
    add_paragraph(doc, '• Отображение аватара, имени, рейтинга')
    add_paragraph(doc, '• Навигация на страницу тренера')
    
    add_heading(doc, '2.1.5. Страница тренера (coach-detail.tsx)', 3)
    add_paragraph(doc, 'Назначение: Детальная информация о тренере')
    add_paragraph(doc, 'Объём: 269 строк')
    add_paragraph(doc, 'Функции:')
    add_paragraph(doc, '• Профиль тренера (аватар, описание, рейтинг)')
    add_paragraph(doc, '• Социальные сети')
    add_paragraph(doc, '• Список услуг с ценами')
    add_paragraph(doc, '• Список видео')
    add_paragraph(doc, '• Отзывы и форма отзыва')
    
    add_heading(doc, '2.1.6. Список матчей (matches.tsx)', 3)
    add_paragraph(doc, 'Назначение: Список последних 20 матчей')
    add_paragraph(doc, 'Объём: 151 строка')
    add_paragraph(doc, 'Функции:')
    add_paragraph(doc, '• Загрузка матчей через Stratz API')
    add_paragraph(doc, '• Отображение героя, результата, KDA, GPM/XPM')
    add_paragraph(doc, '• Цветовая индикация побед/поражений')
    
    add_heading(doc, '2.1.7. Детали матча (match-detail.tsx)', 3)
    add_paragraph(doc, 'Назначение: Детальный просмотр матча')
    add_paragraph(doc, 'Объём: 616 строк')
    add_paragraph(doc, 'Функции:')
    add_paragraph(doc, '• Все 10 игроков с героями и статистикой')
    add_paragraph(doc, '• График нетворса команд')
    add_paragraph(doc, '• Сравнение урона')
    add_paragraph(doc, '• Сборки героев (предметы, скиллы, таланты)')
    
    add_heading(doc, '2.1.8. Чат (chat.tsx)', 3)
    add_paragraph(doc, 'Назначение: Экран чата с тренером')
    add_paragraph(doc, 'Объём: 102 строки')
    add_paragraph(doc, 'Функции:')
    add_paragraph(doc, '• Загрузка истории сообщений')
    add_paragraph(doc, '• Отправка новых сообщений')
    add_paragraph(doc, '• Автопрокрутка к последнему сообщению')
    
    add_heading(doc, '2.2. Серверная часть', 2)
    
    add_heading(doc, '2.2.1. Модели данных (coaching/models.py)', 3)
    add_paragraph(doc, 'Назначение: Определение моделей данных (ORM)')
    add_paragraph(doc, 'Объём: 390 строк')
    add_paragraph(doc, 'Модели:')
    add_paragraph(doc, '• Player — Профиль игрока')
    add_paragraph(doc, '• Coach — Профиль тренера')
    add_paragraph(doc, '• CoachReview — Отзыв о тренере')
    add_paragraph(doc, '• CoachVideo — Видео тренера')
    add_paragraph(doc, '• CoachService — Услуга тренера')
    add_paragraph(doc, '• Conversation — Беседа')
    add_paragraph(doc, '• Message — Сообщение')
    add_paragraph(doc, '• CoachApplication — Заявка на тренера')
    add_paragraph(doc, '• Hero — Герой Dota 2')
    add_paragraph(doc, '• Match — Матч игрока')
    add_paragraph(doc, '• Item — Предмет Dota 2')
    add_paragraph(doc, '• Ability — Способность Dota 2')
    
    add_heading(doc, '2.2.2. API-представления (coaching/views.py)', 3)
    add_paragraph(doc, 'Назначение: Обработка HTTP-запросов')
    add_paragraph(doc, 'Объём: ~600 строк')
    add_paragraph(doc, 'Основные эндпоинты:')
    add_paragraph(doc, '• profile — Профиль пользователя')
    add_paragraph(doc, '• fetch_my_matches — Загрузка матчей')
    add_paragraph(doc, '• match_detail — Детали матча')
    add_paragraph(doc, '• coach_list/coach_detail — Тренеры')
    add_paragraph(doc, '• conversations — Чат')
    add_paragraph(doc, '• my_services — Услуги')
    
    add_heading(doc, '3. Используемые библиотеки', 1)
    
    add_heading(doc, '3.1. Frontend', 2)
    add_table(doc, ['Библиотека', 'Назначение'], [
        ['react', 'UI-библиотека'],
        ['react-native', 'Кроссплатформенный UI'],
        ['expo', 'Фреймворк для React Native'],
        ['expo-router', 'Навигация'],
        ['axios', 'HTTP-клиент'],
        ['typescript', 'Статическая типизация'],
        ['react-native-web', 'Поддержка Web'],
        ['expo-secure-store', 'Безопасное хранение'],
    ])
    
    add_heading(doc, '3.2. Backend', 2)
    add_table(doc, ['Библиотека', 'Назначение'], [
        ['django', 'Web-фреймворк'],
        ['djangorestframework', 'REST API'],
        ['requests', 'HTTP-клиент'],
        ['django-cors-headers', 'CORS'],
        ['python-dotenv', 'Переменные окружения'],
    ])
    
    doc.save('C:/Users/Student/Documents/GitHub/DotaTrener/docs/4_текст_программы.docx')

def create_doc5():
    doc = Document()
    
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    doc.add_paragraph()
    title = doc.add_heading('РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run('«DotaTrener — платформа для поиска и взаимодействия с тренерами по Dota 2»')
    run.font.size = Pt(14)
    run.font.name = 'Times New Roman'
    
    doc.add_page_break()
    
    add_heading(doc, '1. Введение', 1)
    
    add_heading(doc, '1.1. Назначение программы', 2)
    add_paragraph(doc, 'DotaTrener — это приложение для поиска и взаимодействия с тренерами по Dota 2.')
    add_paragraph(doc, 'С помощью программы вы можете:')
    add_paragraph(doc, '• Найти тренера по рейтингу, цене и специализации;')
    add_paragraph(doc, '• Просматривать статистику своих матчей;')
    add_paragraph(doc, '• Общаться с тренерами через мессенджер;')
    add_paragraph(doc, '• Оставлять отзывы о тренерах.')
    
    add_heading(doc, '1.2. Системные требования', 2)
    add_paragraph(doc, 'Для Web-версии:', bold=True)
    add_paragraph(doc, '• Браузер: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+')
    add_paragraph(doc, '• Подключение к интернету')
    
    add_paragraph(doc, 'Для Android:', bold=True)
    add_paragraph(doc, '• Версия Android: 5.0+')
    add_paragraph(doc, '• Подключение к интернету')
    
    add_heading(doc, '2. Установка и запуск', 1)
    
    add_heading(doc, '2.1. Web-версия', 2)
    add_paragraph(doc, '1. Откройте браузер')
    add_paragraph(doc, '2. Перейдите по адресу: http://83.222.16.188')
    add_paragraph(doc, '3. Приложение загрузится автоматически')
    
    add_heading(doc, '2.2. Android-версия', 2)
    add_paragraph(doc, '1. Скачайте APK-файл установщика')
    add_paragraph(doc, '2. Откройте файл на устройстве Android')
    add_paragraph(doc, '3. Разрешите установку из неизвестных источников')
    add_paragraph(doc, '4. Нажмите "Установить"')
    add_paragraph(doc, '5. Нажмите "Открыть"')
    
    add_heading(doc, '3. Работа с программой', 1)
    
    add_heading(doc, '3.1. Авторизация', 2)
    add_paragraph(doc, 'Вход через Steam:', bold=True)
    add_paragraph(doc, '1. На главном экране нажмите "Аккаунт"')
    add_paragraph(doc, '2. Нажмите "Войти через Steam"')
    add_paragraph(doc, '3. Войдите в аккаунт Steam')
    add_paragraph(doc, '4. Подтвердите авторизацию')
    add_paragraph(doc, '5. Вы будете перенаправлены в приложение')
    
    add_heading(doc, '3.2. Профиль', 2)
    add_paragraph(doc, 'Просмотр профиля:', bold=True)
    add_paragraph(doc, '1. Нажмите "Аккаунт"')
    add_paragraph(doc, '2. Вы увидите информацию о профиле')
    
    add_paragraph(doc, 'Редактирование имени:', bold=True)
    add_paragraph(doc, '1. Нажмите на поле с именем')
    add_paragraph(doc, '2. Введите новое имя')
    add_paragraph(doc, '3. Нажмите "Сохранить"')
    
    add_paragraph(doc, 'Загрузка аватара:', bold=True)
    add_paragraph(doc, '1. Нажмите на аватар или "Загрузить аватарку"')
    add_paragraph(doc, '2. Выберите файл изображения')
    add_paragraph(doc, '3. Обрежьте изображение')
    add_paragraph(doc, '4. Нажмите "Обрезать"')
    
    add_heading(doc, '3.3. Просмотр матчей', 2)
    add_paragraph(doc, '1. Нажмите "Мои матчи"')
    add_paragraph(doc, '2. Просмотрите список матчей')
    add_paragraph(doc, '3. Нажмите на матч для деталей')
    
    add_heading(doc, '3.4. Каталог тренеров', 2)
    add_paragraph(doc, '1. Нажмите "Тренеры"')
    add_paragraph(doc, '2. Просмотрите список тренеров')
    add_paragraph(doc, '3. Нажмите на тренера для подробностей')
    
    add_heading(doc, '3.5. Запись на услугу', 2)
    add_paragraph(doc, '1. На странице тренера выберите услугу')
    add_paragraph(doc, '2. Нажмите "Связаться"')
    add_paragraph(doc, '3. Автоматически создастся беседа')
    
    add_heading(doc, '3.6. Чат', 2)
    add_paragraph(doc, '1. Нажмите "Аккаунт" → "Сообщения"')
    add_paragraph(doc, '2. Выберите беседу')
    add_paragraph(doc, '3. Введите текст и нажмите отправить')
    
    add_heading(doc, '3.7. Отзывы', 2)
    add_paragraph(doc, '1. Перейдите на страницу тренера')
    add_paragraph(doc, '2. Выберите оценку (1-5 звёзд)')
    add_paragraph(doc, '3. Введите текст отзыва')
    add_paragraph(doc, '4. Нажмите "Отправить"')
    
    add_heading(doc, '3.8. Услуги тренера', 2)
    add_paragraph(doc, 'Добавление услуги:', bold=True)
    add_paragraph(doc, '1. Перейдите в "Мои услуги"')
    add_paragraph(doc, '2. Нажмите "+ Добавить"')
    add_paragraph(doc, '3. Заполните форму')
    add_paragraph(doc, '4. Нажмите "Сохранить"')
    
    add_heading(doc, '4. Описание интерфейса', 1)
    
    add_heading(doc, '4.1. Главный экран', 2)
    add_paragraph(doc, '• Заголовок: "DOTA TRENER"')
    add_paragraph(doc, '• Рекомендации по героям')
    add_paragraph(doc, '• Сводка матчей (победы, поражения, винрейт)')
    add_paragraph(doc, '• Кнопки навигации: Герои, Мета, Тренеры, Матчи, Аккаунт, Сообщения')
    
    add_heading(doc, '4.2. Профиль', 2)
    add_paragraph(doc, '• Аватар и имя пользователя')
    add_paragraph(doc, '• Steam ID')
    add_paragraph(doc, '• Ранг и MMR')
    add_paragraph(doc, '• Информация о тренере')
    add_paragraph(doc, '• Настройки')
    
    add_heading(doc, '4.3. Чат', 2)
    add_paragraph(doc, '• Заголовок с именем собеседника')
    add_paragraph(doc, '• Сообщения (ваши — справа, чужие — слева)')
    add_paragraph(doc, '• Время отправки')
    add_paragraph(doc, '• Поле ввода и кнопка отправки')
    
    add_heading(doc, '5. Возможные ошибки', 1)
    
    add_heading(doc, '5.1. Ошибки авторизации', 2)
    add_table(doc, ['Ошибка', 'Причина', 'Решение'], [
        ['"Не удалось войти через Steam"', 'Проблемы соединением', 'Проверьте подключение к интернету'],
        ['"Steam ID не найден"', 'Аккаунт не привязан', 'Привяжите Steam аккаунт'],
    ])
    
    add_heading(doc, '5.2. Ошибки загрузки данных', 2)
    add_table(doc, ['Ошибка', 'Причина', 'Решение'], [
        ['"Ошибка загрузки"', 'Сервер недоступен', 'Подождите и повторите'],
        ['"Нет данных"', 'Stratz токен не установлен', 'Установите токен'],
        ['"Токен истёк"', 'Время жизни токена истекло', 'Войдите заново'],
    ])
    
    add_heading(doc, '5.3. Ошибки отправки', 2)
    add_table(doc, ['Ошибка', 'Причина', 'Решение'], [
        ['"Не удалось отправить"', 'Проблемы с сетью', 'Проверьте подключение'],
        ['"Сообщение пустое"', 'Не введён текст', 'Введите текст'],
    ])
    
    doc.save('C:/Users/Student/Documents/GitHub/DotaTrener/docs/5_руководство_пользователя.docx')

def create_doc6():
    doc = Document()
    
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    doc.add_paragraph()
    title = doc.add_heading('РУКОВОДСТВО ПРОГРАММИСТА', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run('«DotaTrener — платформа для поиска и взаимодействия с тренерами по Dota 2»')
    run.font.size = Pt(14)
    run.font.name = 'Times New Roman'
    
    doc.add_page_break()
    
    add_heading(doc, '1. Структура проекта', 1)
    
    add_heading(doc, '1.1. Общая структура', 2)
    add_paragraph(doc, 'DotaTrener/')
    add_paragraph(doc, '├── client/ — Frontend (React Native + Expo)')
    add_paragraph(doc, '│   ├── app/ — Экраны (18 файлов)')
    add_paragraph(doc, '│   ├── src/ — Исходный код')
    add_paragraph(doc, '│   │   ├── components/ — Компоненты')
    add_paragraph(doc, '│   │   ├── lib/ — Утилиты')
    add_paragraph(doc, '│   │   ├── hooks/ — Хуки')
    add_paragraph(doc, '│   │   └── types/ — Типы')
    add_paragraph(doc, '│   ├── package.json')
    add_paragraph(doc, '│   └── tsconfig.json')
    add_paragraph(doc, '├── DotaTrener/ — Backend (Django)')
    add_paragraph(doc, '│   ├── DotaTrener/ — Основной пакет')
    add_paragraph(doc, '│   ├── coaching/ — Приложение coaching')
    add_paragraph(doc, '│   ├── stratz_meta/ — Приложение Stratz')
    add_paragraph(doc, '│   ├── manage.py')
    add_paragraph(doc, '│   └── requirements.txt')
    add_paragraph(doc, '└── docs/ — Документация')
    
    add_heading(doc, '1.2. Описание каталогов', 2)
    add_table(doc, ['Каталог', 'Назначение'], [
        ['client/app/', 'Экраны приложения (Expo Router)'],
        ['client/src/components/', 'Переиспользуемые UI-компоненты'],
        ['client/src/lib/', 'Утилиты (API, тема, токены)'],
        ['DotaTrener/coaching/', 'Основное приложение Django'],
        ['DotaTrener/DotaTrener/', 'Конфигурация Django-проекта'],
    ])
    
    add_heading(doc, '2. Используемые библиотеки', 1)
    
    add_heading(doc, '2.1. Frontend', 2)
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
    
    add_heading(doc, '2.2. Backend', 2)
    add_table(doc, ['Библиотека', 'Версия', 'Назначение'], [
        ['Python', '3.10+', 'Язык программирования'],
        ['Django', '4.2+', 'Web-фреймворк'],
        ['Django REST Framework', '3.14+', 'REST API'],
        ['Requests', '2.31+', 'HTTP-клиент'],
        ['django-cors-headers', '4.3+', 'CORS'],
    ])
    
    add_heading(doc, '3. Настройка окружения', 1)
    
    add_heading(doc, '3.1. Требования к системе', 2)
    add_paragraph(doc, '• ОС: Windows 10+, macOS 10.14+, Ubuntu 20.04+')
    add_paragraph(doc, '• Node.js: 18.0+')
    add_paragraph(doc, '• Python: 3.10+')
    add_paragraph(doc, '• Git: 2.30+')
    add_paragraph(doc, '• Диск: 10 ГБ+')
    
    add_heading(doc, '3.2. Установка зависимостей', 2)
    add_paragraph(doc, 'Клиент (Frontend):', bold=True)
    add_paragraph(doc, 'git clone https://github.com/username/DotaTrener.git')
    add_paragraph(doc, 'cd DotaTrener/client')
    add_paragraph(doc, 'npm install')
    add_paragraph(doc, 'npm run web')
    
    add_paragraph(doc, 'Сервер (Backend):', bold=True)
    add_paragraph(doc, 'cd DotaTrener/DotaTrener')
    add_paragraph(doc, 'python -m venv venv')
    add_paragraph(doc, 'venv\\Scripts\\activate')
    add_paragraph(doc, 'pip install -r ../requirements.txt')
    add_paragraph(doc, 'python manage.py migrate')
    add_paragraph(doc, 'python manage.py createsuperuser')
    add_paragraph(doc, 'python manage.py runserver')
    
    add_heading(doc, '3.3. Переменные окружения', 2)
    add_paragraph(doc, 'Файл .env должен содержать:')
    add_paragraph(doc, 'DEBUG=True')
    add_paragraph(doc, 'SECRET_KEY=your-secret-key')
    add_paragraph(doc, 'STEAM_API_KEY=your-steam-api-key')
    add_paragraph(doc, 'STRATZ_API_TOKEN=your-stratz-token')
    
    add_heading(doc, '4. Сборка и модификация', 1)
    
    add_heading(doc, '4.1. Сборка клиента', 2)
    add_paragraph(doc, 'Web-версия:', bold=True)
    add_paragraph(doc, 'cd client')
    add_paragraph(doc, 'npm run web')
    add_paragraph(doc, 'npx expo export --platform web')
    
    add_paragraph(doc, 'Android-версия:', bold=True)
    add_paragraph(doc, 'cd client')
    add_paragraph(doc, 'npm run android')
    add_paragraph(doc, 'eas build --platform android --profile production')
    
    add_heading(doc, '4.2. Добавление нового экрана', 2)
    add_paragraph(doc, '1. Создайте файл в client/app/')
    add_paragraph(doc, '2. Добавьте навигацию в client/app/index.tsx')
    add_paragraph(doc, '3. Импортируйте компоненты из @/lib/theme')
    
    add_heading(doc, '4.3. Добавление нового API-эндпоинта', 2)
    add_paragraph(doc, '1. Добавьте маршрут в coaching/urls.py')
    add_paragraph(doc, '2. Создайте представление в coaching/views.py')
    add_paragraph(doc, '3. Используйте на клиенте с помощью Axios')
    
    add_heading(doc, '5. Архитектура приложения', 1)
    
    add_heading(doc, '5.1. Паттерн проектирования', 2)
    add_paragraph(doc, 'Приложение использует паттерн Model-View-Controller (MVC):')
    add_paragraph(doc, '• Model (Django ORM): coaching/models.py')
    add_paragraph(doc, '• View (Django REST): coaching/views.py')
    add_paragraph(doc, '• Controller (React Native): client/app/*.tsx')
    
    add_heading(doc, '5.2. Потоки данных', 2)
    add_paragraph(doc, 'Клиент (React) ↔ HTTP/JSON ↔ Сервер (Django) ↔ SQLite/PostgreSQL')
    add_paragraph(doc, 'Сервер (Django) ↔ GraphQL ↔ Stratz API')
    
    add_heading(doc, '6. Тестирование', 1)
    
    add_heading(doc, '6.1. Запуск тестов', 2)
    add_paragraph(doc, 'Backend:', bold=True)
    add_paragraph(doc, 'cd DotaTrener')
    add_paragraph(doc, 'python manage.py test')
    add_paragraph(doc, 'python manage.py test coaching')
    
    add_paragraph(doc, 'Frontend:', bold=True)
    add_paragraph(doc, 'cd client')
    add_paragraph(doc, 'npm run lint')
    add_paragraph(doc, 'npx tsc --noEmit')
    
    add_heading(doc, '7. Git Workflow', 1)
    add_paragraph(doc, 'Ветка для новой фичи:')
    add_paragraph(doc, 'git checkout -b feature/new-feature')
    add_paragraph(doc, 'git add .')
    add_paragraph(doc, 'git commit -m "feat: add new feature"')
    add_paragraph(doc, 'git push origin feature/new-feature')
    
    add_paragraph(doc, 'Формат коммитов:')
    add_paragraph(doc, '• feat: — новая функциональность')
    add_paragraph(doc, '• fix: — исправление бага')
    add_paragraph(doc, '• docs: — документация')
    add_paragraph(doc, '• style: — форматирование')
    add_paragraph(doc, '• refactor: — рефакторинг')
    add_paragraph(doc, '• test: — тесты')
    add_paragraph(doc, '• chore: — сборка')
    
    doc.save('C:/Users/Student/Documents/GitHub/DotaTrener/docs/6_руководство_программиста.docx')

if __name__ == '__main__':
    create_doc1()
    create_doc2()
    create_doc3()
    create_doc4()
    create_doc5()
    create_doc6()
    print("All DOCX files created successfully!")
