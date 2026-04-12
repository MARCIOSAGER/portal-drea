# Design System SGA — Guia do Consumidor

**Versão**: v2.2.0-alpha.1
**Escopo**: Portal DREA (monorepo COE + SSCI, futuros SOA, AVSEC, DIRECÇÃO)
**Audiência**: programadores que consomem o DS, agentes a portar o DS a novos portais, mantenedores.

Para o rationale original (porque foram tomadas as decisões), ver a spec canónica:
[`docs/superpowers/specs/2026-04-11-design-system-sga-design.md`](superpowers/specs/2026-04-11-design-system-sga-design.md).

Este documento é o **guia operacional**: o que usar, como usar, onde está, e como estender.

---

## 1. Introdução

O Design System SGA é a fundação visual partilhada dos portais DREA. Unifica:

- **Cores** alinhadas à identidade institucional SGA (`#004C7B` brand primary + paleta complementar)
- **Tipografia** baseada em Inter Variable (embebida em base64 no HTML final)
- **Espaçamento** variável por densidade de portal (compact para COE, comfortable para SSCI)
- **Componentes** (~19 blocos reutilizáveis: button, badge, card, form-group, table, tabs, stat-card-gauge, ...)
- **Chrome** (shell bar, sidebar, splash, footer, página-grid) idêntico para todos os portais
- **Ícones** via sprite SVG inline (40+ ícones Heroicons adaptados)
- **Impressão** (CSS `@media print` + `@page` Paged Media)

O DS nasceu na v2.1.0-alpha.1, substituindo uma base visual legada onde COE era dark-themed e SSCI claro, com ~8 KB de CSS duplicado por portal e 3 logótipos diferentes. Após a migração:

- **Uma** fundação visual, dois portais consistentes
- **Zero** CSS duplicado entre portais
- **Um** workflow para adicionar componentes ou portais novos

### Quando usar este guia

- **Contribuir para um portal existente**: secções 3, 5, 6, 7 (tokens, componentes, chrome, ícones)
- **Adicionar um componente novo**: secção 5 + governance do [`shared/styles/README.md`](../shared/styles/README.md)
- **Adicionar um portal novo** (Portal SOA, AVSEC, DIRECÇÃO): secção 9
- **Debugging de rendering**: secção 11 (FAQ)

---

## 2. Arquitectura em 3 camadas

```
┌──────────────────────────────────────────────┐
│  Layer 3: Components                         │  ← componentes (button, card, ...)
│  shared/styles/components/*.css              │     NUNCA referenciam primitives
├──────────────────────────────────────────────┤
│  Layer 2: Semantic tokens                    │  ← aliases com significado
│  shared/styles/tokens/semantic.css           │     (--brand-primary, --status-info-bg, ...)
├──────────────────────────────────────────────┤
│  Layer 1: Primitives                         │  ← valores crús
│  shared/styles/tokens/primitive.css          │     (--blue-800, --gray-100, --text-md, ...)
└──────────────────────────────────────────────┘
```

**Regra de ouro**: *Componentes só consomem semantic. Primitives são opacas.*

### Porquê 3 camadas?

- **Primitives** são valores absolutos — cores exactas, rádios, sombras. São estáveis e raramente mudam.
- **Semantic** dá significado a primitives. `--brand-primary: var(--blue-800)` diz "a marca é blue-800". Se algum dia a SGA decidir que o brand muda para um azul diferente, mudamos apenas esta linha.
- **Components** referenciam semantic. Um `<button class="btn-primary">` usa `var(--brand-primary)`, não `var(--blue-800)` directo. Isto significa que um rebrand é uma edição de 1 linha, não uma busca-e-substitui em 13 ficheiros.

### Cascade order (determinística)

O build concatena os ficheiros CSS nesta ordem (crítica):

1. `tokens/primitive.css`
2. `tokens/semantic.css`
3. `tokens/density-compact.css` **OR** `tokens/density-comfortable.css` (escolhido pelo build)
4. `base/*.css` (alfabética: `fonts.css`, `global.css`, `reset.css`, `typography.css`)
5. `chrome/*.css` (alfabética: `footer.css`, `page-grid.css`, `shell-bar.css`, `sidebar.css`, `splash.css`)
6. `components/*.css` (alfabética: `awm-modal.css`, `awm-toast.css`, `badge.css`, `button.css`, ...)
7. `print/print.css`

A ordem está implementada em [`scripts/ds_build_helpers.py::compile_design_system_css`](../scripts/ds_build_helpers.py). Não alterar sem actualizar os testes em `tests/test_ds_build_helpers.py`.

---

## 3. Catálogo de tokens

**Fonte de verdade**: [`shared/styles/tokens/primitive.css`](../shared/styles/tokens/primitive.css) + [`shared/styles/tokens/semantic.css`](../shared/styles/tokens/semantic.css).

Abaixo está um resumo agrupado. Para os valores exactos, ler os ficheiros fonte.

### 3.1 Neutros (chrome)

| Primitive      | Hex       | Semantic             | Uso                     |
|----------------|-----------|----------------------|-------------------------|
| `--gray-50`    | `#f6f8fa` | `--neutral-canvas`   | body background         |
| `--gray-100`   | `#eef2f7` | `--neutral-subtle`   | hover, divider          |
| `--gray-200`   | `#e1e5eb` | `--neutral-muted`    | borders default         |
| `--gray-300`   | `#d1d7e0` | `--neutral-strong`   | borders emphasis        |
| `--gray-400`   | `#8b95a1` | `--neutral-fg-subtle`| texto large only        |
| `--gray-500`   | `#57606a` | `--neutral-fg-muted` | texto secundário        |
| `--gray-800`   | `#24292f` | `--neutral-fg`       | texto principal         |
| `--white`      | `#ffffff` | `--neutral-surface`  | cards, inputs           |

### 3.2 Brand SGA

| Primitive      | Hex       | Semantic                | Contraste vs white |
|----------------|-----------|-------------------------|--------------------|
| `--blue-900`   | `#003a5e` | `--brand-primary-hover` | 11.89:1 (AAA)      |
| `--blue-800`   | `#004C7B` | `--brand-primary`       | 9.05:1  (AAA)      |
| `--blue-700`   | `#0073a0` | `--brand-secondary-text`| 5.30:1  (AA)       |
| `--blue-600`   | `#0094CF` | `--brand-secondary-fill`| 3.42:1 (fill only!)|
| `--blue-500`   | `#38C7F4` | `--brand-accent`        | decorative         |

**Atenção**: `--brand-secondary-fill` (`#0094CF`) **falha WCAG AA como cor de texto**. Usar apenas como preenchimento de elementos não-textuais (borders, shapes). Para texto azul médio, usar `--brand-secondary-text` (`#0073a0`).

### 3.3 Status semânticos (info / success / warning / alert / emergency)

Cada status tem 5 slots: `-bg`, `-border`, `-fg`, `-emphasis`, `-on-emphasis`. Exemplo:

```css
.status-box--warning {
  background: var(--status-warning-bg);      /* bg subtle para a caixa */
  border-left: 4px solid var(--status-warning-border);
  color: var(--status-warning-fg);           /* texto sobre bg */
}
.status-box--warning .badge {
  background: var(--status-warning-emphasis);/* fill forte */
  color: var(--status-warning-on-emphasis);  /* texto sobre emphasis */
}
```

| Status     | bg         | border/emphasis | fg       | on-emphasis |
|------------|------------|-----------------|----------|-------------|
| info       | `#e6f4fb`  | `#0073a0`       | `#003a5e`| `#ffffff`   |
| success    | `#e8f5e9`  | `#2e7d32`       | `#1b5e20`| `#ffffff`   |
| warning    | `#fef5e7`  | `#f39c12`       | `#8a5a00`| `#1a1200` ⚠ |
| alert      | `#fdecea`  | `#c62828`       | `#b71c1c`| `#ffffff`   |
| emergency  | `#ffcdd2`  | `#8b0000`       | `#8b0000`| `#ffffff`   |

**⚠ Cuidado warning `on-emphasis`**: tem de ser **escuro** (`#1a1200`), não branco. Amber claro sobre branco falha WCAG. Isto está documentado em `semantic.css` com comentário explícito.

### 3.4 Category accents (taxonomia de contactos)

Estes tokens dão identidade visual a categorias de contactos. Permanecem dos portais legados.

| Semantic              | Primitive        | Categoria                  |
|-----------------------|------------------|----------------------------|
| `--cat-avsec-bombeiros`| `var(--red-700)`| AVSEC e bombeiros          |
| `--cat-sga-interna`   | `var(--blue-800)`| SGA interno                |
| `--cat-enna-navegacao`| `var(--blue-600)`| ENNA / navegação aérea     |
| `--cat-seg-ordem`     | `var(--brown-700)`| Forças de segurança       |
| `--cat-externa-emg`   | `var(--purple-800)`| Emergência externa       |
| `--cat-operadores`    | `var(--slate-600)`| Operadores do aeroporto   |

### 3.5 Elevation (shadows)

| Semantic            | Primitive     | Uso                  |
|---------------------|---------------|----------------------|
| `--elevation-card`  | `--shadow-1`  | cards estáticos      |
| `--elevation-hover` | `--shadow-2`  | cards em hover       |
| `--elevation-overlay`| `--shadow-3` | dropdowns, tooltips  |
| `--elevation-modal` | `--shadow-4`  | modals                |

### 3.6 Radii, motion, focus

- `--radius-sm: 3px`, `--radius-md: 6px`, `--radius-lg: 8px`, `--radius-pill: 9999px`
- `--transition-fast: 120ms`, `--transition-base: 200ms`, `--transition-slow: 320ms` (todos com `cubic-bezier(.2, 0, 0, 1)`)
- `--focus-ring-color: var(--blue-700)`, `--focus-ring-width: 2px`, `--focus-ring-offset: 2px`

### 3.7 Type scale (Major Third 1.250)

| Token        | Size | Line height |
|--------------|------|-------------|
| `--text-xs`  | 11px | 15px        |
| `--text-sm`  | 13px | 18px        |
| `--text-md`  | 16px | 24px        |
| `--text-lg`  | 20px | 26px        |
| `--text-xl`  | 25px | 30px        |
| `--text-2xl` | 31px | 38px        |
| `--text-3xl` | 39px | 46px        |

### 3.8 Densidade (variáveis sobrepostas)

Estes tokens têm **dois valores possíveis** consoante o modo de densidade activo no portal:

| Token              | Compact (COE) | Comfortable (SSCI) |
|--------------------|---------------|---------------------|
| `--space-1`        | 2px           | 4px                 |
| `--space-4`        | 8px           | 12px                |
| `--space-6`        | 16px          | 24px                |
| `--row-height`     | 32px          | 40px                |
| `--input-height`   | 32px          | 40px                |
| `--nav-item-height`| 36px          | 44px                |
| `--text-base`      | 14px          | 16px                |
| `--line-base`      | 21px          | 24px                |

Ver [`shared/styles/tokens/density-compact.css`](../shared/styles/tokens/density-compact.css) e `density-comfortable.css` para a lista completa.

### 3.9 Status quad (Plan 7)

Tokens para os 4 estados operacionais dos stat-card-gauge KPIs:

| Semantic                    | Uso                                    |
|-----------------------------|----------------------------------------|
| `--status-normal-gauge`     | Preenchimento da gauge quando OK       |
| `--status-warning-gauge`    | Preenchimento da gauge quando warning  |
| `--status-critical-gauge`   | Preenchimento da gauge quando critical |
| `--status-unknown-gauge`    | Preenchimento da gauge quando unknown  |
| `--status-critical-pulse`   | Cor do dot animado (pulse)             |
| `--status-critical-tint`    | Background tint do card em critical    |

### 3.10 Pill active nav (Plan 7)

| Semantic              | Valor default          | Uso                          |
|-----------------------|------------------------|------------------------------|
| `--pill-bg`           | `var(--brand-primary)` | Fundo do nav-btn activo      |
| `--pill-fg`           | `var(--white)`         | Texto do nav-btn activo      |
| `--pill-icon`         | `var(--white)`         | Ícone SVG do nav-btn activo  |
| `--pill-shadow`       | shadow subtil          | Sombra do pill activo        |
| `--pill-hover-bg`     | cinza-azul claro       | Hover state dos nav-btn      |
| `--pill-radius`       | `var(--radius-md)`     | Border-radius do pill        |

### 3.11 Gauge tokens (Plan 7)

| Semantic                | Uso                                 |
|-------------------------|-------------------------------------|
| `--gauge-height`        | Altura da barra de progresso        |
| `--gauge-bg`            | Background track da gauge           |
| `--gauge-radius`        | Border-radius da gauge              |
| `--gauge-fill-normal`   | Fill quando status=normal           |
| `--gauge-fill-warning`  | Fill quando status=warning          |
| `--gauge-fill-critical` | Fill quando status=critical         |
| `--gauge-fill-unknown`  | Fill quando status=unknown          |
| `--gauge-transition`    | Transição da barra (width animate)  |

### 3.12 Motion tokens (Plan 7)

| Semantic               | Valor    | Uso                          |
|------------------------|----------|------------------------------|
| `--transition-hover`   | `120ms`  | Hover transitions (buttons, cards) |
| `--transition-active`  | `80ms`   | Active/press transitions     |

### 3.13 Typography tokens (Plan 7)

| Semantic              | Valor                    | Uso                              |
|-----------------------|--------------------------|----------------------------------|
| `--font-ui`           | `'Inter', sans-serif`    | Texto UI geral                   |
| `--font-numeric`      | `'JetBrains Mono', mono` | Números, IDs, timestamps         |
| `--font-mono-family`  | `'JetBrains Mono'`       | Referência directa à font-face   |

---

## 4. Tipografia — Inter Variable + JetBrains Mono

### Como é embebida

O `scripts/ds_build_helpers.py::encode_font_woff2_base64()` lê `shared/assets/fonts/Inter-VariableFont.woff2` e emite o bytes em base64. O resultado é injectado no placeholder `{{DS_INTER_WOFF2_BASE64}}` dentro de `shared/styles/base/fonts.css`:

```css
@font-face {
  font-family: 'Inter';
  font-weight: 100 900;
  src: url('data:font/woff2;base64,{{DS_INTER_WOFF2_BASE64}}') format('woff2-variations');
  font-display: block;
}
```

Resultado: zero network requests, trabalha offline, overhead ~280 KB de base64 por portal.

### font-feature-settings

Em `shared/styles/base/typography.css`, elementos DS usam `.ds-*` com:

```css
font-feature-settings: 'cv11', 'ss01', 'tnum', 'lnum';
```

- `cv11` (stylistic set) + `ss01` para a variante alternate do `a` e `g` (mais legível em UIs)
- `tnum` (tabular numerals) para alinhar colunas de dígitos
- `lnum` (lining figures) para uso geral (não oldstyle)

### Como actualizar Inter

1. Baixar a versão mais recente de `https://github.com/rsms/inter` (ficheiro `Inter-Variable.woff2`)
2. Copiar para `shared/assets/fonts/Inter-VariableFont.woff2`
3. Actualizar `shared/assets/fonts/README.md` com a nova versão
4. `python scripts/build-all.py` — o base64 é regenerado automaticamente

### JetBrains Mono (Plan 7)

Adicionada na v2.2.0-alpha.1 para valores numéricos (KPIs, timestamps, IDs, coordenadas).

- **Ficheiros**: `shared/assets/fonts/JetBrainsMono-Regular.woff2` + `JetBrainsMono-Bold.woff2`
- **Licença**: SIL Open Font License (OFL), incluída em `shared/assets/fonts/OFL.txt`
- **Tamanho total**: ~183 KB (Regular ~93 KB + Bold ~90 KB)
- **Embedding**: base64 via `encode_font_woff2_base64()`, mesma pipeline da Inter
- **Placeholders**: `{{DS_JETBRAINS_MONO_REGULAR_WOFF2_BASE64}}` e `{{DS_JETBRAINS_MONO_BOLD_WOFF2_BASE64}}`
- **Token**: `--font-mono-family: 'JetBrains Mono'` / `--font-numeric: 'JetBrains Mono', monospace`
- **Uso**: `.form-group--numeric input`, `.stat-card-gauge__value`, `.sticky-timer-card__time`, qualquer elemento que precise de tabular numerals monospace
- **font-feature-settings**: `'tnum' 1` (tabular numerals) para alinhamento perfeito de dígitos em colunas

### Limitações actuais

- Inter é aplicada apenas a elementos dentro de `.ds-shell-bar`, `.ds-sidebar`, `.ds-page-grid`, `.ds-splash`, `.ds-footer`
- Resto da página (cards, forms legacy, tabelas) continua em Segoe UI enquanto a migração de body typography não for feita (ver secção 11, FAQ)
- JetBrains Mono é aplicada selectivamente a campos numéricos e KPI values — não substitui Inter para texto geral

---

## 5. Componentes inventário

Os 19 componentes (13 base + 6 novos Plan 7) vivem em `shared/styles/components/`. Cada ficheiro é auto-contido: selecciona os tokens semantic que precisa e não depende de outros componentes.

| Ficheiro              | Exemplo de classe              | Variantes / estados                                         |
|-----------------------|--------------------------------|-------------------------------------------------------------|
| `button.css`          | `.btn`, `.btn-primary`         | primary, secondary, ghost, danger; hover, active, disabled  |
| `badge.css`           | `.badge`, `.badge--warning`    | 5 variantes de status                                        |
| `card.css`            | `.card`, `.stat-card`          | card, stat-card, elevated hover                              |
| `form-group.css`      | `.form-group`                  | input, textarea, select; focus, invalid, disabled            |
| `table.css`           | `.ds-table`                    | striped rows, sticky header                                  |
| `tabs.css`            | `.ds-tabs`, `.tab-button`      | active, disabled                                             |
| `dropdown.css`        | `.ds-dropdown`                 | open/closed, items                                           |
| `awm-modal.css`       | `.awm-modal*`                  | open/closed, overlay, close button                           |
| `awm-toast.css`       | `.awm-toast*`                  | info, success, warning, alert                                |
| `uxp-savebadge.css`   | `.uxp-savebadge*`              | neutro, saving, saved                                        |
| `skeleton.css`        | `.ds-skeleton`                 | shimmer animation                                            |
| `empty-state.css`     | `.ds-empty-state`              | icon + title + description layout                            |
| `stat-card-gauge.css` | `.stat-card-gauge`             | KPI card + mono value + progress gauge; 4 status states (Plan 7) |
| `state-pulse.css`     | `.state-pulse`                 | animated dot for critical/warning; prefers-reduced-motion fallback (Plan 7) |
| `dash-section.css`    | `.dash-section`                | row-based grouping with gradient divider (Plan 7)            |
| `form-banner.css`     | `.form-banner`                 | warning, info, critical inline contextual banners (Plan 7)   |
| `form-two-col.css`    | `.form-two-col`                | 2fr:1fr wrapper for forms with sticky sidebar (Plan 7)       |
| `sticky-timer-card.css`| `.sticky-timer-card`          | chronometer + summary + auto-save indicator (Plan 7)         |

**Modifiers** (Plan 7 — aplicados a componentes existentes):

| Modifier               | Componente base   | Efeito                                         |
|------------------------|-------------------|-------------------------------------------------|
| `.form-group--numeric` | `.form-group`     | Aplica JetBrains Mono a inputs numéricos        |
| `.nav-btn--pill`       | `.nav-btn`        | Pill active SGA (fundo sólido, shadow, radius)  |

### Exemplo mínimo — `button`

```html
<button class="btn btn-primary">Guardar</button>
<button class="btn btn-ghost">Cancelar</button>
```

O CSS fonte faz:
```css
.btn {
  padding: var(--space-3) var(--space-5);
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}
.btn-primary {
  background: var(--brand-primary);
  color: var(--white);
}
.btn-primary:hover {
  background: var(--brand-primary-hover);
}
```

### JS-load-bearing classes (preservadas!)

Os componentes `awm-modal`, `awm-toast`, `uxp-savebadge` têm classes que JavaScript do portal usa como seletores. **Nunca renomear**:

- `.awm-modal*`, `.awm-toast*`, `.uxp-savebadge*`
- `.contact-card*`, `.alarm-card*`, `.cr-chip`, `.tab-content`

---

## 6. Chrome (shell bar, sidebar, splash, footer, page-grid)

O "chrome" é a moldura visual partilhada. Todos os portais usam exactamente o mesmo markup.

### 6.1 Shell bar

```html
<header class="ds-shell-bar">
  <div class="ds-shell-bar__brand">
    <svg class="ds-shell-bar__logo" aria-hidden="true">
      <use href="#logo-sga-mark"/>
    </svg>
    <span class="ds-shell-bar__name">Portal COE</span>
  </div>
  <div class="ds-shell-bar__meta">
    <span id="clockDisplay">UTC 00:00:00</span>
    <span id="headerUTC"></span>
    <span id="headerDate"></span>
    <span id="operatorBadge"></span>
  </div>
</header>
```

CSS em [`shared/styles/chrome/shell-bar.css`](../shared/styles/chrome/shell-bar.css). Faixa institucional azul de 4px por baixo do shell bar é um `::after` pseudo-element com `background: var(--brand-primary)`.

### 6.2 Sidebar

```html
<aside class="ds-sidebar">
  <nav class="ds-sidebar__nav">
    <button class="nav-btn active" onclick="openSection('dashboard', event)">
      <svg class="icon"><use href="#icon-dashboard"/></svg>
      Dashboard
    </button>
    <!-- ... -->
  </nav>
</aside>
```

Indicador visual de secção activa: `border-left: 4px solid var(--brand-primary)`. Cada `.nav-btn` tem altura `var(--nav-item-height)` que muda com densidade.

### 6.3 Splash screen

```html
<div class="ds-splash" id="ds-splash">
  <svg class="ds-splash__logo"><use href="#logo-sga-full"/></svg>
  <p class="ds-splash__tagline">Aeroporto FNMO — DREA</p>
</div>
```

Lifecycle: aparece no load, fade-out após ~1500ms. Ciclo via JavaScript em `shared/scripts/chrome/splash.js` (inlined no `<body>` via build). Bypass para dev: `?nosplash=1` query param.

### 6.4 Footer

```html
<footer class="ds-footer">
  <span>Portal COE v2.1.0-alpha.1 · OACI FNMO · Build 2026-04-11</span>
</footer>
```

### 6.5 Page grid

```html
<main class="ds-page-grid">
  <div class="ds-page-grid__content">
    <!-- conteúdo operacional do portal aqui -->
  </div>
</main>
```

`ds-page-grid` define `display: grid`, margens, gutters, max-width. É o "viewport" de conteúdo do portal.

---

## 7. Ícones — sprite SVG inline

### Como funciona

Um `<svg>` no início do `<body>` contém **todos** os ícones como `<symbol>` definitions. Cada uso é um `<svg><use href="#icon-X"/></svg>`:

```html
<body>
  <svg class="ds-sprite" hidden>
    <symbol id="icon-home" viewBox="0 0 24 24">...</symbol>
    <symbol id="icon-siren" viewBox="0 0 24 24">...</symbol>
    <!-- 40+ símbolos -->
  </svg>

  <!-- uso -->
  <svg class="icon"><use href="#icon-home"/></svg>
</body>
```

O sprite é `shared/assets/icons/sprite.svg`, injectado via placeholder `{{DS_SPRITE}}` pelo build.

### Ícones disponíveis

Ver [`shared/assets/icons/sprite.svg`](../shared/assets/icons/sprite.svg) — cada `<symbol id="icon-*">` é um ícone. Exemplos: `icon-home`, `icon-dashboard`, `icon-siren`, `icon-fire-truck`, `icon-shield`, `icon-clock`, `icon-users`, `icon-phone`, ...

### Como adicionar um ícone novo

1. Escolher o SVG (Heroicons Outline preferido — já no stack)
2. Guardar o ficheiro em `shared/assets/icons/sources/icon-<name>.svg` (opcional, apenas para histórico)
3. Copiar o conteúdo `<svg>` → `<symbol id="icon-<name>">` em `shared/assets/icons/sprite.svg`
4. `python scripts/build-all.py` → o sprite é re-injectado
5. Usar com `<svg class="icon"><use href="#icon-<name>"/></svg>`

---

## 8. Modos de densidade (compact vs comfortable)

### Como um portal escolhe

Cada portal tem `portal.config.json`. O campo `density` aceita `"compact"` ou `"comfortable"`:

```json
{
  "name": "Portal COE",
  "density": "compact",
  ...
}
```

`scripts/ds_build_helpers.py::resolve_density()` lê este valor e escolhe qual ficheiro de densidade incluir na cascade. O build emite `<html data-density="compact">` no output final.

### Override por aeroporto

Um aeroporto pode ter preferência de densidade diferente do default do portal. Isto é feito em `packages/portal-coe/config/airport-XXX.json`:

```json
{
  "oaci": "FNMO",
  "portals": {
    "coe": { "density": "comfortable" }
  }
}
```

### Semântica operacional

- **Compact (COE)**: operadores jovens, sala de controlo, monitor 24/7. Densidade alta = mais informação por ecrã = menos scroll em cenário de emergência.
- **Comfortable (SSCI)**: operadores de segurança com rondas de inspecção, workstation partilhada, idades variadas. Densidade confortável = menos fadiga visual.

---

## 9. Como adicionar um portal novo

Template para quem vai criar Portal SOA, AVSEC, ou DIRECÇÃO:

### 9.1 Criar a estrutura

```
packages/portal-XXX/
├── config/                       # optional — por-aeroporto overrides
│   └── airport-FNMO.json
├── portal.config.json
├── scripts/
│   └── build.py                  # cópia adaptada do COE/SSCI
└── src/
    └── Portal_XXX_AWM.source.html
```

### 9.2 Configurar `portal.config.json`

```json
{
  "name": "Portal XXX",
  "tagline": "Secção Operacional do Aeroporto",
  "role": "SOA",
  "density": "compact",
  "ui": {
    "show_occurrence_pill": false,
    "show_chronometer": false
  }
}
```

### 9.3 Criar o source HTML

Template mínimo (usando os placeholders do build):

```html
<!DOCTYPE html>
<html lang="pt" data-density="{{DS_DENSITY}}">
<head>
  <meta charset="UTF-8">
  <title>{{PORTAL_NAME}}</title>
  <style>
    {{DS_CSS}}
  </style>
</head>
<body>
  <!-- DS sprite -->
  {{DS_SPRITE}}

  <!-- DS splash -->
  <div class="ds-splash" id="ds-splash">
    <svg class="ds-splash__logo"><use href="#logo-sga-full"/></svg>
    <p class="ds-splash__tagline">{{PORTAL_TAGLINE}}</p>
  </div>

  <header class="ds-shell-bar">...</header>
  <aside class="ds-sidebar">...</aside>
  <main class="ds-page-grid">
    <div class="ds-page-grid__content">
      <!-- conteúdo operacional do portal -->
    </div>
  </main>
  <footer class="ds-footer">...</footer>

  <script>
    {{DS_JS}}
  </script>
</body>
</html>
```

### 9.4 Criar `scripts/build.py`

Copiar `packages/portal-coe/scripts/build.py` e ajustar os paths para o novo portal. As ~50 linhas de boilerplate são praticamente idênticas entre portais.

### 9.5 Registar em `scripts/build-all.py`

Adicionar `"portal-xxx"` à lista de targets.

### 9.6 Build e verificar

```bash
python scripts/build-all.py
```

Abrir o HTML gerado em Chrome. Shell bar, sidebar, splash, footer e page grid devem aparecer automaticamente sem CSS adicional.

**Zero novo CSS é necessário**. Toda a fundação visual vem do DS partilhado.

---

## 10. WCAG compliance + testing

### Contrastes documentados

Todos os pares semantic texto/fundo são verificados em [`shared/styles/tokens/semantic.css`](../shared/styles/tokens/semantic.css) com comentários inline:

```css
--brand-primary: var(--blue-800);  /* 9.05:1 AAA — #004C7B on white */
--status-warning-fg: var(--amber-900);  /* 5.48:1 AA — #8a5a00 on #fef5e7 */
```

Quando um contraste é "at floor" (mesmo no limite), há um comentário explícito: *"7.00:1 AAA AT FLOOR — do not lighten bg or shift fg"*.

### Regra: cor nunca é o único canal

Um indicador de status nunca deve depender só de cor. Exemplos:

- Um badge de erro tem **texto** "Erro" + **ícone** ⚠ + cor vermelha
- Uma linha activa na sidebar tem `border-left` + fundo subtil + cor + bold
- Um input inválido tem `aria-invalid="true"` + border vermelha + ícone ⚠

Razão: utilizadores daltónicos (~8% dos homens) distinguem mal vermelho/verde.

### Axe DevTools

Processo manual de validação:

1. Abrir o portal em Chrome
2. Instalar extensão "axe DevTools"
3. F12 → axe DevTools tab → "Scan all of my page"
4. Zero violations críticas é o alvo

### Simuladores de daltonismo

Chrome DevTools → Rendering tab → "Emulate vision deficiencies" → testar protanopia, deuteranopia, tritanopia.

---

## 11. FAQ / pitfalls

### "Porque é que o meu token não resolve?"

Provavelmente estás a usar um primitive em vez do semantic:

```css
/* ❌ errado — primitives são opacos */
.my-button { background: var(--blue-800); }

/* ✅ correcto */
.my-button { background: var(--brand-primary); }
```

Se o semantic apropriado não existe, adiciona-o em `semantic.css` primeiro e usa o novo token no componente.

### "Porque é que o meu componente parece diferente no SSCI?"

Density mode. SSCI é `comfortable`, COE é `compact`. Tokens como `--space-*`, `--row-height`, `--input-height`, `--text-base` têm valores diferentes. Se o componente precisa de render idêntico em ambos, não usar os tokens de densidade — usar primitives `--space-N-px` explícitos (mas isto é raro).

### "O browser mostra a página sem Inter"

Inter falhou a carregar. Causas:

1. Base64 não intacto no build — verificar `shared/assets/fonts/Inter-VariableFont.woff2` existe
2. `encode_font_woff2_base64()` devolveu string vazia — correr `pytest tests/test_ds_build_helpers.py -v`
3. `font-display: block` está configurado, mas com CSP muito restritivo `data:` URIs podem ser bloqueados — auditar CSP no HTML

### "Adicionei um componente mas não aparece no output"

Faltou registar na cascade:

- Confirma que o ficheiro está em `shared/styles/components/`
- Confirma que tem extensão `.css`
- Corre `python scripts/build-all.py` novamente (o discovery é alfabético, deve apanhar automaticamente)
- Se ainda falha, ver logs do build para ver se foi concatenado

### "Como desligo o splash em desenvolvimento?"

Adicionar `?nosplash=1` ao URL. Ver [`shared/scripts/chrome/splash.js`](../shared/scripts/chrome/splash.js) para o handling.

### "Adicionei um token `--ds-foo` e não funciona"

Durante a v2.1.0 migration o namespace `--ds-*` foi removido. Todos os tokens são `--foo` directamente. Se vires `--ds-*` algures no código, é um resíduo — reportar.

---

## Referências

- Spec canónica: [`docs/superpowers/specs/2026-04-11-design-system-sga-design.md`](superpowers/specs/2026-04-11-design-system-sga-design.md)
- Arquitectura global: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
- Contributor guide (CSS): [`shared/styles/README.md`](../shared/styles/README.md)
- Contributor guide (JS): [`shared/scripts/README.md`](../shared/scripts/README.md)
- Release notes (latest): [`docs/releases/v2.2.0-alpha.1.md`](releases/v2.2.0-alpha.1.md)
- Release notes (foundation): [`docs/releases/v2.1.0-alpha.1.md`](releases/v2.1.0-alpha.1.md)
- CHANGELOG: [`docs/CHANGELOG.md`](CHANGELOG.md)

---

*Guia mantido por Marcio Sager (SGSO) + Claude Opus 4.6 (1M context). Reportar erros ou propor melhorias via issues do repositório.*
