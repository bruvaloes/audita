from dataclasses import dataclass


@dataclass
class DadosCadastroContrato:
    """Dados de entrada para cadastro ou edição de contrato."""
    numero: str
    empresa_contratada: str
    vigencia_inicio: str  # formato dd/mm/aaaa
    vigencia_fim: str     # formato dd/mm/aaaa
    arquivo: str | None = None
