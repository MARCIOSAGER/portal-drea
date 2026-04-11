# Design System SGA — Plan 4: COE Chrome Migration (Implementation Plan)

> **Status:** ✅ **COMPLETED 2026-04-11** on branch `feat/coe-chrome` (worktree `../Portal_DREA-chrome`).
> 13 atomic commits executing all 14 tasks.
> 43 pytest tests passing (38 from Plans 1-3 + 5 new for base/chrome/print cascade).
> New files: base/{reset,typography,global}.css, chrome/{shell-bar,sidebar,page-grid,splash,footer}.css, print/print.css, scripts/chrome/splash.js, scripts/utilities/date-utc.js, logo-sga-mark.svg + logo-sga-full.svg (stubs), icon-siren in sprite.
> COE source HTML surgery: 14 nav-btn preserved, 6 IDs preserved (clockDisplay, headerUTC, headerDate, operatorBadge, dsSplash, dsEmgPill), dual class `ds-shell-bar__oaci header-title-small` for cfgApplyToPortal() contract, splash script inlined before </body>.
> File size delta: COE 4,452,780 → 4,473,169 bytes (+20,389 bytes — new chrome CSS added, legacy header+sidebar HTML removed including the embedded PNG logo). SSCI inherits the new chrome CSS via compile_design_system_css but has no HTML consumer yet (Plan 5 territory).

> **Status:** DRAFT — aguarda execução noutra sessão.
> Este é o plano **mais visualmente consequente** de toda a migração DS SGA: substitui o chrome actual do Portal COE (sidebar azul-escura + header gradient + logo duplicado) pela nova Shell Bar light + faixa institucional de 4 px + logo único + relógio UTC permanente + splash screen + footer institucional + print stylesheet. Depois deste plano o Portal COE passa finalmente a parecer-se com a especificação do Design System SGA.

> **For agentic workers:** REQUIRED SUB-SKILL: usar `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para executar este plano tarefa-a-tarefa. Cada Task termina com um bloco de verificação. Steps usam checkbox (`- [ ]`) para tracking.

**Goal:** substituir o HTML do chrome actual do Portal COE (sidebar `.sidebar` azul-escura + `<header>` gradient) pelo novo chrome Design System SGA — Shell Bar 56 px branca com faixa `#004C7B` 4 px, sidebar 240 px light com `border-left` 3 px na nav activa, canvas `#f6f8fa`, splash screen 1.5 s, footer institucional, print stylesheet `@page`. Preservar **100 % dos event handlers e IDs** da navegação existente (`openSection()`, `.nav-btn`, `logoutCOE()`, relógio, badge de operador) de modo a que o JavaScript de domínio continue a funcionar sem alteração.

**Architecture:** o chrome é introduzido em ficheiros `shared/styles/base/*.css` e `shared/styles/chrome/*.css` consumidos pelo pipeline `compile_design_system_css()` já existente em `scripts/ds_build_helpers.py` (criado no Plan 1, confirmado nos commits `f81d6db..cd72f17`). A função aprende nesta fase a descobrir automaticamente os ficheiros de `base/` (após `tokens/`), `chrome/` (após `components/` adicionados no Plan 3) e `print/` (último), em ordem alfabética por directoria. O HTML do COE é modificado num commit atómico que remove `<div class="sidebar">` e `<header>` e substitui por `<aside class="ds-sidebar">` + `<header class="ds-shell-bar">` preservando os `onclick="openSection('X', event)"` e os IDs `clockDisplay`, `headerUTC`, `headerDate`, `operatorBadge` que o JS de domínio consulta. O splash screen vive antes do shell bar como overlay fixed + fade-out, com um micro-script inline. O único utilitário JavaScript novo do Plan 4 (clock UTC) fica em `shared/scripts/utilities/date-utc.js` e é injectado via `{{DS_JS}}` ou (provisoriamente) inline no próprio source HTML através de um helper específico. Os utilitários `ls-wrapper.js` e `esc-html.js` — inicialmente considerados — foram removidos do scope: nenhum consumidor CSS/HTML do Plan 4 os referencia, e são diferidos para Plan 5 / Plan 6. O CSS legado em bloco 1 fica como está — colisões são evitadas por namespace de classes `.ds-*` em todo o chrome novo.

**Tech Stack:** Python 3.8+ (extensão do `compile_design_system_css`), pytest (regressão de cascade order e descoberta de ficheiros), CSS moderno (flex/grid, CSS custom properties, `@page`, `@media print`, `@keyframes`), vanilla JavaScript (clock UTC ticker, splash fade-out), Inter Variable (já embebida no Plan 1), git (worktree isolado, commits atómicos).

**Source spec:** [docs/superpowers/specs/2026-04-11-design-system-sga-design.md](../specs/2026-04-11-design-system-sga-design.md) — **Secção 4 completa** (Shell bar 4.1, Sidebar 4.2, Page grid 4.3, Splash 4.4, Footer 4.5, Print 4.6) + Secção 6.2 (cascade order determinística) + Secção 7.3 Fase 3 (COE chrome).

**Invariant this plan must preserve:** **equivalência visual deixa de ser o invariante** — este plano muda deliberadamente a aparência do COE. O novo invariante é **spec alignment**:

1. Após execução, abrir `dist/Portal_COE_AWM.html` num browser moderno e comparar com a Secção 4 da spec. O Shell Bar deve ter as três zonas (SGA mark + Portal COE + OACI | breadcrumb | UTC + local + user badge), a faixa de 4 px `#004C7B` imediatamente abaixo, a sidebar 240 px light canvas `#f6f8fa` com `border-left: 3px --ds-brand-primary` na nav activa, e o canvas branco com cards.
2. **Invariante duro de preservação JS**: todas as invocações de `openSection('dashboard', event)`, `openSection('cronometro', event)`, `openSection('contactos', event)`, `openSection('verif-contactos', event)`, `openSection('mapas', event)`, `openSection('fluxogramas', event)`, `openSection('guia-emg', event)`, `openSection('fichas-emg', event)`, `openSection('guia-seg', event)`, `openSection('fichas-seg', event)`, `openSection('documentacao', event)`, `openSection('referencias', event)`, `openSection('ajuda', event)`, `openSection('configuracoes', event)` continuam a funcionar. As classes `.nav-btn` (verificar com `document.querySelectorAll('.nav-btn').length >= 14`) e `.section` continuam a ser reconhecidas. Os IDs `clockDisplay`, `headerUTC`, `headerDate`, `operatorBadge` continuam a existir no DOM (o novo chrome expõe-nos embora possa ligá-los a elementos visualmente diferentes).
3. **Build passes**: `python scripts/build-all.py` exit 0, `pytest` exit 0, `node --check` aos blocos de script OK.
4. **Smoke test manual**: o utilizador abre o HTML, clica em cada item da sidebar, não há erros de console, o relógio UTC está a correr.
5. **axe DevTools**: 0 violations serious/critical nas páginas Dashboard, Contactos, Verificação Mensal.
6. **Print preview**: `Ctrl+P` em Chrome produz um PDF com `@page` header (logo + airport + section name + timestamp), sem shell bar nem sidebar visíveis.

Se qualquer um dos 6 falha, a execução do plano pára e regressa a uma fase anterior via `git reset --hard`.

**Out of scope for Plan 4** (redirigido para os planos indicados):

- ❌ Migração de componentes genéricos (button, badge, card, modal, toast) — já cobertos pelo Plan 3
- ❌ Migração de qualquer coisa no portal SSCI — Plan 5
- ❌ Rename de `--ds-*` → `--*` + remoção de `--dark-blue`, `--medium-blue`, etc. — Plan 6
- ❌ Limpeza/remoção de CSS legado consolidado no bloco 1 — Plan 6
- ❌ Tauri / empacotamento desktop — Fase 2 do projecto, externa ao DS
- ❌ Expansão do icon sprite além dos ícones estritamente referenciados pelo novo chrome HTML. Esta fase adiciona **apenas** `icon-siren` ao sprite (ver Task 10.5). Os outros ícones de domínio listados na spec Section 5.5 (`icon-menu`, `icon-close` já existem; `icon-user`, `icon-shield`, `icon-airplane`, `icon-helmet`, `icon-fire`) são **diferidos para Plan 6** — o shell bar/sidebar do Plan 4 não os referencia (o sidebar usa os glifos Unicode existentes `✈`/`🛡`/`❓`/`⚙` herdados do legado).
- ❌ Novo JS framework ou bundler — continua vanilla JS zero-deps

---

## Key fact sheet (verified by inspection on 2026-04-11 against `main` @ `bc11d89`)

Esta secção é **load-bearing**. Tudo o que segue depende de identificar correctamente o HTML e JS que vão ser substituídos. Verificado directamente no ficheiro `packages/portal-coe/src/Portal_COE_AWM.source.html`.

### Chrome HTML actual — localização e estrutura

**Header actual** (`<header>` sem classe própria, dentro de `<div class="main-container">`):

- **Posição no source:** linhas 3253–3269 (`<div class="main-container">` abre em 3253, `<header>` em 3255, `</header>` em 3269)
- **CSS que o pinta:** bloco 1 consolidado, regra `header { background-color: #004C7B; color: white; padding: 1rem 2rem; display: flex; ... }` a partir da linha 1098
- **Filhos:**
  - `<div class="header-left">` (linha 3256) contendo `<img class="header-logo">` (logo branco) + `<div class="header-title">` com `<h1>Centro de Operações de Emergência</h1>` e `<div class="header-title-small">{{AIRPORT.NAME}} ({{AIRPORT.OACI}}) • {{AIRPORT.LOCATION}}</div>`
  - `<div style="text-align:right;">` contendo:
    - `<div class="header-clock" id="clockDisplay">00:00:00</div>` ← **ID preservar**
    - `<div id="headerUTC">UTC 00:00:00</div>` ← **ID preservar**
    - `<div id="headerDate">` ← **ID preservar**
    - `<div id="operatorBadge" style="display:none;...">` ← **ID preservar, o JS de login activa-o**

**Sidebar actual** (`<div class="sidebar">`, mais 4 `sidebar-section` grupos):

- **Posição no source:** linhas 3179–3251 (`<div class="sidebar">` abre em 3179, fecha em 3251)
- **CSS que a pinta:** bloco 1 consolidado, regra `.sidebar { background-color: #004C7B; ... width: 280px; position: fixed; ... }` ligada à estrutura a partir das linhas 1056+
- **Estrutura interior (lines 3179–3251):**
  - Logo wrapper em `<div style="text-align: center; margin-bottom: 1.5rem;">` (linha 3180) + `<img>` SGA branco (linha 3181) + `<h2>COE AWM</h2>` (linha 3183)
  - **4 grupos** `<div class="sidebar-section">`:
    - **Principal** (linhas 3185–3195) — 6 nav items: dashboard, cronometro, contactos, verif-contactos, mapas, fluxogramas
    - **Ocorrências** (linhas 3197–3227) — `sidebar-section-simulacros`, 4 items com tracks: guia-emg, fichas-emg, guia-seg, fichas-seg
    - **Documentação** (linhas 3229–3235) — 2 items: documentacao, referencias
    - **Sistema** (linhas 3237–3243) — 2 items: ajuda, configuracoes
  - `<div class="sidebar-version-footer">` (linhas 3246–3250) com `{{VERSION}}`, `{{BUILD_DATE_SHORT}}`, `{{AIRPORT.OACI}}`, `{{AIRPORT.OPERATOR_SHORT}}`
- **Total de nav items a preservar: 14** (6 + 4 + 2 + 2)

### Handlers JavaScript que o chrome actual invoca

Todos os `onclick` dos 14 nav items seguem o padrão uniforme `onclick="openSection('<sectionId>', event)"` e aplicam a classe CSS `.nav-btn` (+ opcionalmente `.nav-btn.active`). A função `openSection` está definida nas linhas 9946–9970:

```javascript
function openSection(sectionId, event) {
    if (event) event.preventDefault();
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
    event?.target?.classList.add('active');
    // ...lógica específica de cronometro...
}
```

**Duas exigências críticas para o novo chrome:**

1. Os novos elementos de nav **têm** que continuar a ter `class="nav-btn"` (a função `openSection` filtra por esta classe). Podem **também** ter classes DS novas (`ds-nav-item` ou similar) — a classe legacy `nav-btn` é o contrato.
2. Os `onclick` preservam a assinatura `openSection('<id>', event)` exactamente. Não mudar para `addEventListener` (isso envolveria JS extra e partia a simetria com os restantes elementos).

**Clock updater** (linhas 9930–9943):
```javascript
function updateHeaderClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('pt-PT', { hour12: false });
    const utcStr = now.toLocaleTimeString('pt-PT', { hour12: false, timeZone: 'UTC' });
    document.getElementById('clockDisplay').textContent = timeStr;
    document.getElementById('headerUTC').textContent = 'UTC ' + utcStr;
    document.getElementById('headerDate').textContent = formatDate(now);
    var dbClock = document.getElementById('dashboardClock'); if (dbClock) dbClock.textContent = timeStr;
    var dbUTC = document.getElementById('dashboardUTC'); if (dbUTC) dbUTC.textContent = 'UTC ' + utcStr;
    var dbDate = document.getElementById('dashboardDate'); if (dbDate) dbDate.textContent = formatDate(now);
}
updateHeaderClock();
setInterval(updateHeaderClock, 1000);
```

**Exigência:** os IDs `clockDisplay`, `headerUTC`, `headerDate` **têm que existir no novo chrome** — o novo shell bar ligá-los-á aos elementos que mostram hora local e UTC. Se preferir renomear internamente, manter os IDs antigos como alias invisível (e.g. `<span id="clockDisplay" hidden></span>` redundante ao visual) é aceitável. A escolha preferida é manter os IDs directamente nos elementos visíveis.

**Operator badge** — linhas 6253+, 10446+, 10608+ (três sítios no source):
```javascript
var badge = document.getElementById('operatorBadge');
// ...lógica de login e logout que faz badge.style.display = 'inline-block' e escreve innerHTML...
```
O `operatorBadge` é escondido por default (`display:none`) e revelado no login com o nome do operador. No novo shell bar ele fica na zona direita, ao lado do user dropdown.

**Logout handler** (linhas 6256 e 10449): o `innerHTML` injecta `<button onclick="logoutCOE()">Sair</button>` dentro do `operatorBadge` ou zona adjacente. A função `logoutCOE()` está na linha 10602. **Preservar o nome** — o plano **não** reimplementa logout.

### Relação com o DS actual (Plan 1 + Plan 2 + Plan 3)

- `{{DS_CSS}}` já está a ser injectado no topo do `<head>` (linha 487 do source, confirmado por Plan 2 block 0).
- O `<style>` legado do Plan 2 block 1 consolidado vive imediatamente a seguir e ainda contém **todo** o CSS do chrome legado (`.sidebar`, `header`, `.header-left`, `.header-title`, `.header-clock`, `.sidebar-section`, `.sidebar-menu`, `.nav-btn`, `.main-container`).
- **Plan 4 não remove o CSS legado.** O novo chrome usa classes **com namespace `.ds-*`** (`.ds-shell-bar`, `.ds-sidebar`, `.ds-nav-item`, `.ds-page-grid`) para não colidir. O CSS legado permanece dormente (selectores `.sidebar`, `header`, etc. deixam de corresponder a nenhum elemento assim que o HTML é substituído). A limpeza do CSS legado é scope do Plan 6.
- A única classe **mantida** do contrato legacy é `.nav-btn` nos nav items — usada pela função `openSection()` para resetar o estado `active`. As regras CSS `.nav-btn { ... }` e `.nav-btn.active { ... }` do bloco 1 continuam a aplicar-se mas serão substituídas visualmente pelas regras DS mais específicas do novo ficheiro `chrome/sidebar.css`. Para não depender da ordem de cascade, o novo ficheiro deve usar `.ds-sidebar .nav-btn { ... }` com maior specificity.

### SVG logos — pré-requisito externo

Actualmente existem em `shared/assets/`:
- `logo-sga.png` (7 627 bytes, azul)
- `logo-sga-white.png` (10 858 bytes, branco)

**Nenhuma versão SVG** existe ainda. O plano **exige** dois ficheiros SVG novos antes de poder injectar o shell bar:

- `shared/assets/logo-sga-mark.svg` — apenas o símbolo SGA, 32 × 32 `viewBox`, `currentColor` compatível, para uso no Shell Bar e no cabeçalho de impressão
- `shared/assets/logo-sga-full.svg` — o lockup completo com wordmark + tagline, ~200 × 80 `viewBox`, para uso no splash screen

**Decisão:** estes SVGs são um **pré-requisito externo**. A Task 0 verifica a sua presença e **aborta com erro explícito** se não existirem, instruindo o utilizador a fornecê-los manualmente (ou a pedir ao consultor para tracear os PNG existentes via Inkscape/Illustrator). O plano-writer não tenta gerar SVGs programaticamente.

Durante a Task 0, se os ficheiros não existem, criar um **stub temporário aceitável para dev**:
- `logo-sga-mark.svg` com um rectângulo `#004C7B` + texto "SGA" branco, bastante para validar o pipeline
- `logo-sga-full.svg` com o mesmo rectângulo + "Sociedade de Gestão Aeroportuária"

O stub é aceitável desde que o utilizador confirme na smoke test visual que o resultado é **visualmente tolerável**. A substituição pelos SVG definitivos pode ser feita num commit separado fora do plano (mera substituição de ficheiros).

---

## File Structure (Plan 4 scope)

### Files to **create** (~14 files)

```
Portal_DREA/
├── shared/
│   ├── assets/
│   │   ├── logo-sga-mark.svg                       NEW — símbolo SGA 32×32 (pré-requisito externo, ver Task 0)
│   │   └── logo-sga-full.svg                       NEW — lockup SGA 200×80 (pré-requisito externo)
│   │
│   ├── styles/
│   │   ├── base/
│   │   │   ├── reset.css                           NEW — modern reset (box-sizing, margins, font-smoothing)
│   │   │   ├── typography.css                      NEW — heading hierarchy, body text, font-variant-numeric
│   │   │   └── global.css                          NEW — focus ring, body bg, selection, data-density hook
│   │   │
│   │   ├── chrome/
│   │   │   ├── shell-bar.css                       NEW — .ds-shell-bar + zonas + faixa 4px institucional
│   │   │   ├── sidebar.css                         NEW — .ds-sidebar light canvas + nav items + active border-left
│   │   │   ├── page-grid.css                       NEW — layout grid com canvas + max-width 1440px
│   │   │   ├── splash.css                          NEW — .ds-splash overlay + fade-out keyframes
│   │   │   └── footer.css                          NEW — .ds-footer institucional
│   │   │
│   │   └── print/
│   │       └── print.css                           NEW — @page header + hide chrome + paginação
│   │
│   └── scripts/
│       ├── utilities/
│       │   └── date-utc.js                         NEW — extrai ticker do relógio UTC (wrapper round updateHeaderClock)
│       │
│       └── chrome/
│           └── splash.js                           NEW — micro-lifecycle do splash (1500ms + fade-out + ?nosplash=1)
│
└── tests/
    └── test_ds_build_helpers_plan4.py              NEW — regressão dos novos ficheiros descobertos em base/, chrome/, print/
```

**Nota sobre `ls-wrapper.js` e `esc-html.js`**: ambos estavam inicialmente listados neste plano, mas **foram removidos do scope do Plan 4** porque nenhum consumidor CSS ou HTML do Plan 4 os referencia (o splash e o date-utc não precisam de localStorage nem de escape). A extracção destes utilitários é **diferida**:
- `ls-wrapper.js` → **Plan 5** (SSCI migration) pode beneficiar — decidir durante Plan 5 se extrai ou não.
- `esc-html.js` → **Plan 6** (cleanup) — cristaliza como parte da extracção sistemática do legado.
Esta nota substitui a referência antiga que os tratava como "Plan 3 pode ter extraído".

### Files to **modify** (~5)

```
scripts/ds_build_helpers.py                         MODIFY — extende compile_design_system_css() para percorrer base/, chrome/, print/ por directoria
packages/portal-coe/src/Portal_COE_AWM.source.html  MODIFY — swap chrome HTML (um commit grande), adiciona <div class="ds-splash"> no início do body, ajusta <div class="main-container"> para <main class="ds-page-grid">
tests/test_ds_build_helpers.py                      MODIFY — actualizar fixtures para reflectir nova cascade order esperada
shared/assets/icons/sprite.svg                      MODIFY — adicionar <symbol id="icon-siren"> (Task 10.5) referenciado pelo ds-shell-bar__emg-pill
(opcional) packages/portal-ssci/src/Portal_PSCI_AWM.source.html  NO-OP — Plan 4 toca apenas no COE, mas o build do SSCI continua a passar sem mudança visual (CSS novo é namespaced e não tem corresponders no HTML SSCI)
```

### Files NOT touched
Nada em `config/`, `VERSION`, `.gitignore`, `build-all.py`, `packages/*/scripts/build.py`. A extensão do pipeline acontece toda dentro de `scripts/ds_build_helpers.py::compile_design_system_css()`. Os `build.py` continuam a chamar a mesma função com os mesmos argumentos.

---

## Task 0: Prerequisites — worktree setup + baseline capture + dependency checks

**Files:** none (infra). Esta task é **blocking**: o plano não avança se algum dos checks falha.

- [ ] **Step 0.1: Verify clean working tree on `main`**

```bash
cd d:/VSCode_Claude/03-Resende/Portal_DREA && rtk git status --short
```
Expected: empty output. Se houver mudanças por commitar, **parar** e pedir ao utilizador para resolver antes de continuar.

- [ ] **Step 0.2: Verify Plan 3 is complete (commit exists, components/ directory populated)**

```bash
rtk git log --oneline -20
```
Esperar ver um commit com mensagem a referir `Plan 3` ou `feat(ds): migrate component` no histórico recente. Se não existir, **parar** — Plan 4 depende do Plan 3 ter consolidado components/ (mesmo que o bloco legacy ainda contenha CSS duplicado).

```bash
ls -la shared/styles/components/
```
Esperar ver **ao menos** `button.css`, `badge.css`, `card.css` (ou o conjunto parcial que Plan 3 entregou). Se a directoria não existe, criá-la vazia mas emitir `WARNING: Plan 3 may be incomplete — continuing anyway` e pedir confirmação ao utilizador.

- [ ] **Step 0.3: Create isolated worktree `feat/coe-chrome`**

Using the `@superpowers:using-git-worktrees` skill, criar worktree:

```bash
rtk git worktree add ../Portal_DREA-chrome feat/coe-chrome
cd ../Portal_DREA-chrome
rtk git branch --show-current
```
Expected: `feat/coe-chrome`. Todas as tasks subsequentes executam a partir de `d:/VSCode_Claude/03-Resende/Portal_DREA-chrome/`.

- [ ] **Step 0.4: Baseline build OK on branch**

```bash
python scripts/build-all.py
```
Expected: ambos os portais compilam, exit 0. Se falha, **parar** e resolver antes de continuar.

- [ ] **Step 0.5: Baseline `pytest` passing**

```bash
python -m pytest tests/ -q
```
Expected: todos os testes existentes passam (20 Plan 1 + 13 Plan 2 + N Plan 3 = **≥ 33**). Se algum falha, **parar**.

- [ ] **Step 0.6: Capture COE baseline file size to gitignored file**

```bash
python -c "from pathlib import Path; p=Path('packages/portal-coe/dist/Portal_COE_AWM.html'); print(p.stat().st_size)" > /tmp/plan4-baseline-coe-size.txt
```
Grava em `/tmp/` (ou `d:/tmp/plan4-baseline-coe-size.txt`) — usado na Task 12 para calcular delta.

- [ ] **Step 0.7: Pedir ao utilizador para capturar screenshots "antes"**

Sugerir ao utilizador (via prompt na conversa) que capture screenshots de:
1. Dashboard (ecrã principal após login)
2. Secção Ocorrência (cronómetro)
3. Secção Contactos
4. Verificação Mensal
5. Qualquer modal aberto

Estes "antes" serão comparados com os "depois" da Task 12. O plano **não** faz as screenshots automaticamente — depende do utilizador colaborar. Documentar no commit da Task 0 onde ficam guardados (pasta `d:/tmp/plan4-baselines/` ou similar).

- [ ] **Step 0.8: Verify or create SVG logos — BLOCKING pre-requisite**

```bash
ls -la shared/assets/logo-sga-mark.svg shared/assets/logo-sga-full.svg 2>&1
```

**If both files exist**: OK, continuar.

**If either is missing**:

Escolher um dos dois caminhos abaixo (utilizador decide):

**Caminho A — O utilizador fornece os SVG definitivos**:
- Parar a execução do plano com a mensagem exacta:
  ```
  BLOCKING: Plan 4 requires SVG logos that do not exist yet.

  Expected files:
    shared/assets/logo-sga-mark.svg  (32x32 symbol, institutional #004C7B)
    shared/assets/logo-sga-full.svg  (lockup with wordmark, ~200x80)

  Please provide these files before re-running Plan 4. Possible sources:
    1. Trace the existing shared/assets/logo-sga.png in Inkscape/Illustrator
    2. Request the vector original from SGA brand manager
    3. Run Plan 4 with the stub logos described in Step 0.8 Caminho B

  When the files are in place, resume by repeating Step 0.8.
  ```
- Aguardar o utilizador voltar a invocar o executor.

**Caminho B — Criar stubs temporários**:
- Se o utilizador confirma que está OK com stubs temporários para validar o pipeline, criar via Write tool:

`shared/assets/logo-sga-mark.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32" aria-label="SGA">
  <rect width="32" height="32" rx="4" fill="#004C7B"/>
  <text x="16" y="21" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="#ffffff">SGA</text>
</svg>
```

`shared/assets/logo-sga-full.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 80" width="220" height="80" aria-label="SGA — Sociedade de Gestão Aeroportuária">
  <rect x="4" y="4" width="72" height="72" rx="6" fill="#004C7B"/>
  <text x="40" y="47" text-anchor="middle" font-family="system-ui, sans-serif" font-size="26" font-weight="700" fill="#ffffff">SGA</text>
  <text x="92" y="34" font-family="system-ui, sans-serif" font-size="13" font-weight="600" fill="#004C7B">Sociedade de Gestão</text>
  <text x="92" y="52" font-family="system-ui, sans-serif" font-size="13" font-weight="600" fill="#004C7B">Aeroportuária</text>
  <text x="92" y="68" font-family="system-ui, sans-serif" font-size="10" font-weight="400" fill="#57606a">SGA — Angola</text>
</svg>
```

Documentar claramente no commit: `feat(ds): add STUB SVG logos for Plan 4 pipeline validation — to be replaced with definitive assets`.

- [ ] **Step 0.9: Commit Task 0**

```bash
rtk git add shared/assets/logo-sga-mark.svg shared/assets/logo-sga-full.svg  # apenas se Caminho B
rtk git commit -m "$(cat <<'EOF'
chore(plan4): Task 0 setup — worktree + stub SVG logos

Prepare for Plan 4 COE chrome migration:
- Worktree feat/coe-chrome created
- Baseline sizes captured
- Stub logo-sga-mark.svg and logo-sga-full.svg in place
  (to be replaced with definitive tracings post-migration)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

Se Caminho A foi escolhido e os ficheiros vieram do utilizador, o commit message refere "definitive logos added by user".

### Task 0 verification checklist
- [ ] `git status --short` limpo
- [ ] Worktree `../Portal_DREA-chrome` criado e branch `feat/coe-chrome` activo
- [ ] `python scripts/build-all.py` exit 0
- [ ] `python -m pytest tests/ -q` todos os testes passam
- [ ] `shared/assets/logo-sga-mark.svg` e `shared/assets/logo-sga-full.svg` existem
- [ ] Baseline size COE persistido em `/tmp/plan4-baseline-coe-size.txt`
- [ ] Screenshots "antes" capturados (utilizador confirma)

---

## Task 1: TDD — extend `compile_design_system_css()` to discover base/, chrome/, print/

**Files:**
- `tests/test_ds_build_helpers.py` (modify)
- `scripts/ds_build_helpers.py` (modify)

**Invariante:** a nova função descobre ficheiros por directoria alfabeticamente e respeita a cascade order da spec Secção 6.2. Nenhum portal se parte — os ficheiros em `base/`, `chrome/`, `print/` ainda não existem quando este teste é escrito, mas a função tem que os contemplar quando existirem.

### Step 1.1: Red — escrever o teste primeiro

- [ ] Abrir `tests/test_ds_build_helpers.py` e adicionar no final da class `TestCompileDesignSystemCss` os seguintes novos testes (ou num novo `TestCompileDesignSystemCssPlan4` se o estilo preferir):

```python
def _setup_plan4_styles(self, root: Path) -> None:
    """Extended fake tree with base/, chrome/, components/, print/ directories."""
    self._setup_fake_styles(root)  # tokens + base/fonts.css
    # base/ extras
    (root / "base" / "reset.css").write_text(
        "/* reset */\n*, *::before, *::after { box-sizing: border-box; }\n",
        encoding="utf-8",
    )
    (root / "base" / "typography.css").write_text(
        "/* typography */\nbody { font-family: Inter; }\n",
        encoding="utf-8",
    )
    (root / "base" / "global.css").write_text(
        "/* global */\nbody { background: var(--ds-neutral-canvas); }\n",
        encoding="utf-8",
    )
    # chrome/
    (root / "chrome").mkdir()
    (root / "chrome" / "shell-bar.css").write_text(
        "/* shell-bar */\n.ds-shell-bar { display: flex; }\n", encoding="utf-8"
    )
    (root / "chrome" / "sidebar.css").write_text(
        "/* sidebar */\n.ds-sidebar { width: 240px; }\n", encoding="utf-8"
    )
    (root / "chrome" / "page-grid.css").write_text(
        "/* page-grid */\n.ds-page-grid { display: grid; }\n", encoding="utf-8"
    )
    (root / "chrome" / "splash.css").write_text(
        "/* splash */\n.ds-splash { position: fixed; }\n", encoding="utf-8"
    )
    (root / "chrome" / "footer.css").write_text(
        "/* footer */\n.ds-footer { font-size: 11px; }\n", encoding="utf-8"
    )
    # components/ (Plan 3 — existe pode estar vazia neste teste)
    (root / "components").mkdir()
    (root / "components" / "button.css").write_text(
        "/* button */\n.ds-btn { padding: 6px; }\n", encoding="utf-8"
    )
    # print/
    (root / "print").mkdir()
    (root / "print" / "print.css").write_text(
        "/* print */\n@media print { .ds-shell-bar { display: none; } }\n",
        encoding="utf-8",
    )

def test_plan4_full_cascade_order(self, tmp_path: Path):
    """Plan 4 cascade: tokens → base/*.css (alpha) → chrome/*.css (alpha) → components/*.css (alpha) → print/print.css"""
    self._setup_plan4_styles(tmp_path)
    result = dsh.compile_design_system_css(tmp_path, density="compact")

    # Expected order indexes
    assert result.index("/* primitive */") < result.index("/* semantic */")
    assert result.index("/* semantic */") < result.index("/* compact */")
    # base/ comes after density tokens and in alphabetical order: fonts, global, reset, typography
    assert result.index("/* compact */") < result.index("/* fonts */")
    assert result.index("/* fonts */") < result.index("/* global */")
    assert result.index("/* global */") < result.index("/* reset */")
    assert result.index("/* reset */") < result.index("/* typography */")
    # chrome/ after base, alphabetical: footer, page-grid, shell-bar, sidebar, splash
    assert result.index("/* typography */") < result.index("/* footer */")
    assert result.index("/* footer */") < result.index("/* page-grid */")
    assert result.index("/* page-grid */") < result.index("/* shell-bar */")
    assert result.index("/* shell-bar */") < result.index("/* sidebar */")
    assert result.index("/* sidebar */") < result.index("/* splash */")
    # components/ after chrome
    assert result.index("/* splash */") < result.index("/* button */")
    # print/ last
    assert result.index("/* button */") < result.index("/* print */")

def test_plan4_missing_base_dir_is_ok(self, tmp_path: Path):
    """If base/ doesn't exist at all, still compiles fine (only tokens present)."""
    (tmp_path / "tokens").mkdir()
    (tmp_path / "tokens" / "primitive.css").write_text("/* primitive */\n", encoding="utf-8")
    (tmp_path / "tokens" / "semantic.css").write_text("/* semantic */\n", encoding="utf-8")
    (tmp_path / "tokens" / "density-compact.css").write_text("/* compact */\n", encoding="utf-8")

    result = dsh.compile_design_system_css(tmp_path, density="compact")
    assert "/* primitive */" in result
    # No base/chrome/components/print files, so none of those banners appear
    assert "/* reset */" not in result

def test_plan4_empty_chrome_dir_is_ok(self, tmp_path: Path):
    """An empty chrome/ directory doesn't break anything."""
    self._setup_fake_styles(tmp_path)
    (tmp_path / "chrome").mkdir()  # empty
    result = dsh.compile_design_system_css(tmp_path, density="compact")
    assert "/* primitive */" in result

def test_plan4_print_css_is_always_last(self, tmp_path: Path):
    """Even if base/ and chrome/ have files with names > 'print' alphabetically,
    print.css must come last (not sorted into other directories)."""
    self._setup_plan4_styles(tmp_path)
    # Add a file that would alphabetically come after "print"
    (tmp_path / "chrome" / "zzz.css").write_text("/* zzz */\n", encoding="utf-8")
    result = dsh.compile_design_system_css(tmp_path, density="compact")
    assert result.index("/* zzz */") < result.index("/* print */")

def test_plan4_components_between_chrome_and_print(self, tmp_path: Path):
    """components/ must come after chrome/ but before print/."""
    self._setup_plan4_styles(tmp_path)
    result = dsh.compile_design_system_css(tmp_path, density="compact")
    # button comes after all chrome files
    assert result.index("/* sidebar */") < result.index("/* button */")
    # button comes before print
    assert result.index("/* button */") < result.index("/* print */")
```

- [ ] Correr `python -m pytest tests/test_ds_build_helpers.py -q`. Expected: **os 5 novos testes falham** (red). Os testes existentes (Plan 1) continuam a passar.

### Step 1.2: Green — implementar a descoberta

- [ ] Abrir `scripts/ds_build_helpers.py` e substituir a função `compile_design_system_css` por uma versão que itera `base/`, `chrome/`, `components/` e `print/`:

```python
def compile_design_system_css(styles_root: Path, density: str) -> str:
    """
    Concatenate Design System CSS files in cascade order (spec Section 6.2):

      1. tokens/primitive.css
      2. tokens/semantic.css
      3. tokens/density-<density>.css
      4. base/*.css              (alphabetical; optional — OK if dir missing or empty)
      5. chrome/*.css            (alphabetical; optional)
      6. components/*.css        (alphabetical; optional)
      7. print/print.css         (optional; must be LAST if present)

    Raises:
        ValueError: if density invalid
        FileNotFoundError: if any required tokens file missing
    """
    if density not in _VALID_DENSITIES:
        raise ValueError(
            f"Invalid density {density!r}; must be one of {_VALID_DENSITIES}"
        )

    styles_root = Path(styles_root)

    # Required files (always present from Plan 1 onward)
    required_files = [
        styles_root / "tokens" / "primitive.css",
        styles_root / "tokens" / "semantic.css",
        styles_root / "tokens" / f"density-{density}.css",
    ]
    for f in required_files:
        if not f.exists():
            raise FileNotFoundError(f"Required DS CSS file not found: {f}")

    # Optional directories, in cascade order. Each entry is a directory whose
    # *.css files are picked up in sorted order. `print/` is the exception —
    # it's a single file treated as the last block.
    optional_dirs_alpha = [
        styles_root / "base",
        styles_root / "chrome",
        styles_root / "components",
    ]
    print_file = styles_root / "print" / "print.css"

    def _collect_alpha(directory: Path) -> list[Path]:
        if not directory.exists():
            return []
        return sorted(p for p in directory.glob("*.css") if p.is_file())

    pieces: list[str] = []

    def _append_file(f: Path) -> None:
        rel_path = f.relative_to(styles_root.parent).as_posix()
        banner = f"/* ---------- {rel_path} ---------- */"
        pieces.append(banner)
        pieces.append(f.read_text(encoding="utf-8").rstrip())
        pieces.append("")  # blank line separator

    # 1-3: required tokens
    for f in required_files:
        _append_file(f)

    # 4-6: optional directories
    for d in optional_dirs_alpha:
        for f in _collect_alpha(d):
            _append_file(f)

    # 7: print file (always last)
    if print_file.exists():
        _append_file(print_file)

    return "\n".join(pieces)
```

- [ ] **Compat shim para Plan 1 tests**: os testes do Plan 1 assumiam que `base/fonts.css` aparecia logo após `density-compact.css`. Com a nova estratégia que descobre toda a pasta `base/` alfabeticamente, `fonts.css` vem primeiro, `global.css` segundo, etc. Confirmar com:

```bash
python -m pytest tests/test_ds_build_helpers.py::TestCompileDesignSystemCss::test_concatenates_tokens_in_cascade_order -q
```

Se o teste original falhar, ajustar o `assert` para aceitar a nova ordem (a ordem nos testes Plan 1 usa apenas `fonts.css` em `base/`, portanto continua a ser o único ficheiro encontrado e vem logo a seguir aos tokens). **Nenhum teste Plan 1 deve precisar ser alterado** se só `fonts.css` existir em `base/`.

- [ ] Correr `python -m pytest tests/test_ds_build_helpers.py -q`. Expected: **todos** os testes passam (20 Plan 1 + 5 novos = ≥ 25).

### Step 1.3: Commit Task 1

```bash
rtk git add scripts/ds_build_helpers.py tests/test_ds_build_helpers.py
rtk git commit -m "$(cat <<'EOF'
feat(ds): extend compile_design_system_css for base/chrome/components/print

Task 1 of Plan 4. The helper now discovers *.css files inside
shared/styles/{base,chrome,components}/ alphabetically, and treats
shared/styles/print/print.css as the last block. Matches spec Section 6.2
cascade order.

Added 5 regression tests covering:
- Full Plan 4 cascade order
- Missing base/ dir is OK
- Empty chrome/ dir is OK
- print/print.css is ALWAYS last even when other files sort after it
- components/ sits between chrome/ and print/

All 25+ existing ds_build_helpers tests continue to pass.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 1 verification
- [ ] `pytest tests/test_ds_build_helpers.py` todos passam
- [ ] `python scripts/build-all.py` ainda compila (sem regressões — os ficheiros `base/`, `chrome/`, `components/`, `print/` ainda podem estar vazios/inexistentes a esta altura)
- [ ] Commit criado

---

## Task 2: `shared/styles/base/reset.css`

**File:** `shared/styles/base/reset.css` (NEW)

**Invariante:** depois deste commit, o build passa, mas o reset só entra em efeito em elementos **ainda não estilizados** pelo CSS legado. Dado que o CSS legado no bloco 1 já tem `*` selectors com `box-sizing: border-box`, o reset novo é tipicamente inócuo.

### Step 2.1: Escrever o reset minimalista

- [ ] Criar `shared/styles/base/reset.css` com conteúdo:

```css
/* =========================================================================
 * Design System SGA — base/reset.css
 * =========================================================================
 * Modern CSS reset, adapted from Josh Comeau's reset (MIT). Only global
 * rules; component-specific resets live in their own files.
 * ========================================================================= */

*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
  -moz-tab-size: 4;
  tab-size: 4;
}

body {
  margin: 0;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

img, picture, video, canvas, svg {
  display: block;
  max-width: 100%;
}

button, input, select, textarea {
  font: inherit;
  color: inherit;
}

button {
  cursor: pointer;
  background: none;
  border: 0;
  padding: 0;
}

/* Prevent content from being stretched on narrow viewports */
p, h1, h2, h3, h4, h5, h6 {
  overflow-wrap: break-word;
}
```

**Cuidado**: o legado tem `button { background-color: #0094CF; ... }` em vários sítios. O reset acima tem `button { background: none }` que seria **mais específico em ordem** por vir **antes** do legado (o `{{DS_CSS}}` é injectado primeiro). Mas a specificity é igual — o legado ganha por ordem. Testar manualmente na Task 12 que nenhum botão legado ficou sem cor de fundo.

Se na smoke test houver botões legados partidos, remover a regra `button { background: none; border: 0; padding: 0; }` do reset e deixar apenas `cursor: pointer`. Documentar a decisão no commit.

### Step 2.2: Build + smoke test

- [ ] `python scripts/build-all.py`
- [ ] Abrir `packages/portal-coe/dist/Portal_COE_AWM.html` em Chrome
- [ ] Confirmar que o visual está **idêntico** ao baseline (o reset é dormente em relação ao legado)
- [ ] Verificar console sem erros

### Step 2.3: Commit

```bash
rtk git add shared/styles/base/reset.css
rtk git commit -m "$(cat <<'EOF'
feat(ds): add base/reset.css (modern CSS reset)

Task 2 of Plan 4. Introduces a minimal modern reset (box-sizing, margin,
font-smoothing, media block, button inherit) as the first member of the
base/ directory. The reset is consumed by compile_design_system_css() via
the Plan 4 Task 1 discovery logic.

Visual impact: none on COE (legacy CSS already normalizes box-sizing and
button styles). This file is infrastructure for the chrome migration to
follow.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2 verification
- [ ] Build OK
- [ ] Smoke test zero regressions
- [ ] Commit criado

---

## Task 3: `shared/styles/base/typography.css`

**File:** `shared/styles/base/typography.css` (NEW)

**Invariante:** define a hierarquia de headings DS, usa `tabular-nums` globalmente, e **não parte** a tipografia legada (que usa `Segoe UI`). O ficheiro aplica-se apenas a elementos com classes DS (`.ds-*`) — **não** define `body { font-family }` para não sobrescrever o legacy.

### Step 3.1: Escrever typography.css

- [ ] Criar `shared/styles/base/typography.css`:

```css
/* =========================================================================
 * Design System SGA — base/typography.css
 * =========================================================================
 * Heading hierarchy + tabular-nums scoped to DS-namespaced elements.
 * DOES NOT touch `body { font-family }` during the migration — the legacy
 * block 1 CSS still controls the overall font. Plan 6 will remove the
 * legacy override and let these rules take over globally.
 * ========================================================================= */

:where(.ds-shell-bar, .ds-sidebar, .ds-page-grid, .ds-splash, .ds-footer) {
  font-family: "Inter", -apple-system, BlinkMacSystemFont,
               "Segoe UI Variable", "Segoe UI", Roboto,
               "Helvetica Neue", Arial, sans-serif;
  font-variant-numeric: tabular-nums;
  font-feature-settings: "cv11", "ss01", "ss03";
}

.ds-page-grid h1.ds-page-title {
  font-size: var(--ds-text-2xl, 31px);
  line-height: 1.2;
  font-weight: 700;
  color: var(--ds-brand-primary);
  margin: 0 0 var(--ds-space-3, 6px);
}

.ds-page-grid p.ds-page-desc {
  font-size: var(--ds-text-sm, 13px);
  line-height: 1.5;
  color: var(--ds-neutral-fg-muted);
  margin: 0 0 var(--ds-space-6, 16px);
}

.ds-shell-bar .ds-clock,
.ds-shell-bar .ds-utc-clock {
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum";
  white-space: nowrap;
}
```

**Nota sobre `:where`**: usa specificity 0 propositadamente — se o legado tiver `body { font-family: ... }` ele ganha por specificity (0,0,1 > 0,0,0). Assim os elementos legados continuam Segoe UI e só os novos componentes com classes `ds-*` usam Inter. Plan 6 trocará este `:where` por selector normal quando o legado for limpo.

### Step 3.2: Build + smoke test

- [ ] `python scripts/build-all.py`
- [ ] Abrir dist COE em Chrome, confirmar que tudo continua Segoe UI (porque o novo chrome HTML ainda não foi injectado)

### Step 3.3: Commit

```bash
rtk git add shared/styles/base/typography.css
rtk git commit -m "$(cat <<'EOF'
feat(ds): add base/typography.css (Inter for DS-namespaced elements)

Task 3 of Plan 4. Typography rules scoped to .ds-* classes via :where()
(specificity 0), so legacy body/heading styles continue to win during
the migration. Only elements rendered inside .ds-shell-bar, .ds-sidebar,
.ds-page-grid, .ds-splash, .ds-footer will use Inter + tabular-nums.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 3 verification
- [ ] Build OK
- [ ] Visual baseline (nada mudou — ainda não há elementos `.ds-*` no HTML)
- [ ] Commit criado

---

## Task 4: `shared/styles/base/global.css`

**File:** `shared/styles/base/global.css` (NEW)

**Invariante:** define focus ring DS, selection color, `data-density` hook. **Não** redefine `body { background }` para não colidir com o legado (o legado usa `#e8f0fa` ou similar no canvas COE actual — manter até Plan 6).

### Step 4.1: Escrever global.css

- [ ] Criar `shared/styles/base/global.css`:

```css
/* =========================================================================
 * Design System SGA — base/global.css
 * =========================================================================
 * Global rules that are always safe during migration. Focus ring, selection,
 * data-density hook. DOES NOT touch body background — legacy still controls.
 * ========================================================================= */

:root {
  color-scheme: light;
}

/* Focus ring — applied to all interactive elements inside DS chrome */
:where(.ds-shell-bar, .ds-sidebar, .ds-page-grid, .ds-splash, .ds-footer)
  :is(a, button, input, select, textarea, [tabindex]):focus-visible {
  outline: var(--ds-focus-ring-width, 2px) solid var(--ds-focus-ring-color, #0073a0);
  outline-offset: var(--ds-focus-ring-offset, 2px);
  border-radius: var(--ds-radius-sm, 3px);
}

/* Selection color — neutral institutional */
::selection {
  background: rgba(0, 148, 207, 0.25);  /* --ds-brand-secondary-fill at 25% */
  color: inherit;
}

/* Respect reduced motion globally */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Density hook — :root data-density attribute set by build.py */
:root[data-density="compact"] {
  /* compact density tokens already loaded by density-compact.css */
}

:root[data-density="comfortable"] {
  /* comfortable density tokens already loaded by density-comfortable.css */
}
```

### Step 4.2: Build + smoke test

- [ ] `python scripts/build-all.py`
- [ ] Smoke test — verificar que `::selection` é ligeiramente azulada (selecionar texto na página)
- [ ] Verificar que elementos legados continuam com focus ring legado (não há `.ds-*` chrome ainda)

### Step 4.3: Commit

```bash
rtk git add shared/styles/base/global.css
rtk git commit -m "$(cat <<'EOF'
feat(ds): add base/global.css (focus ring, selection, reduced-motion)

Task 4 of Plan 4. Global rules that are safe during migration:
- Focus ring via :where() scoped to .ds-* chrome
- ::selection brand tint
- Global prefers-reduced-motion reset
- :root[data-density] hook placeholder

No regressions expected — no .ds-* elements exist in the HTML yet.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 4 verification
- [ ] Build OK
- [ ] ::selection is faint blue tint
- [ ] Commit criado

---

## Task 5: `shared/styles/chrome/shell-bar.css`

**File:** `shared/styles/chrome/shell-bar.css` (NEW)

**Invariante:** define a aparência do novo shell bar sem ainda existir HTML que o use. Verificar via build OK. Smoke test pode usar DevTools para inserir um nó de teste e ver o rendering.

### Step 5.1: Escrever shell-bar.css

- [ ] Criar `shared/styles/chrome/shell-bar.css` com conteúdo completo que implementa a Secção 4.1 da spec:

```css
/* =========================================================================
 * Design System SGA — chrome/shell-bar.css
 * =========================================================================
 * Top shell bar: light background, 3 zones, institutional 4px stripe,
 * UTC clock + local time + user badge, optional emergency pill.
 * ========================================================================= */

.ds-shell-bar {
  /* Layout */
  position: fixed;
  top: 0;
  inset-inline: 0;
  height: 56px;
  display: flex;
  align-items: center;
  /* Full padding shorthand (not padding-inline) to override the legacy
     `header { padding: 1rem 2rem; }` rule in block 1 — otherwise the
     legacy padding-top/bottom combined with height:56px + box-sizing
     would squeeze the content. Block-axis padding is 0 because the
     shell bar is vertically centered via align-items:center. */
  padding: 0 var(--ds-space-6, 16px);
  gap: var(--ds-space-6, 16px);

  /* Appearance */
  background: var(--ds-neutral-surface);
  color: var(--ds-neutral-fg);
  border-bottom: 1px solid var(--ds-neutral-muted);
  box-shadow: var(--ds-shadow-1, 0 1px 2px rgba(9,30,66,0.08));
  z-index: 100;
}

/* Institutional 4px stripe anchored directly below the bar */
.ds-shell-bar::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: -4px;
  height: 4px;
  background: var(--ds-brand-primary);
  pointer-events: none;
}

:root[data-density="comfortable"] .ds-shell-bar {
  height: 64px;
}

/* ---------- Zone: left (brand + OACI) ---------- */
.ds-shell-bar__brand {
  display: flex;
  align-items: center;
  gap: var(--ds-space-4, 8px);
  flex: 0 0 auto;
  min-width: 0;
}

.ds-shell-bar__logo {
  width: 32px;
  height: 32px;
  flex: 0 0 32px;
  color: var(--ds-brand-primary);
}

.ds-shell-bar__logo svg {
  width: 100%;
  height: 100%;
}

.ds-shell-bar__portal-name {
  font-size: var(--ds-text-md, 16px);
  font-weight: 600;
  color: var(--ds-brand-primary);
  white-space: nowrap;
}

.ds-shell-bar__separator {
  width: 1px;
  height: 20px;
  background: var(--ds-neutral-muted);
}

.ds-shell-bar__oaci {
  font-size: var(--ds-text-sm, 13px);
  color: var(--ds-neutral-fg-muted);
  font-weight: 500;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* ---------- Zone: centre (breadcrumb) ---------- */
.ds-shell-bar__breadcrumb {
  flex: 1 1 auto;
  display: flex;
  align-items: center;
  min-width: 0;
  font-size: var(--ds-text-sm, 13px);
  color: var(--ds-neutral-fg-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ds-shell-bar__breadcrumb-item + .ds-shell-bar__breadcrumb-item::before {
  content: "›";
  margin-inline: var(--ds-space-3, 6px);
  color: var(--ds-neutral-fg-subtle);
}

/* ---------- Zone: right (clocks + user + occurrence pill) ---------- */
.ds-shell-bar__meta {
  display: flex;
  align-items: center;
  gap: var(--ds-space-5, 12px);
  flex: 0 0 auto;
}

.ds-shell-bar__clocks {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.1;
}

.ds-shell-bar__utc {
  font-size: var(--ds-text-sm, 13px);
  font-weight: 600;
  color: var(--ds-neutral-fg);
  font-variant-numeric: tabular-nums;
}

.ds-shell-bar__local {
  font-size: var(--ds-text-xs, 11px);
  color: var(--ds-neutral-fg-muted);
  font-variant-numeric: tabular-nums;
}

.ds-shell-bar__operator {
  display: none;                         /* shown by JS when logged in */
  align-items: center;
  gap: var(--ds-space-2, 4px);
  padding: 2px var(--ds-space-4, 8px);
  background: var(--ds-neutral-subtle);
  color: var(--ds-neutral-fg);
  border-radius: var(--ds-radius-pill, 9999px);
  font-size: var(--ds-text-xs, 11px);
  font-weight: 600;
}

.ds-shell-bar__operator[data-logged-in="true"] {
  display: inline-flex;
}

.ds-shell-bar__logout {
  margin-inline-start: var(--ds-space-2, 4px);
  font-size: var(--ds-text-xs, 11px);
  color: var(--ds-brand-secondary-text);
  text-decoration: underline;
  cursor: pointer;
}

/* -------------------------------------------------------------------------
 * Legacy "Sair" button override — JS contract compatibility
 * -------------------------------------------------------------------------
 * The legacy COE JS injects the logout button via
 *   badge.innerHTML += ' <button onclick="logoutCOE()" style="background:
 *   rgba(255,255,255,0.25); border:1px solid rgba(255,255,255,0.4);
 *   color:white; ...">Sair</button>';
 * at ~lines 6256 and 10449 of Portal_COE_AWM.source.html. Those inline
 * styles were authored for the legacy gradient `#004C7B` header — on the
 * new white shell bar the button becomes white-on-white and invisible.
 *
 * We cannot touch the legacy JS (out of scope for Plan 4), so we neutralise
 * the inline colours at the CSS layer. `!important` is required here
 * because it is the ONLY CSS mechanism that outranks an element-level
 * `style="..."` attribute. This is a deliberate, scoped exception to the
 * normal "no !important" rule, justified by the legacy JS constraint.
 * Plan 6 should migrate the inline-styled button to a CSS class and
 * remove these overrides.
 * ------------------------------------------------------------------------- */
.ds-shell-bar__operator > button {
  background: var(--ds-neutral-subtle) !important;
  color: var(--ds-neutral-fg) !important;
  border: 1px solid var(--ds-neutral-muted) !important;
  border-radius: var(--ds-radius-sm, 3px) !important;
  padding: 2px var(--ds-space-3, 6px) !important;
  font-size: var(--ds-text-xs, 11px) !important;
  font-weight: 600 !important;
  cursor: pointer !important;
}

.ds-shell-bar__operator > button:hover {
  background: var(--ds-neutral-muted) !important;
  color: var(--ds-brand-primary) !important;
}

/* ---------- Emergency pill (pulsating red when occurrence active) ---------- */
.ds-shell-bar__emg-pill {
  display: none;
  align-items: center;
  gap: var(--ds-space-2, 4px);
  padding: 4px var(--ds-space-4, 8px);
  background: var(--ds-status-emergency-emphasis);
  color: var(--ds-status-emergency-on-emphasis);
  border-radius: var(--ds-radius-pill, 9999px);
  font-size: var(--ds-text-xs, 11px);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  animation: ds-emg-pulse 1.2s ease-in-out infinite;
}

.ds-shell-bar__emg-pill[data-active="true"] {
  display: inline-flex;
}

@keyframes ds-emg-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(139, 0, 0, 0.6); }
  50%      { box-shadow: 0 0 0 6px rgba(139, 0, 0, 0); }
}

@media (prefers-reduced-motion: reduce) {
  .ds-shell-bar__emg-pill { animation: none; }
}

/* ---------- Responsive: collapse breadcrumb <1024px ---------- */
@media (max-width: 1023px) {
  .ds-shell-bar__breadcrumb { display: none; }
}

@media (max-width: 767px) {
  .ds-shell-bar__local { display: none; }
  .ds-shell-bar__portal-name { display: none; }
}
```

### Step 5.2: Build + DevTools sanity check

- [ ] `python scripts/build-all.py`
- [ ] Abrir dist COE em Chrome DevTools, testar: `document.body.insertAdjacentHTML('afterbegin', '<header class="ds-shell-bar"><div class="ds-shell-bar__brand"><span class="ds-shell-bar__portal-name">Portal COE</span><span class="ds-shell-bar__separator"></span><span class="ds-shell-bar__oaci">FNMO</span></div><div class="ds-shell-bar__breadcrumb">Dashboard</div><div class="ds-shell-bar__meta"><div class="ds-shell-bar__clocks"><div class="ds-shell-bar__utc">UTC 12:34:56</div><div class="ds-shell-bar__local">Local 13:34</div></div></div></header>')`
- [ ] Verificar que aparece um shell bar light no topo da página com a faixa de 4 px azul SGA por baixo
- [ ] Remover o nó de teste (`document.querySelector('.ds-shell-bar').remove()`)

### Step 5.3: Commit

```bash
rtk git add shared/styles/chrome/shell-bar.css
rtk git commit -m "$(cat <<'EOF'
feat(ds): add chrome/shell-bar.css per spec Section 4.1

Task 5 of Plan 4. Full shell bar CSS: 56px height (compact) / 64px
(comfortable), 3 zones (brand / breadcrumb / meta), 4px institutional
SGA stripe via ::after, UTC + local clocks, operator badge, emergency
pill with pulse animation (disabled under prefers-reduced-motion).
Responsive: breadcrumb hides <1024px, local+portal-name hide <768px.

Includes a scoped !important override for the legacy "Sair" button
that the COE JS injects via operatorBadge.innerHTML with inline
rgba(255,255,255,...) styles designed for the old gradient header.
Without the override, the button would render white-on-white on the
new light shell bar. Comment in the CSS documents the justification.

No HTML consumer yet — Task 11 will inject .ds-shell-bar into the COE
source.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 5 verification
- [ ] Build OK
- [ ] DevTools insertion renders shell bar correctly
- [ ] Commit criado

---

## Task 6: `shared/styles/chrome/sidebar.css`

**File:** `shared/styles/chrome/sidebar.css` (NEW)

**Invariante:** define `.ds-sidebar` com 240 px (compact) / 256 px (comfortable), canvas light `#f6f8fa`, sem logo, nav items com `border-left: 3px` na active, **e** override para quando `.nav-btn` legada está dentro de `.ds-sidebar` (mantém o contrato legacy e aplica o visual DS).

### Step 6.1: Escrever sidebar.css

- [ ] Criar `shared/styles/chrome/sidebar.css`:

```css
/* =========================================================================
 * Design System SGA — chrome/sidebar.css
 * =========================================================================
 * Left navigation: 240px compact / 256px comfortable, light canvas,
 * no logo, section groups with uppercase headings, nav items with
 * border-left 3px brand-primary when active.
 *
 * IMPORTANT: nav items keep the legacy class `.nav-btn` so that the
 * openSection() JS handler in Portal_COE_AWM.source.html continues to
 * find them. The new visual rules are scoped to `.ds-sidebar .nav-btn`
 * so specificity wins over the legacy block 1 `.nav-btn { ... }` rules.
 * ========================================================================= */

.ds-sidebar {
  position: fixed;
  left: 0;
  top: 60px;                             /* 56px shell bar + 4px stripe */
  bottom: 0;
  width: 240px;
  background: var(--ds-neutral-canvas);
  border-right: 1px solid var(--ds-neutral-muted);
  overflow-y: auto;
  padding-block: var(--ds-space-5, 12px);
  z-index: 90;
}

:root[data-density="comfortable"] .ds-sidebar {
  width: 256px;
  top: 68px;  /* 64px shell bar + 4px stripe */
}

/* Section group */
.ds-sidebar__section {
  padding: 0 var(--ds-space-4, 8px);
  margin-bottom: var(--ds-space-6, 16px);
}

.ds-sidebar__section-title {
  margin: 0 0 var(--ds-space-2, 4px) var(--ds-space-4, 8px);
  font-size: var(--ds-text-xs, 11px);
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--ds-neutral-fg-muted);
}

.ds-sidebar__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Nav item — the legacy class `.nav-btn` is kept for JS contract,
   DS visual lives on `.ds-sidebar .nav-btn` with higher specificity. */
.ds-sidebar .nav-btn {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3, 6px);
  height: var(--ds-nav-item-height, 36px);
  padding: 0 var(--ds-space-4, 8px);
  border-left: 3px solid transparent;
  border-radius: var(--ds-radius-sm, 3px);
  font-size: var(--ds-text-sm, 13px);
  font-weight: 500;
  color: var(--ds-neutral-fg-muted);
  text-decoration: none;
  transition: background var(--ds-transition-fast, 120ms),
              color var(--ds-transition-fast, 120ms);
  /* reset legacy block 1 anchor padding */
  white-space: nowrap;
}

.ds-sidebar .nav-btn:hover {
  background: var(--ds-neutral-subtle);
  color: var(--ds-brand-primary);
}

.ds-sidebar .nav-btn.active {
  background: var(--ds-neutral-surface);
  color: var(--ds-brand-primary);
  font-weight: 600;
  border-left-color: var(--ds-brand-primary);
  box-shadow: var(--ds-shadow-1, 0 1px 2px rgba(9,30,66,0.08));
}

/* Icon slot for future sprite integration */
.ds-sidebar .nav-btn__icon {
  width: 18px;
  height: 18px;
  flex: 0 0 18px;
  color: currentColor;
}

/* Occurrence group — preserve the visual affordance from the legacy
   sidebar-section-simulacros without the dark blue context */
.ds-sidebar__section--occurrences .nav-btn {
  display: grid;
  grid-template-columns: 20px 1fr;
  align-items: center;
  gap: var(--ds-space-3, 6px);
  height: auto;
  padding-block: var(--ds-space-3, 6px);
}

.ds-sidebar__section--occurrences .sim-label {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.ds-sidebar__section--occurrences .sim-label-main {
  font-size: var(--ds-text-sm, 13px);
  font-weight: 600;
}

.ds-sidebar__section--occurrences .sim-label-sub {
  font-size: var(--ds-text-xs, 11px);
  color: var(--ds-neutral-fg-muted);
}

.ds-sidebar__section--occurrences .sim-track-emg .nav-btn.active {
  border-left-color: var(--ds-status-alert-emphasis);
}

.ds-sidebar__section--occurrences .sim-track-seg .nav-btn.active {
  border-left-color: var(--ds-cat-seg-ordem);
}

/* Sidebar footer (version) */
.ds-sidebar__footer {
  margin-top: auto;
  padding: var(--ds-space-5, 12px) var(--ds-space-4, 8px);
  border-top: 1px solid var(--ds-neutral-muted);
  font-size: var(--ds-text-xs, 11px);
  line-height: 1.4;
  color: var(--ds-neutral-fg-subtle);
  text-align: center;
}
```

### Step 6.2: Build + DevTools sanity check

- [ ] `python scripts/build-all.py`
- [ ] DevTools: inserir `<aside class="ds-sidebar"><div class="ds-sidebar__section"><h3 class="ds-sidebar__section-title">Principal</h3><ul class="ds-sidebar__list"><li><a href="#" class="nav-btn active">Dashboard</a></li><li><a href="#" class="nav-btn">Ocorrência</a></li></ul></div></aside>` e verificar visual

### Step 6.3: Commit

```bash
rtk git add shared/styles/chrome/sidebar.css
rtk git commit -m "$(cat <<'EOF'
feat(ds): add chrome/sidebar.css per spec Section 4.2

Task 6 of Plan 4. Light 240px sidebar (256px comfortable), no logo,
uppercase section titles, nav items with border-left 3px brand-primary
when .active. The legacy class .nav-btn is kept and visually re-styled
via higher-specificity .ds-sidebar .nav-btn rules, so openSection() JS
continues to work.

Occurrences group (sim-track-emg / sim-track-seg) preserves its
colour affordance using --ds-status-alert-emphasis for emergency track
and --ds-cat-seg-ordem for security track active state.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 6 verification
- [ ] Build OK
- [ ] DevTools insertion OK
- [ ] Commit criado

---

## Task 7: `shared/styles/chrome/page-grid.css`

**File:** `shared/styles/chrome/page-grid.css` (NEW)

**Invariante:** o `.ds-page-grid` respeita a shell bar 60 px + sidebar 240 px, canvas `#f6f8fa`, max-width 1440 px. **Não** colide com `.main-container` do legado (o legado fica até a Task 10 substituir o wrapper por `.ds-page-grid`).

### Step 7.1: Escrever page-grid.css

- [ ] Criar `shared/styles/chrome/page-grid.css`:

```css
/* =========================================================================
 * Design System SGA — chrome/page-grid.css
 * =========================================================================
 * Main content area: canvas background, left offset for sidebar, top
 * offset for shell bar + 4px stripe, max-width 1440px centered.
 * ========================================================================= */

.ds-page-grid {
  display: block;
  position: relative;
  margin-left: 240px;                   /* sidebar width — compact */
  margin-top: 60px;                     /* 56px shell bar + 4px stripe */
  min-height: calc(100vh - 60px);
  background: var(--ds-neutral-canvas);
  padding: var(--ds-space-7, 24px) var(--ds-space-7, 24px) 0;
}

:root[data-density="comfortable"] .ds-page-grid {
  margin-left: 256px;
  margin-top: 68px;
  min-height: calc(100vh - 68px);
  padding: var(--ds-space-8, 32px) var(--ds-space-8, 32px) 0;
}

.ds-page-grid__inner {
  max-width: 1440px;
  margin-inline: auto;
  padding-bottom: var(--ds-space-8, 32px);
}

/* Page header (h1 + desc) */
.ds-page-grid .ds-page-title {
  font-size: var(--ds-text-2xl, 31px);
  line-height: 1.2;
  font-weight: 700;
  color: var(--ds-brand-primary);
  margin: 0 0 var(--ds-space-3, 6px);
}

.ds-page-grid .ds-page-desc {
  font-size: var(--ds-text-sm, 13px);
  line-height: 1.5;
  color: var(--ds-neutral-fg-muted);
  margin: 0 0 var(--ds-space-6, 16px);
}

/* Section card grid */
.ds-page-grid .ds-section-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--ds-space-6, 16px);
}

/* Responsive */
@media (max-width: 1023px) {
  .ds-page-grid {
    margin-left: 0;
  }
}
```

### Step 7.2: Build + commit

- [ ] `python scripts/build-all.py`
- [ ] `rtk git add shared/styles/chrome/page-grid.css`
- [ ] Commit:

```bash
rtk git commit -m "$(cat <<'EOF'
feat(ds): add chrome/page-grid.css per spec Section 4.3

Task 7 of Plan 4. .ds-page-grid container with left offset (240px/256px)
and top offset (60px/68px) for shell bar + stripe, canvas background,
max-width 1440px inner wrapper, page header + section grid helpers.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 7 verification
- [ ] Build OK
- [ ] Commit criado

---

## Task 8: `shared/styles/chrome/splash.css`

**File:** `shared/styles/chrome/splash.css` (NEW)

**Invariante:** splash aparece fullscreen, fica visível por 1500 ms, faz fade-out, desaparece. Respeita `prefers-reduced-motion`. Tem escape hatch `?nosplash=1` (implementado na Task 11 JS).

### Step 8.1: Escrever splash.css

- [ ] Criar `shared/styles/chrome/splash.css`:

```css
/* =========================================================================
 * Design System SGA — chrome/splash.css
 * =========================================================================
 * Full-screen splash shown for ~1.5s on portal load. Contains SGA lockup,
 * portal name, DREA tagline, OACI, version. Fade-out after ds-splash-out
 * animation. Dismissed via data-state="out" (set by splash.js).
 * ========================================================================= */

.ds-splash {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--ds-neutral-surface);
  color: var(--ds-brand-primary);
  gap: var(--ds-space-5, 12px);
  opacity: 1;
  transition: opacity 400ms ease-out;
  pointer-events: all;
}

.ds-splash[data-state="out"] {
  opacity: 0;
  pointer-events: none;
}

/* Hide entirely once faded for accessibility tree cleanup */
.ds-splash[data-state="done"] {
  display: none;
}

.ds-splash__logo {
  width: 120px;
  height: 120px;
  color: var(--ds-brand-primary);
}

.ds-splash__logo svg {
  width: 100%;
  height: 100%;
}

.ds-splash__portal-name {
  font-size: var(--ds-text-2xl, 31px);
  font-weight: 700;
  color: var(--ds-brand-primary);
  margin: 0;
}

.ds-splash__tagline {
  font-size: var(--ds-text-sm, 13px);
  color: var(--ds-neutral-fg-muted);
  margin: 0;
  text-align: center;
  max-width: 480px;
  padding-inline: var(--ds-space-5, 12px);
}

.ds-splash__airport {
  font-size: var(--ds-text-xs, 11px);
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--ds-neutral-fg-subtle);
  margin-top: var(--ds-space-3, 6px);
}

.ds-splash__version {
  font-size: var(--ds-text-xs, 11px);
  color: var(--ds-neutral-fg-subtle);
  font-variant-numeric: tabular-nums;
}

.ds-splash::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 4px;
  background: var(--ds-brand-primary);
}

@media (prefers-reduced-motion: reduce) {
  .ds-splash {
    transition: none;
  }
}
```

### Step 8.2: Build + commit

- [ ] `python scripts/build-all.py`
- [ ] Commit:

```bash
rtk git add shared/styles/chrome/splash.css
rtk git commit -m "$(cat <<'EOF'
feat(ds): add chrome/splash.css per spec Section 4.4

Task 8 of Plan 4. .ds-splash full-screen overlay with lockup, portal
name, DREA tagline, airport OACI, version + 4px institutional stripe.
Fade-out driven by data-state="out" (splash.js sets it after 1500ms).
data-state="done" fully removes from tab order.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 8 verification
- [ ] Build OK
- [ ] Commit criado

---

## Task 9: `shared/styles/chrome/footer.css`

**File:** `shared/styles/chrome/footer.css` (NEW)

### Step 9.1: Escrever footer.css

- [ ] Criar `shared/styles/chrome/footer.css`:

```css
/* =========================================================================
 * Design System SGA — chrome/footer.css
 * =========================================================================
 * Institutional footer at the bottom of the page content (scroll-bottom,
 * not fixed). Single line with operator + portal + version + OACI + date.
 * ========================================================================= */

.ds-footer {
  padding: var(--ds-space-5, 12px) 0;
  margin-top: var(--ds-space-7, 24px);
  border-top: 1px solid var(--ds-neutral-muted);
  font-size: var(--ds-text-xs, 11px);
  color: var(--ds-neutral-fg-subtle);
  text-align: center;
  line-height: 1.4;
}

.ds-footer__sep::before {
  content: " · ";
}

.ds-footer a {
  color: var(--ds-brand-secondary-text);
  text-decoration: none;
}

.ds-footer a:hover {
  text-decoration: underline;
}
```

### Step 9.2: Commit

- [ ] `python scripts/build-all.py`
- [ ] Commit:

```bash
rtk git add shared/styles/chrome/footer.css
rtk git commit -m "$(cat <<'EOF'
feat(ds): add chrome/footer.css per spec Section 4.5

Task 9 of Plan 4. Thin institutional footer at the end of page content
(scroll-bottom by design). Single centred line with configurable
separators.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 9 verification
- [ ] Build OK
- [ ] Commit criado

---

## Task 10: `shared/styles/print/print.css`

**File:** `shared/styles/print/print.css` (NEW)

**Invariante:** esconde `.ds-shell-bar` + `.ds-sidebar` + `.ds-splash` em `@media print`; adiciona `@page` header com logo + airport + section + timestamp; paginação com `counter(page)`; respeita CSS Paged Media para repetição em cada página.

### Step 10.1: Escrever print.css

- [ ] Criar `shared/styles/print/print.css`:

```css
/* =========================================================================
 * Design System SGA — print/print.css
 * =========================================================================
 * Print stylesheet. Hides interactive chrome, offsets page content,
 * prints document header in @page area with airport + portal + section
 * + timestamp. Uses counter(page) for pagination.
 * ========================================================================= */

@media print {
  .ds-shell-bar,
  .ds-sidebar,
  .ds-splash,
  .ds-footer,
  .header,                              /* legacy fallback */
  .sidebar,                             /* legacy fallback */
  .main-container > header              /* legacy fallback */
  {
    display: none !important;
  }

  html, body {
    background: #ffffff !important;
    color: #000000 !important;
    font-size: 10pt !important;
  }

  .ds-page-grid {
    margin: 0 !important;
    padding: 0 !important;
    background: #ffffff !important;
  }

  .ds-page-grid__inner {
    max-width: none !important;
  }

  /* Cards lose their shadows and keep their borders for legibility */
  .ds-card, .stat-card {
    box-shadow: none !important;
    border: 1px solid #cccccc !important;
    break-inside: avoid;
  }

  /* Tables */
  table {
    border-collapse: collapse !important;
    width: 100% !important;
  }

  thead {
    display: table-header-group !important;  /* repeat on each page */
  }

  tr {
    break-inside: avoid !important;
  }

  /* Avoid orphan headings */
  h1, h2, h3, h4 {
    break-after: avoid;
  }

  /* URL output */
  a[href^="http"]::after {
    content: " (" attr(href) ")";
    font-size: 9pt;
    color: #555;
  }

  /* Hide sections that are not the active one */
  .section:not(.active) { display: none !important; }
}

/* @page — document header and footer on each printed page */
@page {
  size: A4;
  margin: 3cm 1.5cm 2cm;

  @top-left {
    content: "SGA — Sociedade de Gestão Aeroportuária";
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 9pt;
    color: #004C7B;
  }

  @top-right {
    content: "Portal COE · FNMO";
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 9pt;
    color: #004C7B;
  }

  @bottom-left {
    content: "Confidencial · Impresso via Portal COE";
    font-size: 8pt;
    color: #888;
  }

  @bottom-right {
    content: "Página " counter(page) " de " counter(pages);
    font-size: 8pt;
    color: #888;
    font-variant-numeric: tabular-nums;
  }
}

@page :first {
  margin-top: 4cm;  /* extra room for first-page hero */
}
```

**Nota sobre placeholders dinâmicos no `@page`**: Chrome suporta `content: "..."` literal mas **não** placeholders tipo `{{PORTAL.NAME}}`. Dois caminhos:

1. **Hard-coded "Portal COE · FNMO"** (simples, suficiente para FNMO) — é o que acima está
2. **Build-time substitution** — usar `{{PORTAL.NAME_SHORT}} · {{AIRPORT.OACI}}` no string do print.css e deixar o `compile_design_system_css()` passar por `substitute_placeholders` antes de injectar. **Adiar para Plan 6** quando os placeholders forem normalizados.

A escolha pragmática é (1). Documentar no commit.

### Step 10.2: Build + print preview smoke test

- [ ] `python scripts/build-all.py`
- [ ] Abrir dist COE, `Ctrl+P`, verificar print preview em Chrome:
  - Cabeçalho top-left "SGA — Sociedade..." visível
  - Paginação bottom-right "Página 1 de X"
  - Shell bar + sidebar ausentes (quando Tasks 11+ adicionam o HTML, este teste torna-se mais significativo)

### Step 10.3: Commit

```bash
rtk git add shared/styles/print/print.css
rtk git commit -m "$(cat <<'EOF'
feat(ds): add print/print.css per spec Section 4.6

Task 10 of Plan 4. @media print hides DS chrome + legacy chrome,
resets layout margins, forces page-break rules for cards/tables,
adds URL exposure for external links, hides non-active sections.

@page rule adds document header (operator + portal + airport OACI)
and footer (confidentiality + page counter) via CSS Paged Media.
First page gets extra top margin for hero area.

Portal name + OACI are hardcoded in @top-right — build-time substitution
deferred to Plan 6 normalization.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 10 verification
- [ ] Build OK
- [ ] Ctrl+P preview shows @page header
- [ ] Commit criado

---

## Task 10.5: Extend `shared/assets/icons/sprite.svg` with `icon-siren`

**File:** `shared/assets/icons/sprite.svg` (MODIFY)

**Invariante:** o novo chrome HTML (Task 11) referencia `<use href="#icon-siren"/>` no elemento `.ds-shell-bar__emg-pill`. O sprite actual (`bc11d89` @ `main`) contém apenas `icon-sga-mark`, `icon-menu`, `icon-close`. Sem esta task, o pill renderiza um `<svg>` vazio quando uma ocorrência fica activa.

**Audit referencial**: nesta task, confirmar por `grep` que os **únicos** `<use href="#icon-*"/>` referenciados pelo novo chrome HTML da Task 11 são:
- `#icon-sga-mark` — já existe, OK
- `#icon-siren` — a ser adicionado nesta task

Os glifos das tracks de simulacro (`✈`, `🛡`, `❓`, `⚙`) são caracteres Unicode herdados do legado, **não** referências ao sprite. Se no futuro se decidir migrá-los para `<use>`, adicionar os símbolos correspondentes numa task à parte.

### Step 10.5.1: Add `icon-siren` symbol

- [ ] Abrir `shared/assets/icons/sprite.svg` e adicionar um novo `<symbol>` antes do `</svg>` de fecho, após o `icon-close`. Conteúdo a adicionar:

```xml
  <symbol id="icon-siren" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
    <title>Ocorrência activa</title>
    <!-- Heroicons-style megaphone / siren: horn body + stand + sound waves -->
    <path d="M3.75 10.5v3l9.75 4.5V6L3.75 10.5z" />
    <path d="M13.5 7.5v9" />
    <path d="M7.5 13.5v3.75a1.5 1.5 0 0 0 3 0V15" />
    <path d="M17.25 9a3.75 3.75 0 0 1 0 6" />
  </symbol>
```

**Rationale**: Heroicons Outline v2 não tem um "siren" puro, mas o "megaphone" é semanticamente equivalente para "alerta activo" e encaixa nas mesmas convenções do sprite (viewBox 24×24, `stroke="currentColor"`, `stroke-width: 1.75`, `<title>` para a11y). As 4 paths desenham: corpo do horn (path 1), linha vertical de fecho da abertura (path 2), o stand/cabo pendurado (path 3), e a onda sonora (path 4). Renderiza bem a 14 px no pill do shell bar.

- [ ] Verificar visual: abrir `shared/assets/icons/sprite.svg` num browser com uma página stub que renderiza `<svg width="32" height="32" stroke="#8B0000"><use href="sprite.svg#icon-siren"/></svg>`. Confirmar que se reconhece visualmente como um ícone de alerta.

### Step 10.5.2: Build + sanity check

- [ ] `python scripts/build-all.py` — build deve continuar OK (o sprite é parte da cadeia de assets copiados ou inlined consoante o pipeline; Plan 1/2 já estabeleceu a plumbing).
- [ ] Verificar que `dist/Portal_COE_AWM.html` ainda abre sem erros de console. O pill do `ds-shell-bar__emg-pill` ainda não está no DOM (Task 11 é que o injecta), portanto esta task é **visualmente dormente** até lá.

### Step 10.5.3: Commit Task 10.5

```bash
rtk git add shared/assets/icons/sprite.svg
rtk git commit -m "$(cat <<'EOF'
feat(ds): add icon-siren symbol to sprite for shell bar emergency pill

Task 10.5 of Plan 4. The new ds-shell-bar__emg-pill (Task 11 HTML)
references <use href="#icon-siren"/>. Previously the sprite only had
icon-sga-mark, icon-menu, icon-close. Without this commit the pill
would render an empty SVG when an occurrence is active.

Uses a Heroicons-style megaphone path (4 strokes: horn body, closing
line, hanging cable, sound wave) with stroke-width 1.75 to match the
existing sprite conventions. Semantically "megaphone = alert active"
is equivalent to "siren" for this use case.

Other domain icons from spec Section 5.5 (icon-user, icon-shield,
icon-airplane, icon-helmet, icon-fire) are NOT added here — they are
not referenced by any Plan 4 HTML and are deferred to Plan 6.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 10.5 verification
- [ ] `icon-siren` symbol present in `shared/assets/icons/sprite.svg`
- [ ] `python scripts/build-all.py` exit 0
- [ ] No other `<use href="#icon-*"/>` in Task 11 HTML references a missing symbol (only `#icon-sga-mark` and `#icon-siren` are used; both now exist)
- [ ] Commit criado

---

## Task 11: HTML surgery — swap the COE chrome

**File:** `packages/portal-coe/src/Portal_COE_AWM.source.html` (MODIFY)

Esta é a **task crítica** — substitui ~100 linhas de HTML num commit atómico. Requer cuidado máximo com o JS contract.

**Pré-requisitos:**
- Tasks 5–9 concluídas (ficheiros CSS existem)
- `logo-sga-mark.svg` existe em `shared/assets/` (Task 0)
- `compile_design_system_css` descobre todos esses ficheiros (Task 1)

### Step 11.1: Dry-run — construir o novo HTML num scratch

- [ ] Abrir `packages/portal-coe/src/Portal_COE_AWM.source.html` e localizar:
  - Linha 3179 (`<div class="sidebar">`) — início do bloco sidebar
  - Linha 3251 (`</div>` que fecha o sidebar)
  - Linha 3253 (`<div class="main-container">`)
  - Linha 3255 (`<header>`)
  - Linha 3269 (`</header>`)

- [ ] Planear o novo bloco como um único `Edit` que substitui de 3179 a 3269. Estrutura final:

```html
<!-- ======================================================================
     Splash screen (Plan 4 Task 11) — fade-out via splash.js after 1500ms
     Bypass: append ?nosplash=1 to URL
     ====================================================================== -->
<div class="ds-splash" id="dsSplash" data-state="in" role="status" aria-live="polite">
    <div class="ds-splash__logo">
        <svg viewBox="0 0 32 32" aria-hidden="true"><use href="#icon-sga-mark"/></svg>
    </div>
    <h1 class="ds-splash__portal-name">{{PORTAL.NAME}}</h1>
    <p class="ds-splash__tagline">DREA · Direcção de Resposta a Emergências Aeroportuárias</p>
    <p class="ds-splash__airport">{{AIRPORT.OACI}} · {{AIRPORT.NAME}}</p>
    <p class="ds-splash__version">v{{VERSION}} · {{BUILD_DATE_SHORT}}</p>
</div>

<!-- ======================================================================
     DS Shell Bar (replaces legacy <header>) — Plan 4 Task 11
     Preserves JS IDs: clockDisplay, headerUTC, headerDate, operatorBadge
     ====================================================================== -->
<header class="ds-shell-bar" role="banner">
    <div class="ds-shell-bar__brand">
        <span class="ds-shell-bar__logo" aria-hidden="true">
            <svg viewBox="0 0 32 32"><use href="#icon-sga-mark"/></svg>
        </span>
        <span class="ds-shell-bar__portal-name">{{PORTAL.NAME}}</span>
        <span class="ds-shell-bar__separator" aria-hidden="true"></span>
        <!-- Dual class: ds-shell-bar__oaci provides the DS visual; header-title-small
             preserves the legacy JS contract (cfgApplyToPortal() writes the airport
             name into document.querySelector('.header-title-small') at ~line 11097
             of the source). Without this class, operator config swaps would silently
             stop updating the displayed airport identifier. -->
        <span class="ds-shell-bar__oaci header-title-small">{{AIRPORT.OACI}}</span>
    </div>

    <div class="ds-shell-bar__breadcrumb" aria-label="Navigation breadcrumb">
        <span class="ds-shell-bar__breadcrumb-item" id="dsBreadcrumbCurrent">Dashboard</span>
    </div>

    <div class="ds-shell-bar__meta">
        <div class="ds-shell-bar__emg-pill" id="dsEmgPill" aria-live="polite">
            <svg class="ds-shell-bar__emg-pill-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#icon-siren"/></svg>
            <span>OCORRÊNCIA ACTIVA</span>
            <span id="dsEmgPillChrono">00:00:00</span>
        </div>

        <div class="ds-shell-bar__clocks">
            <!-- IDs preserved for existing updateHeaderClock() JS -->
            <div class="ds-shell-bar__utc" id="headerUTC">UTC 00:00:00</div>
            <div class="ds-shell-bar__local" id="clockDisplay">00:00:00</div>
            <div class="ds-shell-bar__local" id="headerDate" style="display:none;"></div>
        </div>

        <div class="ds-shell-bar__operator" id="operatorBadge" data-logged-in="false"></div>
    </div>
</header>

<!-- ======================================================================
     DS Sidebar (replaces legacy <div class="sidebar">) — Plan 4 Task 11
     Preserves nav-btn class + openSection('X', event) onclick contract
     ====================================================================== -->
<aside class="ds-sidebar" role="navigation" aria-label="Navegação principal">
    <div class="ds-sidebar__section">
        <h3 class="ds-sidebar__section-title">Principal</h3>
        <ul class="ds-sidebar__list">
            <li><a href="#" onclick="openSection('dashboard', event)" class="nav-btn active">Dashboard</a></li>
            <li><a href="#" onclick="openSection('cronometro', event)" class="nav-btn">Ocorrência</a></li>
            <li><a href="#" onclick="openSection('contactos', event)" class="nav-btn">Contactos</a></li>
            <li><a href="#" onclick="openSection('verif-contactos', event)" class="nav-btn">✓ Verificação Mensal</a></li>
            <li><a href="#" onclick="openSection('mapas', event)" class="nav-btn">Mapas Quadrícula</a></li>
            <li><a href="#" onclick="openSection('fluxogramas', event)" class="nav-btn">Fluxogramas</a></li>
        </ul>
    </div>

    <div class="ds-sidebar__section ds-sidebar__section--occurrences sidebar-section-simulacros">
        <h3 class="ds-sidebar__section-title">Ocorrências</h3>
        <ul class="ds-sidebar__list">
            <li class="sim-track-emg sim-track-first">
                <a href="#" onclick="openSection('guia-emg', event)" class="nav-btn sim-item">
                    <span class="sim-ico" aria-hidden="true">✈</span>
                    <span class="sim-label"><span class="sim-label-main">Emergência</span><span class="sim-label-sub">Guia</span></span>
                </a>
            </li>
            <li class="sim-track-emg">
                <a href="#" onclick="openSection('fichas-emg', event)" class="nav-btn sim-item">
                    <span class="sim-ico" aria-hidden="true">✈</span>
                    <span class="sim-label"><span class="sim-label-main">Emergência</span><span class="sim-label-sub">Fichas</span></span>
                </a>
            </li>
            <li class="sim-track-seg sim-track-first">
                <a href="#" onclick="openSection('guia-seg', event)" class="nav-btn sim-item">
                    <span class="sim-ico" aria-hidden="true">🛡</span>
                    <span class="sim-label"><span class="sim-label-main">Segurança</span><span class="sim-label-sub">Guia</span></span>
                </a>
            </li>
            <li class="sim-track-seg">
                <a href="#" onclick="openSection('fichas-seg', event)" class="nav-btn sim-item">
                    <span class="sim-ico" aria-hidden="true">🛡</span>
                    <span class="sim-label"><span class="sim-label-main">Segurança</span><span class="sim-label-sub">Fichas</span></span>
                </a>
            </li>
        </ul>
    </div>

    <div class="ds-sidebar__section">
        <h3 class="ds-sidebar__section-title">Documentação</h3>
        <ul class="ds-sidebar__list">
            <li><a href="#" onclick="openSection('documentacao', event)" class="nav-btn">PEA/PCA/PSA</a></li>
            <li><a href="#" onclick="openSection('referencias', event)" class="nav-btn">Referências</a></li>
        </ul>
    </div>

    <div class="ds-sidebar__section">
        <h3 class="ds-sidebar__section-title">Sistema</h3>
        <ul class="ds-sidebar__list">
            <li><a href="#" onclick="openSection('ajuda', event)" class="nav-btn">❓ Guia Rápido</a></li>
            <li><a href="#" onclick="openSection('configuracoes', event)" class="nav-btn">⚙ Configurações</a></li>
        </ul>
    </div>

    <div class="ds-sidebar__footer">
        <div style="font-weight:600;color:var(--ds-neutral-fg);">Portal COE</div>
        <div>v{{VERSION}} · {{BUILD_DATE_SHORT}}</div>
        <div>{{AIRPORT.OACI}} · {{AIRPORT.OPERATOR_SHORT}}</div>
    </div>
</aside>

<main class="ds-page-grid" id="dsPageGrid" role="main">
    <div class="ds-page-grid__inner">
```

E no fim, onde antes fechava `</div><!-- /main-container -->` (linha 11280), fechar com:

```html
    </div><!-- /.ds-page-grid__inner -->

    <footer class="ds-footer">
        SGA — Sociedade de Gestão Aeroportuária
        <span class="ds-footer__sep"></span>
        {{PORTAL.NAME}} v{{VERSION}}
        <span class="ds-footer__sep"></span>
        {{AIRPORT.OACI}}
        <span class="ds-footer__sep"></span>
        {{BUILD_DATE_SHORT}}
    </footer>
</main><!-- /.ds-page-grid -->
```

### Step 11.2: Execute o swap via dois Edits

- [ ] **Primeiro Edit** — substituir o bloco sidebar + header + início do main-container (linhas 3179 a 3254, **até antes de `<!-- Header -->`** fechado em 3269 e `<!-- Main Content -->` começar em 3271). Usar a ferramenta `Edit` com `old_string` = o bloco completo actual da sidebar + header legados e `new_string` = o novo shell bar + sidebar + splash + início do `.ds-page-grid`.

Para poder fazer isto com o `Edit` tool, ler primeiro o bloco inteiro via `Read` com um offset preciso (e.g. linhas 3175-3275). Se a linha 3257 for longa demais para `Read`, partir em dois Edits mais pequenos:

1. **Edit A**: substituir o bloco sidebar completo (linhas 3179 a 3251). `old_string` começa em `    <div class="sidebar">` e acaba em `    </div>` que fecha o sidebar.
2. **Edit B**: substituir o bloco header + main-container open (linhas 3253 a 3269/3270). `old_string` começa em `    <div class="main-container">` e acaba em `        </header>` (incluindo o comment `<!-- Main Content -->` logo a seguir, se ajudar a disambiguar).

- [ ] **Segundo Edit** — substituir o fecho `</div> <!-- /main-container -->` (linha 11280) por `        </div><!-- /.ds-page-grid__inner -->\n\n        <footer class="ds-footer">...</footer>\n    </main><!-- /.ds-page-grid -->`

### Step 11.3: Build após as edições

- [ ] `python scripts/build-all.py`. Expected: build OK (sem erro de sintaxe HTML, node --check passa).

**Se falhar**: o erro mais provável é um placeholder `{{...}}` não resolvido ou um `<div>` não fechado. Usar `git diff packages/portal-coe/src/Portal_COE_AWM.source.html` para inspeccionar diff.

### Step 11.4: Smoke test manual

- [ ] Abrir `packages/portal-coe/dist/Portal_COE_AWM.html` em Chrome
- [ ] Confirmar que o splash aparece por ~1500 ms. **Se não aparece ou não desaparece**, a Task 12 (JS do splash) ainda não corre — aceitável. Pode aparecer e ficar visível permanentemente até à Task 12; usar `?nosplash=1` para simular o by-pass OU remover manualmente via DevTools (`document.getElementById('dsSplash').remove()`).
- [ ] Após dismissar o splash, confirmar:
  - Shell bar branco no topo com faixa 4 px azul SGA abaixo
  - Sidebar light 240 px à esquerda com os 4 grupos e 14 nav items
  - Canvas `#f6f8fa` na área de conteúdo
  - Login funciona (clicar em Entrar)
- [ ] **CRITICAL JS CONTRACT CHECK** — na consola do browser:
  ```javascript
  document.querySelectorAll('.nav-btn').length
  // Expected: 14 (ou mais se Plan 3 adicionou items)

  document.getElementById('clockDisplay')  // != null
  document.getElementById('headerUTC')     // != null
  document.getElementById('headerDate')    // != null
  document.getElementById('operatorBadge') // != null

  // Legacy selector used by cfgApplyToPortal() (~line 11097 of source):
  document.querySelector('.header-title-small')  // != null  (on ds-shell-bar__oaci)

  typeof openSection  // "function"
  ```
- [ ] Navegar por cada uma das 14 secções, confirmar que abrem e que a classe `.active` migra correctamente no sidebar.
- [ ] Esperar 2 segundos e confirmar que `headerUTC` e `clockDisplay` estão a actualizar.

**Se qualquer check falha**: fazer `git reset --hard HEAD` no worktree e investigar. Não avançar para Task 12 com o JS contract partido.

### Step 11.5: Commit

```bash
rtk git add packages/portal-coe/src/Portal_COE_AWM.source.html
rtk git commit -m "$(cat <<'EOF'
feat(coe): replace legacy header+sidebar with DS shell bar + sidebar

Task 11 of Plan 4. Swap the COE chrome HTML:
- <header> gradient SGA       → <header class="ds-shell-bar">
- <div class="sidebar">       → <aside class="ds-sidebar">
- <div class="main-container">→ <main class="ds-page-grid">
- splash overlay added at top of body
- ds-footer added at end of main

Preserved invariants (JS contract):
- 14 <a class="nav-btn" onclick="openSection('X', event)"> items
  (sections: dashboard, cronometro, contactos, verif-contactos, mapas,
  fluxogramas, guia-emg, fichas-emg, guia-seg, fichas-seg, documentacao,
  referencias, ajuda, configuracoes)
- IDs clockDisplay, headerUTC, headerDate, operatorBadge all retained
- sim-track-emg, sim-track-seg, sim-item, sim-label-main, sim-label-sub
  classes preserved so legacy occurrence track styling continues
- openSection() JS handler unchanged (lives in block at line ~9946)
- class="header-title-small" kept as a dual class on ds-shell-bar__oaci
  so cfgApplyToPortal() (around line 11097 of the source) continues to
  write the airport name into the shell bar when the operator swaps the
  configuration at runtime. Without this dual class the guard
  `if (hdrSub && a.nome)` would silently become a no-op.

Legacy chrome CSS (.sidebar, .header-left, header, .main-container, etc.)
is no longer referenced by any HTML element — becomes dead CSS. Plan 6
will remove it.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 11 verification
- [ ] Build OK
- [ ] `document.querySelectorAll('.nav-btn').length >= 14`
- [ ] 4 IDs críticos presentes no DOM
- [ ] 14 nav clicks OK
- [ ] Relógio local + UTC a actualizar
- [ ] Zero erros de console
- [ ] Commit criado

---

## Task 12: JavaScript for splash + utility extraction

**Files:**
- `shared/scripts/chrome/splash.js` (NEW)
- `shared/scripts/utilities/date-utc.js` (NEW)
- `packages/portal-coe/src/Portal_COE_AWM.source.html` (MODIFY — add inline script near end of `<body>` or include via `{{DS_JS}}` placeholder if Plan 3 already set it up)

**Out of scope for this task**: `ls-wrapper.js` and `esc-html.js` were removed from Plan 4's scope (see File Structure section note). They are not consumed by any Plan 4 CSS/HTML and are deferred to Plan 5 / Plan 6 respectively.

**Decisão de integração:** existem dois caminhos para injectar o JS:

- **Caminho inline**: colar o script directamente no source HTML com um comentário `<!-- Plan 4 splash lifecycle -->`. Simples e sem alterações a `build.py`. Recomendado.
- **Caminho via `{{DS_JS}}`**: se Plan 3 já introduziu o placeholder `{{DS_JS}}` e uma função `compile_design_system_js()`, estender essa função para concatenar `shared/scripts/utilities/*.js` + `shared/scripts/chrome/*.js` e deixar o build substituir o placeholder.

**Verificar na Task 0**: `grep -n '{{DS_JS}}' packages/portal-coe/src/Portal_COE_AWM.source.html`. Se o placeholder existe, usar Caminho B; senão usar Caminho A.

Este plano documenta **Caminho A** (inline), que é auto-suficiente. Se o Caminho B já existir, adaptar: os ficheiros `shared/scripts/utilities/date-utc.js` e `shared/scripts/chrome/splash.js` criam-se na mesma, e o pipeline de `compile_design_system_js()` descobre-os automaticamente.

### Step 12.1: Verify `shared/scripts/utilities/` exists (may be empty)

- [ ] `ls -la shared/scripts/utilities/ 2>&1` — a directoria pode estar vazia ou inexistente. Se não existir, criá-la. Plan 4 apenas escreve `date-utc.js` nesta directoria; não toca em `ls-wrapper.js` nem `esc-html.js` (ambos out of scope — ver nota no File Structure).

### Step 12.2: Create `shared/scripts/utilities/date-utc.js`

- [ ] Criar `shared/scripts/utilities/date-utc.js`:

```javascript
/*!
 * Design System SGA — utilities/date-utc.js
 * ------------------------------------------------------------
 * UTC clock ticker used by the shell bar. Provides a single
 * setInterval that updates the headerUTC, clockDisplay and
 * headerDate elements once a second. If these elements already
 * have another updater (legacy updateHeaderClock in COE source),
 * this file is a no-op — it checks for a dsDateUtcInstalled flag
 * before installing its own ticker.
 *
 * Usage: included via {{DS_JS}} or inline before </body>.
 * ============================================================ */
(function () {
    'use strict';

    if (window.dsDateUtcInstalled) return;

    function tick() {
        var now = new Date();
        var timeLocal = now.toLocaleTimeString('pt-PT', { hour12: false });
        var timeUtc = now.toLocaleTimeString('pt-PT', { hour12: false, timeZone: 'UTC' });

        var utcEl = document.getElementById('headerUTC');
        if (utcEl) utcEl.textContent = 'UTC ' + timeUtc;

        var localEl = document.getElementById('clockDisplay');
        if (localEl) localEl.textContent = timeLocal;

        // Also update dashboard clock if present (legacy)
        var dbClock = document.getElementById('dashboardClock'); if (dbClock) dbClock.textContent = timeLocal;
        var dbUTC = document.getElementById('dashboardUTC'); if (dbUTC) dbUTC.textContent = 'UTC ' + timeUtc;
    }

    // If the legacy updateHeaderClock is already installed (COE source),
    // don't double-tick — the legacy function already handles everything.
    if (typeof window.updateHeaderClock === 'function') {
        window.dsDateUtcInstalled = true;
        return;
    }

    tick();
    setInterval(tick, 1000);
    window.dsDateUtcInstalled = true;
})();
```

**Rationale**: this file is a fallback for portals that don't yet have their own clock updater (e.g. future SSCI migration in Plan 5). For the COE source, the existing `updateHeaderClock()` function already handles all the IDs, so `dsDateUtcInstalled` short-circuits and no duplicate ticker runs. **Zero memory leaks**, **zero double-writes**.

### Step 12.3: Create `shared/scripts/chrome/splash.js`

- [ ] Criar `shared/scripts/chrome/splash.js`:

```javascript
/*!
 * Design System SGA — chrome/splash.js
 * ------------------------------------------------------------
 * Splash screen lifecycle:
 *   data-state="in"   (rendered by build HTML)
 *   data-state="out"  (set at 1500ms → CSS fades opacity to 0)
 *   data-state="done" (set at 1900ms → CSS sets display:none)
 *
 * Bypass: any URL with ?nosplash=1 sets state="done" immediately.
 *
 * Does NOT block other init code — this runs right away and does
 * not await anything. Sections are free to initialize underneath.
 * ============================================================ */
(function () {
    'use strict';

    function dismiss(splash) {
        splash.setAttribute('data-state', 'done');
    }

    function init() {
        var splash = document.getElementById('dsSplash');
        if (!splash) return;

        // Bypass via URL param
        try {
            var params = new URLSearchParams(window.location.search);
            if (params.get('nosplash') === '1') {
                dismiss(splash);
                return;
            }
        } catch (_) { /* IE11 — ignore */ }

        // Start fade-out at 1500ms
        setTimeout(function () {
            splash.setAttribute('data-state', 'out');
        }, 1500);

        // Fully remove from tab order at 1500 + 400 = 1900ms
        setTimeout(function () {
            dismiss(splash);
        }, 1900);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
```

### Step 12.4: Inline the scripts into the COE source HTML

- [ ] Abrir `packages/portal-coe/src/Portal_COE_AWM.source.html` e localizar o **último** `</script>` block antes de `</body>` (o source tem ~15150 linhas no estado `bc11d89`; o último `</script>` fica por volta da linha 15140 — use `grep -n '</script>' packages/portal-coe/src/Portal_COE_AWM.source.html | tail -3` para anchor exacto, **nunca** dependa de uma linha hard-coded porque o source cresce entre planos). **Adicionar o novo `<script>` imediatamente APÓS** esse último `</script>` (ou seja, já não existe outro `<script>` entre o novo bloco e `</body>`). Isto garante que `openSection`, `updateHeaderClock` e todos os handlers legados estão já definidos quando o splash lifecycle começa a correr:

```html
<!-- Plan 4 Task 12 — Design System splash + utilities -->
<script>
/* ==== shared/scripts/chrome/splash.js (inlined) ==== */
(function(){'use strict';function dismiss(s){s.setAttribute('data-state','done');}function init(){var s=document.getElementById('dsSplash');if(!s)return;try{var p=new URLSearchParams(window.location.search);if(p.get('nosplash')==='1'){dismiss(s);return;}}catch(e){}setTimeout(function(){s.setAttribute('data-state','out');},1500);setTimeout(function(){dismiss(s);},1900);}if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}})();
</script>
```

**Nota**: minificação manual acima. Se o worker preferir manter legibilidade, copiar o ficheiro todo entre `<script>` e `</script>`. Ambos são aceitáveis — o build é determinístico em qualquer caso.

**Alternativa elegante**: deixar o source HTML referir um placeholder `<script>{{DS_CHROME_JS}}</script>` e estender `ds_build_helpers.py` com uma função `compile_design_system_chrome_js()`. Adiar se Plan 3 ainda não construiu o `{{DS_JS}}` pipeline. Por agora, inline é aceitável.

### Step 12.5: Build + smoke test

- [ ] `python scripts/build-all.py`
- [ ] Abrir dist COE, confirmar:
  - Splash aparece ~1500 ms, desvanece, desaparece
  - Append `?nosplash=1` ao URL → splash nunca aparece
  - Após dismissar, o resto da página funciona normalmente

### Step 12.6: Commit

```bash
rtk git add shared/scripts/chrome/splash.js shared/scripts/utilities/date-utc.js packages/portal-coe/src/Portal_COE_AWM.source.html
rtk git commit -m "$(cat <<'EOF'
feat(coe): splash lifecycle + UTC clock utility for DS chrome

Task 12 of Plan 4. Two new utility scripts:
- shared/scripts/chrome/splash.js — 1500ms fade-out lifecycle for
  .ds-splash, bypass via ?nosplash=1 URL param, reduced-motion friendly
- shared/scripts/utilities/date-utc.js — headless UTC ticker for
  shell bar. Short-circuits if legacy updateHeaderClock() exists
  (no double-tick, no memory leak)

The splash script is inlined into Portal_COE_AWM.source.html right
before </body>. date-utc.js is staged for Plan 5 (SSCI) consumption —
COE still uses its own updateHeaderClock() which writes to the new
shell bar IDs unchanged.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 12 verification
- [ ] Splash visible ~1500 ms then fades
- [ ] `?nosplash=1` bypass works
- [ ] No double-ticker (`window.dsDateUtcInstalled === true` in console)
- [ ] Commit criado

---

## Task 13: Final integration — full build + pytest + user visual smoke test

**Files:** none (verification only)

### Step 13.1: Full build + test suite

- [ ] `python scripts/build-all.py` — exit 0
- [ ] `python -m pytest tests/ -q` — all pass
- [ ] `python -c "from pathlib import Path; p=Path('packages/portal-coe/dist/Portal_COE_AWM.html'); print(p.stat().st_size)"` — captura tamanho final

- [ ] Ler o baseline capturado na Task 0 (`/tmp/plan4-baseline-coe-size.txt`) e calcular delta:
  ```bash
  BASE=$(cat /tmp/plan4-baseline-coe-size.txt)
  NEW=$(python -c "from pathlib import Path; print(Path('packages/portal-coe/dist/Portal_COE_AWM.html').stat().st_size)")
  python -c "b=$BASE; n=$NEW; d=n-b; print(f'delta={d} bytes ({100*d/b:+.2f}%)')"
  ```
  Expected: delta dentro de ±30 KB (adição do CSS novo ~8 KB + HTML novo ~3 KB + JS ~1 KB, menos talvez algum whitespace removido do sidebar). Se o delta for > +100 KB, investigar duplicação.

### Step 13.2: User visual smoke test checklist

Apresentar ao utilizador a seguinte checklist a ser respondida manualmente (em `/tmp/plan4-smoketest-results.md` ou no chat). O executor espera pela confirmação antes de marcar o plano como completo:

```
Portal COE — Plan 4 visual smoke test (spec alignment)

BROWSER: Chrome (latest)
URL: file://<absolute path>/packages/portal-coe/dist/Portal_COE_AWM.html

 [ ] Splash screen aparece ao abrir
 [ ] Splash desaparece em ~1500 ms (fade suave)
 [ ] Shell bar é branco, não azul escuro
 [ ] Faixa institucional 4 px azul SGA imediatamente abaixo do shell bar
 [ ] Logo SGA 32x32 à esquerda no shell bar (só o símbolo)
 [ ] "Portal COE" em bold ao lado do logo
 [ ] Separador vertical + "FNMO" à direita do portal name
 [ ] UTC clock em tabular-nums a actualizar cada segundo
 [ ] Local clock abaixo do UTC
 [ ] Sidebar é 240 px light canvas (#f6f8fa)
 [ ] Sidebar SEM logo (só tem os grupos + versão no fundo)
 [ ] 4 grupos: Principal, Ocorrências, Documentação, Sistema
 [ ] 14 nav items visíveis
 [ ] Nav item activo tem border-left 3 px azul SGA
 [ ] Hover num nav item: fundo #eef2f7, texto azul
 [ ] Canvas bem #f6f8fa (não branco puro)
 [ ] Login funciona (operatorBadge aparece no shell bar direito)
 [ ] Logout funciona (operatorBadge some)
 [ ] Clicar em cada um dos 14 nav items — secção abre, nav active migra
 [ ] Abrir modal (Ocorrência > Iniciar) — modal aparece, ESC fecha
 [ ] Ctrl+P → print preview mostra @page header, sem sidebar nem shell bar
 [ ] Console sem errors nem warnings
 [ ] axe DevTools em Dashboard → 0 critical/serious
 [ ] axe DevTools em Contactos → 0 critical/serious
 [ ] axe DevTools em Verificação Mensal → 0 critical/serious
```

### Step 13.3: Final commit (summary)

- [ ] Se todos os items do checklist passam, criar commit final no plano:

```bash
rtk git commit --allow-empty -m "$(cat <<'EOF'
feat(coe): Plan 4 complete — COE chrome migrated to Design System SGA

Plan 4 delivers the most visually consequential milestone of the DS SGA
migration. The Portal COE now matches spec Section 4:

- Shell bar: 56px light chrome with 4px institutional SGA stripe,
  three zones (brand+OACI / breadcrumb / UTC+local+user+emg pill)
- Sidebar: 240px light canvas, no logo, uppercase section titles,
  border-left 3px brand-primary on active nav-btn
- Page grid: canvas #f6f8fa, max-width 1440px, white cards, subtle shadows
- Splash screen: 1500ms fade with DREA branding and logo lockup
- Footer institucional: single scroll-bottom line
- Print stylesheet: @page header with airport + portal + pagination

Preserved from legacy (JS contract):
- 14 openSection('X', event) handlers
- clockDisplay, headerUTC, headerDate, operatorBadge IDs
- .nav-btn class contract for active state management
- updateHeaderClock() legacy ticker (DS date-utc.js no-ops if present)

Out of scope (deferred):
- Plan 5: repeat for Portal SSCI
- Plan 6: rename --ds-* → --*, drop legacy CSS, swap stub SVGs for
  definitive tracings, consolidate placeholder cleanup

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 13 verification
- [ ] Build OK
- [ ] Pytest OK
- [ ] User checklist all checked
- [ ] Delta size reasonable
- [ ] Final commit created

---

## Verification checklist (end-of-plan)

- [ ] Worktree `../Portal_DREA-chrome` exists on branch `feat/coe-chrome`
- [ ] `shared/styles/base/{reset,typography,global}.css` present
- [ ] `shared/styles/chrome/{shell-bar,sidebar,page-grid,splash,footer}.css` present
- [ ] `shared/styles/print/print.css` present
- [ ] `shared/scripts/chrome/splash.js` present
- [ ] `shared/scripts/utilities/date-utc.js` present
- [ ] `shared/assets/logo-sga-mark.svg` and `logo-sga-full.svg` present
- [ ] `shared/assets/icons/sprite.svg` contains `<symbol id="icon-siren">` (Task 10.5)
- [ ] `scripts/ds_build_helpers.py::compile_design_system_css` discovers base/, chrome/, components/, print/ correctly
- [ ] `tests/test_ds_build_helpers.py` has ≥5 new Plan 4 tests passing
- [ ] `packages/portal-coe/src/Portal_COE_AWM.source.html` has:
  - `<div class="ds-splash">` near top of body
  - `<header class="ds-shell-bar">` replacing legacy `<header>`
  - `<aside class="ds-sidebar">` replacing legacy `<div class="sidebar">`
  - `<main class="ds-page-grid">` replacing legacy `<div class="main-container">`
  - `<footer class="ds-footer">` at end of main
  - Inline `<script>` for splash lifecycle right before `</body>`
- [ ] All 14 `openSection('X', event)` onclick handlers preserved
- [ ] IDs `clockDisplay`, `headerUTC`, `headerDate`, `operatorBadge` still exist
- [ ] Legacy selector `document.querySelector('.header-title-small')` still returns a node (on `ds-shell-bar__oaci` element)
- [ ] `chrome/shell-bar.css` contains the `.ds-shell-bar__operator > button { !important; ... }` override for the legacy "Sair" button
- [ ] `python scripts/build-all.py` exit 0
- [ ] `python -m pytest tests/ -q` exit 0
- [ ] Smoke test checklist (Task 13 Step 13.2) all checked
- [ ] axe DevTools ≥3 pages zero critical violations
- [ ] Print preview produces correct PDF
- [ ] Size delta within ±30 KB of baseline (sanity check)
- [ ] No regressions in SSCI build (Plan 4 does not touch SSCI)

---

## Rollback plan

- **Task-level rollback** (one task broke something):
  ```bash
  rtk git revert <task-commit-sha>
  ```
  Each task is a single atomic commit. Reverting one does not affect others.

- **Plan-level rollback** (chrome approach fundamentally wrong):
  ```bash
  rtk git reset --hard <commit-before-task-1>
  ```
  Or simply stop using `feat/coe-chrome` and delete the worktree:
  ```bash
  rtk git worktree remove ../Portal_DREA-chrome --force
  rtk git branch -D feat/coe-chrome
  ```
  `main` is never touched until explicit merge, so rollback is always safe.

- **Partial rollback** (chrome CSS OK but HTML swap failed):
  - Revert only Task 11 commit
  - Keep Tasks 1–10 and 12 (dormant CSS + JS, no visible impact because no HTML consumer)
  - Re-plan the HTML surgery

- **HTML surgery failure during Task 11 mid-edit**:
  - The source HTML may be half-edited if the sequence of `Edit` calls was interrupted
  - Recovery: `rtk git checkout -- packages/portal-coe/src/Portal_COE_AWM.source.html`
  - Then re-run Task 11 from scratch

- **Worktree lost** (accidentally deleted):
  ```bash
  cd d:/VSCode_Claude/03-Resende/Portal_DREA
  rtk git worktree prune
  rtk git worktree add ../Portal_DREA-chrome feat/coe-chrome
  ```
  Branch commits survive because they're in the bare repo.

- **Nothing to roll back to** (base branch lost too):
  - `main` is at `bc11d89` (Plan 1 complete + Plan 2 complete + Plan 3 end)
  - Worst case: `git reset --hard bc11d89` and start over

---

## Scope recap

This plan **does**:
- Introduce the first real visual change in the migration
- Make the COE look like the DS SGA spec Section 4
- Preserve 100% of the legacy JS contract
- Add 9 new CSS files (3 base + 5 chrome + 1 print), 2 new JS files (date-utc + splash), 1 new icon symbol (icon-siren), 0 Python changes beyond extending one function
- Produce 14 atomic commits (Task 0 + Tasks 1–10 + Task 10.5 + Tasks 11–13)

This plan **does not**:
- Touch Portal SSCI
- Remove any legacy CSS from block 1
- Rename any CSS variables
- Change the build pipeline contract (still two `build.py` calling one `compile_design_system_css`)
- Add new Python dependencies, new icon fonts, or new JS frameworks
- Modify `VERSION`, `CHANGELOG.md`, or `README.md` — those update at the end of the whole design system migration (Plan 6)

---

## Appendix A — CSS size budget estimate

| File | Estimated size |
|---|---|
| `base/reset.css` | ~1 KB |
| `base/typography.css` | ~1 KB |
| `base/global.css` | ~1 KB |
| `chrome/shell-bar.css` | ~3 KB |
| `chrome/sidebar.css` | ~2.5 KB |
| `chrome/page-grid.css` | ~1 KB |
| `chrome/splash.css` | ~1.5 KB |
| `chrome/footer.css` | ~0.5 KB |
| `print/print.css` | ~2 KB |
| `scripts/chrome/splash.js` (inlined) | ~0.5 KB |
| HTML delta (chrome swap) | +~3 KB (new markup) and -~5 KB (legacy removed) |
| **Total estimated delta vs baseline** | **+~12 KB** |

Within the ±30 KB budget documented in Task 13.1.

---

## Appendix B — Spec Section 4 traceability matrix

| Spec section | Spec requirement | Plan 4 task |
|---|---|---|
| 4.1 Shell bar anatomy | 56 px height, light bg, 4 px stripe, 3 zones | Task 5 CSS + Task 11 HTML |
| 4.1 Left zone | SGA mark 32×32, portal name, OACI | Task 5 + Task 11 |
| 4.1 Centre zone | breadcrumb collapse <1024 px | Task 5 (`@media`) |
| 4.1 Right zone | UTC + local + user badge + emg pill | Task 5 + Task 11 + Task 12 |
| 4.1 Right zone — emg pill icon | `icon-siren` symbol in sprite | Task 10.5 |
| 4.2 Sidebar | 240/256 px, light canvas, no logo, uppercase headings, border-left 3 px | Task 6 + Task 11 |
| 4.2 Active state | border-left, bold, surface bg | Task 6 |
| 4.3 Page grid | canvas, max 1440 px, padding `--ds-space-7` | Task 7 + Task 11 |
| 4.3 Section cards | surface, shadow-1, radius-lg, auto-fill grid | Task 7 |
| 4.4 Splash | 120×120 logo, portal name, tagline, OACI, version, 4 px stripe, 1500 ms | Task 8 CSS + Task 11 HTML + Task 12 JS |
| 4.4 Splash bypass | `?nosplash=1` | Task 12 |
| 4.5 Footer | scroll-bottom, thin, single line | Task 9 + Task 11 |
| 4.6 Print header | `@page`, logo, airport, section, timestamp, pagination | Task 10 |

---

## Appendix C — JS contract preservation inventory

The following JavaScript symbols are **never touched** by Plan 4 and must continue to work exactly as they do at commit `bc11d89`:

| Symbol | Source line (approx) | What it does |
|---|---|---|
| `openSection(sectionId, event)` | 9946 | Switches visible section, manages `.nav-btn.active` |
| `updateHeaderClock()` | 9930 | Ticks clockDisplay, headerUTC, headerDate |
| `loginCOE()` | (login flow) | Login form handler |
| `logoutCOE()` | 10602 | Logout handler, resets operatorBadge |
| `activateSocorro()` / `activateUrgencia()` | 3341+ | Emergency condition activators |
| `generateOccNumber()` | (cronometro flow) | Auto-generate occurrence number |
| `setPistaStatus()` | 3331 | Runway status setter |
| `operatorBadge` element | (populated on login) | Shell bar user indicator |
| `.nav-btn` class | (class contract) | Filter target in openSection() |
| `.section` class | (class contract) | Filter target in openSection() |
| `.header-title-small` class | ~11097 | Target of `cfgApplyToPortal()` — writes airport name when operator swaps config. Preserved as a dual class on `.ds-shell-bar__oaci` by Task 11. |

The new chrome HTML in Task 11 makes sure all these are still reachable. The new CSS in Tasks 5–9 targets only `.ds-*` classes, never these legacy class contracts. **If any of the above stops working after Task 11, the task has failed and must be reverted.**

---

**End of Plan 4 document.** Total estimated tasks: **14 (Task 0 + Tasks 1–10 + Task 10.5 + Tasks 11–13)**. Total estimated atomic commits: **14**. Worktree: `../Portal_DREA-chrome` on branch `feat/coe-chrome`.
