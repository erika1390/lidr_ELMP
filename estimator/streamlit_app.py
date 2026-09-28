from time import perf_counter
from typing import Iterator

import streamlit as st

from app.config import get_settings
from app.services.llm_service import (
    build_examples_context,
    build_system_prompt,
    create_estimation_stream,
)


st.set_page_config(
    page_title="Estimador de Software",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Estimador de proyectos de software")
st.caption(
    "Pega la transcripción de una reunión para generar una estimación "
    "de esfuerzo, equipo, duración y riesgos."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_metrics" not in st.session_state:
    st.session_state.last_metrics = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

transcription = st.chat_input("Pega aquí la transcripción de la reunión...")

if transcription:
    transcription = transcription.strip()

    if len(transcription) < 20:
        st.warning("La transcripción debe contener al menos 20 caracteres.")
        st.stop()

    st.session_state.messages.append(
        {"role": "user", "content": transcription}
    )

    with st.chat_message("user"):
        st.markdown(transcription)

    request_metrics = {
        "input_tokens": None,
        "output_tokens": None,
    }

    def estimation_tokens() -> Iterator[str]:
        stream = create_estimation_stream(transcription)

        for chunk in stream:
            if chunk.usage is not None:
                request_metrics["input_tokens"] = chunk.usage.prompt_tokens
                request_metrics["output_tokens"] = (
                    chunk.usage.completion_tokens
                )

            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content
            if content:
                yield content

    settings = get_settings()
    start_time = perf_counter()

    try:
        with st.chat_message("assistant"):
            estimation = st.write_stream(estimation_tokens())

        elapsed_time = perf_counter() - start_time

        if not estimation:
            raise RuntimeError("El modelo no devolvió contenido.")

        st.session_state.messages.append(
            {"role": "assistant", "content": estimation}
        )
        st.session_state.last_metrics = {
            "model": settings.openai_model,
            "provider": settings.llm_provider,
            "input_tokens": request_metrics["input_tokens"],
            "output_tokens": request_metrics["output_tokens"],
            "elapsed_seconds": elapsed_time,
        }

    except Exception as error:
        st.error(f"No fue posible generar la estimación. Detalle: {error}")

with st.sidebar:
    st.header("Contexto CAG")

    if st.button("Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_metrics = None
        st.rerun()

    with st.expander("System prompt activo"):
        st.code(build_system_prompt(), language="text")

    with st.expander("Ejemplos estáticos"):
        st.markdown(build_examples_context())

    st.divider()
    st.subheader("Última llamada")

    metrics = st.session_state.last_metrics
    if metrics is None:
        st.info("Todavía no se ha realizado ninguna llamada.")
    else:
        st.write(f"**Proveedor:** {metrics['provider']}")
        st.write(f"**Modelo:** {metrics['model']}")
        st.metric(
            "Tokens de entrada",
            metrics["input_tokens"]
            if metrics["input_tokens"] is not None
            else "No disponible",
        )
        st.metric(
            "Tokens de salida",
            metrics["output_tokens"]
            if metrics["output_tokens"] is not None
            else "No disponible",
        )
        st.metric(
            "Tiempo de respuesta",
            f"{metrics['elapsed_seconds']:.2f} s",
        )
