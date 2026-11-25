# Tarefas: desfazer a última atualização de contrato

## 1. Memento
- [ ] 1.1 `ContratoMemento` (dataclass imutável, `usuarios_vinculados` em tupla)
- [ ] 1.2 `Contrato.criar_memento()` e `Contrato.restaurar(memento)`

## 2. Caretaker
- [ ] 2.1 `HistoricoAtualizacaoContrato` com um único espaço (`salvar`, `obter`, `limpar`)

## 3. Controller
- [ ] 3.1 Guardar o estado antes de mutar em `atualizar` (cobre `encerrar`), `vincular` e `desvincular`
- [ ] 3.2 `desfazer_ultima_atualizacao`, incluindo o caso de renumeração
- [ ] 3.3 `remover` limpa o histórico

## 4. Erro e controle de acesso
- [ ] 4.1 `NadaParaDesfazerError`
- [ ] 4.2 `Operacao.DESFAZER_ATUALIZACAO_CONTRATO` e permissão do Gestor

## 5. Fachada e interface
- [ ] 5.1 `DesfazerUltimaAtualizacaoContratoComando` e método na fachada
- [ ] 5.2 Método na `ContratoFronteira` e ação no painel (`main.py`)

## 6. Testes
- [ ] 6.1 C1 a C11 (abaixo), nos dois repositórios onde fizer sentido (C9)
- [ ] 6.2 Matriz de acesso cobre a nova operação (C8)
- [ ] 6.3 `test_comandos.py` cobre o novo comando na fachada

## 7. Verificação e documentação
- [ ] 7.1 Suíte completa passando
- [ ] 7.2 Rodar o programa na mão (SQLite e memória)
- [ ] 7.3 `openspec archive desfazer-atualizacao` (só depois de #25 e #26 mescladas na `dev`)

## Critérios de aceite
- [ ] C1: desfaz a última edição, e os valores voltam
- [ ] C2: desfaz o encerramento, e a situação volta a ATIVO
- [ ] C3: desfaz vincular e desvincular usuário
- [ ] C4: desfaz a renumeração: o número antigo volta e o novo deixa de existir
- [ ] C5: só a última atualização é desfeita; um segundo desfazer responde "Nenhuma atualização para desfazer"
- [ ] C6: uma nova atualização substitui a anterior no histórico
- [ ] C7: remover o contrato limpa o histórico
- [ ] C8: Funcionário e Fiscal recebem "Acesso negado" e nada muda
- [ ] C9: funciona no repositório em memória e no SQLite
- [ ] C10: o desfazer gera registro `EDICAO` no log
- [ ] C11: o desfazer não cria um novo ponto de desfazer
- [ ] C12: o histórico fica em memória e some ao reiniciar o programa (registrado no design e no spec)
