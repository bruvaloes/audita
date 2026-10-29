from dataclasses import dataclass
from datetime import datetime

from entidade.origem_evidencia import OrigemEvidencia
from entidade.situacao_validacao import SituacaoValidacao


@dataclass
class Evidencia:
    """Evidência fotográfica de uma tarefa auditada.

    Atributos
    ---------
    id              : identificador único atribuído pelo repositório.
    caminho_imagem  : caminho no sistema de arquivos onde a imagem está armazenada.
                      A imagem deve ser JPG/JPEG/PNG com até 5 MB e mínimo 1024×768.
    enviada_em      : data e hora do envio.
    geolocalizacao  : string com coordenadas geográficas (opcional).
    origem          : CAMERA ou GALERIA.
    situacao        : PENDENTE, APROVADA ou RECUSADA.
    id_funcionario  : id do funcionário que enviou a evidência.
    numero_contrato : número do contrato ao qual a evidência pertence.
    nome_tarefa     : nome da tarefa auditada.
    """

    id: int
    caminho_imagem: str
    enviada_em: datetime
    geolocalizacao: str | None
    origem: OrigemEvidencia
    situacao: SituacaoValidacao
    id_funcionario: int
    numero_contrato: str
    nome_tarefa: str

    def __repr__(self) -> str:
        """Representação técnica completa da Evidencia."""
        return (
            f"Evidencia(id={self.id}, "
            f"caminho_imagem={self.caminho_imagem!r}, "
            f"enviada_em={self.enviada_em.isoformat()}, "
            f"geolocalizacao={self.geolocalizacao!r}, "
            f"origem={self.origem.name}, "
            f"situacao={self.situacao.name}, "
            f"id_funcionario={self.id_funcionario}, "
            f"numero_contrato={self.numero_contrato!r}, "
            f"nome_tarefa={self.nome_tarefa!r})"
        )

    def __str__(self) -> str:
        """Representação legível para exibição em menus, logs, etc."""
        enviada = self.enviada_em.strftime("%d/%m/%Y %H:%M")
        return (
            f"[{self.situacao.name}] {self.nome_tarefa} — "
            f"{self.numero_contrato} ({enviada}, {self.origem.name})"
        )
