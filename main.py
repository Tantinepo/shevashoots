import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from datetime import datetime
import re
import csv
import pickle
import threading
import time


def clear_log():
    log.delete("1.0", tk.END)


def save_data():
    call_sign = call_sign_entry.get()
    if not call_sign:
        call_sign = 'Unknown'

    date_time = datetime.now().strftime('%d.%m.%y %H:%M')
    aim = aim_entry.get()
    inclinometer = inclinometer_var.get()
    projectile = projectile_var.get()
    charge = charge_var.get()
    quantity = quantity_entry.get()

    data_row = f"{date_time}\t{aim}\t{inclinometer}\t{projectile}\t{charge}\t{quantity}\n"

    with open("data.txt", "a") as file:
        # Записуємо заголовки стовпців, якщо файл порожній
        if file.tell() == 0:
            file.write("Дата-Час\tПриціл\tКутомір\tСнаряд\tЗаряд\tКількість\n")

        file.write(data_row)

    update_log()
    calculate_sum()  # Оновити суму

    # Перевірка, чи є новий день
    current_date = datetime.now().strftime('%d.%m.%y')
    with open("data.txt", "r") as file:
        last_line = file.readlines()[-1]
        last_date = last_line.split('\t')[0].split(' ')[0]

    if current_date != last_date:
        # Записуємо суму на новому рядку
        with open("data.txt", "a") as file:
            file.write(f"{current_date}\t\t\t\t\t{str(total)}\n")

        # Обнуляємо суму
        total = 0

    # Очистка полів
    aim_entry.delete(0, tk.END)
    inclinometer_entry.delete(0, tk.END)
    projectile_var.set(projectile_choices[0])
    charge_var.set(charge_choices[0])
    quantity_var.set('0')

    # Очищення вікна журналу
    clear_log()


def update_log_entry(data_row):
    log.insert(tk.END, data_row)


def save_shot():
    call_sign = call_sign_entry.get()
    if not call_sign:
        call_sign = 'Unknown'

    date_time = datetime.now().strftime('%d.%m.%y %H:%M')
    aim = aim_entry.get()
    inclinometer = inclinometer_var.get()
    projectile = projectile_var.get()
    charge = charge_var.get()
    quantity = quantity_entry.get()

    data_row = f"{date_time}\t{aim}\t{inclinometer}\t{projectile}\t{charge}\t{quantity}\n"

    with open("shots.txt", "a") as file:
        # Записуємо заголовки стовпців, якщо файл порожній
        if file.tell() == 0:
            file.write("Дата-Час\tПриціл\tКутомір\tСнаряд\tЗаряд\tКількість\n")

        file.write(data_row)

    # Оновлюємо значення Кількості
    try:
        quantity_int = int(quantity)
        quantity_int += 1
    except ValueError:
        quantity_int = 1
    quantity_var.set(str(quantity_int))

    # Запускаємо таймер
    start_timer()

    # Оновлення журналу
    update_log_entry(data_row)



def validate_inclinometer_input(event):
    text = inclinometer_var.get()

    # Вставка дефісу (-) після двох введених цифр
    if len(text) == 2 and text[-1] != '-':
        text += '-'

    # Обмеження кількості цифр після дефісу (-) на дві
    parts = text.split('-')
    if len(parts) == 2:
        first_part = parts[0][:2]
        second_part = parts[1][:2]
        text = f"{first_part}-{second_part}"

    # Обмеження максимальної довжини поля на 5 символів
    if len(text) > 5:
        text = text[:5]

    # Перевірка правильності формату
    if not re.match(r'^\d{0,2}-\d{0,2}$', text):
        inclinometer_entry.config(bg='red')
    else:
        inclinometer_entry.config(bg='white')

    inclinometer_var.set(text)


def validate_aim_input(new_value):
    if new_value == '' or (new_value.isdigit() and 0 <= int(new_value) <= 1500):
        aim_entry.config(bg='white')
        return True
    else:
        aim_entry.config(bg='red')
        return False


def add_projectile():
    new_projectile = simpledialog.askstring("Додати Снаряд", "Введіть назву нового снаряда:")
    if new_projectile:
        projectile_choices.append(new_projectile)
        projectile_menu['menu'].add_command(label=new_projectile,
                                            command=lambda v=new_projectile: projectile_var.set(v))
        save_projectile_choices()


def add_charge():
    new_charge = simpledialog.askstring("Додати Заряд", "Введіть назву нового заряду:")
    if new_charge:
        charge_choices.append(new_charge)
        charge_menu['menu'].add_command(label=new_charge, command=lambda v=new_charge: charge_var.set(v))
        save_charge_choices()


def save_projectile_choices():
    save_data_to_file(projectile_choices, "projectiles.pkl")


def save_charge_choices():
    save_data_to_file(charge_choices, "charges.pkl")


def load_projectile_choices():
    return load_data_from_file("projectiles.pkl")


def load_charge_choices():
    return load_data_from_file("charges.pkl")


def update_timer():
    if timer_running.get():
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time / 60)
        seconds = int(elapsed_time % 60)
        timer_var.set(f"{minutes:02d}:{seconds:02d}")
    root.after(1000, update_timer)


def start_timer():
    global start_time
    start_time = time.time()
    timer_running.set(True)


def stop_timer():
    timer_running.set(False)


def reset_timer():
    timer_running.set(False)
    timer_var.set("00:00")


def update_log():
    log_text = ""
    with open("data.txt", "r") as file:
        for line in file:
            log_text += line

    log.delete("1.0", tk.END)
    log.insert(tk.END, log_text)


def calculate_sum():
    total = 0
    with open("data.txt", "r") as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader)  # Пропускаємо заголовки стовпців
        for row in reader:
            quantity = int(row[5])  # Кількість - шостий стовпець
            total += quantity
    sum_value.config(text=str(total))


def save_data_to_file(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(data, file)


def load_data_from_file(filename):
    try:
        with open(filename, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return None


def show_archive():
    archive_window = tk.Toplevel(root)
    archive_window.title("Архів Стрільби")

    table = ttk.Treeview(archive_window)
    table.pack()

    # Заголовки стовпців
    table['columns'] = ('Дата-Час', 'Приціл', 'Кутомір', 'Снаряд', 'Заряд', 'Кількість')
    table.column('#0', width=0, stretch=tk.NO)
    table.column('Дата-Час', anchor=tk.CENTER, width=150)
    table.column('Приціл', anchor=tk.CENTER, width=100)
    table.column('Кутомір', anchor=tk.CENTER, width=100)
    table.column('Снаряд', anchor=tk.CENTER, width=100)
    table.column('Заряд', anchor=tk.CENTER, width=100)
    table.column('Кількість', anchor=tk.CENTER, width=100)

    table.heading('#0', text='')
    table.heading('Дата-Час', text='Дата-Час', anchor=tk.CENTER)
    table.heading('Приціл', text='Приціл', anchor=tk.CENTER)
    table.heading('Кутомір', text='Кутомір', anchor=tk.CENTER)
    table.heading('Снаряд', text='Снаряд', anchor=tk.CENTER)
    table.heading('Заряд', text='Заряд', anchor=tk.CENTER)
    table.heading('Кількість', text='Кількість', anchor=tk.CENTER)

    with open("data.txt", "r") as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            table.insert(parent='', index='end', values=row)

    # Додавання загальної суми
    total = 0
    with open("data.txt", "r") as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader)  # Пропускаємо заголовки стовпців
        for row in reader:
            quantity = int(row[5])  # Кількість - шостий стовпець
            total += quantity

    sum_label = tk.Label(archive_window, text="Загальна витрата:")
    sum_label.pack(side=tk.BOTTOM)

    sum_value = tk.Label(archive_window, text=str(total))
    sum_value.pack(side=tk.BOTTOM)



def show_shot_archive():
    archive_window = tk.Toplevel(root)
    archive_window.title("Архів пострілів")

    table = ttk.Treeview(archive_window)
    table.pack()

    # Заголовки стовпців
    table['columns'] = ('Дата-Час', 'Приціл', 'Кутомір', 'Снаряд', 'Заряд', 'Кількість')
    table.column('#0', width=0, stretch=tk.NO)
    table.column('Дата-Час', anchor=tk.CENTER, width=150)
    table.column('Приціл', anchor=tk.CENTER, width=100)
    table.column('Кутомір', anchor=tk.CENTER, width=100)
    table.column('Снаряд', anchor=tk.CENTER, width=100)
    table.column('Заряд', anchor=tk.CENTER, width=100)
    table.column('Кількість', anchor=tk.CENTER, width=100)

    table.heading('#0', text='')
    table.heading('Дата-Час', text='Дата-Час', anchor=tk.CENTER)
    table.heading('Приціл', text='Приціл', anchor=tk.CENTER)
    table.heading('Кутомір', text='Кутомір', anchor=tk.CENTER)
    table.heading('Снаряд', text='Снаряд', anchor=tk.CENTER)
    table.heading('Заряд', text='Заряд', anchor=tk.CENTER)
    table.heading('Кількість', text='Кількість', anchor=tk.CENTER)

    with open("shots.txt", "r") as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader)  # Пропускаємо заголовки стовпців
        for row in reader:
            table.insert(parent='', index='end', values=row)


root = tk.Tk()
root.title("Журнал артилерійської стрільби - автор Шевцов Василь shevabiz@gmail.com")

# Кнопки архіву
archive_button = tk.Button(root, text="Архів стрільби", command=show_archive)
archive_button.pack(side=tk.TOP, pady=5)

shot_archive_button = tk.Button(root, text="Архів пострілів", command=show_shot_archive)
shot_archive_button.pack(side=tk.TOP, pady=5)

# Таймер
timer_frame = tk.Frame(root)
timer_frame.pack(side=tk.TOP, pady=10)

timer_var = tk.StringVar()
timer_var.set("00:00")

timer_label = tk.Label(timer_frame, text="Таймер:")
timer_label.pack()

timer_display = tk.Label(timer_frame, textvariable=timer_var, font=('Arial', 20), width=5, relief=tk.SUNKEN)
timer_display.pack()

timer_running = tk.BooleanVar()
timer_running.set(False)

start_button = tk.Button(timer_frame, text="Старт", command=start_timer)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(timer_frame, text="Стоп", command=stop_timer)
stop_button.pack(side=tk.LEFT, padx=5)

reset_button = tk.Button(timer_frame, text="Скинути", command=reset_timer)
reset_button.pack(side=tk.LEFT, padx=5)

# Журнал
log_frame = tk.Frame(root)
log_frame.pack(side=tk.BOTTOM, pady=10)

log_label = tk.Label(log_frame, text="Журнал:")
log_label.pack()

log = tk.Text(log_frame, height=15, width=50)
log.pack()

# Сума
sum_label = tk.Label(root, text="Загальна витрата :")
sum_label.pack()

sum_value = tk.Label(root, text="0")
sum_value.pack()

# Позивний Entry
call_sign_label = tk.Label(root, text="Позивний:")
call_sign_label.pack()
call_sign_entry = tk.Entry(root, width=20, font=('Arial', 20))
call_sign_entry.pack()

# Приціл Entry
aim_label = tk.Label(root, text="Приціл (максимум 1500):")
aim_label.pack()
aim_entry = tk.Entry(root, validate="key")
aim_entry['validatecommand'] = (aim_entry.register(validate_aim_input), '%P')
aim_entry.pack()

# Кутомір Entry
inclinometer_label = tk.Label(root, text="Кутомір (формат xx-xx):")
inclinometer_label.pack()
inclinometer_var = tk.StringVar()
inclinometer_entry = tk.Entry(root, textvariable=inclinometer_var, width=8, font=('Arial', 16))
inclinometer_entry.pack()
inclinometer_entry.bind('<KeyRelease>', validate_inclinometer_input)

# Опції для Снаряду
projectile_label = tk.Label(root, text="Снаряд:")
projectile_label.pack()
projectile_choices = load_projectile_choices()
if projectile_choices is None:
    projectile_choices = ['107', 'NM', '795']
projectile_var = tk.StringVar(root)
projectile_var.set(projectile_choices[0])
projectile_menu = tk.OptionMenu(root, projectile_var, *projectile_choices)
projectile_menu.pack()

# Опції для Заряду
charge_label = tk.Label(root, text="Заряд:")
charge_label.pack()
charge_choices = load_charge_choices()
if charge_choices is None:
    charge_choices = ['119', 'M4A2', '203']
charge_var = tk.StringVar(root)
charge_var.set(charge_choices[0])
charge_menu = tk.OptionMenu(root, charge_var, *charge_choices)
charge_menu.pack()

# Поле Кількість
quantity_label = tk.Label(root, text="Кількість:")
quantity_label.pack()
quantity_var = tk.StringVar()
quantity_var.set("0")  # Зміна початкового значення з 1 на 0
quantity_entry = tk.Entry(root, textvariable=quantity_var)
quantity_entry.pack()

# Кнопки
add_projectile_button = tk.Button(root, text="+С", command=add_projectile)
add_projectile_button.pack()

add_charge_button = tk.Button(root, text="+З", command=add_charge)
add_charge_button.pack()

save_button = tk.Button(root, text="Записати стрільбу", command=save_data, width=15, bg="#404040", fg="white")
save_button.pack(side=tk.RIGHT)

save_shot_button = tk.Button(root, text="Записати постріл", command=save_shot, width=15,bg="#686868", fg="white")
save_shot_button.pack(side=tk.LEFT)

# Оновлюємо таймер кожну секунду
update_timer()

root.mainloop()

# v.0.2  додав поле Позивний і записав його в назві лог файлу WORK
# v.0.2.1 змінив ввивід інформації в файл
# v.0.2.2 додав кнопку "Запис стрільки" яка додає кожний постріл в файл shots.txt
# v.0.2.3 добавив можливість вносити назви Снарядів і Зарядів
# v.0.2.4 добавив збереження даних  Снарядів і Зарядів після перезапуску програми
# v.0.2.5 додав функцію при кожному натисканні на кнопку постріл добавляється +1 в полі кількість
# v.0.2.6 додав зміни при натиску на кнопку записати постріл , включається таймер і при натиску на кнопку Записати стрільбу обнулюються поля
# v.0.2.7 додав кнопку Архів стрільби в якій відображаються дані в новому вікні з файлу data.txt
# v.0.2.8 додав поле сума в якому відображається виртрати і кожного дня перезаписується
# v.0.2.9 додав кнопку Архів пострілів

#pyinstaller --onefile --icon=my_icon.ico my_script.py
