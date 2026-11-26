# ADR 0005 · Fachada baseada em Command

- **Status:** aceito; revisa o [ADR 0002](0002-fachada-unica.md)
- **Data:** 25/11/2026 - Sprint 5

## Contexto

O [ADR 0002](0002-fachada-unica.md) criou o `FacadeSingletonController` como uma fachada de delegação simples: cada método chamava direto o controller correspondente. A cada sprint a fachada ganhou operações (usuários, autenticação, contratos, vínculos, relatório de acessos e contagem de entidades) e chegou a cerca de 360 linhas, com 10 métodos duplicados como alias (`adicionar`, `listar_todos`, `listar`, `buscar_por_numero`, `atualizar`, `encerrar`, `remover`, `vincular`, `desvincular` e `quantidade_entidades_cadastradas`), usados só pelos testes. Alguns métodos chegaram a 6 parâmetros, acima do limite de 3 do [CONTRIBUTING](../../CONTRIBUTING.md) (§4.2).

A Sprint 5 pede que a fachada da camada de negócio use o padrão **Command** e, logo depois, que a última atualização de contrato possa ser desfeita (#26). Com a delegação direta, cada operação é só uma chamada de método: não há um objeto que represente o pedido nem um ponto único por onde todas as operações passem, onde um comportamento comum, como o desfazer ou um registro, possa ser acrescentado.

## Decisão

Aplicar o padrão **Command** (GoF) na fachada, no pacote `src/controle/comando/`:

- **Command (`Comando`):** interface genérica com um único método, `executar()`, que devolve o resultado da operação (`Comando[Resultado]`).
- **Comandos concretos:** um por operação da fachada, cada um com o seu receptor e os dados do pedido. São 15: `AutenticarComando`, `CadastrarUsuarioComando`, `ListarUsuariosComando`, `CadastrarContratoComando`, `ListarContratosComando`, `BuscarContratoComando`, `AtualizarContratoComando`, `EncerrarContratoComando`, `RemoverContratoComando`, `VincularUsuarioContratoComando`, `DesvincularUsuarioContratoComando`, `ValidarRecebimentoEvidenciaComando`, `DesfazerUltimaAtualizacaoContratoComando`, `GerarRelatorioAcessosComando` e `ContarEntidadesComando`.
- **Invoker (`ExecutorComandos`):** executa os comandos montados pela fachada. É o único ponto por onde as operações de negócio passam.
- **Receivers:** os controllers que já existiam (`UsuarioController`, `AutenticacaoController`, `ContratoController` e `RelatorioController`) e o `EvidenciaRepositorio`, na contagem. A conferência de permissão continua neles.
- **Client (`FacadeSingletonController`):** continua sendo a fachada única e o Singleton do ADR 0002, mas cada método só monta o comando da operação e o entrega ao executor, sem regra de negócio própria. Os aliases duplicados saem.
- **Dados dos pedidos:** os comandos com mais dados recebem um dataclass imutável (`Credenciais`, `FiltroContratos`, `AtualizacaoContrato`, `RemocaoContrato` e `VinculoContrato`), e a fachada recebe os receptores agrupados em `ReceptoresFachada`, para que nenhuma função passe de 3 parâmetros.

A fachada também deixa de expor os controllers e o executor por propriedade (#120), para que quem tem a fachada não a contorne.

## Alternativas consideradas

- **Manter a delegação direta (ADR 0002):** a mais simples, mas não atende ao pedido da sprint, mantém os métodos com muitos parâmetros e não oferece um ponto único onde o desfazer da #26 se encaixe.
- **Strategy:** serve para trocar o algoritmo de uma mesma operação, como o formato de um relatório. Aqui as operações são diferentes entre si, cada uma com receptor e dados próprios, então não há uma família de algoritmos intercambiáveis para escolher.
- **Dicionário de funções (nome da operação → função):** reduziria o número de classes, mas perde a tipagem dos parâmetros e do resultado, não guarda os dados do pedido em um objeto e deixa os erros de nome para a execução. Também ficaria mais difícil testar cada operação isoladamente.

## Consequências

- **Uma classe por operação:** cada operação nova na fachada exige um comando novo em `src/controle/comando/`, além do método na fachada. Há mais arquivos, mas cada um é pequeno e muda por um único motivo.
- **Testes por comando:** cada comando é testado isoladamente com um receptor falso, e um teste da fachada confere que toda operação passa pelo `ExecutorComandos`.
- **Ponto único de execução:** comportamentos comuns a todas as operações, como o desfazer, um registro ou uma medição de tempo, podem entrar no executor sem mudar a fachada nem os comandos. O desfazer da #26 usa um comando próprio, `DesfazerUltimaAtualizacaoContratoComando`, e guarda o estado com o padrão Memento no `ContratoController`.
- **Permissões continuam nos controllers:** o comando não confere perfil, então nenhuma regra de acesso muda e nenhuma operação escapa da conferência, mesmo fora da fachada.
- **Singleton mantido:** a fachada continua sendo estado global, e os testes seguem chamando `resetar_instancia()`.
