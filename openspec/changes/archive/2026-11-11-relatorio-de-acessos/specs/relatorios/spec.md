# Delta: relatorios

## ADDED Requirements

### Requirement: Gerar relatório de acessos

O sistema SHALL permitir que o Gestor gere, pelo painel e depois do login, um relatório em PDF com as estatísticas de acesso, a partir dos registros de `Acesso` gravados no login. O relatório traz o total de tentativas de login, os sucessos (SUCESSO) e as falhas (CREDENCIAIS_INVALIDAS), a quantidade por resultado (SUCESSO, CREDENCIAIS_INVALIDAS e BLOQUEADO, este sempre 0 nesta etapa) e por perfil informado. Ao terminar, o sistema informa onde o arquivo foi salvo.

#### Scenario: C1 — Relatório com acessos
- **WHEN** existem 3 acessos (2 com SUCESSO e 1 com CREDENCIAIS_INVALIDAS) e o gestor escolhe "Gerar relatório de acessos"
- **THEN** o sistema gera o PDF com total 3, 2 sucessos e 1 falha
- **AND** exibe "Relatório gerado com sucesso!" e o caminho do arquivo

#### Scenario: C2 — Sem acessos
- **WHEN** não há nenhum acesso registrado e o gestor gera o relatório
- **THEN** o PDF mostra total 0, com 0 sucessos e 0 falhas

#### Scenario: C3 — Sem permissão
- **WHEN** um Funcionário ou Fiscal abre o painel
- **THEN** a opção não aparece
- **AND** se a geração for acionada mesmo assim, o sistema responde "Acesso negado" e não gera arquivo

#### Scenario: Falha ao gravar
- **WHEN** não é possível gravar o arquivo do relatório
- **THEN** o sistema exibe "Erro de armazenamento" com o motivo, sem encerrar

### Requirement: Datas do relatório no padrão brasileiro

As datas e os horários do relatório SHALL seguir o formato dd/mm/aaaa hh:mm, em 24 horas, sem formato ISO (NF006 de Adequação a padrões). Isso vale para a data de geração e para o período dos registros de acesso, do primeiro ao último.

#### Scenario: NF006 — Data de geração e período
- **WHEN** o relatório é gerado
- **THEN** a data de geração e o período dos acessos aparecem em dd/mm/aaaa hh:mm
- **AND** nenhuma data aparece em formato ISO

### Requirement: Novos formatos de relatório

A estrutura do relatório SHALL permitir acrescentar outros formatos, como HTML, sem alterar a classe abstrata nem os formatos existentes.

#### Scenario: Novo formato
- **WHEN** um novo formato de relatório é criado
- **THEN** ele é uma nova subclasse que implementa só a formatação e a extensão do arquivo
