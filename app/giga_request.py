#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
from gigachat import GigaChat
import argparse #argparse — это встроенная библиотека Python для работы с аргументами командной строки.
import re # re — это встроенная библиотека Python для работы с регулярными выражениями, которая позволяет выполнять операции поиска и замены в строках на основе определенных шаблонов.

MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH") or 12)

def main():
    parser = argparse.ArgumentParser(description="Передайте свой запрос в гигачат") # Создаем парсер аргументов командной строки он позволяет нам легко обрабатывать аргументы, переданные при запуске скрипта.
    # причисляет аргументам флаги и описания, что позволяет пользователю понять, какие аргументы доступны и как их использовать.

    parser.add_argument("-i", type=str, required=True, help="Введите ваш запрос") #required=True делает аргумент обязательным, и если пользователь не предоставит его при запуске скрипта, будет выведено сообщение об ошибке.
    args = parser.parse_args()

    user_input = args.i

    print(f"User input: {user_input}")

    if validate_length(user_input):
        result_snippets = generate_snippets(user_input)
        result_keywords = generate_keywords(user_input)

        print(f"СНИППЕТЫ: {result_snippets}")
        print("\n")
        print(f"КЛЮЧЕВЫЕ СЛОВА: {result_keywords}")
    else:
        raise ValueError(
            f"Длина запроса должна быть не больше {MAX_INPUT_LENGTH} символов.\n"
            f"Длина вашего запроса: {len(user_input)} символов.\n"
            f"Сократите запрос на {len(user_input) - MAX_INPUT_LENGTH} символов и попробуйте снова."
        )

def validate_length(prompt: str) -> bool:
    return len(prompt) <= MAX_INPUT_LENGTH


def generate_snippets(promt: str):

    load_dotenv()
    GIGA_API = os.getenv("GIGA_API")


    giga = GigaChat(
        credentials=GIGA_API,
        verify_ssl_certs=False
    )

    end_promt = f"""Ты бренд-стратег и копирайтер. На входе только название проекта/бизнеса: "{promt}". Дай краткую инструкцию, как написать продающее описание этого проекта. Формат: ровно одна строка без переносов и лишних слов; только значения через запятую с пробелом в порядке: целевая аудитория, ключевая боль, уникальное обещание, доказательства/факты, call to action, тон (2-3 слова). Пиши по-русски, без клише, без подписей и лишних символов.""".strip()

    try:
        response = giga.chat(
            {
                # "model": "GigaChat-Pro",
                "messages": [
                    {
                        "role": "user",
                        "content": end_promt,
                    }
                ],
                "max_tokens": 100,
            }
        )

        model_response: str = response.choices[0].message.content
        model_response = model_response.strip().replace("\n", " ")

        last_char = model_response[-1]
        if last_char not in [",", ".", ";", "!", "?"]:
            model_response += "..."

        return model_response

    except Exception as e:
        print("Ошибка:", e)
        return []
    finally:
        giga.close()

def generate_keywords(promt: str) -> list[str]:

    load_dotenv()
    GIGA_API = os.getenv("GIGA_API")


    giga = GigaChat(
        credentials=GIGA_API,
        verify_ssl_certs=False
    )

    end_promt = f"""Ты бренд-стратег и копирайтер. На входе только название проекта/бизнеса: "{promt}". Сгенерируй 5 релевантных ключевых слов для этого проекта. Формат: ровно одна строка без переносов и лишних слов; только значения через запятую с пробелом. Пиши по-русски, без клише, без подписей и лишних символов.""".strip()

    try:
        response = giga.chat(
            {
                # "model": "GigaChat-Pro",
                "messages": [
                    {
                        "role": "user",
                        "content": end_promt,
                    }
                ],
                "max_tokens": 100,
            }
        )

        model_response: str = response.choices[0].message.content
        model_response = model_response.strip().replace("\n", " ")

        cleaned = re.sub(r"[.,;!?]$", "", model_response)
        keywords = [kw.strip() for kw in re.split(r",\s*", cleaned) if kw.strip()] # if kw.strip() проверяет что строка не пустая

        return keywords

    except Exception as e:
        print("Ошибка:", e)
    finally:
        giga.close()

if __name__ == "__main__":
    main()
