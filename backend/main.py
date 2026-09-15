from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from routes import users, search, menu
from routes import recipes, shopping, pantry, guides

app = FastAPI(
    title="Неделька — планировщик меню",
    description=(
        "API меню на неделю, рецептов и списка покупок.\n\n"
        "Приёмы пищи всегда: `breakfast`, `lunch`, `dinner`, `snack1`, `snack2`.\n"
        "В Swagger нажмите **Authorize** и вставьте токен из `/api/users/login`."
    ),
    version="2.1.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(search.router)
app.include_router(menu.router)
app.include_router(recipes.router)
app.include_router(shopping.router)
app.include_router(pantry.router)
app.include_router(guides.router)


@app.get("/")
def read_root():
    return {
        "message": "Неделька API",
        "docs": "/docs",
        "meal_slots": ["breakfast", "lunch", "dinner", "snack1", "snack2"],
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
