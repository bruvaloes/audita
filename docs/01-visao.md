# 01 · Visão

## Motivação

A fiscalização de contratos terceirizados em órgãos públicos é hoje manual e subjetiva: depende do julgamento presencial do fiscal. A Lei nº 14.133/2021 exige que a execução dos contratos seja acompanhada e fiscalizada, mas o modelo atual não produz registros confiáveis dessa fiscalização.

Essa lacuna gera risco jurídico e financeiro, porque a falta de rastreabilidade dificulta comprovar irregularidades perante órgãos de controle como o TCU e a CGU. O Audita troca um processo baseado em percepção por um baseado em evidências verificáveis.

## Problemas

- Não há comprovação real da execução dos serviços; a fiscalização depende da percepção do fiscal.
- Faltas de colaboradores e tarefas não executadas não são registradas de forma sistemática.
- Órgãos públicos podem pagar por serviços que não foram prestados.
- A falta de rastreabilidade compromete a aplicação de penalidades e glosas.
- As obrigações dos contratos viram rotinas de trabalho manualmente, o que é lento e sujeito a erro.
- Não existe canal padronizado para relatar irregularidades nem para validar as evidências apresentadas.

## Visão do sistema

O Audita digitaliza a fiscalização de contratos públicos de serviços terceirizados (limpeza, conservação, manutenção). O produto completo se apoia em quatro pilares: geração do cronograma de atividades, execução das atividades pelo funcionário terceirizado, fiscalização presencial com chamados pelo fiscal e validação centralizada pelo gestor.

**Nesta etapa** o Audita é uma aplicação de console em Python, com menus e persistência em memória ou em SQLite. Ela entrega o núcleo essencial, e cada capacidade é especificada na sprint em que é implementada:

| Capacidade | Sprint | Onde está especificada |
|------------|--------|------------------------|
| Gerenciamento de usuários (cadastro com validação, listagem, persistência) | 1 e 2 | `openspec/specs/usuarios/` |
| CRUD de contratos | 3 | change `crud-contrato` |
| Relatórios de estatísticas de acesso | 4 | change `relatorio-de-acessos` |
| Desfazer a última atualização de contrato | 5 | change `desfazer-atualizacao` |

## Escopo negativo

O Audita **não** fará:

- **Aplicação automática de penalidades ou glosas.** O sistema fornece evidências e relatórios; a decisão é da autoridade competente.
- **Pagamento e gestão financeira dos contratos.** Medições, faturamento e pagamentos ficam nos sistemas financeiros do órgão.
- **Licitação e elaboração de contratos.** O Audita parte de um contrato já assinado.
- **Controle de ponto e folha de pagamento dos terceirizados.** É responsabilidade da empresa contratada.
- **Acesso direto do preposto e dos órgãos de controle.** Nesta versão eles só recebem notificações e relatórios, sem painel próprio.

## Usuários

| Perfil | Quem é | O que faz |
|--------|--------|-----------|
| Funcionário | Colaborador da empresa terceirizada | Executa as tarefas e registra evidências fotográficas |
| Fiscal | Servidor que acompanha a execução do contrato | Acompanha o contrato em campo e, em versão futura, abre chamados |
| Gestor | Servidor responsável pela gestão dos contratos | Cadastra contratos, vincula usuários, valida evidências e lista usuários |

Usuários indiretos: o **preposto** da empresa terceirizada e os **órgãos de controle** (TCU, CGU), que usam a trilha de evidências.

## Restrições

- **Legais:** Lei nº 14.133/2021 (registros de fiscalização) e LGPD (Lei nº 13.709/2018) no tratamento de CPF e e-mail.
- **Tecnologia desta etapa:** Python 3.10 ou superior, SQLite, `pytest` e interface de console.
- **Persistência substituível:** os dados ficam em memória ou em SQLite, escolhido no início da execução (veja [ADR 0001](adr/0001-persistencia-substituivel.md)).
- **Sem cliente:** não houve contato direto com o cliente; os requisitos partem do documento da coordenação e podem ser revistos após validação (veja [03-elicitacao](03-elicitacao.md)).

## Documentos relacionados

- Documento de Requisitos (PDF nesta pasta, `docs/documento_de_requisitos_*.pdf`)
- [Glossário](02-glossario.md)
- [Elicitação](03-elicitacao.md)
