import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

DB = "sklad.db"


def sql(query, args=()):
    """Выполнить запрос и вернуть результат (если есть)"""
    conn = sqlite3.connect(DB)
    cur = conn.execute(query, args)
    result = cur.fetchall()
    conn.commit()
    conn.close()
    return result


class App:
    def __init__(self, root):
        self.root = root
        root.title("Склад")
        root.geometry("650x500")

        # поля ввода
        top = tk.Frame(root)
        top.pack(pady=8)

        tk.Label(top, text="Название").pack(side="left")
        self.name = tk.Entry(top, width=18)
        self.name.pack(side="left", padx=3)

        tk.Label(top, text="Кол-во").pack(side="left")
        self.qty = tk.Entry(top, width=6)
        self.qty.pack(side="left", padx=3)

        tk.Label(top, text="Цена ($)").pack(side="left")
        self.price = tk.Entry(top, width=6)
        self.price.pack(side="left", padx=3)

        tk.Button(top, text="Добавить", command=self.add).pack(side="left", padx=5)

        # таблица
        self.tree =ttk.Treeview(root, columns=("id", "name", "qty", "price"), show="headings")
        for c, t, w in [("id", "ID", 50), ("name", "Название", 250), ("qty", "Кол-во", 100), ("price", "Цена", 100)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # кнопки операций
        bot = tk.Frame(root)
        bot.pack(pady=8)

        tk.Label(bot, text="Кол-во:").pack(side="left")
        self.amount = tk.Entry(bot, width=6)
        self.amount.pack(side="left", padx=3)

        tk.Button(bot, text="Приход", command=lambda: self.change(1)).pack(side="left", padx=3)
        tk.Button(bot, text="Расход", command=lambda: self.change(-1)).pack(side="left", padx=3)
        tk.Button(bot, text="Удалить", command=self.delete).pack(side="left", padx=3)

        self.refresh()

    def add(self):
        try:
            name = self.name.get().strip()
            qty = int(self.qty.get())
            price = float(self.price.get())
            if not name:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Проверь поля! Название — текст, кол-во — число, цена — число")
            return

        sql("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
        self.name.delete(0, "end")
        self.qty.delete(0, "end")
        self.price.delete(0, "end")
        self.refresh()

    def change(self, sign):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Инфо", "Выбери товар")
            return
        try:
            amount = int(self.amount.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введи положительное число")
            return

        pid = self.tree.item(sel[0])["values"][0]
        qty = sql("SELECT quantity FROM products WHERE id=?", (pid,))[0][0]

        if sign == -1 and qty < amount:
            messagebox.showerror("Ошибка", f"На складе только {qty} шт.")
            return

        sql("UPDATE products SET quantity=? WHERE id=?", (qty + sign * amount, pid))
        self.amount.delete(0, "end")
        self.refresh()

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Инфо", "Выбери товар")
            return
        sql("DELETE FROM products WHERE id=?", (self.tree.item(sel[0])["values"][0],))
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in sql("SELECT id, name, quantity, price FROM products ORDER BY id"):
            self.tree.insert("", "end", values=row)


# создаём таблицу при запуске
sql("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, quantity INTEGER, price REAL)")

root = tk.Tk()
App(root)
root.mainloop()