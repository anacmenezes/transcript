import json
import logging

from src.transcript.observability.logging import JsonFormatter


def test_json_formatter_produz_log_estruturado():
    record = logging.LogRecord(
        name="transcript.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Requisicao concluida",
        args=(),
        exc_info=None,
    )
    record.request_id = "teste-123"

    result = JsonFormatter().format(record)
    data = json.loads(result)

    assert data["level"] == "INFO"
    assert data["logger"] == "transcript.test"
    assert data["message"] == "Requisicao concluida"
    assert data["request_id"] == "teste-123"
    assert "timestamp" in data