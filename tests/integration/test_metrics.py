def test_endpoint_metrics_existe(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "python_info" in response.text or "process_cpu_seconds" in response.text


def test_requisicao_retorna_request_id(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")
    assert response.json()["status"] == "alive"


def test_request_id_enviado_pelo_cliente_e_reutilizado(client):
    request_id = "observabilidade-teste-123"

    response = client.get(
        "/health/live",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id