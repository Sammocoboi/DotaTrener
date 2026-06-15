import re

with open('C:/Users/Student/Documents/GitHub/DotaTrener/docs/create_single_docx.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    ("doc.add_paragraph('Сервер:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Сервер:'); run.bold = True"),
    ("doc.add_paragraph('Клиент:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Клиент:'); run.bold = True"),
    ("doc.add_paragraph('Критерии приёмки:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Критерии приёмки:'); run.bold = True"),
    ("doc.add_paragraph('Вход через Steam:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Вход через Steam:'); run.bold = True"),
    ("doc.add_paragraph('Просмотр профиля:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Просмотр профиля:'); run.bold = True"),
    ("doc.add_paragraph('Редактирование имени:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Редактирование имени:'); run.bold = True"),
    ("doc.add_paragraph('Загрузка аватара:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Загрузка аватара:'); run.bold = True"),
    ("doc.add_paragraph('Добавление услуги:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Добавление услуги:'); run.bold = True"),
    ("doc.add_paragraph('Для Web-версии:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Для Web-версии:'); run.bold = True"),
    ("doc.add_paragraph('Для Android:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Для Android:'); run.bold = True"),
    ("doc.add_paragraph('Клиент (Frontend):', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Клиент (Frontend):'); run.bold = True"),
    ("doc.add_paragraph('Сервер (Backend):', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Сервер (Backend):'); run.bold = True"),
    ("doc.add_paragraph('Web-версия:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Web-версия:'); run.bold = True"),
    ("doc.add_paragraph('Android-версия:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Android-версия:'); run.bold = True"),
    ("doc.add_paragraph('Backend:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Backend:'); run.bold = True"),
    ("doc.add_paragraph('Frontend:', bold=True)", "p = doc.add_paragraph(); run = p.add_run('Frontend:'); run.bold = True"),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('C:/Users/Student/Documents/GitHub/DotaTrener/docs/create_single_docx.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed!")
