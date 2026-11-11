# ADR 0004 · Adapter para log de auditoria

- **Status:** aceito
- **Data:** Sprint 3, mas formalizado em 10/11/2026 - Sprint 4

## Contexto

A aplicação exige o registro e a consulta de ações críticas em um log de auditoria contínuo e imutável (requisito funcional RF 15 e requisito não funcional NF004). O NF004 estabelece que todo evento crítico deve ser gravado em armazenamento persistente em menos de 1 segundo, sem possibilidade de exclusão ou alteração de registros pela interface da aplicação.

A biblioteca padrão do Python (`logging`) oferece infraestrutura robusta e madura para gravação em arquivo via `FileHandler` e controle de formatação com `Formatter`. No entanto, a sua interface pública é orientada a níveis de severidade arbitrários (`debug`, `info`, `warning`, `error`), aceita mensagens em texto puro ou strings formatadas e não possui suporte nativo à leitura estruturada ou à tipagem do domínio. Acoplar controllers ou validadores diretamente à biblioteca padrão `logging` violaria o isolamento arquitetural e dificultaria a substituição por outro mecanismo ou por implementações voltadas a testes.

## Decisão

Aplicar o padrão **Adapter** (GoF) criando a classe `LogAuditoriaAdapter` (em `src/log/log_auditoria_adapter.py`), que atua como o adaptador concreto, implementando a interface de domínio `LogAuditoria` (Target, em `src/log/log_auditoria.py`):

- **Target (`LogAuditoria`):** expõe exclusivamente as operações permitidas pelo domínio: `registrar(registro: RegistroLog)` para acréscimo de eventos e `listar() -> list[RegistroLog]` para consulta ordenada. Não expõe métodos de edição ou remoção, assegurando a imutabilidade por contrato.
- **Adaptee (`logging`):** os detalhes de configuração do `logging.Logger`, manipulação do `logging.FileHandler`, codificação UTF-8 e aplicação do `logging.Formatter` ficam totalmente encapsulados no interior do adapter.
- **Conformidade com NF004:** o método `registrar()` formata o `RegistroLog` em linha delimitada e invoca explicitamente `self._handler.flush()`, garantindo persistência imediata em disco em menos de 1 segundo.
- **Isolamento estrito:** nenhuma outra classe ou camada do sistema importa o módulo padrão `logging`.

## Alternativas consideradas

- **Uso direto de `logging` nos controllers e na raiz:** simples de imediato, mas espalharia chamadas a `logging.info(...)` pela regra de negócio, vazaria detalhes de infraestrutura e impediria a substituição limpa em testes automatizados.
- **Mecanismo próprio de escrita em arquivo (com `open()` direto):** evitaria a biblioteca `logging`, mas perderia os benefícios nativos de tratamento de fluxo, formatação de logs e segurança contra conflitos de concorrência oferecidos pelo subsistema padrão do Python.
- **Bibliotecas externas de log estruturado (ex.: Loguru ou structlog):** adicionariam dependências de terceiros desnecessárias para o porte atual da aplicação.

## Consequências

- **Desacoplamento do domínio:** os controllers, serviços e a fachada de negócio dependem unicamente da abstração `LogAuditoria` e da entidade `RegistroLog`, sem ciência do mecanismo subjacente.
- **Facilidade de troca de implementação:** substituir o `logging` por um banco de dados, serviço de log em nuvem ou formato estruturado (ex.: JSON) exige criar uma nova implementação de `LogAuditoria`, sem qualquer impacto nas camadas de negócio ou apresentação.
- **Suporte a testes sem I/O:** foi viabilizada a criação de `LogAuditoriaMemoria` para testes unitários, permitindo inspecionar registros em memória sem gerar arquivos físicos em disco.
- **Responsabilidade de parsing no adapter:** como a biblioteca `logging` padrão não possui leitura nativa de registros, a reconstituição dos objetos `RegistroLog` no método `listar()` é realizada pelo próprio adapter a partir da leitura e separação dos campos do arquivo formatado.

