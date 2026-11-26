# Delta: fachada

## ADDED Requirements

### Requirement: Fachada baseada em Command

Toda operação de negócio exposta pela fachada SHALL ser encapsulada em um `Comando` e executada por um único `ExecutorComandos`. A fachada NÃO SHALL conter regra de negócio própria nem alias de métodos dos controllers: cada método monta o comando da operação e o entrega ao executor, e os controllers continuam conferindo as permissões, como receptores do comando.

#### Scenario: Toda operação passa pelo executor
- **WHEN** a fronteira pede qualquer operação da fachada (usuário, contrato, relatório ou contagem)
- **THEN** a fachada monta o comando correspondente e devolve o resultado da execução pelo `ExecutorComandos`

#### Scenario: Sem aliases
- **WHEN** a fachada é inspecionada
- **THEN** ela não expõe métodos que só repassam para outro método dela mesma

### Requirement: Comando de desfazer a última atualização de contrato

A fachada SHALL oferecer uma operação para desfazer a última atualização de contrato, executada como um comando pelo `ExecutorComandos`, delegando ao `ContratoController`.

#### Scenario: Desfazer pela fachada
- **WHEN** a fronteira pede à fachada para desfazer a última atualização de contrato
- **THEN** a fachada executa o comando correspondente e devolve o contrato restaurado
