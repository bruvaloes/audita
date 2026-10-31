# Proposta: CRUD de contratos

## Por quê

O Audita existe para fiscalizar contratos terceirizados, mas hoje só gerencia usuários. Sem contratos não há a quem vincular fiscais e funcionários, e as evidências (sprints futuras) não têm a que se referir. A Sprint 3 pede o CRUD da entidade principal do domínio, relacionada a Usuário, e uma fachada única para os controles.

## O que muda

- Nova entidade **Contrato**, com cadastro, listagem (com busca, filtro e paginação), edição (inclusive encerramento), remoção e vínculo de fiscais e funcionários (RF 04 a RF 08).
- **Controle de acesso** nas operações de contrato: só o Gestor opera (RF 03).
- **Registro no log de auditoria** do cadastro, da edição, da remoção e dos vínculos (NF004).
- **Datas no padrão brasileiro** na interface e no log (NF006).
- **`FacadeSingletonController`**: fachada única (Facade + Singleton) para os controllers, com a consulta da quantidade de entidades cadastradas (RF 16).
- Persistência de contratos nos dois mecanismos (memória e SQLite), seguindo o ADR 0001.

## Capacidades

### Novas
- `contratos`: ciclo de vida do contrato e vínculo de usuários.
- `fachada`: ponto único de acesso aos controllers e contagem de entidades.

### Alteradas
- `usuarios`: sem mudança de requisito. O controller de usuários passa a ser acessado também pela fachada e a registrar o cadastro no log de auditoria.

## Fora do escopo

- Evidências e validação (RF 09 a RF 12): a entidade e os repositórios existem, mas as regras ficam para outra sprint.
- Leitura do arquivo do contrato por IA e geração de cronograma.
- Padrão Command na fachada (Sprint 5) e desfazer atualização (Sprint 5).
- Relatório de acessos (Sprint 4).

## Impacto

- Código: `entidade/contrato`, `persistencia/contrato_repositorio*`, `controle/contrato_controller`, validadores de contrato, `controle/utils/datas`, `fronteira/contrato_fronteira`, `controle/facade_singleton_controller`, `main.py`.
- Requisitos: RF 04 a RF 08, RF 16, NF001 de Usabilidade, NF003 e NF004 de Segurança, NF006 de Adequação a padrões.
