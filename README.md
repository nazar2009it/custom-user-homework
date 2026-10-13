# Домашнее задание: CustomUser

Отдельный учебный проект Django + Django REST Framework. Регистрация и вход происходят по email. API можно проверять в Swagger.

## Как прочитано задание

На скриншоте сначала сказано проверить обязательность телефона, а последний пункт уточняет: телефон обязателен **только для суперпользователя**. В проекте реализован последний пункт:

- обычный пользователь может зарегистрироваться без телефона;
- суперпользователь должен указать телефон;
- любой указанный номер проверяется: `996` и ещё 9 цифр, с необязательным плюсом;
- примеры: `996700123456` и `+996700123456`;
- в базе номер сохраняется как `+996700123456`.

Это новый проект. Для уже существующего проекта замена модели пользователя требует отдельной проверки его миграций и связей. Не удаляй существующую базу или миграции, чтобы перенести этот пример.

## Запуск в Windows

1. Распакуй архив и открой папку `custom_user_homework` в VS Code.
2. Открой терминал. Он должен находиться в папке, где лежит `manage.py`.
3. Выполняй команды по одной:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Если команда `py` не найдена, замени её в первой строке на `python`.

Команда `createsuperuser` спросит email, номер телефона и пароль. Для примера можно указать `admin@example.com` и `+996700123456`. Пароль выбери сам; при вводе символы в терминале не показываются.

Миграция пользователя уже включена в архив: перед первым запуском достаточно `migrate`. Активация виртуального окружения не нужна — команды явно используют его Python.

Поддерживается Python 3.10 и новее. В зависимости от версии Python установится совместимая версия Django из диапазона 5.2–6.0; Python 3.14 тоже подходит.

Открой:

- Swagger: http://127.0.0.1:8000/swagger/
- Админка: http://127.0.0.1:8000/admin/
- Схема API: http://127.0.0.1:8000/api/schema/

Настройки рассчитаны на учебный запуск на своём компьютере.

## Запуск в Ubuntu / WSL

Из папки с `manage.py`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

## Проверка в Swagger

### 1. Зарегистрируй обычного пользователя

Раскрой `POST /api/v1/auth/register/`, нажми **Try it out**, вставь JSON и нажми **Execute**:

```json
{
  "email": "student@example.com",
  "password": "StudyPassword!2026",
  "password_confirm": "StudyPassword!2026"
}
```

Ожидаемый результат — **201**, объект пользователя и `token`. Телефон в запросе отсутствует, но регистрация работает. Пароль в ответе отсутствует.

Для регистрации с телефоном используй другой email:

```json
{
  "email": "student2@example.com",
  "phone_number": "996700123456",
  "password": "StudyPassword!2026",
  "password_confirm": "StudyPassword!2026"
}
```

Если ввести `+77001234567` или `996`, сервер вернёт **400** с ошибкой в поле `phone_number`. Если повторить уже зарегистрированный email, сервер вернёт **400** с ошибкой в поле `email`. Регистр букв в email не различается.

### 2. Войди по email

Раскрой `POST /api/v1/auth/login/` → **Try it out**:

```json
{
  "email": "student@example.com",
  "password": "StudyPassword!2026"
}
```

Ожидаемый результат — **200**, `token` и пользователь. Неверный пароль даст **400**.

### 3. Проверь авторизацию

Нажми **Authorize** в Swagger. В поле токена вставь:

```text
Token твой_токен_из_ответа
```

Затем вызови `GET /api/v1/auth/me/`. Сервер вернёт пользователя, которому принадлежит токен. Без токена этот запрос возвращает **401**.

### 4. Проверь суперпользователя

`createsuperuser` требует телефон. Вызов менеджера без телефона тоже отклоняется:

```python
User.objects.create_superuser(email="admin2@example.com", password="StudyPassword!2026")
```

Для проверки этого кода сначала запусти `manage.py shell` и импортируй `User`:

```python
from users.models import User
```

Публичная регистрация создаёт обычного пользователя. Права администратора выдаются через `createsuperuser` или админку.

## Где выполнены пункты задания

| Требование | Файл и реализация |
| --- | --- |
| Менеджер на основе `BaseUserManager` | `users/managers.py`, класс `UserManager` |
| Пользователь на основе `AbstractBaseUser` и `PermissionsMixin` | `users/models.py`, класс `User` |
| Регистрация и вход по email | `email` с `unique=True`, `USERNAME_FIELD = "email"`, сериализаторы |
| Настройка модели пользователя | `config/settings.py`, `AUTH_USER_MODEL = "users.User"` |
| Поле телефона и проверка `996` | `users/models.py`, `users/validators.py` |
| Телефон обязателен только для суперпользователя | `create_superuser`, `User.clean`, ограничение базы данных |
| Регистрация и вход через Swagger | `users/serializers.py`, `users/views.py`, `config/urls.py` |
| Работа с пользователем в админке | `users/admin.py`, `users/forms.py` |

## Как объяснить решение преподавателю

`AbstractBaseUser` даёт основу пользователя: пароль, проверку пароля и дату последнего входа. `PermissionsMixin` добавляет группы, разрешения и признак суперпользователя. Email становится полем входа благодаря `USERNAME_FIELD`.

`UserManager.create_user()` создаёт обычного пользователя. Он проверяет email и телефон, вызывает `set_password()` для хеширования пароля и сохраняет пользователя. `create_superuser()` дополнительно требует телефон и выставляет `is_staff=True`, `is_superuser=True`.

`REQUIRED_FIELDS = ["phone_number"]` заставляет команду `createsuperuser` спрашивать телефон. Это **не** делает телефон обязательным при регистрации через API. Для проверки этого правила вне команды также есть `User.clean()` и проверка в менеджере. Ограничение базы данных не позволяет сохранить суперпользователя с пустым телефоном напрямую.

Сериализатор регистрации проверяет данные до сохранения: свободен ли email, верен ли телефон, совпадают ли пароли и достаточно ли надёжен пароль. Сериализатор входа передаёт email и пароль в `authenticate()`. Swagger получает описание полей из сериализаторов; `extend_schema` задаёт примеры запросов и формат ответов.

## Автоматические проверки

После установки зависимостей:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test users
.\.venv\Scripts\python.exe manage.py spectacular --file schema.yml --validate --fail-on-warn
```

В Ubuntu / WSL вместо `.\.venv\Scripts\python.exe` используй `.venv/bin/python`.

В тестах проверяются создание пользователей, обязательность телефона для администратора, формат номера, хеширование паролей, повторный email, регистрация, вход, права доступа и поля схемы Swagger. Фактически выполненные при подготовке проверки описаны в `VALIDATION.md`.

## Что отправлять преподавателю

После запуска и проверки отправь этот проект архивом или ссылкой на свой GitHub. В архив для сдачи включай исходный код, `requirements.txt` и миграции. Папку `.venv`, `__pycache__` и `db.sqlite3` добавлять не нужно.

## Документация

- Django: https://docs.djangoproject.com/en/5.2/topics/auth/customizing/
- Django и Python 3.14: https://docs.djangoproject.com/en/5.2/releases/5.2.8/
- Django REST Framework: https://www.django-rest-framework.org/api-guide/authentication/
- Swagger / drf-spectacular: https://drf-spectacular.readthedocs.io/en/latest/readme.html
