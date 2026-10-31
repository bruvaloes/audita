# Audita
Aplicação para registro e gestão de vistorias de serviços terceirizados.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/Licença-MIT-yellow.svg?style=flat-square)

</div>

---

## Sumário

- [Audita](#audita)
  - [Sumário](#sumário)
  - [Visão geral](#visão-geral)
  - [Status atual](#status-atual)
  - [Integrantes](#integrantes)
  - [Tecnologias](#tecnologias)
  - [Como rodar](#como-rodar)
  - [Regras de validação](#regras-de-validação)
  - [Autenticação](#autenticação)
  - [Contratos](#contratos)
  - [Fachada e log de auditoria](#fachada-e-log-de-auditoria)
  - [Persistência](#persistência)
  - [Repositório](#repositório)
  - [Documentação](#documentação)
  - [Estrutura de pastas](#estrutura-de-pastas)
  - [Contribuição](#contribuição)
  - [Licença](#licença)

---

## Visão geral

O Audita apoia a fiscalização de contratos públicos terceirizados: o gestor cadastra os contratos, vincula fiscais e funcionários, e a execução dos serviços passa a ser comprovada por evidências fotográficas validadas.

**Nesta etapa** ele é uma aplicação de console em Python, com:

- **Cadastro e login de usuários**, com perfil (Gestor, Fiscal ou Funcionário) e controle de acesso por perfil.
- **Cadastro e gestão de contratos**: cadastrar, listar (com busca, filtro e paginação), editar, encerrar, remover e vincular usuários.
- **Log de auditoria** das ações críticas e **fachada única** que concentra o acesso aos controllers.

O registro fotográfico de tarefas e a validação manual das evidências fazem parte do produto completo e ainda não foram implementados.

## Status atual

**Implementado**

- Cadastro e listagem de usuários, com validação de login, senha, CPF, e-mail e perfil, e aceite dos Termos de Uso.
- Login por login, CPF ou e-mail, com senha e perfil, e registro de cada tentativa de acesso (veja [Autenticação](#autenticação)).
- Controle de acesso por perfil nos controllers e painel por perfil.
- CRUD de contratos e vínculo de fiscais e funcionários (veja [Contratos](#contratos)).
- Log de auditoria e fachada única, com a contagem de entidades cadastradas (veja [Fachada e log de auditoria](#fachada-e-log-de-auditoria)).
- Persistência em memória ou em SQLite, escolhida no início da execução (veja [Persistência](#persistência)).

**Planejado**

- Bloqueio após tentativas de login falhas e expiração de sessão.
- Relatório de acessos.
- Registro fotográfico de tarefas e validação das evidências.
- Repository com Factory, Template Method, Command e Memento (próximas sprints).

## Integrantes

| GitHub |
|--------|
| [@bruvaloes](https://github.com/bruvaloes) |
| [@luyluish](https://github.com/luyluish) |
| [@ilyrsa](https://github.com/ilyrsa) |

## Tecnologias

- **Python 3.10+**
- **SQLite** e memória como mecanismos de persistência, escolhidos ao iniciar
- **argon2-cffi** para o hash das senhas (Argon2id)
- **pytest** para testes
- Interface de console

## Como rodar

```bash
# 1. Clonar o repositório
git clone https://github.com/bruvaloes/audita.git
cd audita

# 2. Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Executar a aplicação (ao iniciar, escolha SQLite ou memória)
python src/main.py

# 5. Rodar os testes
pytest
```

## Regras de validação

Ao cadastrar um usuário, a aplicação valida os campos e informa qual regra foi violada.

| Campo | Regra |
|-------|-------|
| Login | Obrigatório, com no máximo 12 caracteres, sem números, e único sem diferenciar maiúsculas de minúsculas |
| Senha | De 8 a 128 caracteres, com ao menos 3 dos 4 tipos (maiúscula A-Z, minúscula a-z, número 0-9 e caractere especial), diferente do login |
| Confirmação da senha | Deve ser igual à senha |
| Nome | Obrigatório, com até 100 caracteres |
| CPF | Com ou sem pontuação, 11 dígitos com dígitos verificadores válidos (sequências como `111.111.111-11` são recusadas) e único entre os usuários. É guardado só com números e exibido mascarado (`XXX.456.789-XX`) |
| E-mail | Formato `nome@dominio`, sem espaços e com até 100 caracteres, único entre os usuários e guardado em minúsculas |
| Perfil | Um dos perfis disponíveis (`GESTOR`, `FISCAL` ou `FUNCIONARIO`) |
| Termos de Uso | O aceite da Política de Privacidade é obrigatório e a data e hora do aceite ficam registradas |

**Política de senhas.** As regras da senha tomam como referência a [política de senhas da AWS IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_passwords_account-policy.html), exigindo pelo menos 3 dos 4 tipos de caractere e senha diferente do login. Os caracteres especiais aceitos são:

```
! @ # $ % ^ & * ( ) _ + - = [ ] { } | '
```

Letras acentuadas não contam como maiúscula ou minúscula, e espaço não conta como caractere especial. A senha é guardada apenas como hash Argon2id, com salt próprio por senha, e nunca em texto aberto. A recuperação de senha não faz parte do escopo.

> **Bancos antigos.** Um `usuarios.db` criado antes do hash guarda as senhas em texto aberto e essas senhas não passam na verificação do hash. Apague o arquivo e cadastre os usuários de novo (o `.db` fica fora do Git).

**Exceções.** Todas as regras do cadastro usam exceções próprias, definidas em `src/excecao/`, e a tela de cadastro exibe a mensagem correspondente sem encerrar o programa:

- `ValidacaoError` é a base de todas as regras do cadastro. Também derivam dela `CampoObrigatorioError`, `CpfInvalidoError`, `NomeMuitoLongoError`, `EmailInvalidoError`, `PerfilInvalidoError`, `UsuarioDuplicadoError` e `TermosNaoAceitosError`.
- `LoginInvalidoError`: `LoginVazioError`, `LoginMuitoLongoError` e `LoginComNumerosError`.
- `SenhaInvalidaError`: `SenhaMuitoCurtaError`, `SenhaMuitoLongaError`, `SenhaComPoucosTiposError`, `SenhaIgualLoginError` e `SenhasDiferentesError`.

Cada regra é um validador próprio em `src/controle/validacao/`, e as regras que cruzam campos (confirmação da senha, senha diferente do login) ficam em `RegraCadastro`.

**Termos de Uso e Política de Privacidade.** O cadastro exibe um resumo antes de pedir o aceite, e o texto completo está na opção **2** do menu (`src/fronteira/textos_legais.py`).

## Autenticação

A opção **3 - Entrar (login)** do menu pede o identificador, a senha e o perfil.

| Regra | Comportamento |
|-------|---------------|
| RN02.1 | O identificador é o login, o CPF (com ou sem pontuação) ou o e-mail (qualquer texto com `@`, sem diferenciar maiúsculas de minúsculas). A senha é sempre exigida e conferida pelo hash. |
| RN02.2 | O perfil informado deve ser o do cadastro. |
| RN02.3 | Qualquer falha mostra apenas `Credenciais inválidas` (`CredenciaisInvalidasError`), sem revelar o motivo. |
| RN02.6 | Usuário inativo não autentica. |

Em caso de sucesso, abre o painel do perfil, que mostra só as ações que o perfil pode executar.

**Controle de acesso por perfil (RF 03).** A matriz de permissões fica em `src/controle/acesso/permissoes.py`, e o `ControleAcesso` confere a permissão nos controllers, e não só no menu. Sem usuário autenticado, toda operação protegida responde `Acesso negado`. Cadastrar-se, ver os termos e entrar são públicos.

| Perfil | Pode |
|--------|------|
| Gestor | Listar usuários, gerenciar contratos (RF 04 a RF 08) e validar evidências (RF 10 e RF 11) |
| Funcionário | Registrar evidência (RF 09) e consultar os próprios envios (RF 12) |
| Fiscal | Só se autenticar, nesta etapa |

O painel do Gestor oferece "Listar usuários" e as ações de contrato. As demais funcionalidades se registram no painel (`PainelFronteira.registrar`) quando forem implementadas.

**Registro de acessos.** Toda tentativa, com sucesso ou falha, grava exatamente um `Acesso` (`AcessoRepositorio`, em memória ou SQLite, tabela `acessos`) com o usuário, o perfil informado, a data e hora e o `ResultadoAcesso` (`SUCESSO`, `CREDENCIAIS_INVALIDAS` ou `BLOQUEADO`; este último só será gerado quando o bloqueio por tentativas for implementado). Quando nenhum usuário é identificado, o usuário fica vazio. O texto digitado como identificador não é guardado. Se o registro falhar, o login não é concedido.

## Contratos

O painel do Gestor traz as ações de contrato. Cada operação confere a permissão no `ContratoController`, e não só no menu.

| Operação | Regras principais |
|----------|-------------------|
| Cadastrar | Número (até 20 caracteres, único), empresa (até 150), vigência em `dd/mm/aaaa` com fim igual ou posterior ao início, e arquivo opcional (PDF ou DOCX existente, até 30 MB). Nasce `ATIVO`. |
| Listar | Mais recentes primeiro, busca por parte do número ou da empresa, filtro por situação e 20 contratos por página. |
| Editar e encerrar | Mesmas validações do cadastro. Contrato encerrado não recebe evidências, e não se encerra um contrato já encerrado. |
| Remover | Exige confirmação e é recusado se o contrato tem evidências (nesse caso, encerre-o). |
| Vincular | Só usuários ativos, fiscais ou funcionários. Todo contrato ativo mantém ao menos um fiscal. |

Renumerar um contrato com evidências é recusado, porque as evidências apontam para o número.

## Fachada e log de auditoria

- **Fachada.** `FacadeSingletonController` (Facade + Singleton) é o ponto único de acesso das telas aos controllers de autenticação, de usuários e de contratos. Ela também informa a quantidade de entidades cadastradas (`contar_entidades()` e `contar_entidades_detalhado()`), uma consulta pública que não traz dados pessoais. Veja o [ADR 0002](docs/adr/0002-fachada-unica.md).
- **Log de auditoria.** O cadastro de usuário e o cadastro, a edição, a remoção e os vínculos de contrato geram um registro com usuário, operação, data e hora e detalhes. A interface `LogAuditoria` só permite registrar e consultar, e o `LogAuditoriaAdapter` isola a biblioteca `logging`. No SQLite os registros ficam em `auditoria.log`.

## Persistência

Ao iniciar, o programa pergunta onde guardar os dados:

- **1 - Banco de dados (SQLite):** os dados permanecem depois de encerrar o programa. Os arquivos ficam na pasta de execução: `usuarios.db` (usuários e acessos), `contratos.db` (contratos e vínculos), `evidencias.db` e `auditoria.log`.
- **2 - Em memória:** os dados somem ao encerrar.

Cada entidade tem uma interface de repositório, dividida em consulta e persistência (`ConsultaUsuarios` e `PersistenciaUsuarios`, `ConsultaContratos` e `PersistenciaContratos`), com uma implementação em memória e outra em SQLite. A escolha acontece só no `main.py`; veja o [ADR 0001](docs/adr/0001-persistencia-substituivel.md). Falhas de leitura ou gravação viram `PersistenciaError` e aparecem como `Erro de armazenamento: <motivo>`, sem encerrar o programa.

## Repositório

[https://github.com/bruvaloes/audita](https://github.com/bruvaloes/audita)

## Documentação

- [Documento de Requisitos](docs/documento_de_requisitos_v2.pdf)
- [Visão](docs/01-visao.md), [glossário](docs/02-glossario.md) e [elicitação](docs/03-elicitacao.md)
- [Casos de uso](docs/04-casos-de-uso/README.md) e [casos de uso do sistema](docs/04-casos-de-uso/casos-de-uso-completo.md)
- [Análise](docs/05-analise.md), [interface](docs/06-interface/README.md), [arquitetura](docs/07-arquitetura/README.md) e [projeto](docs/08-projeto.md)
- Decisões de arquitetura: [ADR 0001](docs/adr/0001-persistencia-substituivel.md) e [ADR 0002](docs/adr/0002-fachada-unica.md)
- Especificações em [`openspec/specs`](openspec/specs) (usuários, contratos e fachada)
- [Board do projeto (GitHub Projects)](https://github.com/users/bruvaloes/projects/1)
- [Guia de contribuição](CONTRIBUTING.md)

## Estrutura de pastas

```
audita/
├── docs/                        # Documentação, ADRs e diagramas
│   ├── adr/
│   └── diagramas/
├── openspec/
│   ├── specs/                   # Especificações do sistema entregue
│   └── changes/archive/         # Mudanças já concluídas
├── src/
│   ├── fronteira/               # Telas de console e painel por perfil
│   ├── controle/                # Regras de negócio, validações, acesso, autenticação e fachada
│   ├── entidade/                # Entidades de domínio
│   ├── excecao/                 # Exceções de validação, de acesso, de autenticação e de persistência
│   ├── log/                     # Log de auditoria
│   ├── persistencia/            # Repositórios (memória e SQLite)
│   └── main.py                  # Ponto de entrada da aplicação
├── tests/                       # Testes unitários e de integração
└── requirements.txt             # Dependências
```

## Contribuição

As práticas de branches, commits e pull requests do projeto estão documentadas em [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licença

Este projeto está sob a licença MIT — veja o arquivo [`LICENSE`](LICENSE) para mais detalhes.
