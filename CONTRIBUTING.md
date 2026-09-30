# Guia de Contribuição

Este documento define as práticas e convenções adotadas no projeto Audita. Todo membro da equipe deve segui-las.

---

## 1. Estratégia de branches principais

O repositório possui duas branches de longa duração. Nenhuma delas recebe commits diretos.

```
main ──────────────────────────────────────────────► produção
  ▲                                          ▲
  │  merge (release ou hotfix)               │ hotfix
  │                                          │
dev ───────────────────────────────────────► merge antes da release
  ▲         ▲          ▲
  │         │          │
feat/x   fix/y     refactor/z   ← branches de trabalho (curta duração)
```

### `main`

- Representa o estado **atual de produção/entrega**
- Todo commit em `main` é uma versão estável, correspondente a um marco do projeto
- Só recebe merges vindos de `dev` (via release) ou de `hotfix/*`
- Protegida: exige PR com pelo menos 1 aprovação e conversas resolvidas

### `dev`

- Branch de **integração contínua** — onde o trabalho da equipe converge
- Deve sempre estar em estado funcional
- Branches de feature, fix e refactor partem daqui e retornam aqui via PR
- Periodicamente promovida para `main` quando um conjunto de funcionalidades está pronto

### Fluxo resumido

```
1. Partir de dev
   git checkout dev && git pull
   git checkout -b feat/12-cadastro-contrato

2. Desenvolver com commits atômicos

3. Abrir PR de feat/12-... → dev
   (revisão, aprovação)

4. Merge em dev (squash ou merge commit — decisão do time)

5. Quando dev está pronta para virar entrega:
   PR dev → main
```

### Hotfix (bug crítico já entregue)

```
main → hotfix/99-descricao → PR para main  +  PR para dev
```

Um hotfix parte de `main`, é corrigido, e depois é integrado em `dev` também — para não perder a correção na próxima entrega.

---

## 2. Commits

### Formato (Conventional Commits)

```
<tipo>(<escopo>): <descrição curta no imperativo>

[corpo opcional — o quê e por quê, não como]

[rodapé opcional: refs à issue]
```

**Tipos permitidos:**

| Tipo       | Quando usar                                               |
|------------|-----------------------------------------------------------|
| `feat`     | Nova funcionalidade                                        |
| `fix`      | Correção de bug                                           |
| `refactor` | Mudança interna sem alterar comportamento externo         |
| `test`     | Adição ou correção de testes                              |
| `docs`     | Apenas documentação                                       |
| `chore`    | Configs, dependências — sem código de produção            |
| `style`    | Formatação, espaçamento — sem mudança de lógica           |
| `perf`     | Melhoria de performance                                   |
| `revert`   | Reverte um commit anterior                                |

**Escopo:** camada ou módulo afetado (`usuario`, `contrato`, `persistencia`, `auth`, `ci`, etc.).

**Exemplos válidos:**

```
feat(contrato): adicionar cadastro de contrato

fix(usuario): corrigir validação de CPF duplicado

refactor(persistencia): extrair interface de repositório

docs(readme): atualizar instruções de instalação
```

**Regras:**
- Descrição em **português**, no **imperativo** ("adicionar", não "adicionei" ou "adicionando")
- Máximo de **72 caracteres** na primeira linha
- Um commit = uma responsabilidade. Se precisar de "e" na descrição, considere dividir
- Commits de trabalho em progresso devem usar `wip:` e ser squashados antes do merge

---

## 3. Branches

```
<tipo>/<issue>-<descricao-curta>
```

```
feat/12-cadastro-contrato
fix/18-validacao-cpf
refactor/persistencia-repositorio
docs/atualizar-readme
```

**Regras:**
- Nunca commitar diretamente em `main` ou `dev`
- Branches de feature e fix partem de `dev` (ver seção 1)
- Hotfixes partem de `main` e são integrados em `main` e `dev`
- Delete a branch após o merge

---

## 4. Práticas de Clean Code

> Independentes de linguagem. Válidas para qualquer camada (fronteira, controle, entidade, persistência).

### 4.1 Nomes revelam intenção

```python
# ❌
d = 0
flag = True
def process(x): ...

# ✅
dias_ate_vencimento = 0
usuario_esta_ativo = True
def processar_evidencias_pendentes(evidencias): ...
```

- Nomes de **variáveis e funções**: descrevem *o que são* ou *o que fazem*
- Nomes de **classes**: substantivos (`Contrato`, `UsuarioRepositorio`)
- Nomes de **funções/métodos**: verbos (`calcular`, `validar`, `buscar`)
- Evite abreviações que exijam contexto mental (`usrRepo` → `usuario_repositorio`)
- Evite prefixos redundantes (`contrato.contrato_id` → `contrato.id`)

### 4.2 Funções fazem uma coisa

- Uma função cabe em uma tela sem scroll → suspeite se precisar de mais
- Se você precisar usar "e" para descrever o que ela faz, extraia
- Parâmetros: idealmente 0–2; 3 é o limite; acima disso, agrupe em objeto/dataclass

### 4.3 Não deixe comentários onde o código pode falar

```python
# ❌ Comentário que repete o código
# Verifica se o usuário é maior de idade
if usuario.idade >= 18: ...

# ✅ Nome que dispensa o comentário
if usuario.e_maior_de_idade(): ...
```

Comentários válidos: decisões de negócio não óbvias, workarounds com link para issue, advertências sobre efeitos colaterais.

### 4.4 Sem números mágicos ou strings soltas

```python
# ❌
if tentativas > 3: ...
status = "APROVADO"

# ✅
MAX_TENTATIVAS_LOGIN = 3
if tentativas > MAX_TENTATIVAS_LOGIN: ...
status = StatusEvidencia.APROVADO
```

### 4.5 Regra do Escoteiro

> Deixe o código *ligeiramente* melhor do que você encontrou.

Não é refactoring massivo — é renomear uma variável confusa, extrair um bloco repetido, remover um TODO resolvido.

### 4.6 Testes são cidadãos de primeira classe

- Todo bug corrigido ganha um teste que o reproduz antes do fix
- Nomes de teste descrevem o cenário: `deve_retornar_erro_quando_cpf_invalido`
- Um teste = um comportamento verificado
- Testes não devem depender de ordem de execução

---

## 5. Pull Requests

**Título:** mesmo formato de commit (`feat(contrato): adicionar edição de contrato`)

**Checklist antes de abrir o PR:**
- [ ] Testes passando localmente
- [ ] Nenhum `TODO` novo sem issue associada
- [ ] Documentação atualizada (se aplicável)

**Destino:** todo PR de feature, fix ou refactor é aberto para `dev` (nunca direto para `main`, exceto hotfix).

**Aprovação:** é necessária pelo menos **1 aprovação** de outro integrante antes do merge.

**Descrição:** deve conter `Closes #N`, com o número da issue que o PR resolve, para que ela seja fechada no merge.

**Tamanho:** PRs grandes são difíceis de revisar. Prefira PRs focados em uma única issue/funcionalidade.

---

## 6. Para Agentes IA

Ao atuar neste repositório, siga adicionalmente:

1. **Leia a issue e a documentação em `docs/`** antes de implementar — ali está o contexto e o escopo esperado
2. **Prefira edições cirúrgicas** a reescritas completas de arquivos existentes
3. **Documente suposições** no corpo do commit quando o requisito for ambíguo
4. **Não invente dependências** externas sem registrar no PR por que são necessárias
5. **Nunca altere o comportamento de um padrão de projeto já implementado** (Repository, Facade, etc.) sem justificar a mudança no PR