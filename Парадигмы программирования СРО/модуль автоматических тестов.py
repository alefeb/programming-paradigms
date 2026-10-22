import unittest
from models import Room, QueuePolicy, BenefitPolicy
from services import validate_applicant, filter_valid_applicants, allocate_rooms_pure, calculate_statistics

class TestDormitorySystem(unittest.TestCase):
    
    def setUp(self):
        self.rooms = [
            Room("101", capacity=2, gender="ANY"),
            Room("102", capacity=1, gender="ANY")
        ]
        self.applicants_data = [
            {"applicant_id": "1", "full_name": "Тест 1", "gender": "M", "gpa": 3.5, "is_beneficiary": False, "course": 1, "queue_number": 2},
            {"applicant_id": "2", "full_name": "Тест 2", "gender": "M", "gpa": 4.0, "is_beneficiary": True, "course": 1, "queue_number": 5},
            {"applicant_id": "3", "full_name": "Тест 3", "gender": "F", "gpa": 3.8, "is_beneficiary": False, "course": 2, "queue_number": 1},
        ]

    def test_validation_success(self):
        data = {"applicant_id": "10", "full_name": "Иван", "gender": "M", "gpa": 3.0, "is_beneficiary": False, "course": 1, "queue_number": 1}
        is_valid, err = validate_applicant(data)
        self.assertTrue(is_valid)
        self.assertIsNone(err)

    def test_validation_failure_gender(self):
        data = {"applicant_id": "10", "full_name": "Иван", "gender": "X", "gpa": 3.0, "is_beneficiary": False, "course": 1, "queue_number": 1}
        is_valid, err = validate_applicant(data)
        self.assertFalse(is_valid)
        self.assertIsNotNone(err)

    def test_validation_failure_gpa(self):
        data = {"applicant_id": "10", "full_name": "Иван", "gender": "M", "gpa": 5.5, "is_beneficiary": False, "course": 1, "queue_number": 1}
        is_valid, err = validate_applicant(data)
        self.assertFalse(is_valid)

    def test_filter_valid_applicants(self):
        corrupted_data = self.applicants_data + [{"applicant_id": "", "full_name": "", "gender": "M", "gpa": 2.0, "is_beneficiary": False, "course": 1, "queue_number": 1}]
        filtered = filter_valid_applicants(corrupted_data)
        self.assertEqual(len(filtered), 3)

    def test_queue_policy_allocation(self):
        valid_apps = filter_valid_applicants(self.applicants_data)
        policy = QueuePolicy()
        plan, waiting = allocate_rooms_pure(valid_apps, self.rooms, policy)
        # Всего мест: 3. Заявителей: 3. Никто не должен остаться в листе ожидания.
        self.assertEqual(len(waiting), 0)
        self.assertIn("3", plan["101"] or plan["102"]) # Заявитель 3 имеет queue_number=1, первый на очереди

    def test_benefit_policy_allocation(self):
        valid_apps = filter_valid_applicants(self.applicants_data)
        policy = BenefitPolicy()
        plan, waiting = allocate_rooms_pure(valid_apps, self.rooms, policy)
        # Заявитель 2 имеет льготу (is_beneficiary=True), должен получить приоритет
        all_allocated = [item for occupants in plan.values() for item in occupants]
        self.assertIn("2", all_allocated)

    def test_statistics_calculation(self):
        plan = {"101": ["1", "2"], "102": ["3"]}
        stats = calculate_statistics(plan, self.rooms, waiting_count=1)
        self.assertEqual(stats["total_capacity"], 3)
        self.assertEqual(stats["total_occupied"], 3)
        self.assertEqual(stats["occupancy_rate_percent"], 100.0)
        self.assertEqual(stats["waiting_list_count"], 1)

    def test_room_is_full_property(self):
        room = Room("201", capacity=1, gender="M", current_occupants=["1"])
        self.assertTrue(room.is_full)
        self.assertEqual(room.available_spots, 0)

    def test_immutability_of_allocation(self):
        valid_apps = filter_valid_applicants(self.applicants_data)
        policy = QueuePolicy()
        initial_occupants_len = len(self.rooms[0].current_occupants)
        allocate_rooms_pure(valid_apps, self.rooms, policy)
        # Проверяем, что чистая функция не изменила исходные объекты комнат
        self.assertEqual(len(self.rooms[0].current_occupants), initial_occupants_len)

if __name__ == "__main__":
    unittest.main()