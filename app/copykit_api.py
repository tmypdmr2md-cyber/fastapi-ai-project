from fastapi import FastAPI
from copykit import generate_snippets, generate_keywords

app = FastAPI()

# uvicorn copykit_api:app --reload
# http://127.0.0.1:8000/docs

@app.get("/generate_snippets")
async def generate_snippet_api(promt: str = None):
    snippet = await generate_snippets(promt)

    return {"snippet": snippet,
            "keywords": [],
            "promt": promt}

@app.get("/generate_keywords")
async def generate_keywords_api(promt: str = None):
    keywords = await generate_keywords(promt)

    return {"snippet": None,
            "keywords": keywords,
            "promt": promt}

@app.get("/generate_all")
async def generate_all_api(promt: str = None):
    snippets = await generate_snippets(promt)
    keywords = await generate_keywords(promt)

    return {"snippets": snippets,
            "keywords": keywords,
            "promt": promt}
