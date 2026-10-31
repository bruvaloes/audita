def normalizar_email(texto: str) -> str:
    """Remove espaços nas pontas e passa para minúsculas, para o e-mail ser
    gravado e buscado sempre da mesma forma."""
    return texto.strip().lower()
