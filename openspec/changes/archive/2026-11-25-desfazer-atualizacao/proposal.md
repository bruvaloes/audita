# Proposta: desfazer a última atualização de contrato

## Por quê

Editar, encerrar, vincular ou desvincular usuário de um contrato muta o registro direto no repositório. Um engano — uma empresa digitada errada, um encerramento antes da hora, um vínculo feito no contrato errado — não tem volta hoje. A Sprint 5 pede o padrão **Memento** para desfazer, no mínimo, a última dessas atualizações.

## O que muda

- **Desfazer a última atualização do Contrato**, entendida como editar, encerrar, vincular e desvincular usuário. Um único nível de desfazer: só a atualização mais recente pode ser desfeita, e desfazer não é, por sua vez, desfazível.
- **Memento:** `Contrato` ganha `criar_memento()` e `restaurar(memento)`; `ContratoMemento` é uma cópia imutável dos valores (com `usuarios_vinculados` em tupla).
- **Caretaker:** `HistoricoAtualizacaoContrato`, com um único espaço guardado — uma nova atualização substitui o anterior, e remover o contrato limpa o histórico.
- **Nova operação** `DESFAZER_ATUALIZACAO_CONTRATO`, só do Gestor, com ação própria no painel.
- **Comando na fachada:** `DesfazerUltimaAtualizacaoContratoComando`, executado pelo `ExecutorComandos` da #25.

## Capacidades

### Alteradas
- `contratos`: ganha o requisito de desfazer a última atualização.
- `fachada`: ganha o comando de desfazer; esta change também registra o requisito da fachada baseada em Command (#25), que ainda não tinha sido escrito em nenhuma change anterior.

## Fora do escopo

- Histórico de mais de uma versão e refazer (redo).
- Persistir o histórico entre execuções: ele fica em memória e some ao reiniciar o programa.
- A implementação do Command na fachada em si (#25, já entregue) — só o registro do requisito.

## Impacto

- Código: `entidade/contrato.py`, novo `entidade/contrato_memento.py`, novo `controle/historico_atualizacao_contrato.py`, `controle/contrato_controller.py`, `excecao/validacao_error.py`, `controle/acesso/operacao.py` e `permissoes.py`, novo comando em `controle/comando/`, `controle/facade_singleton_controller.py`, `fronteira/contrato_fronteira.py`, `main.py`.
- Requisitos: novo RF de desfazer a última atualização de contrato, RN03.2 (permissão do Gestor), NF004 (log de auditoria).

## Texto para o documento de requisitos

**RF XX — Desfazer a última atualização de contrato**
O sistema deve permitir que o Gestor desfaça a última atualização feita em um contrato — edição de dados, encerramento, vínculo ou desvínculo de usuário —, voltando os valores ao estado anterior a essa atualização. Só a atualização mais recente pode ser desfeita; o sistema não mantém um histórico de várias versões, e desfazer não gera, por si, um novo ponto para desfazer.

**Caso de uso — Desfazer última atualização de contrato**
- **Ator principal:** Gestor.
- **Pré-condição:** existe uma atualização de contrato (edição, encerramento, vínculo ou desvínculo) desde o início do programa, ainda não desfeita.
- **Fluxo principal:**
  1. O Gestor escolhe "Desfazer última atualização de contrato" no painel.
  2. O sistema localiza o contrato afetado pela última atualização e restaura seus valores anteriores.
  3. O sistema confirma a restauração e registra a ação no log de auditoria.
- **Fluxo alternativo — nada para desfazer:** se não há atualização registrada (nenhuma ocorreu, ou a última já foi desfeita, ou o contrato foi removido depois), o sistema informa "Nenhuma atualização para desfazer" e nada muda.
- **Pós-condição:** o contrato volta ao estado anterior à última atualização; o histórico fica vazio até a próxima atualização.
