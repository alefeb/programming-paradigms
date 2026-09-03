def is_even(number: int) -> bool:
    return number % 2 == 0


def square(number: int) -> int:
    return number ** 2


def get_even_numbers(values: list[int]) -> list[int]:
    return [number for number in values if is_even(number)]


def get_squares(values: list[int]) -> list[int]:
    return [square(number) for number in values]


def sum_even_squares(values: list[int]) -> int:
    total = 0
    for number in values:
        if is_even(number):
            total += square(number)
    return total


numbers = [4, 7, 2, 9, 12, 5, 8, 3]
even_numbers = get_even_numbers(numbers)
squares = get_squares(even_numbers)

print("Проверка is_even(4):", is_even(4))
print("Проверка square(4):", square(4))
print("Чётные числа:", even_numbers)
print("Квадраты чётных чисел:", squares)
print("Сумма квадратов:", sum_even_squares(numbers))
