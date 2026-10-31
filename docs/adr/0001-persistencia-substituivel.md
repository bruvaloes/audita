# ADR 0001 · Persistência substituível

- **Status:** aceito
- **Data:** Sprint 2

## Contexto

Na Sprint 1 os usuários eram guardados numa coleção em memória. A Sprint 2 exige também um mecanismo permanente (arquivo ou banco), escolhido no início da execução. Novos mecanismos podem aparecer depois, e a regra de negócio não pode depender de nenhum deles.

## Decisão

Os repositórios ficam atrás de uma interface (`UsuarioRepositorio`), e a aplicação escolhe a implementação apenas na raiz de composição (`main.py`):

- `UsuarioRepositorioMemoria`: coleção em memória, volátil.
- `UsuarioRepositorioSQLite`: banco SQLite no arquivo `usuarios.db`, tabela `usuarios` com `UNIQUE` em CPF, e-mail e login.

A interface é dividida em duas, pelo princípio da segregação de interfaces:

- `ConsultaUsuarios`: `listar_todos`, `buscar_por_cpf` e `buscar_por_email`.
- `PersistenciaUsuarios`: `salvar`.

Quem só consulta (os validadores de unicidade) depende só de `ConsultaUsuarios`.

As falhas de E/S viram exceções de domínio (`PersistenciaError`, com `ConexaoPersistenciaError`, `LeituraPersistenciaError` e `EscritaPersistenciaError`), tratadas na fronteira com a mensagem `Erro de armazenamento: <motivo>`, sem encerrar o programa.

## Consequências

- Trocar o mecanismo é incluir uma implementação e uma entrada em `MECANISMOS_ARMAZENAMENTO`, sem mexer em controllers nem validadores.
- Os testes usam o repositório em memória; o contrato do repositório é testado nas duas implementações.
- Duas implementações precisam se comportar igual; a unicidade, por exemplo, é garantida pelo validador e pela restrição `UNIQUE` do SQLite.
- Quando surgirem outras entidades, cada uma terá o seu repositório com a mesma divisão.
