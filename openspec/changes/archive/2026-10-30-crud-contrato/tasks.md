# Tarefas: CRUD de contratos

## 1. Entidade e persistência
- [x] 1.1 Entidade `Contrato` e enum `SituacaoContrato`
- [x] 1.2 Interfaces `ConsultaContratos`, `PersistenciaContratos` e `ContratoRepositorio`
- [x] 1.3 `ContratoRepositorioMemoria` e `ContratoRepositorioSQLite`, com `UNIQUE` no número
- [x] 1.4 Testes do contrato do repositório nas duas implementações
- [x] 1.5 Entidade `Evidencia` e repositórios (referência do contrato e da regra de remoção)

## 2. Regras e controller
- [x] 2.1 Exceções de contrato em `validacao_error` e mensagens do requisito
- [x] 2.2 Validadores de número, empresa, vigência e arquivo
- [x] 2.3 `ContratoController`: cadastrar, listar, editar, encerrar, remover, vincular e desvincular
- [x] 2.4 Controle de acesso por perfil em todas as operações
- [x] 2.5 Registro no log de auditoria (cadastro, edição, remoção, vínculo e desvínculo)
- [x] 2.6 Renumeração segura (gravar o novo antes de apagar o antigo; recusar com evidências)
- [x] 2.7 Utilitário de datas no padrão brasileiro

## 3. Log de auditoria
- [x] 3.1 Interface `LogAuditoria` sem operações de alterar ou apagar
- [x] 3.2 `LogAuditoriaAdapter` (biblioteca `logging`) e `LogAuditoriaMemoria`

## 4. Interface
- [x] 4.1 `ContratoFronteira` com as telas de contrato
- [x] 4.2 Ações de contrato no painel por perfil e composição em `main.py`

## 5. Fachada
- [x] 5.1 `FacadeSingletonController` (Singleton) delegando aos controllers
- [x] 5.2 Contagem de entidades (total e por tipo)
- [x] 5.3 Fronteiras passam a usar a fachada
- [x] 5.4 Testes de unicidade, delegação e contagem

## 6. Verificação e documentação
- [x] 6.1 Suíte completa passando na `dev`
- [x] 6.2 Rodar o programa na mão (cadastrar usuário, entrar, cadastrar e vincular contrato, contagem)
- [x] 6.3 ADR da fachada e arquitetura (`docs/07-arquitetura`)
- [x] 6.4 `openspec archive crud-contrato`
