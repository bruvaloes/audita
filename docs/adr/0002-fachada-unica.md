# ADR 0002 · Fachada única (Facade + Singleton)

- **Status:** aceito
- **Data:** Sprint 3

## Contexto

Com o CRUD de contratos, a camada de fronteira passou a depender de vários controllers: autenticação, usuários e contratos. Cada tela precisaria conhecer e receber os controllers de que usa, e a composição em `main.py` ficaria espalhada. A Sprint 3 também pede um ponto único que informe a quantidade de entidades cadastradas.

## Decisão

Criar o `FacadeSingletonController`, que combina dois padrões:

- **Facade:** oferece uma interface única e simples sobre `AutenticacaoController`, `UsuarioController` e `ContratoController`. A fronteira passa a depender só da fachada, que delega cada operação ao controller correspondente. A fachada não tem regra de negócio própria.
- **Singleton:** garante uma única instância, para que todas as telas usem os mesmos controllers e repositórios. A instância é obtida por `obter_instancia()`, que sinaliza erro se a fachada ainda não foi criada, e `resetar_instancia()` serve para isolar os testes.

A fachada também responde a quantidade de entidades cadastradas (`contar_entidades()`, o total, e `contar_entidades_detalhado()`, o total e a quantidade de usuários, contratos e evidências).

A conferência de permissão continua nos controllers: nenhuma operação de usuário ou de contrato passa pela fachada sem ela. A única exceção, por decisão, é a contagem de entidades, que é pública: ela devolve só números agregados, sem dado pessoal, e o RF 16 não exige login. Se for preciso restringir, basta uma operação nova na matriz de permissões.

## Alternativas consideradas

- **Fronteiras recebendo cada controller (como antes):** simples, mas cada tela passa a conhecer vários controllers e a composição cresce a cada entidade nova.
- **Contêiner de injeção de dependência:** resolve a composição, mas é pesado demais para o tamanho do projeto.
- **Fachada sem Singleton:** funciona, mas permite várias instâncias com controllers diferentes. A Sprint 3 pede o Singleton explicitamente.

## Consequências

- Uma nova entidade entra na fronteira por um ponto só: o método da fachada.
- A fachada pode crescer demais; quando isso ocorrer, é preciso separá-la por área.
- O Singleton é estado global: os testes precisam chamar `resetar_instancia()` para não vazarem estado entre si.
- Na Sprint 5, a fachada passa a usar o padrão Command (ADR próprio), e esta decisão será revista.
