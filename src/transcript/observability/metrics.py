from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "transcript_http_requests_total",
    "Total de requisicoes HTTP recebidas",
    ["method", "route", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "transcript_http_request_duration_seconds",
    "Duracao das requisicoes HTTP em segundos",
    ["method", "route"],
)