# Unit-тесты для PhoneValidator (unittest - встроенный модуль)
# Запуск: python test_phone_validator_simple.py

import unittest
import tempfile
import os
from lab2_phone_validator import PhoneValidator


class TestValidateRussianPhone(unittest.TestCase):
    """Тесты для проверки корректности российских номеров"""
    
    def test_valid_plus7_with_spaces(self):
        """Тест: +7 с пробелами"""
        self.assertTrue(PhoneValidator.validate_russian_phone("+7 999 123 45 67"))
    
    def test_valid_plus7_with_dashes(self):
        """Тест: +7 с дефисами"""
        self.assertTrue(PhoneValidator.validate_russian_phone("+7-999-123-45-67"))
    
    def test_valid_8_with_dashes(self):
        """Тест: 8 с дефисами"""
        self.assertTrue(PhoneValidator.validate_russian_phone("8-999-123-45-67"))
    
    def test_valid_8_with_parentheses(self):
        """Тест: 8 со скобками"""
        self.assertTrue(PhoneValidator.validate_russian_phone("8(999)123-45-67"))
    
    def test_valid_7_without_plus(self):
        """Тест: 7 без плюса"""
        self.assertTrue(PhoneValidator.validate_russian_phone("79991234567"))
    
    def test_valid_with_mixed_separators(self):
        """Тест: смешанные разделители"""
        self.assertTrue(PhoneValidator.validate_russian_phone("+7(999)123 45-67"))
    
    def test_invalid_short_number(self):
        """Тест: слишком короткий номер"""
        self.assertFalse(PhoneValidator.validate_russian_phone("8-999-123"))
    
    def test_invalid_letters(self):
        """Тест: содержит буквы"""
        self.assertFalse(PhoneValidator.validate_russian_phone("8-999-abc-45-67"))
    
    def test_invalid_wrong_country_code(self):
        """Тест: неверный код страны"""
        self.assertFalse(PhoneValidator.validate_russian_phone("+1-234-567-89-01"))
    
    def test_invalid_empty_string(self):
        """Тест: пустая строка"""
        self.assertFalse(PhoneValidator.validate_russian_phone(""))


class TestNormalizePhone(unittest.TestCase):
    """Тесты для нормализации номеров"""
    
    def test_normalize_with_plus7(self):
        """Тест: нормализация +7"""
        result = PhoneValidator.normalize_phone("+7 999 123 45 67")
        self.assertEqual(result, "+79991234567")
    
    def test_normalize_with_8(self):
        """Тест: нормализация 8"""
        result = PhoneValidator.normalize_phone("8-999-123-45-67")
        self.assertEqual(result, "+79991234567")
    
    def test_normalize_with_7(self):
        """Тест: нормализация 7"""
        result = PhoneValidator.normalize_phone("79991234567")
        self.assertEqual(result, "+79991234567")
    
    def test_normalize_with_parentheses(self):
        """Тест: нормализация со скобками"""
        result = PhoneValidator.normalize_phone("8(999)123-45-67")
        self.assertEqual(result, "+79991234567")
    
    def test_normalize_invalid_short(self):
        """Тест: слишком короткий номер"""
        result = PhoneValidator.normalize_phone("123")
        self.assertIsNone(result)


class TestFindPhonesInText(unittest.TestCase):
    """Тесты для поиска номеров в тексте"""
    
    def test_find_single_phone(self):
        """Тест: один номер в тексте"""
        text = "Позвоните нам: +7 999 123 45 67"
        phones = PhoneValidator.find_phones_in_text(text)
        self.assertEqual(len(phones), 1)
    
    def test_find_multiple_phones(self):
        """Тест: несколько номеров"""
        text = """
        Контакты:
        Офис: +7 495 123-45-67
        Мобильный: 8-999-888-77-66
        """
        phones = PhoneValidator.find_phones_in_text(text)
        self.assertEqual(len(phones), 2)
    
    def test_find_no_phones(self):
        """Тест: нет номеров"""
        text = "В этом тексте нет номеров телефонов"
        phones = PhoneValidator.find_phones_in_text(text)
        self.assertEqual(len(phones), 0)
    
    def test_find_phones_in_empty_text(self):
        """Тест: пустой текст"""
        phones = PhoneValidator.find_phones_in_text("")
        self.assertEqual(len(phones), 0)


class TestExtractParts(unittest.TestCase):
    """Тесты для извлечения частей номера"""
    
    def test_extract_parts_plus7(self):
        """Тест: извлечение частей из +7"""
        parts = PhoneValidator.extract_parts("+7 999 123 45 67")
        self.assertIsNotNone(parts)
        self.assertEqual(parts['country_code'], '+7')
        self.assertEqual(parts['operator'], '999')
        self.assertEqual(parts['number'], '1234567')
    
    def test_extract_parts_8(self):
        """Тест: извлечение частей из 8"""
        parts = PhoneValidator.extract_parts("8-999-123-45-67")
        self.assertIsNotNone(parts)
        self.assertEqual(parts['country_code'], '+7')
        self.assertEqual(parts['operator'], '999')
    
    def test_extract_parts_invalid(self):
        """Тест: некорректный номер"""
        parts = PhoneValidator.extract_parts("123")
        self.assertIsNone(parts)
    
    def test_extract_parts_moscow(self):
        """Тест: московский номер (код 495)"""
        parts = PhoneValidator.extract_parts("+7 495 123 45 67")
        self.assertIsNotNone(parts)
        self.assertEqual(parts['operator'], '495')


class TestFindPhonesInFile(unittest.TestCase):
    """Тесты для поиска номеров в файле"""
    
    def test_find_phones_in_existing_file(self):
        """Тест: поиск в существующем файле"""
        # Создаём временный файл
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Контакты:\n")
            f.write("Менеджер: +7 999 123 45 67\n")
            f.write("Директор: 8-800-555-35-35\n")
            temp_file = f.name
        
        try:
            phones = PhoneValidator.find_phones_in_file(temp_file)
            self.assertEqual(len(phones), 2)
        finally:
            os.unlink(temp_file)
    
    def test_find_phones_in_nonexistent_file(self):
        """Тест: несуществующий файл"""
        phones = PhoneValidator.find_phones_in_file("nonexistent_file.txt")
        self.assertEqual(len(phones), 0)


def run_tests():
    """Запуск всех тестов с красивым выводом"""
    print("\n" + "="*70)
    print("ЗАПУСК UNIT-ТЕСТОВ")
    print("="*70 + "\n")
    
    # Создаём набор тестов
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем все тест-классы
    suite.addTests(loader.loadTestsFromTestCase(TestValidateRussianPhone))
    suite.addTests(loader.loadTestsFromTestCase(TestNormalizePhone))
    suite.addTests(loader.loadTestsFromTestCase(TestFindPhonesInText))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractParts))
    suite.addTests(loader.loadTestsFromTestCase(TestFindPhonesInFile))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Итоговая статистика
    print("\n" + "="*70)
    print("РЕЗУЛЬТАТЫ")
    print("="*70)
    print(f"Всего тестов: {result.testsRun}")
    print(f" Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" Провалено: {len(result.failures)}")
    print(f" Ошибки: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print("\n ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ")
    
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
