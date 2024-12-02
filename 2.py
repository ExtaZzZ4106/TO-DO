import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Scrollbar, Frame
import mysql.connector

class PhoneBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Телефонный справочник")
        self.root.geometry('500x500')
        # Соединение с базой данных MySQL
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",          # Замените на ваше имя пользователя
            password="0000",      # Замените на ваш пароль
        )
        self.cursor = self.conn.cursor()
        
        # Создание базы данных, если она не существует
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS phonebook_db")
        self.conn.database = "phonebook_db"
        self.create_table()
        # UI
        self.create_widgets()

    def create_table(self):
        # Создание таблицы, если она не существует
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                phone VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(255),
                address TEXT
            )
        """)
        self.conn.commit()

    def create_widgets(self):
        # Поля ввода
        self.first_name_entry = tk.Entry(self.root)
        self.last_name_entry = tk.Entry(self.root)
        self.phone_entry = tk.Entry(self.root)
        self.email_entry = tk.Entry(self.root)
        self.address_entry = tk.Entry(self.root)

        # Метки
        tk.Label(self.root, text="Имя").pack()
        self.first_name_entry.pack()
        tk.Label(self.root, text="Фамилия").pack()
        self.last_name_entry.pack()
        tk.Label(self.root, text="Телефон").pack()
        self.phone_entry.pack()
        tk.Label(self.root, text="Email").pack()
        self.email_entry.pack()
        tk.Label(self.root, text="Адрес").pack()
        self.address_entry.pack()

        # Кнопки
        tk.Button(self.root, text="Добавить контакт", command=self.add_contact).pack()
        tk.Button(self.root, text="Редактировать контакт", command=self.edit_contact).pack()
        tk.Button(self.root, text="Удалить контакт", command=self.delete_contact).pack()

        # Поле поиска
        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack()
        tk.Button(self.root, text="Поиск", command=self.search_contacts).pack()

        # Список контактов
        self.contact_list = Listbox(self.root)
        self.contact_list.pack(fill=tk.BOTH, expand=True)

        self.load_contacts()

    def load_contacts(self):
        # Загружает контакты из базы данных
        self.contact_list.delete(0, tk.END)
        self.cursor.execute("SELECT * FROM contacts")
        for row in self.cursor.fetchall():
            self.contact_list.insert(tk.END, f"{row[1]} {row[2]} - {row[3]}")  # Имя Фамилия - Телефон

    def add_contact(self):

        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        address = self.address_entry.get()

        if not all([first_name, last_name, phone]):
            messagebox.showerror("Ошибка", "Заполните все обязательные поля.")
            return

        try:
            self.cursor.execute("INSERT INTO contacts (first_name, last_name, phone, email, address) VALUES (%s, %s, %s, %s, %s)",
                                (first_name, last_name, phone, email, address))
            self.conn.commit()
            self.load_contacts()
            messagebox.showinfo("Успех", "Контакт добавлен.")
        except mysql.connector.IntegrityError:
            messagebox.showerror("Ошибка", "Контакт с таким номером телефона уже существует.")

    def delete_contact(self):
        selected_index = self.contact_list.curselection()
        if selected_index:
            selected_contact = self.contact_list.get(selected_index).split(" - ")[-1]  # Получаем номер телефона
            self.cursor.execute("DELETE FROM contacts WHERE phone = %s", (selected_contact,))
            self.conn.commit()
            self.load_contacts()
            messagebox.showinfo("Успех", "Контакт удален.")
        else:
            messagebox.showerror("Ошибка", "Выберите контакт для удаления.")

    def edit_contact(self):
        selected_index = self.contact_list.curselection()
        if selected_index:
            selected_contact = self.contact_list.get(selected_index)
            phone = selected_contact.split(" - ")[-1]
            
            first_name = simpledialog.askstring("Изменить имя", "Введите новое имя:")
            last_name = simpledialog.askstring("Изменить фамилию", "Введите новую фамилию:")
            email = simpledialog.askstring("Изменить Email", "Введите новый Email:")
            address = simpledialog.askstring("Изменить адрес", "Введите новый адрес:")
            
            self.cursor.execute("UPDATE contacts SET first_name = %s, last_name = %s, email = %s, address = %s WHERE phone = %s",
                                (first_name, last_name, email, address, phone))
            self.conn.commit()
            self.load_contacts()
            messagebox.showinfo("Успех", "Контакт обновлен.")
        else:
            messagebox.showerror("Ошибка", "Выберите контакт для редактирования.")

    def search_contacts(self):
        search_term = self.search_entry.get()
        self.contact_list.delete(0, tk.END)
        self.cursor.execute("SELECT * FROM contacts WHERE first_name LIKE %s OR last_name LIKE %s OR phone LIKE %s",
                            (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        for row in self.cursor.fetchall():
            self.contact_list.insert(tk.END, f"{row[1]} {row[2]} - {row[3]}")

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneBookApp(root)
    root.mainloop()
