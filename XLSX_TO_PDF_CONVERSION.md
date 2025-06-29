# Конвертация XLSX в PDF

Этот модуль предоставляет несколько способов конвертации XLSX файлов в PDF формат.

## Установка зависимостей

Добавьте следующие зависимости в `requirements.txt`:

```txt
pandas==2.3.0
pdfkit==1.0.0
wkhtmltopdf==0.2
```

## Доступные функции

### 1. `convert_xlsx_to_pdf(xlsx_file_path, pdf_file_path=None)`

Основная функция конвертации, использующая pandas + pdfkit + wkhtmltopdf.

**Преимущества:**

- Высокое качество конвертации
- Поддержка сложного форматирования
- CSS стили

**Недостатки:**

- Требует установки wkhtmltopdf
- Может быть медленнее

**Использование:**

```python
from apps.client.utils import convert_xlsx_to_pdf

# Автоматическое создание PDF с тем же именем
pdf_path = convert_xlsx_to_pdf("path/to/file.xlsx")

# Указание пути для PDF
pdf_path = convert_xlsx_to_pdf("path/to/file.xlsx", "path/to/output.pdf")
```

### 2. `convert_xlsx_to_pdf_simple(xlsx_file_path, pdf_file_path=None)`

Простая функция конвертации, использующая только pandas + reportlab.

**Преимущества:**

- Не требует дополнительных зависимостей
- Быстрая работа
- Простая установка

**Недостатки:**

- Ограниченное форматирование
- Базовые стили

**Использование:**

```python
from apps.client.utils import convert_xlsx_to_pdf_simple

pdf_path = convert_xlsx_to_pdf_simple("path/to/file.xlsx")
```

### 3. `convert_xlsx_to_pdf_advanced(xlsx_file_path, pdf_file_path=None)`

Продвинутая функция конвертации с улучшенным форматированием.

**Преимущества:**

- Лучшее форматирование чем простая версия
- Поддержка шрифтов
- Настраиваемые стили

**Недостатки:**

- Требует reportlab
- Может не сохранить все элементы форматирования

**Использование:**

```python
from apps.client.utils import convert_xlsx_to_pdf_advanced

pdf_path = convert_xlsx_to_pdf_advanced("path/to/file.xlsx")
```

### 4. `create_xlsx_and_pdf_bill(...)`

Комбинированная функция для создания XLSX счета и его конвертации в PDF.

**Использование:**

```python
from apps.client.utils import create_xlsx_and_pdf_bill

result = create_xlsx_and_pdf_bill(
    specification=specification_id,
    request=request,
    is_contract=True,
    order=order,
    type_delivery=type_delivery,
    post_update=False,
    type_save="new"
)

xlsx_path, pdf_path, bill_name, version, name_bill_to_fullname = result
```

## Тестирование

Для тестирования конвертации используйте тестовую страницу:

```
http://your-domain/supplier/test_xlsx_to_pdf/
```

Эта страница создаст тестовый XLSX файл и попробует конвертировать его всеми доступными методами.

## Рекомендации по выбору метода

### Для простых таблиц:

Используйте `convert_xlsx_to_pdf_simple()` - быстро и надежно.

### Для сложных документов с форматированием:

Используйте `convert_xlsx_to_pdf()` - лучшее качество, но требует wkhtmltopdf.

### Для документов со средним форматированием:

Используйте `convert_xlsx_to_pdf_advanced()` - хороший баланс между качеством и простотой.

## Установка wkhtmltopdf (для основной функции)

### Ubuntu/Debian:

```bash
sudo apt-get install wkhtmltopdf
```

### CentOS/RHEL:

```bash
sudo yum install wkhtmltopdf
```

### Windows:

1. Скачайте установщик с https://wkhtmltopdf.org/downloads.html
2. Установите и добавьте в PATH

### Docker:

Добавьте в Dockerfile:

```dockerfile
RUN apt-get update && apt-get install -y wkhtmltopdf
```

## Обработка ошибок

Все функции включают обработку ошибок и логирование:

```python
try:
    pdf_path = convert_xlsx_to_pdf("file.xlsx")
    print(f"PDF создан: {pdf_path}")
except Exception as e:
    print(f"Ошибка конвертации: {e}")
    # Ошибка будет записана в логи через error_alert
```

## Примеры использования в Django views

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
