# Design: relatório de acessos

## Contexto

Cada tentativa de login gera um `Acesso` (usuário, perfil informado, data e hora e resultado), gravado pelo `AutenticacaoController` no repositório de acessos, em memória ou SQLite. O controle de acesso por perfil (`ControleAcesso` e `PERMISSOES_PADRAO`) já protege as operações de usuário e de contrato, e a fronteira chega aos controllers pela fachada (ADR 0002).

## Decisões

### 1. Template Method

`RelatorioAcessos` é uma classe abstrata com o método `gerar()`, que fixa a ordem dos passos:

1. `_coletar()`: lê os acessos pela interface `ConsultaAcessos` (só leitura, ISP);
2. `_calcular(acessos)`: monta as `EstatisticasAcessos`;
3. `_formatar(estatisticas)`: **abstrato**, converte as estatísticas no conteúdo do arquivo;
4. `_salvar(conteudo, gerado_em)`: grava o arquivo e devolve o caminho.

Cada formato implementa só `extensao` e `_formatar`. `RelatorioAcessosPdf` é a única classe que conhece a biblioteca de PDF. Os títulos e rótulos ficam no módulo da classe abstrata, para todos os formatos dizerem o mesmo.

**Alternativa descartada:** Strategy, com um formatador injetado. Também separa o formato, mas o enunciado da sprint pede o Template Method, e aqui o passo a passo é fixo: só um passo varia.

### 2. Estatísticas separadas do formato

`EstatisticasAcessos` é imutável e traz o total, a contagem por resultado e por perfil informado (com todas as chaves, mesmo com 0), o período (primeiro e último acesso) e a data de geração. Sucessos e falhas são derivados da contagem por resultado. A chave `None` em `por_perfil` conta as tentativas com perfil inválido, que o `Acesso` guarda como vazio.

### 3. Permissão no controller

`RelatorioController` confere `GERAR_RELATORIO_ACESSOS` no `ControleAcesso` antes de gerar. O painel só mostra a opção ao Gestor, mas a conferência no controller é o que garante o RN15.1 (NF003 de Segurança). O controller recebe o relatório pela classe abstrata e não conhece o formato: a escolha do PDF fica no `main.py`.

### 4. Arquivo gerado

O arquivo é salvo na pasta `relatorios/` da pasta de execução, com o nome `relatorio-acessos_dd-mm-aaaa_hh-mm-ss.<extensão>`. Os segundos evitam que dois relatórios do mesmo minuto se sobrescrevam. Falhas de gravação viram `EscritaPersistenciaError`, e a fronteira mostra "Erro de armazenamento", como nas outras telas. A pasta fica fora do Git.

### 5. Biblioteca de PDF

`fpdf2`: é Python puro e escreve com as fontes padrão do PDF (Helvetica, que cobre os acentos do português), sem arquivo de fonte no projeto. Nos testes, `pypdf` lê o texto do PDF gerado para conferir os números e o formato das datas.

**Alternativa descartada:** `reportlab`, mais completa, mas maior que o necessário para um relatório de uma página.

## Riscos

- **Formatos divergentes:** um formato novo pode esquecer um número. Mitigado com os rótulos comuns e o cálculo único em `EstatisticasAcessos`.
- **Volume:** o relatório lê todos os acessos de uma vez. No volume de referência isso é imediato; filtros por período ficam para quando forem pedidos.
