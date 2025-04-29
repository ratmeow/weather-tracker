# Трекер погоды

[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

Веб-приложение для просмотра текущей погоды.

## Функционал приложения
* Регистрация и авторизация пользователя
* Поиск локация по названию
* Добавление локаций в коллекцию пользователя и их удаление
* Отображение текущей погоды для каждой локации пользователя

## Архитектура проекта
Проект разделен на следующие слои.
  - domain - основная логика добавления и удаления локаций.
  - application - сценарии использования приложения(use_cases) и интерфейсы.
  - infrastructure - реализация интерфейсов слоя application; логика работы с хранилищем данных, хранилищем сессий и внешним API.
  - presentation - обработчики запросов пользователей
  - weather_tracker - агрегирует все слои, содержит конфигурацию приложения, контейнер зависимостей и точку входа.

## Запуск проекта[DEV] - сервисы в контейнерах, backend на хосте
1. Склонировать репозиторий `git clone https://github.com/ratmeow/weather-tracker.git`
2. Cоздать файл окружения .env по примеру файла tests.env. Обязательно нужен действительный ключ OPENWEATHER_API_KEY, который можно получить на https://openweathermap.org/
3. Убедитесь, что у вас установлен docker
4. Если у вас **linux**, то чтобы frontend правильно проксировал запросы на backend необходимо в `nginx.conf` поменять значение переменной **proxy_pass** на `http://backend:8080/;`
5. Запустить сервисы `docker compose -f compose.dev.yaml up -d`
6. Установить зависимости `poetry install --only main`
7. Выполнить начальную миграцию `alembic upgrade head`
8. Запустить локальный backend `uvicorn weather_tracker.app:create_production_app --port 8080`
9. После этого backend сервиса будет доступен на `localhost:8080`, frontend на `localhost:3000`


## Запуск проекта[PROD] - все сервисы в контейнерах
1. Шаги 1-4 из инструкции выше
2. Запустить сервисы `docker compose -f compose.prod.yaml up -d`
3. После этого backend будет доступен на `localhost:8080`, frontend на `localhost:3000`

## Тестирование
Были написаны unit тесты на основную логику каждого слоя приложения и интеграционные тесты для проверки работы всех уровней вместе.
Чтобы запустить все тесты, нужно:
* Убедиться, что файл `test.env` находится в корне проекта и содержит все необходимые переменные окружения.
* Установить зависимости, необходимые для тестирования `poetry install --only test`
* Выполнить `pytest tests`

## Codestyle
* В качестве линтера и форматера был использован **ruff**. Его конфиг можно найти в pyproject.toml 
* Код в директории `weather_tracker` был проверен с помощью **mypy**

### Стeк технологий backend
- Python 3.12
- FastAPI
- dishka
- pydantic
- aiohttp
- SQLAlchemy(asyncpg)
- Redis
- Alembic
- Docker

