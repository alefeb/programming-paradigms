numbers = [4, 7, 2, 9, 12, 5, 8, 3]

even_numbers = list(filter(lambda number: number % 2 == 0, numbers))
squares = list(map(lambda number: number ** 2, even_numbers))
result = sum(squares)

generator_squares = (number ** 2 for number in numbers if number % 2 == 0)
generator_result = sum(generator_squares)

print("Чётные числа:", even_numbers)
print("Квадраты чётных чисел:", squares)
print("Сумма квадратов:", result)
print("Результат через генераторное выражение:", generator_result)
print("Изменяемый накопитель total не используется.")
