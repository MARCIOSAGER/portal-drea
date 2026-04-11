# Pesquisa de Mercado — Design System para Portal DREA

**Data**: 2026-04-11
**Contexto**: Brainstorming da padronização visual dos Portais COE e SSCI (e preparação dos portais futuros SOA, AVSEC, DIRECÇÃO)
**Escopo**: Design systems operacionais/mission-critical, UI aeronáutica, padrões de C2 (command & control), tipografia data-dense, placement de branding, cores de status
**Ambição confirmada**: Design System SGA completo (opção C do brainstorming)
**Tema confirmado**: Light theme only

---

## 1. Design systems operacionais/enterprise de referência

Avaliados seis sistemas com tracção comprovada em software profissional data-dense. Excluídos deliberadamente sistemas orientados a marketing/consumidor (Material 3, Apple HIG).

### IBM Carbon — https://carbondesignsystem.com/
- **Produto**: IBM Cloud, Watson, consoles enterprise, dashboards de infraestrutura.
- **Chrome em light**: "UI shell" com header branco ou cinza muito claro (`#f4f4f4`), sidebar light colapsável ("side nav"), acentos de cor limitados a primário e estados. Cor institucional aparece em logo, botão primário e focus ring — não em superfícies grandes.
- **Densidade**: compacta. Table rows de 32/40/48 px configuráveis. Um dos únicos sistemas com *data table density tokens* formalizados.
- **Tipografia**: **IBM Plex Sans** (humanista, aberta, excelente para números). Escala tipográfica "productive" (compacta) vs "expressive" (marketing) — o DREA precisa da productive.
- **Força**: tokens bem estruturados (`$layer-01/02/03`), guidelines explícitas para *data visualization*, componentes de *notification* (inline, toast, actionable) maduros.
- **Fraqueza**: curva de aprendizagem alta, estética "IBM" muito reconhecível pode dominar a identidade SGA.

### Atlassian Design System — https://atlassian.design/
- **Produto**: Jira, Confluence, Bitbucket — ferramentas de trabalho intenso.
- **Chrome**: header branco com faixa azul fina de acento, sidebar light (`#fafbfc`). Muito discreto.
- **Densidade**: média (mais espaçoso que Carbon, mais denso que Spectrum).
- **Tipografia**: system font stack ("Charlie Sans" apenas em marketing). **Relevante dado o constraint de não-CDN**.
- **Força**: tokens semânticos exemplares (`color.background.accent.blue.subtlest` etc.), ADG (Atlassian Design Guidelines) com checklists operacionais.
- **Fraqueza**: menos componentes de alta-tensão (emergency/alarm) que SAP Fiori ou Carbon.

### SAP Fiori — https://experience.sap.com/fiori-design-web/
- **Produto**: ERP, MRO, airline ops (SAP é fornecedor de muitas aéreas e aeroportos, incluindo módulos *airport operations*).
- **Chrome**: "shell bar" superior azul-escuro SAP ou branco com logo + user menu + notifications. Sidebar colapsável. **Fiori 3 introduziu "Quartz Light" com chrome praticamente branco e o azul institucional só na shell bar** — modelo directamente comparável ao que o COE precisa.
- **Densidade**: oferece *Compact mode* e *Cozy mode* formal — exactamente o problema de software industrial.
- **Tipografia**: **"72"** (fonte proprietária SAP) com fallback para Arial.
- **Força**: provas reais em ambientes 24/7 industriais; guidelines explícitas para *object pages*, *worklist*, *overview page* (padrões que encaixam em checklists SSCI e fichas COE).
- **Fraqueza**: documentação pesada, assume ecossistema SAP.

### Microsoft Fluent 2 — https://fluent2.microsoft.design/
- **Produto**: Microsoft 365, Teams, Azure Portal.
- **Chrome**: header branco ou cinza (`#faf9f8`), sidebar light, acentos da cor institucional em selected state e primary button.
- **Densidade**: média; tem variante "Teams" mais compacta.
- **Tipografia**: **Segoe UI** (Windows) / **system-ui** fallback — *zero dependências*, match perfeito para single-file HTML.
- **Força**: *depth tokens* (elevation) bem definidos em light.
- **Fraqueza**: mistura visual com Windows pode ser percebida como "aplicação Microsoft".

### GitHub Primer — https://primer.style/
- **Produto**: GitHub.com, dashboards de desenvolvimento.
- **Chrome**: header branco ou cinza muito claro, sidebar light. Acento institucional pontual.
- **Tipografia**: system font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", ...`) — **referência canónica do stack sem dependências**.
- **Força**: tokens semânticos `fg.default`, `canvas.subtle`, `border.muted` são uma lição directa; documentação open-source exemplar.
- **Fraqueza**: poucos componentes de *status/alert* de alta criticidade.

### USWDS — https://designsystem.digital.gov/
- **Produto**: portais governamentais dos EUA, incluindo FAA e TSA.
- **Chrome**: header com faixa de identidade governamental, corpo branco.
- **Tipografia**: **Source Sans 3** (fallback system).
- **Força**: **WCAG AA compliance é first-class citizen** — directamente relevante para operadores sob stress que precisam de contraste inequívoco. Tokens de status (`--usa-state-error`, `--usa-state-warning`) prontos.
- **Fraqueza**: estética "institucional US" pode parecer deslocada; menos componentes densos.

### Candidatos mais fortes para o Portal DREA
1. **SAP Fiori (Quartz Light)** — o mais próximo do caso de uso real: ops industrial, chrome institucional preservado em light, padrões de worklist e object page alinhados com COE/SSCI.
2. **IBM Carbon** — rigor em tokens, densidade configurável, excelência em data tables e notifications.
3. **GitHub Primer + USWDS (híbrido)** — Primer pela disciplina de tokens semânticos e system font stack (crítico para single-file HTML), USWDS pela robustez de estados de status WCAG AA.

A recomendação natural é **inspirar-se na arquitectura de tokens de Carbon/Primer, nos padrões de layout de Fiori, e nas garantias de acessibilidade de USWDS** — sem adoptar nenhum como dependência.

---

## 2. UI em aviação e operações aeroportuárias

Padrões observáveis em software público/semi-público:

- **ForeFlight** (https://foreflight.com/) — pilotos/dispatch. *Light theme é o default em modo briefing*; dark reservado para cockpit nocturno. Cards brancos sobre fundo cinza muito claro, blocos de METAR/TAF com tipografia monospace. Acentos de cor limitados a status de aeródromo (VFR verde, MVFR azul, IFR vermelho, LIFR magenta) — **codificação ICAO directa**.
- **Jeppesen FliteDeck Pro** — interface de cartas e rotas. Status operacionais via *iconografia pequena + texto curto*, não via *cores saturadas de fundo*. Lição: fundos grandes coloridos cansam; cor vive em *badges*, *borders* e *icon fills*.
- **Eurocontrol NM Portal / CHMI / NOP** (https://www.eurocontrol.int/network-operations) — ferramentas de gestão de fluxo. Tabelas muito densas, headers fixos, filtros persistentes laterais, **sempre light theme para uso diurno em sala de controlo**. Logo Eurocontrol no header, nunca na sidebar.
- **Amadeus Altéa Airport / SITA Airport Management** — screenshots públicos em press kits mostram shells brancos com header institucional colorido fino, e cores operacionais reservadas para códigos de voo/status de gate.
- **FAA Ops Dashboards públicos** (NASFlight, ASPM — https://aspm.faa.gov/, verificar acesso público) — tabelas densas, tipografia pequena mas legível, status por badges de cor sólida pequenos.

**Padrões recorrentes relevantes para o DREA**:
1. **Header com identidade institucional sempre visível** (logo + nome do sistema + user + timestamp/hora UTC).
2. **Status operacional por badges pequenos de alto contraste**, não por fundos grandes de cor — reduz fadiga em turnos longos.
3. **Sidebar light com secções por domínio** (não por acção), colapsável para maximizar área de dados.
4. **Timestamp UTC visível permanentemente** — convenção aeronáutica, deve entrar no chrome do DREA.
5. **Tipografia tabular-figures obrigatória** para colunas numéricas (horas, flight levels, quantidades).

---

## 3. UI de emergência / comando e controlo

Referências e padrões identificáveis:

- **NASA Mission Control (MCC-H)** — fotografias públicas (https://www.nasa.gov/johnson/flight-operations/) mostram consolas com **múltiplos monitores light-theme** em horas diurnas; dark só em operações nocturnas específicas. Grid de telemetria com fundos neutros, valores em verde/âmbar/vermelho conforme desvio de nominal.
- **Police CAD / Motorola Flex, Hexagon OnCall Dispatch** (https://hexagon.com/products/oncall-dispatch) — screenshots em brochuras mostram light shell, mapa ocupando 60-70% do ecrã, *incident panel* lateral, estados por cor sólida em *border-left* de cards (truque comum: barra de 4px à esquerda do card indica prioridade).
- **Military COP** — exemplos públicos (Palantir Gotham, Systematic SitaWare) tendem a dark, mas versões civis de *incident command* (FEMA WebEOC, Veoci) são light.
- **NIMS/ICS software** (https://training.fema.gov/nims/) — ICS Forms 201/202/214 têm layout de formulário muito formal; software que os digitaliza preserva esse layout *documento-like*. Relevante para o SSCI que já tem feel "documento".
- **Fire service dispatch** — produtos como ESO Fire (https://www.eso.com/fire/), ImageTrend Elite — light themes com acentos em vermelho-bombeiro e âmbar NFPA apenas em *status pills* e botões de acção destrutiva.

**Padrões para light theme de C2 (comando e controlo)**:
1. **"Calm by default, loud when it matters"** — fundo totalmente neutro; a cor só aparece quando há um estado não-nominal.
2. **Hierarquia de alertas visual progressiva**: info → warning → alert → critical → emergency, cada nível com contraste e saturação maior.
3. **Cards com *status stripe* lateral** (4px à esquerda) em vez de fundos inteiros coloridos.
4. **Blink/pulse reservado exclusivamente para emergency** — nunca para warnings, caso contrário banaliza.
5. **Acknowledge obrigatório** em alertas críticos antes de poderem ser visualmente atenuados.

---

## 4. Tipografia para UIs operacionais data-dense (2025-2026)

| Fonte | Vantagem | Desvantagem para DREA |
|---|---|---|
| **System font stack** | Zero dependências, nativa, cobre Windows/macOS/Linux | Inconsistência cross-plataforma |
| **Inter** (https://rsms.me/inter/) | Standard de facto em 2025 para produtos SaaS, tabular figures excelentes | Requer embutir |
| **IBM Plex Sans** (https://www.ibm.com/plex/) | Humanista, personalidade, números claros | Pesada (vários pesos) |
| **Geist** (https://vercel.com/font) | Moderna, Vercel/Next | Jovem, menos provada |
| **Source Sans 3** (Adobe/USWDS) | Open, neutra | Menos carácter |
| **JetBrains Mono** / **IBM Plex Mono** | Mono para checklists, timestamps, códigos ICAO | Complemento, não corpo |

**Recomendação específica para o DREA dadas as constraints**:

**Opção A (mais segura) — System font stack puro**, seguindo Primer/Atlassian:
```css
-apple-system, BlinkMacSystemFont, "Segoe UI", "Segoe UI Variable",
Roboto, "Helvetica Neue", Arial, sans-serif
```
Zero bytes de fonte no `.html`, funciona offline sempre, cobre Chrome/Edge/Firefox em Windows 10/11 (alvo real dos postos de trabalho SGA — *Segoe UI Variable* já é excelente).

**Opção B (mais identidade) — Inter Variable embutida como woff2 base64**:
Um único ficheiro `Inter-Variable.woff2` (~100-150 KB) cobre todos os pesos. Inlined em base64 no `.html` adiciona ~200 KB ao ficheiro final — tolerável. Inter tem *tabular figures* via `font-feature-settings: "tnum"` essenciais para tabelas de horas, pesos, quantidades.

**Complemento mono** (opcional, para checklist codes e timestamps): `ui-monospace, "SF Mono", "Cascadia Mono", "Segoe UI Mono", Consolas, monospace` — também system stack, zero bytes.

**Recomendação**: começar com **Opção A (system stack)** para o COE e SSCI imediatos, manter a **Opção B (Inter embutida) como upgrade path** quando o design system for formalizado.

---

## 5. Placement de logo e branding institucional

Convenções observadas em portais operacionais:

- **Uma única âncora dominante — o header esquerdo**. É a convenção mais forte: Fiori (shell bar), Carbon (UI shell), Jira, GitHub, Eurocontrol NM, ForeFlight. O olhar do operador passa milhares de vezes por esse canto em turnos longos; colocar o logo lá fixa identidade sem ocupar *content area*.
- **Sidebar não é sítio para logo grande** — convenção é colocar no topo da sidebar apenas um *mark* reduzido (símbolo sem wordmark) ou nada. O COE actual que tem logo em dois sítios (header + sidebar) é tecnicamente redundância — convenção enterprise é **um só**.
- **Splash/loading screen** é aceitável e recomendado para afirmação institucional no arranque da aplicação (2-3 segundos), depois desaparece. Aeronáutico civil usa muito (ForeFlight, Jeppesen).
- **Footer institucional discreto** (linha fina com "SGA — Sociedade de Gestão Aeroportuária · versão X.Y" + copyright) é convenção comum em software governamental/regulado — ver USWDS footer pattern.
- **Print headers** — em print stylesheets o logo deve aparecer *em cada página impressa* (cabeçalho do documento), porque o output sai do contexto digital e precisa de reancoragem institucional. Importante para fichas SSCI e relatórios COE.

**Para o DREA concretamente**:
1. Logo SGA no header esquerdo dos cinco portais — âncora única institucional.
2. Sidebar sem logo (ou só mark de 24x24 px colapsado).
3. Splash screen de arranque com logo completo + nome do portal ("Portal COE", "Portal SSCI", etc.) + tagline DREA.
4. Footer com linha institucional discreta.
5. Print header reimprime logo + nome do portal + timestamp de impressão.

---

## 6. Sistema de cores de status (WCAG AA, escala semântica)

**Estrutura em 5 níveis semânticos** (encontrada em Carbon, Fiori, USWDS com nomenclatura variável):

| Nível | Uso | Exemplo aeronáutico |
|---|---|---|
| `info` | Informação contextual, neutro | Nota sobre procedimento |
| `success` | Confirmação, estado OK | Checklist completo, veículo VCI operacional |
| `warning` | Atenção, degradação aceitável | Tempo de resposta acima do target mas dentro de tolerância |
| `alert` / `danger` | Problema que requer acção | Veículo VCI inoperacional, checklist com falhas |
| `emergency` / `critical` | Crítico, acção imediata | Ocorrência AVSEC activa, emergência aeronáutica em curso |

**Cada nível precisa de 3-4 tokens** (padrão Carbon/Primer):
- `--status-X-fg` (texto/ícone) — alto contraste
- `--status-X-bg` (fundo de badge/banner) — fundo subtle
- `--status-X-border` (borda/stripe lateral)
- `--status-X-emphasis` (botão/fill forte quando preciso)

**Regras de acessibilidade WCAG AA**:
- Contraste texto vs fundo ≥ **4.5:1** para texto normal, ≥ **3:1** para texto grande (≥18pt / 14pt bold).
- UI components e gráficos ≥ **3:1**.
- **Cor nunca é o único canal** — acompanhar sempre com ícone + texto. Crítico para daltónicos e para operadores sob stress.

**Mapeamento proposto da paleta SGA para escala semântica**:

```
info       → #0094CF (medium blue SGA) sobre #e6f4fb (bg subtle)
success    → verde NOVO (não existe na paleta — sugestão: #2e7d32 sobre #e8f5e9)
warning    → #f39c12 (AVSEC amber SGA) sobre #fef5e7
alert      → #c62828 (warning red SGA) sobre #fdecea
emergency  → #b71c1c (red deepened) sobre #fdecea com border 2px pulsante
```

### Pontos de atenção CRÍTICOS para validação com o consultor

1. **AVSEC amber SGA (`#f39c12`) tem duplo uso** — é cor *institucional* de uma categoria operacional (bombeiros/AVSEC) E cor semântica de *warning*. Isto pode criar ambiguidade: quando um badge é amber, é "categoria AVSEC" ou "warning"? Sugestão: reservar `#f39c12` *exclusivamente* para warning semântico e usar outro tom para branding AVSEC (ou vice-versa). **Decisão pendente**.

2. **Verde success está ausente da paleta SGA** — precisa de adição formal.

3. **Contraste de `#f39c12` sobre branco** é ~2.1:1 — **falha WCAG AA para texto**. Deve ser usado apenas como *fundo* ou *border*, nunca como *foreground text*. Para texto warning usar um amber mais escuro (`#8a5a00` tem ~6.3:1).

4. **`#0094CF` sobre branco** é ~3.5:1 — falha para texto normal, passa para large text. Para links/texto usar `#004C7B` (dark blue SGA, ~9.1:1, passa AAA).

5. **Padrão "status stripe"** (border-left 4px) é o recomendado para cards operacionais — permite usar a cor com força sem carregar o fundo inteiro.

---

## Recomendação sintética para o Portal DREA

Pontos accionáveis para decisão humana/consultor:

- **Arquitectura de referência**: inspirar o design system SGA numa combinação **Fiori (padrões de layout operacional) + Carbon/Primer (disciplina de tokens semânticos) + USWDS (rigor de acessibilidade)**. Nenhum adoptado como dependência — apenas como referência escrita nos guidelines.

- **Chrome institucional em light**: header branco ou com faixa fina de `#004C7B` (cor institucional SGA) contendo logo + nome do portal + timestamp UTC + user — convenção "shell bar" Fiori/Carbon. Sidebar light sem logo. Isto preserva identidade COE sem recuperar a sidebar azul-escura.

- **Tipografia**: começar com **system font stack** (zero-dependência, compatível com single-file HTML) para COE e SSCI; manter **Inter Variable embutida em base64** como upgrade path formalizável na v2 do design system. Activar `font-feature-settings: "tnum"` globalmente em tabelas.

- **Escala de status semântica em 5 níveis** (info / success / warning / alert / emergency) com 3-4 tokens cada, usando *status stripe* lateral em cards. **Resolver com o consultor a ambiguidade do amber `#f39c12`** (branding AVSEC vs semântica warning) — é a única tensão real da paleta actual. Adicionar verde success à paleta oficial SGA.

- **Placement de logo unificado** nos 5 portais: header esquerdo (único), splash screen de arranque, footer institucional discreto, print header em cada página impressa. Remover o logo duplicado do sidebar COE actual.

- **Densidade configurável** (*compact* vs *cozy*, padrão Fiori/Carbon) como token de base — SSCI pode preferir cozy (feel documento), COE provavelmente compact (mission control). Fica configurável por portal sem ramificar o design system.

---

## Referências verificáveis

- carbondesignsystem.com
- atlassian.design
- experience.sap.com/fiori-design-web
- fluent2.microsoft.design
- primer.style
- designsystem.digital.gov
- foreflight.com
- eurocontrol.int/network-operations
- hexagon.com/products/oncall-dispatch
- training.fema.gov/nims
- rsms.me/inter
- ibm.com/plex
- vercel.com/font

Referências assinaladas para verificação adicional: ASPM FAA (https://aspm.faa.gov/), screenshots internos de Amadeus Altéa e SITA AMS.
