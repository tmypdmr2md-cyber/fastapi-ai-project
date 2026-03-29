from fastapi import FastAPI
from typing import Optional
from copykit import generate_snippets, generate_keywords

app = FastAPI()


@app.get("/generate_snippets")
async def generate_snippet_api(promt: Optional[str] = None):
    snippet = generate_snippets(promt)

    return {"snippet": snippet}

@app.get("/generate_keywords")
async def generate_keywords_api(promt: Optional[str] = None):
    keywords = generate_keywords(promt)
    return {"keywords": keywords}