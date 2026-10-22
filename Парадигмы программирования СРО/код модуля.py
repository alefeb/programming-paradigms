from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True)
class Applicant:
    """Сущность заявителя (Лекция 5: ООП, Лекция 7: неизменяемость)."""
    applicant_id: str
    full_name: str
    gender: str          # 'M' или 'F'
    gpa: float
    is_beneficiary: bool # льгота
    course: int
    queue_number: int    # очередность подачи

@dataclass
class Room:
    """Сущность комнаты с изменяемым состоянием (Лекция 2, 5)."""
    room_number: str
    capacity: int
    gender: str          # 'M', 'F' или 'ANY' (если пустая)
    current_occupants: List[str] = field(default_factory=list)

    @property
    def is_full(self) -> bool:
        return len(self.current_occupants) >= self.capacity

    @property
    def available_spots(self) -> int:
        return self.capacity - len(self.current_occupants)


# Лекция 6: Общий интерфейс и взаимозаменяемые реализации (Полиморфизм)

class AllocationPolicy(ABC):
    @abstractmethod
    def sort_key(self, applicant: Applicant):
        """Возвращает ключ сортировки для приоритета заселения."""
        pass


class QueuePolicy(AllocationPolicy):
    """Приоритет по дате подачи (очередности) и GPA."""
    def sort_key(self, applicant: Applicant):
        return (applicant.queue_number, -applicant.gpa)


class BenefitPolicy(AllocationPolicy):
    """Приоритет в первую очередь по льготам, затем по очевидному GPA."""
    def sort_key(self, applicant: Applicant):
        return (not applicant.is_beneficiary, applicant.queue_number, -applicant.gpa)