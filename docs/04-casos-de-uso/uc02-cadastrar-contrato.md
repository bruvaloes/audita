# UC02 · Cadastrar contrato

| | |
|---|---|
| **Ator** | Gestor |
| **Requisito** | RF 04 |
| **Pré-condição** | O gestor está autenticado e vê a opção "Cadastrar contrato" no painel (RF 03) |
| **Pós-condição (sucesso)** | O contrato existe com situação ATIVO, sem usuários vinculados, e há um registro `CADASTRO` no log de auditoria |
| **Pós-condição (falha)** | Nenhum contrato é criado |

## Fluxo principal

1. O gestor escolhe "Cadastrar contrato" no painel.
2. O sistema pede número, empresa contratada, vigência início, vigência fim e, opcionalmente, o caminho do arquivo.
3. O gestor informa os dados.
4. O sistema valida os dados, cria o contrato com situação ATIVO e grava o registro no log de auditoria.
5. O sistema exibe "Contrato cadastrado com sucesso!" e o contrato criado.

## Fluxos alternativos

| Passo | Condição | Resultado |
|-------|----------|-----------|
| 4 | Número ou empresa vazios, ou uma das datas vazia | O sistema indica o campo como obrigatório |
| 4 | Número com mais de 20 caracteres, ou empresa com mais de 150 | O sistema rejeita e informa o limite |
| 4 | Número já cadastrado | "Número de contrato já cadastrado" |
| 4 | Data em formato diferente de dd/mm/aaaa | O sistema rejeita e informa o formato |
| 4 | Fim anterior ao início | "A data de fim deve ser igual ou posterior à data de início" |
| 4 | Arquivo que não é PDF ou DOCX, ou com mais de 30 MB | O sistema recusa e informa o formato e o tamanho aceitos |
| 1 | O usuário não é Gestor | A opção não aparece no painel; se acionada, "Acesso negado" |
| 4 | Falha ao gravar | "Erro de armazenamento: <motivo>" |

Em todos os alternativos o contrato não é criado e o sistema volta ao painel.

## Regras de negócio

RN04.1 a RN04.5 do documento de requisitos. O contrato aparece na listagem do RF 05, ordenada pelo início da vigência, do mais recente para o mais antigo.

## Tela

Veja o wireframe em [06-interface](../06-interface/README.md#tela-3--cadastro-de-contrato).
