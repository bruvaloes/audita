# Proposta: relatório de acessos

## Por quê

Os gestores precisam saber como o sistema está sendo usado: quantas tentativas de login houve, quantas falharam e de quais perfis. Cada tentativa já é gravada como `Acesso` desde a autenticação (#56), mas nada consulta esses registros. A Sprint 4 pede mais um tipo de relatório (HTML ou PDF), aplicando o padrão Template Method; a equipe escolheu **PDF**. Requisito de origem: RF 15 da v2.0.

## O que muda

- **Relatório de estatísticas de acesso em PDF**, gerado pelo Gestor no painel, com o total de tentativas, sucessos e falhas, a quantidade por resultado e por perfil informado (RN15.3).
- **Template Method:** a classe abstrata `RelatorioAcessos` fixa o passo a passo (coletar, calcular, formatar e salvar), e a subclasse `RelatorioAcessosPdf` implementa o formato. Outro formato é outra subclasse (RN15.5).
- **Controle de acesso:** nova operação `GERAR_RELATORIO_ACESSOS`, só do Gestor, conferida no `RelatorioController` (RN15.1).
- **Datas no padrão brasileiro** no relatório, com a função `formatar_data_hora` da #18 (RN15.4).
- **Fachada:** passa a delegar a geração do relatório ao `RelatorioController`.
- **Dependência nova:** `fpdf2` para gerar o PDF; `pypdf` só nos testes, para ler o PDF gerado.

## Capacidades

### Novas
- `relatorios`: relatório de estatísticas de acesso.

### Alteradas
- `fachada`: sem mudança de requisito; ganha a operação de gerar o relatório.
- `usuarios`: sem mudança de requisito; o painel do Gestor ganha a opção "Gerar relatório de acessos".

## Fora do escopo

- Outros formatos, como HTML (a estrutura permite acrescentá-los depois).
- Dashboard web.
- Filtro por período ou por usuário.
- Bloqueio por tentativas (#57): o resultado `BLOQUEADO` aparece no relatório, sempre com 0 nesta etapa.

## Impacto

- Código: `controle/acesso` (operação e matriz), `controle/relatorio/`, `controle/relatorio_controller`, `controle/facade_singleton_controller`, `fronteira/relatorio_fronteira`, `main.py`.
- Dependências: `fpdf2` e `pypdf` em `requirements.txt`.
- Requisitos: RF 15, RF 03, NF003 de Segurança e NF006 de Adequação a padrões.
