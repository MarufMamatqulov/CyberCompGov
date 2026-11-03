from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import analytics, assessment, auth, catalog, officers, reports


@asynccontextmanager
async def lifespan(_: FastAPI):
    if get_settings().seed_on_startup:
        from app.seed.seed import seed
        seed()
    yield


app = FastAPI(title="CyberComp-Gov API", version="1.0.0", lifespan=lifespan,
              docs_url="/api/docs", openapi_url="/api/openapi.json")

_origins = [o.strip() for o in get_settings().cors_origins.split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_methods=["*"], allow_headers=["*"])

for r in (auth, officers, assessment, analytics, catalog, reports):
    app.include_router(r.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
