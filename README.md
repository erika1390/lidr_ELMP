# AI Engineering — Sesión 01: Primera llamada a un LLM vía API

Ejercicio del programa **AI Engineering de LIDR** para conectar Python con la API de OpenAI, obtener respuestas de un modelo y explorar cómo las instrucciones modifican su comportamiento.

## Contenido

El archivo [session_01_ejercicios.ipynb](session_01_ejercicios.ipynb) está preparado para Google Colab y utiliza el SDK de OpenAI, la API Responses y el modelo `gpt-4o-mini`.

| Nivel | Objetivo | Implementación en el notebook |
| --- | --- | --- |
| 1 — Llamada básica | Enviar un mensaje y mostrar la respuesta. | Pregunta `What a REST API is.` y muestra `response.output_text`. |
| 2 — System prompt | Dar un rol al modelo y comparar al menos dos instrucciones. | Usa `instructions` para definir un experto en estimación de proyectos con tono directo y técnico. La comparación escrita está pendiente. |
| 3 — Metadatos y coste | Consultar el consumo y estimar el coste de una llamada. | Muestra modelo, estado y tokens de entrada, salida y totales; calcula un coste estimado. |

Los niveles 1 y 2 son obligatorios; el nivel 3 es opcional.

## Requisitos

- Acceso a Google Colab con un entorno de Python 3.
- Una clave de API de OpenAI con acceso al modelo utilizado y disponibilidad para realizar llamadas.
- Conexión a Internet para instalar el SDK y consultar la API.

El notebook instala la dependencia `openai` en su primera celda de código. La salida guardada registra la versión `2.54.0`, pero la instalación no fija una versión concreta.

## Ejecución en Google Colab

1. Sube `session_01_ejercicios.ipynb` a Google Colab y ábrelo.
2. En el panel **Secretos**, crea un secreto llamado `OPENAI_API_KEY` y habilita su acceso para este notebook.
3. Ejecuta las celdas en orden, comenzando por la instalación y la configuración.
4. Revisa las respuestas de cada nivel y completa la comparación de instrucciones del nivel 2.

El notebook configura el cliente así:

```python
import os
from google.colab import userdata
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
openai_client = OpenAI()
```

Las llamadas utilizan la clave cargada desde Colab Secrets. No es necesario escribirla en el código.

## Ejemplo de llamada

```python
response = openai_client.responses.create(
    model="gpt-4o-mini",
    input="What a REST API is."
)

print(response.output_text)
```

En el nivel 2 se añade el parámetro `instructions` para orientar el rol y el estilo de la respuesta. Para completar el ejercicio, prueba un segundo rol claramente diferente, por ejemplo un docente que explica conceptos a principiantes, manteniendo la misma pregunta. Anota los cambios de tono, detalle y estructura, y cuál sería más útil para un producto real.

## Metadatos y estimación de coste

El nivel 3 consulta `response.model`, `response.status` y `response.usage`. El cálculo implementado es:

```text
coste = (tokens_entrada / 1_000_000 × tarifa_entrada)
      + (tokens_salida / 1_000_000 × tarifa_salida)
```

El notebook contiene tarifas de ejemplo de **0,15 USD por millón de tokens de entrada** y **0,60 USD por millón de tokens de salida**. Son valores incorporados al ejercicio, no tarifas verificadas en esta revisión; comprueba su vigencia antes de reutilizarlos para presupuestar llamadas.

La salida guardada del nivel 3 muestra 24 tokens de entrada, 437 de salida y 461 en total. Con los valores del código, el coste estimado es de `0,0002658 USD`, mostrado como `0,000266 USD`. Corresponde únicamente a esa llamada, no a toda la sesión. Las nuevas ejecuciones pueden producir respuestas y consumos diferentes.

## Estado de la revisión

- El archivo se pudo leer como JSON y contiene las instrucciones, el código y salidas guardadas de los tres niveles.
- **Actividad pendiente:** el nivel 2 contiene una sola llamada. El nivel 3 utiliza otra instrucción similar, pero no se documenta la comparación requerida de tono, detalle, estructura y utilidad.
- El notebook depende de `google.colab.userdata` y la instalación utiliza comandos de shell como `grep` y `tail`; para ejecutarlo en Jupyter local, especialmente en Windows, es necesario adaptar esas celdas.
- Esta revisión fue estática: no se ejecutó el notebook ni se realizaron nuevas llamadas a la API. Las salidas guardadas no garantizan que el código actual funcione desde un entorno limpio.

## Aprendizajes

- Configurar credenciales mediante Colab Secrets.
- Crear un cliente y realizar una llamada a un LLM desde Python.
- Orientar una respuesta mediante instrucciones de rol y estilo.
- Consultar metadatos y relacionar el consumo de tokens con un coste estimado.
