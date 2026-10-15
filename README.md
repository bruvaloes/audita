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

**Planejado**

- Login e controle de acesso por perfil.
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
| Senha | De 8 a 128 caracteres, com ao menos uma letra maiúscula (A-Z), uma minúscula (a-z), um número (0-9) e um caractere especial |
| CPF | Exatamente 11 dígitos numéricos e único entre os usuários |
| E-mail | Deve conter `@` e ser único entre os usuários |

**Política de senhas.** As regras da senha tomam como referência a [política de senhas da AWS IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_passwords_account-policy.html), exigindo cada tipo de caractere. Os caracteres especiais aceitos são:

```
! @ # $ % ^ & * ( ) _ + - = [ ] { } | '
```

Letras acentuadas não contam como maiúscula ou minúscula, e espaço não conta como caractere especial. Hash e recuperação de senha ainda não fazem parte do escopo.

**Exceções.** Os erros de login e de senha usam exceções próprias, definidas em `src/excecao/`, e a tela de cadastro exibe a mensagem correspondente sem encerrar o programa:

- `LoginInvalidoError`: `LoginVazioError`, `LoginMuitoLongoError` e `LoginComNumerosError`.
- `SenhaInvalidaError`: `SenhaMuitoCurtaError`, `SenhaMuitoLongaError`, `SenhaSemMaiusculaError`, `SenhaSemMinusculaError`, `SenhaSemNumeroError` e `SenhaSemCaractereEspecialError`.

As demais validações (campos obrigatórios, CPF, e-mail, unicidade e perfil) ainda lançam `ValueError`.

## Persistência

Hoje, `UsuarioRepositorio` guarda os usuários em memória. O [diagrama de classes](docs/diagramas/classes-analise-usuarios.png) descreve a evolução prevista, ainda **não implementada**:

- `UsuarioRepositorio` passa a ser a interface do repositório.
- `UsuarioRepositorioMemoria` (a implementação atual) e `UsuarioRepositorioSQLite` implementam a interface.
- `UsuarioRepositorioFactory` escolhe a implementação pela variável de ambiente `AUDITA_PERSISTENCIA` (`sqlite` ou `memoria`; padrão `sqlite`), e o `main.py` injeta o repositório criado no controlador.

## Repositório

[https://github.com/bruvaloes/audita](https://github.com/bruvaloes/audita)

## Documentação

- [Documento de Requisitos](docs/documento_de_requisitos_v1.pdf)
- [Diagrama de casos de uso](docs/diagramas/casos-de-uso-usuarios.png)
- [Diagrama de classes](docs/diagramas/classes-analise-usuarios.png) ([fonte editável no draw.io](docs/diagramas/classes-analise-usuarios.drawio))
- [Board do projeto (GitHub Projects)](https://github.com/users/bruvaloes/projects/1)
- [Guia de contribuição](CONTRIBUTING.md)

## Estrutura de pastas

```
audita/
├── docs/
│   ├── diagramas/               # Diagramas de casos de uso e de classes
│   └── documento_de_requisitos_v1.pdf
├── src/
│   ├── fronteira/               # Telas de console
│   ├── controle/                # Regras de negócio e validações
│   ├── entidade/                # Entidades de domínio
│   ├── excecao/                 # Exceções de validação (login e senha)
│   ├── persistencia/            # Repositórios (memória hoje; SQLite planejado)
│   └── main.py                  # Ponto de entrada da aplicação
├── tests/                       # Testes unitários e de integração
└── requirements.txt             # Dependências
```

## Contribuição

As práticas de branches, commits e pull requests do projeto estão documentadas em [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licença

Este projeto está sob a licença MIT — veja o arquivo [`LICENSE`](LICENSE) para mais detalhes.
