# Art Collection API (YaMDB)

## Описание проекта
Art Collection API — это приложение, которое позволяет сохранять любимые произведения искусства.
С его помощью можно:
- Добавлять произведения искусства.
- Управлять жанрами и категориями произведений.
- Использовать API для взаимодействия с данными.

Приложение идеально подходит для создания и управления персональной коллекцией произведений искусства.

---

## Установка и запуск приложения

### 1. Запуск через Docker

Если проект настроен для работы с Docker:

1. Соберите и запустите контейнеры:
   ```bash
   docker-compose up --build
   ```

2. Выполните миграции базы данных:
   ```bash
   docker exec -it django_web python manage.py migrate
   ```

3. Создайте суперпользователя:
   ```bash
   docker exec -it django_web python manage.py createsuperuser
   ```

4. (Опционально) Заполните базу данных начальными данными:
   ```bash
   docker exec -it django_web python manage.py loaddata fixtures.json
   ```

---

### 2. Локальный запуск без Docker

Если Docker не используется:

1. Установите зависимости проекта:
   ```bash
   pip install -r requirements.txt
   ```

2. Выполните миграции базы данных:
   ```bash
   python manage.py migrate
   ```

3. Создайте суперпользователя:
   ```bash
   python manage.py createsuperuser
   ```

4. Запустите приложение:
   ```bash
   python manage.py runserver
   ```

5. (Опционально) Заполните базу данных начальными данными:
   ```bash
   python manage.py loaddata fixtures.json
   ```

---

## Экспорт начальных данных
Если вы хотите экспортировать текущие данные из базы:
```bash
python manage.py dumpdata > fixtures.json
```

---

Теперь вы можете пользоваться Art Collection API для управления коллекцией произведений искусства!

