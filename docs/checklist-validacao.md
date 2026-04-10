# Checklist de Validação — Portal DREA

> Lista de verificação manual para validar uma release do Portal DREA antes de distribuição ou após mudanças estruturais

**Versão do checklist:** `v2.0` · **Para o Portal DREA:** `v2.0.0-alpha.2` e superior

---

## Como usar este checklist

- Imprime ou preenche digitalmente
- Corre este checklist **antes** de qualquer release ao IT do aeroporto
- Corre este checklist **depois** de uma instalação nova num PC
- Corre este checklist **sempre** que uma mudança estrutural significativa for aplicada (ex: etapa nova do plano, refactor grande, fusão de branches)

**Data de execução:** ________________
**Versão testada:** Portal DREA `v_______________`
**Testado por:** ________________________
**Aeroporto configurado:** ________________

---

## Bloco 1 — Build e sintaxe (automático)

Antes de testar manualmente, corre os builds e confirma que passam sintacticamente.

- [ ] `python scripts/build-all.py` → ambos os targets **OK**
- [ ] Portal COE: **18 blocks / 0 errors**
- [ ] Portal SSCI: **7 blocks / 0 errors**
- [ ] Sem warnings Python inesperados no output do build
- [ ] Ficheiros de output existem:
  - [ ] `packages/portal-coe/dist/Portal_COE_AWM.html` (3.7–4 MB)
  - [ ] `packages/portal-ssci/dist/Portal_PSCI_AWM.html` (1.4–1.6 MB)

---

## Bloco 2 — Portal COE — Abertura e login

Abre `packages/portal-coe/dist/Portal_COE_AWM.html` num browser moderno (Edge/Chrome/Firefox).

- [ ] Página carrega sem erros visíveis
- [ ] Título da janela mostra "Portal COE — [Nome do aeroporto]"
- [ ] Aparece ecrã de **Login de Operador** com logo SGA centrado
- [ ] Campo de nome do operador aceita texto
- [ ] Dropdown de função funciona e mostra opções
- [ ] Botão **Entrar** funciona
- [ ] Após login, vai para o **Dashboard**

---

## Bloco 3 — Portal COE — Sidebar e navegação

- [ ] Sidebar à esquerda mostra os 4 grupos: **PRINCIPAL**, **OCORRÊNCIAS**, **DOCUMENTAÇÃO**, **SISTEMA**
- [ ] Grupo **PRINCIPAL** tem: Dashboard, Ocorrência, Contactos, ✓ Verificação Mensal, Mapas Quadrícula, Fluxogramas
- [ ] Grupo **OCORRÊNCIAS** tem: Emergência GUIA, Emergência FICHAS, Segurança GUIA, Segurança FICHAS (com barras coloridas ao lado)
- [ ] Grupo **DOCUMENTAÇÃO** tem: PEA/PCA/PSA, Referências
- [ ] Grupo **SISTEMA** tem: ❓ Guia Rápido, ⚙ Configurações
- [ ] **Footer de versão** na base da sidebar mostra:
  - [ ] "Portal COE"
  - [ ] versão semântica correcta (ex: `v2.0.0-alpha.2`)
  - [ ] data de build (YYYY-MM-DD)
  - [ ] OACI · operador (ex: `FNMO · SGA`)
- [ ] Clicar em cada item da sidebar abre a secção correspondente
- [ ] Item activo fica destacado

---

## Bloco 4 — Portal COE — Secção Contactos

- [ ] Clica em **Principal → Contactos**
- [ ] Aparecem **26 contactos** organizados em 5 grupos (SGA Internas, ENNA, Segurança/Ordem, Externas, Operadores)
- [ ] Cada card mostra: ID, Entidade, Nome, Função, CISCO (se aplicável), Celular, Email (se aplicável)
- [ ] Campos CISCO/Celular aparecem em fonte monospace
- [ ] Botão **🔄 Actualizar** no topo funciona (re-renderiza os cards)
- [ ] Ctrl+P imprime a secção correctamente (sem cortar cards)

---

## Bloco 5 — Portal COE — Editor de contactos

- [ ] Clica em **Sistema → Configurações**
- [ ] Tab **📇 Contactos** está activo por defeito
- [ ] Tabela mostra 26 linhas com todos os campos editáveis
- [ ] Pesquisa por "Esperança" filtra para 1 linha (Esperança Vasco, SSCI)
- [ ] Pesquisa por "SPCB" filtra para 1 linha
- [ ] Filtro de categoria "ENNA" filtra para 3 linhas (TWR, AIS, Meteo)
- [ ] Limpar filtro volta a mostrar 26
- [ ] Editar um campo (ex: celular do Director) + clicar **💾 Guardar Alterações** → aparece toast "contactos guardados"
- [ ] Voltar à secção Contactos mostra o novo valor
- [ ] Voltar ao editor mostra o valor editado
- [ ] Botão **+ Adicionar** cria linha nova com ID auto-gerado
- [ ] Botão **✕** numa linha pede confirmação e remove após confirmar
- [ ] Clicar **🏢 Dados Aeroporto** abre o tab de configurações do aeroporto
- [ ] Tab **👤 Operadores COE** continua funcional
- [ ] Botão **⬇ Exportar JSON** descarrega um ficheiro
- [ ] Botão **⬆ Importar JSON** aceita um JSON válido

---

## Bloco 6 — Portal COE — Ocorrência / EFB

- [ ] Clica em **Principal → Ocorrência**
- [ ] Aparece a secção do cronómetro
- [ ] Selecciona "Emergência Aeronáutica" como tipo de ocorrência
- [ ] O **EFB** (Emergency Form Block) aparece com todos os campos esperados:
  - [ ] Identificação (Nº Ocorrência, Hora Notificação, Nº Voo, Tipo Aeronave)
  - [ ] Declaração piloto (MAYDAY, PAN-PAN, Squawk 7700, Nenhuma)
  - [ ] Tempos (ETA, minutos até, hora TWR, nível)
  - [ ] Fase do voo, RWY, altitude, distância
  - [ ] Origem, destino
  - [ ] Natureza específica (chips)
  - [ ] POB, meteo, notas
- [ ] Ao clicar num chip de natureza específica, ele fica marcado com ✓
- [ ] Ao clicar num botão de declaração (MAYDAY, etc.), ele fica destacado
- [ ] Preencher alguns campos e iniciar o cronómetro funciona

---

## Bloco 7 — Portal COE — Guias de ocorrência

- [ ] Clica em **Ocorrências → ✈ Emergência → GUIA**
- [ ] Aparece **cartão de acção imediata** vermelho no topo
- [ ] 3 botões grandes: 🕐 Cronómetro, 📋 Formulário EFB, 📞 Contactos TWR
- [ ] Quadro de 3 níveis (Alerta Local / Alerta Completo / Acidente) visível
- [ ] 4 cards accordion **Fase 1/2/3/4** — clicar abre/fecha
- [ ] Card de referências rápidas no fim com 4 botões
- [ ] Os botões de referência navegam para a secção correcta
- [ ] Clica em **Ocorrências → 🛡 Segurança → GUIA**
- [ ] Banner **RESTRITO AVSEC** visível
- [ ] Cartão de acção imediata âmbar
- [ ] Aviso sobre comunicação em código destacado
- [ ] 4 fases AVSEC (Recepção, Activação, Busca, Resolução)
- [ ] FRM-FNMO-AB-001 com 10 perguntas presente

---

## Bloco 8 — Portal COE — Fluxogramas

- [ ] Clica em **Principal → Fluxogramas**
- [ ] Aparece o fluxo de **Emergência Aeronáutica**
- [ ] Cada nó de entidade mostra o nome + telefone formatado correctamente
- [ ] Os telefones correspondem aos contactos do aeroporto
- [ ] Edita um contacto em Configurações (ex: mudar celular do COE/Rui Fernandes)
- [ ] Volta aos Fluxogramas → o nó do COE mostra o novo número
- [ ] Clica para alternar para fluxo **Segurança** — funciona
- [ ] Mesmo comportamento no fluxo de segurança

---

## Bloco 9 — Portal COE — Verificação Mensal

- [ ] Clica em **Principal → ✓ Verificação Mensal**
- [ ] Selector de mês no topo está presente e aceita input
- [ ] Tabela mostra 26 entidades
- [ ] Para cada entidade, aparecem: ID, categoria, label, nome, CISCO, celular
- [ ] 4 chips de status por linha (Atendeu / Não atendeu / Nº errado / Actualizado)
- [ ] Clicar num chip marca-o e regista o timestamp
- [ ] Campo de "novo telefone" aceita input
- [ ] Cards de estatísticas no topo actualizam ao marcar chips
- [ ] Botão **💾 Gravar Mês** funciona (toast de sucesso)
- [ ] Histórico mostra o mês gravado
- [ ] Botão **📄 Exportar PDF** abre uma janela de impressão com o relatório formatado

---

## Bloco 10 — Portal COE — Documentação

- [ ] Clica em **Documentação → PEA/PCA/PSA**
- [ ] Aparecem cards: PEA, PSCI, PCA, PSA, MOA
- [ ] Clicar em **📖 Ver documento** no PEA abre o PDF embutido
- [ ] Clicar em **📂 Abrir PDF** no PCA/PSA/MOA abre o picker de ficheiros
- [ ] Clica em **Documentação → Referências** — aparece info ANAC

---

## Bloco 11 — Portal SSCI — Abertura e sidebar

Abre `packages/portal-ssci/dist/Portal_PSCI_AWM.html` num browser.

- [ ] Página carrega sem erros
- [ ] Título mostra "Portal PSCI — SSCI [Nome do aeroporto]"
- [ ] Header lateral mostra "Centro de Operações de Emergência" (ou título equivalente)
- [ ] Header subtitle mostra o nome completo do aeroporto
- [ ] Sidebar à esquerda mostra secções: Dashboard, Mapas, Registo Serviço, Inspecções, Testes, Avarias, Combustível, Tempo Resposta, Presença, Stock, Checklists, Ajuda, Configurações
- [ ] **Footer de versão** na base da sidebar mostra Portal SSCI + versão + data + OACI
- [ ] Clicar em cada item funciona

---

## Bloco 12 — Portal SSCI — Secções operacionais

- [ ] **Registo de Serviço**: formulário abre, campos funcionam
- [ ] **Inspecção W01 / W02**: checklists aparecem com items marcáveis
- [ ] **Inspecção Eqp. Resgate W01/W02**: checklists funcionais
- [ ] **Teste Comunicações**: secção carrega
- [ ] **Avaria Equipamento**: formulário aceita input
- [ ] **Abastecimento VCI**: secção funcional
- [ ] **Tempo Resposta**: formulário abre
- [ ] **Lista Presença**: secção carrega
- [ ] **Controlo de Estoque**: tabela de stock aparece
- [ ] **CheckList COE / PCM**: checklists funcionais

---

## Bloco 13 — Portal SSCI — Configurações

- [ ] Vai a **Configurações**
- [ ] Secções de configuração abrem
- [ ] Botões de guardar/exportar/importar presentes e funcionais

---

## Bloco 14 — Portais: comportamentos transversais

- [ ] **Modais**: clicar num botão que abre um modal (ex: Limpar Ocorrência) mostra overlay centrado
- [ ] **Modal focus trap**: dentro de um modal, Tab navega apenas entre os botões do modal
- [ ] **Modal Esc**: pressionar Esc fecha o modal
- [ ] **Save badge**: ao guardar algo, aparece badge no canto inferior direito "Guardado" e desaparece após 2.8s
- [ ] **Toasts**: mensagens temporárias aparecem e desaparecem
- [ ] **Skip link**: Tab logo após abrir a página mostra "Saltar para conteúdo principal"
- [ ] **Impressão** (Ctrl+P): layout limpo, sem sidebar, sem toasts, sem save badge
- [ ] **Teclado**: navegação por Tab funciona em toda a UI
- [ ] **Responsivo**: redimensionar a janela para <800px não parte o layout (sidebar pode colapsar)

---

## Bloco 15 — Portais: persistência

- [ ] Fecha o Portal COE
- [ ] Reabre-o
- [ ] Os dados que introduziste (contactos editados, ocorrência em progresso, verificação mensal) continuam lá
- [ ] Faz export JSON
- [ ] Importa o export — substitui correctamente
- [ ] Vai a **Configurações → Repor Padrão** → confirma → os valores voltam aos defaults do config
- [ ] Reimporta o backup — restaura correctamente

---

## Bloco 16 — Diferenciação entre aeroportos (se aplicável)

Apenas se estás a validar um build para **outro aeroporto** (não o FNMO):

- [ ] Executaste o build com `--config config/airport-XXXX.json` onde `XXXX` é o OACI do novo aeroporto
- [ ] O header mostra o nome do **novo aeroporto**, não FNMO
- [ ] O footer da sidebar mostra o **novo OACI**
- [ ] A secção Contactos mostra os contactos do novo aeroporto (se actualizados no config)
- [ ] Zero menções a "FNMO" ou "Welwitschia Mirabilis" no ecrã (excepto em códigos de documento hard-coded)

---

## Resultado final

**Data de conclusão:** ________________
**Hora de conclusão:** ________________

- [ ] **TODOS OS CHECKBOXES ACIMA ESTÃO MARCADOS** → Release APROVADA
- [ ] **Algum checkbox não marcado** → Release BLOQUEADA, listar problemas abaixo

### Problemas encontrados

| # | Bloco | Descrição do problema | Severidade (B/M/A) | Acção |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

**Severidade**:
- **B**aixa — cosmético, não afecta operação
- **M**édia — afecta 1 secção mas há workaround
- **A**lta — bloqueia uso operacional, reverter release

---

## Assinaturas

**Validado por:** ________________________________

**Data:** ________________

**Aprovado para distribuição por:** ________________________________

**Data:** ________________
