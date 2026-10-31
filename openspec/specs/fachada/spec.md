# Fachada

## Purpose

Oferecer à camada de fronteira um ponto único de acesso aos controllers e a consulta da quantidade de entidades cadastradas.

## Requirements

### Requirement: Fachada única

O sistema SHALL oferecer uma fachada única, com uma só instância, que concentra o acesso da camada de fronteira aos controllers de autenticação, de usuários e de contratos.

#### Scenario: Instância única
- **WHEN** a fachada é obtida mais de uma vez
- **THEN** o sistema devolve sempre a mesma instância

#### Scenario: Fachada ainda não criada
- **WHEN** a instância é pedida antes de a fachada ser criada
- **THEN** o sistema sinaliza o erro, sem criar uma fachada vazia

#### Scenario: Delegação
- **WHEN** a fronteira pede uma operação de contrato ou de usuário pela fachada
- **THEN** a fachada executa a operação no controller correspondente e devolve o mesmo resultado

### Requirement: Quantidade de entidades cadastradas

A fachada SHALL informar a quantidade de entidades cadastradas: o total e a de cada tipo (usuários, contratos e evidências).

#### Scenario: Contagem
- **WHEN** existem 2 usuários, 1 contrato e nenhuma evidência e a consulta é feita
- **THEN** a fachada devolve 2 usuários, 1 contrato, 0 evidências e o total 3

#### Scenario: Sem nenhum registro
- **WHEN** não há nenhuma entidade cadastrada
- **THEN** a fachada devolve 0 no total e em cada tipo
