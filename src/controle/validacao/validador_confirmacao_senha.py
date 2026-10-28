from controle.dados_cadastro_usuario import DadosCadastroUsuario
from controle.validacao.regra_cadastro import RegraCadastro
from excecao.senha_invalida_error import SenhasDiferentesError


class ValidadorConfirmacaoSenha(RegraCadastro):

    def validar(self, dados: DadosCadastroUsuario) -> None:
        if dados.senha != dados.confirmacao_senha:
            raise SenhasDiferentesError()
