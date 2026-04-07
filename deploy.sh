#!/bin/bash

# CopyKit FastAPI - Direct Deployment to Yandex Cloud Serverless Container
# Этот скрипт развёртывает контейнер напрямую в Yandex Cloud без CI/CD

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 CopyKit FastAPI - Yandex Cloud Deployment${NC}"
echo ""

# 1. Проверка переменных окружения
echo -e "${YELLOW}1️⃣  Checking environment...${NC}"

if [ -z "$YC_REGISTRY_ID" ]; then
  echo -e "${RED}❌ YC_REGISTRY_ID not set${NC}"
  echo "Set it: export YC_REGISTRY_ID=crpnf0rvfiv5edm37kfc"
  exit 1
fi

if [ -z "$YC_FOLDER_ID" ]; then
  echo -e "${RED}❌ YC_FOLDER_ID not set${NC}"
  echo "Set it: export YC_FOLDER_ID=your_folder_id"
  exit 1
fi

echo -e "${GREEN}✓ Environment OK${NC}"
echo "  Registry: $YC_REGISTRY_ID"
echo "  Folder: $YC_FOLDER_ID"
echo ""

# 2. Проверка Docker
echo -e "${YELLOW}2️⃣  Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
  echo -e "${RED}❌ Docker not installed${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"
echo ""

# 3. Проверка YC CLI
echo -e "${YELLOW}3️⃣  Checking Yandex Cloud CLI...${NC}"
if ! command -v yc &> /dev/null; then
  echo -e "${RED}❌ YC CLI not installed${NC}"
  echo "Install: curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash"
  exit 1
fi
echo -e "${GREEN}✓ YC CLI found${NC}"
echo ""

# 4. Проверка аутентификации YC
echo -e "${YELLOW}4️⃣  Checking YC authentication...${NC}"
if ! yc config list &> /dev/null; then
  echo -e "${RED}❌ YC not authenticated${NC}"
  echo "Run: yc init"
  exit 1
fi
echo -e "${GREEN}✓ YC authenticated${NC}"
echo ""

# 5. Сборка Docker образа
echo -e "${YELLOW}5️⃣  Building Docker image...${NC}"
IMAGE_NAME="copykit-fastapi"
docker build -t $IMAGE_NAME:latest .
echo -e "${GREEN}✓ Image built locally${NC}"
echo ""

# 6. Тестирование образа локально
echo -e "${YELLOW}6️⃣  Testing image locally...${NC}"
docker run -d --name test-container \
  --env GIGA_API=test \
  --env MAX_INPUT_LENGTH=100 \
  -p 8080:8080 \
  $IMAGE_NAME:latest \
  uvicorn app.copykit_api:app --host 0.0.0.0 --port 8080

sleep 5

if curl -f http://localhost:8080/docs > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Local test passed${NC}"
else
  echo -e "${RED}❌ Local test failed${NC}"
  docker logs test-container
  docker stop test-container || true
  docker rm test-container || true
  exit 1
fi

docker stop test-container
docker rm test-container
echo ""

# 7. Настройка Docker для Yandex Registry
echo -e "${YELLOW}7️⃣  Configuring Docker for Yandex Registry...${NC}"
yc container registry configure-docker
echo -e "${GREEN}✓ Docker configured for registry${NC}"
echo ""

# 8. Тегирование образа
echo -e "${YELLOW}8️⃣  Tagging image for registry...${NC}"
IMAGE_TAG="cr.yandex.ru/$YC_REGISTRY_ID/$IMAGE_NAME:latest"
docker tag $IMAGE_NAME:latest $IMAGE_TAG
echo "Tag: $IMAGE_TAG"
echo -e "${GREEN}✓ Image tagged${NC}"
echo ""

# 9. Push в реестр
echo -e "${YELLOW}9️⃣  Pushing image to registry (this may take a few minutes)...${NC}"
docker push $IMAGE_TAG
echo -e "${GREEN}✓ Image pushed${NC}"
echo ""

# 10. Развёртывание контейнера
echo -e "${YELLOW}🔟 Deploying to Yandex Cloud Serverless Container...${NC}"

CONTAINER_NAME="copykit-fastapi"
SERVICE_ACCOUNT_ID=$(yc iam service-account list --folder-id $YC_FOLDER_ID --format=json | jq -r '.[0].id')

if [ -z "$SERVICE_ACCOUNT_ID" ]; then
  echo -e "${RED}❌ No service accounts found in folder${NC}"
  exit 1
fi

# Читаем GIGA_API из .env если существует
GIGA_API=$(grep GIGA_API .env 2>/dev/null | cut -d '=' -f2 || echo "")

if [ -z "$GIGA_API" ]; then
  echo -e "${RED}❌ GIGA_API not found in .env file${NC}"
  exit 1
fi

yc serverless container revision deploy \
  --container-name $CONTAINER_NAME \
  --image $IMAGE_TAG \
  --cores 1 \
  --memory 512MB \
  --concurrency 5 \
  --execution-timeout 60s \
  --service-account-id $SERVICE_ACCOUNT_ID \
  --environment GIGA_API=$GIGA_API,MAX_INPUT_LENGTH=100 \
  --folder-id $YC_FOLDER_ID

echo -e "${GREEN}✓ Container deployed${NC}"
echo ""

# 11. Получение URL контейнера
echo -e "${YELLOW}11️⃣ Getting container URL...${NC}"
CONTAINER_URL=$(yc serverless container get --name $CONTAINER_NAME --folder-id $YC_FOLDER_ID --format json | jq -r '.url')

echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo ""
echo -e "${GREEN}Container URL: ${YELLOW}$CONTAINER_URL${NC}"
echo ""
echo "Test it:"
echo "  curl $CONTAINER_URL/docs"
echo "  curl '$CONTAINER_URL/generate_snippets?promt=hello'"
echo ""
