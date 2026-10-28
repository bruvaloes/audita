from abc import ABC, abstractmethod

from controle.dados_cadastro_usuario import DadosCadastroUsuario


class RegraCadastro(ABC):
    """Regra que depende de mais de um campo do cadastro.

    Levanta uma subclasse de ValidacaoError quando o cadastro é inválido.
    """

    @abstractmethod
    def validar(self, dados: DadosCadastroUsuario) -> None:
        ...
