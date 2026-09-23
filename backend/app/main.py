from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, candidates, job_descriptions

app = FastAPI(title="HireSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(job_descriptions.router)
app.include_router(candidates.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
