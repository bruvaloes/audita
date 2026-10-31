# UC03 · Vincular usuário a contrato

| | |
|---|---|
| **Ator** | Gestor |
| **Requisito** | RF 08 |
| **Pré-condição** | O gestor está autenticado; existem um contrato e um usuário ATIVO com perfil FISCAL ou FUNCIONARIO |
| **Pós-condição (sucesso)** | O usuário passa a constar entre os vinculados do contrato; um funcionário vinculado passa a ver o contrato |
| **Pós-condição (falha)** | Os vínculos do contrato não mudam |

## Fluxo principal

1. O gestor escolhe "Vincular usuário a contrato" no painel.
2. O sistema pede o número do contrato e o ID do usuário.
3. O gestor informa os dois valores (o ID aparece em "Listar usuários").
4. O sistema confere que o contrato existe e que o usuário está ATIVO e tem perfil FISCAL ou FUNCIONARIO.
5. O sistema grava o vínculo e exibe "Usuário <id> vinculado ao contrato <número> com sucesso!".

Um usuário pode estar vinculado a mais de um contrato (RN08.3). Vincular de novo o mesmo usuário não duplica o vínculo.

## Fluxos alternativos

| Passo | Condição | Resultado |
|-------|----------|-----------|
| 4 | ID que não é número | "ID inválido. Informe um número inteiro." |
| 4 | Contrato inexistente | "Contrato '<número>' não encontrado" |
| 4 | Usuário inexistente | "Usuário id=<id> não encontrado" |
| 4 | Usuário INATIVO | "Usuário inativo não pode ser vinculado a contrato" |
| 4 | Usuário com perfil GESTOR | "Perfil não pode ser vinculado a contrato" |
| 1 | O usuário não é Gestor | A opção não aparece no painel; se acionada, "Acesso negado" |

### Desvincular usuário

1. O gestor escolhe "Desvincular usuário de contrato" e informa o contrato e o ID.
2. Se o usuário for o **único fiscal** de um contrato ATIVO, o sistema recusa com "O contrato deve ter ao menos um fiscal" (RN08.2).
3. Caso contrário, o vínculo é removido.

## Regras de negócio

RN08.1 a RN08.4 do documento de requisitos. A listagem filtrada por funcionário (RN08.4) mostra só os contratos aos quais ele está vinculado.

## Tela

Veja o wireframe em [06-interface](../06-interface/README.md#tela-4--vincular-usuário-a-contrato).
