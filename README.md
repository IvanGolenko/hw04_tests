# Yatube: покрытие тестами

[![CI](https://github.com/yandex-praktikum/hw04_tests/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw04_tests/actions/workflows/python-app.yml)

### Описание
Социальная сеть для публикации дневников, где реализовано: реализована регистрация, размещение/редактирование публикаций, добавление публикаций в группы. \
\
Дополнения в проекте: покрытие проекта тестами. Написаны тесты для проверки:
- моделей приложения.
- URLs.
- view-функций.
- Forms.
- создания и публикации поста.

### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение
```
python -m venv venv
source venv/Scripts/activate
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- В папке с файлом manage.py выполните команду:
```
python manage.py runserver
```
### Технологии
- Python 3.7
- Django 2.2.6

### Автор
Иван Голенко
