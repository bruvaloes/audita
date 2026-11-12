# 08 · Projeto

## 1. Divisão de pacotes

```
src/
├── fronteira/     # Telas de console (usuários, login, painel por perfil, contratos, relatórios)
├── controle/      # Regras de negócio
│   ├── acesso/    # Controle de acesso por perfil
│   ├── relatorio/ # Relatório de acessos (Template Method e formato PDF)
│   ├── seguranca/ # Hash de senha
│   ├── utils/     # Datas no padrão brasileiro
│   └── validacao/ # Um validador por regra
├── entidade/      # Usuario, Perfil, Acesso, Contrato e Evidencia
├── excecao/       # Exceções de validação, de acesso e de persistência
├── log/           # Log de auditoria (interface, adaptador e versão em memória)
├── negocio/       # Interfaces dos repositórios (camada de negócio)
├── infraestrutura/ # Repositórios em memória e SQLite e as fábricas (persistência)
└── main.py        # Raiz de composição
```

**Regra de dependência:** `fronteira` → `controle` → `entidade`; `controle` depende da **interface** do repositório, em `negocio`, nunca de uma implementação de `infraestrutura`. Só o `main.py` escolhe a fábrica concreta, e ela cria as implementações que são injetadas.

## 2. Diagrama de classes de projeto

O diagrama de projeto tem três páginas, editáveis no draw.io a partir de [`diagramas/classes-projeto.drawio`](diagramas/classes-projeto.drawio), e cada página é exportada para um PNG. Cada padrão de projeto aparece com o seu nome, no estereótipo da classe ou no título do grupo.

| Página | PNG | Padrões identificados |
|--------|-----|-----------------------|
| Usuários | `classes-projeto-usuarios.png` | Facade e Singleton, Repository, Factory Method |
| Contratos | `classes-projeto-contratos.png` | Facade e Singleton, Repository, Adapter, Template Method |
| Persistência | `classes-projeto-persistencia.png` | Repository, Factory Method, Adapter |

### Usuários, autenticação e controle de acesso

![Diagrama de classes de projeto do gerenciamento de usuários](diagramas/classes-projeto-usuarios.png)

O diagrama mostra as camadas, os validadores com as exceções que cada um lança, a hierarquia de exceções de validação, o repositório de usuários nas camadas de negócio e de infraestrutura com as exceções de armazenamento, a fábrica usada pelo `main.py`, e a autenticação com o controle de acesso.

As duas partes que mais importam estão também abaixo, para leitura no GitHub.

### Exceções de validação e de persistência

```mermaid
classDiagram
    Exception <|-- ValidacaoError
    Exception <|-- PersistenciaError
    ValidacaoError <|-- CampoObrigatorioError
    ValidacaoError <|-- CpfInvalidoError
    ValidacaoError <|-- EmailInvalidoError
    ValidacaoError <|-- PerfilInvalidoError
    ValidacaoError <|-- UsuarioDuplicadoError
    ValidacaoError <|-- NomeMuitoLongoError
    ValidacaoError <|-- TermosNaoAceitosError
    ValidacaoError <|-- ContratoNumeroJaCadastradoError
    ValidacaoError <|-- ContratoNaoEncontradoError
    ValidacaoError <|-- ContratoComEvidenciasError
    ValidacaoError <|-- VigenciaInvalidaError
    ValidacaoError <|-- DataInvalidaError
    ValidacaoError <|-- ArquivoInvalidoError
    ValidacaoError <|-- PerfilNaoVinculavelError
    ValidacaoError <|-- UltimoFiscalError
    ValidacaoError <|-- ContratoJaEncerradoError
    ValidacaoError <|-- SituacaoInvalidaError
    Exception <|-- AcessoNegadoError
    Exception <|-- CredenciaisInvalidasError
    ValidacaoError <|-- LoginInvalidoError
    ValidacaoError <|-- SenhaInvalidaError
    LoginInvalidoError <|-- LoginVazioError
    LoginInvalidoError <|-- LoginMuitoLongoError
    LoginInvalidoError <|-- LoginComNumerosError
    SenhaInvalidaError <|-- SenhaForaDaPoliticaError
    SenhaForaDaPoliticaError <|-- SenhaMuitoCurtaError
    SenhaForaDaPoliticaError <|-- SenhaMuitoLongaError
    SenhaForaDaPoliticaError <|-- SenhaComPoucosTiposError
    SenhaInvalidaError <|-- SenhaIgualLoginError
    SenhaInvalidaError <|-- SenhasDiferentesError
    PersistenciaError <|-- ConexaoPersistenciaError
    PersistenciaError <|-- LeituraPersistenciaError
    PersistenciaError <|-- EscritaPersistenciaError
```

A fronteira captura `ValidacaoError` e `PersistenciaError` e mostra a mensagem sem encerrar o programa.

### Os dois mecanismos de persistência

```mermaid
classDiagram
    class ConsultaUsuarios {
        <<interface>>
        +listar_todos() list
        +buscar_por_cpf(cpf) Usuario
        +buscar_por_login(login) Usuario
        +buscar_por_email(email) Usuario
    }
    class PersistenciaUsuarios {
        <<interface>>
        +salvar(usuario) Usuario
    }
    class UsuarioRepositorio {
        <<interface>>
    }
    ConsultaUsuarios <|-- UsuarioRepositorio
    PersistenciaUsuarios <|-- UsuarioRepositorio
    class RepositorioFactory {
        <<Factory Method>>
        +criar_usuario_repositorio() UsuarioRepositorio
        +criar_todos() tuple
    }
    UsuarioRepositorio <|.. UsuarioRepositorioMemoria
    UsuarioRepositorio <|.. UsuarioRepositorioSQLite
    RepositorioFactory <|-- RepositorioFactoryMemoria
    RepositorioFactory <|-- RepositorioFactorySQLite
    RepositorioFactoryMemoria ..> UsuarioRepositorioMemoria : cria
    RepositorioFactorySQLite ..> UsuarioRepositorioSQLite : cria
    UsuarioController --> UsuarioRepositorio
    ValidadorCadastroUsuario --> ConsultaUsuarios
```

A escolha do mecanismo está registrada no [ADR 0001](adr/0001-persistencia-substituivel.md), e as fábricas no [ADR 0003](adr/0003-repository-factory.md).

### Contratos, evidências, log de auditoria, relatório e fachada

![Diagrama de classes de projeto: contratos, evidências, log de auditoria, relatório e fachada](diagramas/classes-projeto-contratos.png)

O diagrama mostra o vínculo entre `Contrato` e `Usuario` (RF 08), a `Evidencia` com a sua situação e a sua origem, o log de auditoria com os papéis do Adapter e o relatório de acessos com o Template Method.

A parte de contratos e da fachada, em Mermaid, para leitura direta no GitHub:

```mermaid
classDiagram
    class Usuario {
        <<Entity>>
    }
    class Evidencia {
        <<Entity>>
        numero_contrato
    }
    class Contrato {
        <<Entity>>
        id
        numero
        empresa_contratada
        vigencia_inicio
        vigencia_fim
        arquivo
        situacao
        usuarios_vinculados
    }
    class SituacaoContrato {
        <<Enumeration>>
        ATIVO
        ENCERRADO
    }
    class ConsultaContratos {
        <<interface>>
        +buscar_por_numero(numero) Contrato
        +listar() list
    }
    class PersistenciaContratos {
        <<interface>>
        +salvar(contrato) Contrato
        +atualizar(contrato)
        +remover(numero)
    }
    class ContratoRepositorio {
        <<interface>>
    }
    class ContratoController {
        <<Control>>
        +adicionar(solicitante, dados) Contrato
        +listar(solicitante, busca, situacao, pagina) ResultadoPaginado
        +buscar_por_numero(solicitante, numero) Contrato
        +atualizar(solicitante, numero_atual, dados, nova_situacao) Contrato
        +encerrar(solicitante, numero) Contrato
        +remover(solicitante, numero, confirmado) bool
        +vincular(solicitante, numero, id_usuario)
        +desvincular(solicitante, numero, id_usuario)
        +contar() int
    }
    class ValidadorCadastroContrato {
        <<Control>>
        +validar(dados)
    }
    class ControleAcesso {
        <<Control>>
        +permite(usuario, operacao) bool
        +verificar(usuario, operacao)
    }
    class LogAuditoria {
        <<interface>>
        +registrar(registro)
        +listar() list
    }
    class LogAuditoriaAdapter
    class LogAuditoriaMemoria
    class FacadeSingletonController {
        <<Facade, Singleton>>
        +obter_instancia()$
        +resetar_instancia()$
        +contar_entidades() int
        +contar_entidades_detalhado() dict
    }
    class UsuarioController
    class AutenticacaoController
    class ContratoFronteira
    class UsuarioFronteira
    class AutenticacaoFronteira
    class EvidenciaRepositorio {
        <<interface>>
    }
    class UsuarioRepositorio {
        <<interface>>
    }

    Contrato --> SituacaoContrato
    Contrato --> "0..*" Usuario : usuarios_vinculados
    Evidencia --> Contrato : numero_contrato
    ContratoFronteira --> FacadeSingletonController
    UsuarioFronteira --> FacadeSingletonController
    AutenticacaoFronteira --> FacadeSingletonController
    FacadeSingletonController --> EvidenciaRepositorio
    ContratoController --> EvidenciaRepositorio
    ContratoController --> UsuarioRepositorio
    ConsultaContratos <|-- ContratoRepositorio
    PersistenciaContratos <|-- ContratoRepositorio
    ContratoRepositorio <|.. ContratoRepositorioMemoria
    ContratoRepositorio <|.. ContratoRepositorioSQLite
    ContratoController --> ContratoRepositorio
    ContratoController --> ValidadorCadastroContrato
    ContratoController --> ControleAcesso
    ContratoController --> LogAuditoria
    LogAuditoria <|.. LogAuditoriaAdapter
    LogAuditoria <|.. LogAuditoriaMemoria
    FacadeSingletonController --> ContratoController
    FacadeSingletonController --> UsuarioController
    FacadeSingletonController --> AutenticacaoController
    class RelatorioController {
        <<Control>>
        +gerar_relatorio_acessos(solicitante) Path
    }
    class RelatorioAcessos {
        <<Template Method>>
        +gerar() Path
        #_formatar(estatisticas) bytes*
    }
    class RelatorioAcessosPdf
    RelatorioFronteira --> FacadeSingletonController
    FacadeSingletonController --> RelatorioController
    RelatorioController --> RelatorioAcessos
    RelatorioAcessos <|-- RelatorioAcessosPdf
```

A fachada concentra o acesso da fronteira aos controllers ([ADR 0002](adr/0002-fachada-unica.md)). A permissão é conferida nos controllers, e o log de auditoria só aceita acrescentar e consultar registros.

### Persistência em camadas

![Diagrama de classes de projeto: camadas de negócio e de infraestrutura](diagramas/classes-projeto-persistencia.png)

A camada de negócio (`negocio/`) guarda só as interfaces dos repositórios de usuário, acesso, contrato e evidência, separadas entre consulta e gravação (Repository e ISP). A camada de infraestrutura (`infraestrutura/`) tem os dois mecanismos de persistência, em memória e SQLite, e uma fábrica para cada um (Factory Method). Os controllers e o relatório dependem só das interfaces de `negocio`, e os dois mecanismos lançam as exceções de `PersistenciaError`. O log de auditoria é criado pela mesma fábrica: `LogAuditoriaMemoria` no mecanismo em memória e `LogAuditoriaAdapter` (Adapter da biblioteca `logging`) no SQLite.

## 3. Padrões e princípios usados

Tabela preenchida a cada sprint, conforme os padrões entram no código.

| Padrão / princípio | Onde | Para quê |
|--------------------|------|----------|
| Segregação de interfaces (ISP) | `ConsultaUsuarios` e `PersistenciaUsuarios` | Quem só consulta não depende de gravação |
| Inversão de dependência (DIP) | `UsuarioController` → `UsuarioRepositorio` | Trocar o mecanismo sem mexer na regra de negócio |
| Raiz de composição | `main.py` | Único lugar que escolhe as implementações |
| Uma regra por classe | `Validador` e seus filhos | Incluir ou mudar uma regra sem tocar nas outras |
| DTO | `DadosCadastroUsuario` e `DadosCadastroContrato` | Levar os dados da fronteira ao controle |
| Facade (GoF) | `FacadeSingletonController` | Ponto único de acesso da fronteira aos controllers |
| Singleton (GoF) | `FacadeSingletonController` | Uma só instância da fachada em toda a aplicação |
| Adapter (GoF) | `src/log/log_auditoria_adapter.py` (`LogAuditoriaAdapter`) | Isolar a biblioteca `logging` atrás da interface `LogAuditoria` |
| Repository (GoF) | `src/negocio/usuario_repositorio.py`, `src/negocio/contrato_repositorio.py`, `src/negocio/evidencia_repositorio.py`, `src/negocio/acesso_repositorio.py` | Separar a regra de negócio do mecanismo de persistência; qualquer implementação (memória ou SQLite) é substituível sem alterar os controllers |
| Factory Method (GoF) | `src/infraestrutura/repositorio_factory.py` (`RepositorioFactory`, `RepositorioFactoryMemoria`, `RepositorioFactorySQLite`); instanciado em `src/main.py` | Encapsular a criação da implementação concreta; a escolha do mecanismo (memória ou SQLite) não vaza para os controllers |
| Template Method (GoF) | `src/controle/relatorio/relatorio_acessos.py` (`RelatorioAcessos`); subclasse `relatorio_acessos_pdf.py` | Definir o esqueleto da geração do relatório uma vez (`gerar`) e variar apenas a renderização (`_formatar`) por subclasse |

Os demais padrões GoF (Command e Memento) entram nesta tabela nas sprints em que forem implementados.
