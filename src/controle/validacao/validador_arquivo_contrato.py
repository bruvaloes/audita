import os
from pathlib import Path

from excecao.validacao_error import ArquivoInvalidoError

EXTENSOES_PERMITIDAS = {".pdf", ".docx"}
TAMANHO_MAXIMO_BYTES = 30 * 1024 * 1024  # 30 MB


class ValidadorArquivoContrato:
    """Valida o arquivo anexado ao contrato: opcional, formato PDF/DOCX e até 30 MB (RN04.3)."""

    def validar(self, caminho_arquivo: str | None) -> None:
        if not caminho_arquivo or not str(caminho_arquivo).strip():
            return

        caminho = Path(caminho_arquivo.strip())
        extensao = caminho.suffix.lower()
        if extensao not in EXTENSOES_PERMITIDAS:
            raise ArquivoInvalidoError(
                "Arquivo inválido. Formato e tamanho aceitos: PDF ou DOCX com até 30 MB"
            )

        if os.path.exists(caminho):
            tamanho = os.path.getsize(caminho)
            if tamanho > TAMANHO_MAXIMO_BYTES:
                raise ArquivoInvalidoError(
                    "Arquivo excede 30 MB. Formato e tamanho aceitos: PDF ou DOCX com até 30 MB"
                )
