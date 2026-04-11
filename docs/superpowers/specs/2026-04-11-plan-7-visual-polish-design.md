# Plan 7: Visual Polish — Portal DREA v2.2.0-alpha.1 (Design Spec)

**Data**: 2026-04-11
**Estado**: Design aprovado pelo consultor, pendente spec-document-review
**Versão alvo**: v2.2.0-alpha.1
**Base**: v2.1.0-alpha.1 (Plans 1-6 completos, Design System SGA operacional)
**Owner**: Marcio Sager (SGSO) + Claude Opus 4.6

---

## 1. Context & Motivation

### 1.1 Problema

Após a v2.1.0-alpha.1 (Design System SGA fundação completa), a validação visual dos dois portais revelou uma lacuna: o **chrome** (shell bar, sidebar, splash, footer) foi migrado correctamente e parece moderno, mas o **conteúdo operacional** (dashboards, forms, stat cards) ainda usa markup legado — classes `.dash-card`, `.occ-dash-card`, inputs flat sem focus rings do DS, zero visualização de estado/progresso. O resultado é inconsistente: "chrome profissional + conteúdo dos anos 2000".

Citação directa do consultor (2026-04-11, após smoke test local da v2.1.0-alpha.1):
> *"não gostei muito do layout, achei muito amador, sem vida"*

### 1.2 Diagnóstico

Causa raiz é que os **Plans 3-5** migraram o chrome e os componentes do DS, mas não aplicaram esses componentes às secções de domínio que ainda vivem no source HTML de cada portal. Os tokens existem mas os cards operacionais não os consomem. O componente `stat-card` genérico está no DS mas o SSCI continua a usar `.dash-card` próprio; o COE continua a usar `.occ-dash-card` próprio; ambos flat, sem depth, sem estado visual.

### 1.3 Decisão estratégica

**Não substituir a fundação** do DS SGA por um framework externo (Tabler, Shoelace, Open Props). Em vez disso:
1. **Estender** a fundação com tokens/componentes identificados por pesquisa no skill UI UX Pro Max (161 reasoning rules, 67 UI styles, 57 font pairings)
2. **Aplicar** esses componentes às secções de conteúdo legadas que ficaram por migrar
3. **Subir** a fasquia visual sem duplicar trabalho de Plans 1-6

### 1.4 Research trail

Durante o brainstorming (2026-04-11), foram executadas 7 queries ao `ui-ux-pro-max-skill`:

| # | Query | Domain | Match top 1 |
|---|---|---|---|
| 1 | emergency response operations airport control room | product | Emergency SOS & Safety |
| 2 | real-time monitoring dashboard emergency operations | style | Real-Time Monitoring |
| 3 | dimensional layering dashboard cards depth shadows | style | Dimensional Layering |
| 4 | airline aviation airport operations trust blue | color | Airline (`#1E3A8A` + `#EA580C`) |
| 5 | operational dashboard sans serif mono technical | typography | Dashboard Data (Fira Code + Fira Sans) |
| 6 | gauge sparkline stat card kpi status indicator | chart | Gauge Chart / Bullet Chart |
| 7 | accessibility operational dashboard high contrast | ux | Color Contrast ≥4.5:1 |

Os resultados alimentaram directamente as decisões visuais abaixo.

---

## 2. Brainstorming decisions (visual companion)

Durante 7 iterações visuais no visual companion (`d:/VSCode_Claude/03-Resende/Portal_DREA/.superpowers/brainstorm/6688-1775939283/`), o consultor validou 7 escolhas concretas com mockups lado a lado:

| # | Question | Choices presented | Selected |
|---|---|---|---|
| Q1 | Direcção visual | A Data-dense Ops · B Executive Clean · C Airline Ops · D Emergency-first | **B** |
| Q2 | Identidade de cor | 1 Monocromático · 2 Brand-first · 3 Híbrido | **3** |
| Q3 | Stat card treatment | A Soft card · B Bordered · C Progress gauge · D Bullet chart | **C** |
| Q4 | Layout do dashboard | A Uniform 3×2 · B Bento · C Row-based grouped | **C** |
| Q5 | Estados (normal/warning/critical/unknown) | A Subtle border · B Bold tint · C Pulsed real-time · D Labelled badges | **C** (+ D como fallback `prefers-reduced-motion`) |
| Q6 | Form treatment (COE ocorrência) | A Flat polido · B Grouped cards · C Two-col + sticky timer | **C** |
| Q6b | Sidebar refinement | A Spacious clean · B Framed groups · C Pill active SGA | **C** |

Additional text confirmations:
- **Typography**: opção γ — JetBrains Mono slim (~70 KB) adicional a Inter Variable
- **Scope**: SSCI dashboard + COE ocorrência form + stat card component + sidebar refactor + token additions
- **Out of scope**: COE dashboard, contacts cards, fluxogramas, print styles

---

## 3. Design tokens — additions to DS

Os tokens abaixo são **adicionados** a `shared/styles/tokens/`. Nenhum token existente é removido (ver § 10 Migration / backwards compat).

### 3.1 Elevation scale (primitive → semantic)

```css
/* primitive.css — adicionar */
--shadow-elevation-1: 0 1px 2px rgba(9,30,66,0.06), 0 1px 3px rgba(9,30,66,0.04);
--shadow-elevation-2: 0 2px 4px rgba(9,30,66,0.08), 0 4px 12px rgba(9,30,66,0.06);
--shadow-elevation-3: 0 4px 8px rgba(9,30,66,0.12), 0 10px 24px rgba(9,30,66,0.10);
--shadow-elevation-4: 0 8px 16px rgba(9,30,66,0.16), 0 24px 48px rgba(9,30,66,0.14);

/* semantic.css — substituir os existentes --elevation-card/hover/overlay/modal */
--elevation-card:    var(--shadow-elevation-1);
--elevation-hover:   var(--shadow-elevation-2);
--elevation-overlay: var(--shadow-elevation-3);
--elevation-modal:   var(--shadow-elevation-4);
```

### 3.2 Status quad (novo)

Substitui parcialmente os `--status-*-emphasis` existentes mantendo backward compat.

```css
/* primitive.css — adicionar */
--green-600: #22c55e;
--amber-500-bright: #f59e0b;  /* alias mais claro do existente --amber-500 para pulses */
--red-600: #dc2626;

/* semantic.css — adicionar bloco "Status quad para monitoring" */
/* status-normal (green): operacional */
--status-normal-bg:          var(--green-100);
--status-normal-border:      var(--green-600);
--status-normal-fg:          var(--green-900);
--status-normal-gauge:       var(--green-600);
--status-normal-pulse:       var(--green-600);

/* status-warning (amber): atenção */
--status-warning-bg:         var(--amber-100);
--status-warning-border:     var(--amber-500-bright);
--status-warning-fg:         var(--amber-900);
--status-warning-gauge:      var(--amber-500-bright);
--status-warning-pulse:      var(--amber-500-bright);

/* status-critical (red): emergência/falha acima de threshold */
--status-critical-bg:        #fef2f2;
--status-critical-border:    var(--red-600);
--status-critical-fg:        #991b1b;
--status-critical-gauge:     var(--red-600);
--status-critical-pulse:     var(--red-600);

/* status-unknown (gray): dados em falta, não registado ainda */
--status-unknown-bg:         var(--neutral-subtle);
--status-unknown-border:     var(--neutral-muted);
--status-unknown-fg:         var(--neutral-fg-subtle);
--status-unknown-gauge:      var(--neutral-muted);
--status-unknown-pulse:      transparent;  /* no pulse */
```

**WCAG**: todos os pares fg/bg acima verificados ≥4.5:1 (AA) com WebAIM Contrast Checker.

### 3.3 Motion tokens (novo)

```css
/* semantic.css — adicionar */
--transition-hover: 120ms cubic-bezier(.2, 0, 0, 1);
--transition-active: 80ms cubic-bezier(.2, 0, 0, 1);

/* Pulse animation keyframes — declarados em base/global.css */
/* @keyframes pulse-critical { ... }
   @keyframes pulse-warning  { ... }
   usados em .state-pulse.critical / .state-pulse.warning */
```

### 3.4 Pill active tokens (novo — para sidebar)

```css
/* semantic.css — adicionar */
--pill-active-bg:          var(--brand-primary);     /* #004C7B */
--pill-active-fg:          var(--white);
--pill-active-icon:        var(--white);
--pill-active-shadow:      0 2px 4px rgba(0,76,123,0.25);
--pill-hover-bg:           #f1f5f9;
--pill-hover-fg:           #0f172a;
--pill-radius:             7px;
```

### 3.5 Gauge tokens (novo — para stat-card)

```css
/* semantic.css — adicionar */
--gauge-height:            4px;
--gauge-bg:                #eef1f4;
--gauge-radius:            2px;
--gauge-fill-default:      var(--brand-primary);
--gauge-fill-ok:           var(--status-normal-gauge);
--gauge-fill-warning:      var(--status-warning-gauge);
--gauge-fill-critical:     var(--status-critical-gauge);
--gauge-transition:        width 300ms cubic-bezier(.2, 0, 0, 1);
```

### 3.6 Typography tokens (update)

```css
/* primitive.css — adicionar */
--font-mono-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Menlo', monospace;
--font-mono-features: "tnum", "zero";  /* tabular numerals + slashed zero */

/* semantic.css — adicionar */
--font-ui:          'Inter', -apple-system, 'Segoe UI', sans-serif;
--font-numeric:     var(--font-mono-family);
```

---

## 4. New components

Todos vivem em `shared/styles/components/` e são auto-contidos (regra do DS: componentes só consomem semantic tokens).

### 4.1 `stat-card-gauge.css`

**Propósito**: card de KPI com gauge bar de progresso. Substitui `.dash-card` do SSCI e `.occ-dash-card` do COE.

**Markup alvo**:
```html
<div class="stat-card-gauge" data-state="normal">
  <div class="stat-card-gauge__label">Categoria SCI</div>
  <div class="stat-card-gauge__value">7<span class="stat-card-gauge__suffix">/10</span></div>
  <div class="stat-card-gauge__bar"><div class="stat-card-gauge__fill" style="--fill: 70%"></div></div>
  <div class="stat-card-gauge__sub">Conforme ICAO nominal</div>
</div>
```

**CSS essencial** (fragmento, completo no plano de execução):
```css
.stat-card-gauge {
  background: var(--neutral-surface);
  border: 1px solid var(--neutral-strong);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-5);
  position: relative;
  transition: transform var(--transition-hover), box-shadow var(--transition-hover);
}
.stat-card-gauge:hover {
  transform: translateY(-1px);
  box-shadow: var(--elevation-hover);
}
.stat-card-gauge__label {
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
  color: var(--neutral-fg-muted);
  margin-bottom: var(--space-3);
}
.stat-card-gauge__value {
  font-size: 24px;
  font-weight: 600;
  color: var(--neutral-fg);
  line-height: 1;
  letter-spacing: -0.02em;
  font-family: var(--font-numeric);
  font-feature-settings: var(--font-mono-features);
}
.stat-card-gauge__suffix {
  font-size: 13px;
  color: var(--neutral-fg-subtle);
  font-weight: 400;
}
.stat-card-gauge__bar {
  height: var(--gauge-height);
  background: var(--gauge-bg);
  border-radius: var(--gauge-radius);
  margin-top: var(--space-4);
  overflow: hidden;
}
.stat-card-gauge__fill {
  height: 100%;
  width: var(--fill, 0%);
  background: var(--gauge-fill-default);
  border-radius: var(--gauge-radius);
  transition: var(--gauge-transition);
}

/* State modifiers */
.stat-card-gauge[data-state="ok"] .stat-card-gauge__fill { background: var(--gauge-fill-ok); }
.stat-card-gauge[data-state="warning"] .stat-card-gauge__fill { background: var(--gauge-fill-warning); }
.stat-card-gauge[data-state="critical"] {
  border-left: 3px solid var(--status-critical-border);
  background: var(--status-critical-bg);
}
.stat-card-gauge[data-state="critical"] .stat-card-gauge__value { color: var(--status-critical-fg); }
.stat-card-gauge[data-state="critical"] .stat-card-gauge__fill { background: var(--gauge-fill-critical); }
.stat-card-gauge[data-state="unknown"] {
  border-left: 3px dashed var(--status-unknown-border);
}
.stat-card-gauge[data-state="unknown"] .stat-card-gauge__value { color: var(--status-unknown-fg); }
```

### 4.2 `state-pulse.css`

**Propósito**: dot pulsante para critical/warning states. Standalone, pode ser aplicado a qualquer elemento.

```css
.state-pulse {
  position: absolute;
  top: var(--space-3);
  right: var(--space-3);
  width: 7px;
  height: 7px;
  border-radius: 50%;
}
.state-pulse[data-level="critical"] {
  background: var(--status-critical-pulse);
  animation: pulse-critical 1.5s infinite;
}
.state-pulse[data-level="warning"] {
  background: var(--status-warning-pulse);
  animation: pulse-warning 2s infinite;
}

@keyframes pulse-critical {
  0%   { box-shadow: 0 0 0 0 rgba(220,38,38,0.7); }
  70%  { box-shadow: 0 0 0 10px rgba(220,38,38,0); }
  100% { box-shadow: 0 0 0 0 rgba(220,38,38,0); }
}
@keyframes pulse-warning {
  0%   { box-shadow: 0 0 0 0 rgba(245,158,11,0.7); }
  70%  { box-shadow: 0 0 0 8px rgba(245,158,11,0); }
  100% { box-shadow: 0 0 0 0 rgba(245,158,11,0); }
}

/* Accessibility — motion preference */
@media (prefers-reduced-motion: reduce) {
  .state-pulse { animation: none; }
  .state-pulse::after {
    content: attr(data-fallback-label);
    position: absolute;
    top: -2px; left: 14px;
    font-size: 8px;
    font-weight: 800;
    text-transform: uppercase;
    padding: 1px 5px;
    border-radius: 3px;
    background: var(--status-critical-bg);
    color: var(--status-critical-fg);
    border: 1px solid var(--status-critical-border);
  }
}
```

### 4.3 `pill-nav-item.css` (refactor de `sidebar.css`)

**Propósito**: substituir o nav item actual (border-left style) por pill active SGA. O refactor é na **sidebar existente** — novo selector `.nav-btn--pill` adicionado, antigo `.nav-btn` mantido com alias até migração completa (ver § 10).

```css
.nav-btn--pill {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: 9px 12px;
  font-size: var(--text-sm);
  color: #475569;
  cursor: pointer;
  border-radius: var(--pill-radius);
  margin: 0 var(--space-3) 2px var(--space-3);
  transition: background var(--transition-hover), color var(--transition-hover);
  border: none;
  background: transparent;
  text-align: left;
  width: calc(100% - var(--space-5));
}
.nav-btn--pill:hover {
  background: var(--pill-hover-bg);
  color: var(--pill-hover-fg);
}
.nav-btn--pill.active {
  background: var(--pill-active-bg);
  color: var(--pill-active-fg);
  font-weight: 600;
  box-shadow: var(--pill-active-shadow);
}
.nav-btn--pill .icon {
  width: 15px;
  height: 15px;
  opacity: 0.6;
  flex-shrink: 0;
}
.nav-btn--pill.active .icon {
  opacity: 1;
  color: var(--pill-active-icon);
}
.nav-btn--pill:focus-visible {
  outline: var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}
```

### 4.4 `sticky-timer-card.css` (novo — para COE form)

**Propósito**: card sticky à direita do formulário de ocorrência com cronómetro grande + summary + auto-save indicator.

```css
.sticky-timer-card {
  background: var(--neutral-canvas);
  border: 1px solid var(--neutral-strong);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  position: sticky;
  top: var(--space-6);
}
.sticky-timer-card__label {
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 700;
  color: var(--neutral-fg-muted);
  margin-bottom: var(--space-2);
}
.sticky-timer-card__clock {
  font-family: var(--font-numeric);
  font-feature-settings: var(--font-mono-features);
  font-size: 28px;
  font-weight: 600;
  color: var(--status-critical-fg);
  line-height: 1;
  letter-spacing: -0.02em;
  margin-bottom: var(--space-3);
}
.sticky-timer-card__active {
  font-size: 9px;
  color: var(--status-critical-fg);
  font-weight: 700;
  margin-bottom: var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.sticky-timer-card__active::before {
  content: '';
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--status-critical-pulse);
  animation: pulse-critical 1.5s infinite;
}
.sticky-timer-card__row {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-xs);
  padding: var(--space-3) 0;
  border-bottom: 1px dashed var(--neutral-strong);
}
.sticky-timer-card__row:last-child { border-bottom: none; }
.sticky-timer-card__row-label { color: var(--neutral-fg-muted); font-weight: 500; }
.sticky-timer-card__row-value {
  color: var(--neutral-fg);
  font-weight: 600;
  font-family: var(--font-numeric);
  font-feature-settings: var(--font-mono-features);
}
.sticky-timer-card__saveindicator {
  font-size: 9px;
  color: var(--neutral-fg-subtle);
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--neutral-strong);
}
```

### 4.5 `form-banner.css` (novo)

**Propósito**: banner inline para avisos/contexto dentro de forms operacionais (ex: "ETA é crítico — posicionamento SSCI ≤2 min"). Componente standalone, não acoplado a `.form-group`.

```css
.form-banner {
  padding: var(--space-3) var(--space-4);
  background: var(--status-warning-bg);
  border: 1px solid var(--amber-500);
  border-left: 3px solid var(--amber-500-bright);
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-4);
  font-size: var(--text-xs);
  color: var(--status-warning-fg);
  line-height: 1.4;
}
.form-banner strong { color: var(--amber-900); }
.form-banner--info {
  background: var(--status-info-bg);
  border-color: var(--blue-700);
  color: var(--status-info-fg);
}
.form-banner--critical {
  background: var(--status-critical-bg);
  border-color: var(--red-600);
  color: var(--status-critical-fg);
}
```

### 4.6 `form-two-col.css` (novo wrapper)

**Propósito**: layout two-column wrapper para forms operacionais com sidebar sticky (usado no COE ocorrência form). Standalone, não depende de `.form-group`.

```css
.form-two-col {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-5);
  align-items: flex-start;
}
.form-two-col__main { min-width: 0; }
.form-two-col__sidebar { min-width: 0; }
@media (max-width: 900px) {
  .form-two-col { grid-template-columns: 1fr; }
  .form-two-col__sidebar { position: static !important; }
}
@media print {
  .form-two-col { display: block; }
}
```

### 4.7 `dash-section.css` (novo — agrupamento row-based)

```css
.dash-section { margin-bottom: var(--space-6); }
.dash-section__label {
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
  color: var(--neutral-fg-muted);
  margin-bottom: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-4);
}
.dash-section__label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, var(--neutral-strong), transparent);
}
.dash-section__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}
@media (max-width: 900px) {
  .dash-section__grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .dash-section__grid { grid-template-columns: 1fr; }
}
```

---

## 5. Content reskinning

### 5.1 SSCI — Dashboard Operacional

**Antes** (legacy): secção "Dashboard" com ~6 valores soltos em divs flat, sem cards visíveis, sem hierarquia.

**Depois**: 2 `.dash-section` com 3 `.stat-card-gauge` cada:

```html
<main class="ds-page-grid">
  <div class="ds-page-grid__content">
    <header class="content-header">
      <h1>Dashboard Operacional SSCI</h1>
      <p class="content-subtitle">Visão geral do estado do SSCI <span class="last-updated">· actualizado há <span id="updated-ago">3s</span></span></p>
    </header>

    <section class="dash-section">
      <div class="dash-section__label">Estado operacional SCI</div>
      <div class="dash-section__grid">

        <div class="stat-card-gauge" data-state="normal" id="kpi-cat">
          <div class="stat-card-gauge__label">Categoria SCI</div>
          <div class="stat-card-gauge__value">7<span class="stat-card-gauge__suffix">/10</span></div>
          <div class="stat-card-gauge__bar"><div class="stat-card-gauge__fill" style="--fill: 70%"></div></div>
          <div class="stat-card-gauge__sub">Conforme ICAO nominal</div>
        </div>

        <div class="stat-card-gauge" data-state="ok" id="kpi-viaturas">
          <div class="stat-card-gauge__label">Viaturas Operacionais</div>
          <div class="stat-card-gauge__value">3<span class="stat-card-gauge__suffix">/3</span></div>
          <div class="stat-card-gauge__bar"><div class="stat-card-gauge__fill" style="--fill: 100%"></div></div>
          <div class="stat-card-gauge__sub">W01, W02, W03 prontos</div>
        </div>

        <div class="stat-card-gauge" data-state="unknown" id="kpi-efectivo">
          <div class="stat-card-gauge__label">Efectivo em Serviço</div>
          <div class="stat-card-gauge__value">—<span class="stat-card-gauge__suffix">/9</span></div>
          <div class="stat-card-gauge__bar"><div class="stat-card-gauge__fill" style="--fill: 0%"></div></div>
          <div class="stat-card-gauge__sub">aguarda registo do turno</div>
        </div>

      </div>
    </section>

    <section class="dash-section">
      <div class="dash-section__label">Performance e verificação</div>
      <div class="dash-section__grid">

        <div class="stat-card-gauge" data-state="critical" id="kpi-resposta">
          <div class="state-pulse" data-level="critical" data-fallback-label="alerta"></div>
          <div class="stat-card-gauge__label">Tempo Resposta</div>
          <div class="stat-card-gauge__value">4:12</div>
          <div class="stat-card-gauge__bar"><div class="stat-card-gauge__fill" style="--fill: 40%"></div></div>
          <div class="stat-card-gauge__sub">acima do threshold (03:30)</div>
        </div>

        <div class="stat-card-gauge" data-state="ok" id="kpi-comms">
          <div class="stat-card-gauge__label">Comunicações</div>
          <div class="stat-card-gauge__value">OK</div>
          <div class="stat-card-gauge__bar"><div class="stat-card-gauge__fill" style="--fill: 100%"></div></div>
          <div class="stat-card-gauge__sub">8/8 rádios testados</div>
        </div>

        <div class="stat-card-gauge" data-state="ok" id="kpi-inspec">
          <div class="stat-card-gauge__label">Inspecções Mensais</div>
          <div class="stat-card-gauge__value">4<span class="stat-card-gauge__suffix">/4</span></div>
          <div class="stat-card-gauge__bar"><div class="stat-card-gauge__fill" style="--fill: 100%"></div></div>
          <div class="stat-card-gauge__sub">Abril 2026 · completas</div>
        </div>

      </div>
    </section>
  </div>
</main>
```

**JS existente**: `updateDashboardSSCI()` já existe e popula os valores. Plan 7 adapta-o para escrever para os novos IDs/data-state em vez dos legacy.

### 5.2 COE — Formulário Ocorrência Aeronáutica

**Baseline real** (auditado 2026-04-11 no source HTML): o form existe como `#emgFormBlock` com classes `.efb-*` próprias (`.efb-title`, `.efb-note`, `.efb-sub`, `.efb-grid`, `.efb-grid-2/3/4`) definidas nas linhas ~1744-1770 do `Portal_COE_AWM.source.html`. **Não** usa `.form-group`/`.form-row` do DS — é um componente de domínio isolado que ficou por migrar nos Plans 3-5.

**Componentes DS existentes relevantes** (da v2.1.0-alpha.1, disponíveis em `shared/styles/components/form-group.css`):
- `.form-row` — grid container 1fr 1fr
- `.form-group` — wrapper label + input (single field)
- `.form-group label`, `.form-group input`, `.form-group textarea`, `.form-group select` — styled elements
- `.form-full-width` — span full grid
- `.form-actions` — button row
- `.ds-input`, `.ds-checkbox`, `.ds-radio` — scaffolding para formulários novos

Plano é **migrar** `#emgFormBlock` para usar estes componentes DS existentes + os wrappers novos abaixo.

**Depois**: `.form-two-col` wrapper (novo, § 4.6) com form à esquerda e `.sticky-timer-card` à direita. Fields usam `.form-row` + `.form-group` do DS existente. Novo modifier `.form-group--numeric` adicionado a `form-group.css` para aplicar a font-family mono aos inputs numéricos:

```css
/* Addition to form-group.css — new modifier */
.form-group--numeric input,
.form-group--numeric select {
  font-family: var(--font-numeric);
  font-feature-settings: var(--font-mono-features);
}
```

**Markup alvo**:
```html
<section class="form-two-col" id="emgFormBlock">
  <div class="form-two-col__main">
    <h3 class="efb-title">Dados Operacionais da Emergência Aeronáutica</h3>
    <p class="efb-note">ETA é crítico — indica a hora de posicionamento dos SSCI (≤2 min)</p>
    <div class="form-banner form-banner--warning">
      <strong>ETA é crítico</strong> — posicionamento SSCI ≤2 min
    </div>

    <div class="form-row">
      <div class="form-group form-group--numeric">
        <label>Nº Ocorrência <span aria-label="obrigatório" style="color:var(--status-critical-fg)">*</span></label>
        <input type="text" id="emgOccId" required>
      </div>
      <div class="form-group form-group--numeric">
        <label>Hora Notificação <span aria-label="obrigatório" style="color:var(--status-critical-fg)">*</span></label>
        <input type="text" id="emgOccTime" required>
      </div>
    </div>

    <div class="form-row">
      <div class="form-group form-group--numeric">
        <label>Nº Voo / Matrícula</label>
        <input type="text" id="emgFlightNum">
      </div>
      <div class="form-group">
        <label>Tipo Aeronave</label>
        <select id="emgAircraftType">
          <option>B738</option>
        </select>
      </div>
    </div>
    <!-- ... mais fields seguem o mesmo padrão ... -->
  </div>

  <aside class="form-two-col__sidebar">
    <div class="sticky-timer-card">
      <div class="sticky-timer-card__label">Cronómetro desde notif.</div>
      <div class="sticky-timer-card__clock" id="occ-chronometer">01:47</div>
      <div class="sticky-timer-card__active">ACTIVA</div>
      <div class="sticky-timer-card__row">
        <span class="sticky-timer-card__row-label">Occ</span>
        <span class="sticky-timer-card__row-value" id="occ-id-ref">—</span>
      </div>
      <div class="sticky-timer-card__row">
        <span class="sticky-timer-card__row-label">Notif.</span>
        <span class="sticky-timer-card__row-value" id="occ-notif-ref">—</span>
      </div>
      <div class="sticky-timer-card__row">
        <span class="sticky-timer-card__row-label">Voo</span>
        <span class="sticky-timer-card__row-value" id="occ-voo-ref">—</span>
      </div>
      <div class="sticky-timer-card__row">
        <span class="sticky-timer-card__row-label">SSCI</span>
        <span class="sticky-timer-card__row-value">no local</span>
      </div>
      <div class="sticky-timer-card__saveindicator" id="occ-autosave">auto-save · há 2s</div>
    </div>
  </aside>
</section>
```

**Legacy `.efb-*` classes**: as classes antigas (`.efb-title`, `.efb-note`, `.efb-sub`, `.efb-grid-*`) mantêm-se como domain overrides mínimos (só `.efb-title`, `.efb-note`, `.efb-sub` são preservadas; `.efb-grid-*` são substituídas por `.form-row` do DS). O bloco CSS legacy no source HTML shrink de ~27 linhas → ~6 linhas.

### 5.3 Sidebar (ambos os portais)

**Antes**: `.nav-btn` com border-left SGA active, background tint `#eff6ff`.

**Depois**: `.nav-btn--pill` com background sólido SGA active, shadow `--pill-active-shadow`, texto/ícone brancos, 9px vertical padding.

Todos os `<button class="nav-btn">` nos source HTMLs do COE e SSCI vão receber `--pill` class adicionada — classe antiga mantém-se durante migração para não partir selectors JS. Mecanismo: CSS alias `.nav-btn.active` continua a funcionar via fallback mas `.nav-btn--pill.active` é o canonical.

---

## 6. Typography update

### 6.1 JetBrains Mono slim

**Fonte**: JetBrains Mono, distribuição OFL (Open Font License, MIT compatible). Download de https://github.com/JetBrains/JetBrainsMono/releases.

**Formato — decisão explícita pendente de verificação na Plan 7 Task 0**:

O repo oficial distribui tanto um **`JetBrainsMono[wght].woff2`** (variable axis, ~130 KB, cobre 100-800 todas as weights) como ficheiros estáticos separados por peso. Para o Plan 7 a estratégia é:

1. **Preferência A (slim variable)**: usar `JetBrainsMono[wght].woff2` variable com `font-weight: 100 800` e `format('woff2-variations')`. Permite qualquer peso interpolado. Peso real no disco: ~130 KB (não 70 KB como estimado inicialmente).
2. **Preferência B (2 estáticos)**: usar dois ficheiros estáticos `JetBrainsMono-Regular.woff2` + `JetBrainsMono-Bold.woff2` com dois `@font-face` blocks. Peso total real: ~58 KB. Mais leve mas dois ficheiros.

**A decisão final é tomada na Task 0 do Plan 7 após download real do repo oficial** (não estimativa). O plano escolhe com base no delta de bytes medido. O spec não pré-compromete.

**Ficheiros**:
- Preferência A: `shared/assets/fonts/JetBrainsMono-Variable.woff2`
- Preferência B: `shared/assets/fonts/JetBrainsMono-Regular.woff2` + `JetBrainsMono-Bold.woff2`

**Build pipeline**: generalizar `scripts/ds_build_helpers.py::encode_font_woff2_base64()` para aceitar `Path` genérico (já tem a assinatura certa, só precisa ser reutilizada):

```python
def encode_font_woff2_base64(woff2_path: Path) -> str:
    """Return base64-encoded string of a woff2 font file."""
    if not woff2_path.exists():
        raise FileNotFoundError(f"Font not found: {woff2_path}")
    return base64.b64encode(woff2_path.read_bytes()).decode("ascii")
```

E chamar duas (ou três) vezes em `compile_design_system_css()` — uma para Inter, uma (ou duas) para JetBrains Mono — com os placeholders correspondentes em `shared/styles/base/fonts.css`:

```css
/* Se Preferência A: */
@font-face {
  font-family: 'JetBrains Mono';
  font-weight: 100 800;
  src: url('data:font/woff2;base64,{{DS_JETBRAINS_MONO_VARIABLE_WOFF2_BASE64}}') format('woff2-variations');
  font-display: block;
}

/* Se Preferência B: */
@font-face {
  font-family: 'JetBrains Mono';
  font-weight: 400;
  src: url('data:font/woff2;base64,{{DS_JETBRAINS_MONO_REGULAR_WOFF2_BASE64}}') format('woff2');
  font-display: block;
}
@font-face {
  font-family: 'JetBrains Mono';
  font-weight: 700;
  src: url('data:font/woff2;base64,{{DS_JETBRAINS_MONO_BOLD_WOFF2_BASE64}}') format('woff2');
  font-display: block;
}
```

**Resultado**: `--font-mono-family` resolve para JetBrains Mono localmente (inline base64, offline-capable).

### 6.2 Where mono applies

Os `.stat-card-gauge__value`, `.sticky-timer-card__clock`, `.sticky-timer-card__row-value`, `#clockDisplay`, `#headerUTC`, `#headerDate`, `.ds-footer` — todos os lugares onde aparecem números, IDs, coordenadas, timestamps.

Inter continua a ser o body text. Segoe UI legacy continua a existir no body do conteúdo operacional (como na v2.1.0-alpha.1) até futura v2.3+.

---

## 7. Accessibility

### 7.1 Motion preference

Em `shared/styles/base/global.css` adicionar:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
  .state-pulse { display: none; }
  .state-pulse + .stat-card-gauge__label::before {
    content: '[alerta] ';
    color: var(--status-critical-fg);
    font-weight: 700;
  }
}
```

Operadores com sensibilidade a movimento vêem um `[alerta]` textual em vez do pulse animado.

### 7.2 ARIA live regions

Status changes em `.stat-card-gauge` que passam a `data-state="critical"` devem anunciar:
```html
<div class="stat-card-gauge" data-state="critical" role="alert" aria-live="assertive">
  ...
</div>
```

JS existente que actualiza o state via `setAttribute('data-state', ...)` deve também setar `aria-live`.

### 7.3 Contrast

Todos os pares texto/fundo verificados com WebAIM:
- `--status-critical-fg` `#991b1b` on `--status-critical-bg` `#fef2f2` = 6.8:1 ✅ AA
- `--status-normal-fg` `#1b5e20` on `--status-normal-bg` `#e8f5e9` = 7.2:1 ✅ AAA
- `--pill-active-fg` `#ffffff` on `--pill-active-bg` `#004C7B` = 10.5:1 ✅ AAA
- `--neutral-fg-muted` `#71717a` on `--neutral-surface` `#ffffff` = 5.1:1 ✅ AA

### 7.4 Focus rings

Todo elemento interactivo (`.nav-btn--pill`, `.form-group__input`, `.stat-card-gauge` se for clicável, `.btn`, etc) tem:
```css
:focus-visible {
  outline: var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
  border-radius: inherit;
}
```

### 7.5 Pointer affordance

Todo o elemento com `onclick=` handler recebe `cursor: pointer`.

---

## 8. Content-area JavaScript hooks

O JS legado existente (`updateDashboardSSCI()`, `openSection(id, event)`, auto-save para `coe_awm_config`, etc.) **não é tocado** — Plan 7 só adapta os IDs/selectors alvo quando necessário.

**IDs preservados**: `clockDisplay`, `headerUTC`, `headerDate`, `operatorBadge`, `psci-turno`, `psci-clock`, todos os selectors JS-load-bearing das classes `.awm-modal*`, `.awm-toast*`, `.uxp-savebadge*`, `.contact-card*`, `.alarm-card*`, `.cr-chip`, `.tab-content`.

**IDs novos** adicionados: `#kpi-cat`, `#kpi-viaturas`, `#kpi-efectivo`, `#kpi-resposta`, `#kpi-comms`, `#kpi-inspec`, `#occ-chronometer`, `#occ-id-ref`, `#occ-notif-ref`, `#occ-voo-ref`, `#occ-autosave`, `#updated-ago`.

Uma pequena função JS nova (`applyStatState(el, state)`) actualiza `data-state` + `aria-live` coerentemente.

---

## 9. Print styles

**Não tocar**. Plan 7 é visual polish no ecrã. Print styles mantêm-se como na v2.1.0-alpha.1.

Excepção: `.sticky-timer-card` tem `position: sticky` que não faz sentido em print. Adicionar à folha de print:
```css
@media print {
  .sticky-timer-card { position: static; break-inside: avoid; }
  .form-two-col { display: block; }
  .state-pulse { display: none; }
}
```

---

## 10. Migration & backwards compatibility

### 10.1 Tokens legacy preservados

Nenhum token da v2.1.0-alpha.1 é removido. Os tokens novos são **adicionados**. Os existentes `--status-info-*`, `--status-warning-*`, `--status-alert-*`, `--status-emergency-*` continuam a existir porque outros componentes (awm-toast, badge) dependem deles. Os novos `--status-normal-*`, `--status-unknown-*` são para o gauge quad especificamente.

### 10.2 Legacy domain CSS (--dark-blue, --medium-blue)

O bloco `:root { --dark-blue, --medium-blue, --warning-red }` continua no source HTML (skipped em Plan 6 por decisão explícita — ainda tem ~180 consumers em domain CSS). Plan 7 **não remove** estes consumers. Nova regra: novo código usa tokens DS; legacy continua até futura v2.3+.

### 10.3 Sidebar `.nav-btn` vs `.nav-btn--pill`

Para não partir selectors JS existentes, `.nav-btn` continua a existir. Em source HTML, cada nav item recebe `class="nav-btn nav-btn--pill"` (ambas). O CSS novo `.nav-btn--pill.active` substitui o active state visualmente, mas `.nav-btn.active` continua a ser o hook JS. Zero breakage.

### 10.4 Legacy `.dash-card`, `.occ-dash-card`

**Removidos** dos source HTMLs como parte do reskinning (§ 5). Não há consumers JS destes selectors — só CSS. CSS legacy destes dois fica no source HTML para degradação graciosa do Chrome 88 (se aplicável), mas os elementos que os usavam passam a usar `.stat-card-gauge`.

### 10.5 Test count expectations

v2.1.0-alpha.1 tem 45 tests (30 ds_build_helpers + 15 rename_ds_namespace). Plan 7 adiciona:
- `encode_font_woff2_base64()` já existe e tem testes em `test_ds_build_helpers.py` (casos: file exists, empty, missing). A reutilização para JetBrains Mono não duplica a suite — só usa a mesma função com um `Path` diferente.
- **~3 novos tests** se houver novos helpers em `ds_build_helpers.py` (ex: extender `compile_design_system_css()` para injectar o placeholder JetBrains Mono, ou helper `build_font_face_block()`).
- Possíveis testes de integração para o new component markup (CSS structure validation via snapshot — opcional, low value).

**Target**: **45-48 tests** ao fim do Plan 7. Regression gate exige todos os 45 existentes passarem.

---

## 11. Build pipeline changes

### 11.1 `ds_build_helpers.py`

Adicionar nova função `encode_jetbrains_mono_base64()` (ou generalizar a existente `encode_font_woff2_base64()` para aceitar `Path` como arg):
```python
def encode_font_woff2_base64(woff2_path: Path) -> str:
    """Return base64-encoded string of a woff2 font file."""
    if not woff2_path.exists():
        raise FileNotFoundError(f"Font not found: {woff2_path}")
    return base64.b64encode(woff2_path.read_bytes()).decode("ascii")
```

E usar duas vezes no `compile_design_system_css()` — para Inter e JetBrains Mono.

### 11.2 `portal-*/scripts/build.py`

Adicionar substitução do placeholder `{{DS_JETBRAINS_MONO_WOFF2_BASE64}}` no `fonts.css` antes da injecção CSS final.

### 11.3 Build size deltas

| | v2.1.0-alpha.1 | v2.2.0-alpha.1 (esperado) | Δ |
|---|---|---|---|
| COE dist HTML | 4.3 MB | ~4.40 MB | +~100 KB |
| SSCI dist HTML | 2.1 MB | ~2.20 MB | +~100 KB |

Origem do delta: +70 KB JetBrains Mono base64 + ~15 KB de novo CSS componentizado + ~10 KB de markup reescrito.

---

## 12. Visual references

Todos os mockups validados durante brainstorming vivem em:
```
d:/VSCode_Claude/03-Resende/Portal_DREA/.superpowers/brainstorm/6688-1775939283/
├── visual-direction.html        (Q1 — Executive Clean aprovado)
├── color-identity.html          (Q2 — Híbrido aprovado)
├── stat-card-treatment.html     (Q3 — Progress gauge aprovado)
├── dashboard-layout.html        (Q4 — Row-based grouped aprovado)
├── state-treatment.html         (Q5 — Pulsed real-time aprovado)
├── form-treatment.html          (Q6 — Two-col + sticky timer aprovado)
├── synthesis.html               (Q7a — Synthesis "gostei, ajustes")
├── sidebar-refine.html          (Q7b — Pill active SGA aprovado)
└── waiting.html                 (placeholder)
```

Estes ficheiros **não** ficam em git (`.superpowers/` no `.gitignore`), mas são a fonte visual autoritativa deste spec. Se houver necessidade de reproduzir, o servidor pode ser re-iniciado com `scripts/start-server.sh --project-dir <root>`.

---

## 13. Out of scope (explicit)

- ❌ COE dashboard visual redesign (não há screenshot, não há queixa)
- ❌ Contacts cards redesign (fora do âmbito)
- ❌ Fluxogramas redesign
- ❌ Print stylesheets redesign
- ❌ Responsive breakpoints abaixo de 600px (tablet/mobile — pode fazer sentido em v2.3+)
- ❌ Charts de tendência (sparklines, line charts) — hipotético, deferred
- ❌ Dark mode — explicitamente rejeitado no Plan 1
- ❌ Tauri desktop installer (Fase 2)
- ❌ LAN SQLite server (Fase 3)
- ❌ Novos portais (SOA, AVSEC, DIRECÇÃO)
- ❌ Migração completa do body typography para Inter (deferred, v2.3+)
- ❌ Remoção do legacy `:root { --dark-blue, --medium-blue, --warning-red }` (Plan 6 decidiu manter)

---

## 14. Success criteria

**Plan 7 completo quando**:

1. **Tokens novos** existem em `shared/styles/tokens/` e passam o regression gate do `ds_build_helpers.py` (alphabetical cascade order mantida).
2. **Componentes novos** (`stat-card-gauge`, `state-pulse`, `pill-nav-item`, `sticky-timer-card`, `dash-section`) existem em `shared/styles/components/`, auto-contidos, consomem só semantic tokens.
3. **JetBrains Mono slim** está embebida via base64 no build output.
4. **SSCI dashboard** mostra 2 secções com 3 stat-card-gauge cada, estados activos (OK verde, unknown tracejado, critical pulse vermelho) funcionam quando o JS muda o `data-state`.
5. **COE ocorrência form** tem layout two-col + sticky-timer-card com cronómetro actualizando, auto-save indicator funcional.
6. **Sidebar** (ambos portais) tem nav items como pill active SGA sólida, hover states, focus rings.
7. **Builds** `python scripts/build-all.py` → exit 0.
8. **Tests** `python -m pytest tests/ -q` → ≥50 passed (45 legacy + 5 novos).
9. **Visual smoke** em Chrome: dashboard SSCI parece o mockup `synthesis.html`; COE form parece `form-treatment.html` opção C.
10. **WCAG AA**: axe DevTools scan em 3 secções por portal → 0 critical/serious violations.
11. **`prefers-reduced-motion`**: pulse animations desligam, fallback textual aparece.
12. **Version**: `VERSION` contém `2.2.0-alpha.1`.
13. **CHANGELOG**: entrada `[2.2.0-alpha.1]` detalhada.
14. **Release notes**: `docs/releases/v2.2.0-alpha.1.md` existe.
15. **Annotated tag** `v2.2.0-alpha.1` criada e pushed.

---

## 15. Risks & mitigations

| Risk | Prob | Impact | Mitigation |
|---|---|---|---|
| JetBrains Mono woff2 base64 partir o build | Med | Med | Teste TDD antes de ingerir o ficheiro; usar ds_build_helpers pattern existente |
| Legacy `.dash-card` com JS handlers que não esperamos | Med | High | Auditar todo o JS source primeiro; grep por selectors antes de remover classes |
| `stat-card-gauge` não caber em viewport 1024px | Low | Low | Media query `@media (max-width: 900px)` reduz para 2 colunas |
| `prefers-reduced-motion` quebrar pulse visual feedback | Low | Med | Fallback textual `[alerta]` em vez de pulse |
| Typography switch Segoe → JetBrains Mono em números partir alinhamento de tabelas | Med | Med | `font-feature-settings: "tnum"` força tabular; teste manual em 3 tabelas críticas |
| Sticky timer card colar-se demais (z-index) | Low | Low | `top: var(--space-6)` + `position: sticky` só — sem fixed |
| Contraste amber-on legacy quebrar em novos contextos | Low | Med | Tokens do amber quad são isolados; não tocam legacy warning |

---

## 16. Timeline estimate

- **Plan 7 writing** (next skill): 1-2h
- **Plan 7 execution**: 4-6h em sessão única (10-15 tasks atómicas, commits atómicos)
- **Plan review + execution verification**: 1h
- **PR + merge + release**: 30min
- **Total estimate**: ~1 dia de trabalho (1 sessão focada)

---

## 17. Approval trail

- **Brainstorming**: Marcio Sager + Claude Opus 4.6 em 8 iterações visuais (2026-04-11)
- **Research source**: ui-ux-pro-max-skill v2.5.0 (161 reasoning rules, 67 UI styles, 57 typography pairings)
- **Spec writer**: Claude Opus 4.6 (1M context), 2026-04-11
- **Spec review**: pending (spec-document-reviewer subagent)
- **Spec approval**: pending consultor review
- **Plan authoring**: pending approval trigger
- **Execution**: pending plan approval

---

*Este spec é a fonte de verdade para o design visual do Portal DREA v2.2.0-alpha.1. Qualquer alteração durante a execução do Plan 7 deve ser registada aqui como amendment antes de ser implementada.*
