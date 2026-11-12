from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Mapping

from entidade.acesso import Acesso
from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso


@dataclass(frozen=True)
class EstatisticasAcessos:
    """Números do relatório de acessos (RN15.3), iguais em qualquer formato.

    `por_resultado` e `por_perfil` trazem todas as chaves, mesmo com 0; em
    `por_perfil`, a chave None conta as tentativas com perfil inválido.
    """
    total: int
    por_resultado: Mapping[ResultadoAcesso, int]
    por_perfil: Mapping[Perfil | None, int]
    primeiro_acesso: datetime | None
    ultimo_acesso: datetime | None
    gerado_em: datetime

    @property
    def sucessos(self) -> int:
        return self.por_resultado[ResultadoAcesso.SUCESSO]

    @property
    def falhas(self) -> int:
        return self.total - self.sucessos

    @classmethod
    def calcular(cls, acessos: Iterable[Acesso],
                 gerado_em: datetime) -> "EstatisticasAcessos":
        acessos = list(acessos)
        resultados = Counter(acesso.resultado for acesso in acessos)
        perfis = Counter(acesso.perfil for acesso in acessos)
        datas = [acesso.data_hora for acesso in acessos]
        return cls(
            total=len(acessos),
            por_resultado={resultado: resultados[resultado]
                           for resultado in ResultadoAcesso},
            por_perfil={perfil: perfis[perfil]
                        for perfil in [*Perfil, None]},
            primeiro_acesso=min(datas, default=None),
            ultimo_acesso=max(datas, default=None),
            gerado_em=gerado_em,
        )
