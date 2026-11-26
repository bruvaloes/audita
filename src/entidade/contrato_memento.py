from dataclasses import dataclass
from datetime import date

from entidade.situacao_contrato import SituacaoContrato


@dataclass(frozen=True)
class ContratoMemento:
    """Memento (GoF): cópia imutável dos valores de um Contrato, para
    permitir desfazer a última atualização sem compartilhar estado com o
    objeto original."""
    numero: str
    empresa_contratada: str
    vigencia_inicio: date
    vigencia_fim: date
    arquivo: str | None
    situacao: SituacaoContrato
    usuarios_vinculados: tuple[int, ...]
