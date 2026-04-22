# Nexus Orchestrator (Paperclip + Hermes + OpenClaw + MemPalace)

This repository contains an automated architecture for running autonomous AI agents using a corporate "Org Chart" structure, deploying them in separate, isolated containers, and utilizing a unified memory protocol (MemPalace).

## 🚀 Як розгорнути на VPS (Linux з встановленим Docker)

Система створена для максимальної портативності. Всі дані лежать у директорії `data/`, і ви завжди можете просто перенести цілу папку на інший сервер без втрати пам'яті агентів.

### Крок 1. Завантаження репозиторію

Якщо ви залили цей код на GitHub, підключіться до свого VPS через SSH та виконайте наступне:

```bash
# Клонуємо репозиторій
git clone https://github.com/ВАШ_ЮЗЕР/ВАША_НАЗВА_РЕПОЗИТОРІЮ.git
cd ВАША_НАЗВА_РЕПОЗИТОРІЮ

# Створюємо базовий файл ключів
cp .env.example ./data/env/.env
```

### Крок 2. Запуск всієї системи
Система налаштована через єдиний контур:
```bash
docker-compose up -d --build
```
> При першому запуску Docker завантажить всі необхідні образи (Python, Node, Paperclip, MemPalace) та збілдить ваш кастомний Gateway-скрипт.

### Крок 3. Налаштування ключів через Web UI
Після успішного старту, зайдіть в браузері на адресу вашого сервера (на порт 8000):

👉 **URL:** `http://IP_ВАШОГО_VPS:8000`

В цьому інтерфейсі:
1. Вставте ваші API-Ключі (OpenAI, Claude, Gemini), і вони автоматично збережуться в `.env` файл на сервері і будуть роздаватись агентам.
2. Ви можете вручну створювати ("спавнити") нових агентів Hermes або OpenClaw. Система сама створить під них Docker-контейнер та виділить ізольовану пам'ять (MemPalace "Wing").

## 🧠 Структура та Пам'ять
* `gateway-script/` – код управлінської адмінки.
* `data/mempalace-db/` – тут всі агенти зберігають свій контекст.
* `data/agents/` – у кожного працівника власна папка зі Skills (для Hermes) або конфігами (OpenClaw).
