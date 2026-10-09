from typing import Callable

from controle.validacao.validador import Validador
from entidade.usuario import Usuario
from excecao.validacao_error import UsuarioDuplicadoError
from persistencia.usuario_repositorio import ConsultaUsuarios


class ValidadorUnicidade(Validador):
    """Rejeita valores que já pertencem a algum usuário cadastrado.

    Depende só da busca desejada (ex.: consulta.buscar_por_cpf), não do
    repositório inteiro.
    """

    def __init__(self, nome_campo: str,
                 buscar: Callable[[str], Usuario | None]):
        self._nome_campo = nome_campo
        self._buscar = buscar

    def validar(self, valor: str) -> None:
        if self._buscar(valor):
            raise UsuarioDuplicadoError(self._nome_campo)

    @classmethod
    def para_cpf(cls, consulta: ConsultaUsuarios) -> "ValidadorUnicidade":
        return cls("CPF", consulta.buscar_por_cpf)

    @classmethod
    def para_email(cls, consulta: ConsultaUsuarios) -> "ValidadorUnicidade":
        return cls("e-mail", consulta.buscar_por_email)
