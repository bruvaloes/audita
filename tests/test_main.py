"""O programa encerra com uma mensagem, e não com traceback, quando o
terminal fecha a entrada (Ctrl+D) ou o usuário interrompe (Ctrl+C)."""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MAIN = RAIZ / "src" / "main.py"


def executar(entrada: str, tmp_path):
    return subprocess.run(
        [sys.executable, str(MAIN)], input=entrada, text=True,
        capture_output=True, cwd=tmp_path, timeout=30,
        env={"PYTHONPATH": str(RAIZ / "src"), "PATH": ""},
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
