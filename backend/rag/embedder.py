from typing import Optional
from openai import AsyncOpenAI

_client: Optional[AsyncOpenAI] = None

EMBEDDING_MODEL = "text-embedding-3-small"


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI()
    return _client


async def embed_texts(texts: list[str]) -> list[list[float]]:
    client = get_client()
    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


async def embed_query(text: str) -> list[float]:
    embeddings = await embed_texts([text])
    return embeddings[0]
