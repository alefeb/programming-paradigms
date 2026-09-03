def is_even(number: int) -> bool:
    return number % 2 == 0


def get_even_numbers(values: list[int]) -> list[int]:
    return [number for number in values if is_even(number)]


def calculate_average(values: list[int]) -> float:
    even_numbers = get_even_numbers(values)
    if not even_numbers:
        return 0.0
    return sum(even_numbers) / len(even_numbers)


numbers = [4, 7, 2, 9, 12, 5, 8, 3]
even_numbers = get_even_numbers(numbers)

print("Индивидуальный вариант №7")
print("Чётные числа:", even_numbers)
print("Среднее значение:", calculate_average(numbers))
