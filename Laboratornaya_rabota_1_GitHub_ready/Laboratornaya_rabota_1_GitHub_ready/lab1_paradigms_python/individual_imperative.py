numbers = [4, 7, 2, 9, 12, 5, 8, 3]

even_numbers = []
total = 0
count = 0

for number in numbers:
    if number % 2 == 0:
        even_numbers.append(number)
        total += number
        count += 1

average = total / count if count else 0

print("Индивидуальный вариант №7")
print("Задание: найти среднее значение чётных чисел.")
print("Чётные числа:", even_numbers)
print("Сумма чётных чисел:", total)
print("Количество чётных чисел:", count)
print("Среднее значение:", average)
print("Изменяемые переменные: even_numbers, total, count")
