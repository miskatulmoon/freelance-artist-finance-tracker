from app.services.llm import FallbackClient


class InvalidLLM:
    def categorize(self, type, description, merchant, amount):
        return {"source": "not-a-source", "confidence": 2}


def test_invalid_llm_categorization_falls_back(caplog):
    result = FallbackClient(InvalidLLM()).categorize("income", "etsy print", "", 15)

    assert result == {"source": "etsy", "confidence": 0.6}
    fallback_log = next(record for record in caplog.records if record.event == "llm_fallback")
    assert fallback_log.operation == "categorize"
    assert fallback_log.error_type == "ValueError"


class BrokenLLM:
    def narrate_insights(self, metrics):
        raise RuntimeError("provider down")

    def narrate_cashflow(self, radar):
        raise RuntimeError("provider down")

    def answer_question(self, question, bundle):
        raise RuntimeError("provider down")


def assert_fallback_logged(caplog, operation):
    fallback_log = next(record for record in caplog.records if record.event == "llm_fallback")
    assert fallback_log.operation == operation
    assert fallback_log.error_type == "RuntimeError"


def test_narrate_insights_fallback_logs_event(caplog):
    result = FallbackClient(BrokenLLM()).narrate_insights({})

    assert isinstance(result, str)
    assert_fallback_logged(caplog, "narrate_insights")


def test_narrate_cashflow_fallback_logs_event(caplog):
    result = FallbackClient(BrokenLLM()).narrate_cashflow({})

    assert isinstance(result, str)
    assert_fallback_logged(caplog, "narrate_cashflow")


def test_answer_question_fallback_logs_event(caplog):
    result = FallbackClient(BrokenLLM()).answer_question("how am I doing?", {})

    assert isinstance(result, str)
    assert_fallback_logged(caplog, "answer_question")
