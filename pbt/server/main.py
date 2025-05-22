from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import promptgen, testgen, seo, auth, claude_score, analytics, stripe, stars, export, promptpacks

app = FastAPI(
    title="Prompt Build Tool API",
    description="""Use this API to generate, evaluate, and deploy modular LLM prompt packs.

Try:
- `POST /api/promptgen` to generate a prompt YAML file.
- `POST /api/evals/judge` to get Claude-based model evaluation.
- `GET /api/promptpacks/list` to view deployed prompt modules.
    """,
    version="1.0.0",
    contact={
        "name": "Prompt Build Team",
        "url": "https://github.com/your-org/pbt",
        "email": "founder@yourdomain.com",
    },
    openapi_tags=[
        {"name": "Prompt Generator", "description": "Create structured prompt templates"},
        {"name": "Evaluator", "description": "LLM scoring, similarity, pass/fail"},
        {"name": "Prompt Packs", "description": "View, publish, deploy packs"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(promptgen.router, prefix="/api/promptgen", tags=["Prompt Generator"])
app.include_router(testgen.router, prefix="/api/testgen", tags=["Prompt Generator"])
app.include_router(seo.router, prefix="/api/seo", tags=["Prompt Generator"])
app.include_router(auth.router, prefix="/api/auth")
app.include_router(claude_score.router, prefix="/api/evals", tags=["Evaluator"])
app.include_router(analytics.router, prefix="/api/stats", tags=["Usage"])
app.include_router(stripe.router, prefix="/api/payment")
app.include_router(stars.router, prefix="/api/star")
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(promptpacks.router, prefix="/api/promptpacks", tags=["Prompt Packs"])

@app.get("/")
def read_root():
    return {"message": "PBT API is running"}
