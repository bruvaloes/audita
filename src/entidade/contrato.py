from dataclasses import dataclass, field
from datetime import date

from entidade.situacao_contrato import SituacaoContrato


@dataclass
class Contrato:
    id: int
    numero: str
    empresa_contratada: str
    vigencia_inicio: date
    vigencia_fim: date
    arquivo: str | None
    situacao: SituacaoContrato
    usuarios_vinculados: list[int] = field(default_factory=list)

    def __repr__(self) -> str:
        """Representação técnica completa do Contrato."""
        return (
            f"Contrato(id={self.id}, numero='{self.numero}', "
            f"empresa_contratada='{self.empresa_contratada}', "
            f"vigencia_inicio={self.vigencia_inicio}, "
            f"vigencia_fim={self.vigencia_fim}, "
            f"arquivo={self.arquivo!r}, "
            f"situacao={self.situacao.name}, "
            f"usuarios_vinculados={self.usuarios_vinculados})"
        )

    def __str__(self) -> str:
        """Representação legível para exibição em menus, logs, etc."""
        inicio = self.vigencia_inicio.strftime("%d/%m/%Y")
        fim = self.vigencia_fim.strftime("%d/%m/%Y")
        return (
            f"[{self.situacao.name}] {self.numero} — "
            f"{self.empresa_contratada} ({inicio} ate {fim})"
        )
