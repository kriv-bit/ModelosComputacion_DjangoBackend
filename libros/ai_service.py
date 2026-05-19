"""
Servicio de IA usando DeepSeek API (compatible con SDK de OpenAI).
Modelo: deepseek-v4-flash con thinking habilitado y streaming.
"""

import os
from openai import OpenAI


def get_deepseek_client() -> OpenAI:
    """Crea y retorna un cliente OpenAI configurado para DeepSeek."""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )


def build_book_chat_messages(
    book_title: str,
    book_author: str,
    selected_text: str,
    context: str,
    question: str,
    history: list | None = None,
) -> list[dict]:
    """
    Construye la lista de mensajes para la API de chat.

    Args:
        book_title: Título del libro.
        book_author: Autor del libro.
        selected_text: Fragmento seleccionado por el usuario en el PDF.
        context: Descripción/contexto general del libro.
        question: Pregunta del usuario.
        history: Historial previo de mensajes (lista de dicts role/content).

    Returns:
        Lista de mensajes para enviar a la API.
    """
    system_prompt = (
        f"Eres un asistente literario experto y amigable. "
        f"Estás ayudando al usuario a comprender el libro «{book_title}» de {book_author}. "
        f"Contexto del libro: {context or 'No disponible'}. "
        "Responde siempre en el idioma del usuario. "
        "Sé claro, pedagógico y usa el fragmento seleccionado para anclar tu análisis."
    )

    messages: list[dict] = [{"role": "system", "content": system_prompt}]

    # Añadir historial previo si existe
    if history:
        messages.extend(history)

    # Mensaje del usuario con el texto seleccionado y la pregunta
    user_content = question
    if selected_text and selected_text.strip():
        user_content = (
            f"**Fragmento seleccionado del libro:**\n"
            f"«{selected_text.strip()}»\n\n"
            f"**Mi pregunta:**\n{question}"
        )

    messages.append({"role": "user", "content": user_content})
    return messages


def stream_chat_response(messages: list[dict]):
    """
    Genera un stream de tokens de respuesta de DeepSeek.

    Yields:
        str: Chunks de texto de la respuesta.
    """
    client = get_deepseek_client()

    stream = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        stream=True,
        extra_body={
            "thinking": {"type": "enabled"},
            "reasoning_effort": "high",
        },
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
