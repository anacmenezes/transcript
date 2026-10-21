
class TranscriptAIError(Exception):
    """Erro base da aplicação Transcript AI."""


class InvalidFileError(TranscriptAIError):
    """Arquivo inválido ou incompatível."""


class TranscriptionError(TranscriptAIError):
    """Falha ao transcrever áudio ou vídeo."""


class AnalysisError(TranscriptAIError):
    """Falha ao gerar a análise estruturada."""


class DocumentProcessingError(TranscriptAIError):
    """Falha ao processar documentos PDF."""


class ChatInitializationError(TranscriptAIError):
    """Falha ao inicializar o chat com documentos."""


class ChatQueryError(TranscriptAIError):
    """Falha ao consultar documentos no chat."""


class FileOperationError(TranscriptAIError):
    """Falha ao salvar ou manipular arquivos."""