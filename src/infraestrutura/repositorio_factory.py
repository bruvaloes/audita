from abc import ABC, abstractmethod

from log.log_auditoria import LogAuditoria
from log.log_auditoria_adapter import LogAuditoriaAdapter
from log.log_auditoria_memoria import LogAuditoriaMemoria
from negocio.acesso_repositorio import AcessoRepositorio
from negocio.contrato_repositorio import ContratoRepositorio
from negocio.evidencia_repositorio import EvidenciaRepositorio
from negocio.usuario_repositorio import UsuarioRepositorio
from infraestrutura.acesso_repositorio_memoria import AcessoRepositorioMemoria
from infraestrutura.acesso_repositorio_sqlite import AcessoRepositorioSQLite
from infraestrutura.contrato_repositorio_memoria import ContratoRepositorioMemoria
from infraestrutura.contrato_repositorio_sqlite import ContratoRepositorioSQLite
from infraestrutura.evidencia_repositorio_memoria import EvidenciaRepositorioMemoria
from infraestrutura.evidencia_repositorio_sqlite import EvidenciaRepositorioSQLite
from infraestrutura.usuario_repositorio_memoria import UsuarioRepositorioMemoria
from infraestrutura.usuario_repositorio_sqlite import UsuarioRepositorioSQLite


class RepositorioFactory(ABC):
    """Fábrica abstrata (Abstract Factory / Factory Method) para criação dos
    repositórios das entidades do sistema e do log de auditoria, garantindo
    que todos os repositórios pertençam à mesma família de persistência.
    """

    @abstractmethod
    def criar_usuario_repositorio(self) -> UsuarioRepositorio:
        """Cria o repositório de usuários."""

    @abstractmethod
    def criar_acesso_repositorio(self) -> AcessoRepositorio:
        """Cria o repositório de acessos."""

    @abstractmethod
    def criar_contrato_repositorio(self) -> ContratoRepositorio:
        """Cria o repositório de contratos."""

    @abstractmethod
    def criar_evidencia_repositorio(self) -> EvidenciaRepositorio:
        """Cria o repositório de evidências."""

    @abstractmethod
    def criar_log_auditoria(self) -> LogAuditoria:
        """Cria o mecanismo de log de auditoria."""

    def criar_todos(self) -> tuple[
        UsuarioRepositorio,
        AcessoRepositorio,
        ContratoRepositorio,
        EvidenciaRepositorio,
        LogAuditoria,
    ]:
        """Cria e retorna a tupla com todos os repositórios e log."""
        return (
            self.criar_usuario_repositorio(),
            self.criar_acesso_repositorio(),
            self.criar_contrato_repositorio(),
            self.criar_evidencia_repositorio(),
            self.criar_log_auditoria(),
        )

    # Aliases curtos para conveniência
    def criar_usuario(self) -> UsuarioRepositorio:
        return self.criar_usuario_repositorio()

    def criar_acesso(self) -> AcessoRepositorio:
        return self.criar_acesso_repositorio()

    def criar_contrato(self) -> ContratoRepositorio:
        return self.criar_contrato_repositorio()

    def criar_evidencia(self) -> EvidenciaRepositorio:
        return self.criar_evidencia_repositorio()

    def criar_log(self) -> LogAuditoria:
        return self.criar_log_auditoria()


class RepositorioFactoryMemoria(RepositorioFactory):
    """Fábrica para instanciar repositórios voláteis em memória."""

    def criar_usuario_repositorio(self) -> UsuarioRepositorio:
        return UsuarioRepositorioMemoria()

    def criar_acesso_repositorio(self) -> AcessoRepositorio:
        return AcessoRepositorioMemoria()

    def criar_contrato_repositorio(self) -> ContratoRepositorio:
        return ContratoRepositorioMemoria()

    def criar_evidencia_repositorio(self) -> EvidenciaRepositorio:
        return EvidenciaRepositorioMemoria()

    def criar_log_auditoria(self) -> LogAuditoria:
        return LogAuditoriaMemoria()


class RepositorioFactorySQLite(RepositorioFactory):
    """Fábrica para instanciar repositórios persistentes utilizando SQLite."""

    def __init__(
        self,
        db_usuarios: str = "usuarios.db",
        db_acessos: str | None = None,
        db_contratos: str = "contratos.db",
        db_evidencias: str = "evidencias.db",
        caminho_log: str = "auditoria.log",
    ):
        self.db_usuarios = db_usuarios
        self.db_acessos = db_acessos or db_usuarios
        self.db_contratos = db_contratos
        self.db_evidencias = db_evidencias
        self.caminho_log = caminho_log

    def criar_usuario_repositorio(self) -> UsuarioRepositorio:
        return UsuarioRepositorioSQLite(self.db_usuarios)

    def criar_acesso_repositorio(self) -> AcessoRepositorio:
        return AcessoRepositorioSQLite(self.db_acessos)

    def criar_contrato_repositorio(self) -> ContratoRepositorio:
        return ContratoRepositorioSQLite(self.db_contratos)

    def criar_evidencia_repositorio(self) -> EvidenciaRepositorio:
        return EvidenciaRepositorioSQLite(self.db_evidencias)

    def criar_log_auditoria(self) -> LogAuditoria:
        return LogAuditoriaAdapter(self.caminho_log)

