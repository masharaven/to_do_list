import logging
import os
from contextlib import asynccontextmanager
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
load_dotenv()

def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(
            f"Не задана переменная {name}. Скопируйте .env.example в .env"
        )
    return value

APP_NAME = require_env("APP_NAME")
APP_AUTHOR = require_env("APP_AUTHOR")
APP_VERSION = require_env("APP_VERSION")
MAX_TASKS = int(require_env("MAX_TASKS"))
LOG_LEVEL = require_env("LOG_LEVEL").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("todo")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск сервиса '%s' версии %s", APP_NAME, APP_VERSION)
    yield
    logger.info("Сервис остановлен")

app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)

@app.get("/")
def root():
    return {"message": f"Сервис '{APP_NAME}' работает"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": APP_VERSION}

@app.get("/info")
def info():
    return {"app_name": APP_NAME, "author": APP_AUTHOR, "max_tasks": MAX_TASKS}


tasks: dict[int, dict] = {}
counter = {"next_id": 1}


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")

@app.get("/tasks")
def list_tasks(done: Optional[bool] = None, priority: Optional[str] = None):
    """Список задач. Фильтры: ?done=true/false и ?priority=low|normal|high."""
    result = list(tasks.values())
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if priority is not None:
        result = [t for t in result if t["priority"] == priority]
    logger.info("Запрошен список задач, найдено: %d", len(result))
    return result

@app.post("/tasks", status_code=201)
def create_task(data: TaskCreate):
    if len(tasks) >= MAX_TASKS:
        logger.warning("Достигнут лимит задач: %d", MAX_TASKS)
        raise HTTPException(status_code=409, detail="Достигнут лимит задач")
    task_id = counter["next_id"]
    counter["next_id"] += 1
    task = {
        "id": task_id,
        "title": data.title,
        "priority": data.priority,
        "done": False,
    }
    tasks[task_id] = task
    logger.info("Создана задача #%d: %s", task_id, data.title)
    return task

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        logger.warning("Задача #%d не найдена", task_id)
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

@app.post("/tasks/{task_id}/done")
def complete_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        logger.warning("Задача #%d не найдена", task_id)
        raise HTTPException(status_code=404, detail="Задача не найдена")
    task["done"] = True
    logger.info("Задача #%d выполнена", task_id)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if task_id not in tasks:
        logger.warning("Задача #%d не найдена", task_id)
        raise HTTPException(status_code=404, detail="Задача не найдена")
    del tasks[task_id]
    logger.info("Задача #%d удалена", task_id)
    return {"deleted": task_id}

@app.get("/stats")
def stats():
    total = len(tasks)
    done_count = sum(1 for t in tasks.values() if t["done"])
    return {"total": total, "done": done_count, "active": total - done_count}