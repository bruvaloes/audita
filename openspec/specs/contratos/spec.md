# Contratos

## Purpose

Gerenciar o ciclo de vida dos contratos (cadastro, listagem, edição, encerramento e remoção) e o vínculo de fiscais e funcionários, com controle de acesso por perfil, log de auditoria e datas no padrão brasileiro.

## Requirements

### Requirement: Cadastrar contrato

O sistema SHALL permitir que o Gestor cadastre um contrato informando número, empresa contratada, vigência (início e fim) e, opcionalmente, o arquivo. O número (até 20 caracteres, único), a empresa (até 150 caracteres) e as duas datas (dd/mm/aaaa) são obrigatórios. O contrato é criado com situação ATIVO e o cadastro gera registro `CADASTRO` no log de auditoria.

#### Scenario: Cadastro válido
- **WHEN** o gestor informa número, empresa e vigência válidos
- **THEN** o contrato é criado com situação ATIVO e aparece na listagem
- **AND** exibe "Contrato cadastrado com sucesso!"

#### Scenario: Número duplicado
- **WHEN** já existe contrato com o mesmo número
- **THEN** o sistema rejeita e exibe "Número de contrato já cadastrado"

#### Scenario: Vigência inválida
- **WHEN** a data de fim é anterior à de início
- **THEN** o sistema rejeita e exibe "A data de fim deve ser igual ou posterior à data de início"

#### Scenario: Arquivo inválido
- **WHEN** o arquivo não é PDF ou DOCX, ou tem mais de 30 MB
- **THEN** o sistema recusa o arquivo e informa o formato e o tamanho aceitos

#### Scenario: Campo obrigatório vazio
- **WHEN** a empresa contratada não foi preenchida
- **THEN** o sistema indica o campo "Empresa contratada" como obrigatório

### Requirement: Listar contratos

O sistema SHALL exibir ao Gestor os contratos com número, empresa, vigência e situação, ordenados pelo início da vigência do mais recente para o mais antigo. SHALL permitir busca por parte do número ou da empresa (sem diferenciar maiúsculas de minúsculas) e filtro por situação (ATIVO, ENCERRADO ou todos). A lista SHALL ser paginada com 20 contratos por página.

#### Scenario: Listagem padrão
- **WHEN** existem 45 contratos e o gestor abre a listagem
- **THEN** vê os 20 mais recentes e a navegação para as páginas 2 e 3

#### Scenario: Busca
- **WHEN** o gestor busca "limpeza"
- **THEN** só aparecem contratos cujo número ou empresa contenham o termo

#### Scenario: Filtro por situação
- **WHEN** o gestor aplica o filtro ENCERRADO
- **THEN** só aparecem contratos encerrados

#### Scenario: Sem resultados
- **WHEN** o termo buscado não tem correspondência
- **THEN** o sistema exibe "Nenhum contrato encontrado"

### Requirement: Editar e encerrar contrato

O sistema SHALL permitir que o Gestor altere os dados de um contrato e o encerre (situação ENCERRADO), com as mesmas validações do cadastro. Contrato ENCERRADO NÃO SHALL receber novas evidências. A edição SHALL gerar registro `EDICAO` no log, com os valores anterior e novo. O número de um contrato que já tem evidências NÃO SHALL ser alterado.

#### Scenario: Edição válida
- **WHEN** o gestor altera a empresa de um contrato e salva
- **THEN** a listagem mostra o novo valor
- **AND** o log registra a alteração com os valores anterior e novo

#### Scenario: Número em uso
- **WHEN** o novo número pertence a outro contrato
- **THEN** o sistema rejeita e exibe "Número de contrato já cadastrado"

#### Scenario: Encerramento
- **WHEN** o gestor encerra um contrato ATIVO
- **THEN** a situação passa a ENCERRADO
- **AND** o contrato deixa de aceitar novas evidências

#### Scenario: Renumerar contrato com evidências
- **WHEN** o gestor tenta mudar o número de um contrato que já tem evidências
- **THEN** o sistema recusa com "Contrato com evidências não pode ter o número alterado"

### Requirement: Remover contrato

O sistema SHALL permitir que o Gestor remova um contrato sem evidências, mediante confirmação explícita. Contrato com ao menos uma evidência NÃO SHALL ser removido; o gestor deve encerrá-lo. A remoção SHALL gerar registro `EXCLUSAO` no log e desfazer os vínculos do contrato.

#### Scenario: Remoção permitida
- **WHEN** o gestor confirma a remoção de um contrato sem evidências
- **THEN** o contrato deixa de aparecer na listagem

#### Scenario: Remoção cancelada
- **WHEN** o gestor cancela a confirmação
- **THEN** o contrato permanece inalterado

#### Scenario: Remoção bloqueada
- **WHEN** o gestor tenta remover um contrato com evidências
- **THEN** o sistema recusa e informa "Contrato com evidências não pode ser removido; encerre-o"

### Requirement: Vincular usuários a um contrato

O sistema SHALL permitir que o Gestor vincule e desvincule fiscais e funcionários de um contrato. Só SHALL ser vinculado usuário ATIVO com perfil FISCAL ou FUNCIONARIO. Todo contrato ATIVO SHALL ter ao menos um fiscal vinculado. Um usuário pode estar em mais de um contrato. O vínculo e o desvínculo SHALL gerar registro no log de auditoria.

#### Scenario: Vínculo válido
- **WHEN** o gestor vincula um funcionário ATIVO a um contrato ATIVO
- **THEN** o contrato passa a aparecer para esse funcionário

#### Scenario: Perfil incompatível
- **WHEN** o gestor tenta vincular um usuário com perfil GESTOR
- **THEN** o sistema recusa com "Perfil não pode ser vinculado a contrato"

#### Scenario: Último fiscal
- **WHEN** o gestor tenta desvincular o único fiscal de um contrato ATIVO
- **THEN** o sistema recusa com "O contrato deve ter ao menos um fiscal"

### Requirement: Controle de acesso nas operações de contrato

As operações de contrato SHALL ser permitidas só ao perfil Gestor, e a conferência SHALL ser feita na camada de controle, e não só no menu. Sem usuário autenticado, toda operação SHALL ser recusada.

#### Scenario: Perfil sem permissão
- **WHEN** um Funcionário ou um Fiscal aciona qualquer operação de contrato
- **THEN** o sistema responde "Acesso negado" e não altera nada nem gera registro no log

#### Scenario: Sem login
- **WHEN** ninguém está autenticado e uma operação de contrato é acionada
- **THEN** o sistema responde "Acesso negado"

### Requirement: Datas no padrão brasileiro

As datas SHALL ser exibidas no formato dd/mm/aaaa e os horários em hh:mm de 24 horas, no fuso de Brasília. As datas digitadas SHALL ser aceitas só nesse formato e como datas reais de calendário.

#### Scenario: Data digitada fora do formato
- **WHEN** o gestor digita a vigência como 2026-01-31
- **THEN** o sistema rejeita e informa o formato dd/mm/aaaa

#### Scenario: Data inexistente
- **WHEN** o gestor digita 31/02/2026
- **THEN** o sistema rejeita a data

### Requirement: Persistência dos contratos

Os contratos e os vínculos SHALL ser guardados nos dois mecanismos de persistência (memória e SQLite). No SQLite, o número do contrato SHALL ser único.

#### Scenario: Contratos preservados no SQLite
- **WHEN** um contrato é cadastrado com o SQLite e o programa é reiniciado com o SQLite
- **THEN** o contrato e seus vínculos continuam disponíveis

#### Scenario: Falha de armazenamento
- **WHEN** a gravação do contrato falha
- **THEN** o sistema exibe "Erro de armazenamento: <motivo>" e continua em execução
