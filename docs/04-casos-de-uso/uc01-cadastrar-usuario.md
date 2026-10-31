# UC01 · Cadastrar usuário

| | |
|---|---|
| **Ator** | Usuário (visitante que ainda não tem conta) |
| **Requisito** | RF 01 |
| **Pré-condição** | O sistema está em execução, com um mecanismo de persistência escolhido |
| **Pós-condição (sucesso)** | O usuário existe com situação ATIVO, o aceite dos termos tem data e hora, e a senha está guardada só como hash |
| **Pós-condição (falha)** | Nenhum usuário é criado e o sistema continua no menu |

## Fluxo principal

1. O usuário escolhe "1 - Cadastrar usuário" no menu.
2. O sistema pede nome, CPF, e-mail, login, senha, confirmação da senha e perfil.
3. O usuário informa os dados (**Selecionar perfil de acesso**, incluído neste passo).
4. O sistema exibe o resumo dos Termos de Uso e da Política de Privacidade e pede o aceite.
5. O usuário responde "s" ou "sim".
6. O sistema valida os campos, grava o usuário (senha com hash) e exibe "Usuário cadastrado com sucesso!".

## Fluxos alternativos

| Passo | Condição | Resultado |
|-------|----------|-----------|
| 6 | Campo obrigatório vazio | "O campo '<campo>' é obrigatório." |
| 6 | Nome com mais de 100 caracteres | "Nome: use até 100 caracteres" |
| 6 | CPF com dígitos verificadores inválidos ou todos iguais | "CPF inválido" |
| 6 | CPF já cadastrado, em qualquer formato | "CPF já cadastrado" |
| 6 | E-mail fora do formato `nome@dominio` ou com mais de 100 caracteres | "E-mail: use o formato nome@dominio, com até 100 caracteres" |
| 6 | E-mail já cadastrado | "E-mail já cadastrado" |
| 6 | Login vazio, com mais de 12 caracteres ou com número | "Login: use até 12 caracteres, sem números" |
| 6 | Login já cadastrado | "Login já cadastrado" |
| 6 | Senha fora da política (8 a 128 caracteres, 3 dos 4 tipos) | "Senha: use 8 a 128 caracteres e 3 destes tipos: maiúscula, minúscula, número, especial" |
| 6 | Senha igual ao login | "Senha: não pode ser igual ao login" |
| 6 | Confirmação diferente da senha | "As senhas não coincidem" |
| 6 | Perfil que não existe | "Perfil: use um destes valores: GESTOR, FISCAL, FUNCIONARIO" |
| 5 | Resposta diferente de "s" ou "sim" | "Termos de Uso: aceite os Termos e a Política de Privacidade para concluir o cadastro" |
| 6 | Falha ao gravar | "Erro de armazenamento: <motivo>" |

Em todos os alternativos o sistema volta ao menu principal, sem encerrar.

## Regras de negócio

RN01.1 a RN01.11 do documento de requisitos. As regras completas, com cenários, estão em [`openspec/specs/usuarios`](../../openspec/specs/usuarios/spec.md).

## Tela

Veja o wireframe em [06-interface](../06-interface/README.md#tela-1--cadastro-de-usuário).
