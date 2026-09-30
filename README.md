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
  - [Integrantes](#integrantes)
  - [Tecnologias](#tecnologias)
  - [Como rodar](#como-rodar)
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

## Integrantes

| GitHub |
|--------|
| [@bruvaloes](https://github.com/bruvaloes) |
| [@luyluish](https://github.com/luyluish) |
| [@ilyrsa](https://github.com/ilyrsa) |

## Tecnologias

- **Python 3.10+**
- **SQLite** para persistência
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
python main.py

# 5. Rodar os testes
pytest
```

## Repositório

[https://github.com/bruvaloes/audita](https://github.com/bruvaloes/audita)

## Documentação

- [Documento de Requisitos](docs/documento_de_requisitos_v1.pdf)
- [Board do projeto (GitHub Projects)](https://github.com/users/bruvaloes/projects/1)
- [Guia de contribuição](CONTRIBUTING.md)

## Estrutura de pastas

```
audita/
├── docs/
│   ├── diagramas/               # Diagramas de casos de uso e de classes
│   └── documento_de_requisitos_v1.pdf
├── fronteira/                   # Telas de console
├── controle/                    # Regras de negócio e padrões
├── entidade/                    # Entidades de domínio
├── persistencia/                # Repositórios (memória, arquivo, SQLite)
├── tests/                       # Testes unitários e de integração
├── main.py                      # Ponto de entrada da aplicação
└── requirements.txt             # Dependências
```

## Contribuição

As práticas de branches, commits e pull requests do projeto estão documentadas em [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licença

Este projeto está sob a licença MIT — veja o arquivo [`LICENSE`](LICENSE) para mais detalhes.