# Usuários

Gerenciamento de usuários do Audita: cadastro com validação, listagem e persistência substituível. É o núcleo essencial das Sprints 1 e 2.

## Purpose

Permitir que pessoas se cadastrem com um dos três perfis (Funcionário, Fiscal ou Gestor), que os dados sejam validados com mensagens claras e que possam ser guardados em memória ou em SQLite.

## Requirements

### Requirement: Cadastrar usuário

O sistema SHALL permitir criar um usuário informando nome, CPF, e-mail, login, senha, confirmação da senha, perfil e a resposta aos Termos de Uso e à Política de Privacidade. Todos os campos são obrigatórios, e os espaços no início e no fim são descartados. O usuário é criado com situação ATIVO e exatamente um perfil.

#### Scenario: Cadastro válido
- **WHEN** o visitante informa todos os campos com dados válidos e aceita os termos
- **THEN** o sistema cria o usuário com situação ATIVO
- **AND** exibe "Usuário cadastrado com sucesso!"

#### Scenario: Campo obrigatório vazio
- **WHEN** o nome está vazio
- **THEN** o sistema exibe "O campo 'nome' é obrigatório."
- **AND** a mesma forma vale para cpf, e-mail, senha e perfil

#### Scenario: Nome longo
- **WHEN** o nome tem mais de 100 caracteres
- **THEN** o sistema rejeita e exibe "Nome: use até 100 caracteres"

### Requirement: Regras do login

O login SHALL ser obrigatório, ter no máximo 12 caracteres, não conter números e ser único no sistema.

#### Scenario: Login com número
- **WHEN** o login é "ana2"
- **THEN** o sistema rejeita e exibe "Login: use até 12 caracteres, sem números"

#### Scenario: Login vazio
- **WHEN** o login está vazio
- **THEN** o sistema rejeita e exibe "Login: use até 12 caracteres, sem números"

#### Scenario: Login com mais de 12 caracteres
- **WHEN** o login tem 13 caracteres
- **THEN** o sistema rejeita e exibe "Login: use até 12 caracteres, sem números"

#### Scenario: Login já cadastrado
- **WHEN** já existe um usuário com o login informado
- **THEN** o sistema não cria o usuário e exibe "Login já cadastrado"

### Requirement: Regras da senha

A senha SHALL seguir a política padrão do AWS IAM: de 8 a 128 caracteres, com pelo menos 3 dos 4 tipos (maiúscula, minúscula, número e caractere especial), diferente do login e igual à confirmação. Os caracteres especiais aceitos são `! @ # $ % ^ & * ( ) _ + - = [ ] { } | '`. Letra acentuada e espaço não contam como tipo de caractere.

#### Scenario: Senha com menos de 8 caracteres
- **WHEN** a senha tem menos de 8 caracteres
- **THEN** o sistema rejeita e exibe "Senha: use 8 a 128 caracteres e 3 destes tipos: maiúscula, minúscula, número, especial"

#### Scenario: Senha com mais de 128 caracteres
- **WHEN** a senha tem mais de 128 caracteres
- **THEN** o sistema rejeita com a mesma mensagem

#### Scenario: Senha com menos de 3 tipos
- **WHEN** a senha é "abcdefgh1" (apenas minúscula e número)
- **THEN** o sistema rejeita com a mesma mensagem

#### Scenario: Senha com exatamente 3 tipos
- **WHEN** a senha é "Abcdefg1" (maiúscula, minúscula e número)
- **THEN** o sistema aceita

#### Scenario: Senha igual ao login
- **WHEN** a senha é idêntica ao login
- **THEN** o sistema rejeita e exibe "Senha: não pode ser igual ao login"

#### Scenario: Confirmação diferente
- **WHEN** a confirmação difere da senha
- **THEN** o sistema exibe "As senhas não coincidem"

### Requirement: Regras do CPF e do e-mail

O CPF SHALL ter 11 dígitos com dígitos verificadores corretos, ser informado com ou sem pontuação, ser gravado só com os números e ser único. O e-mail SHALL ter o formato `nome@dominio`, no máximo 100 caracteres, sem espaços, e ser único.

#### Scenario: CPF inválido
- **WHEN** o CPF tem dígitos verificadores incorretos ou todos os dígitos iguais
- **THEN** o sistema rejeita e exibe "CPF inválido"

#### Scenario: CPF em outro formato
- **WHEN** já existe o CPF 52998224725 e o visitante informa 529.982.247-25
- **THEN** o sistema rejeita e exibe "CPF já cadastrado"

#### Scenario: E-mail inválido
- **WHEN** o e-mail não tem @, não tem texto antes ou depois do @, tem espaço ou passa de 100 caracteres
- **THEN** o sistema rejeita e exibe "E-mail: use o formato nome@dominio, com até 100 caracteres"

#### Scenario: E-mail já cadastrado
- **WHEN** já existe um usuário com o e-mail informado
- **THEN** o sistema não cria o usuário e exibe "E-mail já cadastrado"

### Requirement: Perfil e aceite dos termos

O perfil SHALL ser FUNCIONARIO, FISCAL ou GESTOR, aceito sem diferenciar maiúsculas de minúsculas. O cadastro SHALL exigir a resposta "s" ou "sim" aos Termos de Uso e à Política de Privacidade, e a data e hora do aceite SHALL ser gravada.

#### Scenario: Perfil inválido
- **WHEN** o perfil não é FUNCIONARIO, FISCAL nem GESTOR
- **THEN** o sistema rejeita e exibe "Perfil: use um destes valores: GESTOR, FISCAL, FUNCIONARIO"

#### Scenario: Termos não aceitos
- **WHEN** a resposta aos termos não é "s" nem "sim"
- **THEN** o cadastro não é concluído
- **AND** o sistema exibe "Termos de Uso: aceite os Termos e a Política de Privacidade para concluir o cadastro"

### Requirement: Listar usuários

O sistema SHALL listar todos os usuários cadastrados, na ordem do cadastro, com as colunas ID, Nome, E-mail, Perfil e Situação. O CPF e a senha NÃO SHALL ser exibidos. A lista termina com "Total: N usuário(s)".

#### Scenario: Lista com usuários
- **WHEN** existem 2 usuários e a listagem é pedida
- **THEN** o sistema mostra as 2 linhas e "Total: 2 usuário(s)"

#### Scenario: Lista vazia
- **WHEN** não há usuários
- **THEN** o sistema exibe "Nenhum usuário cadastrado."

### Requirement: Persistência substituível

O sistema SHALL guardar os usuários em dois mecanismos, em memória ou em SQLite, escolhidos no início da execução. A regra de negócio NÃO SHALL depender do mecanismo escolhido (veja o ADR 0001).

#### Scenario: Escolha do mecanismo
- **WHEN** o sistema inicia e o usuário escolhe 1 ou 2
- **THEN** o sistema exibe "Usando: Banco de dados (SQLite)" ou "Usando: Em memória"

#### Scenario: Opção inválida
- **WHEN** o usuário digita uma opção que não existe
- **THEN** o sistema exibe "Opção inválida. Tente novamente." e pergunta de novo

#### Scenario: Dados preservados no SQLite
- **WHEN** o usuário foi cadastrado com o SQLite e o programa é reiniciado com o SQLite
- **THEN** o usuário continua listado

#### Scenario: Dados perdidos em memória
- **WHEN** o usuário foi cadastrado em memória e o programa é reiniciado
- **THEN** a lista começa vazia

## Requisitos não funcionais ligados aos usuários

### Requirement: A senha nunca é exibida

A senha NÃO SHALL aparecer em listagens, mensagens de erro, logs nem na representação textual do usuário. Depois do cadastro ela SHALL ser guardada somente como hash (Argon2id, com salt aleatório por senha), nunca em texto aberto.

#### Scenario: Representação do usuário
- **WHEN** um usuário é impresso (`str` ou `repr`)
- **THEN** a senha não aparece na saída

#### Scenario: Senha gravada
- **WHEN** um usuário é cadastrado
- **THEN** o valor guardado começa com `$argon2id$` e não contém a senha digitada

### Requirement: Falha de armazenamento tratada

Falhas de leitura ou gravação SHALL virar exceções de domínio, ser tratadas na fronteira com a mensagem "Erro de armazenamento: <motivo>" e NÃO SHALL encerrar o programa.

#### Scenario: Banco indisponível na gravação
- **WHEN** o SQLite não consegue gravar o novo usuário
- **THEN** o sistema exibe "Erro de armazenamento: <motivo>"
- **AND** o programa continua no menu

#### Scenario: Banco não abre no início
- **WHEN** o SQLite não pode ser aberto na escolha do mecanismo
- **THEN** o sistema exibe a mensagem do erro e "Escolha outro mecanismo de armazenamento."
- **AND** pergunta de novo

### Requirement: Mensagens de validação com campo e regra

Cada mensagem de validação SHALL dizer qual campo e qual regra foram violados.

#### Scenario: Mensagem de validação
- **WHEN** qualquer validação do cadastro falha
- **THEN** a mensagem exibida nomeia o campo e a regra violada
