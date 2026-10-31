# Design: CRUD de contratos

## Contexto

O gerenciamento de usuários já segue a arquitetura em camadas (fronteira, controle, entidade, persistência), com repositório atrás de interface (ADR 0001), uma classe por regra de validação e exceções de domínio. O contrato reaproveita todos esses padrões.

## Decisões

### 1. Entidade e repositório

`Contrato` é uma entidade com número (chave natural, único), empresa, vigência (`date`), arquivo opcional, situação (`SituacaoContrato`: ATIVO ou ENCERRADO) e a lista dos ids dos usuários vinculados.

O repositório segue a divisão do ADR 0001: `ConsultaContratos` (`buscar_por_numero`, `listar`) e `PersistenciaContratos` (`salvar`, `atualizar`, `remover`), compostas em `ContratoRepositorio`, com as implementações em memória e SQLite. No SQLite os vínculos ficam em uma coluna de texto com a lista de ids em JSON.

**Alternativa descartada:** tabela intermediária contrato-usuário. É o modelo mais normalizado, mas pesa mais para uma lista curta de ids e nesta etapa não há consulta que a exija.

### 2. Validação

Uma classe por regra, herdando de `Validador` (`ValidadorNumeroContrato`, `ValidadorEmpresaContratada`, `ValidadorVigencia`, `ValidadorArquivoContrato`), compostas em `ValidadorCadastroContrato`. A vigência recebe o texto digitado e o converte, para a regra de data real de calendário ficar num só lugar. As mensagens saem das exceções de `ValidacaoError`, como no cadastro de usuários.

### 3. Controle de acesso no controller

O `ContratoController` recebe o `ControleAcesso` e confere a permissão de cada operação antes de agir; o primeiro parâmetro de toda operação é o solicitante. O painel só mostra as ações permitidas, mas a conferência no controller é o que garante o RF 03 (NF003 de Segurança). Editar e encerrar usam a mesma permissão (`EDITAR_CONTRATO`), e vincular e desvincular, a mesma (`VINCULAR_USUARIO_CONTRATO`).

### 4. Log de auditoria

O controller recebe uma `LogAuditoria` (interface própria, com o `LogAuditoriaAdapter` sobre a biblioteca `logging` e uma versão em memória) e registra CADASTRO, EDICAO e EXCLUSAO. A interface só tem `registrar` e `listar`, sem alterar nem apagar (NF004). O vínculo e o desvínculo entram como EDICAO.

### 5. Renumerar um contrato

As evidências apontam para o número do contrato. Por isso:
- com evidências, o número não pode mudar;
- sem evidências, o novo registro é gravado **antes** de o antigo ser apagado, para uma falha não perder o contrato.

### 6. Remoção e encerramento

A remoção exige confirmação e é recusada quando há evidências; nesse caso o caminho é encerrar. O encerramento é uma edição que muda a situação para ENCERRADO.

### 7. Listagem

O controller ordena por início da vigência (mais recente primeiro), aplica a busca e o filtro e pagina, devolvendo um `ResultadoPaginado` com os itens, a página atual, o total de páginas e o total de itens. A fronteira só desenha a tabela e a navegação.

### 8. Datas

O módulo `utils/datas` concentra o formato (`dd/mm/aaaa`, `hh:mm`, fuso de Brasília) e a leitura estrita das datas digitadas. Em ambientes sem a base de fusos horários, usa o deslocamento fixo de -3 horas.

### 9. Fachada

`FacadeSingletonController` é um Singleton (instância única, com `obter_instancia` e `resetar_instancia` para os testes) que delega às operações dos controllers e oferece a contagem de entidades. Veja o [ADR 0002](../../../../docs/adr/0002-fachada-unica.md).

## Riscos

- **Estado global do Singleton** pode vazar entre testes; mitigado com `resetar_instancia` e uma fixture automática.
- **Vínculos em JSON** não permitem consulta por usuário no banco; a consulta por usuário é feita em memória, o que basta para 50 contratos.
- **Dois mecanismos de persistência com a mesma regra de unicidade:** a restrição `UNIQUE` do SQLite e o validador precisam concordar; o validador é a regra, e o banco é a segunda barreira.
