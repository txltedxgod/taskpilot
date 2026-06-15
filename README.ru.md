# 🛫 TaskPilot

[![CI](https://github.com/txltedxgod/taskpilot/actions/workflows/ci.yml/badge.svg)](https://github.com/txltedxgod/taskpilot/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-261230.svg)](https://github.com/astral-sh/ruff)

**TaskPilot** — лёгкий инструмент для автоматизации и планирования задач на Python.
Опиши *что* нужно запускать и *когда* в простом YAML-файле, а TaskPilot возьмёт на
себя разбор cron-выражений, цикл планирования, выполнение задач, обработку ошибок
и структурированное логирование — **без тяжёлых зависимостей** (только `PyYAML`).

Думай об этом как о крошечном, легко изучаемом cron-демоне, который можно прочитать
за вечер и расширить за пару минут.

---

## 🛰️ Демо — Flight Deck

Самодостаточный дашборд, визуализирующий пример конфига из
[`examples/tasks.yaml`](examples/tasks.yaml): живые циферблаты обратного отсчёта
до следующего запуска каждой задачи, переключатель ARMED/STANDBY, кнопка
ручного запуска и лента «flight log».

➡️ **[Открыть демо Flight Deck](https://txltedxgod.github.io/taskpilot/dashboard.html)**
*(чтобы ссылка заработала — включи GitHub Pages: ветка `main`, папка `/docs`)*

Либо запусти локально — без сборки, просто открой файл:

```bash
open docs/dashboard.html      # macOS
start docs\dashboard.html     # Windows
```

---

## ✨ Возможности

- **Настоящие cron-выражения** — `*`, диапазоны (`1-5`), списки (`1,3,5`), шаги
  (`*/15`) и алиасы (`@hourly`, `@daily`, `@weekly`, `@monthly`).
- **Подключаемые действия (actions)** — встроенные `log`, `shell`, `http` и
  `webhook`, плюс однострочный декоратор для регистрации своих.
- **Конфигурация через файл** — задачи описываются в YAML или JSON; для типовых
  автоматизаций код не нужен.
- **Удобный CLI** — подкоманды `list`, `next`, `run`, `serve` и `actions`.
- **Тестируемое ядро** — планировщик — чистая функция от текущего времени, поэтому
  всё поведение покрыто быстрыми, детерминированными unit-тестами.
- **Типизация и линтинг** — чисто проходит `mypy` + `ruff`, CI на Python 3.9–3.12.

---

## 📦 Установка

```bash
git clone https://github.com/txltedxgod/taskpilot.git
cd taskpilot
pip install -e ".[dev]"   # убери [dev] для установки только runtime-зависимостей
```

---

## 🚀 Быстрый старт

Создай конфиг (или используй готовый [`examples/tasks.yaml`](examples/tasks.yaml)):

```yaml
tasks:
  - name: heartbeat
    schedule: "*/5 * * * *"     # каждые 5 минут
    action: log
    params:
      message: "TaskPilot is alive"

  - name: nightly-backup
    schedule: "@daily"          # каждый день в полночь
    action: shell
    params:
      command: "tar czf /tmp/backup.tgz ./data"
```

Дальше управляй им через CLI:

```bash
# Посмотреть, что настроено
taskpilot list -c examples/tasks.yaml

# Узнать время следующего запуска каждой задачи (JSON)
taskpilot next -c examples/tasks.yaml

# Запустить одну задачу прямо сейчас (удобно для отладки)
taskpilot run -c examples/tasks.yaml --task heartbeat

# Запустить цикл планирования
taskpilot serve -c examples/tasks.yaml --poll 60
```

> Совет: добавь `--dry-run` к команде `run`, чтобы безопасно посмотреть, что сделает
> действие, без побочных эффектов.

---

## 🧩 Написание собственного действия (action)

Действия — это просто функции, зарегистрированные по имени:

```python
from taskpilot.actions.base import ActionContext, registry

@registry.register("greet")
def greet(context: ActionContext, who: str = "world") -> str:
    return f"Hello, {who}!"
```

Используй его в конфиге:

```yaml
tasks:
  - name: say-hi
    schedule: "0 9 * * 1-5"
    action: greet
    params:
      who: "team"
```

---

## 🧠 Использование TaskPilot как библиотеки

```python
from datetime import datetime
from taskpilot import CronSchedule, Task, Scheduler

task = Task(
    name="tick",
    schedule=CronSchedule.parse("*/5 * * * *"),
    action="log",
    params={"message": "tick"},
)

scheduler = Scheduler([task])
results = scheduler.run_pending(datetime.now())
for r in results:
    print(r.as_dict())
```

---

## 🗂 Структура проекта

```
taskpilot/
├── src/taskpilot/
│   ├── cron.py          # парсер и матчер cron без внешних зависимостей
│   ├── models.py        # датаклассы Task / TaskResult
│   ├── config.py        # загрузчик YAML/JSON
│   ├── runner.py        # выполняет задачу, собирает результаты
│   ├── scheduler.py      # цикл планирования/опроса
│   ├── cli.py            # CLI на основе argparse
│   └── actions/          # встроенные действия и реестр действий
├── tests/                # набор тестов pytest (cron, config, scheduler, actions)
├── examples/tasks.yaml   # пример конфигурации
└── .github/workflows/    # CI: линтинг + проверка типов + тесты (3.9–3.12)
```

---

## 🧪 Разработка

```bash
ruff check .       # линтинг
mypy               # проверка типов
pytest --cov=taskpilot --cov-report=term-missing
```

Контрибьюции приветствуются — см. [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 Лицензия

Распространяется под лицензией [MIT](LICENSE).
