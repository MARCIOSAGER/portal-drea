# Design System SGA — Plan 5: SSCI Full Migration (Components + Chrome)

> **Status:** Draft — depende dos Planos 3 e 4 estarem **merged** antes de executar.
> Plan 5 é deliberadamente **mais curto** que os Planos 3 e 4 porque **reutiliza** os artefactos criados por eles (`shared/styles/components/*.css`, `shared/styles/chrome/*.css`, `shared/styles/base/*.css`, `shared/styles/print/print.css`, `shared/assets/logo-sga-*.svg`, sprite SVG expandida, `shared/scripts/*.js`). Plan 5 não **cria** componentes nem chrome CSS — só **consome** e remove os duplicados da versão legada do SSCI.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrar o **Portal SSCI** para o Design System SGA completo, em duas metades executadas no mesmo plano e no mesmo worktree:
- **Metade A** — substituir os selectores legados de componentes genéricos (button, badge, form-group, card, table, tabs, dropdown, awm-modal, awm-toast, uxp-savebadge, skeleton, empty-state) na consolidated block 1 do SSCI pelos componentes partilhados que os Planos 3 e 4 já criaram. Invariante: equivalência visual.
- **Metade B** — substituir o chrome (header com gradient dark-blue, sidebar branca, layout, print) pelo novo Shell Bar / Sidebar / Page Grid / Splash / Footer light, com a identidade visual institucional SGA (logo visível no shell bar, faixa 4px `--brand-primary`). Invariante: **mudança visual intencional e validada pelo utilizador**.

**Arquitectura:** Plan 5 opera exclusivamente dentro de `packages/portal-ssci/src/Portal_PSCI_AWM.source.html` (+ pequenas edições opcionais à config SSCI e, se necessário, um aditivo ao `print.css` partilhado). Não cria ficheiros em `shared/styles/components/`, `shared/styles/chrome/` ou `shared/styles/base/` — esses foram criados pelos Planos 3 e 4 e já estão em `main`. Plan 5 verifica por inspecção que os ficheiros esperados existem e refere-os como pré-requisito. A densidade do SSCI é `comfortable` (já definida em `packages/portal-ssci/portal.config.json`), portanto os tokens `--nav-item-height: 44px`, `--text-base: 16px`, `--row-height: 40px` são aplicados automaticamente via `:root[data-density="comfortable"]` sem qualquer alteração ao CSS dos componentes.

**Tech Stack:** Python 3.8+ (build + pytest), vanilla CSS (consumo dos componentes partilhados), vanilla JS (consumo dos utilitários partilhados — ver Task 14), git (atomic commits em worktree isolado). Zero dependências novas. Zero alterações aos `build.py`.

**Source spec:** [docs/superpowers/specs/2026-04-11-design-system-sga-design.md](../specs/2026-04-11-design-system-sga-design.md) (v1.1 aprovado 2026-04-11)

**Planos precedentes:**
- [Plan 1 — Foundation Dormant](./2026-04-11-design-system-plan-1-foundation.md) ✅ merged at `f81d6db`
- [Plan 2 — Style Block Consolidation](./2026-04-11-design-system-plan-2-style-consolidation.md) ✅ merged at `9dcd9ef`
- [Plan 3 — COE Component Migration](./2026-04-11-design-system-plan-3-coe-components.md) — **must be merged before Plan 5 starts**
- [Plan 4 — COE Chrome Migration](./2026-04-11-design-system-plan-4-coe-chrome.md) — **must be merged before Plan 5 starts**

**Invariant this plan must preserve:**

1. **Metade A (components) — equivalência visual**: após cada commit de componente na Metade A, o SSCI dist HTML deve renderizar **visualmente idêntico** ao estado imediatamente anterior (o utilizador não deve notar nenhuma mudança em botões, cards, formulários, tabelas, modais, toasts ou save-badge). O que muda é apenas a proveniência do CSS — passa da block 1 legada a vir de `shared/styles/components/*.css`.

2. **Metade B (chrome) — mudança visual intencional**: após a Metade B ser executada, o SSCI tem uma aparência deliberadamente diferente (shell bar light, logo SGA visível, sidebar light com border-left no item active, splash screen, print header institucional). Esta mudança é validada pelo utilizador final antes de merge. O comportamento funcional (navegação entre secções, persistência de dados, save-badge, modals, toasts, impressão) permanece exactamente idêntico.

3. **Comportamento JS preservado**: `openSection()`, `updateClock()`, `window.notify`, `window.awmAlert`, `window.lsGet/lsSet`, `PSCI_CFG.*` continuam a funcionar. A Metade B pode renomear alguns elementos DOM (ex: `#psci-clock` → `#shell-clock`) mas o JS que os lê é actualizado em simultâneo no mesmo commit.

**Out of scope for Plan 5:**
- ❌ Criação de novos componentes `shared/styles/components/*.css` (Plan 3 criou)
- ❌ Criação de novo chrome CSS `shared/styles/chrome/*.css`, base `shared/styles/base/*.css`, print `shared/styles/print/print.css` (Plan 4 criou)
- ❌ Criação de logo SVGs e icon sprite expandida (Plan 4 criou)
- ❌ Extracção de domain components SSCI (VCI inspection row, stock counter, comms test grid, service registry form, response time dashboard). Estes permanecem no SSCI source, consumindo tokens DS, mas o HTML/CSS é portal-específico.
- ❌ Rename `--ds-*` → `--*` (Plan 6)
- ❌ Remoção dos tokens legados `--dark-blue`, `--medium-blue`, etc. (Plan 6)
- ❌ Release, tag, CHANGELOG (Plan 6)
- ❌ Alterações aos `build.py` ou `ds_build_helpers.py` (Plan 1/3/4 já cobriram tudo o que é preciso)
- ❌ Alterações ao `portal.config.json` do SSCI (já está correcto: density=comfortable, `ui.show_occurrence_pill=false`, `ui.show_emergency_stopwatch=false`, `ui.show_utc_clock=true`)
- ❌ Tauri packaging (Fase 2)

---

## Key fact sheet (verified by inspection on 2026-04-11)

### SSCI source — `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`

- **Tamanho:** 1,563,883 bytes, 4140 linhas
- **Estado pós-Plan 2:** 5 `<style>` blocks (1 DS placeholder + 1 consolidated legacy block + 3 JS-embedded PDF CSS strings intocáveis)
- **Consolidated block 1:** 21,720 chars (vs COE 100,006 — ~5x mais pequeno)
- **Placeholders presentes no source:** `{{DS_CSS}}`, `{{ICON_SPRITE}}`, `{{AIRPORT.NAME}}`, `{{AIRPORT.OACI}}`, `{{AIRPORT.LOCATION}}`, `{{AIRPORT.NAME_SHORT}}`, `{{AIRPORT.OPERATOR_SHORT}}`, `{{VERSION}}`, `{{BUILD_DATE_SHORT}}`, `{{PORTAL.DENSITY}}` (no `<html>`). Ainda **não** presentes: `{{DS_FONTS_CSS}}`, `{{DS_JS}}`, `{{LOGO_SGA_MARK}}`, `{{LOGO_SGA_FULL}}`, `{{BUILD_TIMESTAMP}}`, `{{PORTAL.NAME}}`, `{{PORTAL.TAGLINE}}`. Plan 5 **adiciona** os que faltam onde fizer sentido.

### Content breakdown of SSCI consolidated block 1 (by selector cluster)

Mapeado por inspecção linha-a-linha entre as linhas ~10 e ~464 do source. Componentes marcados **[migrar]** são alvo da Metade A; **[domain]** ficam no SSCI source; **[chrome]** são substituídos na Metade B.

| Cluster | Linhas aprox. | Selectores principais | Classificação |
|---|---|---|---|
| `:root` legacy tokens | 13–23 | `--dark-blue`, `--medium-blue`, `--light-blue`, `--light-bg`, `--white`, `--warning-red`, `--success-green`, `--amber`, `--gray-light` | **legacy tokens** (ficam — Plan 6 remove) |
| Reset + body font | 24–25 | `* { margin:0; padding:0; box-sizing:border-box; }`, `body { font-family: 'Segoe UI'... }` | **[chrome]** (Task 13 — substitui pelo reset + typography partilhados via consumo do `base/*.css`) |
| Header gradient | 28–31 | `.header`, `.header h1`, `.header-sub`, `.header-badge` | **[chrome]** (Task 13) |
| Layout flex | 34–35 | `.layout`, `.sidebar` | **[chrome]** (Task 13) |
| Sidebar headings + nav | 36–41 | `.sidebar h3`, `.sidebar h3:first-child`, `.nav-item`, `.nav-item:hover`, `.nav-item.active`, `.nav-icon` | **[chrome]** (Task 13) |
| Main + section | 43–45 | `.main`, `.section`, `.section.active` | **[chrome]** (Task 13) |
| Page title + desc | 48–49 | `h1.page-title`, `.page-desc` | **[chrome]** (Task 13 — movem para `page-grid.css`) |
| **form-card** | 50–52 | `.form-card`, `.form-card h3`, `.form-card .badge` | **[migrar]** Task 5 (card) + Task 3 (badge) |
| **form-row + form-group** | 54–61 | `.form-row`, `.form-row.three`, `.form-row.four`, `.form-row.full`, `.form-group`, `.form-group label`, `.form-group input/select/textarea` | **[migrar]** Task 4 (form-group) |
| check-table (VCI inspection) | 64–73 | `.check-table`, `.check-table th/td/tr/input`, `.check-table .section-header`, `.check-table .obs-cell` | **[migrar]** Task 6 (table base) + **[domain]** (VCI row-specific rules stay) |
| **btn** | 76–82 | `.btn`, `.btn-primary/danger/success/gray`, `.btn-row` | **[migrar]** Task 2 (button) |
| separator | 84 | `.separator` | **[migrar]** Task 7 (divider) |
| **dash-grid + dash-card** | 87–91 | `.dash-grid`, `.dash-card`, `.dash-icon`, `.dash-title`, `.dash-value` | **[migrar]** Task 5 (stat-card pattern) |
| time-display | 94 | `.time-display` | **[chrome]** (Task 13 — vira UTC clock do shell bar) |
| Responsive sidebar | 96–104 | `@media (max-width: 768px)` | **[chrome]** (Task 13 — substituído pelo responsive do novo shell/sidebar) |
| **result-toggle** (OK/NOK/OP/NO/NA) | 107–149 | `.result-toggle`, `.result-toggle .rt-btn`, `.result-toggle .rt-btn.active[data-result=...]` | **[domain]** (inspecção VCI) — fica no SSCI source, consome tokens DS |
| **awm-toast** | 152–207 | `#awmToastContainer`, `.awm-toast`, `.awm-toast-*`, `@keyframes awmToast*` | **[migrar]** Task 9 (awm-toast) |
| **awm-modal** | 209–276 | `.awm-modal-overlay`, `.awm-modal`, `.awm-modal-header/icon/title/body/footer/btn*`, `@keyframes awmModal*` | **[migrar]** Task 8 (awm-modal) |
| Responsive awm-* | 298–303 | `@media (max-width: 520px)` — `#awmToastContainer`, `.awm-modal-footer`, `.awm-modal-btn` | **[migrar]** Task 8/9 (já contemplado nos respectivos componentes partilhados) |
| `#tr-occ-real-block` | 306–341 | Bloco dinâmico de ocorrência (Plan 2 block 5) | **[domain]** — fica no SSCI |
| UXP layer | 344–443 | `.uxp-fv`, `.uxp-skip`, `.uxp-savebadge*`, `.uxp-toasts`, `.uxp-toast*`, `.uxp-totop`, `.uxp-modal-bg`, `.uxp-modal`, `@keyframes uxp-*` | **[migrar]** Task 10 (uxp-savebadge) + **[overlap com Task 9 awm-toast]** — ver nota abaixo |
| @media print (UXP) | 435–441 | UXP hide-in-print rules | **[chrome]** (Task 15 — print stylesheet) |
| Print safety net (block 7) | 452–464 | `@media print` — hide UXP + awm-modal-overlay + #awm-section-announcer | **[chrome]** (Task 15 — print stylesheet) |

**Nota sobre overlap UXP layer vs awm-toast**: SSCI tem **dois** sistemas de toast coexistentes — `awm-toast` (chamado via `window.notify`, linhas 152–207) e `uxp-toast` (chamado internamente pela UXP layer, linhas 384–398). Ambos servem para notificações. Task 9 migra **apenas** os `awm-toast*` selectores para `components/awm-toast.css`. Os `uxp-toast*` ficam no SSCI source como fallback legado até o Plan 6 decidir se são removidos ou migrados. **Não mexer nos uxp-toast nesta passagem.**

### SSCI JS landscape (4140 linhas)

**Inline JS patches encontrados** (cada um num `<script>` separado no body):
- `updateClock()` / `openSection()` / `addPresencaRow()` / `window.notify` / awm-toast + awm-modal inline implementation (linhas ~2145–~2400)
- `PSCI_CFG.*` — configuração SSCI persistida em `localStorage` chave `psci_awm_config` (linhas ~2680–~2950). **Nota crítica**: `PSCI_CFG.contactos` é um array de contactos operacionais do quartel (Chefe SSCI, DREA, TWR, COE, SPCB, INEMA, PNA) editáveis pelo utilizador via UI `Sistema → Configurações → Contactos`. **Não é** o mesmo que os `airport.contacts.items` do `config/airport-fnmo.json` (que são os contactos do aeroporto inteiro, partilhados com COE). **O `awmContacts` shared module não se aplica aqui** — o SSCI tem contactos internos do quartel geridos pelo chefe SSCI.
- PATCH v3 (`escHtml` + awm-modal focus trap / a11y)
- PATCH v4 (`lsGet/lsSet` wrapper + section change announcer)
- PATCH v5 (print safety net — já consolidado para a block 1 pelo Plan 2)

### Bonus scope decision: awm-contacts.js

O task brief propõe a extracção de `awm-contacts.js` como bonus scope. **Decisão após inspecção**: **não aplicável ao SSCI**, porque:

1. O SSCI não tem uma secção de contactos do aeroporto — tem uma secção de configuração interna onde o chefe SSCI edita os contactos operacionais do seu próprio quartel.
2. Esses contactos (`PSCI_CFG.contactos`) são editados e persistidos localmente em `localStorage` com chave `psci_awm_config`; não consomem `config/airport-XXX.json::contacts.items`.
3. O `awmContacts` shared module (extraído pelo Plan 3 para servir o COE) é um read-only API sobre `{{CONTACTS_JSON}}` injectado do `airport-fnmo.json` — serve o COE que consome a fonte única do aeroporto. Aplicá-lo ao SSCI seria uma mudança de semântica, não uma extracção.
4. Se no futuro se quiser que o SSCI também mostre os contactos completos do aeroporto (read-only, além dos seus próprios), isso é trabalho de Fase 2+ e fora do escopo do Design System SGA.

**Decisão registada**: Plan 5 **não** toca em contactos. A bonus scope é omitida explicitamente. Se o Plan 3 extraiu `shared/scripts/awm-contacts.js` (provavelmente não, dado que Plan 3 é 100% CSS), o SSCI **não** o consome. Quanto aos outros módulos partilhados: Plans 3 e 4 **só** produzem `shared/scripts/chrome/splash.js` (inlineado no source pelo próprio Plan 4) e `shared/scripts/utilities/date-utc.js` — este último é o único que Plan 5 Task 14 realmente consome. `awm-modal.js`, `awm-toast.js`, `awm-save-badge.js`, `ls-wrapper.js` e `esc-html.js` **não** existem ao terminar Plans 3+4 e ficam como implementações inline no SSCI source, deferred para Plan 6.

### Current SSCI header/sidebar HTML structure (source state pre-Plan-5)

Linhas 472–530 do source:

```html
<body>
{{ICON_SPRITE}}
<div id="awmToastContainer" aria-live="polite" aria-atomic="true"></div>

<!-- HEADER -->
<div class="header">
    <div>
        <h1>🚒 Portal PSCI — SSCI</h1>
        <div class="header-sub">{{AIRPORT.NAME}} — {{AIRPORT.OACI}} — {{AIRPORT.LOCATION}}</div>
    </div>
    <div style="text-align:right;">
        <div class="time-display" id="psci-clock"></div>
        <div class="header-badge" id="psci-turno">Turno: —</div>
    </div>
</div>

<!-- LAYOUT -->
<div class="layout">
    <nav class="sidebar">
        <h3>Painel</h3>
        <button class="nav-item active" onclick="openSection('dashboard')">
            <span class="nav-icon">📊</span>Dashboard
        </button>
        <button class="nav-item" onclick="openSection('mapas')">
            <span class="nav-icon">🗺</span>Mapas Quadrícula
        </button>

        <h3>Formulários Diários</h3>
        <button class="nav-item" onclick="openSection('reg-servico')">...</button>
        <button class="nav-item" onclick="openSection('insp-w01')">...</button>
        <button class="nav-item" onclick="openSection('insp-w02')">...</button>
        <button class="nav-item" onclick="openSection('insp-resgate-w01')">...</button>
        <button class="nav-item" onclick="openSection('insp-resgate-w02')">...</button>
        <button class="nav-item" onclick="openSection('teste-comms')">...</button>

        <h3>Formulários Operacionais</h3>
        <button class="nav-item" onclick="openSection('avaria')">...</button>
        <button class="nav-item" onclick="openSection('combustivel')">...</button>
        <button class="nav-item" onclick="openSection('tempo-resp')">...</button>
        <button class="nav-item" onclick="openSection('presenca')">...</button>

        <h3>Recursos</h3>
        <button class="nav-item" onclick="openSection('stock')">...</button>

        <h3>Checklists Mensais</h3>
        <button class="nav-item" onclick="openSection('checklist-coe')">...</button>
        <button class="nav-item" onclick="openSection('checklist-pcm')">...</button>

        <h3>Sistema</h3>
        <button class="nav-item" onclick="openSection('ajuda')">...</button>
        <button class="nav-item" onclick="openSection('configuracoes')">...</button>

        <!-- Footer de versão (Fase 1 Etapa 4) -->
        <div class="sidebar-version-footer" style="...">
            <div>Portal SSCI</div>
            <div>v{{VERSION}} · {{BUILD_DATE_SHORT}}</div>
            <div>{{AIRPORT.OACI}} · {{AIRPORT.OPERATOR_SHORT}}</div>
        </div>
    </nav>

    <div class="main">
        <!-- Secções a partir daqui — DASHBOARD activa por defeito -->
```

Total: **17 nav-items** em **6 section groups** (Painel: 2, Formulários Diários: 6, Formulários Operacionais: 4, Recursos: 1, Checklists Mensais: 2, Sistema: 2). Verificado por grep: `rtk grep -c 'class="nav-item"' packages/portal-ssci/src/Portal_PSCI_AWM.source.html` → **17** (corrige um `18` anterior na draft do task brief). **Corrigir nota do task brief**: o SSCI actual **tem header com gradient dark-blue → medium-blue** (linha 28 CSS: `background: linear-gradient(135deg, var(--dark-blue), var(--medium-blue))`), **não** light/minimal como sugerido no brief. E **tem** um emoji bombeiro 🚒 no H1 (linha 482). O que **não** tem é um logo SGA institucional em SVG — isso é o que a Metade B adiciona pela primeira vez.

### Current SSCI JS that must keep working after Plan 5

1. `openSection(id)` — classList toggle sobre `.section` e `.nav-item`. **Contract changes em Plan 5 Task 13**: (a) class name passa de `.nav-item` para `.nav-btn` (para casar com o contrato do Plan 4); (b) assinatura passa de `openSection(id)` para `openSection(id, event)` (2 args, igual ao COE). As 17 chamadas do sidebar + 4 do dashboard (21 total) são reescritas na Task 13a; a função é reescrita na Task 13c.
2. `updateClock()` — lê `#psci-clock`. **Em Plan 5 Task 13c**, reescreve-se para escrever nos IDs Plan 4 (`headerUTC`, `clockDisplay`, `headerDate`) com tick a cada segundo, formato `UTC HH:MM:SS` conforme spec §4.1. Ou, alternativamente (Task 14 Path A), o `updateClock()` inline é substituído por inline do `shared/scripts/utilities/date-utc.js`.
3. `#psci-turno` — badge do turno (Alfa/Bravo/Charlie) no header, ligado a `PSCI_CFG.efectivo[PSCI_TURNO_ACTUAL]`. Em Plan 5 **o ID `psci-turno` é preservado** (não renomear): a Task 13a coloca `<div class="ds-shell-bar__operator" id="psci-turno">` na zona direita do shell bar, e o JS existente que escreve para `#psci-turno` continua a funcionar sem mudanças.
4. `window.notify()` (toast) e `window.awmAlert()` (modal) — continuam a funcionar via `#awmToastContainer` e overlays criados on-demand. **Permanecem implementações inline no SSCI** — Plans 3 e 4 não extraem `awm-modal.js` / `awm-toast.js`, então não há nada partilhado para consumir. Só o CSS passa a vir dos componentes partilhados; o JS mantém-se verbatim.
5. `window.lsGet/lsSet/lsRemove` — inline PATCH v4. **Permanece inline em Plan 5** — Plans 3 e 4 não produzem `shared/scripts/utilities/ls-wrapper.js`, deferred para Plan 6.
6. `psciEsc(s)` + `escHtml(s)` inline PATCH v3 — **permanece inline em Plan 5** — Plans 3 e 4 não produzem `shared/scripts/utilities/esc-html.js`, deferred para Plan 6.
7. `PSCI_CFG` + `psciCfgLoad()` / `psciCfgPersist()` — ficam **exactamente** como estão. Plan 5 não toca na config interna do SSCI.
8. PDF export code paths (linhas ~2540, ~3400, ~3410) — usam `<style>` JS-embedded strings **intocáveis**. Plan 5 verifica que nenhuma mexida acidental acontece aqui.

---

## File structure (Plan 5 scope)

### Files to create

**Nenhum em `shared/`** (asumindo que Planos 3 e 4 entregaram tudo). Se a verificação da Task 0 falhar (por ex. Plan 3 não extraiu `uxp-savebadge.css`), Plan 5 abre uma exceção e para — não improvisa, pede revisão.

Opcionalmente (Task 15), **um possível aditivo** a `shared/styles/print/print.css` para cobrir uma regra SSCI-específica (esconder `.result-toggle` em print? ver Task 15).

### Files to modify (1 principal)

```
packages/portal-ssci/src/Portal_PSCI_AWM.source.html   MODIFY — muitas edições ao longo de 17 tasks (Task 0..16)
```

### Files optionally touched

```
shared/styles/print/print.css                           MAYBE MODIFY — Task 15, se SSCI precisar de regra adicional
tests/test_ssci_plan5.py                                NEW — Task 16, teste programático (≤100 linhas)
```

### Files NOT touched

Tudo o resto:
- `packages/portal-ssci/portal.config.json` — **já está correcto**, não mexer
- `packages/portal-ssci/scripts/build.py` — nada muda
- `packages/portal-coe/**` — zero impacto (COE já foi migrado nos Planos 3+4)
- `shared/styles/components/*.css` — reusar tal como estão
- `shared/styles/chrome/*.css` — reusar tal como estão
- `shared/styles/base/*.css` — reusar tal como estão
- `shared/styles/tokens/*.css` — reusar tal como estão
- `shared/scripts/*.js` — consumir tal como estão
- `shared/assets/**` — reusar tal como estão
- `scripts/ds_build_helpers.py` — nada muda
- `config/airport-fnmo.json` — nada muda
- `VERSION` — nada muda (release é Plan 6)
- `docs/CHANGELOG.md` — nada muda (release é Plan 6)

---

## Task 0: Prerequisites — worktree, baseline, verify Plans 3 and 4 merged

**Files:** none (infrastructure)

- [ ] **Step 1: Verify main is clean and both Plan 3 and Plan 4 are merged**

```bash
cd d:/VSCode_Claude/03-Resende/Portal_DREA
git status --short
git log --oneline -15
```

Expected: empty working tree. Último commit deve referir Plan 4 (chrome migration COE) ou um release pós-Plan-4. Procurar pelos commits:
- `feat(ds): extract shared components (Plan 3)` ou similar
- `feat(coe): replace header+sidebar with design system shell (Plan 4)` ou similar

Se algum deles **não** existir em `main`, **PARAR**: Plan 5 não pode começar sem Planos 3 e 4 merged. Reportar e esperar.

- [ ] **Step 2: Verify shared/ files created by Plans 3 and 4 exist**

```bash
python << 'PYEOF'
from pathlib import Path

repo = Path('.')
# IMPORTANT: this list reflects ONLY what Plans 3 and 4 ACTUALLY produce.
# Plan 3 produces 13 component CSS files (no divider.css, save-badge is
# uxp-savebadge.css matching the real legacy class). Plan 3 produces ZERO JS.
# Plan 4 produces 3 base, 5 chrome, 1 print CSS files + 2 logo SVGs +
# exactly 2 JS files (chrome/splash.js, utilities/date-utc.js).
# Any file NOT in this list is deferred to Plan 6 or later.
required_component_css = [
    'button.css', 'badge.css', 'form-group.css', 'card.css', 'stat-card.css',
    'table.css', 'tabs.css', 'dropdown.css', 'awm-modal.css', 'awm-toast.css',
    'uxp-savebadge.css', 'skeleton.css', 'empty-state.css',
]
required_chrome_css = [
    'shell-bar.css', 'sidebar.css', 'page-grid.css', 'splash.css', 'footer.css',
]
required_base_css = ['reset.css', 'typography.css', 'global.css']
required_print_css = ['print.css']
required_assets = [
    'shared/assets/logo-sga-mark.svg',
    'shared/assets/logo-sga-full.svg',
    'shared/assets/icons/sprite.svg',
]
# Plan 4 Task 12 creates exactly these 2 JS files. `ls-wrapper.js` and
# `esc-html.js` are NOT produced by Plans 3 or 4 — they remain inline in
# the SSCI source and are deferred to Plan 6.
required_shared_js = [
    'shared/scripts/chrome/splash.js',
    'shared/scripts/utilities/date-utc.js',
]

missing = []
for f in required_component_css:
    p = repo / 'shared/styles/components' / f
    if not p.exists(): missing.append(str(p))
for f in required_chrome_css:
    p = repo / 'shared/styles/chrome' / f
    if not p.exists(): missing.append(str(p))
for f in required_base_css:
    p = repo / 'shared/styles/base' / f
    if not p.exists(): missing.append(str(p))
for f in required_print_css:
    p = repo / 'shared/styles/print' / f
    if not p.exists(): missing.append(str(p))
for f in required_assets + required_shared_js:
    p = repo / f
    if not p.exists(): missing.append(str(p))

if missing:
    print("MISSING PREREQUISITES (Plans 3 and/or 4 incomplete):")
    for m in missing:
        print(" -", m)
    raise SystemExit(1)
print("OK — all prerequisites for Plan 5 are present")
PYEOF
```

Expected: `OK — all prerequisites for Plan 5 are present`. Se algum ficheiro falta, **PARAR** e reportar ao revisor humano — Plan 3 ou Plan 4 não cumpriu o contrato.

- [ ] **Step 3: Create isolated worktree for Plan 5**

Usando a skill @superpowers:using-git-worktrees:

```bash
git worktree add ../Portal_DREA-ssci -b feat/ssci-migration
git worktree list
```

Expected: novo worktree listado em `d:/VSCode_Claude/03-Resende/Portal_DREA-ssci/` no branch `feat/ssci-migration`, criado a partir do HEAD actual do `main`.

- [ ] **Step 4: Switch to the worktree and run baseline build + tests**

```bash
cd d:/VSCode_Claude/03-Resende/Portal_DREA-ssci
git branch --show-current
python scripts/build-all.py
python -m pytest tests/ -q
```

Expected: branch `feat/ssci-migration`, ambos os portais buildam OK, todos os testes existentes passam (Plan 1: 20 + Plan 2: 13 + Plan 3 tests + Plan 4 tests = total a determinar por inspecção — aceitar o count que vier).

- [ ] **Step 5: Capture the baseline SSCI dist artifact**

```bash
python << 'PYEOF'
import hashlib, shutil
from pathlib import Path

baseline_dir = Path('d:/tmp/plan5-baseline')
baseline_dir.mkdir(parents=True, exist_ok=True)

src = Path('packages/portal-ssci/dist/Portal_PSCI_AWM.html')
content = src.read_bytes()
sha = hashlib.sha256(content).hexdigest()
dst = baseline_dir / 'ssci-pre-plan5.html'
dst.write_bytes(content)

print(f"SSCI baseline:")
print(f"  size:   {len(content):>10} bytes")
print(f"  sha256: {sha}")
print(f"  path:   {dst}")
PYEOF
```

Guardar output para comparação na Task 16. Abrir o ficheiro em Chrome e tirar screenshots de:
- Dashboard (secção inicial)
- Registo de Serviço (form-row, form-group, check-table)
- Inspecção Whisky 01 (check-table com result-toggle)
- Controlo de Estoque (stat-cards, btn-row)
- Sistema → Configurações → Contactos (tabela de contactos operacionais)
- Guia Rápido (documentação + callouts)
- Impressão de uma secção (Ctrl+P → preview) — Registo de Serviço

Guardar os screenshots em `d:/tmp/plan5-baseline/screenshots/`. Estes são **o estado antes de Plan 5** e serão usados na Task 16 para comparação visual (Metade A deve parecer idêntico até à Task 13; Metade B é a diferença visual intencional validada pelo utilizador).

- [ ] **Step 6: Commit task 0 marker (optional empty commit)**

Opcional: criar um commit marker vazio para facilitar rollback parcial.

```bash
git commit --allow-empty -m "chore(ssci): Plan 5 task 0 — baseline captured"
```

---

## Task 1: (optional) Decide awm-contacts scope — decision recorded, zero code

**Files:** none

- [ ] **Step 1: Confirm the decision taken in the fact sheet**

Revisto durante a inspecção: **SSCI não consome `shared/scripts/awm-contacts.js`**. Razão documentada no fact sheet (§ Bonus scope decision). Os contactos operacionais do quartel vivem em `PSCI_CFG.contactos` no `localStorage` e continuam a ser editáveis via Sistema → Configurações → Contactos.

- [ ] **Step 2: Verify that no task later in Plan 5 depends on awm-contacts**

Inspeccionar Tasks 2–16 e confirmar que nenhuma referencia `awm-contacts.js` ou `{{CONTACTS_JSON}}` para o SSCI.

Esta task é puramente documental — não há commits nem edições. Marca-se como done quando a decisão é recordada no plano.

---

## Task 2: Migrate button to shared components/button.css

**Files:**
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html` (remove `.btn*` from consolidated block 1)
- Read-only reference: `shared/styles/components/button.css` (already exists)

**Pre-flight verification:**

- [ ] **Step 1: Grep current .btn selectors in SSCI source**

```bash
rtk grep -n '\.btn\b\|\.btn-primary\|\.btn-danger\|\.btn-success\|\.btn-gray\|\.btn-row' \
  packages/portal-ssci/src/Portal_PSCI_AWM.source.html
```

Expected: matches in the consolidated block 1 around lines 76–82 (CSS declarations) AND matches in the HTML body (class usages). Count the HTML usages: these are the ones that will continue to work unchanged by consuming `components/button.css`.

- [ ] **Step 2: Compare SSCI .btn variants to COE's migrated button.css**

```bash
rtk read shared/styles/components/button.css
```

Expected: file exists, contains `.btn`, `.btn-primary`, `.btn-danger`, `.btn-success`, `.btn-gray` (o `gray` pode ser `neutral` conforme Plan 3 naming), `.btn-row`. Se algum variant do SSCI não existir (improvável dado que foram baseados nos COE selectors originais), **PARAR** e reportar ao Plan 3 para completar.

**Action:**

- [ ] **Step 3: Remove .btn selectors from consolidated block 1**

Usar o Edit tool. Localizar o bloco entre os comentários `/* Buttons */` e `/* Dashboard */` (ou `.separator { ... }`, whichever comes first) e substituí-lo por um comment marker:

```css
/* Buttons — MIGRATED to shared/styles/components/button.css (Plan 5 Task 2) */
```

- [ ] **Step 4: Build and smoke test**

```bash
python scripts/build-all.py --only portal-ssci
```

Expected: build OK. Abrir `packages/portal-ssci/dist/Portal_PSCI_AWM.html` em Chrome e verificar **visualmente** que:
- Botões em todas as secções têm o mesmo aspecto que no baseline
- `.btn-row` continua a alinhar à direita
- Hover states funcionam (medium-blue → dark-blue na primária)

- [ ] **Step 5: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "refactor(ssci): consume shared button.css, drop legacy .btn selectors"
```

---

## Task 3: Migrate badge to shared components/badge.css

**Files:**
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html` (remove `.form-card .badge` from consolidated block 1)
- Read-only reference: `shared/styles/components/badge.css`

- [ ] **Step 1: Locate all badge declarations in SSCI block 1**

```bash
rtk grep -n 'badge' packages/portal-ssci/src/Portal_PSCI_AWM.source.html
```

Expected: `.form-card .badge` (declaration, line ~52), `.header-badge` (declaration, line 31 — **chrome**, handled by Task 13, NOT here), `.sidebar-version-footer` (NO badge), `#psci-turno.header-badge` (HTML class usage).

Só o `.form-card .badge` legacy selector é removido nesta task. `.header-badge` é parte do chrome e fica até ao Task 13.

- [ ] **Step 2: Remove the `.form-card .badge` rule**

Editar a consolidated block 1 e remover a regra específica. Substituir por comment marker:

```css
/* .form-card .badge — MIGRATED to shared/styles/components/badge.css (Plan 5 Task 3) */
```

- [ ] **Step 3: Build and visual check**

```bash
python scripts/build-all.py --only portal-ssci
```

Verificar visualmente nas secções Registo de Serviço, Avaria Equipamento e Tempo Resposta (onde há `<span class="badge">`) que os badges continuam iguais.

- [ ] **Step 4: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "refactor(ssci): consume shared badge.css for form-card badges"
```

---

## Task 4: Migrate form-group / form-row to shared components/form-group.css

**Files:**
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`
- Read-only reference: `shared/styles/components/form-group.css`

**Pre-flight:**

- [ ] **Step 1: Inspect SSCI form-group selectors vs shared form-group.css**

```bash
rtk grep -n 'form-row\|form-group' packages/portal-ssci/src/Portal_PSCI_AWM.source.html
rtk read shared/styles/components/form-group.css
```

Expected SSCI block 1 declarations (linhas ~54–61):
```
.form-row { display:grid; grid-template-columns:1fr 1fr; gap:0.8rem; margin-bottom:0.8rem; }
.form-row.three { grid-template-columns:1fr 1fr 1fr; }
.form-row.four { grid-template-columns:1fr 1fr 1fr 1fr; }
.form-row.full { grid-template-columns:1fr; }
.form-group { display:flex; flex-direction:column; }
.form-group label { font-size:0.75rem; font-weight:600; color:#555; margin-bottom:0.2rem; }
.form-group input, .form-group select, .form-group textarea { padding:0.4rem 0.6rem; border:1px solid #ddd; border-radius:4px; font-size:0.85rem; font-family:inherit; }
.form-group textarea { resize:vertical; }
```

Shared `components/form-group.css` deve cobrir todos estes selectores. Se não, **PARAR** e reportar.

- [ ] **Step 2: Remove the block**

Remover o cluster completo e substituir por comment marker:

```css
/* form-row + form-group — MIGRATED to shared/styles/components/form-group.css (Plan 5 Task 4) */
```

- [ ] **Step 3: Build and visual check focused on form-heavy sections**

Testar visualmente:
- Registo de Serviço (form-row two/three columns, inputs, selects, textareas)
- Avaria Equipamento (campos texto)
- Tempo Resposta (inputs type=time)
- Controlo de Estoque (inputs type=number)
- Sistema → Configurações (todos os tabs têm forms)

Expected: inputs com mesma altura, labels no mesmo estilo, grid 1/2/3/4 colunas funcional.

- [ ] **Step 4: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "refactor(ssci): consume shared form-group.css, drop legacy form-row/form-group"
```

---

## Task 5: Migrate card + stat-card (dash-card) to shared components

**Files:**
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`
- Read-only reference: `shared/styles/components/card.css`, `shared/styles/components/stat-card.css`

**Pre-flight:**

- [ ] **Step 1: Compare selectors**

```bash
rtk grep -n 'form-card\|dash-card\|dash-grid\|dash-icon\|dash-title\|dash-value' \
  packages/portal-ssci/src/Portal_PSCI_AWM.source.html
rtk read shared/styles/components/card.css
rtk read shared/styles/components/stat-card.css
```

Mapping esperado:
- `.form-card` → card.css `.card` + `.card-with-header` (wrapper genérico com header `h3`)
- `.dash-card` + `.dash-icon` + `.dash-title` + `.dash-value` → stat-card.css `.stat-card`, `.stat-card-icon`, `.stat-card-title`, `.stat-card-value`

**Decisão de naming**: duas opções possíveis, à escolha do implementador da Task 5:

**Opção A** (preferida se Plan 3 já renomeou o COE). Usar os novos class names do DS (`.card`, `.stat-card`, ...) em vez dos legados (`.form-card`, `.dash-card`, ...). Isto requer **também** editar o HTML do SSCI source para renomear as classes usadas no body. ~30–50 edições mas é definitivo.

**Opção B** (preservar naming legado). Manter `.form-card` / `.dash-card` como aliases que consumem tokens DS. Nesse caso, Plan 3 deve ter adicionado aliases no `shared/styles/components/card.css`. Verificar. Se sim, não há nada a fazer além de remover os legacy selectors.

**Acção baseada no que o Plan 3 escolheu para o COE**: inspeccionar o COE source como referência.

```bash
rtk grep -n 'form-card\|dash-card\|class="card"\|class="stat-card"' \
  packages/portal-coe/src/Portal_COE_AWM.source.html
```

Se o COE usa `.card`/`.stat-card` — Plan 5 aplica Opção A ao SSCI (renomear classes + remover legacy). Se o COE mantém `.form-card`/`.dash-card` como aliases — Plan 5 aplica Opção B.

- [ ] **Step 2: Remove legacy selectors from block 1 (accompanied by HTML renaming if Opção A)**

Remover as regras `.form-card`, `.form-card h3`, `.dash-grid`, `.dash-card`, `.dash-card .dash-icon`, `.dash-card .dash-title`, `.dash-card .dash-value`. Substituir por comment marker:

```css
/* form-card + dash-card — MIGRATED to shared/styles/components/{card,stat-card}.css (Plan 5 Task 5) */
```

Se Opção A: executar uma substituição global no HTML body, `class="form-card"` → `class="card card-with-header"` (ou o que o Plan 3 definiu), `class="dash-card"` → `class="stat-card"`, `class="dash-grid"` → `class="stat-card-grid"`, `class="dash-icon"` → `class="stat-card-icon"`, `class="dash-title"` → `class="stat-card-title"`, `class="dash-value"` → `class="stat-card-value"`. Verificar contagens antes/depois para garantir que todas as ocorrências foram substituídas.

- [ ] **Step 3: Build and visual check focused on Dashboard and Form sections**

Visual check:
- Dashboard stat cards (Categoria SCI, CAT Actual, Viaturas, Efectivo, Comunicações) — paddings, borders, border-top color do stat-card
- Form-cards em Registo de Serviço, Inspecções, Avaria, Tempo Resposta — paddings, sombras, `h3` headers

- [ ] **Step 4: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "refactor(ssci): consume shared card.css + stat-card.css, drop legacy form-card/dash-card"
```

---

## Task 6: Migrate table (check-table base) to shared components/table.css

**Files:**
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`
- Read-only reference: `shared/styles/components/table.css`

**Context crítico:** `.check-table` é usada pelos checklists VCI, e **o layout do check-table é domain-specific** (colunas OK/NOK, obs cell largura fixa, secção headers). O **base table styling** (border-collapse, th background, hover, zebra) **é** migrável para `table.css` partilhado. Os refinamentos domain-specific **ficam** no SSCI block 1 como overrides que consomem tokens DS.

- [ ] **Step 1: Identify which rules are base vs domain**

```bash
rtk grep -n '\.check-table' packages/portal-ssci/src/Portal_PSCI_AWM.source.html
```

Expected rules (linhas ~64–73):
```
.check-table { width:100%; border-collapse:collapse; font-size:0.82rem; }                              [BASE — migrate]
.check-table th { background:var(--dark-blue); color:white; padding:0.5rem; ... }                      [BASE — migrate]
.check-table th:first-child { text-align:left; }                                                      [BASE — migrate]
.check-table td { padding:0.4rem 0.5rem; border-bottom:1px solid #eee; }                              [BASE — migrate]
.check-table tr:nth-child(even) { background:#fafafa; }                                               [BASE — migrate]
.check-table td:not(:first-child) { text-align:center; width:50px; }                                  [DOMAIN — keep]
.check-table .obs-cell { width:120px; }                                                                [DOMAIN — keep]
.check-table .obs-cell input { width:100%; ... }                                                       [DOMAIN — keep]
.check-table input[type="checkbox"] { width:16px; height:16px; ... }                                  [DOMAIN — keep]
.check-table .section-header { background:#e8f4fd; font-weight:700; color:var(--dark-blue); }         [DOMAIN — keep]
```

Nota: as base rules assumem que o `table.css` partilhado tem um class `.table` genérica. Decisão: em vez de renomear `.check-table` → `.table`, criar as base rules **via** `.check-table` (aliasing). **Opção mais limpa**: Plan 3's `table.css` deve incluir `.table` as primary e `.check-table` as a defensive alias — verificar no `shared/styles/components/table.css`. Se não tiver, Plan 5 remove as base rules do block 1 e adiciona o alias no SSCI source como override local (uma linha: `.check-table { /* inherits from .table via alias */ }` ou simplesmente renomeia `.check-table` → `.table` no HTML body de todas as checklists SSCI).

**Recomendação**: fazer o rename no HTML (`class="check-table"` → `class="table check-table"`) e manter os DOMAIN selectors como refinamentos — isto deixa o naming coerente com o DS e preserva o comportamento.

- [ ] **Step 2: Apply the rename + remove base rules**

- Remove base rules da block 1 (linhas ~64, ~65, ~66, ~67, ~68 do mapping acima)
- Keep domain rules: `td:not(:first-child)`, `.obs-cell`, `input[type="checkbox"]`, `.section-header`
- Global rename no HTML body: `class="check-table"` → `class="table check-table"` (adiciona `.table` sem retirar `.check-table`)

Substituir os 5 base rules por comment marker:

```css
/* .check-table base rules — MIGRATED to shared/styles/components/table.css (Plan 5 Task 6)
   Domain-specific refinements for VCI inspection checklists remain below. */
```

- [ ] **Step 3: Build and visual check — VCI checklists are the critical surface**

Testar:
- Inspecção Whisky 01 + Whisky 02 (tabela completa com secção-headers)
- Eqp. Resgate W01/W02 (outra variante de check-table)
- Teste Comunicações (check-table diferente)
- CheckList COE / CheckList PCM (mensais)

Expected: tabelas com mesma aparência (header azul, zebra, row hover se o `table.css` do Plan 3 incluir hover), checkboxes alinhados ao centro, obs cells com largura fixa, section headers destacados.

- [ ] **Step 4: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "refactor(ssci): consume shared table.css, keep VCI domain refinements"
```

---

## Task 7: `.separator` — no-op (not extracted by Plan 3)

**Files:** none (verification only)

**Context:** Plan 3's File Structure (13 component files) does **not** include `divider.css`. The selector `.separator` in SSCI block 1 line ~84 (`.separator { border:none; border-top:2px solid var(--medium-blue); margin:1rem 0; }`) has no shared destination and stays exactly where it is. Plan 5 does nothing with it.

- [ ] **Step 1: Confirm Plan 3 did not extract `divider.css`**

```bash
ls shared/styles/components/divider.css 2>&1 || echo "Not present — expected"
```

Expected: not present. If it somehow exists (unplanned Plan 3 addition), re-read Plan 3 and decide whether to migrate — but by default this task is a no-op.

- [ ] **Step 2: Document the decision and move on**

No CSS edits, no HTML edits, no commit. The `.separator` rule stays in SSCI consolidated block 1 exactly as it is. It consumes `var(--medium-blue)` which is a legacy token that Plan 6 will rename globally; the token alias layer from Plan 1/2 already makes it resolve correctly.

**Rationale**: Plan 5's invariant is "consume what Plans 3/4 produced, remove legacy duplicates". There is no shared divider component to consume, so the legacy rule can't be removed as a duplicate. Plan 6 (cleanup) may decide to either extract a `divider.css` component or fold `.separator` into `global.css`. Either way, that is out of scope here.

---

## Task 8: Migrate awm-modal to shared components/awm-modal.css

**Files:**
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`
- Read-only reference: `shared/styles/components/awm-modal.css`

**Risco médio-alto**: o modal system tem animações keyframes, variantes (default/warning/danger) e overlays. Plan 3 garantidamente re-tokenizou isto do COE. Aqui no SSCI apenas **removemos** os selectors legados porque o shared CSS já os serve.

- [ ] **Step 1: Inventory SSCI awm-modal legacy CSS**

Linhas ~209–276 da block 1 (verified in fact sheet):

```
.awm-modal-overlay, .awm-modal-overlay.awm-modal-closing
.awm-modal, .awm-modal-header, .awm-modal-icon
.awm-modal-warning .awm-modal-icon, .awm-modal-danger .awm-modal-icon
.awm-modal-title, .awm-modal-warning .awm-modal-title, .awm-modal-danger .awm-modal-title
.awm-modal-body, .awm-modal-footer
.awm-modal-btn, .awm-modal-btn-cancel, .awm-modal-btn-primary, .awm-modal-btn-danger
@keyframes awmModalFade, @keyframes awmModalPop
@media (max-width:520px) { .awm-modal-footer { flex-direction: column-reverse; } .awm-modal-btn { width:100%; } }
```

- [ ] **Step 2: Verify shared/styles/components/awm-modal.css has equivalents**

```bash
rtk read shared/styles/components/awm-modal.css
```

Tem que ter os mesmos class names (classe API is contractual — não renomear) e os mesmos keyframes. Se o Plan 3 renomeou os keyframes (improvável — viola o contrato "API JS preservada"), **PARAR** e rever.

- [ ] **Step 3: Remove legacy awm-modal CSS from block 1**

Substituir o bloco todo (incluindo `@keyframes awmModalFade`, `@keyframes awmModalPop` e o `@media (max-width:520px)` relativo aos awm-modal, mas **não** o `@media` relativo aos awm-toasts) por comment marker:

```css
/* awm-modal — MIGRATED to shared/styles/components/awm-modal.css (Plan 5 Task 8) */
```

**Atenção ao @media (max-width: 520px)**: linhas 298–303 contêm regras para **ambos** awm-modal e awm-toast. Dividir com cuidado — ou mover toda a media query no Task 9 (awm-toast) se o Plan 3's awm-modal.css já incluir responsive internamente.

- [ ] **Step 4: Build and smoke test modal**

Testar:
- `window.awmAlert('Test', 'error')` via DevTools console — ver variante danger
- `window.awmAlert('Warning', 'warning')` — ver variante warning
- `window.awmConfirm('Delete?')` (se existir) — ver botões cancel + danger
- Eliminar uma linha de equipamento em Configurações → dispara um confirm modal

Expected: aparência idêntica ao baseline, animações smooth, focus trap funcional, Esc fecha.

- [ ] **Step 5: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "refactor(ssci): consume shared awm-modal.css, preserve JS API contract"
```

---

## Task 9: Migrate awm-toast to shared components/awm-toast.css

**Files:**
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`
- Read-only reference: `shared/styles/components/awm-toast.css`

- [ ] **Step 1: Inventory SSCI awm-toast legacy CSS**

Linhas ~152–207 (fact sheet):

```
#awmToastContainer, .awm-toast, .awm-toast.awm-toast-out
.awm-toast-success, .awm-toast-warning, .awm-toast-error, .awm-toast-info
.awm-toast-icon, .awm-toast-body, .awm-toast-title
.awm-toast-success .awm-toast-title, .awm-toast-warning .awm-toast-title, .awm-toast-error .awm-toast-title
.awm-toast-msg, .awm-toast-close, .awm-toast-close:hover
.awm-toast-progress, .awm-toast-success/warning/error .awm-toast-progress
@keyframes awmToastIn, @keyframes awmToastOut, @keyframes awmToastProgress
@media (max-width:520px) { #awmToastContainer { ... }; .awm-toast { ... } }
```

- [ ] **Step 2: Verify shared/styles/components/awm-toast.css has equivalents**

```bash
rtk read shared/styles/components/awm-toast.css
```

- [ ] **Step 3: Remove legacy awm-toast CSS**

Substituir por comment marker:

```css
/* awm-toast — MIGRATED to shared/styles/components/awm-toast.css (Plan 5 Task 9) */
```

Atenção ao `@media (max-width:520px)`: se ainda houver regras awm-toast nesse media query, remover; se já foram removidas na Task 8 por completo, skip.

- [ ] **Step 4: Build and smoke test**

No DevTools console:
```js
window.notify('Serviço guardado', 'success');
window.notify('Falta preencher campo', 'warn');
window.notify('Erro ao gravar', 'error');
window.notify('Informação', 'info');
```

Expected: 4 toasts visíveis, cada um com border-left na cor semântica, animação de entrada, progress bar, close button funcional.

- [ ] **Step 5: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "refactor(ssci): consume shared awm-toast.css, preserve window.notify API"
```

---

## Task 10: Migrate save badge to shared components/uxp-savebadge.css

**Files:**
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`
- Read-only reference: `shared/styles/components/uxp-savebadge.css`

**Contexto importante**: No SSCI, o save badge vive na **UXP layer** (linhas ~365–383), prefixado com `.uxp-savebadge`. Plan 3 preserva deliberadamente este class name real: o ficheiro partilhado chama-se `components/uxp-savebadge.css` (NÃO `awm-save-badge.css`) precisamente porque a class name legacy do COE é também `.uxp-savebadge`. O JS do SSCI (linhas ~3641–3660) cria `saveBadge.className = 'uxp-savebadge'` — essa string é o contrato e **não muda**.

- [ ] **Step 1: Verify Plan 3's save badge file name and class**

```bash
rtk read shared/styles/components/uxp-savebadge.css
```

Expected: o ficheiro existe, usa `.uxp-savebadge` como class principal (verificar top-of-file banner a dizer algo como "class is uxp-*, not awm-*"). Se não existir, **PARAR** e reportar — Plan 5 não inventa nada.

- [ ] **Step 2: Remove legacy uxp-savebadge CSS from block 1**

Remover linhas ~365–383 (todos os `.uxp-savebadge`, `.uxp-savebadge.visible`, `.uxp-savebadge.saving`, `.uxp-savebadge.saved`, `.uxp-savebadge .dot`, `.uxp-savebadge.saving .dot`, `.uxp-savebadge.saved .dot`, `@keyframes uxp-pulse`).

Substituir por comment marker:

```css
/* uxp-savebadge — MIGRATED to shared/styles/components/uxp-savebadge.css (Plan 5 Task 10) */
```

- [ ] **Step 3: No JS changes — class name is preserved**

Plan 3 keeps the `.uxp-savebadge` class verbatim (see Plan 3 Task 11 banner). Plan 5 **não renomeia nada**: as linhas ~3641–3660 do SSCI source ficam intocadas. `saveBadge.className = 'uxp-savebadge'` continua correcto e o CSS partilhado casa porque usa o mesmo selector.

- [ ] **Step 4: Build and smoke test**

Abrir o portal, ir a qualquer form (Registo de Serviço, Avaria), editar um campo, esperar ~1.5s. O save-badge deve aparecer top-right com "A guardar..." → "Guardado".

- [ ] **Step 5: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "refactor(ssci): consume shared uxp-savebadge.css for persistence indicator"
```

---

## Task 11: Skeleton + empty-state — verify no legacy exists

**Files:** none (verification only)

- [ ] **Step 1: Grep SSCI source for skeleton / empty-state selectors**

```bash
rtk grep -n 'skeleton\|empty-state\|placeholder' packages/portal-ssci/src/Portal_PSCI_AWM.source.html
```

Expected: SSCI **não** tem CSS legado para skeleton ou empty-state. Ambos foram adicionados pelo Plan 3 como novos componentes no DS. SSCI pode usá-los no futuro ou não — nesta passagem zero legacy a remover.

Se a grep retornar resultados (inesperado), documentar e decidir ad-hoc se migrar ou não.

- [ ] **Step 2: Mark task as no-op and skip commit**

Esta task é documentalmente concluída sem commit. Seguir para Task 12.

---

## Task 12: Tabs + dropdown — verify no legacy exists

**Files:** none (verification only)

- [ ] **Step 1: Grep SSCI source for tabs/dropdown selectors**

```bash
rtk grep -n '\.tab-btn\|\.tabs\b\|dropdown\|menu-item\|psci-cfg-tab' \
  packages/portal-ssci/src/Portal_PSCI_AWM.source.html
```

Expected:
- `.psci-cfg-tab-btn` — é uma implementação **local inline** em `<style>` dos botões tab do Sistema → Configurações (linhas ~2014 no HTML body, CSS inline). Não está na consolidated block 1 porque foi escrito inline em `style="..."` attributes. **Decisão**: deixar como está — é domain da página de Configurações, não vale a pena migrar (é ~5 linhas de style inline repetidas).
- Nenhuma regra `.tabs` / `.tab-btn` na block 1.
- Nenhuma regra `dropdown` / `menu-item` em lado nenhum.

- [ ] **Step 2: Mark task as no-op**

SSCI não tem tabs/dropdowns no sentido do DS. As "tabs" das configurações são estilo inline que consome já `var(--dark-blue)` de forma ad-hoc. Seguir para Task 13.

**Observação para Plan 6**: o `psci-cfg-tab-btn` inline styling é um candidato para futura refactoring via `shared/styles/components/tabs.css`, mas não é bloqueante para o DS migration.

---

## Task 13: Chrome swap — HTML surgery replacing header + sidebar + layout + splash + footer

**Files:**
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html` — **mudança maior**
- Read-only reference:
  - `shared/styles/chrome/shell-bar.css`
  - `shared/styles/chrome/sidebar.css`
  - `shared/styles/chrome/page-grid.css`
  - `shared/styles/chrome/splash.css`
  - `shared/styles/chrome/footer.css`
  - `shared/styles/base/reset.css`, `typography.css`, `global.css`
  - `shared/assets/logo-sga-mark.svg`, `logo-sga-full.svg`

**This is the visual change task.** After this task, the SSCI looks visibly different from the baseline — that is the **intentional visual change**. User must validate before the task is marked done.

**Decomposition** (sub-commits):
- Task 13a — Adicionar placeholders e markup base (header + sidebar + splash + footer + version footer re-positioned)
- Task 13b — Remover CSS chrome legado da block 1 (reset, body, header, layout, sidebar, nav-item, main, section, page-title, page-desc, responsive)
- Task 13c — Actualizar JS para novos IDs (clock, turno, openSection)
- Task 13d — Smoke test do novo chrome

### Task 13a — Replace HTML chrome markup

- [ ] **Step 1: Read the COE Plan 4 task 13 equivalent for reference**

```bash
rtk read packages/portal-coe/src/Portal_COE_AWM.source.html
```

Procurar o bloco `<!-- DS Shell Bar (replaces legacy <header>) -->` (Plan 4 Task 11 Step 11.2, linhas ~3253–3269 do COE source post-Plan-4). **Copiar a estrutura** adaptando:
- `{{PORTAL.NAME}}` já é `Portal SSCI` via `portal.config.json`
- `{{PORTAL.TAGLINE}}` é `Serviço de Salvamento e Combate a Incêndios`
- **Ocorrência pill** é omitida — `portal.config.json::ui.show_occurrence_pill = false`. **Reality check importante**: Plan 4 **NÃO** implementou nenhum placeholder `{{PORTAL.UI_SHOW_OCCURRENCE_PILL}}` nem qualquer conditional build-time. O elemento `<div class="ds-shell-bar__emg-pill" id="dsEmgPill">...</div>` é emitido **incondicionalmente** no markup do COE (Plan 4 Task 11 Step 11.2, linha ~1888 do plano). O runtime toggle usa `data-active="true"` via JS cronómetro. Portanto, ao copiar o shell bar para o SSCI, Plan 5 tem que **remover explicitamente** o elemento `<div class="ds-shell-bar__emg-pill">...</div>` da cópia — é uma omissão hard-coded no SSCI source.
- **Emergency stopwatch** é omitido — `ui.show_emergency_stopwatch = false`. Mesma lógica: Plan 4 não tem conditional build, o elemento existe sempre no markup COE; Plan 5 omite-o explicitamente no SSCI. (No COE o stopwatch vive dentro do próprio emg-pill — ver `#dsEmgPillChrono` — portanto omitir o pill inteiro cobre ambos os flags.)
- **UTC clock** é incluído — `ui.show_utc_clock = true`. **Decisão (obrigatória)**: preservar os IDs exactos do Plan 4 (`headerUTC`, `clockDisplay`, `headerDate`) no markup SSCI para que o helper `shared/scripts/utilities/date-utc.js` — que escreve nesses IDs e curto-circuita via `dsDateUtcInstalled` — funcione out-of-the-box na Task 14. O `updateClock()` reescrito em Task 13c Step 1 também escreve nesses IDs.

**Nota sobre unification futura**: as flags `ui.show_occurrence_pill`, `ui.show_emergency_stopwatch` em `portal.config.json` são actualmente **não consumidas por nenhum placeholder**. Plan 5 hard-codes a omissão no SSCI source. Plan 6 (ou uma task futura) pode unificar isto introduzindo `{{PORTAL.UI_SHOW_OCCURRENCE_PILL}}` como flatten placeholder conditional no build. **Adiar deliberadamente**.

- [ ] **Step 2: Write the new header block in SSCI source**

Substituir linhas 480–489 (o `<div class="header">...</div>` actual) pelo novo shell bar. **Usar exactamente a estrutura que Plan 4 Task 11 Step 11.2 produziu para o COE** — NÃO inventar class names. Os class names canónicos (verificados em `shared/styles/chrome/shell-bar.css`) são: `.ds-shell-bar`, `.ds-shell-bar__brand`, `.ds-shell-bar__logo`, `.ds-shell-bar__portal-name`, `.ds-shell-bar__separator`, `.ds-shell-bar__oaci`, `.ds-shell-bar__breadcrumb`, `.ds-shell-bar__breadcrumb-item`, `.ds-shell-bar__meta`, `.ds-shell-bar__clocks`, `.ds-shell-bar__utc`, `.ds-shell-bar__local`, `.ds-shell-bar__operator`, `.ds-shell-bar__emg-pill` (a omitir).

Template para o SSCI (cópia fiel do Plan 4, com o emg-pill removido e sem `.header-title-small` dual class — o SSCI não usa esse contrato legacy):

```html
<!-- ======================================================================
     DS Shell Bar (replaces legacy <div class="header">) — Plan 5 Task 13a
     Copied verbatim from COE shell bar (Plan 4 Task 11 Step 11.2) with:
       - .ds-shell-bar__emg-pill element REMOVED (SSCI
         portal.config.json::ui.show_occurrence_pill = false
         and ui.show_emergency_stopwatch = false; Plan 4 emits the
         pill unconditionally, so Plan 5 hard-codes the omission here)
       - .header-title-small dual class OMITTED (SSCI has no
         cfgApplyToPortal() JS writing to that class)
     ====================================================================== -->
<header class="ds-shell-bar" role="banner">
    <div class="ds-shell-bar__brand">
        <span class="ds-shell-bar__logo" aria-hidden="true">
            <svg viewBox="0 0 32 32"><use href="#icon-sga-mark"/></svg>
        </span>
        <span class="ds-shell-bar__portal-name">{{PORTAL.NAME}}</span>
        <span class="ds-shell-bar__separator" aria-hidden="true"></span>
        <span class="ds-shell-bar__oaci">{{AIRPORT.OACI}}</span>
    </div>

    <div class="ds-shell-bar__breadcrumb" aria-label="Navigation breadcrumb">
        <span class="ds-shell-bar__breadcrumb-item" id="dsBreadcrumbCurrent">Dashboard</span>
    </div>

    <div class="ds-shell-bar__meta">
        <!-- NOTE: ds-shell-bar__emg-pill intentionally omitted.
             Plan 4 emits it unconditionally at this position (Plan 4
             Task 11 Step 11.2 line ~1888). SSCI config sets both
             show_occurrence_pill=false and show_emergency_stopwatch=false,
             and Plan 4 implements NO build-time conditional. Hard-coding
             the omission here is the correct Plan 5 behaviour; Plan 6
             may unify via a flatten placeholder. -->

        <div class="ds-shell-bar__clocks">
            <!-- IDs preserved verbatim from Plan 4 so that
                 shared/scripts/utilities/date-utc.js writes to them
                 out-of-the-box (see Task 14.1). -->
            <div class="ds-shell-bar__utc" id="headerUTC">UTC 00:00:00</div>
            <div class="ds-shell-bar__local" id="clockDisplay">00:00:00</div>
            <div class="ds-shell-bar__local" id="headerDate" style="display:none;"></div>
        </div>

        <!-- Turno badge — SSCI specific (COE uses operatorBadge instead) -->
        <div class="ds-shell-bar__operator" id="psci-turno" data-turno="—">Turno: —</div>
    </div>
</header>
```

**Se ao ler `shared/styles/chrome/shell-bar.css` algum class name diferir do acima** (ex: `.ds-shell-bar__clocks` renomeado para `.ds-shell-bar__clock-group`), **copiar a convenção exacta do ficheiro** — não inventar. A task 13a falha se o naming divergir do Plan 4.

- [ ] **Step 3: Write the new sidebar block**

Substituir `<nav class="sidebar">...</nav>` (linhas ~494–530) pelo novo markup ds-sidebar. Preservar a estrutura dos 6 section groups e dos **17** nav items, mas aplicar **duas mudanças obrigatórias** que herdamos do contrato Plan 4:

1. **Class name rename `.nav-item` → `.nav-btn`** (NOT optional). Plan 4 converteu o COE para usar `class="nav-btn"` como class canónica — é o filtro que `openSection()` usa (`document.querySelectorAll('.nav-btn')`). SSCI tem que usar o mesmo class name para consumir o mesmo CSS `shared/styles/chrome/sidebar.css` (que tem rules scoped a `.ds-sidebar .nav-btn`). **Todas as 17** ocorrências de `class="nav-item"` e `class="nav-item active"` no body do SSCI passam a `class="nav-btn"` / `class="nav-btn active"`.

2. **Assinatura `openSection(id, event)` — 2 argumentos**. Plan 4 alterou o contrato da função (Plan 4 fact sheet linha ~76: `function openSection(sectionId, event) { ... }`). SSCI tem que seguir o mesmo: **todas as 17** ocorrências de `onclick="openSection('xxx')"` no sidebar SSCI passam a `onclick="openSection('xxx', event)"`. Além disso, os 4 botões de atalho do Dashboard (linhas 594–597 do source: `<button class="btn btn-primary" onclick="openSection('reg-servico')" ...>` etc.) também têm que ser actualizados para passar `event`. Total: **21 edições de onclick**.

A estrutura do markup DS sidebar segue exactamente Plan 4 Task 11 Step 11.2: wrapper `<aside class="ds-sidebar">`, sections como `<div class="ds-sidebar__section">` com `<h3 class="ds-sidebar__section-title">` + `<ul class="ds-sidebar__list">` + `<li>` items. Verificar os class names exactos em `shared/styles/chrome/sidebar.css`.

Exemplo de uma nav item (template, aplicar aos 17):

```html
<li><a href="#" onclick="openSection('dashboard', event)" class="nav-btn active">
    <span class="nav-icon">📊</span>Dashboard
</a></li>
```

Os 6 section groups do SSCI são: Painel (2 items), Formulários Diários (6 items), Formulários Operacionais (4 items), Recursos (1 item), Checklists Mensais (2 items), Sistema (2 items). Total 17. (O source atualmente tem 17 botões; a fact sheet anterior dizia 18 — era um erro que esta task corrige.)

Sobre os **nav icons**: o SSCI actualmente usa emoji (🚒, 🗺, 📋, etc.). O DS spec §4.2 diz `ícone 20x20` via SVG inline usando o sprite. **Decisão**: substituir cada emoji pelo `<svg><use href="#icon-X"/></svg>` apropriado. Mapeamento proposto (verificar contra `shared/assets/icons/sprite.svg` o que o Plan 4 incluiu):

| nav-item | emoji actual | sprite id proposto | fallback se não existir |
|---|---|---|---|
| Dashboard | 📊 | `#icon-dashboard` | manter 📊 |
| Mapas Quadrícula | 🗺 | `#icon-map` | manter 🗺 |
| Registo de Serviço | 📋 | `#icon-clipboard` | manter 📋 |
| Inspecção Whisky 01/02 | 🚒 | `#icon-truck` ou `#icon-fire-truck` | manter 🚒 |
| Eqp. Resgate W01/W02 | 🧰 | `#icon-tools` | manter 🧰 |
| Teste Comunicações | 📡 | `#icon-antenna` ou `#icon-radio` | manter 📡 |
| Avaria Equipamento | ⚠ | `#icon-alert-triangle` | manter ⚠ |
| Abastecimento VCI | ⛽ | `#icon-fuel` | manter ⛽ |
| Tempo Resposta | ⏱ | `#icon-clock` | manter ⏱ |
| Lista Presença | ✅ | `#icon-check-circle` | manter ✅ |
| Controlo de Estoque | 📦 | `#icon-package` | manter 📦 |
| CheckList COE | 📝 | `#icon-document-check` | manter 📝 |
| CheckList PCM | 📝 | `#icon-document-check` | manter 📝 |
| Guia Rápido | ❓ | `#icon-help` | manter ❓ |
| Configurações | ⚙ | `#icon-settings` | manter ⚙ |

Se um sprite id não existir no `sprite.svg` entregue pelo Plan 4, **manter o emoji** (inline como `<span class="ds-sidebar__nav-icon-emoji">📊</span>`) e registar na lista de pendências para Plan 6 ou para uma future task de icon extension. **Não criar ícones neste plano** — isso violaria o "nenhum ficheiro em shared/" contract.

Os `onclick` handlers são obrigatoriamente **reescritos** para a assinatura 2-arg (`openSection('xxx', event)`) já nesta task 13a, como descrito no topo do Step 3. Task 13c acaba por actualizar a própria função `openSection()` para aceitar o 2º parâmetro.

- [ ] **Step 4: Add splash screen markup right after `<body>`**

Antes do `{{ICON_SPRITE}}`, inserir (estrutura copiada do Plan 4 Task 11 Step 11.2 — mesmo ID `dsSplash`, mesmo `data-state="in"`, mesmo uso de `<use href="#icon-sga-mark"/>`):

```html
<!-- ======================================================================
     Splash screen (Plan 5 Task 13a) — fade-out via inlined splash.js
     Bypass: append ?nosplash=1 to URL
     ID and data-state contract come from Plan 4; the inlined script
     is also from Plan 4 Task 12 Step 12.4 (see Task 13c Step 4).
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
```

Se o naming do `shared/styles/chrome/splash.css` (Plan 4) diferir em algum class name BEM, ajustar; a regra geral é **preservar exactamente o que Plan 4 commitou** em `packages/portal-coe/src/Portal_COE_AWM.source.html`.

- [ ] **Step 5: Move version footer from sidebar to institutional footer**

Actualmente o `sidebar-version-footer` vive dentro da sidebar. O spec §4.5 diz que o footer institucional é uma linha fina no fundo do content do page-grid. Retirar do markup da sidebar e adicionar ao fim do `<div class="main">` (ou fora dela no `<div class="layout">`):

```html
<!-- DS INSTITUTIONAL FOOTER -->
<footer class="ds-footer" role="contentinfo">
    <div class="ds-footer__content">
        SGA — Sociedade de Gestão Aeroportuária
        · {{PORTAL.NAME}} v{{VERSION}}
        · {{AIRPORT.OACI}}
        · Build {{BUILD_DATE_SHORT}}
    </div>
</footer>
```

- [ ] **Step 6: Update `<body>` tag + page grid wrapper**

Garantir que o `<body>` e o layout wrapper usam classes do page-grid.css. Pode requerer envolver o `<div class="layout">` existente (ou renomear) para:

```html
<body class="ds-body">
  {{ICON_SPRITE}}
  <div class="ds-splash">...</div>
  <div id="awmToastContainer">...</div>
  <header class="ds-shell-bar">...</header>
  <div class="ds-page-grid">
    <nav class="ds-sidebar">...</nav>
    <main class="ds-main" id="main-content">
      <!-- DASHBOARD, MAPAS, ... sections intactas aqui -->
    </main>
  </div>
  <footer class="ds-footer">...</footer>
</body>
```

- [ ] **Step 7: Commit 13a**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "feat(ssci): add DS shell bar, sidebar, splash, and footer markup (Plan 5 Task 13a)"
```

**Nota**: depois deste commit o SSCI **ainda não renderiza correctamente** porque o CSS legado da header/sidebar ainda está activo. Isso corrige-se no 13b.

### Task 13b — Remove legacy chrome CSS from block 1

- [ ] **Step 1: Remove all chrome-related rules from consolidated block 1**

Em linhas ~24 a ~104 da block 1, remover:
- `*` reset rule (substituído por `base/reset.css` que o DS já serve)
- `body { font-family: 'Segoe UI'... }` (substituído por `base/typography.css`)
- `.header`, `.header h1`, `.header-sub`, `.header-badge` (substituído por `chrome/shell-bar.css`)
- `.layout`, `.sidebar`, `.sidebar h3`, `.sidebar h3:first-child`, `.nav-item`, `.nav-item:hover`, `.nav-item.active`, `.nav-icon` (substituído por `chrome/sidebar.css`)
- `.main`, `.section`, `.section.active` (substituído por `chrome/page-grid.css` — **atenção**: o `.section.active` visibility toggle é crítico para o JS `openSection`. Se `chrome/page-grid.css` não tem a regra, manter apenas essa)
- `h1.page-title`, `.page-desc` (substituído por `chrome/page-grid.css` ou `base/typography.css`)
- `.time-display` (chrome)
- `@media (max-width: 768px)` — toda a media query responsive do chrome legado

Substituir por comment marker:

```css
/* Chrome (reset, body, header, layout, sidebar, main, section, responsive)
   — MIGRATED to shared/styles/{base,chrome}/*.css (Plan 5 Task 13b) */
```

**Verificação crítica**: a regra `.section { display: none; }` + `.section.active { display: block; }` é **essencial** para o funcionamento do `openSection()`. Se o `chrome/page-grid.css` do Plan 4 não a contiver (porque o COE pode usar um mecanismo diferente de navegação), **manter** essa regra no SSCI source como local override:

```css
/* Section visibility toggle — kept as local override for openSection() JS */
.section { display: none; }
.section.active { display: block; }
```

- [ ] **Step 2: Commit 13b**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "refactor(ssci): remove legacy chrome CSS, consume DS chrome (Plan 5 Task 13b)"
```

### Task 13c — Update JS for new DOM IDs and clock behavior

- [ ] **Step 1: Update `updateClock()` function**

Actual (linhas ~2159–2168):
```js
function updateClock() {
    var now = new Date();
    var h = String(now.getHours()).padStart(2,'0');
    var m = String(now.getMinutes()).padStart(2,'0');
    var el = document.getElementById('psci-clock');
    if (el) el.textContent = h + ':' + m + ' — ' + now.toLocaleDateString('pt-PT');
}
updateClock();
setInterval(updateClock, 30000);
```

Nova versão — **escrever nos IDs preservados do Plan 4** (`headerUTC`, `clockDisplay`) que a Task 13a Step 2 colocou no shell bar markup. Isto deixa Task 14 livre para, opcionalmente, substituir isto pelo inline do `shared/scripts/utilities/date-utc.js` (que escreve nesses mesmos IDs e curto-circuita via `dsDateUtcInstalled`):

```js
function updateClock() {
    var now = new Date();
    var utcH = String(now.getUTCHours()).padStart(2,'0');
    var utcM = String(now.getUTCMinutes()).padStart(2,'0');
    var utcS = String(now.getUTCSeconds()).padStart(2,'0');
    var locH = String(now.getHours()).padStart(2,'0');
    var locM = String(now.getMinutes()).padStart(2,'0');
    var locS = String(now.getSeconds()).padStart(2,'0');
    var utcEl = document.getElementById('headerUTC');
    var locEl = document.getElementById('clockDisplay');
    if (utcEl) utcEl.textContent = 'UTC ' + utcH + ':' + utcM + ':' + utcS;
    if (locEl) locEl.textContent = locH + ':' + locM + ':' + locS;
}
updateClock();
setInterval(updateClock, 1000);  // was 30000 — UTC clock needs second-level precision per spec §4.1
```

Nota: `setInterval(..., 1000)` vs `setInterval(..., 30000)` é uma mudança de comportamento. Isto está alinhado com o spec §4.1 que pede "actualiza a cada segundo" para o UTC clock. Revisor: confirmar que é aceitável (impacto: CPU idle mínimo).

**Alternativa (Task 14 Path A)**: em vez de manter este `updateClock()` inline, deletá-lo e inlinear directamente o conteúdo de `shared/scripts/utilities/date-utc.js` num `<script>` antes de `</body>` (como Plan 4 faz para o `splash.js`). A Task 14 Step 3 documenta este path.

- [ ] **Step 2: Verify `#psci-turno` ID is preserved**

Task 13a Step 2 deliberately keeps the ID `psci-turno` on the new `<div class="ds-shell-bar__operator" id="psci-turno">` element. Todo o JS existente que faz `document.getElementById('psci-turno')` continua a funcionar sem edições. Confirmar por grep:

```bash
rtk grep -n 'psci-turno' packages/portal-ssci/src/Portal_PSCI_AWM.source.html
```

Expected: um match no `id="psci-turno"` do shell bar markup + os matches do JS existente (PSCI_CFG + `updateTurno()` se existir). **Não renomear nada**. Se o reviewer preferir `shell-turno` por consistência estética com o naming DS, é uma decisão de Plan 6, não Plan 5.

- [ ] **Step 3: Update `.nav-item` selector and `openSection` signature — mandatory**

Plan 4 canonicalised `.nav-btn` as the class used by `openSection()` (verified at Plan 4 Task 11 Step 11.2). SSCI has to follow the same contract:

**(a) Rewrite `openSection()` to accept 2 arguments** and ignore the `event` parameter (or use it for `preventDefault()` when nav items are `<a>` elements, as in the COE markup):

```js
function openSection(id, event) {
    if (event && typeof event.preventDefault === 'function') event.preventDefault();
    document.querySelectorAll('.section').forEach(function(s) { s.classList.remove('active'); });
    // Query by the new class .nav-btn — matches both the Plan 4 contract and
    // the Task 13a markup rename (see Step 3 of Task 13a).
    document.querySelectorAll('.nav-btn').forEach(function(n) { n.classList.remove('active'); });
    var sec = document.getElementById(id);
    if (sec) sec.classList.add('active');
    document.querySelectorAll('.nav-btn').forEach(function(n) {
        if (n.getAttribute('onclick') && n.getAttribute('onclick').indexOf("'" + id + "'") > -1) {
            n.classList.add('active');
        }
    });
}
```

**(b) Grep sanity check** — confirm that after Task 13a edits + this rewrite, every remaining reference in the SSCI source to `.nav-item` or `nav-item` is either:
  - inside a legacy CSS rule in consolidated block 1 (which is about to be removed in Task 13b), or
  - inside a comment marker.

```bash
rtk grep -n '\.nav-item\|nav-item' packages/portal-ssci/src/Portal_PSCI_AWM.source.html
```

Expected: zero matches in active HTML markup or active JS after Task 13a + 13c. The old CSS declarations at lines 38–40, 100–101, 436 are removed in Task 13b.

**(c) Verify the 21 onclick calls were updated in Task 13a**. Quick grep:

```bash
rtk grep -n "openSection('" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
```

Every `openSection('xxx'...)` call in HTML must end with `, event)`. Expected count: **21** (17 sidebar nav-btn + 4 dashboard quick-access buttons). The grep results should show each call ending with `event)`. If any call is still 1-arg, go back to Task 13a Step 3 and fix it.

- [ ] **Step 4: Install splash fade-out handler**

**Plan 4 produziu `shared/scripts/chrome/splash.js`** com a lógica canónica (1500ms + fade-out via `data-state="out"` + `?nosplash=1`). Plan 5 **copia o mesmo script inline** para o SSCI source, imediatamente antes de `</body>`, usando o ID `dsSplash` (mesmo que Plan 4 colocou no COE). A Task 13a Step 4 já adicionou `<div class="ds-splash" id="dsSplash" data-state="in">` no topo do body; basta copiar o inline `<script>` do Plan 4 Task 12 Step 12.4 (minified):

```html
<!-- Plan 5 Task 13c — DS splash lifecycle (copy of Plan 4 Task 12 Step 12.4) -->
<script>
/* ==== shared/scripts/chrome/splash.js (inlined) ==== */
(function(){'use strict';function dismiss(s){s.setAttribute('data-state','done');}function init(){var s=document.getElementById('dsSplash');if(!s)return;try{var p=new URLSearchParams(window.location.search);if(p.get('nosplash')==='1'){dismiss(s);return;}}catch(e){}setTimeout(function(){s.setAttribute('data-state','out');},1500);setTimeout(function(){dismiss(s);},1900);}if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}})();
</script>
```

**Nota importante**: adicionar este bloco **imediatamente antes de `</body>`**, depois do último `<script>` existente (isto é, o script que define `updateClock`, `openSection`, `window.notify`, etc.). Se Task 13a Step 4 usou um ID diferente (`ds-splash` em vez de `dsSplash`), ajustar o `getElementById` aqui para bater certo — mas a recomendação é **usar o mesmo ID que Plan 4 (`dsSplash`) em Task 13a** por consistência.

- [ ] **Step 5: Commit 13c**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "feat(ssci): wire UTC clock (2s→1s), openSection 2-arg + .nav-btn, splash fade-out to new chrome (Plan 5 Task 13c)"
```

### Task 13d — Smoke test new chrome manually

- [ ] **Step 1: Build**

```bash
python scripts/build-all.py --only portal-ssci
```

Expected: build OK.

- [ ] **Step 2: Open in Chrome and visually verify against spec §4**

Check list:
- [ ] Splash screen aparece ~1.5s com logo SGA, "Portal SSCI", tagline DREA, OACI, versão
- [ ] Splash fade-out smooth
- [ ] Shell bar tem: logo SGA mark 32x32, "Portal SSCI" + role, separador, OACI
- [ ] Shell bar centro: breadcrumb "Dashboard"
- [ ] Shell bar direito: UTC clock em tabular-nums actualizando a cada segundo, Local clock abaixo, separador, "Turno: —"
- [ ] **Não há** emergency pill (SSCI `show_occurrence_pill=false`)
- [ ] **Não há** stopwatch (SSCI `show_emergency_stopwatch=false`)
- [ ] Faixa 4px azul-institucional debaixo do shell bar
- [ ] Sidebar light (canvas bg), section headings em uppercase small caps, border-right 1px neutral-muted
- [ ] Nav items 44px altura (comfortable density)
- [ ] Dashboard `.nav-btn.active` tem border-left 3px em `--brand-primary`
- [ ] Navegar entre secções: `openSection(id, event)` 2-arg continua a funcionar; secção activa mostra conteúdo, outras escondidas
- [ ] Footer institucional na linha do fundo, `--text-xs`, com version + OACI + build date
- [ ] Save badge, toasts, modal continuam a funcionar (testar via DevTools como nas tasks 8, 9, 10)
- [ ] Resize browser a 1024px → breadcrumb colapsa (spec §4.1)
- [ ] Resize a 768px → sidebar colapsa ou vira menu mobile conforme `chrome/sidebar.css`

- [ ] **Step 3: Capture new screenshots**

Tirar screenshots da nova aparência em `d:/tmp/plan5-postchrome/screenshots/` (mesmo conjunto da baseline: Dashboard, Registo de Serviço, Inspecção W01, Stock, Configurações, Guia Rápido, Print preview). Estes ficam ao lado dos baselines para apresentação ao utilizador.

- [ ] **Step 4: User validation gate**

**STOP**. Apresentar ao utilizador:
- Os screenshots baseline (`d:/tmp/plan5-baseline/screenshots/`)
- Os screenshots novos (`d:/tmp/plan5-postchrome/screenshots/`)
- Perguntar: "Confirmas que esta é a aparência pretendida para o Portal SSCI depois do Plan 5?"

Esperar confirmação explícita. Se o utilizador pedir ajustes (ex: "a faixa azul está demasiado fina"), fazer os ajustes pontuais no SSCI source **sem** criar novos ficheiros em `shared/` (aqueles são do Plan 4). Commit de ajustes: `fix(ssci): tune shell bar stripe thickness per user feedback`.

---

## Task 14: Wire SSCI JS to consume shared date-utc.js

**Files:**
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`
- Read-only reference: `shared/scripts/utilities/date-utc.js`, `shared/scripts/chrome/splash.js`

**Scope (reality-bound)**: Plans 3 and 4 produce exactly **two** shared JS files: `shared/scripts/chrome/splash.js` (wired into SSCI during Task 13a/13c as the splash lifecycle script) and `shared/scripts/utilities/date-utc.js` (the UTC ticker). Plan 3 extracts **zero** JS. Therefore this task is much smaller than originally outlined: it only covers **date-utc.js consumption**. The other would-be sub-tasks (lsGet/lsSet wrapper, esc-html helper, awm-modal.js, awm-toast.js, awm-save-badge.js) are **deferred to Plan 6 or later** because no corresponding shared file exists to consume. The SSCI inline implementations of `window.lsGet`/`lsSet`, `escHtml`/`psciEsc`, awm-modal focus trap, `window.notify`, and save badge **stay inline** in this plan — they already work and there is nothing to wire them to.

### Task 14.1 — date-utc.js wiring (was Task 14.6)

- [ ] **Step 1: Verify `shared/scripts/utilities/date-utc.js` exists (Plan 4 Task 12 produced it)**

```bash
rtk read shared/scripts/utilities/date-utc.js
```

Expected: file exists, IIFE that writes to element IDs `headerUTC`, `clockDisplay`, `headerDate`, `dashboardClock`, `dashboardUTC` and self-guards via `window.dsDateUtcInstalled`. Short-circuits if `window.updateHeaderClock` is defined.

- [ ] **Step 2: Confirm SSCI shell bar IDs match Plan 4 naming**

Task 13a Step 2 preserves the Plan 4 IDs `headerUTC`, `clockDisplay`, `headerDate` verbatim in the SSCI shell bar markup (that is the recommended decision). Confirm by grep:

```bash
rtk grep -n 'headerUTC\|clockDisplay\|headerDate' packages/portal-ssci/src/Portal_PSCI_AWM.source.html
```

Expected: matches inside the new `<div class="ds-shell-bar__clocks">` block (from Task 13a). If the IDs were renamed during Task 13a, either revert to the Plan 4 names or adapt `updateClock()` in Task 13c to target whatever IDs the SSCI uses — the simplest path is to keep Plan 4's naming.

- [ ] **Step 3: Decide between two integration paths**

**Path A (preferred)**: Use Plan 4's `date-utc.js` as the single source of truth. Delete the inline `updateClock()` body from the SSCI source (the one Task 13c wrote) and instead inline the content of `shared/scripts/utilities/date-utc.js` via a `<script>` block immediately before `</body>` (mirroring Plan 4 Task 12 Step 12.4 which inlines `splash.js`). The file's self-guard (`if (typeof window.updateHeaderClock === 'function') return;`) ensures zero double-ticking.

**Path B (fallback)**: Keep the inline `updateClock()` the Task 13c added and do nothing. This is acceptable if the Path A integration proves awkward; the inline function is only ~10 lines and consumes `var(--tabular-nums)` css without needing the shared file.

- [ ] **Step 4: Build and smoke test**

```bash
python scripts/build-all.py --only portal-ssci
```

Testar:
- Shell bar UTC clock ticks every second.
- `window.notify('test', 'info')` still works (inline `window.notify` untouched).
- `window.awmAlert('test', 'warning')` still works (inline modal untouched).
- Editar um form → save badge aparece (inline save-badge untouched).
- Recarregar a página → `PSCI_CFG` é lido correctamente (inline `lsGet`/`lsSet` untouched).

### Task 14.2 — Commit

- [ ] **Step 1: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "refactor(ssci): consume shared date-utc.js for shell bar clock ticker"
```

If Path B was chosen and nothing changed in the file, skip the commit entirely — this whole task becomes a verification-only pass. Document the decision in a small note (no empty commit).

**Deferred to Plan 6** (explicitly out of scope here because Plans 3/4 do not produce the shared files):
- `shared/scripts/utilities/ls-wrapper.js`
- `shared/scripts/utilities/esc-html.js`
- `shared/scripts/awm-modal.js`
- `shared/scripts/awm-toast.js`
- `shared/scripts/awm-save-badge.js`

The SSCI keeps these as inline implementations until someone extracts them in a future plan.

---

## Task 15: SSCI print stylesheet verification / adaptation

**Files:**
- Read-only reference: `shared/styles/print/print.css`
- Maybe modify: `shared/styles/print/print.css` (only if SSCI-specific rule needed)
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html` (remove any leftover `@media print` from block 1)

**Context:** SSCI consolidated block 1 tem dois `@media print` rules residuais:
1. Linhas ~435–441 — UXP layer hide-in-print (UXP skip, savebadge, toasts, totop, modal-bg)
2. Linhas ~452–464 — Print safety net (UXP elements + awm-modal-overlay + #awm-section-announcer + no-print)

Estes dois blocos sobrepõem-se ao `shared/styles/print/print.css` que o Plan 4 entregou. A maioria das regras já lá está. Verificar se há algo SSCI-específico.

- [ ] **Step 1: Compare existing print rules in SSCI block 1 vs shared print.css**

```bash
rtk read shared/styles/print/print.css
```

Listar regras que estão **só** na SSCI e não no shared:
- `@media print { .sidebar, .top-bar, nav, .nav-item, ... } { display: none !important; }` — este hide-all do chrome é chrome-based; shared `print.css` do Plan 4 já deve incluir `.ds-shell-bar`, `.ds-sidebar`, `.ds-footer` hide-in-print. Verificar.
- `.section { display: block !important; page-break-after: auto; }` — este mostra **todas** as secções em print (overriding o JS show/hide). Provavelmente o Plan 4 também incluiu isto para o COE. Verificar.
- `body { background: #fff !important; color: #000 !important; font-size: 11pt; }` — sim, shared `print.css` deve ter.
- `.card, .info-card { box-shadow: none !important; border: 1px solid #999 !important; page-break-inside: avoid; }` — provavelmente sim.
- **Possivelmente SSCI-específico**: nada óbvio. O `.result-toggle` em print pode precisar de regra própria (esconder os botões OK/NOK e mostrar só o valor activo), mas isso é domain — e se for um problema real, é tratado como ajuste localizado no SSCI source, não no print.css partilhado.

- [ ] **Step 2: Remove both @media print blocks from consolidated block 1**

Substituir por comment marker:

```css
/* @media print rules — MIGRATED to shared/styles/print/print.css (Plan 5 Task 15) */
```

- [ ] **Step 3: Build and smoke test print**

```bash
python scripts/build-all.py --only portal-ssci
```

Abrir o dist em Chrome, ir a Registo de Serviço, Ctrl+P (print preview). Verificar:
- [ ] Shell bar escondido
- [ ] Sidebar escondida
- [ ] Footer escondido
- [ ] Save badge, toasts, modals escondidos
- [ ] Todas as secções visíveis (não só a activa)
- [ ] Cards têm border 1px em vez de sombra
- [ ] Text pretos, fundo branco
- [ ] Se o spec `print.css` do Plan 4 introduziu print header institucional (logo + aeroporto + portal + data) repetido por página via `@page margin-top`, verificar que aparece. Se não aparece, NÃO é bloqueante — a decisão do Plan 4 foi validada separadamente.

Testar print preview em:
- Registo de Serviço (form-heavy)
- Inspecção Whisky 01 (check-table com result-toggle)
- Controlo de Estoque (stat-cards + table)

- [ ] **Step 4: Fix SSCI-specific print issues if any**

Se um teste de print revelar um problema SSCI-específico (ex: `.result-toggle` mostra botões OK/NOK em vez de só o valor activo), adicionar uma regra local no SSCI source dentro de um `<style>` ou como aditivo no `shared/styles/print/print.css` consoante a natureza do fix:

- Se a regra é genérica (qualquer portal com result-toggle), adicionar ao `shared/print.css` (com justificação na commit message).
- Se a regra é domain SSCI (só para result-toggle das VCI), adicionar regra local no SSCI source como `<style>` adicional antes do `</head>` ou no consolidated block 1.

Preferir a segunda opção por default — manter shared clean.

- [ ] **Step 5: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
# if print.css touched: git add shared/styles/print/print.css
git commit -m "refactor(ssci): consume shared print.css, remove legacy @media print from block 1"
```

---

## Task 16: Final integration — pytest + build + full visual smoke test

**Files:**
- Create: `tests/test_ssci_plan5.py` (optional but recommended)

- [ ] **Step 1: Write a small programmatic regression test for SSCI dist**

**Nota importante**: os assertions abaixo assumem class names `ds-shell-bar`, `ds-sidebar`, `ds-splash`, `ds-footer`. Se o Plan 4 usou naming diferente para o COE (ex: `shell-bar` sem prefixo, ou `app-header`), **actualizar os assertions** antes de correr para coincidir com o que Plan 4 committou. A fonte de verdade é o que está em `shared/styles/chrome/*.css`. Grep primeiro:

```bash
rtk grep -n '^\.[a-z-]*shell-bar\|^\.[a-z-]*sidebar\|^\.[a-z-]*splash\|^\.[a-z-]*footer' \
  shared/styles/chrome/
```

Ajustar os strings nos `assert ... in ssci_dist_html` abaixo conforme o output.

```python
# tests/test_ssci_plan5.py
"""Regression checks for Portal SSCI after Plan 5 (components + chrome migration)."""
from pathlib import Path
import re

import pytest


@pytest.fixture
def ssci_dist_html(repo_root: Path) -> str:
    dist = repo_root / 'packages' / 'portal-ssci' / 'dist' / 'Portal_PSCI_AWM.html'
    assert dist.exists(), f"SSCI dist not built: {dist}"
    return dist.read_text(encoding='utf-8')


def test_ssci_dist_consumes_ds_css(ssci_dist_html: str):
    """The DS CSS block must be present and non-trivial."""
    # DS style block inserted before the legacy <style>
    assert '<style>' in ssci_dist_html
    # Expect DS tokens to be resolved (no raw placeholder)
    assert '{{DS_CSS}}' not in ssci_dist_html
    # Expect density token data-attribute
    assert 'data-density="comfortable"' in ssci_dist_html


def test_ssci_dist_has_shell_bar(ssci_dist_html: str):
    """New chrome markup must be present."""
    assert 'ds-shell-bar' in ssci_dist_html
    assert 'ds-sidebar' in ssci_dist_html
    assert 'ds-splash' in ssci_dist_html
    assert 'ds-footer' in ssci_dist_html


def test_ssci_dist_no_occurrence_pill(ssci_dist_html: str):
    """SSCI has show_occurrence_pill=false — the pill element from Plan 4's
    shell bar must NOT appear anywhere in the SSCI dist. Plan 4 uses the
    class name .ds-shell-bar__emg-pill (verified in Plan 4 Task 11 Step
    11.2 line ~1888); Plan 5 Task 13a hard-codes its omission."""
    assert 'ds-shell-bar__emg-pill' not in ssci_dist_html
    assert 'dsEmgPill' not in ssci_dist_html


def test_ssci_dist_utc_clock_present(ssci_dist_html: str):
    """UTC clock element must be in the shell bar. Plan 5 Task 13a preserves
    Plan 4's element IDs verbatim (headerUTC, clockDisplay) so that
    shared/scripts/utilities/date-utc.js works out-of-the-box."""
    assert 'id="headerUTC"' in ssci_dist_html
    assert 'id="clockDisplay"' in ssci_dist_html


def test_ssci_dist_removed_legacy_chrome_css(ssci_dist_html: str):
    """Legacy chrome CSS must not exist in the consolidated block."""
    # Look for signature strings that only existed in the old chrome
    assert '.header { background: linear-gradient' not in ssci_dist_html
    # Legacy .nav-item CSS declaration shouldn't be in the body
    assert '.nav-item { display: block; padding: 0.5rem 1rem;' not in ssci_dist_html
    # Post Task 13a, no HTML element should still carry class="nav-item" —
    # all 17 sidebar buttons were renamed to class="nav-btn" to match the
    # Plan 4 JS contract.
    assert 'class="nav-item"' not in ssci_dist_html
    assert 'class="nav-item active"' not in ssci_dist_html


def test_ssci_dist_nav_btn_contract(ssci_dist_html: str):
    """Plan 5 Task 13a canonicalises .nav-btn (Plan 4 contract) across 17
    sidebar items. openSection() must accept (id, event) per Plan 4."""
    # At least 17 .nav-btn occurrences (sidebar items); Plan 5 dashboard
    # quick-access buttons remain .btn .btn-primary.
    assert ssci_dist_html.count('class="nav-btn"') + \
        ssci_dist_html.count('class="nav-btn active"') >= 17
    # 2-arg openSection signature — every onclick call in the new markup
    # ends with ", event)". There are 17 nav-btn + 4 dashboard buttons = 21.
    assert ssci_dist_html.count(", event)") >= 21


def test_ssci_dist_preserves_section_markup(ssci_dist_html: str):
    """All 17 nav-items and their sections must still exist (no content lost).
    Verified against the real SSCI source: 17 sidebar buttons across 6
    section groups (Painel 2 / Diários 6 / Operacionais 4 / Recursos 1 /
    Checklists 2 / Sistema 2)."""
    expected_sections = [
        'dashboard', 'mapas', 'reg-servico', 'insp-w01', 'insp-w02',
        'insp-resgate-w01', 'insp-resgate-w02', 'teste-comms',
        'avaria', 'combustivel', 'tempo-resp', 'presenca',
        'stock', 'checklist-coe', 'checklist-pcm',
        'ajuda', 'configuracoes',
    ]
    assert len(expected_sections) == 17  # sanity check on the list itself
    for sec_id in expected_sections:
        # Plan 5 uses 2-arg openSection('id', event) per Plan 4 contract.
        assert f"openSection('{sec_id}', event)" in ssci_dist_html, \
            f"Section '{sec_id}' not found in navigation (or still 1-arg)"
        assert f'id="{sec_id}"' in ssci_dist_html, \
            f"Section '{sec_id}' panel not in HTML body"


def test_ssci_dist_preserves_psci_cfg(ssci_dist_html: str):
    """Internal PSCI_CFG must still be present."""
    assert 'PSCI_CFG' in ssci_dist_html
    assert 'PSCI_DEFAULT_CFG' in ssci_dist_html
    assert 'psci_awm_config' in ssci_dist_html  # localStorage key
```

- [ ] **Step 2: Run full pytest suite**

```bash
python -m pytest tests/ -q
```

Expected: all previous tests still pass (Plan 1 + Plan 2 + Plan 3 + Plan 4 + **8 new Plan 5 tests**: `consumes_ds_css`, `has_shell_bar`, `no_occurrence_pill`, `utc_clock_present`, `removed_legacy_chrome_css`, `nav_btn_contract`, `preserves_section_markup`, `preserves_psci_cfg`).

- [ ] **Step 3: Run full build-all and check outputs**

```bash
python scripts/build-all.py
```

Expected:
- COE builds OK (zero impact from Plan 5)
- SSCI builds OK
- Both dist HTMLs present with sane sizes

- [ ] **Step 4: Manual full visual smoke test walkthrough**

Abrir `packages/portal-ssci/dist/Portal_PSCI_AWM.html` em Chrome. Percorrer secção a secção:

**Chrome:**
- [ ] Splash aparece ~1.5s e desaparece
- [ ] Shell bar: logo + Portal SSCI + OACI + breadcrumb + UTC clock + Local clock + Turno badge
- [ ] UTC clock actualiza a cada segundo em tabular-nums
- [ ] Sidebar light com 6 section groups e 17 nav-btn items
- [ ] Active `.nav-btn` tem border-left 3px em `--brand-primary`
- [ ] Nav item hover states suaves
- [ ] Footer institucional no fundo

**Dashboard:**
- [ ] Stat cards renderizam (Categoria SCI, CAT Actual, Viaturas, Efectivo, Comunicações)
- [ ] Páginas carregam default values de `PSCI_CFG`

**Formulários Diários:**
- [ ] **Registo de Serviço** — form-rows, form-groups, selects, textareas todos visualmente corretos
- [ ] **Inspecção Whisky 01** — check-table renderiza, result-toggle buttons OK/NOK/OP/NO/NA funcionam, section headers destacados
- [ ] **Inspecção Whisky 02** — idem
- [ ] **Eqp. Resgate W01/W02** — idem
- [ ] **Teste Comunicações** — form + table híbrida

**Formulários Operacionais:**
- [ ] **Avaria Equipamento** — forms
- [ ] **Abastecimento VCI** — forms + inputs numéricos
- [ ] **Tempo Resposta** — inputs type=time, auto-calc diferença (JS preservado)
- [ ] **Lista Presença** — table com 13 linhas iniciais

**Recursos:**
- [ ] **Controlo de Estoque** — stat-cards do stock, tabelas, export JSON button

**Checklists Mensais:**
- [ ] **CheckList COE** — tabela grande de checklist
- [ ] **CheckList PCM** — tabela PCM

**Sistema:**
- [ ] **Guia Rápido** — documentação HTML
- [ ] **Configurações** — 5 tabs (Efectivo, Viaturas, Equipamento, Contactos, Parâmetros), add/del rows, save button
- [ ] Editar uma linha → save badge aparece → guardar → toast success

**Persistência:**
- [ ] Recarregar a página → dados do `PSCI_CFG` ainda lá (lsGet/lsSet funcional)
- [ ] DevTools → Application → Local Storage → `psci_awm_config` presente

**Interactions:**
- [ ] `window.notify('test success', 'success')` via console → toast aparece
- [ ] `window.awmAlert('test error', 'error')` via console → modal aparece
- [ ] Esc fecha modal, click fora fecha modal, focus trap funciona

**Impressão:**
- [ ] Ctrl+P em Registo de Serviço — preview limpo, sem chrome, todas as secções visíveis, cards com border, fundo branco
- [ ] Ctrl+P em Inspecção Whisky 01 — print header institucional (se Plan 4 implementou), tabela legível

**Responsive:**
- [ ] Reduzir browser a 1024px → breadcrumb colapsa
- [ ] Reduzir a 768px → sidebar colapsa ou vira menu
- [ ] Reduzir a 520px → toasts e modal full-width

- [ ] **Step 5: Compare size deltas to baseline**

```bash
python << 'PYEOF'
import hashlib
from pathlib import Path

src = Path('packages/portal-ssci/dist/Portal_PSCI_AWM.html')
new_size = src.stat().st_size
new_sha = hashlib.sha256(src.read_bytes()).hexdigest()

baseline = Path('d:/tmp/plan5-baseline/ssci-pre-plan5.html')
base_size = baseline.stat().st_size

delta = new_size - base_size
print(f"SSCI pre-Plan5:  {base_size:>10} bytes")
print(f"SSCI post-Plan5: {new_size:>10} bytes")
print(f"Delta:           {delta:+>10} bytes")
print(f"New sha256: {new_sha}")
PYEOF
```

Expected delta (sanity check):
- Metade A remove ~8–12 KB de CSS legacy duplicado (button, badge, form, card, table, awm-modal, awm-toast, uxp-savebadge) — **redução**. Note: Task 7 `.separator` no-op doesn't contribute (regra fica local).
- Metade B adiciona markup HTML novo (shell bar + sidebar + splash + footer) — **aumento de ~2–4 KB** HTML.
- Chrome CSS não conta porque já vem do `{{DS_CSS}}` (inalterado em Plan 5).
- Likely delta: **−5 to −10 KB** total (SSCI fica mais pequeno porque reutiliza mais código partilhado).

Se o delta for positivo (SSCI fica maior sem razão óbvia), investigar.

- [ ] **Step 6: Commit final**

```bash
git add tests/test_ssci_plan5.py
git commit -m "test(ssci): add regression suite for Plan 5 (components + chrome)"
```

- [ ] **Step 7: Plan 5 complete — ready for PR or merge**

Abrir PR para `main` com título `feat(ssci): Plan 5 — components + chrome migration` e corpo a referir cada commit e a listar os screenshots pré/pós validados pelo utilizador. **Não** fazer merge sem revisão.

---

## Verification checklist (before marking Plan 5 as done)

- [ ] Task 0: Prerequisites verified (Plans 3+4 merged, shared files exist, worktree created, baseline captured)
- [ ] Task 1: awm-contacts decision recorded (SSCI não consome)
- [ ] Task 2: button.css consumed, legacy removed
- [ ] Task 3: badge.css consumed, `.form-card .badge` legacy removed
- [ ] Task 4: form-group.css consumed, legacy removed
- [ ] Task 5: card.css + stat-card.css consumed, legacy removed (with Opção A/B decision)
- [ ] Task 6: table.css base consumed, VCI domain refinements preserved
- [ ] Task 7: `.separator` — no-op (Plan 3 did not extract `divider.css`; rule stays local; no commit)
- [ ] Task 8: awm-modal.css consumed, legacy removed, smoke test passed
- [ ] Task 9: awm-toast.css consumed, legacy removed, `window.notify` still works
- [ ] Task 10: uxp-savebadge.css consumed, legacy removed, save badge functional (class name `.uxp-savebadge` preserved per Plan 3)
- [ ] Task 11: skeleton/empty-state — no legacy in SSCI, task no-op
- [ ] Task 12: tabs/dropdown — no legacy in SSCI, task no-op (psci-cfg-tab-btn inline deferred)
- [ ] Task 13a: New chrome markup added (shell bar, sidebar, splash, footer); `.ds-shell-bar__emg-pill` hard-coded omission; 17 sidebar buttons renamed to `.nav-btn`; 21 `openSection('x', event)` calls rewritten
- [ ] Task 13b: Legacy chrome CSS removed from block 1
- [ ] Task 13c: JS updated (`openSection(id, event)` 2-arg signature, `.nav-btn` query selector, UTC clock at 1s interval or wired to shared date-utc, splash fade-out)
- [ ] Task 13d: Visual smoke test passed and **user explicitly validated the new SSCI chrome**
- [ ] Task 14: `date-utc.js` consumption decided (Path A inline the shared file, or Path B keep Task 13c inline `updateClock`). No other shared JS modules exist in Plans 3/4 to consume.
- [ ] Task 15: print.css consumed, legacy `@media print` removed, print preview verified
- [ ] Task 16: pytest suite green (Plan 1 + 2 + 3 + 4 + 5 tests), full manual smoke test completed, size delta sane
- [ ] All commits are atomic and have clear Plan 5 Task N markers in messages
- [ ] `config/airport-fnmo.json` untouched
- [ ] `packages/portal-coe/**` untouched (zero impact on COE)
- [ ] `shared/**` untouched (except possibly `shared/styles/print/print.css` in Task 15 — only if SSCI-generic rule found missing)
- [ ] `packages/portal-ssci/portal.config.json` untouched
- [ ] `VERSION` untouched

---

## Rollback plan

Plan 5 vive inteiramente num worktree isolado `../Portal_DREA-ssci` no branch `feat/ssci-migration`. Cada task é um commit atómico. Rollback options, ordered from least to most destructive:

1. **Revert last task**: `git revert HEAD` — reverte o último commit. Útil se uma task individual quebrou algo que as tasks anteriores não quebraram. Commits ficam no histórico como "revert of X".

2. **Reset to previous task**: `git reset --hard HEAD~1` — apaga o último commit **do worktree apenas**. Só fazer se explicitamente pedido e se o commit ainda não foi pushed.

3. **Reset to start of Plan 5**: `git reset --hard $(git merge-base feat/ssci-migration main)` — volta ao estado anterior de todo o Plan 5. Main fica intocado.

4. **Delete the worktree entirely**: `git worktree remove ../Portal_DREA-ssci --force && git branch -D feat/ssci-migration`. Main permanece no estado post-Plan-4 (COE migrado, SSCI não). Seguro — zero impacto no COE.

**Garantia de isolamento:** desde que nenhum commit seja mergado para `main` sem aprovação do utilizador, o pior caso é perder o trabalho do worktree e recomeçar. O COE (Plans 3+4) não é afectado por nenhuma operação de rollback de Plan 5.

**Parcial rollback (recomendado por task group):**
- Se a Metade A (Tasks 2–12) estiver OK mas a Metade B (Task 13) falhar visualmente: `git reset --hard` para o commit imediatamente antes de Task 13a. Plan 5 fica entregue a 70% (só components) e a Metade B pode ser re-planejada.
- Se a Task 14 (JS wiring) partir alguma interacção: reverter só os commits da Task 14 (`git revert` em cadeia). O SSCI continua visualmente correcto e funcional, só a optimização de código partilhado fica pendente.

---

## Notes for the executor

1. **Este plano é deliberadamente mais curto que os Planos 3 e 4.** Isso é intencional. Se estás a pensar em copiar sections inteiras do Plan 3/4, **pára** — provavelmente estás a duplicar trabalho que já foi feito. O Plan 5 **não cria** componentes, **não cria** chrome CSS, **não cria** logo SVGs. Plano 5 só **consome** e **remove** legacy.

2. **Visual equivalence vs visual change**: Tasks 2–12 + 15 têm invariant de **equivalência visual** (o utilizador não deve notar diferença). Task 13 tem invariant de **mudança visual intencional** (o utilizador **deve** notar a diferença e confirmar que gosta). Não misturar os dois modos.

3. **Density flip**: SSCI usa `comfortable`. Não alterar nada para forçar essa densidade — o `data-density="comfortable"` no `<html>` já está lá (vem do `portal.config.json` via `{{PORTAL.DENSITY}}`) e os `shared/styles/tokens/density-comfortable.css` já estão injetados pelo Plan 1. Quando o `shared/styles/chrome/sidebar.css` diz `height: var(--nav-item-height)`, o valor resolve-se para 44px automaticamente no SSCI. Zero trabalho extra.

4. **Se um ficheiro shared não existe, PARA e reporta.** Não crias o ficheiro em Plan 5 — esse é trabalho de outro plano. Documenta a falha e espera.

5. **Screenshots são obrigatórios**. Pre e pós para o mesmo conjunto de secções, lado-a-lado, para o user visual validation na Task 13d.

6. **Commit messages seguem a convenção dos Planos 3+4**: `refactor(ssci): ...` para migração de componente, `feat(ssci): ...` para adições de chrome, `fix(ssci): ...` para ajustes pós-feedback, `test(ssci): ...` para tests. Todos com marcador `(Plan 5 Task N)` no corpo.

7. **O JS inline `window.notify`/`awmAlert`/`lsGet`/`escHtml` do SSCI permanece inline após Task 14** — Plans 3 e 4 **não extraem** nenhum destes helpers para `shared/scripts/`. Task 14 só cobre `date-utc.js` (o único utility JS que Plan 4 produz). A extracção dos outros é deferred para Plan 6 ou posterior. Isto é intencional, não um atraso.

8. **PDF export code paths são intocáveis** em Plan 5. As linhas 2540, 3400, 3410+ do SSCI source têm strings JavaScript com CSS dentro — `html += '.footer{...}'`, etc. **NÃO** as alterar, mesmo que o CSS dentro pareça duplicado com shared. Esses são used por export/print code paths completamente separados do render normal.

9. **`.result-toggle`, `#tr-occ-real-block`, stock counter, VCI inspection refinements — ficam no SSCI source como domain.** Não extrair para shared/. Não os remover. Continuam a consumir tokens DS quando referenciam `var(--dark-blue)`, etc.

10. **Se o Plan 4 tiver introduzido algum padrão de naming diferente do previsto aqui (ex: `shell-bar` sem `ds-` prefix)**, **usar o naming do Plan 4 exactamente**. Este plano é um guia; a fonte de verdade para naming é o que Plan 4 commitou. Consultar o COE source migrado sempre que há dúvida.
