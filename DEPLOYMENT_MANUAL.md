# 🚀 Deployment Guide - Yandex Cloud Serverless Container

Простой гайд по развёртыванию FastAPI + GigaChat в Yandex Cloud без CI/CD.

## Требования

- ✅ Docker установлен и работает
- ✅ Yandex Cloud CLI (`yc`) установлен
- ✅ Аккаунт в Yandex Cloud
- ✅ Сервис-аккаунт с правами на Container Registry
- ✅ .env файл с `GIGA_API`

## Шаг 1: Установка Yandex Cloud CLI

```bash
curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash

# Перезагрузить shell
exec -l $SHELL

# Проверить установку
yc --version
```

## Шаг 2: Инициализация YC и создание сервис-аккаунта

```bash
# Инициализация
yc init

# Получить ID папки
FOLDER_ID=$(yc config get folder-id)
echo "Folder ID: $FOLDER_ID"

# Создать сервис-аккаунт
yc iam service-account create --name copykit-sa --folder-id $FOLDER_ID

# Получить ID сервис-аккаунта
SA_ID=$(yc iam service-account list --folder-id $FOLDER_ID --format json | jq -r '.[0].id')
echo "Service Account ID: $SA_ID"

# Добавить роль для Container Registry
yc resource-manager folder add-access-binding $FOLDER_ID \
  --service-account-id=$SA_ID \
  --role=container-registry.images.pusher

# Создать ключ
yc iam service-account key create --service-account-id=$SA_ID --output key.json

# Сохранить путь для скрипта
export YC_SERVICE_ACCOUNT_KEY=$(cat key.json)
```

## Шаг 3: Создание Container Registry

```bash
# Создать реестр
yc container registry create --name copykit-registry

# Получить ID реестра
REGISTRY_ID=$(yc container registry list --format json | jq -r '.[0].id')
echo "Registry ID: $REGISTRY_ID"

# Сохранить переменные окружения для скрипта
export YC_REGISTRY_ID=$REGISTRY_ID
export YC_FOLDER_ID=$FOLDER_ID
```

## Шаг 4: Создание Serverless Container

```bash
# Создать serverless контейнер
yc serverless container create \
  --name copykit-fastapi \
  --folder-id $YC_FOLDER_ID
```

## Шаг 5: Подготовка .env файла

```bash
# Копировать .env.example
cp .env.example .env

# Отредактировать .env и добавить свои значения
# GIGA_API=your-uuid-key-here
# MAX_INPUT_LENGTH=100
nano .env
```

## Шаг 6: Развертывание

### Вариант A: Автоматический скрипт (рекомендуется)

```bash
# Дать права на выполнение
chmod +x deploy.sh

# Установить переменные окружения
export YC_REGISTRY_ID="crXXXXXXXXXXXXXXXXXX"
export YC_FOLDER_ID="b1XXXXXXXXXXXXXXXXXXXX"

# Запустить скрипт
./deploy.sh
```

### Вариант B: Ручной процесс

```bash
# 1. Собрать образ
docker build -t copykit-fastapi:latest .

# 2. Протестировать
docker run -d --name test \
  --env GIGA_API=test \
  --env MAX_INPUT_LENGTH=100 \
  -p 8080:8080 \
  copykit-fastapi:latest

# Проверить здоровье (должен вернуть 200)
curl http://localhost:8080/docs

# Остановить контейнер
docker stop test && docker rm test

# 3. Настроить Docker для реестра
yc container registry configure-docker

# 4. Тегировать образ
docker tag copykit-fastapi:latest \
  cr.yandex.ru/$YC_REGISTRY_ID/copykit-fastapi:latest

# 5. Push в реестр
docker push cr.yandex.ru/$YC_REGISTRY_ID/copykit-fastapi:latest

# 6. Развернуть контейнер
GIGA_API=$(grep GIGA_API .env | cut -d'=' -f2)
SA_ID=$(yc iam service-account list --folder-id $YC_FOLDER_ID --format json | jq -r '.[0].id')

yc serverless container revision deploy \
  --container-name copykit-fastapi \
  --image cr.yandex.ru/$YC_REGISTRY_ID/copykit-fastapi:latest \
  --cores 1 \
  --memory 512MB \
  --concurrency 5 \
  --execution-timeout 60s \
  --service-account-id $SA_ID \
  --environment GIGA_API=$GIGA_API,MAX_INPUT_LENGTH=100 \
  --folder-id $YC_FOLDER_ID

# 7. Получить URL
yc serverless container get --name copykit-fastapi --folder-id $YC_FOLDER_ID --format json | jq -r '.url'
```

## Шаг 7: Проверка

```bash
# Получить URL контейнера
CONTAINER_URL=$(yc serverless container get --name copykit-fastapi --folder-id $YC_FOLDER_ID --format json | jq -r '.url')

# Проверить Swagger UI
curl $CONTAINER_URL/docs

# Протестировать API
curl "$CONTAINER_URL/generate_snippets?promt=hello%20world"
```

## 🐛 Troubleshooting

### Ошибка 403 Forbidden при push

**Причина:** сервис-аккаунт не имеет прав
**Решение:** проверить роль в IAM → добавить `container-registry.images.pusher`

```bash
yc resource-manager folder add-access-binding $YC_FOLDER_ID \
  --service-account-id=$SA_ID \
  --role=container-registry.images.pusher
```

### Docker push не авторизован

```bash
# Пересконфигурировать Docker
yc container registry configure-docker --folder-id $YC_FOLDER_ID
```

### Контейнер не запускается

Проверить логи:
```bash
yc serverless container logs \
  --name copykit-fastapi \
  --folder-id $YC_FOLDER_ID \
  --tail 100
```

## 📊 Мониторинг

Проверить статус контейнера:
```bash
yc serverless container get --name copykit-fastapi --folder-id $YC_FOLDER_ID
```

Просмотреть логи:
```bash
yc serverless container logs \
  --name copykit-fastapi \
  --folder-id $YC_FOLDER_ID
```

## 💡 Полезные команды

```bash
# Обновить контейнер (new deployment)
yc serverless container revision deploy \
  --container-name copykit-fastapi \
  --image cr.yandex.ru/$YC_REGISTRY_ID/copykit-fastapi:latest \
  --folder-id $YC_FOLDER_ID

# Список контейнеров
yc serverless container list --folder-id $YC_FOLDER_ID

# Удалить контейнер
yc serverless container delete copykit-fastapi --folder-id $YC_FOLDER_ID
```

---

**Успехов с развертыванием!** 🎉
