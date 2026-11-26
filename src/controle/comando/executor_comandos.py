from controle.comando.comando import Comando, Resultado


class ExecutorComandos:
    """Invocador do padrão Command: executa os comandos montados pela fachada.

    É o único ponto por onde as operações de negócio passam, o que permite
    acrescentar um comportamento comum a todas elas, como o desfazer, sem
    mudar a fachada nem os comandos.
    """

    def executar(self, comando: Comando[Resultado]) -> Resultado:
        return comando.executar()
