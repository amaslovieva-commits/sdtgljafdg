import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.expenses = []

        # Создаем поля для ввода
        self.create_input_fields()

        # Создаем таблицу и отображение суммы
        self.create_treeview()

        # Создаем фильтры и кнопки
        self.create_controls()

        # Загружаем данные из файла
        self.load_data()

    def create_input_fields(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        # Ввод суммы
        tk.Label(frame, text="Сумма:").grid(row=0, column=0, padx=5)
        self.amount_entry = tk.Entry(frame)
        self.amount_entry.grid(row=0, column=1, padx=5)

        # Ввод категории
        tk.Label(frame, text="Категория:").grid(row=0, column=2, padx=5)
        self.category_entry = tk.Entry(frame)
        self.category_entry.grid(row=0, column=3, padx=5)

        # Ввод даты
        tk.Label(frame, text="Дата (ДД-ММ-ГГГГ):").grid(row=0, column=4, padx=5)
        self.date_entry = tk.Entry(frame)
        self.date_entry.grid(row=0, column=5, padx=5)

    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)

        add_button = tk.Button(control_frame, text="Добавить расход", command=self.add_expense)
        add_button.pack(side=tk.LEFT, padx=5)

        # Фильтры
        filter_frame = tk.LabelFrame(self.root, text="Фильтры")
        filter_frame.pack(pady=10, fill="x", padx=5)

        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category = ttk.Combobox(filter_frame, values=["Все"])
        self.filter_category.current(0)
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Начальная дата:").grid(row=0, column=2, padx=5, pady=5)
        self.start_date_entry = tk.Entry(filter_frame)
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="Конечная дата:").grid(row=0, column=4, padx=5, pady=5)
        self.end_date_entry = tk.Entry(filter_frame)
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5)

        filter_button = tk.Button(filter_frame, text="Фильтровать", command=self.apply_filters)
        filter_button.grid(row=0, column=6, padx=5, pady=5)

        show_all_button = tk.Button(filter_frame, text="Показать всё", command=self.show_all)
        show_all_button.grid(row=0, column=7, padx=5, pady=5)

    def create_treeview(self):
        columns = ("amount", "category", "date")
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=10)
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        self.tree.pack(padx=5, pady=5, fill="both", expand=True)

        self.total_label = tk.Label(self.root, text="Общая сумма: 0")
        self.total_label.pack(pady=5)

    def add_expense(self):
        amount_str = self.amount_entry.get()
        category = self.category_entry.get()
        date_str = self.date_entry.get()

        # Проверка суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительную сумму")
            return

        # Проверка даты
        try:
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите дату в формате ДД-ММ-ГГГГ")
            return

        expense = {
            "amount": amount,
            "category": category,
            "date": date_str
        }
        self.expenses.append(expense)
        self.update_treeview()
        self.save_data()

        # Очистка полей
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

        # Обновление фильтров
        self.update_filter_categories()

    def update_treeview(self, expenses=None):
        self.tree.delete(*self.tree.get_children())
        if expenses is None:
            expenses = self.expenses
        total = 0
        for exp in expenses:
            self.tree.insert('', tk.END, values=(exp["amount"], exp["category"], exp["date"]))
            total += exp["amount"]
        self.total_label.config(text=f"Общая сумма: {total:.2f}")

    def save_data(self):
        try:
            with open("expenses.json", "w", encoding="utf-8") as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")

    def load_data(self):
        try:
            with open("expenses.json", "r", encoding="utf-8") as f:
                self.expenses = json.load(f)
        except FileNotFoundError:
            self.expenses = []
        self.update_treeview()
        self.update_filter_categories()

    def update_filter_categories(self):
        categories = list({exp["category"] for exp in self.expenses})
        categories.sort()
        categories.insert(0, "Все")
        self.filter_category['values'] = categories
        self.filter_category.current(0)

    def apply_filters(self):
        category_filter = self.filter_category.get()
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        filtered = self.expenses

        # Фильтр по категории
        if category_filter != "Все":
            filtered = [exp for exp in filtered if exp["category"] == category_filter]

        # Фильтр по датам
        try:
            start_date = datetime.strptime(start_date_str, "%d-%m-%Y") if start_date_str else None
            end_date = datetime.strptime(end_date_str, "%d-%m-%Y") if end_date_str else None
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте формат дат")
            return

        if start_date:
            filtered = [exp for exp in filtered if datetime.strptime(exp["date"], "%d-%m-%Y") >= start_date]
        if end_date:
            filtered = [exp for exp in filtered if datetime.strptime(exp["date"], "%d-%m-%Y") <= end_date]

        self.update_treeview(filtered)

    def show_all(self):
        self.update_treeview()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
