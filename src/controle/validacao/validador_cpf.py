from controle.validacao.validador import Validador
from entidade.cpf import cpf_valido
from excecao.validacao_error import CpfInvalidoError


class ValidadorCpf(Validador):

    def validar(self, valor: str) -> None:
        if not cpf_valido(valor):
            raise CpfInvalidoError()
