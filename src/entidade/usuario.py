from dataclasses import dataclass
from datetime import datetime

from entidade.cpf import mascarar_cpf
from entidade.perfil import Perfil


@dataclass
class Usuario:
    id: int
    nome: str
    cpf: str
    email: str
    login: str
    senha_hash: str
    perfil: Perfil
    ativo: bool = True
    aceite_termos_em: datetime | None = None

    @property
    def situacao(self) -> str:
        return "Ativo" if self.ativo else "Inativo"

    def __repr__(self) -> str:
        """
        Representação geral do Usuário, sem printar a senha por questões
        de segurança.
        """
        return (f"Usuario(id={self.id}, nome='{self.nome}', "
                f"cpf='{mascarar_cpf(self.cpf)}', "
                f"email='{self.email}', login='{self.login}', "
                f"perfil={self.perfil.name}, ativo={self.ativo})")

    def __str__(self) -> str:
        """
        Representação mais organizada, para exibição em prints, logs, etc.
        """
        return (f"[{self.perfil.name}] {self.nome} - "
                f"E-mail: {self.email} ({self.situacao})")
