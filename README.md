# Список дел (to_do_list)

## Что делает приложение

Приложение для ведения списка дел: можно добавлять задачи с приоритетом, смотреть и фильтровать их, отмечать выполненными, удалять и смотреть статистику.

Основа: учебный `app_final.py` с занятий. Добавлены своя тема, маршруты задач, параметры и фильтры, настройки из файла `.env`, логи и собственные тесты.

## Подготовка: окружение и зависимости

```bash
git clone https://github.com/ВАШ_ЛОГИН/todo-service.git
cd to_do_list
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

Для Windows (PowerShell) команды активации и копирования другие:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
copy .env.example .env
```

## Запуск

Для разработки (с автоперезагрузкой при изменении кода):

```bash
python -m uvicorn app_final:app --host 0.0.0.0 --port 8000
```

## Маршруты

| Метод | Адрес | Описание |
|-------|-------|----------|
| GET | `/` | Приветствие |
| GET | `/health` | Проверка работоспособности |
| GET | `/version` | Версия приложения |
| GET | `/info` | Название, автор, лимит задач |
| GET | `/tasks` | Список задач; фильтры `?done=true` и `?priority=high` |
| POST | `/tasks` | Создать задачу (`title`, `priority`: low/normal/high) |
| GET | `/tasks/{task_id}` | Получить задачу по номеру |
| POST | `/tasks/{task_id}/done` | Отметить выполненной |
| DELETE | `/tasks/{task_id}` | Удалить задачу |
| GET | `/stats` | Статистика: всего / выполнено / активных |

Пример:

```bash
curl -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d '{"title": "Купить молоко", "priority": "high"}'
curl "http://127.0.0.1:8000/tasks?done=false"
```

## Переменные окружения

Настройки читаются из файла `.env`, который создаётся копированием образца `.env.example` - добавьте свои значения.

| Переменная | Пример значения | Назначение |
|-----------|-----------------|------------|
| `APP_NAME` | Список дел | Название сервиса |
| `APP_AUTHOR` | Ваше Имя | Автор |
| `APP_VERSION` | 1.0.0 | Версия (отдаётся в `/version`) |
| `MAX_TASKS` | 100 | Максимальное число задач |
| `LOG_LEVEL` | INFO | Уровень логов: DEBUG, INFO, WARNING, ERROR |


## Тесты

```bash
python -m pytest -v
```

## Проверка и диагностика

Проверка работоспособности:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/version
```

Ожидаемые ответы: `{"status":"ok"}` и `{"version":"1.0.0"}` (версия берётся из `APP_VERSION`).

Логи выводятся в терминал, где запущен сервис. Чтобы сохранять их в файл и читать в реальном времени:

```bash
python -m uvicorn app_final:app --host 0.0.0.0 --port 8000 > app.log 2>&1
tail -f app.log
```
