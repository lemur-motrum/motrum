# Конвертация XLSX в PDF - Руководство пользователя

## Обзор

Этот модуль предоставляет функциональность для конвертации XLSX файлов в PDF формат с использованием различных методов. Реализовано три подхода к конвертации, каждый со своими преимуществами и ограничениями.

## Быстрый старт

### 1. Установка зависимостей

```bash
# Обновите requirements.txt
pip install pandas==2.3.0 pdfkit==1.0.0 wkhtmltopdf==0.2

# Или установите через requirements.txt
pip install -r docker/python/requirements.txt
```

### 2. Установка wkhtmltopdf (для основной функции)

#### Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install wkhtmltopdf
```

#### CentOS/RHEL:

```bash
sudo yum install wkhtmltopdf
```

#### Windows:

1. Скачайте установщик с [https://wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html)
2. Установите и добавьте в PATH

#### Docker:

wkhtmltopdf уже добавлен в Dockerfile проекта.

### 3. Тестирование

```bash
# Запустите тестовый скрипт
python test_conversion.py

# Или используйте тестовую страницу
http://your-domain/supplier/test_xlsx_to_pdf/
```

## Доступные функции

### 1. Простая конвертация (рекомендуется для начала)

```python
from apps.client.utils import convert_xlsx_to_pdf_simple

# Конвертируем XLSX в PDF
pdf_path = convert_xlsx_to_pdf_simple("path/to/file.xlsx")
print(f"PDF создан: {pdf_path}")
```

**Преимущества:**

- ✅ Не требует дополнительных зависимостей
- ✅ Быстрая работа
- ✅ Простая установка
- ✅ Надежная работа

**Недостатки:**

- ❌ Ограниченное форматирование
- ❌ Базовые стили

### 2. Продвинутая конвертация

```python
from apps.client.utils import convert_xlsx_to_pdf_advanced

# Конвертируем XLSX в PDF с улучшенным форматированием
pdf_path = convert_xlsx_to_pdf_advanced("path/to/file.xlsx")
print(f"PDF создан: {pdf_path}")
```

**Преимущества:**

- ✅ Лучшее форматирование чем простая версия
- ✅ Поддержка шрифтов
- ✅ Настраиваемые стили
- ✅ Не требует wkhtmltopdf

**Недостатки:**

- ❌ Может не сохранить все элементы форматирования

### 3. Основная конвертация (высокое качество)

```python
from apps.client.utils import convert_xlsx_to_pdf

# Конвертируем XLSX в PDF с максимальным качеством
pdf_path = convert_xlsx_to_pdf("path/to/file.xlsx")
print(f"PDF создан: {pdf_path}")
```

**Преимущества:**

- ✅ Высокое качество конвертации
- ✅ Поддержка сложного форматирования
- ✅ CSS стили
- ✅ Максимальная совместимость

**Недостатки:**

- ❌ Требует установки wkhtmltopdf
- ❌ Может быть медленнее

## Использование в Django

### 1. Конвертация существующего XLSX файла

```python
from django.http import FileResponse
from apps.client.utils import convert_xlsx_to_pdf_simple
import os

def download_pdf(request, xlsx_path):
    try:
        # Конвертируем XLSX в PDF
        pdf_path = convert_xlsx_to_pdf_simple(xlsx_path)

        # Отправляем файл пользователю
        with open(pdf_path, 'rb') as f:
            response = FileResponse(f, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            return response

    except Exception as e:
        return HttpResponse(f"Ошибка конвертации: {e}", status=500)
```

### 2. Создание счета и конвертация

```python
from apps.client.utils import create_xlsx_and_pdf_bill

def create_bill(request, order_id):
    try:
        order = Order.objects.get(id=order_id)

        # Создаем XLSX и PDF
        result = create_xlsx_and_pdf_bill(
            specification=order.specification.id,
            request=request,
            is_contract=True,
            order=order,
            type_delivery=order.type_delivery,
            post_update=False,
            type_save="new"
        )

        xlsx_path, pdf_path, bill_name, version, name_bill_to_fullname = result

        return JsonResponse({
            'success': True,
            'xlsx_path': xlsx_path,
            'pdf_path': pdf_path,
            'bill_name': bill_name
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
```

## URL маршруты

Добавлены следующие URL для работы с конвертацией:

```python
# Конвертация XLSX в PDF
path("convert-xlsx-to-pdf/<path:xlsx_path>/", views.convert_xlsx_to_pdf_view, name="convert_xlsx_to_pdf")

# Создание и конвертация счета
path("bill-conversion/<int:order_id>/", views.BillConversionView.as_view(), name="bill_conversion")
```

### Примеры использования URL:

```bash
# Конвертация с простым методом
GET /client/convert-xlsx-to-pdf/documents/bill/file.xlsx/

# Конвертация с продвинутым методом
GET /client/convert-xlsx-to-pdf/documents/bill/file.xlsx/?method=advanced

# Конвертация с полным методом (wkhtmltopdf)
GET /client/convert-xlsx-to-pdf/documents/bill/file.xlsx/?method=full

# Создание счета для заказа
GET /client/bill-conversion/123/
POST /client/bill-conversion/123/
```

## Тестирование

### 1. Автоматическое тестирование

```bash
# Запуск тестового скрипта
python test_conversion.py
```

### 2. Веб-интерфейс для тестирования

```
http://your-domain/supplier/test_xlsx_to_pdf/
```

### 3. Создание тестового XLSX файла

```python
from test_xlsx_bill import test_create_xlsx_bill

# Создаем тестовый файл
xlsx_path = test_create_xlsx_bill()
print(f"Тестовый файл создан: {xlsx_path}")
```

## Обработка ошибок

Все функции включают обработку ошибок и логирование:

```python
try:
    pdf_path = convert_xlsx_to_pdf_simple("file.xlsx")
    print(f"PDF создан: {pdf_path}")
except Exception as e:
    print(f"Ошибка конвертации: {e}")
    # Ошибка автоматически записывается в логи через error_alert
```

## Рекомендации по выбору метода

### Для простых таблиц:

```python
convert_xlsx_to_pdf_simple()  # Быстро и надежно
```

### Для документов со средним форматированием:

```python
convert_xlsx_to_pdf_advanced()  # Хороший баланс
```

### Для сложных документов с форматированием:

```python
convert_xlsx_to_pdf()  # Лучшее качество
```

## Устранение неполадок

### Ошибка "wkhtmltopdf not found"

```bash
# Установите wkhtmltopdf
sudo apt-get install wkhtmltopdf  # Ubuntu/Debian
sudo yum install wkhtmltopdf      # CentOS/RHEL
```

### Ошибка "No module named 'pandas'"

```bash
pip install pandas==2.3.0
```

### Ошибка "No module named 'pdfkit'"

```bash
pip install pdfkit==1.0.0
```

### Медленная конвертация

- Используйте `convert_xlsx_to_pdf_simple()` для быстрой конвертации
- Убедитесь, что XLSX файл не слишком большой
- Проверьте доступность системных ресурсов

### Проблемы с кодировкой

- Убедитесь, что XLSX файл сохранен в UTF-8
- Используйте `convert_xlsx_to_pdf_advanced()` для лучшей поддержки кодировок

## Производительность

| Метод    | Скорость   | Качество   | Зависимости                 |
| -------- | ---------- | ---------- | --------------------------- |
| Simple   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | pandas, reportlab           |
| Advanced | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | pandas, reportlab           |
| Full     | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ | pandas, pdfkit, wkhtmltopdf |

## Лицензия

Этот модуль является частью проекта Motrum и использует те же лицензионные условия.

## Поддержка

При возникновении проблем:

1. Проверьте логи Django
2. Убедитесь, что все зависимости установлены
3. Запустите тестовый скрипт
4. Обратитесь к документации в `XLSX_TO_PDF_CONVERSION.md`
