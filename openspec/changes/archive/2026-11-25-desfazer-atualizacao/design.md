# Design: desfazer a última atualização de contrato

## Contexto

`ContratoController.atualizar` lê o contrato do repositório e muta o próprio objeto (no repositório em memória, é o mesmo objeto armazenado); `encerrar` delega a `atualizar`, e `vincular`/`desvincular` mutam a lista `usuarios_vinculados` do mesmo jeito. Nenhum desses caminhos guarda o estado anterior.

## Decisões

### 1. Memento por cópia de valores

`ContratoMemento` é uma dataclass imutável (`frozen=True`) com os mesmos campos mutáveis de `Contrato` (`numero`, `empresa_contratada`, `vigencia_inicio`, `vigencia_fim`, `arquivo`, `situacao`), e `usuarios_vinculados` como **tupla**, para não compartilhar a lista do objeto original. `Contrato.criar_memento()` é o Originator; `Contrato.restaurar(memento)` aplica os valores de volta (convertendo a tupla para lista).

**Alternativa descartada:** guardar uma cópia profunda do próprio `Contrato`. Funciona, mas expõe um segundo objeto com identidade de entidade (inclusive `id`), que não deveria ser confundido com o contrato "real" guardado no repositório. Um memento com só os valores deixa claro que ele não é uma entidade.

### 2. Caretaker com um único espaço, em memória

`HistoricoAtualizacaoContrato` guarda no máximo uma dupla (número do contrato no momento da atualização, memento do estado anterior). `salvar` substitui o que havia; `limpar` esvazia; `obter` devolve a dupla ou `None`. Não há pilha nem persistência: o histórico some ao reiniciar o programa, e isso é aceitável porque o requisito pede só a última atualização.

**Alternativa descartada:** uma pilha por contrato (um histórico por número). Permitiria desfazer a última atualização de cada contrato independentemente, mas o requisito pede desfazer "a última atualização", no singular, do sistema — não por contrato.

### 3. Desfazer não cria um novo memento

`desfazer_ultima_atualizacao` só chama `limpar()` no caretaker, nunca `salvar()`. Assim, um segundo desfazer sempre encontra o histórico vazio e informa que não há nada para desfazer — não existe "refazer".

### 4. Renumeração

Quando a atualização desfeita envolveu trocar o número do contrato, o registro atual está sob o número novo. Desfazer remove esse registro e insere um novo com o número antigo e os demais valores do memento; como a inserção passa pelo `salvar` do repositório, o `id` é reatribuído (not o mesmo `id` de antes da renumeração). Isso é uma limitação aceita: o número volta, o `id` não.

**Alternativa descartada:** preservar o `id` original na restauração. Exigiria que os repositórios (memória e SQLite) permitissem escolher o `id` na inserção, o que abriria espaço para colisão de `id`s e sai do contrato de `ContratoRepositorio` (`salvar` sempre atribui um `id` novo).

### 5. Nova operação, só do Gestor

`Operacao.DESFAZER_ATUALIZACAO_CONTRATO` segue o mesmo modelo das demais operações de contrato: verificada no controller (não só escondida no painel), e adicionada à permissão do `Perfil.GESTOR` em `PERMISSOES_PADRAO`.

### 6. Comando na fachada

Como a fachada já executa toda operação por um `Comando` (#25), o desfazer ganha `DesfazerUltimaAtualizacaoContratoComando`, sem dado de pedido além do solicitante — o mesmo padrão de `EncerrarContratoComando`.

## Riscos

- **Histórico em memória:** reiniciar o programa (ou um erro não tratado) perde o que havia para desfazer. Aceito — é o escopo definido para esta sprint.
- **Remover um contrato diferente do que está no histórico:** removida o contrato que não é o do histórico não deveria limpar o histórico de outro contrato; como o caretaker tem um único espaço global, qualquer remoção limpa o que houver. Simplificação aceita: o requisito não pede rastrear a qual contrato o histórico pertence para esse caso.
