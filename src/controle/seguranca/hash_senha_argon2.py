from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from controle.seguranca.hash_senha import HashSenha

CUSTO_TEMPO_PADRAO = 3
CUSTO_MEMORIA_KIB_PADRAO = 65536
PARALELISMO_PADRAO = 4


class HashSenhaArgon2(HashSenha):
    """Argon2id com salt aleatório por senha (NF001 de Segurança).

    Diferente do bcrypt, não trunca senhas longas, e a política aceita até
    128 caracteres.
    """

    def __init__(self, custo_tempo: int = CUSTO_TEMPO_PADRAO,
                 custo_memoria_kib: int = CUSTO_MEMORIA_KIB_PADRAO,
                 paralelismo: int = PARALELISMO_PADRAO):
        self._hasher = PasswordHasher(
            time_cost=custo_tempo,
            memory_cost=custo_memoria_kib,
            parallelism=paralelismo,
        )

    def gerar(self, senha: str) -> str:
        return self._hasher.hash(senha)

    def verificar(self, senha: str, hash_senha: str) -> bool:
        try:
            return self._hasher.verify(hash_senha, senha)
        except (VerificationError, InvalidHashError):
            return False
