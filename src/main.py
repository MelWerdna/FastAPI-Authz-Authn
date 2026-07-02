from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from contextlib import asynccontextmanager
from src.database import init_db
from src.config import settings
from src.users.router import router as users_router
from src.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.project_name,
    description="FastAPI AuthN and AuthZ service",
    version="1.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


app.include_router(users_router)
app.include_router(auth_router)
