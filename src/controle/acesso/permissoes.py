from typing import Mapping

from controle.acesso.operacao import Operacao
from entidade.perfil import Perfil

# RF 03 da v2.0. Um novo perfil ou uma nova permissão é uma linha aqui; os
# controllers não mudam.
PERMISSOES_PADRAO: Mapping[Perfil, frozenset[Operacao]] = {
    # RN03.2: gerenciar contratos (RF 04 a RF 08) e validar evidências
    # (RF 10 e RF 11). Listar usuários apoia o vínculo ao contrato (RF 08).
    Perfil.GESTOR: frozenset({
        Operacao.LISTAR_USUARIOS,
        Operacao.CADASTRAR_CONTRATO,
        Operacao.LISTAR_CONTRATOS,
        Operacao.EDITAR_CONTRATO,
        Operacao.REMOVER_CONTRATO,
        Operacao.VINCULAR_USUARIO_CONTRATO,
        Operacao.LISTAR_EVIDENCIAS,
        Operacao.VALIDAR_EVIDENCIA,
    }),
    # RN03.3: nesta etapa o fiscal só se autentica.
    Perfil.FISCAL: frozenset(),
    # RN03.1: registrar evidência (RF 09) e consultar os próprios envios
    # (RF 12).
    Perfil.FUNCIONARIO: frozenset({
        Operacao.REGISTRAR_EVIDENCIA,
        Operacao.CONSULTAR_PROPRIOS_ENVIOS,
    }),
}
