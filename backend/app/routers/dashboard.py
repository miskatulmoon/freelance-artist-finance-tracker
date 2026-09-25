import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.database import get_session
from app.schemas import ChatRequest
from app.services.llm import LLMClient, get_llm
from app.services.stats import (
    balance,
    cashflow_radar,
    context_bundle,
    hourly_rate,
    monthly_trend,
    per_source_net,
    top_merchants,
    total_fees,
)

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/summary")
def dashboard_summary(session: Session = Depends(get_session)):
    return {
        "balance": balance(session),
        "per_source_net": per_source_net(session),
        "monthly_trend": monthly_trend(session),
        "top_merchants": top_merchants(session),
        "total_fees": total_fees(session),
        "hourly_rate": hourly_rate(session),
    }


@router.post("/dashboard/insights")
def dashboard_insights(session: Session = Depends(get_session), llm: LLMClient = Depends(get_llm)):
    return {"insights": llm.narrate_insights(context_bundle(session))}


@router.get("/cashflow/radar")
def cashflow_radar_endpoint(session: Session = Depends(get_session)):
    return cashflow_radar(session)


@router.post("/cashflow/radar/insights")
def cashflow_insights(session: Session = Depends(get_session), llm: LLMClient = Depends(get_llm)):
    radar = cashflow_radar(session)
    return {"radar": radar, "narrative": llm.narrate_cashflow(radar)}


@router.post("/chat")
def chat(request: ChatRequest, session: Session = Depends(get_session), llm: LLMClient = Depends(get_llm)):
    return {"answer": llm.answer_question(request.question, context_bundle(session))}


@router.post("/chat/stream")
def chat_stream(request: ChatRequest, session: Session = Depends(get_session), llm: LLMClient = Depends(get_llm)):
    bundle = context_bundle(session)

    def event_stream():
        for chunk in llm.stream_answer_question(request.question, bundle):
            yield f"data: {json.dumps({'delta': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
