from typing import List, Tuple, Dict, Any
from models import Applicant, Room, AllocationPolicy

# Лекция 2 & 3: Императивные и процедурные функции с явными параметрами

def validate_applicant(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Функция 1: Валидация заявки заявителя."""
    if not data.get("applicant_id") or not data.get("full_name"):
        return False, "Отсутствует ID или ФИО."
    if data.get("gender") not in ["M", "F"]:
        return False, "Некорректный пол (укажите 'M' или 'F')."
    gpa = data.get("gpa", 0.0)
    if not (0.0 <= gpa <= 4.0):
        return False, "GPA должен быть в диапазоне от 0.0 до 4.0."
    if data.get("course", 0) < 1:
        return False, "Некорректный курс обучения."
    return True, None


def create_applicant_safely(data: Dict[str, Any]) -> Optional[Applicant]:
    """Функция 2: Создание объекта заявителя после проверки."""
    is_valid, error = validate_applicant(data)
    if not is_valid:
        return None
    return Applicant(
        applicant_id=data["applicant_id"],
        full_name=data["full_name"],
        gender=data["gender"],
        gpa=float(data["gpa"]),
        is_beneficiary=bool(data["is_beneficiary"]),
        course=int(data["course"]),
        queue_number=int(data["queue_number"])
    )


def filter_valid_applicants(raw_data_list: List[Dict[str, Any]]) -> List[Applicant]:
    """Функция 3: Фильтрация некорректных заявок (Лекция 8: filter)."""
    valid_dicts = filter(lambda d: validate_applicant(d)[0], raw_data_list)
    return [create_applicant_safely(d) for d in valid_dicts if create_applicant_safely(d) is not None]


def sort_applicants(applicants: List[Applicant], policy: AllocationPolicy) -> List[Applicant]:
    """Функция 4: Сортировка по заданной политике распределения."""
    return sorted(applicants, key=policy.sort_key)


def allocate_rooms_pure(applicants: List[Applicant], rooms: List[Room], policy: AllocationPolicy) -> Tuple[Dict[str, List[str]], List[Applicant]]:
    """
    Функция 5: Чистая функция подбора комнат и формирования листа ожидания.
    Не изменяет исходные коллекции напрямую (Лекция 7: чистые функции и неизменяемость).
    Возвращает новый план заселения и новый лист ожидания.
    """
    sorted_apps = sort_applicants(applicants, policy)
    
    # Создаем глубокую копию состояния комнат для неизменяемости результата
    room_copies: Dict[str, Room] = {
        r.room_number: Room(r.room_number, r.capacity, r.gender, list(r.current_occupants))
        for r in rooms
    }
    
    allocation_plan: Dict[str, List[str]] = {r_num: list(r.current_occupants) for r_num in room_copies}
    waiting_list: List[Applicant] = []

    for app in sorted_apps:
        assigned = False
        for r_num, room in room_copies.items():
            # Проверка вместимости и гендерного соответствия комнаты
            if not room.is_full and (room.gender == "ANY" or room.gender == app.gender):
                room.current_occupants.append(app.applicant_id)
                room.gender = app.gender  дверь фиксирует гендер при первом заселении
                allocation_plan[r_num].append(app.applicant_id)
                assigned = True
                break
        if not assigned:
            waiting_list.append(app)

    return allocation_plan, waiting_list


def calculate_statistics(allocation_plan: Dict[str, List[str]], rooms: List[Room], waiting_count: int) -> Dict[str, Any]:
    """
    Функция 6: Расчет статистики заселения с использованием reduce (Лекция 8).
    """
    total_capacity = sum(map(lambda r: r.capacity, rooms))
    total_occupied = sum(map(lambda occupants: len(occupants), allocation_plan.values()))
    
    occupancy_rate = (total_occupied / total_capacity * 100) if total_capacity > 0 else 0.0

    return {
        "total_capacity": total_capacity,
        "total_occupied": total_occupied,
        "total_free": total_capacity - total_occupied,
        "occupancy_rate_percent": round(occupancy_rate, 2),
        "waiting_list_count": waiting_count
    }