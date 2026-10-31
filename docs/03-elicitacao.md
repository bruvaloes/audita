# 03 · Elicitação de requisitos

A elicitação do Audita não pôde contar com entrevistas diretas com o cliente final. Ela partiu do documento prévio de escopo da coordenação do projeto, complementado por duas técnicas. Os requisitos foram priorizados pelo impacto direto na integridade da fiscalização, pela exigência legal e pela viabilidade técnica dentro do prazo.

## Técnica 1: análise de documentos

Leitura detalhada do documento prévio de escopo (apresentação entregue pela professora e coordenadora) para levantar necessidades funcionais, atores e o contexto da fiscalização de contratos terceirizados. Também foram consultadas a Lei nº 14.133/2021 e a LGPD, para identificar requisitos legais.

| Item | Registro |
|------|----------|
| Data | maio a agosto de 2026 |
| Local | Centro de Informática |
| Participantes | Bruna Valões, Larissa Donato |
| Fonte | Apresentação de escopo da professora; Lei nº 14.133/2021; Lei nº 13.709/2018 |
| Justificativa | Sem acesso ao cliente, o documento prévio era a principal fonte sobre as necessidades do sistema; a análise documental extrai requisitos de forma sistemática de material já existente. |
| Resultado | Levantamento inicial dos perfis de usuário, das funcionalidades principais e dos requisitos legais aplicáveis. |

## Técnica 2: brainstorming

Sessões de discussão em grupo para definir os pilares funcionais do sistema a partir do documento de escopo. Cada integrante propôs funcionalidades e restrições, depois agrupadas, discutidas e priorizadas pela equipe.

| Item | Registro |
|------|----------|
| Data | maio a agosto de 2026 |
| Local | Remoto, via Discord |
| Participantes | Bruna Valões, Larissa Donato |
| Fonte | Equipe de desenvolvimento |
| Justificativa | A técnica gera muitas ideias em pouco tempo e ajudou a preencher lacunas do documento prévio, como o modo offline, a validação automática de metadados e os lembretes ao funcionário. |
| Resultado | Definição dos quatro pilares do sistema (cronograma, execução pelo funcionário, fiscalização com chamados e validação pelo gestor) e da lista de requisitos funcionais e não funcionais. |

## Validação

Não houve contato direto com o cliente em nenhum marco do projeto. A validação foi interna, por revisão em grupo (walkthrough) de cada requisito, e pelo registro formal dos apontamentos da coordenação, tratados como principal insumo de validação externa.

Pontos que dependem de validação com o cliente: o volume de referência dos requisitos de desempenho, o autocadastro com escolha de perfil, o uso do login (apelido) junto com CPF e e-mail na autenticação, as regras de bloqueio de login e a proibição de remover contratos com evidências.
