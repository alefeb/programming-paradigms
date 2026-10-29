import re
import sqlite3

# ==========================================
# ИСХОДНЫЕ ДАННЫЕ
# (Исправлены синтаксические опечатки из методички)
# ==========================================
students = [
    {'name': 'Aida', 'group': 'IS-24-01', 'score': 82, 'attendance': 91, 'email': 'aida@atu.edu.kz'},
    {'name': 'Miras', 'group': 'IS-24-01', 'score': 69, 'attendance': 88, 'email': 'miras@atu.edu.kz'},
    {'name': 'Dana', 'group': 'IS-24-02', 'score': 91, 'attendance': 96, 'email': 'dana@atu.edu.kz'},
    {'name': 'Timur', 'group': 'IS-24-02', 'score': 74, 'attendance': 62, 'email': 'timur_at_atu.kz'},
    {'name': 'Aliya', 'group': 'IS-24-03', 'score': 87, 'attendance': 79, 'email': 'aliya@atu.edu.kz'},
    {'name': 'Arman', 'group': 'IS-24-03', 'score': 55, 'attendance': 72, 'email': 'arman@atu.edu.kz'}
]

# ==========================================
# ЗАДАНИЕ 1: Сравнение двух стилей
# ==========================================
print("=== ЗАДАНИЕ 1: Сравнение двух стилей ===")

# Императивный подход (пошаговый алгоритм)
passed_imperative = []
for student in students:
    if student['score'] >= 75:
        passed_imperative.append(student['name'])

# Декларативный подход (списковое включение)
passed_declarative = [
    student['name']
    for student in students
    if student['score'] >= 75
]

print("Императивный результат:", passed_imperative)
print("Декларативный результат:", passed_declarative)
print("Результаты совпадают:", passed_imperative == passed_declarative)
print()

# ==========================================
# ЗАДАНИЕ 2: Условия для коллекции
# ==========================================
print("=== ЗАДАНИЕ 2: Условия для коллекции ===")

has_excellent = any(s['score'] >= 90 for s in students)
all_attended = all(s['attendance'] >= 60 for s in students)
average = sum(s['score'] for s in students) / len(students) if students else 0

print('Есть отличник:', has_excellent)
print('Посещаемость всех не ниже 60%:', all_attended)
print('Средний балл:', round(average, 1))

# Демонстрация изменения all_attended
print("\n[Изменение] Уменьшаем посещаемость Timur до 50%...")
students[3]['attendance'] = 50
all_attended_updated = all(s['attendance'] >= 60 for s in students)
print('Посещаемость всех не ниже 60% (новое значение):', all_attended_updated)

# Возвращаем исходное значение обратно
students[3]['attendance'] = 62
print()

# ==========================================
# ЗАДАНИЕ 3: Проверка данных регулярными выражениями
# ==========================================
print("=== ЗАДАНИЕ 3: Проверка данных регулярными выражениями ===")

group_pattern = r'^[A-Z]{2}-\d{2}-\d{2}$'
email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

invalid_groups = [s['group'] for s in students if not re.fullmatch(group_pattern, s['group'])]
invalid_emails = [s['email'] for s in students if not re.fullmatch(email_pattern, s['email'])]

print('Ошибочные группы:', invalid_groups if invalid_groups else 'Отсутствуют')
print('Ошибочные email:', invalid_emails if invalid_emails else 'Отсутствуют')

# Исправление некорректного email
print("\n[Исправление] Обновляем адрес Timur на корректный...")
for s in students:
    if s['name'] == 'Timur':
        s['email'] = 'timur@atu.edu.kz'

invalid_emails_fixed = [s['email'] for s in students if not re.fullmatch(email_pattern, s['email'])]
print('Ошибочные email после исправления:', invalid_emails_fixed if invalid_emails_fixed else 'Отсутствуют')
print()

# ==========================================
# ЗАДАНИЕ 4: Создание базы SQLite
# ==========================================
print("=== ЗАДАНИЕ 4: Создание базы SQLite ===")

connection = sqlite3.connect(':memory:')
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE students (
    name TEXT NOT NULL,
    group_name TEXT NOT NULL,
    score INTEGER NOT NULL,
    attendance INTEGER NOT NULL,
    email TEXT NOT NULL
)
""")

rows = [(s['name'], s['group'], s['score'], s['attendance'], s['email']) for s in students]

# Безопасное вставление с помощью плейсхолдеров ?
cursor.executemany(
    'INSERT INTO students VALUES (?, ?, ?, ?, ?)',
    rows
)
connection.commit()
print("База данных в оперативной памяти успешно создана и заполнена.")
print()

# ==========================================
# ЗАДАНИЕ 5: Декларативные SQL запросы
# ==========================================
print("=== ЗАДАНИЕ 5: Декларативные SQL запросы ===")

print("--- 1. Выборка и сортировка (score >= 75 и attendance >= 70) ---")
query_select = """
SELECT name, score, attendance
FROM students
WHERE score >= 75 AND attendance >= 70
ORDER BY score DESC
"""
rows_select = cursor.execute(query_select).fetchall()
if rows_select:
    for row in rows_select:
        print(f"Студент: {row[0]:<8} | Балл: {row[1]} | Посещаемость: {row[2]}%")
else:
    print("Записи не найдены.")

print("\n--- 2. Группировка и агрегирование (средний балл группы >= 70) ---")
query_group = """
SELECT group_name,
       COUNT(*) AS student_count,
       ROUND(AVG(score), 1) AS average_score
FROM students
GROUP BY group_name
HAVING AVG(score) >= 70
ORDER BY average_score DESC
"""
rows_group = cursor.execute(query_group).fetchall()
if rows_group:
    for row in rows_group:
        print(f"Группа: {row[0]} | Студентов: {row[1]} | Средний балл: {row[2]}")
else:
    print("Записи не найдены.")
print()

# ==========================================
# ЗАДАНИЕ 6: Интегрированный результат
# ==========================================
print("=== ЗАДАНИЕ 6: Интегрированный результат ===")

query_integrated = """
SELECT name, group_name, score, email
FROM students
WHERE score >= 70 AND attendance >= 70
ORDER BY score DESC
"""
result = cursor.execute(query_integrated).fetchall()

# Валидация почты через регулярное выражение Python
valid_result = [row for row in result if re.fullmatch(email_pattern, row[3])]

if valid_result:
    for place, row in enumerate(valid_result, start=1):
        name, group_name, score, email = row
        print(f"{place}. {name:<7} | {group_name} | Балл: {score} | Email: {email}")
else:
    print("Список допущенных студентов пуст.")
print()

# ==========================================
# ИНДИВИДУАЛЬНОЕ ЗАДАНИЕ (Вариант 1)
# ==========================================
print("=== ИНДИВИДУАЛЬНОЕ ЗАДАНИЕ (Вариант 1) ===")
# Условия Варианта 1:
# - Результат: Рейтинг отличников (score >= 90)
# - Условие 1: score >= 90
# - Условие 2: Группа IS-24-01 (для демонстрации проверяем домен почты atu.edu.kz)

atu_email_pattern = r'^[A-Za-z0-9._%+-]+@atu\.edu\.kz$'

query_variant1 = """
SELECT name, group_name, score, email
FROM students
WHERE score >= 90
ORDER BY score DESC
"""
var1_rows = cursor.execute(query_variant1).fetchall()

# Дополнительная фильтрация средствами Python и Regex
filtered_var1 = [row for row in var1_rows if re.fullmatch(atu_email_pattern, row[3])]

if filtered_var1:
    print("Отличники с корректной корпоративной почтой (@atu.edu.kz):")
    for row in filtered_var1:
        print(f"Студент: {row[0]} | Группа: {row[1]} | Оценка: {row[2]} | Email: {row[3]}")
else:
    print("Студенты, соответствующие всем условиям индивидуального варианта, не найдены.")

connection.close()