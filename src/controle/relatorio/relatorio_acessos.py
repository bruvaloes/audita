from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Callable

from controle.relatorio.estatisticas_acessos import EstatisticasAcessos
from entidade.acesso import Acesso
from entidade.perfil import Perfil
from entidade.resultado_acesso import ResultadoAcesso
from excecao.persistencia_error import EscritaPersistenciaError
from negocio.acesso_repositorio import ConsultaAcessos

PASTA_RELATORIOS = "relatorios"
PREFIXO_ARQUIVO = "relatorio-acessos"
# Também no padrão brasileiro (NF006), com segundos para dois relatórios
# gerados no mesmo minuto não se sobrescreverem.
FORMATO_DATA_ARQUIVO = "%d-%m-%Y_%H-%M-%S"

# Textos comuns a todos os formatos, para o relatório dizer o mesmo em
# PDF, HTML ou qualquer outro.
TITULO_RELATORIO = "Relatório de estatísticas de acesso"
ROTULOS_RESULTADO = {
    ResultadoAcesso.SUCESSO: "Sucesso",
    ResultadoAcesso.CREDENCIAIS_INVALIDAS: "Credenciais inválidas",
    ResultadoAcesso.BLOQUEADO: "Bloqueado",
}
ROTULOS_PERFIL = {
    Perfil.GESTOR: "Gestor",
    Perfil.FISCAL: "Fiscal",
    Perfil.FUNCIONARIO: "Funcionário",
    None: "Perfil inválido",
}


class RelatorioAcessos(ABC):
    """Template Method (GoF) do relatório de estatísticas de acesso (RF 15).

    `gerar` fixa o passo a passo: coletar os acessos, calcular as
    estatísticas, formatar e salvar o arquivo. Cada formato é uma subclasse
    que só implementa `extensao` e `_formatar`; acrescentar um formato, como
    HTML, não muda esta classe nem as outras subclasses (RN15.5).
    """

    def __init__(self, consulta_acessos: ConsultaAcessos,
                 pasta_destino: Path | str = PASTA_RELATORIOS,
                 relogio: Callable[[], datetime] = datetime.now):
        self._consulta_acessos = consulta_acessos
        self._pasta_destino = Path(pasta_destino)
        self._relogio = relogio

    def gerar(self) -> Path:
        """Gera o relatório e devolve o caminho do arquivo salvo (RN15.6).

        Levanta PersistenciaError se não for possível ler os acessos ou
        gravar o arquivo.
        """
        acessos = self._coletar()
        estatisticas = self._calcular(acessos)
        conteudo = self._formatar(estatisticas)
        return self._salvar(conteudo, estatisticas.gerado_em)

    @property
    @abstractmethod
    def extensao(self) -> str:
        """Extensão do arquivo gerado, sem o ponto (ex.: "pdf")."""

    @abstractmethod
    def _formatar(self, estatisticas: EstatisticasAcessos) -> bytes:
        """Converte as estatísticas no conteúdo do arquivo deste formato.

        Datas e horários seguem o padrão dd/mm/aaaa hh:mm (RN15.4).
        """

    def _coletar(self) -> list[Acesso]:
        return self._consulta_acessos.listar_todos()

    def _calcular(self, acessos: list[Acesso]) -> EstatisticasAcessos:
        return EstatisticasAcessos.calcular(acessos, gerado_em=self._relogio())

    def _salvar(self, conteudo: bytes, gerado_em: datetime) -> Path:
        nome = (f"{PREFIXO_ARQUIVO}_{gerado_em.strftime(FORMATO_DATA_ARQUIVO)}"
                f".{self.extensao}")
        caminho = self._pasta_destino / nome
        try:
            self._pasta_destino.mkdir(parents=True, exist_ok=True)
            caminho.write_bytes(conteudo)
        except OSError as erro:
            raise EscritaPersistenciaError(
                f"Não foi possível salvar o relatório em {caminho}: "
                f"{erro.strerror or erro}") from erro
        return caminho.resolve()
