# ADR 0003 · Repository e Abstract Factory

- **Status:** aceito
- **Data:** 10/11/2026 - Sprint 4

## Contexto

O projeto adota o padrão Repository para abstrair a camada de persistência, separando regras de negócio dos detalhes de armazenamento. Estão definidas em `src/negocio/` as interfaces `UsuarioRepositorio`, `ContratoRepositorio`, `EvidenciaRepositorio` e `AcessoRepositorio` (além da interface `LogAuditoria` em `src/log/`).

Anteriormente, a raiz de composição (`main.py`) e os arquivos de teste instanciavam manualmente cada implementação concreta de repositório (`*RepositorioMemoria` ou `*RepositorioSQLite`). Com a adição de novas entidades e repositórios a cada sprint, essa abordagem trazia riscos de inconsistência (por exemplo, misturar repositório em memória com repositório em banco) e duplicava código de inicialização e configuração dos caminhos de banco de dados. A Sprint 4 exigiu a introdução de um mecanismo explícito e coeso de criação via Factory.

## Decisão

Aplicar o padrão **Abstract Factory** (GoF) por meio da classe base abstrata `RepositorioFactory` (em `src/infraestrutura/repositorio_factory.py`), responsável por definir a interface de criação de toda a família de repositórios do sistema e do log de auditoria:

- `criar_usuario_repositorio() -> UsuarioRepositorio`
- `criar_acesso_repositorio() -> AcessoRepositorio`
- `criar_contrato_repositorio() -> ContratoRepositorio`
- `criar_evidencia_repositorio() -> EvidenciaRepositorio`
- `criar_log_auditoria() -> LogAuditoria`

Foram implementadas duas fábricas concretas:

1. `RepositorioFactoryMemoria`: instancia implementações puramente em memória (`*RepositorioMemoria` e `LogAuditoriaMemoria`), ideal para testes automatizados rápidos e execução volátil.
2. `RepositorioFactorySQLite`: instancia implementações persistentes baseadas em SQLite (`*RepositorioSQLite` e `LogAuditoriaAdapter`), recebendo e centralizando a parametrização dos caminhos dos bancos (`usuarios.db`, `contratos.db`, `evidencias.db`) e do arquivo de auditoria (`auditoria.log`).

A raiz de composição (`main.py`) e os testes passam a selecionar apenas a fábrica apropriada no início da execução. A camada de fronteira, os controllers e os validadores continuam desacoplados, interagindo exclusivamente com as interfaces abstratas de domínio.

## Alternativas consideradas

- **Instanciação manual na raiz de composição (como era antes):** simples para poucas classes, mas propensa a falhas de consistência à medida que o número de entidades e mecanismos cresce.
- **Factory Method isolado para cada repositório:** funções ou classes de fábrica individuais para cada entidade. Foi descartado porque não impedia que o sistema misturasse acidentalmente implementações de famílias distintas (ex.: persistência SQLite para usuários com repositório em memória para contratos).
- **Contêiner IoC/Injeção de Dependências externo:** adicionaria bibliotecas externas e complexidade arquitetural desnecessárias ao escopo do projeto.

## Consequências

- **Consistência garantida:** assegura que todas as dependências de persistência pertençam à mesma família (todas em memória ou todas em SQLite).
- **Isolamento de mudanças:** trocar a tecnologia de armazenamento ou adicionar um novo mecanismo (ex.: PostgreSQL) exige apenas a criação de uma nova fábrica concreta derivada de `RepositorioFactory`, sem alterar controllers, validadores ou telas.
- **Facilidade nos testes:** baterias de testes unitários ou de integração podem injetar `RepositorioFactoryMemoria` para obter um ambiente zerado e rápido sem necessidade de gerenciar arquivos temporários de banco de dados.
- **Acoplamento na infraestrutura:** a classe abstrata `RepositorioFactory` reúne a criação de repositórios de diferentes entidades. Sempre que uma nova entidade for adicionada ao sistema, a fábrica abstrata e suas subclasses concretas devem ser estendidas com o método correspondente.

