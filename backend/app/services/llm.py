import json
import re
from collections.abc import Iterator
from typing import ClassVar, Protocol

from openai import OpenAI

from app.config import Settings
from app.models import Category, Source


class LLMClient(Protocol):
    def categorize(self, type: str, description: str, merchant: str, amount: float) -> dict: ...

    def narrate_insights(self, metrics: dict) -> str: ...

    def narrate_cashflow(self, radar: dict) -> str: ...

    def answer_question(self, question: str, bundle: dict) -> str: ...

    def stream_answer_question(self, question: str, bundle: dict) -> Iterator[str]: ...


def _extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"no JSON block in response: {text[:200]}")
    return json.loads(match.group(0))


def _validate_categorization(type: str, result: object) -> dict:
    if not isinstance(result, dict):
        raise ValueError("categorization response must be a JSON object")

    field = "source" if type == "income" else "category"
    choices = set(Source) if type == "income" else set(Category)
    label = result.get(field)
    confidence = result.get("confidence")
    if label not in choices:
        raise ValueError(f"invalid {field} in categorization response")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ValueError("categorization confidence must be between 0 and 1")
    return {field: label, "confidence": float(confidence)}


class OpenAIClient:
    def __init__(self, settings: Settings):
        self.client = OpenAI(
            api_key=settings.llm_api_key, base_url=settings.llm_base_url, timeout=60.0, max_retries=0
        )
        self.model = settings.llm_model

    def _complete(self, system: str, user: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=500,
        )
        return response.choices[0].message.content or ""

    def categorize(self, type: str, description: str, merchant: str, amount: float) -> dict:
        if type == "income":
            choices = "commission, etsy, patreon, other_income"
            field = "source"
        else:
            choices = "supplies, platform_fees, subscriptions, equipment, other_expense"
            field = "category"
        system = "You categorize financial records for a freelance artist. Respond with ONLY a JSON object."
        user = (
            f'Transaction: "{description}" merchant="{merchant}" amount=${amount:.2f}\n'
            f"Pick exactly one of: {choices}.\n"
            f'Respond: {{"{field}": "<value>", "confidence": <0.0-1.0>}}'
        )
        return _extract_json(self._complete(system, user))

    def narrate_insights(self, metrics: dict) -> str:
        system = (
            "You are a friendly financial coach for a freelance artist. "
            "Write 2-4 numbered insights as short lines, citing exact figures from the data. No markdown."
        )
        return self._complete(system, f"Here are the artist's metrics as JSON:\n{json.dumps(metrics)}")

    def narrate_cashflow(self, radar: dict) -> str:
        system = (
            "You are a financial coach for a freelance artist. "
            "Interpret this cash-flow radar in 2-3 concise sentences with a plain recommendation. No markdown."
        )
        return self._complete(system, f"Cash-flow radar as JSON:\n{json.dumps(radar)}")

    def _answer_prompt(self, question: str, bundle: dict) -> tuple[str, str]:
        system = (
            "Answer the user's question about their personal finances using ONLY the provided figures. "
            "Be concise, cite exact numbers, and never invent data. If the data can't answer it, say so."
        )
        return system, f"User question: {question}\n\nCurrent data (JSON):\n{json.dumps(bundle)}"

    def answer_question(self, question: str, bundle: dict) -> str:
        system, user = self._answer_prompt(question, bundle)
        return self._complete(system, user)

    def stream_answer_question(self, question: str, bundle: dict) -> Iterator[str]:
        system, user = self._answer_prompt(question, bundle)
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=500,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta


class HeuristicFallback:
    """Offline keyword-driven fallback so the app works with no API key."""

    SOURCE_KEYWORDS: ClassVar[dict] = {
        Source.COMMISSION.value: [
            "commission",
            "commish",
            "commision",
            "client",
            "artwork for",
            "portrait",
            "sketch for",
            "chibi",
        ],
        Source.ETSY.value: ["etsy", "sticker", "print", "shop sale", "digital download"],
        Source.PATREON.value: ["patreon", "ko-fi", "kofi", "subscribe", "subscription income", "donation"],
    }
    CATEGORY_KEYWORDS: ClassVar[dict] = {
        Category.SUPPLIES.value: [
            "paint",
            "canvas",
            "paper",
            "brush",
            "ink",
            "tablet pen",
            "supply",
            "art supply",
            "marker",
        ],
        Category.PLATFORM_FEES.value: ["fee", "etsy fee", "paypal fee", "commission", "processing", "ad fee"],
        Category.SUBSCRIPTIONS.value: [
            "adobe",
            "procreate",
            "clip studio",
            "photoshop",
            "spotify",
            "dropbox",
            "youtube premium",
            "portfolioplus",
        ],
        Category.EQUIPMENT.value: [
            "ipad",
            "tablet",
            "camera",
            "monitor",
            "laptop",
            "computer",
            "wacom",
            "scanner",
            "printer",
        ],
    }

    def _match(self, text: str, table: dict) -> tuple[str, float] | None:
        lowered = text.lower()
        best: tuple[str, float] | None = None
        for label, keywords in table.items():
            for keyword in keywords:
                if keyword in lowered:
                    confidence = 0.6 if best is None else max(best[1], 0.6)
                    best = (label, confidence)
        return best

    def categorize(self, type: str, description: str, merchant: str, amount: float) -> dict:
        text = f"{merchant or ''} {description}"
        if type == "income":
            label, confidence = self._match(text, self.SOURCE_KEYWORDS) or (Source.OTHER_INCOME.value, 0.3)
            return {"source": label, "confidence": confidence}
        label, confidence = self._match(text, self.CATEGORY_KEYWORDS) or (Category.OTHER_EXPENSE.value, 0.3)
        return {"category": label, "confidence": confidence}

    def narrate_insights(self, metrics: dict) -> str:
        hourly = metrics.get("hourly_rate")
        lines = []
        if hourly is not None:
            lines.append(f"1. Effective rate is ${hourly}/hr across logged commissions.")
        top = metrics.get("top_merchants", [])
        if top:
            lines.append(f"2. Biggest expense line is {top[0]['merchant']} at ${top[0]['total']}.")
        fees = metrics.get("total_fees", 0)
        lines.append(f"3. Platform fees totaled ${fees}.")
        radar = metrics.get("cashflow", {})
        lines.append(f"4. Cash-flow level: {radar.get('level', 'unknown')} (coverage {radar.get('coverage_pct')}%).")
        return "\n".join(lines)

    def narrate_cashflow(self, radar: dict) -> str:
        if radar.get("level") == "healthy":
            return (
                f"Coverage is {radar['coverage_pct']}% with a projected balance of ${radar['projected_balance_30d']} "
                "in 30 days. Keep your current pace."
            )
        if radar.get("level") == "low":
            return (
                f"Coverage is just {radar['coverage_pct']}%. Committed income of ${radar['committed_next_30d']} "
                f"and a balance of ${radar['balance']} won't cover ${radar['burn_next_30d']} of spend "
                f"(projected ${radar['projected_balance_30d']}). Line up more commissions or trim spending."
            )
        return (
            f"Coverage is {radar.get('coverage_pct', 'n/a')}%. "
            f"Your projected 30-day balance is ${radar.get('projected_balance_30d')}."
        )

    def answer_question(self, question: str, bundle: dict) -> str:
        q = question.lower()
        if "etsy" in q:
            return f"Etsy produced ${bundle['per_source_net'].get('etsy', 0):.2f} in net income all-time."
        if "patreon" in q or "ko-fi" in q:
            return f"Patreon/Ko-fi produced ${bundle['per_source_net'].get('patreon', 0):.2f} in net income all-time."
        if "balance" in q:
            return f"Your all-time net balance is ${bundle['balance']:.2f}."
        if "hour" in q or "rate" in q:
            rate = bundle.get("hourly_rate")
            return f"Your effective rate is ${rate:.2f}/hr" if rate else "No hours logged yet."
        if "fee" in q:
            return f"You've paid ${bundle['total_fees']:.2f} in platform fees all-time."
        if "spend" in q or "expense" in q:
            if not bundle.get("top_merchants"):
                return "No expense data yet."
            top = bundle["top_merchants"][0]
            return f"Your biggest merchant is {top['merchant']} at ${top['total']:.2f}."
        return "I don't have a template for that offline. Configure an LLM key for full natural-language answers."

    def stream_answer_question(self, question: str, bundle: dict) -> Iterator[str]:
        text = self.answer_question(question, bundle)
        words = text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")


def get_llm() -> "FallbackClient":
    from app.config import get_settings

    settings = get_settings()
    primary: LLMClient
    if settings.llm_api_key:
        primary = OpenAIClient(settings)
    else:
        primary = HeuristicFallback()
    return FallbackClient(primary)


class FallbackClient:
    """Keeps the app alive: if the LLM provider errors, degrade to heuristics."""

    def __init__(self, primary: LLMClient):
        self.primary = primary
        self.fallback = HeuristicFallback()

    def categorize(self, type: str, description: str, merchant: str, amount: float) -> dict:
        try:
            result = self.primary.categorize(type, description, merchant, amount)
            return _validate_categorization(type, result)
        except Exception:
            result = self.fallback.categorize(type, description, merchant, amount)
            return _validate_categorization(type, result)

    def narrate_insights(self, metrics: dict) -> str:
        try:
            return self.primary.narrate_insights(metrics)
        except Exception:
            return self.fallback.narrate_insights(metrics)

    def narrate_cashflow(self, radar: dict) -> str:
        try:
            return self.primary.narrate_cashflow(radar)
        except Exception:
            return self.fallback.narrate_cashflow(radar)

    def answer_question(self, question: str, bundle: dict) -> str:
        try:
            return self.primary.answer_question(question, bundle)
        except Exception:
            return self.fallback.answer_question(question, bundle)

    def stream_answer_question(self, question: str, bundle: dict) -> Iterator[str]:
        try:
            stream = self.primary.stream_answer_question(question, bundle)
            first = next(stream, None)
        except Exception:
            yield from self.fallback.stream_answer_question(question, bundle)
            return
        if first is None:
            yield from self.fallback.stream_answer_question(question, bundle)
            return
        yield first
        try:
            yield from stream
        except Exception:
            return
