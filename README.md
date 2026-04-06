# fastapi-ai-project
видео инструкция
остановился на 48:03
https://youtu.be/yxyyYMWu1ZA?si=CCoSttjvu1ty2JSp


Запуск виртуального окружения

```
python3.12 -m venv venv
```

```
source venv/bin/actiate
```

Установка зависимостей

```
pip3 install -r requirements.txt
```

запуск сервера 

```
fastapi dev
```

для запуска сервера

```
uvicorn copykit_api:app --reload
```

интерактивная документация со всеми эндпоинтами

```
http://127.0.0.1:8000/docs
```

