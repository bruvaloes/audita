from dataclasses import dataclass
from entidade.perfil import Perfil

@dataclass
class Usuario:
    id: int
    nome: str
    cpf: str
    email: str
    login: str
    senha: str
    perfil: Perfil
    ativo: bool = True

    def __repr__(self) -> str:
        """
        Representação geral do Usuário, sem printar a senha por questões
        de segurança.
        """
        return (f"Usuario(id={self.id}, nome='{self.nome}', cpf='{self.cpf}', "
                f"email='{self.email}', login='{self.login}', perfil={self.perfil.name}, ativo={self.ativo})")

    def __str__(self) -> str:
        """
        Representação mais organizada, para exibição em prints, logs, etc.  
        """
        status = "Ativo" if self.ativo else "Inativo"
        return f"[{self.perfil.name}] {self.nome} - E-mail: {self.email} ({status})"
