# 02 · Glossário

Termos do domínio do Audita. Os atributos, tamanhos e domínios das entidades ficam aqui para não se repetirem nos requisitos. Os tamanhos são uma proposta inicial da equipe e podem ser ajustados na modelagem de dados.

## Siglas

| Sigla | Descrição |
|-------|-----------|
| CGU | Controladoria-Geral da União |
| ERS | Especificação de Requisitos de Software |
| IA | Inteligência Artificial |
| LGPD | Lei Geral de Proteção de Dados (Lei nº 13.709/2018) |
| RF | Requisito Funcional |
| RN | Regra de Negócio |
| RNF / NF | Requisito Não Funcional |
| SLA | Service Level Agreement (acordo de nível de serviço) |
| SSG | Setor responsável pela gestão de contratos terceirizados na instituição |
| TCU | Tribunal de Contas da União |

## Usuário

Pessoa cadastrada que acessa o Audita mediante autenticação. Todo usuário tem exatamente um perfil de acesso, que define as funcionalidades liberadas.

| Atributo | Tamanho | Tipo | Domínio / regras |
|----------|---------|------|------------------|
| Identificador | — | Numérico | Gerado pelo sistema; único |
| Nome completo | até 100 | Texto | Obrigatório |
| CPF | 11 | Numérico | Informado com ou sem pontuação e gravado só com os números; dígitos verificadores corretos; todos os dígitos iguais é inválido; único |
| E-mail | até 100 | Texto | Formato `nome@dominio`, um único `@`, sem espaços; único |
| Login | 1 a 12 | Texto | Apelido do usuário; obrigatório; pode ter letras, espaços e símbolos, mas **não números**; único |
| Senha | 8 a 128 | Texto | Pelo menos 3 dos 4 tipos (maiúscula, minúscula, número, especial); diferente do login; guardada somente como hash |
| Perfil de acesso | 1 valor | Enumerado | `FUNCIONARIO` / `FISCAL` / `GESTOR` |
| Situação | 1 valor | Enumerado | `ATIVO` / `INATIVO` (exibida como Ativo / Inativo) |
| Aceite dos termos | — | Data e hora | Preenchido no cadastro; sem aceite o cadastro não é concluído |

## Perfil de acesso

Papel assumido pelo usuário no sistema. Determina as funcionalidades disponíveis.

- **Funcionário:** colaborador da empresa terceirizada que executa as tarefas e registra as evidências fotográficas.
- **Fiscal:** servidor público que acompanha presencialmente a execução do contrato. Todo contrato ativo deve ter ao menos um fiscal responsável.
- **Gestor:** servidor público responsável por cadastrar contratos, vincular usuários e validar evidências. É o responsável pela auditoria centralizada.

## Mecanismo de persistência

Forma de guardar os dados do sistema. Há dois, escolhidos no início da execução: **em memória** (volátil, os dados somem ao encerrar) e **SQLite** (os dados permanecem no arquivo `usuarios.db`).

## Termos de Uso e Política de Privacidade

Textos exibidos antes do aceite no cadastro, com finalidade do tratamento, dados coletados, tempo de conservação e canal para os direitos do titular (LGPD, art. 9º).

## Termos do restante do domínio

Estes termos aparecem nos requisitos, mas são especificados em sprints posteriores.

| Termo | Definição |
|-------|-----------|
| Contrato | Instrumento firmado entre o órgão público e a empresa terceirizada, cadastrado pelo gestor. |
| Evidência fotográfica | Fotografia que comprova a execução de uma atividade. |
| Atividade (tarefa) | Instância de uma obrigação de serviço a ser executada por um funcionário; só é concluída com uma evidência válida. |
| Validação manual | Processo em que o gestor aprova ou recusa uma evidência; a decisão é registrada e não pode ser alterada. |
| Chamado | Registro aberto pelo fiscal para relatar irregularidade ou necessidade de reposição (versão futura). |
| Preposto | Representante da empresa terceirizada; não opera o sistema, recebe notificações. |
| Log de auditoria | Registro imutável de uma ação crítica no sistema. |
