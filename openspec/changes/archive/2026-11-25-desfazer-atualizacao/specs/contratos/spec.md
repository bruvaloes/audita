# Delta: contratos

## ADDED Requirements

### Requirement: Desfazer a última atualização do contrato

O sistema SHALL permitir que o Gestor desfaça a última atualização de um contrato — edição, encerramento, vínculo ou desvínculo de usuário —, restaurando os valores ao estado imediatamente anterior a essa atualização. SHALL manter só um nível de desfazer: a atualização mais recente, de qualquer contrato. Desfazer NÃO SHALL criar um novo ponto para desfazer, e o histórico SHALL ficar só em memória, sem sobreviver a um reinício do programa.

#### Scenario: Desfazer uma edição
- **WHEN** o Gestor edita um contrato e, antes de qualquer outra atualização, escolhe desfazer
- **THEN** os valores do contrato voltam aos de antes da edição

#### Scenario: Desfazer um encerramento
- **WHEN** o Gestor encerra um contrato e desfaz
- **THEN** a situação do contrato volta a ATIVO

#### Scenario: Desfazer um vínculo ou desvínculo
- **WHEN** o Gestor vincula ou desvincula um usuário de um contrato e desfaz
- **THEN** o vínculo volta ao estado anterior à operação

#### Scenario: Desfazer uma renumeração
- **WHEN** o Gestor edita o número de um contrato e desfaz
- **THEN** o número antigo volta a existir e o número novo deixa de existir
- **AND** o contrato restaurado recebe um novo identificador interno

#### Scenario: Nada para desfazer
- **WHEN** não há nenhuma atualização registrada, ou a última já foi desfeita, ou o contrato daquela atualização foi removido
- **THEN** o sistema informa "Nenhuma atualização para desfazer" e nada muda

#### Scenario: Nova atualização substitui o ponto de desfazer
- **WHEN** há uma atualização registrada e uma nova atualização (de qualquer contrato) ocorre antes do desfazer
- **THEN** só a atualização mais recente pode ser desfeita; a anterior deixa de estar disponível

#### Scenario: Remoção limpa o histórico
- **WHEN** um contrato é removido
- **THEN** o histórico de desfazer fica vazio, mesmo que a última atualização registrada fosse de outro contrato

#### Scenario: Acesso restrito ao Gestor
- **WHEN** um usuário Fiscal ou Funcionário tenta desfazer a última atualização
- **THEN** o sistema nega o acesso e nada muda

#### Scenario: Funciona nos dois mecanismos de persistência
- **WHEN** o repositório de contratos é em memória ou SQLite
- **THEN** o desfazer tem o mesmo comportamento nos dois casos
