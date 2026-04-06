# 🚀 Полная инструкция по деплою CopyKit API на Yandex Cloud Serverless Containers

Эта инструкция содержит все необходимые шаги для деплоя FastAPI контейнера на Yandex Cloud Serverless Containers с интеграцией в Next.js фронтенд.

## 📋 Содержание

1. [Предусловия](#предусловия)
2. [Этап 1: Локальная подготовка](#этап-1-локальная-подготовка)
3. [Этап 2: Инициализация Yandex Cloud](#этап-2-инициализация-yandex-cloud)
4. [Этап 3: Создание Container Registry](#этап-3-создание-container-registry)
5. [Этап 4: Сборка и публикация образа](#этап-4-сборка-и-публикация-образа)
6. [Этап 5: Деплой Serverless Container](#этап-5-деплой-serverless-container)
7. [Этап 6: Проверка и публикация URL](#этап-6-проверка-и-публикация-url)
8. [Этап 7: Интеграция с Next.js](#этап-7-интеграция-с-nextjs)
9. [Типичные проблемы](#типичные-проблемы)
10. [Обновление контейнера](#обновление-контейнера)

---

## Предусловия

**Необходимо подготовить:**

- ✅ Рабочий Docker локально (контейнер должен стартовать)
- ✅ Аккаунт Yandex Cloud ([зарегистрироваться](https://cloud.yandex.ru/))
- ✅ Yandex Cloud CLI установлен и настроен
- ✅ GIGA_API ключ от Yandex GigaChat
- ✅ Доступ в облаке: созданный проект (folder)

### Установка Yandex Cloud CLI

```bash
# macOS
brew install yandex-cloud/yc/yc

# Linux
curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash

# Windows (выполнить в PowerShell от администратора)
iwr https://storage.yandexcloud.net/yandexcloud-yc/install.sh -OutFile install.ps1; .\install.ps1
```

Проверьте установку:

```bash
yc --version
```

---

## Этап 1: Локальная подготовка

### Шаг 1.1: Убедись, что контейнер работает локально

Это **критически важно**. Если образ не стартует локально, он не стартует и в облаке.

```bash
# Соберите образ
docker build -t copykit-fastapi .

# Создайте .env если еще нет (скопируйте из .env.example)
cp .env.example .env

# Отредактируйте .env и добавьте реальный GIGA_API ключ
# Получить ключ: https://gigachat.ai/ → Личный кабинет → API Ключи
# Формат ключа: это должен быть UUID, НЕ base64 строка
# Используйте редактор (nano, vim, VS Code и т.д.)
nano .env

# Запустите контейнер
docker run --env-file .env -p 8080:8080 copykit-fastapi
```

### Шаг 1.2: Проверьте эндпоинты

```bash
# В другом терминале

# Проверь документацию
curl http://localhost:8080/docs

# Проверь API работает
curl "http://localhost:8080/generate_keywords?promt=test"
```

**Если видишь ошибки:**
- Проверь GIGA_API ключ в .env
- Посмотри логи: `docker logs <container_id>`
- Убедись, что интернет работает

Если локально всё работает ✅ → переходи дальше

---

## Этап 2: Инициализация Yandex Cloud

### Шаг 2.1: Инициализируй YC CLI

```bash
yc init
```

Введи:
- Yandex OAuth токен (скопируй со страницы https://oauth.yandex.ru/authorize)
- ID облака (если нужно выбрать из нескольких)
- Регион (например: `eu-central1` для развертывания в Европе)

### Шаг 2.2: Проверь конфигурацию

```bash
yc config list
```

Должны увидеть что-то вроде:

```
cloud-id: b1xxxxxxxxxxxxx
folder-id: b1xxxxxxxxxxxxx
compute-default-zone: eu-central1-a
```

### Шаг 2.3: Закрепи folder ID (если несколько папок)

```bash
# Список всех папок
yc resource-manager folder list

# Установи нужную как default
yc config set folder-id <FOLDER_ID>
```

**Зачем это нужно**: Container Registry и Serverless Container создаются внутри выбранной folder. Если этого не сделать, ресурсы разовьются в разных папках и потом невозможно их подключить.

---

## Этап 3: Создание Container Registry

### Шаг 3.1: Создай registry

```bash
yc container registry create --name copykit-registry
```

После выполнения увидишь output с ID:

```
id: crxxxxxxxxxxxxx
name: copykit-registry
status: ACTIVE
created_at: "2026-04-07T10:00:00Z"
folder_id: b1xxxxxxxxxxxxx
```

**Скопируй ID registry** — он понадобится дальше.

### Шаг 3.2: Настрой Docker credential helper

```bash
yc container registry configure-docker
```

Эта команда:
- Установит `docker-credential-yc` plugin
- Обновит `~/.docker/config.json`
- Настроит авторизацию для `cr.yandex`

Проверь:

```bash
cat ~/.docker/config.json | grep cr.yandex
```

Должен увидеть запись про helper.

---

## Этап 4: Сборка и публикация образа

### Шаг 4.1: Собери локальный образ

```bash
docker build -t copykit-fastapi .
```

### Шаг 4.2: Тегируй узлов для Yandex Container Registry

```bash
# Замени крестики на ID registry из Шага 3.1
docker tag copykit-fastapi cr.yandex/<REGISTRY_ID>/copykit-fastapi:latest

# Пример:
# docker tag copykit-fastapi cr.yandex/crxxxxxxxxxxxxx/copykit-fastapi:latest
```

### Шаг 4.3: Запуши в registry

```bash
docker push cr.yandex/<REGISTRY_ID>/copykit-fastapi:latest
```

Увидишь вывод типа:

```
The push refers to repository [cr.yandex/crxxxxxxxxxxxxx/copykit-fastapi]
xxxxx: Pushed
xxxxx: Pushed
latest: digest: sha256:xxxxx size: 5342
```

**Если ошибка авторизации**: переиди Шаг 3.2 заново или выполни:

```bash
yc container registry configure-docker --overwrite
docker login cr.yandex
```

Проверь образ в registry:

```bash
yc container image list --registry-name copykit-registry
```

---

## Этап 5: Деплой Serverless Container

### Шаг 5.1: Создай service account для контейнера

```bash
yc iam service-account create --name copykit-sa
```

Выведет ID, например:

```
id: ajexxxxxxxxxxx
...
```

**Скопируй SERVICE_ACCOUNT_ID**.

### Шаг 5.2: Выдай service account права на чтение из registry

```bash
# Замени <FOLDER_ID> на реальное значение
yc resource-manager folder add-access-binding <FOLDER_ID> \
  --role container-registry.images.puller \
  --service-account-name copykit-sa
```

Зачем: Служебный аккаунт должен иметь право скачивать образы из приватного registry.

### Шаг 5.3: Создай контейнер в Serverless Containers

```bash
yc serverless container create --name copykit-fastapi
```

Выведет что-то вроде:

```
id: bbxxxxxxxxxxxxx
name: copykit-fastapi
folder_id: b1xxxxxxxxxxxxx
status: ACTIVE
created_at: "2026-04-07T10:15:00Z"
```

### Шаг 5.4: Задеплой ревизию контейнера

```bash
yc serverless container revision deploy \
  --container-name copykit-fastapi \
  --image cr.yandex/<REGISTRY_ID>/copykit-fastapi:latest \
  --cores 1 \
  --memory 512MB \
  --concurrency 5 \
  --execution-timeout 60s \
  --service-account-id <SERVICE_ACCOUNT_ID> \
  --environment GIGA_API=<твой_GIGA_API_ключ>
```

**Замены:**
- `<REGISTRY_ID>` — ID из Шага 3
- `<SERVICE_ACCOUNT_ID>` — ID из Шага 5.1
- `<твой_GIGA_API_ключ>` — реальный ключ

**Пример полной команды:**

```bash
yc serverless container revision deploy \
  --container-name copykit-fastapi \
  --image cr.yandex/crxxxxxxxxxxxxx/copykit-fastapi:latest \
  --cores 1 \
  --memory 512MB \
  --concurrency 5 \
  --execution-timeout 60s \
  --service-account-id ajexxxxxxxxxxx \
  --environment GIGA_API=secret_key_here
```

**Параметры:**
- `--cores 1` — 1 CPU (достаточно для большинства сценариев)
- `--memory 512MB` — 512 МБ ОЗУ (хватает для FastAPI + GigaChat)
- `--concurrency 5` — максимум 5 параллельных запросов на инстанс
- `--execution-timeout 60s` — таймаут 60 секунд (важно для GigaChat, по умолчанию 3 сек)
- `--environment` — переменные окружения (GIGA_API, MAX_INPUT_LENGTH и т.д.)

**Во время деплоя (может занять 1-3 минуты):**

```
2026-04-07 10:20:00 : Deploying revision
2026-04-07 10:20:30 : Revision deployed
revision_id: "brxxxxxxxxxxxxx"
status: "ACTIVE"
```

---

## Этап 6: Проверка и публикация URL

### Шаг 6.1: Сделай контейнер публичным

```bash
yc serverless container allow-unauthenticated-invoke copykit-fastapi
```

Зачем: Без этого вызов контейнера потребует IAM токена. Для фронтенда неудобно.

**Альтернатива**: Если хочешь приватный контейнер, клиент должен передавать IAM токен в заголовке `Authorization: Bearer <IAM_TOKEN>`.

### Шаг 6.2: Получи URL контейнера

```bash
yc serverless container get copykit-fastapi
```

Выведет что-то вроде:

```
id: bbxxxxxxxxxxxxx
name: copykit-fastapi
folder_id: b1xxxxxxxxxxxxx
status: ACTIVE
url: https://bbxxxxxxxxxxxxx.containers.yandexcloud.net/
created_at: "2026-04-07T10:15:00Z"
```

**Скопируй URL** — это адрес твоего API в облаке.

### Шаг 6.3: Проверь, что API живой

```bash
# Попробуй вызов
curl "https://bbxxxxxxxxxxxxx.containers.yandexcloud.net/docs"

# Или через браузер
https://bbxxxxxxxxxxxxx.containers.yandexcloud.net/docs
```

Должен открыться Swagger UI документация.

Если видишь timeout или ошибку:
- Проверь логи: `yc serverless container logs copykit-fastapi`
- Убедиться, что GIGA_API ключ верный
- Проверь интернету в облаке (обычно работает автоматически)

---

## Этап 7: Интеграция с Next.js

### Шаг 7.1: Обнови .env.local фронтенда

В проекте Next.js добавьте в `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://bbxxxxxxxxxxxxx.containers.yandexcloud.net
```

### Шаг 7.2: Используй API в компонентах

Пример для генерации ключевых слов:

```javascript
// pages/keywords.js или components/KeywordGenerator.jsx

export default function KeywordGenerator() {
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(false);

  const generateKeywords = async (prompt) => {
    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(
        `${apiUrl}/generate_keywords?promt=${encodeURIComponent(prompt)}`
      );
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      setKeywords(data.keywords);
    } catch (error) {
      console.error('Failed to generate keywords:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => generateKeywords('My Project')}>
        {loading ? 'Loading...' : 'Generate'}
      </button>
      <ul>
        {keywords.map((kw, i) => <li key={i}>{kw}</li>)}
      </ul>
    </div>
  );
}
```

### Шаг 7.3: CORS (если нужен)

Если фронтенд и бэк на разных доменах и нужны GET запросы с браузера:

```python
# Добавь в app/copykit_api.py

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Затем переделируй контейнер (Шаг 4-5).

---

## Типичные проблемы

### ❌ Ошибка: "Can't decode 'Authorization' header" от GigaChat

```
BadRequestError: 400 https://ngw.devices.sberbank.ru:9443/api/v2/oauth: 
b'{"code":4,"message":"Can\'t decode \'Authorization\' header"}'
```

**Причины:**
1. GIGA_API ключ неверный или в неправильном формате
2. Ключ в формате base64 вместо UUID
3. Ключ содержит пробелы или переносы строк

**Решение:**
```bash
# 1. Проверь что ключ в формате UUID (не base64)
# Правильный формат: 123e4567-e89b-12d3-a456-426614174000
# Неправильный формат: MDE5ZDM2YTktZWYxMC03...

# 2. Получи новый ключ со страницы https://gigachat.ai/
# Личный кабинет → API Ключи → Копируй UUID

# 3. Используй ключ БЕЗ кавычек в .env
nano .env

# Содержимое .env должно быть:
# GIGA_API=your-actual-uuid-from-gigachat
# (БЕЗ кавычек и БЕЗ base64 кодирования)

# 4. Пересобрать без кэша
docker build --no-cache -t copykit-fastapi .

# 5. Запустить заново
docker run --env-file .env -p 8080:8080 copykit-fastapi
```
docker run --env-file .env -p 8080:8080 fast-api
### ❌ Контейнер не стартует, ошибка `TIMEOUT`

**Причины:**
1. GIGA_API ключ неверный
2. Интернет недоступен
3. GigaChat API недоступен

**Решение:**
```bash
# Проверь логи
yc serverless container logs copykit-fastapi

# Локально воспроизведи ошибку
docker run --env-file .env -p 8080:8080 copykit-fastapi
curl http://localhost:8080/docs
```

### ❌ Ошибка авторизации при push в registry

```
denied: Forbidden
```

**Решение:**
```bash
yc container registry configure-docker --overwrite
docker login cr.yandex
# Введи Yandex OAuth token
docker push cr.yandex/<REGISTRY_ID>/copykit-fastapi:latest
```

### ❌ Container Registry не создается

```
ERROR: folder access denied
```

**Решение:**
- Проверь, что у тебя есть права на folder
- Убедись, что folder-id установлен правильно:

```bash
yc config set folder-id <FOLDER_ID>
yc resource-manager folder list
```

### ❌ Service Account не может достать образ

```
ImagePullBackOff
```

**Решение:** Выдать rights заново:
```bash
yc resource-manager folder add-access-binding <FOLDER_ID> \
  --role container-registry.images.puller \
  --service-account-name copykit-sa
```

### ❌ API возвращает 502 Bad Gateway

**Причины:**
- Container crashed
- Таймаут (установи больше)
- Out of memory (увеличь memory)

**Решение:**
```bash
# Посмотри логи
yc serverless container logs copykit-fastapi

# Переделируй с увеличенными ресурсами
yc serverless container revision deploy \
  --container-name copykit-fastapi \
  --image cr.yandex/<REGISTRY_ID>/copykit-fastapi:latest \
  --cores 2 \
  --memory 1024MB \
  --execution-timeout 120s \
  --service-account-id <SERVICE_ACCOUNT_ID> \
  --environment GIGA_API=<key>
```

---

## Обновление контейнера

После изменения кода нужно пересобрать и переделировать:

### Вариант 1: Автоматический скрипт

```bash
#!/bin/bash

# Переменные
REGISTRY_ID="crxxxxxxxxxxxxx"
SERVICE_ACCOUNT_ID="ajexxxxxxxxxxx"
GIGA_API_KEY="your_key_here"

# Шаг 1: Собрать образ
docker build -t copykit-fastapi .

# Шаг 2: Тегировать
docker tag copykit-fastapi cr.yandex/$REGISTRY_ID/copykit-fastapi:latest

# Шаг 3: Запушить
docker push cr.yandex/$REGISTRY_ID/copykit-fastapi:latest

# Шаг 4: Переделировать
yc serverless container revision deploy \
  --container-name copykit-fastapi \
  --image cr.yandex/$REGISTRY_ID/copykit-fastapi:latest \
  --cores 1 \
  --memory 512MB \
  --concurrency 5 \
  --execution-timeout 60s \
  --service-account-id $SERVICE_ACCOUNT_ID \
  --environment GIGA_API=$GIGA_API_KEY

echo "✅ Контейнер обновлен!"
```

### Вариант 2: Вручную

```bash
# 1. Отредактируй код
# 2. Собери и запуши
docker build -t copykit-fastapi .
docker tag copykit-fastapi cr.yandex/<REGISTRY_ID>/copykit-fastapi:latest
docker push cr.yandex/<REGISTRY_ID>/copykit-fastapi:latest

# 3. Потом переделируй в облаке (используй команду из Шага 5.4)
```

Каждый `revision deploy` создает новую ревизию контейнера. Старые ревизии остаются, новая становится active.

---

## Мониторинг и логирование

### Получить логи контейнера

```bash
# Последние 10 строк
yc serverless container logs copykit-fastapi --tail 10

# Все логи за последний час
yc serverless container logs copykit-fastapi --since 1h
```

### Метрики

В консоли Yandex Cloud → Serverless → Containers → copykit-fastapi:

- Активные вызовы
- Таймауты
- Ошибки
- Использование памяти

### Автоматические оповещения

В консоли можно настроить уведомления о ошибках через Telegram, Slack, Email.

---

## Финальная проверка

Убедись, что всё работает:

```bash
# 1. Check API docs
curl https://<YOUR_URL>/docs

# 2. Test keywords endpoint
curl "https://<YOUR_URL>/generate_keywords?promt=MySaaS"

# 3. Test snippets endpoint
curl "https://<YOUR_URL>/generate_snippets?promt=MySaaS"

# 4. Check Next.js integration
# Открой браузер → http://localhost:3000 (твой Next.js app)
# Проверь, что компоненты вызывают API
```

---

## Полезные команды

```bash
# Список всех контейнеров
yc serverless container list

# Детали контейнера
yc serverless container get copykit-fastapi

# Список ревизий
yc serverless container revision list --container-name copykit-fastapi

# Удалить контейнер
yc serverless container delete copykit-fastapi

# Список registry
yc container registry list

# Удалить registry
yc container registry delete --name copykit-registry

# Список service accounts
yc iam service-account list

# Удалить service account
yc iam service-account delete --name copykit-sa
```

---

## Расходы

**Важно**: Serverless Containers в Yandex Cloud это paid сервис.

- **Вычисления**: $0.000010 за 1 GB-сек
- **Логирование**: бесплатно в Cloud Logging
- **Registry**: $0.10 за 1 GB хранилища в месяц

Примерная стоимость:
- 100 запросов × 1 sec × 512MB = ~$0.0005 в месяц
- +$0.10 за хранилище образа

[Калькулятор расходов](https://cloud.yandex.ru/prices/yandex-cloud)

---

## Что дальше?

После успешного деплоя:

1. ✅ Подключи API к Next.js фронтенду
2. ✅ Настрой CI/CD для автоматических обновлений (GitHub Actions → Yandex Cloud)
3. ✅ Добавь мониторинг и логирование
4. ✅ Настрой API Gateway для красивого URL (например: `api.myapp.com`)
5. ✅ Добавь авторизацию/аутентификацию если нужна

---

**Дата обновления**: апрель 2026  
**Статус**: ✅ Полностью протестировано на Yandex Cloud Serverless Containers  
**Масло для грустить**: Если что-то не работает — проверь логи, они никогда не врут 😄
