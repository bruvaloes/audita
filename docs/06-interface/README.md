# 06 · Interface

O Audita, nesta etapa, é uma aplicação de **console**. Os wireframes abaixo mostram as telas como o usuário as vê no terminal: menus numerados, perguntas em sequência e mensagens de erro depois do envio. O texto é o do sistema; o que aparece depois de `>` é o que o usuário digita.

Convenções do console:
- `0 - Sair` (ou `0 - Voltar`) fecha o menu atual.
- Opção inválida: "Opção inválida. Tente novamente."
- Erros de validação: "Erro ao cadastrar: <mensagem>" (usuário) e "Erro ao cadastrar contrato: <mensagem>" (contrato).
- Falha de armazenamento: "Erro de armazenamento: <motivo>", sem encerrar o programa.

Casos de uso relacionados: [UC01](../04-casos-de-uso/uc01-cadastrar-usuario.md), [UC02](../04-casos-de-uso/uc02-cadastrar-contrato.md) e [UC03](../04-casos-de-uso/uc03-vincular-usuario-contrato.md).

## Tela 0 · Escolha do armazenamento e menu principal

```
===== CONFIGURAÇÃO DE PERSISTÊNCIA =====
1 - Banco de dados (SQLite)
2 - Em memória
Escolha o mecanismo de armazenamento: > 1
Usando: Banco de dados (SQLite)

===== GERENCIAMENTO DE USUÁRIOS =====
1 - Cadastrar usuário
2 - Ver Termos de Uso e Política de Privacidade
3 - Entrar (login)
0 - Sair
Escolha uma opção: >
```

## Tela 1 · Cadastro de usuário

Caso de uso: [UC01](../04-casos-de-uso/uc01-cadastrar-usuario.md).

```
--- Cadastro de Usuário ---
Nome: > Maria Souza
CPF (11 dígitos, com ou sem pontuação): > 529.982.247-25
E-mail: > maria@email.com
Login: > maria
Senha: > Senha@123
Confirme a senha: > Senha@123
Perfis disponíveis: GESTOR, FISCAL, FUNCIONARIO
Perfil: > GESTOR

<resumo dos Termos de Uso e da Política de Privacidade>
Aceita os Termos de Uso e a Política de Privacidade? (s/n): > s

Usuário cadastrado com sucesso!
   [GESTOR] Maria Souza - E-mail: maria@email.com (Ativo)
```

Com erro de validação, o menu principal volta depois da mensagem:

```
Aceita os Termos de Uso e a Política de Privacidade? (s/n): > s

Erro ao cadastrar: Login: use até 12 caracteres, sem números
```

## Tela 2 · Painel do Gestor

Aparece depois do login (opção 3 do menu principal). Só as ações que o perfil pode executar são mostradas.

```
===== PAINEL DO GESTOR =====
Bem-vindo(a), Maria Souza.
1 - Listar usuários
2 - Cadastrar contrato
3 - Listar contratos
4 - Editar contrato
5 - Encerrar contrato
6 - Remover contrato
7 - Vincular usuário a contrato
8 - Desvincular usuário de contrato
0 - Sair
Escolha uma opção: >
```

Os painéis do Funcionário e do Fiscal mostram apenas `0 - Sair`, por enquanto.

```
===== PAINEL DO FISCAL =====
Bem-vindo(a), Carlos Lima.
0 - Sair
Escolha uma opção: >
```

## Tela 3 · Cadastro de contrato

Caso de uso: [UC02](../04-casos-de-uso/uc02-cadastrar-contrato.md).

```
--- Cadastro de Contrato ---
Número do contrato (até 20 caracteres): > CT-2026-001
Empresa contratada: > Limpeza Brasil Ltda
Vigência início (dd/mm/aaaa): > 01/01/2026
Vigência fim (dd/mm/aaaa): > 31/12/2026
Caminho do arquivo (PDF ou DOCX até 30 MB, opcional): >

Contrato cadastrado com sucesso!
   <dados do contrato>
```

Com erro:

```
Vigência fim (dd/mm/aaaa): > 31/12/2025

Erro ao cadastrar contrato: A data de fim deve ser igual ou posterior à data de início
```

## Tela 4 · Vincular usuário a contrato

Caso de uso: [UC03](../04-casos-de-uso/uc03-vincular-usuario-contrato.md).

```
--- Vincular Usuário ao Contrato ---
Número do contrato: > CT-2026-001
ID do usuário a vincular (fiscal ou funcionário): > 3

Usuário 3 vinculado ao contrato CT-2026-001 com sucesso!
```

Com erro:

```
ID do usuário a vincular (fiscal ou funcionário): > 1

Erro ao vincular usuário: Perfil não pode ser vinculado a contrato
```

## Tela 5 · Listar contratos

```
--- Listagem de Contratos ---
Termo de busca por número ou empresa (ou Enter para todos): >
Filtro de situação (ATIVO, ENCERRADO ou Enter para todos): >

Número             Empresa                      Vigência                  Situação
-------------------------------------------------------------------------------------
CT-2026-001        Limpeza Brasil Ltda          01/01/2026 até 31/12/2026 ATIVO

Total: 1 contrato(s) | Página 1 de 1
```

A listagem mostra 20 contratos por página, do início de vigência mais recente para o mais antigo. Com mais de uma página, aparece a navegação: `P` próxima, `A` anterior, `V` voltar ao menu.
