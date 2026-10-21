
from pydantic import BaseModel, Field


class Tarefa(BaseModel):
    """Representa uma tarefa identificada na transcrição."""

    descricao: str = Field(
        min_length=1,
        description="Descrição da ação mencionada na transcrição.",
    )
    responsavel: str | None = Field(
        default=None,
        description="Responsável, somente quando explicitamente identificado.",
    )


class AnaliseTranscricao(BaseModel):
    """Estrutura validada da análise de uma transcrição."""

    resumo: str = Field(
        min_length=1,
        description="Resumo fiel do conteúdo da transcrição.",
    )
    topicos_principais: list[str] = Field(
        default_factory=list,
        description="Principais assuntos abordados.",
    )
    decisoes: list[str] = Field(
        default_factory=list,
        description="Decisões explicitamente mencionadas.",
    )
    tarefas: list[Tarefa] = Field(
        default_factory=list,
        description="Ações identificadas no conteúdo.",
    )
    duvidas_em_aberto: list[str] = Field(
        default_factory=list,
        description="Questões pendentes identificadas.",
    )