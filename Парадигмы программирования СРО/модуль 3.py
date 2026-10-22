import sys
from models import Room, QueuePolicy, BenefitPolicy
from services import filter_valid_applicants, allocate_rooms_pure, calculate_statistics

# Лекция 1: Обоснование парадигм
PARADIGM_COMPARISON_NOTE = """
--- Сравнение парадигм в проекте №13 ---
1. Императивный подход: используется при изменении состояния комнат и циклических проверках.
2. Объектно-ориентированный подход: сущности Applicant, Room и полиморфные политики QueuePolicy/BenefitPolicy.
3. Функциональный подход: чистые функции вычисления распределения, неизменяемые структуры (frozen=True для Applicant), а также применение map, filter и reduce.
"""

def get_initial_data() -> tuple[list[dict], list[Room]]:
    raw_applicants = [
        {"applicant_id": "A101", "full_name": "Иванов Иван", "gender": "M", "gpa": 3.7, "is_beneficiary": True, "course": 2, "queue_number": 3},
        {"applicant_id": "A102", "full_name": "Петрова Анна", "gender": "F", "gpa": 3.9, "is_beneficiary": False, "course": 1, "queue_number": 1},
        {"applicant_id": "A103", "full_name": "Смирнов Алексей", "gender": "M", "gpa": 3.2, "is_beneficiary": False, "course": 3, "queue_number": 5},
        {"applicant_id": "A104", "full_name": "Кузнецова Ольга", "gender": "F", "gpa": 3.5, "is_beneficiary": True, "course": 2, "queue_number": 2},
        {"applicant_id": "A105", "full_name": "Васильев Дмитрий", "gender": "M", "gpa": 4.0, "is_beneficiary": False, "course": 4, "queue_number": 4},
        {"applicant_id": "ERR1", "full_name": "", "gender": "X", "gpa": 5.0, "is_beneficiary": False, "course": 0, "queue_number": 99}, # Некорректная для теста валидации
    ]
    
    rooms = [
        Room("ГЗ-301", capacity=2, gender="ANY"),
        Room("ГЗ-302", capacity=2, gender="ANY"),
        Room("ГЗ-303", capacity=1, gender="ANY"),
    ]
    return raw_applicants, rooms


def main():
    print("=== СИСТЕМА РАСПРЕДЕЛЕНИЯ МЕСТ В ОБЩЕЖИТИИ (АТУ) ===")
    print(PARADIGM_COMPARISON_NOTE)
    
    raw_apps, rooms = get_initial_data()
    
    # Шаг 1: Валидация и фильтрация
    valid_applicants = filter_valid_applicants(raw_apps)
    print(, len(valid_apps), "валидных заявок из", len(raw_apps), "загружено.")

    # Шаг 2: Выбор политики распределения
    print("\nВыберите политику распределения:")
    print("1. Очередь + GPA (QueuePolicy)")
    print("2. Льготная приоритетная + GPA (BenefitPolicy)")
    choice = input("Введите номер (1 или 2, по умолчанию 1): ").strip()
    
    policy = BenefitPolicy() if choice == "2" else QueuePolicy()
    print(f"Применена политика: {type(policy).__name__}")

    # Шаг 3: Распределение (чистая функция)
    plan, waiting_list = allocate_rooms_pure(valid_applicants, rooms, policy)
    stats = calculate_statistics(plan, rooms, len(waiting_list))

    # Шаг 4: Вывод результатов
    print("\n" + "="*40)
    print("ОБРАБОТАННЫЙ ПЛАН ЗАСЕЛЕНИЯ:")
    for room_num, occupants in plan.items():
        print(f" Комната {room_num}: Заселено {len(occupants)} чел. -> {occupants}")

    print("\nЛИСТ ОЖИДАНИЯ:")
    if waiting_list:
        for app in waiting_list:
            print(f" - {app.applicant_id}: {app.full_name} (GPA: {app.gpa}, Очередь: {app.queue_number})")
    else:
        print(" Лист ожидания пуст.")

    print("\nПОКАЗАТЕЛИ ИСПОЛЬЗОВАНИЯ МЕСТ:")
    print(f" * Общая вместимость: {stats['total_capacity']}")
    print(f" * Всего заселено: {stats['total_occupied']}")
    print(f" * Свободных мест: {stats['total_free']}")
    print(f" * Процент заполняемости: {stats['occupancy_rate_percent']}%")
    print("="*40)

if __name__ == "__main__":
    main()