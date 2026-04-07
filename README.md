# CopyKit API — Генератор сниппетов и ключевых слов на базе GigaChat

1:17

FastAPI приложение для автоматической генерации маркетинговых сниппетов и ключевых слов на основе названия бизнеса/проекта. Использует Yandex GigaChat API для анализа и генерации контента.

## 🎯 Возможности

- ✅ Генерация продающих копирайтинг-сниппетов
- ✅ Автоматический подбор ключевых слов
- ✅ Валидация входных данных
- ✅ Интерактивная документация (Swagger UI)
- ✅ Готово к деплою на Yandex Cloud Serverless Containers
- ✅ Работает локально и в облаке с одинаковым конфигом

## 🚀 Быстрый старт

### Локальная разработка

```bash
# Создать виртуальное окружение
python3.12 -m venv venv

# Активировать окружение
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Скопировать .env.example в .env и заполнить
cp .env.example .env
# Отредактируй .env и добавь свой GIGA_API ключ

# Запустить сервер (режим разработки)
fastapi dev

# Или напрямую через uvicorn
uvicorn app.copykit_api:app --reload
```

Интерактивная документация доступна: **http://127.0.0.1:8000/docs**

### API Эндпоинты

#### 1. Генерация сниппетов
```bash
GET /generate_snippets?promt=MySaaSProject
```
Возвращает:
- целевая аудитория
- ключевая боль адреса
- уникальное обещание
- доказательства/факты
- call to action
- тон общения

#### 2. Генерация ключевых слов
```bash
GET /generate_keywords?promt=MySaaSProject
```
Возвращает список релевантных ключевых слов для SEO/контекстной рекламы.

#### 3. Генерация всего
```bash
GET /generate_all?promt=MySaaSProject
```
Возвращает и сниппеты, и ключевые слова одновременно.

### Требования

- Python 3.10+
- Ключ API от Yandex GigaChat ([получить](https://gigachat.ai/))

## 🐳 Docker

### Локальная проверка контейнера

```bash
# Собрать образ
docker build -t copykit-fastapi .

# Запустить контейнер с .env
docker run --env-file .env -p 8080:8080 copykit-fastapi

# Проверить, что API живой
curl http://localhost:8080/docs
```

Образ полностью совместим и с локальным Docker, и с Yandex Cloud Serverless Containers.

## 📋 Структура проекта

```
.
├── dockerfile                  # Docker сборка
├── requirements.txt            # Python зависимости
├── .env.example               # Пример переменных окружения
├── .dockerignore              # Файлы для исключения из образа
├── README.md                  # Этот файл
├── DEPLOYMENT_YANDEX_CLOUD.md # Подробная инструкция по деплою
└── app/
    ├── __init__.py
    ├── copykit_api.py         # FastAPI маршруты
    └── copykit.py             # Основная логика (GigaChat интеграция)
```

## 🔧 Переменные окружения

| Переменная | Описание | Обязательна | Default |
|-----------|---------|-----------|---------|
| `GIGA_API` | API ключ Yandex GigaChat | ✅ Да | - |
| `MAX_INPUT_LENGTH` | Макс длина промпта (символы) | ❌ Нет | `100` |
| `PORT` | Порт запуска (только Docker) | ❌ Нет | `8080` |

Получить `GIGA_API`: https://gigachat.ai/ → Личный кабинет → API Ключи

## ✅ Статус готовности к деплою

- ✅ Dockerfile оптимизирован (python:3.10-slim)
- ✅ Использует переменную PORT для совместимости с Yandex Cloud
- ✅ Модульная структура приложения
- ✅ Обработка ошибок и валидация входных данных
- ✅ .dockerignore настроен
- ✅ .env.example подготовлен
- ✅ `deploy.sh` скрипт готов
- ✅ **Готово к деплою! Запустите: `./deploy.sh`**

## 🌐 Деплой на Yandex Cloud Serverless Containers

### 🚀 Быстрый деплой (Скрипт)

```bash
# 1. Установить переменные окружения
export YC_REGISTRY_ID="crXXXXXXXXXXXXXXXXXX"       # ID вашего Container Registry
export YC_FOLDER_ID="b1XXXXXXXXXXXXXXXXXXXX"      # ID вашей папки в YC

# 2. Запустить автоматический скрипт
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматически:
- ✅ Собирает Docker образ
- ✅ Тестирует его локально
- ✅ Pushит в Yandex Registry
- ✅ Развёртывает на Serverless Container
- ✅ Выдаёт публичный URL

### 📖 Полная инструкция

Детальная пошаговая инструкция: **[DEPLOYMENT_MANUAL.md](./DEPLOYMENT_MANUAL.md)**

Там описано:
- Установка YC CLI
- Создание сервис-аккаунта
- Создание Container Registry
- Все команды для ручного развертывания
- Troubleshooting

## 🔗 Интеграция с Next.js фронтендом

После деплоя добавь в `.env.local` фронтенда:

```env
NEXT_PUBLIC_API_URL=https://your-url.containers.yandexcloud.net
```

И используй в коде:

```javascript
const res = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/generate_keywords?promt=MyProject`
);
const data = await res.json();
console.log(data.keywords);
```

## 📝 Примеры запросов

### cURL

```bash
curl "https://your-url.containers.yandexcloud.net/generate_keywords?promt=Fitness%20App"
curl "https://your-url.containers.yandexcloud.net/docs"
```

### JavaScript (fetch)

```javascript
const response = await fetch(
  'https://your-url.containers.yandexcloud.net/generate_snippets?promt=E-commerce%20Platform'
);
const { snippet, keywords, promt } = await response.json();
```

## ⚠️ Важные замечания

- **MAX_INPUT_LENGTH**: По умолчанию 100 символов. Чем выше — тем дольше ответ GigaChat
- **Таймауты**: В Yandex Cloud Serverless установлены на 60 сек (для GigaChat обычно достаточно)
- **Приватность**: По умолчанию контейнер публичный. Для ограничения доступа используй IAM политики
- **Логирование**: GigaChat может быть медленнее других LLM, учитывай это в SLA

## 📚 Ссылки

- [Yandex GigaChat](https://gigachat.ai/)
- [Yandex Cloud Serverless Containers](https://cloud.yandex.ru/services/serverless-containers)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker Docs](https://docs.docker.com/)

## 📧 Поддержка

Если контейнер не стартует локально, не будет стартовать и в облаке. Проверь:
- Валидность GIGA_API ключа
- Что PORT переменная читается корректно
- Логи: `docker logs <container_id>`

---

**Статус**: ✅ Готово к деплою на Yandex Cloud







