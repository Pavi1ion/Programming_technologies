import tkinter as tk
from tkinter import ttk, messagebox
import logging
from model import FuelPrice, DataHandler, FuelPriceParseError

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная работа №3 – Цены на топливо")
        self.geometry("700x500")
        self.data_file = "data.txt"
        self.items = []
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        # Таблица
        columns = ("Тип топлива", "Дата", "Цена (руб.)")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Панель ввода
        frame = tk.Frame(self)
        frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(frame, text="Новый объект:").pack(side=tk.LEFT)
        self.entry = tk.Entry(frame, width=50)
        self.entry.pack(side=tk.LEFT, padx=5)
        self.entry.bind("<Return>", lambda e: self._add_item())

        add_btn = tk.Button(frame, text="Добавить", command=self._add_item)
        add_btn.pack(side=tk.LEFT, padx=2)
        del_btn = tk.Button(frame, text="Удалить", command=self._delete_item)
        del_btn.pack(side=tk.LEFT, padx=2)

        # Статусная строка
        self.status_var = tk.StringVar()
        status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_data(self):
        self.items = DataHandler.load(self.data_file)
        self._refresh_table()
        self._show_status(f"Загружено {len(self.items)} записей")

    def _save_data(self):
        DataHandler.save(self.data_file, self.items)
        self._show_status("Данные сохранены")

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in self.items:
            self.tree.insert("", tk.END, values=(
                item.type,
                item.date.strftime("%Y.%m.%d"),
                f"{item.price:.2f}"
            ))

    def _add_item(self):
        text = self.entry.get().strip()
        if not text:
            messagebox.showwarning("Ввод", "Введите строку в формате:\n\"тип\" гггг.мм.дд цена")
            return

        try:
            new_item = FuelPrice.from_string(text)
            # Проверка на дубликат (опционально, но полезно)
            for it in self.items:
                if (it.type == new_item.type and
                    it.date == new_item.date and
                    abs(it.price - new_item.price) < 0.0001):
                    messagebox.showwarning("Дубликат", "Такая запись уже существует")
                    return
            self.items.append(new_item)
            self._save_data()
            self._refresh_table()
            self.entry.delete(0, tk.END)
            self._show_status(f"Добавлено: {new_item.type}")
        except FuelPriceParseError as e:
            # Логируем ошибку и показываем сообщение
            logging.error(f"Ошибка добавления: {e} | Строка: {text}")
            messagebox.showerror("Ошибка формата", str(e))

    def _delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Удаление", "Выделите строку для удаления")
            return
        idx = self.tree.index(selected[0])
        deleted = self.items.pop(idx)
        self._save_data()
        self._refresh_table()
        self._show_status(f"Удалено: {deleted.type}")

    def _show_status(self, msg, timeout=3000):
        self.status_var.set(msg)
        self.after(timeout, lambda: self.status_var.set(""))