#!/usr/bin/env python
"""
Скрипт для тестирования конвертации XLSX в PDF
"""
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from test_xlsx_bill import test_create_xlsx_bill
from apps.client.utils import (
    convert_xlsx_to_pdf,
    convert_xlsx_to_pdf_simple,
    convert_xlsx_to_pdf_advanced
)


def test_all_conversion_methods():
    """Тестирует все методы конвертации"""
    print("🧪 Тестирование конвертации XLSX в PDF")
    print("=" * 60)
    
    # Создаем тестовый XLSX файл
    print("📄 Создаем тестовый XLSX файл...")
    xlsx_path = test_create_xlsx_bill()
    
    if not xlsx_path:
        print("❌ Не удалось создать тестовый XLSX файл")
        return False
    
    print(f"✅ XLSX файл создан: {xlsx_path}")
    print()
    
    # Тестируем простую конвертацию
    print("🔄 Тестируем простую конвертацию (pandas + reportlab)...")
    try:
        pdf_path_simple = convert_xlsx_to_pdf_simple(xlsx_path)
        print(f"✅ Простая конвертация успешна: {pdf_path_simple}")
        
        # Проверяем размер файла
        if os.path.exists(pdf_path_simple):
            size = os.path.getsize(pdf_path_simple)
            print(f"   📊 Размер PDF: {size} байт")
    except Exception as e:
        print(f"❌ Простая конвертация не удалась: {e}")
    
    print()
    
    # Тестируем продвинутую конвертацию
    print("🔄 Тестируем продвинутую конвертацию...")
    try:
        pdf_path_advanced = convert_xlsx_to_pdf_advanced(xlsx_path)
        print(f"✅ Продвинутая конвертация успешна: {pdf_path_advanced}")
        
        # Проверяем размер файла
        if os.path.exists(pdf_path_advanced):
            size = os.path.getsize(pdf_path_advanced)
            print(f"   📊 Размер PDF: {size} байт")
    except Exception as e:
        print(f"❌ Продвинутая конвертация не удалась: {e}")
    
    print()
    
    # Тестируем основную конвертацию (с wkhtmltopdf)
    print("🔄 Тестируем основную конвертацию (pandas + pdfkit + wkhtmltopdf)...")
    try:
        pdf_path_main = convert_xlsx_to_pdf(xlsx_path)
        print(f"✅ Основная конвертация успешна: {pdf_path_main}")
        
        # Проверяем размер файла
        if os.path.exists(pdf_path_main):
            size = os.path.getsize(pdf_path_main)
            print(f"   📊 Размер PDF: {size} байт")
    except Exception as e:
        print(f"❌ Основная конвертация не удалась: {e}")
        print("   💡 Убедитесь, что wkhtmltopdf установлен")
    
    print()
    print("=" * 60)
    print("🎉 Тестирование завершено!")
    
    return True


def cleanup_test_files():
    """Удаляет тестовые файлы"""
    print("🧹 Очистка тестовых файлов...")
    
    # Ищем и удаляем тестовые файлы
    current_dir = os.getcwd()
    for file in os.listdir(current_dir):
        if file.endswith('.xlsx') and 'test' in file.lower():
            try:
                os.remove(file)
                print(f"   🗑️ Удален: {file}")
            except:
                pass
        
        if file.endswith('.pdf') and 'test' in file.lower():
            try:
                os.remove(file)
                print(f"   🗑️ Удален: {file}")
            except:
                pass


if __name__ == "__main__":
    print("🚀 Запуск тестирования конвертации XLSX в PDF")
    print()
    
    # Запускаем тесты
    success = test_all_conversion_methods()
    
    # Спрашиваем пользователя о необходимости очистки
    if success:
        print()
        cleanup = input("🗑️ Удалить тестовые файлы? (y/n): ").lower().strip()
        if cleanup in ['y', 'yes', 'да']:
            cleanup_test_files()
    
    print("👋 До свидания!") 