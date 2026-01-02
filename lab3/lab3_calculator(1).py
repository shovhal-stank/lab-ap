# Лабораторная работа №3
# Научный калькулятор с графическим интерфейсом

import tkinter as tk
from tkinter import ttk, messagebox, Menu
import math
import re


class ScientificCalculator:
    """Научный калькулятор с графическим интерфейсом"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Научный калькулятор")
        self.root.geometry("400x600")
        self.root.minsize(350, 500)
        
        # Переменные
        self.display_var = tk.StringVar(value="0")
        self.current_value = "0"
        self.history = []
        self.memory = 0
        self.angle_mode = "DEG"  # DEG или RAD
        
        # Создание интерфейса
        self.create_menu()
        self.create_display()
        self.create_buttons()
        
        # Привязка клавиатуры
        self.bind_keyboard()
        
        # Центрирование окна
        self.center_window()
    
    def center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_menu(self):
        """Создает меню приложения"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Очистить историю", command=self.clear_history)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Вид"
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Размер: Маленький (350x500)", 
                             command=lambda: self.resize_window(350, 500))
        view_menu.add_command(label="Размер: Средний (400x600)", 
                             command=lambda: self.resize_window(400, 600))
        view_menu.add_command(label="Размер: Большой (500x700)", 
                             command=lambda: self.resize_window(500, 700))
        
        # Меню "Режим"
        mode_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Режим", menu=mode_menu)
        mode_menu.add_command(label="Градусы (DEG)", command=lambda: self.set_angle_mode("DEG"))
        mode_menu.add_command(label="Радианы (RAD)", command=lambda: self.set_angle_mode("RAD"))
        
        # Меню "Справка"
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Инструкция", command=self.show_help)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def create_display(self):
        """Создает дисплей калькулятора"""
        display_frame = tk.Frame(self.root, bg='#2c3e50', padx=10, pady=10)
        display_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        # Индикатор режима
        self.mode_label = tk.Label(display_frame, text=f"[{self.angle_mode}]", 
                                   font=('Arial', 10), bg='#2c3e50', fg='#ecf0f1')
        self.mode_label.pack(anchor='e')
        
        # Основной дисплей
        display = tk.Entry(display_frame, textvariable=self.display_var, 
                          font=('Arial', 24), justify='right', 
                          state='readonly', readonlybackground='#34495e', 
                          fg='#ecf0f1', relief='flat', borderwidth=0)
        display.pack(fill=tk.BOTH, ipady=10)
    
    def create_buttons(self):
        """Создает кнопки калькулятора"""
        # Основной контейнер для кнопок
        button_frame = tk.Frame(self.root, bg='#ecf0f1')
        button_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Конфигурация сетки для автоматического изменения размера
        for i in range(7):
            button_frame.grid_rowconfigure(i, weight=1)
        for i in range(5):
            button_frame.grid_columnconfigure(i, weight=1)
        
        # Определение кнопок (текст, строка, столбец, цвет)
        buttons = [
            # Строка 0: Память и специальные функции
            ('MC', 0, 0, '#95a5a6'), ('MR', 0, 1, '#95a5a6'), ('M+', 0, 2, '#95a5a6'), 
            ('M-', 0, 3, '#95a5a6'), ('MS', 0, 4, '#95a5a6'),
            
            # Строка 1: Тригонометрические функции
            ('sin', 1, 0, '#3498db'), ('cos', 1, 1, '#3498db'), ('tan', 1, 2, '#3498db'), 
            ('(', 1, 3, '#95a5a6'), (')', 1, 4, '#95a5a6'),
            
            # Строка 2: Степени и корни
            ('x²', 2, 0, '#3498db'), ('√', 2, 1, '#3498db'), ('xʸ', 2, 2, '#3498db'), 
            ('C', 2, 3, '#e74c3c'), ('⌫', 2, 4, '#e67e22'),
            
            # Строка 3: Логарифмы
            ('ln', 3, 0, '#3498db'), ('log', 3, 1, '#3498db'), ('π', 3, 2, '#3498db'), 
            ('e', 3, 3, '#3498db'), ('÷', 3, 4, '#f39c12'),
            
            # Строка 4-6: Цифры и операции
            ('7', 4, 0, '#ecf0f1'), ('8', 4, 1, '#ecf0f1'), ('9', 4, 2, '#ecf0f1'), 
            ('×', 4, 3, '#f39c12'), ('1/x', 4, 4, '#3498db'),
            
            ('4', 5, 0, '#ecf0f1'), ('5', 5, 1, '#ecf0f1'), ('6', 5, 2, '#ecf0f1'), 
            ('-', 5, 3, '#f39c12'), ('|x|', 5, 4, '#3498db'),
            
            ('1', 6, 0, '#ecf0f1'), ('2', 6, 1, '#ecf0f1'), ('3', 6, 2, '#ecf0f1'), 
            ('+', 6, 3, '#f39c12'), ('±', 6, 4, '#3498db'),
            
            ('0', 7, 0, '#ecf0f1'), ('.', 7, 1, '#ecf0f1'), ('=', 7, 2, '#27ae60'),
        ]
        
        # Кнопка 0 занимает 2 столбца, = занимает 2 столбца
        for btn_text, row, col, color in buttons:
            if btn_text == '0':
                colspan = 1
            elif btn_text == '=':
                colspan = 3
            else:
                colspan = 1
            
            btn = tk.Button(button_frame, text=btn_text, 
                          command=lambda t=btn_text: self.on_button_click(t),
                          font=('Arial', 14, 'bold'), bg=color, fg='#2c3e50',
                          relief='flat', borderwidth=0, cursor='hand2')
            btn.grid(row=row, column=col, columnspan=colspan, 
                    sticky='nsew', padx=2, pady=2)
            
            # Эффект при наведении
            btn.bind('<Enter>', lambda e, b=btn, c=color: 
                    b.config(bg=self.lighten_color(c)))
            btn.bind('<Leave>', lambda e, b=btn, c=color: 
                    b.config(bg=c))
    
    def lighten_color(self, color):
        """Осветляет цвет для эффекта hover"""
        colors = {
            '#ecf0f1': '#ffffff',
            '#f39c12': '#f5b041',
            '#3498db': '#5dade2',
            '#27ae60': '#52be80',
            '#e74c3c': '#ec7063',
            '#e67e22': '#eb984e',
            '#95a5a6': '#aab7b8'
        }
        return colors.get(color, color)
    
    def bind_keyboard(self):
        """Привязывает клавиатурные сочетания"""
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<Return>', lambda e: self.on_button_click('='))
        self.root.bind('<Escape>', lambda e: self.on_button_click('C'))
        self.root.bind('<BackSpace>', lambda e: self.on_button_click('⌫'))
    
    def on_key_press(self, event):
        """Обработка нажатий клавиш"""
        key = event.char
        if key.isdigit() or key in '.+-*/()':
            if key == '*':
                self.on_button_click('×')
            elif key == '/':
                self.on_button_click('÷')
            else:
                self.on_button_click(key)
    
    def on_button_click(self, button_text):
        """Обработка нажатий кнопок"""
        try:
            if button_text == 'C':
                self.clear_display()
            elif button_text == '⌫':
                self.backspace()
            elif button_text == '=':
                self.calculate()
            elif button_text in ['MC', 'MR', 'M+', 'M-', 'MS']:
                self.memory_operation(button_text)
            elif button_text in ['sin', 'cos', 'tan', 'ln', 'log', '√', 'x²', '1/x', '|x|', '±']:
                self.scientific_operation(button_text)
            elif button_text in ['π', 'e']:
                self.insert_constant(button_text)
            elif button_text == 'xʸ':
                self.append_to_display('^')
            else:
                self.append_to_display(button_text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
            self.clear_display()
    
    def clear_display(self):
        """Очищает дисплей"""
        self.current_value = "0"
        self.display_var.set("0")
    
    def backspace(self):
        """Удаляет последний символ"""
        if self.current_value != "0":
            self.current_value = self.current_value[:-1]
            if not self.current_value:
                self.current_value = "0"
            self.display_var.set(self.current_value)
    
    def append_to_display(self, text):
        """Добавляет символ на дисплей"""
        if self.current_value == "0" and text.isdigit():
            self.current_value = text
        else:
            self.current_value += text
        self.display_var.set(self.current_value)
    
    def insert_constant(self, constant):
        """Вставляет математическую константу"""
        if self.current_value == "0":
            self.current_value = ""
        if constant == 'π':
            self.current_value += str(math.pi)
        elif constant == 'e':
            self.current_value += str(math.e)
        self.display_var.set(self.current_value)
    
    def scientific_operation(self, operation):
        """Выполняет научную операцию"""
        try:
            # Получаем текущее число
            expr = self.current_value
            value = self.evaluate_expression(expr)
            
            if operation == 'sin':
                result = math.sin(self.to_radians(value))
            elif operation == 'cos':
                result = math.cos(self.to_radians(value))
            elif operation == 'tan':
                result = math.tan(self.to_radians(value))
            elif operation == 'ln':
                if value <= 0:
                    raise ValueError("ln: значение должно быть положительным")
                result = math.log(value)
            elif operation == 'log':
                if value <= 0:
                    raise ValueError("log: значение должно быть положительным")
                result = math.log10(value)
            elif operation == '√':
                if value < 0:
                    raise ValueError("√: значение не может быть отрицательным")
                result = math.sqrt(value)
            elif operation == 'x²':
                result = value ** 2
            elif operation == '1/x':
                if value == 0:
                    raise ValueError("Деление на ноль")
                result = 1 / value
            elif operation == '|x|':
                result = abs(value)
            elif operation == '±':
                result = -value
            
            self.current_value = str(result)
            self.display_var.set(self.format_result(result))
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка вычисления: {str(e)}")
            self.clear_display()
    
    def to_radians(self, degrees):
        """Преобразует градусы в радианы если нужно"""
        if self.angle_mode == "DEG":
            return math.radians(degrees)
        return degrees
    
    def calculate(self):
        """Вычисляет выражение"""
        try:
            expr = self.current_value
            
            # Сохраняем в историю
            self.history.append(expr)
            
            # Вычисляем
            result = self.evaluate_expression(expr)
            
            # Отображаем результат
            self.current_value = str(result)
            self.display_var.set(self.format_result(result))
            
        except ZeroDivisionError:
            messagebox.showerror("Ошибка", "Деление на ноль")
            self.clear_display()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка вычисления: {str(e)}")
            self.clear_display()
    
    def evaluate_expression(self, expr):
        """Безопасно вычисляет математическое выражение"""
        # Заменяем символы
        expr = expr.replace('×', '*').replace('÷', '/').replace('^', '**')
        
        # Безопасное вычисление через eval с ограниченным namespace
        allowed_names = {
            'abs': abs, 'round': round, 'pow': pow,
            'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos,
            'tan': math.tan, 'log': math.log, 'log10': math.log10,
            'pi': math.pi, 'e': math.e
        }
        
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        return result
    
    def format_result(self, result):
        """Форматирует результат для отображения"""
        # Если очень маленькое или большое число - научный формат
        if abs(result) < 0.0001 and result != 0:
            return f"{result:.6e}"
        elif abs(result) > 1e10:
            return f"{result:.6e}"
        else:
            # Обычный формат, убираем лишние нули
            formatted = f"{result:.10f}".rstrip('0').rstrip('.')
            return formatted
    
    def memory_operation(self, operation):
        """Операции с памятью"""
        try:
            if operation == 'MC':
                self.memory = 0
                messagebox.showinfo("Память", "Память очищена")
            elif operation == 'MR':
                self.current_value = str(self.memory)
                self.display_var.set(self.format_result(self.memory))
            elif operation == 'M+':
                value = self.evaluate_expression(self.current_value)
                self.memory += value
                messagebox.showinfo("Память", f"Добавлено в память: {value}")
            elif operation == 'M-':
                value = self.evaluate_expression(self.current_value)
                self.memory -= value
                messagebox.showinfo("Память", f"Вычтено из памяти: {value}")
            elif operation == 'MS':
                value = self.evaluate_expression(self.current_value)
                self.memory = value
                messagebox.showinfo("Память", f"Сохранено в память: {value}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка памяти: {str(e)}")
    
    def set_angle_mode(self, mode):
        """Устанавливает режим углов (градусы/радианы)"""
        self.angle_mode = mode
        self.mode_label.config(text=f"[{mode}]")
        messagebox.showinfo("Режим", f"Режим изменен на: {mode}")
    
    def resize_window(self, width, height):
        """Изменяет размер окна"""
        self.root.geometry(f"{width}x{height}")
        self.center_window()
    
    def clear_history(self):
        """Очищает историю вычислений"""
        self.history = []
        messagebox.showinfo("История", "История очищена")
    
    def show_help(self):
        """Показывает справку"""
        help_text = """
НАУЧНЫЙ КАЛЬКУЛЯТОР - ИНСТРУКЦИЯ

ОСНОВНЫЕ ОПЕРАЦИИ:
+ - × ÷  Базовые арифметические операции
x²       Возведение в квадрат
xʸ       Возведение в степень (используйте ^)
√        Квадратный корень
1/x      Обратное значение
|x|      Модуль числа
±        Смена знака

ТРИГОНОМЕТРИЯ:
sin, cos, tan  Тригонометрические функции
Режим: DEG (градусы) или RAD (радианы)

ЛОГАРИФМЫ:
ln       Натуральный логарифм
log      Десятичный логарифм

КОНСТАНТЫ:
π        Число Пи (3.14159...)
e        Число Эйлера (2.71828...)

ПАМЯТЬ:
MC       Очистить память
MR       Прочитать из памяти
M+       Добавить к памяти
M-       Вычесть из памяти
MS       Сохранить в память

КЛАВИШИ:
Enter    Вычислить (=)
Esc      Очистить (C)
Backspace Удалить символ (⌫)
0-9, +, -, *, /, .  Ввод с клавиатуры
        """
        messagebox.showinfo("Справка", help_text)
    
    def show_about(self):
        """Показывает информацию о программе"""
        about_text = """
НАУЧНЫЙ КАЛЬКУЛЯТОР
Версия 1.0

Лабораторная работа №3
Приложения с графическим интерфейсом

Возможности:
• Базовые арифметические операции
• Научные функции
• Тригонометрия
• Логарифмы
• Работа с памятью
• Настраиваемый размер окна
• Поддержка клавиатуры

© 2024
        """
        messagebox.showinfo("О программе", about_text)
    
    def run(self):
        """Запускает приложение"""
        self.root.mainloop()


def main():
    """Главная функция"""
    try:
        root = tk.Tk()
        app = ScientificCalculator(root)
        app.run()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", 
                            f"Не удалось запустить приложение: {str(e)}")


if __name__ == "__main__":
    main()
