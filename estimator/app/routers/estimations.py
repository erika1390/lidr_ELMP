from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.llm_service import generate_estimation


router = APIRouter(tags=["Estimaciones"])


class EstimationRequest(BaseModel):
    transcription: str = Field(
        min_length=20,
        description="Texto de la transcripción de la reunión",
    )


class EstimationResponse(BaseModel):
    estimation: str
    model: str
    provider: str


@router.post("/estimate", response_model=EstimationResponse)
def estimate(request: EstimationRequest) -> EstimationResponse:
    try:
        result = generate_estimation(request.transcription)
        return EstimationResponse(**result)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"No fue posible generar la estimación: {error}",
        ) from error