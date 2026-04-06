# 🚀 Настройка CI/CD на GitHub Actions

Полностью автоматический деплой на Yandex Cloud Serverless Containers.

## 📋 Что настроили

GitHub Actions workflow (`.github/workflows/deploy.yml`) делает:

1. ✅ При `push` в `main` ветку:
   - Собирает Docker образ
   - Локально тестирует контейнер
   - Пушит в Yandex Container Registry
   - Делает `revision deploy` на Yandex Cloud
   - Отправляет уведомление в Slack

2. ✅ При создании `release`/`tag`:
   - Все то же самое, но с тегом версии

## 🔐 Что нужно настроить в GitHub

### Шаг 1: Получи Yandex Cloud Service Account Key

```bash
# На твоём компьютере локально:

# 1. Создай service account (если ещё не создан)
yc iam service-account create --name github-ci

# 2. Создай认證 ключ
yc iam key create --service-account-name github-ci --output sa-key.json

# 3. Содержимое файла нужно скопировать в GitHub secrets
cat sa-key.json
# Выдаст что-то вроде:
# {
#   "id": "ajexxxxxxxxxxx",
#   "service_account_id": "ajexxxxxxxxxxx",
#   "created_at": "2026-04-07...",
#   "key_algorithm": "RSA_2048",
#   "public_key": "-----BEGIN PUBLIC KEY-----...",
#   "private_key": "-----BEGIN PRIVATE KEY-----..."
# }
```


id: ajesl5ki00acebvl9jop
folder_id: b1gsqihlr0jhh3spccd3
created_at: "2026-04-06T22:00:25Z"
name: github-ci

# Замени <FOLDER_ID> на реальный ID
yc resource-manager folder add-access-binding b1gsqihlr0jhh3spccd3 \
  --role container-registry.images.pusher \
  --service-account-name github-ci

yc resource-manager folder add-access-binding b1gsqihlr0jhh3spccd3 \
  --role serverless.containers.editor \
  --service-account-name github-ci



Получение необходимых айди

# Registry ID
yc container registry get copykit-registry --format=json | jq '.id'

# Folder ID
yc config list | grep folder-id

# Service Account ID
yc iam service-account get github-ci --format=json | jq '.id'


Это будет содержимое secret `YC_SERVICE_ACCOUNT_KEY`.

### Шаг 2: Выдай service account права в Yandex Cloud

```bash
# Дай права на push в registry
yc resource-manager folder add-access-binding b1gsqihlr0jhh3spccd3 \
  --role container-registry.images.pusher \
  --service-account-name github-ci

# Дай права на создание/изменение контейнеров
yc resource-manager folder add-access-binding b1gsqihlr0jhh3spccd3 \
  --role serverless.containers.editor \
  --service-account-name github-ci
```

### Шаг 3: Получи нужные ID

```bash
# Registry ID
yc container registry get copykit-registry --format=json | jq '.id'
# Результат: crxxxxxxxxxxxxx

# Folder ID
yc config list
# Найди folder-id

# Service Account ID
yc iam service-account get github-ci --format=json | jq '.id'
# Результат: ajexxxxxxxxxxx
```

### Шаг 4: Добавь secrets в GitHub репо

Переходишь в GitHub:
1. Repo → **Settings** → **Secrets and variables** → **Actions**
2. Нажимаешь **New repository secret**

Добавляешь следующие secrets:

| Secret Name | Значение | Где взять |
|------------|---------|----------|
| `YC_SERVICE_ACCOUNT_KEY` | Содержимое `sa-key.json` | `cat sa-key.json` |
| `YC_REGISTRY_ID` | `crxxxxxxxxxxxxx` | `yc container registry get copykit-registry` |
| `YC_FOLDER_ID` | `b1xxxxxxxxxxxxx` | `yc config list` |
| `YC_SERVICE_ACCOUNT_ID` | `ajexxxxxxxxxxx` | `yc iam service-account get github-ci` |
| `GIGA_API` | Твой UUID ключ | https://gigachat.ai/ → API Ключи |
| `SLACK_WEBHOOK` | (опционально) | Твой Slack вебхук |

**Пример добавления YAML:**

```yaml
name: YC_REGISTRY_ID
type: repository secret
value: crxxxxxxxxxxxxx
```

---

## 🎯 Как работает pipeline

### Триггер 1: Push в main

```bash
git add .
git commit -m "Update copykit API"
git push origin main
```

↓ Автоматически:
1. GitHub Actions запускает workflow
2. Собирает Docker образ (`docker build`)
3. Тестирует локально (`curl http://localhost:8080/docs`)
4. Пушит в registry (`docker push cr.yandex/...`)
5. Делает `yc serverless container revision deploy`
6. Отправляет уведомление в Slack

Примерное время: **2-3 минуты**

### Триггер 2: Создание release/tag

```bash
# Локально
git tag v1.0.0
git push origin v1.0.0

# Или через GitHub UI:
# Releases → Draft a new release → v1.0.0
```

↓ Все то же самое, но образ тегируется не только как `:latest`, но и как `:v1.0.0`

---

## 📊 Мониторинг

### В GitHub

1. Repo → **Actions** → выбираешь workflow run
2. Видишь все шаги, логи, ошибки

### В Slack (если настроен)

При успехе:
```
✅ CopyKit API deployed successfully
Branch: refs/heads/main
Commit: abc123...
Author: yourself
```

При ошибке:
```
❌ CopyKit API deployment failed
Branch: refs/heads/main
Commit: abc123...
```

---

## 🔍 Что если что-то сломалось?

### ❌ GitHub Action не запускается

**Причина**: workflow файл не в `.github/workflows/`

```bash
ls -la .github/workflows/
# Должен быть deploy.yml
```

### ❌ Ошибка авторизации в registry

**Причина**: неправильный `YC_SERVICE_ACCOUNT_KEY`

```bash
# Проверь:
1. Файл sa-key.json скопирован полностью (весь JSON)
2. Нет лишних переносов строк
3. Service account имеет права container-registry.images.pusher
```

### ❌ Container не деплоится

**Причина**: `YC_SERVICE_ACCOUNT_ID` неправильный

```bash
# Проверь:
yc iam service-account get github-ci --format=json | jq '.id'
# ID должен совпадать с secret
```

### ❌ Видишь ошибку пермишенов

```
yc ERR-RC-01 access denied
```

**Решение**: выдать права service account:

```bash
yc resource-manager folder add-access-binding <FOLDER_ID> \
  --role container-registry.images.pusher \
  --service-account-name github-ci

yc resource-manager folder add-access-binding <FOLDER_ID> \
  --role serverless.containers.editor \
  --service-account-name github-ci
```

---

## 📝 Что деплоится

При каждом push:
- **Образ**: `cr.yandex/<REGISTRY_ID>/copykit-fastapi:latest`
- **Контейнер**: `copykit-fastapi` (обновится существующий)
- **Ревизия**: новая ревизия с новым кодом
- **URL**: https://bbxxxxxxxxxxxxx.containers.yandexcloud.net/ (не меняется)

---

## 🚦 Статус готовности

- ✅ Workflow создан (`.github/workflows/deploy.yml`)
- ⏳ Нужно добавить secrets в GitHub
- ⏳ Нужно выдать права service account
- ⏳ Первый push → тест деплоя

---

## Быстрый чеклист

- [ ] Service account создан: `yc iam service-account create --name github-ci`
- [ ] Ключ создан: `yc iam key create --service-account-name github-ci --output sa-key.json`
- [ ] Права выданы (images.pusher + containers.editor)
- [ ] Secrets добавлены в GitHub (YC_SERVICE_ACCOUNT_KEY, YC_REGISTRY_ID, YC_FOLDER_ID, YC_SERVICE_ACCOUNT_ID, GIGA_API)
- [ ] `.github/workflows/deploy.yml` закоммичена
- [ ] Сделан push в main
- [ ] Проверены логи в GitHub Actions

---

**Всё готово к автоматизации! 🎉**

После настройки secrets:
```bash
git add .
git commit -m "Add GitHub Actions CI/CD"
git push origin main
```

И workflow автоматически запустится.

**Дата**: апрель 2026
