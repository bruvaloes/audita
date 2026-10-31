from controle.validacao.validador import Validador
from excecao.validacao_error import CampoObrigatorioError, ValidacaoError


class ValidadorEmpresaContratada(Validador):
    """Valida o nome da empresa contratada: obrigatório e até 150 caracteres (RN04.1)."""

    def validar(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise CampoObrigatorioError("Empresa contratada")

        if len(valor.strip()) > 150:
            raise ValidacaoError("Empresa contratada: use até 150 caracteres")
