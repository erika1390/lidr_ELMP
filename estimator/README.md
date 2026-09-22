# Estimador de software con FastAPI y CAG

API REST que recibe la transcripción de una reunión con un cliente y genera una estimación de desarrollo de software mediante un modelo de lenguaje de OpenAI.

El proyecto utiliza una arquitectura **CAG (Context-Augmented Generation)**: los ejemplos de estimaciones anteriores se almacenan como contexto estático y se incluyen directamente en el prompt enviado al modelo. En esta primera versión no se utilizan bases de datos, búsqueda semántica, RAG ni persistencia.

## Funcionalidades

- Recibe una transcripción mediante `POST /api/v1/estimate`.
- Valida la entrada con modelos de Pydantic.
- Incorpora ejemplos históricos en el prompt como referencias *few-shot*.
- Envía el prompt al modelo `gpt-4o-mini` de OpenAI.
- Devuelve la estimación, el modelo utilizado y el proveedor.
- Expone un endpoint de salud en `GET /health`.
- Genera documentación interactiva con Swagger.
- Incluye pruebas automáticas con pytest.

## Arquitectura CAG

El flujo de una petición es el siguiente:

```text
Transcripción del cliente
          │
          ▼
Endpoint de FastAPI
          │
          ▼
Servicio del LLM ──── Ejemplos estáticos
          │            de estimaciones
          ▼
Prompt: instrucciones + ejemplos + transcripción
          │
          ▼
      OpenAI API
          │
          ▼
Estimación en formato JSON
```

Los ejemplos estáticos actúan como conocimiento de referencia. Todos se envían al modelo en cada llamada, por lo que esta solución resulta adecuada mientras el volumen de contexto sea pequeño.

## Estructura del proyecto

```text
estimator/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── context/
│   │   ├── __init__.py
│   │   └── examples.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── estimations.py
│   └── services/
│       ├── __init__.py
│       └── llm_service.py
├── data/
│   └── transcription.txt
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

### Responsabilidades

- `app/main.py`: crea la aplicación, registra el router y define `/health`.
- `app/config.py`: carga las variables de entorno con Pydantic Settings.
- `app/context/examples.py`: contiene las estimaciones históricas utilizadas como contexto.
- `app/services/llm_service.py`: construye el prompt y realiza la llamada a OpenAI.
- `app/routers/estimations.py`: define los esquemas y el endpoint de estimación.
- `data/transcription.txt`: contiene una transcripción de ejemplo para probar el servicio.
- `tests/test_api.py`: verifica el endpoint de salud y la validación de la entrada.

## Requisitos

- Python 3.11 o posterior.
- [`uv`](https://docs.astral.sh/uv/) como gestor de paquetes.
- Una cuenta de OpenAI Platform con créditos disponibles.
- Una API key de OpenAI.

## Instalación

Clona el repositorio y entra en la carpeta del proyecto:

```powershell
git clone URL_DEL_REPOSITORIO
cd estimator
```

Instala las dependencias declaradas en `uv.lock`:

```powershell
uv sync --dev
```

## Variables de entorno

Copia el archivo de ejemplo:

```powershell
Copy-Item .env.example .env
```

Completa `.env` con una API key válida:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-4o-mini
```

El archivo `.env` está incluido en `.gitignore` y no debe publicarse ni incorporarse al repositorio. Puedes comprobarlo con:

```powershell
git check-ignore -v .env
```

## Ejecutar la aplicación

Desde la raíz del proyecto, inicia el servidor:

```powershell
uv run uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`.

Direcciones útiles:

- Estado del servicio: `http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`
- Esquema OpenAPI: `http://localhost:8000/openapi.json`

## Uso de la API

### Comprobar el estado

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/health"
```

Respuesta esperada:

```json
{
  "status": "ok"
}
```

### Generar una estimación

En PowerShell:

```powershell
$body = @{
    transcription = "En la reunión con marketing se solicitó una landing page con formulario de contacto, integración con HubSpot y un blog administrable. El diseño ya está preparado en Figma y debe entregarse en cuatro semanas."
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8000/api/v1/estimate" `
    -ContentType "application/json" `
    -Body $body
```

También se puede probar desde Swagger en `http://localhost:8000/docs` con este cuerpo:

```json
{
  "transcription": "En la reunión con marketing se solicitó una landing page con formulario de contacto, integración con HubSpot y un blog administrable. El diseño ya está preparado en Figma y debe entregarse en cuatro semanas."
}
```

La respuesta tiene esta estructura:

```json
{
  "estimation": "## Estimación: ...",
  "model": "gpt-4o-mini",
  "provider": "openai"
}
```

La transcripción debe contener al menos 20 caracteres. Una entrada más corta produce una respuesta HTTP `422`.

## Cómo se construye la estimación

El servicio realiza estos pasos:

1. Lee la configuración desde `.env`.
2. Obtiene las estimaciones históricas de `app/context/examples.py`.
3. Construye un mensaje de sistema con el rol del estimador, el formato esperado y los ejemplos.
4. Añade la nueva transcripción como mensaje del usuario.
5. Envía los mensajes a OpenAI con una temperatura de `0.2`.
6. Devuelve el contenido generado junto con el modelo y el proveedor.

La respuesta solicita un resumen, supuestos, tareas con horas, horas totales, equipo recomendado, duración, riesgos y asuntos pendientes.

## Pruebas automáticas

Ejecuta las pruebas desde la raíz del repositorio:

```powershell
uv run python -m pytest
```

Se utiliza `python -m pytest` para asegurar que la raíz del proyecto esté disponible en la ruta de importación y que `from app.main import app` se resuelva correctamente.

Las pruebas actuales verifican:

- Que `GET /health` responda con código `200` y `{"status": "ok"}`.
- Que una transcripción demasiado corta sea rechazada con código `422`.

Estas pruebas no realizan llamadas a OpenAI y, por tanto, no consumen créditos.

## Posibles errores

### `ModuleNotFoundError: No module named 'app'`

Ejecuta las pruebas de esta manera:

```powershell
uv run python -m pytest
```

Verifica también que estás ubicado en la carpeta que contiene `app`, `tests` y `pyproject.toml`.

### La API devuelve un error `502`

Comprueba que:

- `OPENAI_API_KEY` contiene una clave válida.
- La cuenta de OpenAI tiene créditos disponibles.
- El equipo tiene conexión a Internet.
- El modelo configurado en `OPENAI_MODEL` está disponible para la cuenta.

### La API devuelve un error `422`

Verifica que el JSON incluya el campo `transcription` y que el texto tenga al menos 20 caracteres.

## Seguridad

- No publiques `.env` ni claves de API.
- Usa `.env.example` únicamente para documentar los nombres de las variables.
- Revisa `git status` antes de crear cada commit.
- Si una clave se publica accidentalmente, revócala y genera una nueva desde OpenAI Platform.

## Estado del ejercicio

- [x] Aplicación FastAPI configurada.
- [x] Endpoint `GET /health`.
- [x] Endpoint `POST /api/v1/estimate`.
- [x] Configuración mediante variables de entorno.
- [x] Ejemplos estáticos inyectados con arquitectura CAG.
- [x] Integración con OpenAI.
- [x] Esquemas de entrada y salida con Pydantic.
- [x] Documentación Swagger.
- [x] Transcripción de ejemplo.
- [x] Pruebas automáticas.

## Licencia

Proyecto educativo desarrollado como parte del programa AI Engineering 2026.
