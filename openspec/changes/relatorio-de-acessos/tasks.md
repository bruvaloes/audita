# Tarefas: relatório de acessos

## 1. Controle de acesso
- [x] 1.1 Operação `GERAR_RELATORIO_ACESSOS` na matriz, só para o Gestor

## 2. Template Method
- [x] 2.1 `EstatisticasAcessos` com total, sucessos, falhas, contagem por resultado e por perfil
- [x] 2.2 Classe abstrata `RelatorioAcessos` com `gerar()` (coletar, calcular, formatar e salvar)
- [x] 2.3 Testes do passo a passo com um formato criado só no teste

## 3. Formato PDF
- [x] 3.1 `fpdf2` e `pypdf` em `requirements.txt`
- [x] 3.2 `RelatorioAcessosPdf` com datas em dd/mm/aaaa hh:mm
- [x] 3.3 Testes de C1, C2 e das datas (nenhuma em ISO), em memória e SQLite

## 4. Controller, fachada e interface
- [x] 4.1 `RelatorioController` com a conferência no `ControleAcesso`
- [x] 4.2 Fachada delegando a geração do relatório
- [x] 4.3 `RelatorioFronteira` e opção "Gerar relatório de acessos" no painel do Gestor
- [x] 4.4 Composição em `main.py`

## 5. Verificação e documentação
- [x] 5.1 Suíte completa passando
- [x] 5.2 Rodar o programa na mão (SQLite: login com falha, dois logins e o relatório)
- [x] 5.3 Projeto, arquitetura e README
- [ ] 5.4 `openspec archive relatorio-de-acessos`
