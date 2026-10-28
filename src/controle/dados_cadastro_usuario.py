from dataclasses import dataclass


@dataclass(frozen=True)
class DadosCadastroUsuario:
    """Dados brutos (texto) informados no cadastro, antes da validação."""
    nome: str
    cpf: str
    email: str
    login: str
    senha: str
    confirmacao_senha: str
    perfil: str
    aceite_termos: str
