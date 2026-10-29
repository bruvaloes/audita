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
  - [Persistência](#persistência)
  - [Repositório](#repositório)
  - [Documentação](#documentação)
  - [Estrutura de pastas](#estrutura-de-pastas)
  - [Contribuição](#contribuição)
  - [Licença](#licença)

---

## Visão geral

Nesta etapa do projeto, o Audita permite:

- **Cadastro e login de usuários**, com seleção de perfil (Gestor, Fiscal ou Funcionário) e controle de acesso.
- **Cadastro e gestão de contratos**, vinculados aos usuários responsáveis.
- **Registro fotográfico de tarefas** pelo funcionário, como evidência da execução do serviço.
- **Validação manual das evidências** pelo gestor, aprovando ou recusando os registros enviados.

## Status atual

**Implementado**

- Cadastro e listagem de usuários pelo console, com seleção de perfil.
- Validação de login, senha, CPF e e-mail, com mensagem específica para cada regra violada.
- Persistência de usuários em memória.
- Login por login, CPF ou e-mail, com senha e perfil, e registro de cada tentativa de acesso (veja [Autenticação](#autenticação)).

**Planejado**

- Bloqueio após tentativas de login falhas, expiração de sessão e relatório de acessos.
- Contratos, registro fotográfico de tarefas e validação das evidências.
- Persistência em SQLite e escolha do mecanismo de persistência (veja [Persistência](#persistência)).

## Integrantes

| GitHub |
|--------|
| [@bruvaloes](https://github.com/bruvaloes) |
| [@luyluish](https://github.com/luyluish) |
| [@ilyrsa](https://github.com/ilyrsa) |

## Tecnologias

- **Python 3.10+**
- **SQLite** para persistência (planejado; hoje os dados ficam em memória)
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

# 4. Executar a aplicação
python src/main.py

# 5. Rodar os testes
pytest
```

## Regras de validação

Ao cadastrar um usuário, a aplicação valida os campos e informa qual regra foi violada.

| Campo | Regra |
|-------|-------|
| Login | Obrigatório, com no máximo 12 caracteres e sem números |
| Senha | De 8 a 128 caracteres, com ao menos 3 dos 4 tipos (maiúscula A-Z, minúscula a-z, número 0-9 e caractere especial), diferente do login |
| Confirmação da senha | Deve ser igual à senha |
| Nome | Obrigatório, com até 100 caracteres |
| CPF | Com ou sem pontuação, 11 dígitos com dígitos verificadores válidos (sequências como `111.111.111-11` são recusadas) e único entre os usuários. É guardado só com números e exibido mascarado (`XXX.456.789-XX`) |
| E-mail | Formato `nome@dominio`, sem espaços e com até 100 caracteres, único entre os usuários |
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
| RN02.1 | O identificador é o login, o CPF (**só números**, sem pontuação) ou o e-mail (qualquer texto com `@`). A senha é sempre exigida e conferida pelo hash. |
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

Por enquanto só "Listar usuários" tem tela; as demais funcionalidades se registram no painel (`PainelFronteira.registrar`) quando forem implementadas.

**Registro de acessos.** Toda tentativa, com sucesso ou falha, grava exatamente um `Acesso` (`AcessoRepositorio`, em memória ou SQLite, tabela `acessos`) com o usuário, o perfil informado, a data e hora e o `ResultadoAcesso` (`SUCESSO`, `CREDENCIAIS_INVALIDAS` ou `BLOQUEADO`; este último só será gerado quando o bloqueio por tentativas for implementado). Quando nenhum usuário é identificado, o usuário fica vazio. O texto digitado como identificador não é guardado. Se o registro falhar, o login não é concedido.

## Persistência

Hoje, `UsuarioRepositorio` guarda os usuários em memória. O [diagrama de classes](docs/diagramas/classes-analise-usuarios.png) descreve a evolução prevista, ainda **não implementada**:

- `UsuarioRepositorio` passa a ser a interface do repositório.
- `UsuarioRepositorioMemoria` (a implementação atual) e `UsuarioRepositorioSQLite` implementam a interface.
- `UsuarioRepositorioFactory` escolhe a implementação pela variável de ambiente `AUDITA_PERSISTENCIA` (`sqlite` ou `memoria`; padrão `sqlite`), e o `main.py` injeta o repositório criado no controlador.

## Repositório

[https://github.com/bruvaloes/audita](https://github.com/bruvaloes/audita)

## Documentação

- [Documento de Requisitos](docs/documento_de_requisitos_v2.pdf)
- [Diagrama de casos de uso](docs/diagramas/casos-de-uso-usuarios.png)
- [Diagrama de classes](docs/diagramas/classes-analise-usuarios.png) ([fonte editável no draw.io](docs/diagramas/classes-analise-usuarios.drawio))
- [Board do projeto (GitHub Projects)](https://github.com/users/bruvaloes/projects/1)
- [Guia de contribuição](CONTRIBUTING.md)

## Estrutura de pastas

```
audita/
├── docs/
│   ├── diagramas/               # Diagramas de casos de uso e de classes
│   └── documento_de_requisitos_v2.pdf
├── src/
│   ├── fronteira/               # Telas de console
│   ├── controle/                # Regras de negócio, validações e autenticação
│   ├── entidade/                # Entidades de domínio
│   ├── excecao/                 # Exceções de validação, de autenticação e de persistência
│   ├── persistencia/            # Repositórios de usuários e de acessos (memória e SQLite)
│   └── main.py                  # Ponto de entrada da aplicação
├── tests/                       # Testes unitários e de integração
└── requirements.txt             # Dependências
```

## Contribuição

As práticas de branches, commits e pull requests do projeto estão documentadas em [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licença

Este projeto está sob a licença MIT — veja o arquivo [`LICENSE`](LICENSE) para mais detalhes.
