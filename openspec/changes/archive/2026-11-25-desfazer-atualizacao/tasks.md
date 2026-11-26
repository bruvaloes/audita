# Tarefas: desfazer a última atualização de contrato

## 1. Memento
- [x] 1.1 `ContratoMemento` (dataclass imutável, `usuarios_vinculados` em tupla)
- [x] 1.2 `Contrato.criar_memento()` e `Contrato.restaurar(memento)`

## 2. Caretaker
- [x] 2.1 `HistoricoAtualizacaoContrato` com um único espaço (`salvar`, `obter`, `limpar`)

## 3. Controller
- [x] 3.1 Guardar o estado antes de mutar em `atualizar` (cobre `encerrar`), `vincular` e `desvincular`
- [x] 3.2 `desfazer_ultima_atualizacao`, incluindo o caso de renumeração
- [x] 3.3 `remover` limpa o histórico

## 4. Erro e controle de acesso
- [x] 4.1 `NadaParaDesfazerError`
- [x] 4.2 `Operacao.DESFAZER_ATUALIZACAO_CONTRATO` e permissão do Gestor

## 5. Fachada e interface
- [x] 5.1 `DesfazerUltimaAtualizacaoContratoComando` e método na fachada
- [x] 5.2 Método na `ContratoFronteira` e ação no painel (`main.py`)

## 6. Testes
- [x] 6.1 C1 a C11 (abaixo), nos dois repositórios onde fizer sentido (C9)
- [x] 6.2 Matriz de acesso cobre a nova operação (C8)
- [x] 6.3 `test_comandos.py` cobre o novo comando na fachada

## 7. Verificação e documentação
- [x] 7.1 Suíte completa passando
- [x] 7.2 Rodar o programa na mão (SQLite e memória)
- [x] 7.3 `openspec archive desfazer-atualizacao` (só depois de #25 e #26 mescladas na `dev`)

## Critérios de aceite
- [x] C1: desfaz a última edição, e os valores voltam
- [x] C2: desfaz o encerramento, e a situação volta a ATIVO
- [x] C3: desfaz vincular e desvincular usuário
- [x] C4: desfaz a renumeração: o número antigo volta e o novo deixa de existir
- [x] C5: só a última atualização é desfeita; um segundo desfazer responde "Nenhuma atualização para desfazer"
- [x] C6: uma nova atualização substitui a anterior no histórico
- [x] C7: remover o contrato limpa o histórico
- [x] C8: Funcionário e Fiscal recebem "Acesso negado" e nada muda
- [x] C9: funciona no repositório em memória e no SQLite
- [x] C10: o desfazer gera registro `EDICAO` no log
- [x] C11: o desfazer não cria um novo ponto de desfazer
- [x] C12: o histórico fica em memória e some ao reiniciar o programa (registrado no design e no spec)
