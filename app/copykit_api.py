import os

from fastapi import FastAPI, HTTPException
from copykit import generate_snippets, generate_keywords, validate_input_length
from dotenv import load_dotenv

app = FastAPI()

MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", 100))

# uvicorn copykit_api:app --reload
# http://127.0.0.1:8000/docs

@app.get("/generate_snippets")
async def generate_snippet_api(promt: str = None):
    if not validate_input_length(promt):
        raise HTTPException(
            status_code=400,
            detail=f"Длина запроса должна быть не больше {MAX_INPUT_LENGTH} символов и не меньше 3.\n"
                   f"Длина вашего запроса: {len(promt)} символов.\n"
        )
    snippet =  generate_snippets(promt)

    return {"snippet": snippet,
            "keywords": [],
            "promt": promt}

@app.get("/generate_keywords")
async def generate_keywords_api(promt: str = None):
    if not validate_input_length(promt):
        raise HTTPException(
            status_code=400,
            detail=f"Длина запроса должна быть не больше {MAX_INPUT_LENGTH} символов и не меньше 3.\n"
                   f"Длина вашего запроса: {len(promt)} символов.\n"
        )
    
    keywords =  generate_keywords(promt)

    return {"snippet": None,
            "keywords": keywords,
            "promt": promt}

@app.get("/generate_all")
async def generate_all_api(promt: str = None):
    if not validate_input_length(promt):
        raise HTTPException(
            status_code=400,
            detail=f"Длина запроса должна быть не больше {MAX_INPUT_LENGTH} символов и не меньше 3.\n"
                   f"Длина вашего запроса: {len(promt)} символов.\n"
        )
    
    snippets =  generate_snippets(promt)
    keywords =  generate_keywords(promt)

    return {"snippets": snippets,
            "keywords": keywords,
            "promt": promt}


