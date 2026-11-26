"""O programa encerra com uma mensagem, e não com traceback, quando o
terminal fecha a entrada (Ctrl+D) ou o usuário interrompe (Ctrl+C). A
composição oferece os dois formatos do relatório."""
import os
import subprocess
import sys
from pathlib import Path

from controle.acesso.controle_acesso import ControleAcesso
from infraestrutura.acesso_repositorio_memoria import AcessoRepositorioMemoria
from main import montar_relatorio_controller

RAIZ = Path(__file__).resolve().parent.parent
MAIN = RAIZ / "src" / "main.py"


def executar(entrada: str, tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(RAIZ / "src")
    return subprocess.run(
        [sys.executable, str(MAIN)], input=entrada, text=True,
        capture_output=True, cwd=tmp_path, timeout=30,
        env=env,
    )


def test_ctrl_d_na_escolha_do_armazenamento_nao_deve_mostrar_traceback(tmp_path):
    resultado = executar("", tmp_path)

    assert resultado.returncode == 0
    assert "Encerrando..." in resultado.stdout
    assert "Traceback" not in resultado.stderr


def test_ctrl_d_no_menu_principal_nao_deve_mostrar_traceback(tmp_path):
    resultado = executar("2\n", tmp_path)  # escolhe "Em memória" e a entrada acaba

    assert resultado.returncode == 0
    assert "Encerrando..." in resultado.stdout
    assert "Traceback" not in resultado.stderr


def test_composicao_deve_oferecer_pdf_e_html_com_pdf_como_padrao():
    controller = montar_relatorio_controller(
        AcessoRepositorioMemoria(), ControleAcesso())

    assert controller.formatos_relatorio_acessos() == ["pdf", "html"]
