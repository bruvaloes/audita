MENSAGEM_CREDENCIAIS_INVALIDAS = "Credenciais inválidas"


class CredenciaisInvalidasError(Exception):
    """Falha de autenticação por qualquer motivo (RN02.3).

    Há uma só mensagem e nenhuma subclasse de propósito: nada na exceção
    pode revelar se o erro foi no identificador, na senha, no perfil ou na
    situação do usuário.
    """

    def __init__(self):
        super().__init__(MENSAGEM_CREDENCIAIS_INVALIDAS)
