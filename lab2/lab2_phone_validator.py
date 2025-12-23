# Лабораторная работа №2
# Регулярные выражения: Проверка номеров телефона

import re
from typing import List, Optional


class PhoneValidator:
    """Класс для проверки и поиска номеров телефонов"""
    
    # Паттерны для разных форматов телефонов
    PATTERNS = {
        'russian': r'\+?[78][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
        'international': r'\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,9}',
        'simple': r'\d{10,11}'
    }
    
    @staticmethod
    def validate_russian_phone(phone: str) -> bool:
        """
        Проверяет корректность российского номера телефона
        
        Примеры корректных форматов:
        - +7 999 123 45 67
        - 8-999-123-45-67
        - 8(999)123-45-67
        - 79991234567
        
        Args:
            phone: Строка с номером телефона
            
        Returns:
            bool: True если номер корректен, иначе False
        """
        pattern = r'^(\+7|8|7)[\s\-]?\(?(\d{3})\)?[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})$'
        return bool(re.match(pattern, phone.strip()))
    
    @staticmethod
    def normalize_phone(phone: str) -> Optional[str]:
        """
        Приводит номер к стандартному формату +7XXXXXXXXXX
        
        Args:
            phone: Строка с номером телефона
            
        Returns:
            str: Нормализованный номер или None если номер некорректен
        """
        # Убираем все кроме цифр и +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Проверяем длину
        if len(cleaned) == 10:
            return '+7' + cleaned
        elif len(cleaned) == 11 and cleaned[0] in ['7', '8']:
            return '+7' + cleaned[1:]
        elif len(cleaned) == 12 and cleaned.startswith('+7'):
            return cleaned
        
        return None
    
    @staticmethod
    def find_phones_in_text(text: str) -> List[str]:
        """
        Находит все номера телефонов в тексте
        
        Args:
            text: Текст для поиска
            
        Returns:
            List[str]: Список найденных номеров
        """
        pattern = PhoneValidator.PATTERNS['russian']
        phones = re.findall(pattern, text)
        return phones
    
    @staticmethod
    def find_phones_in_file(filename: str) -> List[str]:
        """
        Находит номера телефонов в файле
        
        Args:
            filename: Путь к файлу
            
        Returns:
            List[str]: Список найденных номеров
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
            return PhoneValidator.find_phones_in_text(text)
        except FileNotFoundError:
            print(f"Файл {filename} не найден")
            return []
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            return []
    
    @staticmethod
    def find_phones_on_webpage(url: str) -> List[str]:
        """
        Находит номера телефонов на веб-странице
        
        Args:
            url: URL веб-страницы
            
        Returns:
            List[str]: Список найденных номеров
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            text = response.text
            return PhoneValidator.find_phones_in_text(text)
        except requests.RequestException as e:
            print(f"Ошибка при загрузке страницы: {e}")
            return []
    
    @staticmethod
    def extract_parts(phone: str) -> Optional[dict]:
        """
        Извлекает части номера телефона (код страны, оператор, номер)
        
        Args:
            phone: Строка с номером телефона
            
        Returns:
            dict: Словарь с частями номера или None
        """
        pattern = r'^(\+7|8|7)[\s\-]?\(?(\d{3})\)?[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})$'
        match = re.match(pattern, phone.strip())
        
        if match:
            country, operator, part1, part2, part3 = match.groups()
            return {
                'country_code': '+7',
                'operator': operator,
                'number': f"{part1}{part2}{part3}"
            }
        return None


def interactive_mode():
    """Интерактивный режим для проверки номеров"""
    print("\n" + "="*60)
    print("ПРОВЕРКА НОМЕРОВ ТЕЛЕФОНОВ")
    print("="*60)
    
    while True:
        print("\n1. Проверить номер телефона")
        print("2. Нормализовать номер")
        print("3. Найти номера в тексте")
        print("4. Найти номера в файле")
        print("5. Найти номера на веб-странице")
        print("6. Выход")
        
        choice = input("\nВыберите действие: ").strip()
        
        if choice == "1":
            phone = input("Введите номер телефона: ")
            if PhoneValidator.validate_russian_phone(phone):
                print(f"✓ Номер '{phone}' корректен")
                parts = PhoneValidator.extract_parts(phone)
                if parts:
                    print(f"  Код страны: {parts['country_code']}")
                    print(f"  Код оператора: {parts['operator']}")
                    print(f"  Номер: {parts['number']}")
            else:
                print(f"✗ Номер '{phone}' некорректен")
        
        elif choice == "2":
            phone = input("Введите номер телефона: ")
            normalized = PhoneValidator.normalize_phone(phone)
            if normalized:
                print(f"✓ Нормализованный номер: {normalized}")
            else:
                print("✗ Не удалось нормализовать номер")
        
        elif choice == "3":
            print("Введите текст (для завершения введите пустую строку):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            text = "\n".join(lines)
            
            phones = PhoneValidator.find_phones_in_text(text)
            if phones:
                print(f"\nНайдено номеров: {len(phones)}")
                for i, phone in enumerate(phones, 1):
                    print(f"{i}. {phone}")
            else:
                print("Номера не найдены")
        
        elif choice == "4":
            filename = input("Введите путь к файлу: ")
            phones = PhoneValidator.find_phones_in_file(filename)
            if phones:
                print(f"\nНайдено номеров: {len(phones)}")
                for i, phone in enumerate(phones, 1):
                    print(f"{i}. {phone}")
            else:
                print("Номера не найдены")
        
        elif choice == "5":
            url = input("Введите URL: ")
            print("Загрузка страницы...")
            phones = PhoneValidator.find_phones_on_webpage(url)
            if phones:
                print(f"\nНайдено номеров: {len(phones)}")
                # Убираем дубликаты
                unique_phones = list(set(phones))
                for i, phone in enumerate(unique_phones, 1):
                    print(f"{i}. {phone}")
            else:
                print("Номера не найдены")
        
        elif choice == "6":
            print("Выход...")
            break
        
        else:
            print("Неверный выбор!")


def demo_examples():
    """Демонстрация работы с примерами"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ")
    print("="*60)
    
    # Примеры корректных номеров
    valid_phones = [
        "+7 999 123 45 67",
        "8-999-123-45-67",
        "8(999)123-45-67",
        "79991234567",
        "+7(999)123-45-67",
        "8 999 123 45 67"
    ]
    
    print("\nПроверка корректных номеров:")
    for phone in valid_phones:
        is_valid = PhoneValidator.validate_russian_phone(phone)
        normalized = PhoneValidator.normalize_phone(phone)
        print(f"  {phone:25} -> {'✓' if is_valid else '✗'} -> {normalized}")
    
    # Примеры некорректных номеров
    invalid_phones = [
        "123",
        "+1 234 567 89 01",
        "abcd",
        "8-999-123",
        "+7 999 123 45 6"
    ]
    
    print("\nПроверка некорректных номеров:")
    for phone in invalid_phones:
        is_valid = PhoneValidator.validate_russian_phone(phone)
        print(f"  {phone:25} -> {'✓' if is_valid else '✗'}")
    
    # Поиск в тексте
    text = """
    Контакты:
    Отдел продаж: +7 495 123-45-67
    Поддержка: 8-800-555-35-35
    Мобильный: 8(999)888-77-66
    Email: info@example.com
    Также звоните: +79161234567
    """
    
    print("\nПоиск номеров в тексте:")
    print(text)
    phones = PhoneValidator.find_phones_in_text(text)
    print(f"Найдено: {phones}")


if __name__ == "__main__":
    # Сначала демонстрация
    demo_examples()
    
    # Затем интерактивный режим
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана")
