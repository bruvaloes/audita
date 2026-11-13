from dataclasses import dataclass

from controle.dados_cadastro_contrato import DadosCadastroContrato


@dataclass(frozen=True)
class AtualizacaoContrato:
    """Pedido de edição dos dados cadastrais de um contrato (RF 06)."""
    numero_atual: str
    dados: DadosCadastroContrato


@dataclass(frozen=True)
class RemocaoContrato:
    """Pedido de remoção de um contrato (RF 07)."""
    numero: str
    confirmado: bool = False


@dataclass(frozen=True)
class VinculoContrato:
    """Usuário a vincular ou desvincular de um contrato (RF 08)."""
    numero: str
    id_usuario: int
