from typing import Any

from openai import OpenAI

from app.config import get_settings
from app.context.examples import ESTIMATION_EXAMPLES


def build_examples_context() -> str:
    sections = []

    for index, example in enumerate(ESTIMATION_EXAMPLES, start=1):
        sections.append(
            f"""
EJEMPLO {index}

Resumen de la reunión:
{example["meeting_summary"]}

Estimación:
{example["estimation"]}
"""
        )

    return "\n".join(sections)


def build_system_prompt() -> str:
    examples_context = build_examples_context()

    return f"""
Eres un estimador de proyectos de software con experiencia en análisis,
arquitectura, desarrollo, pruebas y despliegue.

Genera una estimación a partir de la transcripción proporcionada.

La respuesta debe incluir:
- Resumen del proyecto.
- Supuestos.
- Desglose de tareas con horas.
- Total de horas.
- Equipo recomendado.
- Duración estimada.
- Riesgos y aspectos pendientes por aclarar.

Usa los siguientes ejemplos históricos como referencia de formato y nivel
de detalle:

{examples_context}

No copies los ejemplos literalmente. Adapta la estimación a los requisitos
de la nueva transcripción.
""".strip()


def build_messages(transcription: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": build_system_prompt(),
        },
        {
            "role": "user",
            "content": (
                "Genera una estimación para esta transcripción:\n\n"
                f"{transcription}"
            ),
        },
    ]


def create_estimation_stream(transcription: str) -> Any:
    """
    Inicia una respuesta de OpenAI en streaming.

    El consumidor debe recorrer los chunks devueltos.
    """
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    return client.chat.completions.create(
        model=settings.openai_model,
        messages=build_messages(transcription),
        temperature=0.2,
        stream=True,
        stream_options={"include_usage": True},
    )


def generate_estimation(transcription: str) -> dict[str, str]:
    """
    Generación no streaming utilizada actualmente por FastAPI.
    """
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=build_messages(transcription),
        temperature=0.2,
    )

    estimation = response.choices[0].message.content

    if not estimation:
        raise RuntimeError("El modelo no devolvió una estimación.")

    return {
        "estimation": estimation,
        "model": settings.openai_model,
        "provider": settings.llm_provider,
    }