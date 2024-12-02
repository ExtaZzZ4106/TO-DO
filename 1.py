import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector

class Task:
    def __init__(self, id, title, priority, deadline, status=False):
        self.id = id
        self.title = title
        self.priority = priority
        self.deadline = deadline
        self.status = status

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Список дел")
        self.root.geometry('500x500')

        # Подключение к БД
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",  # укажите свое имя пользователя
            password="0000",  # укажите свой пароль
        )
        self.cursor = self.conn.cursor()

        # Создание базы данных, если она не существует
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS todo_db")
        self.conn.database = "todo_db"

        # Создание таблицы, если она не существует
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                priority ENUM('low', 'medium', 'high') NOT NULL,
                deadline DATE NOT NULL,
                status BOOLEAN DEFAULT FALSE
            )
        """)

        self.task_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50)
        self.task_listbox.pack(pady=10)

        self.add_task_button = tk.Button(root, text="Добавить задачу", command=self.add_task)
        self.add_task_button.pack(pady=5)

        self.edit_task_button = tk.Button(root, text="Редактировать задачу", command=self.edit_task)
        self.edit_task_button.pack(pady=5)

        self.delete_task_button = tk.Button(root, text="Удалить задачу", command=self.delete_task)
        self.delete_task_button.pack(pady=5)

        self.mark_completed_button = tk.Button(root, text="Отметить как выполненную", command=self.mark_completed)
        self.mark_completed_button.pack(pady=5)
        
        self.tasks = []  # Инициализация списка задач
        self.load_tasks()  # Загружаем задачи после создания элементов интерфейса

    def load_tasks(self):
        self.tasks.clear()  # Очищаем текущие задачи перед загрузкой из базы
        self.cursor.execute("SELECT * FROM tasks")
        for (id, title, priority, deadline, status) in self.cursor.fetchall():
            self.tasks.append(Task(id, title, priority, deadline, status))
        self.update_task_listbox()

    def add_task(self):
       title = simpledialog.askstring("Задача", "Введите название задачи:")
       priority = simpledialog.askstring("Приоритет", "Введите приоритет (low, medium, high):")
       deadline = simpledialog.askstring("Дедлайн", "Введите дедлайн (гггг-мм-дд):")

       # Проверка на допустимые значения приоритета
       if priority not in ['low', 'medium', 'high']:
           messagebox.showerror("Ошибка", "Приоритет должен быть 'low', 'medium' или 'high'.")
           return

       try:
           self.cursor.execute("INSERT INTO tasks (title, priority, deadline) VALUES (%s, %s, %s)", (title, priority, deadline))
           self.conn.commit()
           self.load_tasks()
       except mysql.connector.Error as err:
           print(f"Ошибка базы данных: {err}")
           messagebox.showerror("Ошибка", f"Ошибка базы данных: {err}")

    def edit_task(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            task = self.tasks[selected_index]
            title = simpledialog.askstring("Задача", "Введите новое название задачи:", initialvalue=task.title)
            if title:
                priority = simpledialog.askstring("Приоритет", "Введите новый приоритет:", initialvalue=task.priority)

                deadline = simpledialog.askstring("Дедлайн", "Введите новый дедлайн:", initialvalue=task.deadline)
                self.cursor.execute("UPDATE tasks SET title = %s, priority = %s, deadline = %s WHERE id = %s", (title, priority, deadline, task.id))
                self.conn.commit()
                self.load_tasks()
        except IndexError:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите задачу для редактирования.")

    def delete_task(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            task = self.tasks[selected_index]
            self.cursor.execute("DELETE FROM tasks WHERE id = %s", (task.id,))
            self.conn.commit()
            self.load_tasks()
        except IndexError:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите задачу для удаления.")

    def mark_completed(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            task = self.tasks[selected_index]
            task.status = not task.status
            self.cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (task.status, task.id))
            self.conn.commit()
            self.update_task_listbox()
        except IndexError:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите задачу для отметки.")

    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            status_str = "[Выполнено] " if task.status else "[Не выполнено] "
            self.task_listbox.insert(tk.END, f"{status_str}{task.title} (Приоритет: {task.priority}, Дедлайн: {task.deadline})")

    def __del__(self):
        try:
            if hasattr(self, 'cursor'):
                self.cursor.close()
        except AttributeError:
            pass
        finally:
            if hasattr(self, 'conn'):
                self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
