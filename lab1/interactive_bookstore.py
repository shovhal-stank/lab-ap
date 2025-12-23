import json
import xml.etree.ElementTree as ET
import os


class BookStoreException(Exception):
    """Собственное исключение для магазина книг"""
    pass


class Book:
    def __init__(self, title, author, price, book_id):
        if not title or not author:
            raise BookStoreException("Название и автор книги обязательны")
        if price <= 0:
            raise ValueError("Цена должна быть положительной")
        
        self.title = title
        self.author = author
        self.price = price
        self.book_id = book_id
    
    def __str__(self):
        return f"[{self.book_id}] '{self.title}' - {self.author} ({self.price} руб.)"


class Customer:
    def __init__(self, name, email):
        if not name or not email:
            raise BookStoreException("Имя и email обязательны")
        if "@" not in email:
            raise ValueError("Некорректный email")
        
        self.name = name
        self.email = email
        self.purchased_books = []
        self.balance = 0
    
    def add_balance(self, amount):
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        self.balance += amount
    
    def buy_book(self, book):
        if self.balance < book.price:
            raise BookStoreException(f"Недостаточно средств! Нужно: {book.price} руб., у вас: {self.balance} руб.")
        self.balance -= book.price
        self.purchased_books.append(book)
    
    def __str__(self):
        return f"{self.name} ({self.email}) | Баланс: {self.balance} руб. | Куплено книг: {len(self.purchased_books)}"


class BookStore:
    def __init__(self):
        self.books = []
        self.customers = []
        self.current_customer = None
        self._init_books()
    
    def _init_books(self):
        """Инициализация магазина книгами"""
        self.books = [
            Book("Война и мир", "Л.Толстой", 599, 1),
            Book("Мастер и Маргарита", "М.Булгаков", 450, 2),
            Book("Преступление и наказание", "Ф.Достоевский", 399, 3),
            Book("1984", "Дж.Оруэлл", 350, 4),
            Book("Гарри Поттер", "Дж.Роулинг", 500, 5)
        ]
    
    def register_customer(self, name, email):
        for customer in self.customers:
            if customer.email == email:
                raise BookStoreException("Пользователь с таким email уже существует")
        
        customer = Customer(name, email)
        self.customers.append(customer)
        self.current_customer = customer
        return customer
    
    def login_customer(self, email):
        for customer in self.customers:
            if customer.email == email:
                self.current_customer = customer
                return customer
        raise BookStoreException("Пользователь не найден")
    
    def show_books(self):
        print("\n" + "="*60)
        print("КАТАЛОГ КНИГ:")
        print("="*60)
        for book in self.books:
            print(book)
        print("="*60)
    
    def show_my_books(self):
        if not self.current_customer:
            print("Сначала войдите в систему")
            return
        
        print("\n" + "="*60)
        print(f"МОИ КНИГИ ({self.current_customer.name}):")
        print("="*60)
        if self.current_customer.purchased_books:
            for book in self.current_customer.purchased_books:
                print(book)
        else:
            print("У вас пока нет купленных книг")
        print("="*60)
    
    def save_to_json(self, filename="lab1/bookstore_data.json"):
        """Сохраняет данные в JSON"""
        try:
            data = {
                "books": [
                    {"title": b.title, "author": b.author, "price": b.price, "id": b.book_id}
                    for b in self.books
                ],
                "customers": [
                    {"name": c.name, "email": c.email, "balance": c.balance,
                     "purchased": [b.book_id for b in c.purchased_books]}
                    for c in self.customers
                ]
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Данные успешно сохранены в {filename}")
        except IOError as e:
            print(f"Ошибка записи в файл: {e}")
    
    def save_to_xml(self, filename="lab1/bookstore_data.xml"):
        """Сохраняет данные в XML"""
        try:
            # Создаём корневой элемент
            root = ET.Element('bookstore')
            
            # Секция с книгами
            books_elem = ET.SubElement(root, 'books')
            for book in self.books:
                book_elem = ET.SubElement(books_elem, 'book', id=str(book.book_id))
                
                title_elem = ET.SubElement(book_elem, 'title')
                title_elem.text = book.title
                
                author_elem = ET.SubElement(book_elem, 'author')
                author_elem.text = book.author
                
                price_elem = ET.SubElement(book_elem, 'price')
                price_elem.text = str(book.price)
            
            # Секция с покупателями
            customers_elem = ET.SubElement(root, 'customers')
            for customer in self.customers:
                customer_elem = ET.SubElement(customers_elem, 'customer')
                
                name_elem = ET.SubElement(customer_elem, 'name')
                name_elem.text = customer.name
                
                email_elem = ET.SubElement(customer_elem, 'email')
                email_elem.text = customer.email
                
                balance_elem = ET.SubElement(customer_elem, 'balance')
                balance_elem.text = str(customer.balance)
                
                # Купленные книги
                if customer.purchased_books:
                    purchased_elem = ET.SubElement(customer_elem, 'purchased_books')
                    for book in customer.purchased_books:
                        book_id_elem = ET.SubElement(purchased_elem, 'book_id')
                        book_id_elem.text = str(book.book_id)
            
            # Создаём дерево и сохраняем
            tree = ET.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            
            print(f"Данные успешно сохранены в {filename}")
            
        except Exception as e:
            print(f"Ошибка при сохранении XML: {e}")
    
    def load_from_json(self, filename="lab1/bookstore_data.json"):
        """Загружает данные из JSON"""
        try:
            if not os.path.exists(filename):
                return
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.customers = []
            for c in data['customers']:
                customer = Customer(c['name'], c['email'])
                customer.balance = c['balance']
                for book_id in c['purchased']:
                    book = next((b for b in self.books if b.book_id == book_id), None)
                    if book:
                        customer.purchased_books.append(book)
                self.customers.append(customer)
        except (FileNotFoundError, json.JSONDecodeError):
            pass


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def run():
    store = BookStore()
    store.load_from_json()
    
    print("=" * 60)
    print("         ЦИФРОВОЙ МАГАЗИН КНИГ")
    print("=" * 60)
    
    while True:
        if not store.current_customer:
            print("\n" + "=" * 60)
            print("ГЛАВНОЕ МЕНЮ:")
            print("=" * 60)
            print("1. Войти")
            print("2. Зарегистрироваться")
            print("3. Просмотреть каталог книг")
            print("0. Выход")
            print("=" * 60)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == '1':
                try:
                    email = input("Email: ").strip()
                    customer = store.login_customer(email)
                    print(f"\nДобро пожаловать, {customer.name}!")
                except BookStoreException as e:
                    print(f"\nОшибка: {e}")
            
            elif choice == '2':
                try:
                    name = input("Ваше имя: ").strip()
                    email = input("Email: ").strip()
                    customer = store.register_customer(name, email)
                    print(f"\nРегистрация успешна! Добро пожаловать, {customer.name}!")
                except (BookStoreException, ValueError) as e:
                    print(f"\nОшибка: {e}")
            
            elif choice == '3':
                store.show_books()
            
            elif choice == '0':
                print("\nДо свидания!")
                break
            
            else:
                print("\nНеверный выбор")
        
        else:
            print("\n" + "=" * 60)
            print(f"Пользователь: {store.current_customer.name}")
            print(f"Баланс: {store.current_customer.balance} руб.")
            print("=" * 60)
            print("1. Просмотреть каталог")
            print("2. Мои книги")
            print("3. Купить книгу")
            print("4. Пополнить баланс")
            print("5. Сохранить данные")
            print("6. Выйти из аккаунта")
            print("0. Завершить программу")
            print("=" * 60)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == '1':
                store.show_books()
            
            elif choice == '2':
                store.show_my_books()
            
            elif choice == '3':
                try:
                    store.show_books()
                    book_id = int(input("\nВведите ID книги: "))
                    book = next((b for b in store.books if b.book_id == book_id), None)
                    
                    if not book:
                        print("\nКнига не найдена")
                    else:
                        store.current_customer.buy_book(book)
                        print(f"\nКнига '{book.title}' успешно куплена!")
                        print(f"Остаток на балансе: {store.current_customer.balance} руб.")
                        store.save_to_json()
                except ValueError:
                    print("\nВведите корректное число")
                except BookStoreException as e:
                    print(f"\n{e}")
            
            elif choice == '4':
                try:
                    amount = float(input("Сумма пополнения: "))
                    store.current_customer.add_balance(amount)
                    print(f"\nБаланс пополнен на {amount} руб.")
                    print(f"Текущий баланс: {store.current_customer.balance} руб.")
                    store.save_to_json()
                except ValueError as e:
                    print(f"\n{e}")
            
            elif choice == '5':
                print("\n=== СОХРАНЕНИЕ ДАННЫХ ===")
                print("1. Сохранить в JSON")
                print("2. Сохранить в XML")
                
                save_choice = input("Выберите формат: ").strip()
                
                if save_choice == '1':
                    store.save_to_json()
                elif save_choice == '2':
                    store.save_to_xml()
                else:
                    print("Неверный выбор")
            
            elif choice == '6':
                store.current_customer = None
                print("\nВы вышли из аккаунта")
            
            elif choice == '0':
                store.save_to_json()
                print("\nДанные сохранены. До свидания!")
                break
            
            else:
                print("\nНеверный выбор")


if __name__ == "__main__":
    run()