import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# Конфигурация подключения к базе данных
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '0000',
    'database': 'expense_tracker'
}

# Подключение к базе данных
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Проверка и создание базы данных и таблицы, если их нет
def check_and_create_db_and_table():
    try:
        # Подключаемся к MySQL без базы данных для создания базы
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()

        # Создание базы данных, если не существует
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        conn.close()

        # Теперь подключаемся к нашей базе данных
        conn = get_db_connection()
        cursor = conn.cursor()

        # Создание таблицы, если не существует
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                amount DECIMAL(10, 2) NOT NULL,
                category VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                description TEXT,
                type ENUM('income', 'expense') NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось создать базу данных или таблицу: {e}")

# Добавление транзакции в базу данных
def add_transaction():
    amount = entry_amount.get()
    category = entry_category.get()
    date = entry_date.get()
    description = entry_description.get()
    type_ = combo_type.get()

    if not amount or not category or not date or not type_:
        messagebox.showerror("Ошибка", "Все поля обязательны для заполнения!")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (amount, category, date, description, type)
            VALUES (%s, %s, %s, %s, %s)
        """, (amount, category, date, description, type_))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Успех", "Транзакция добавлена!")
        clear_form()
        show_transactions()
        show_statistics()  # Обновляем статистику после добавления транзакции
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось добавить транзакцию: {e}")

# Очистка формы ввода
def clear_form():
    entry_amount.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    entry_description.delete(0, tk.END)

# Получение и отображение списка транзакций
def show_transactions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        transactions = cursor.fetchall()
        cursor.close()
        conn.close()

        for row in tree.get_children():
            tree.delete(row)

        for trans in transactions:
            tree.insert('', tk.END, values=(trans['date'], trans['category'], trans['amount'], trans['type'], trans['description']))

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить транзакции: {e}")

# Отображение статистики по категориям
def show_statistics():
    # Удаляем старый график перед созданием нового
    for widget in statistics_frame.winfo_children():
        widget.destroy()

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT category, SUM(amount) AS total FROM transactions
            WHERE type = 'expense'
            GROUP BY category
        """)
        expenses = cursor.fetchall()

        cursor.execute("""
            SELECT category, SUM(amount) AS total FROM transactions
            WHERE type = 'income'
            GROUP BY category
        """)
        incomes = cursor.fetchall()

        cursor.close()
        conn.close()

        categories = [e['category'] for e in expenses]
        expense_values = [e['total'] for e in expenses]
        income_values = [i['total'] for i in incomes]

        # Создание графика
        fig, ax = plt.subplots()
        ax.bar(categories, expense_values, label='Расходы', color='red')
        ax.bar(categories, income_values, label='Доходы', color='green', bottom=expense_values)

        ax.set_xlabel('Категория')
        ax.set_ylabel('Сумма')
        ax.set_title('Статистика по категориям')
        ax.legend()

        # Отображение графика в окне Tkinter
        canvas = FigureCanvasTkAgg(fig, master=statistics_frame)
        canvas.get_tk_widget().pack()
        canvas.draw()

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить статистику: {e}")

# Создание главного окна
root = tk.Tk()
root.title("Учёт расходов")
root.geometry("800x600")

# Вкладки для формы и статистики
tab_control = ttk.Notebook(root)

# Вкладка с формой добавления транзакции
tab_form = ttk.Frame(tab_control)
tab_control.add(tab_form, text='Добавить транзакцию')

# Вкладка для отображения статистики
tab_stats = ttk.Frame(tab_control)
tab_control.add(tab_stats, text='Статистика')

tab_control.pack(expand=1, fill="both")

# Форма для добавления транзакции
form_frame = tk.Frame(tab_form)
form_frame.pack(padx=10, pady=10)

label_amount = tk.Label(form_frame, text="Сумма:")
label_amount.grid(row=0, column=0, padx=5, pady=5)
entry_amount = tk.Entry(form_frame)
entry_amount.grid(row=0, column=1, padx=5, pady=5)

label_category = tk.Label(form_frame, text="Категория:")
label_category.grid(row=1, column=0, padx=5, pady=5)
entry_category = tk.Entry(form_frame)
entry_category.grid(row=1, column=1, padx=5, pady=5)

label_date = tk.Label(form_frame, text="Дата (ГГГГ-ММ-ДД):")
label_date.grid(row=2, column=0, padx=5, pady=5)
entry_date = tk.Entry(form_frame)
entry_date.grid(row=2, column=1, padx=5, pady=5)

label_description = tk.Label(form_frame, text="Описание:")
label_description.grid(row=3, column=0, padx=5, pady=5)
entry_description = tk.Entry(form_frame)
entry_description.grid(row=3, column=1, padx=5, pady=5)

label_type = tk.Label(form_frame, text="Тип:")
label_type.grid(row=4, column=0, padx=5, pady=5)
combo_type = ttk.Combobox(form_frame, values=["income", "expense"])
combo_type.grid(row=4, column=1, padx=5, pady=5)

button_add = tk.Button(form_frame, text="Добавить", command=add_transaction)
button_add.grid(row=5, column=0, columnspan=2, pady=10)

# Таблица для отображения транзакций
tree = ttk.Treeview(tab_form, columns=("Дата", "Категория", "Сумма", "Тип", "Описание"), show="headings")
tree.heading("Дата", text="Дата")
tree.heading("Категория", text="Категория")
tree.heading("Сумма", text="Сумма")
tree.heading("Тип", text="Тип")
tree.heading("Описание", text="Описание")
tree.pack(fill="both", expand=True, padx=10, pady=10)

# Кнопка для отображения статистики
button_stats = tk.Button(tab_stats, text="Показать статистику", command=show_statistics)
button_stats.pack(pady=10)

# Фрейм для отображения графика
statistics_frame = tk.Frame(tab_stats)
statistics_frame.pack(padx=10, pady=10)

# Проверка и создание базы и таблицы при запуске
check_and_create_db_and_table()

# Загрузка и отображение транзакций при запуске
show_transactions()

# Запуск приложения
root.mainloop()
