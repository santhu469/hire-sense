from fastapi import APIRouter, FastAPI
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

# Nested under /api so the frontend and backend can share one ALB origin in
# production (path-based routing: /api/* -> backend, everything else ->
# frontend) with no CORS needed and no collision with frontend page routes
# of the same name (e.g. /job-descriptions/[jdId]). /health stays
# unprefixed since it's hit directly by the ALB target group health check,
# not through the public listener's path rules.
api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(job_descriptions.router)
api_router.include_router(candidates.router)
app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
