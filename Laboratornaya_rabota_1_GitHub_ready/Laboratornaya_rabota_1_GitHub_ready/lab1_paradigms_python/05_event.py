import tkinter as tk


def calculate():
    try:
        values = [int(value) for value in entry.get().split()]
        even_numbers = [n for n in values if n % 2 == 0]
        squares = [n ** 2 for n in even_numbers]
        result = sum(squares)

        result_label.config(
            text=f"Чётные: {even_numbers}\n"
                 f"Квадраты: {squares}\n"
                 f"Сумма квадратов: {result}"
        )
    except ValueError:
        result_label.config(text="Ошибка: вводи только целые числа через пробел.")


def clear_result():
    entry.delete(0, tk.END)
    result_label.config(text="Результат очищен")


root = tk.Tk()
root.title("Парадигмы программирования")
root.geometry("430x250")

tk.Label(root, text="Введи целые числа через пробел:").pack(pady=10)

entry = tk.Entry(root, width=45)
entry.pack()
entry.insert(0, "4 7 2 9 12 5 8 3")

tk.Button(root, text="Вычислить", command=calculate).pack(pady=10)
tk.Button(root, text="Очистить", command=clear_result).pack()

result_label = tk.Label(root, text="Нажми кнопку «Вычислить»")
result_label.pack(pady=15)

root.mainloop()
