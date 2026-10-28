QUANTIDADE_DIGITOS_CPF = 11
MASCARA_CPF_INVALIDO = "XXX.XXX.XXX-XX"


def normalizar_cpf(texto: str) -> str:
    """Remove espaços nas pontas, pontos e traço, deixando só os dígitos."""
    return texto.strip().replace(".", "").replace("-", "")


def cpf_valido(texto: str) -> bool:
    """Confere tamanho, dígitos verificadores e rejeita CPF de dígitos iguais."""
    cpf = normalizar_cpf(texto)
    if not cpf.isdigit() or len(cpf) != QUANTIDADE_DIGITOS_CPF:
        return False
    if len(set(cpf)) == 1:
        return False
    return cpf[9] == _digito_verificador(cpf[:9]) and \
        cpf[10] == _digito_verificador(cpf[:10])


def mascarar_cpf(texto: str) -> str:
    """Oculta os 3 primeiros e os 2 últimos dígitos: XXX.456.789-XX."""
    cpf = normalizar_cpf(texto)
    if not cpf.isdigit() or len(cpf) != QUANTIDADE_DIGITOS_CPF:
        return MASCARA_CPF_INVALIDO
    return f"XXX.{cpf[3:6]}.{cpf[6:9]}-XX"


def _digito_verificador(base: str) -> str:
    pesos = range(len(base) + 1, 1, -1)
    soma = sum(int(digito) * peso for digito, peso in zip(base, pesos))
    return str((soma * 10 % 11) % 10)
