from functools import reduce

numbers = [4, 7, 2, 9, 12, 5, 8, 3]

even_numbers = list(filter(lambda n: n % 2 == 0, numbers))
total = reduce(lambda a, b: a + b, even_numbers, 0)
count = len(even_numbers)
average = total / count if count else 0.0

print("Индивидуальный вариант №7")
print("Чётные числа:", even_numbers)
print("Среднее значение:", average)
print("Использованы filter() и reduce() без отдельной переменной-накопителя.")
