import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.config import get_settings
from app.database import get_session
from app.dependencies import limiter, require_api_key
from app.schemas import (
    CashflowInsightsResponse,
    CashflowRadarRead,
    ChatRequest,
    ChatResponse,
    DashboardSummary,
    InsightsResponse,
)
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

_settings = get_settings()
limit_per_min = _settings.chat_rate_limit_per_minute
_chat_limit = f"{limit_per_min}/minute" if limit_per_min > 0 else "1000/second"


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(session: Session = Depends(get_session)):
    return {
        "balance": balance(session),
        "per_source_net": per_source_net(session),
        "monthly_trend": monthly_trend(session),
        "top_merchants": top_merchants(session),
        "total_fees": total_fees(session),
        "hourly_rate": hourly_rate(session),
    }


@router.post("/dashboard/insights", response_model=InsightsResponse)
def dashboard_insights(session: Session = Depends(get_session), llm: LLMClient = Depends(get_llm)):
    return {"insights": llm.narrate_insights(context_bundle(session))}


@router.get("/cashflow/radar", response_model=CashflowRadarRead)
def cashflow_radar_endpoint(session: Session = Depends(get_session)):
    return cashflow_radar(session)


@router.post("/cashflow/radar/insights", response_model=CashflowInsightsResponse)
def cashflow_insights(session: Session = Depends(get_session), llm: LLMClient = Depends(get_llm)):
    radar = cashflow_radar(session)
    return {"radar": radar, "narrative": llm.narrate_cashflow(radar)}


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(_chat_limit)
def chat(
    request: Request,
    chat_req: ChatRequest,
    session: Session = Depends(get_session),
    llm: LLMClient = Depends(get_llm),
    _auth=Depends(require_api_key),
):
    # Enforce max length beyond Pydantic: check stripped length and settings
    settings = get_settings()
    max_len = settings.chat_max_length
    if len(chat_req.question.strip()) > max_len:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Question too long")
    return {"answer": llm.answer_question(chat_req.question, context_bundle(session))}


@router.post("/chat/stream")
@limiter.limit(_chat_limit)
def chat_stream(
    request: Request,
    chat_req: ChatRequest,
    session: Session = Depends(get_session),
    llm: LLMClient = Depends(get_llm),
    _auth=Depends(require_api_key),
):
    settings = get_settings()
    max_len = settings.chat_max_length
    if len(chat_req.question.strip()) > max_len:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Question too long")
    bundle = context_bundle(session)

    def event_stream():
        for chunk in llm.stream_answer_question(chat_req.question, bundle):
            yield f"data: {json.dumps({'delta': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
