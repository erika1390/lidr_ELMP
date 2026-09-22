from fastapi import FastAPI

from app.routers.estimations import router as estimations_router


app = FastAPI(
    title="Estimador de Software CAG",
    description=(
        "API que genera estimaciones de proyectos de software mediante "
        "un LLM y ejemplos estáticos incluidos en el prompt."
    ),
    version="1.0.0",
)

app.include_router(estimations_router, prefix="/api/v1")


@app.get("/health", tags=["Salud"])
def health() -> dict[str, str]:
    return {"status": "ok"}