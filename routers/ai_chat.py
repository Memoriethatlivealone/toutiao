"""AI 问答接口：把前端的对话转交给 LangChain agent，并以 SSE 流式返回。"""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from services.ai_chat import stream_chat

router = APIRouter(prefix="/api/ai", tags=["ai"])


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/chat")
async def chat(payload: ChatRequest):
    messages = [message.model_dump() for message in payload.messages]

    async def event_stream():
        try:
            async for text in stream_chat(messages):
                # 沿用 OpenAI 的流式格式，前端解析逻辑可以复用
                yield _sse({"choices": [{"delta": {"content": text}}]})
        except Exception as exc:  # 把错误也通过流返回，前端能显示出来
            yield _sse({"error": {"message": str(exc)[:500]}})
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )