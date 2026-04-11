# Design System SGA — Design Document

**Data**: 2026-04-11
**Versão do documento**: 1.1 (post spec-review fixes)
**Autor**: Marcio Sager (consultor SGSO) + Claude (brainstorming session)
**Status**: Aprovado pelo spec-review — aguarda aprovação final do utilizador
**Pesquisa de mercado associada**: [2026-04-11-design-system-market-research.md](../research/2026-04-11-design-system-market-research.md)
**Milestone de destino**: Portal DREA v2.1.0-alpha.1

### Revisions
- **v1.0** (2026-04-11): draft inicial consolidando brainstorming session
- **v1.1** (2026-04-11): aplicados 5 fixes não-bloqueantes identificados no spec-review:
  1. Assinatura real do `build()` preservada (`source_path, config_path, output_path, validate`); nota explícita de que há dois `build.py` a actualizar em paralelo; refactoring opcional para `scripts/ds_build_helpers.py` documentado
  2. Coexistência de CSS legado com `{{DS_CSS}}` durante Fases 1-4 explicitada com regras determinísticas de posicionamento e ordem
  3. Convenção de placeholders alinhada com `_flatten_dict` existente: blobs manuais em `{{UPPER_SNAKE}}`, campos de config em `{{PARENT.CHILD}}`
  4. `--status-<level>-emphasis` e `--status-<level>-on-emphasis` com hex explícitos para os 5 níveis, incluindo nota crítica de que warning emphasis exige texto escuro (amber brilhante falha WCAG com branco)
  5. Threshold de tamanho de HTML na validação Nível 1 refinado para deltas intencionais pré-declarados por fase

---

## 1. Contexto e problema

### 1.1 Estado actual

O Portal DREA é uma plataforma monorepo (`v2.0.0-beta.1`) que contém dois portais operacionais em produção para aeroportos da SGA (Sociedade de Gestão Aeroportuária, Angola):

- **Portal COE** — usado pelo Coordenador do Centro de Operações de Emergência durante ocorrências reais (emergências aeronáuticas, AVSEC). Visual actual: sidebar azul-escura, header gradient SGA, logo SGA em dois sítios (sidebar + header). Feel "mission control".
- **Portal SSCI** — usado pelo Chefe SSCI/Bombeiros para gestão do quartel (inspecções VCI, checklists, estoque, tempos de resposta). Visual actual: tudo light/branco, header minimalista, **sem logo visível**. Feel "documento institucional".

Os dois portais partilham a mesma paleta SGA em `:root` (`--dark-blue: #004C7B`, `--medium-blue: #0094CF`) mas não partilham componentes. Cada um tem o seu próprio `<style>` monolítico inline. A pasta `shared/styles/` e `shared/scripts/` existem mas estão vazias.

### 1.2 Problema

A divergência visual entre os dois portais prejudica:
1. **Percepção de "produto unificado"** — utilizadores e auditores ANAC vêem duas ferramentas aparentemente não-relacionadas
2. **Manutenção** — qualquer mudança visual tem que ser aplicada duas vezes, com risco de divergência
3. **Escala futura** — os portais planeados (SOA, AVSEC, DIRECÇÃO) não têm um design system donde herdar
4. **Consistência de identidade SGA** — o logo aparece em alguns sítios e noutros não, as cores são usadas inconsistentemente, não há convenções

### 1.3 Escopo do documento

Este design define o **Design System SGA** a ser criado em `shared/` e aplicado aos dois portais existentes. Prepara o terreno para os três portais futuros. **Não** cobre a extracção de componentes de domínio (flow-node, cronómetro, inspecção VCI) para `shared/` — esses ficam no portal respectivo consumindo tokens do DS.

---

## 2. Decisões aprovadas durante o brainstorming

Estas decisões foram tomadas em conjunto durante a sessão de brainstorming de 2026-04-11 e são **pré-requisitos load-bearing** para todo o resto do documento:

| # | Decisão | Escolha |
|---|---|---|
| 1 | Ambição | **Design System SGA completo** — tokens, componentes, guidelines, documentação, servindo COE+SSCI+futuros |
| 2 | Tema | **Light theme only** — não há dark, não há toggle |
| 3 | Chrome | **Shell Bar Puro** — estilo Fiori Quartz Light: chrome todo light, header com faixa institucional fina, logo único no header, sidebar totalmente branca, UTC timestamp permanente |
| 4 | Conflito amber `#f39c12` | **Amber fica como warning semântico**, AVSEC/Bombeiros passa a ser identificado pelo **vermelho `#c62828`** (aceita-se o dual-use vermelho = categoria + alert, resolvido por posição + ícone + contexto) |
| 5 | Tipografia | **Inter Variable embutida em base64** (~+200KB por portal) — identidade visual mais forte, tabular figures nativas |
| 6 | Densidade | **Configurável por portal via token** — COE compact, SSCI comfortable, futuros escolhem no build |

Estas decisões derivam de uma pesquisa de mercado de 6 eixos (design systems operacionais, UI aeronáutica, C2 mission-critical, tipografia data-dense, placement de branding, escalas de status WCAG AA) documentada em [docs/superpowers/research/2026-04-11-design-system-market-research.md](../research/2026-04-11-design-system-market-research.md).

As três referências principais que informaram o design (nenhuma adoptada como dependência):
- **SAP Fiori Quartz Light** — padrões de layout operacional, shell bar, object page
- **IBM Carbon + GitHub Primer** — disciplina de tokens semânticos, system font stack
- **USWDS** — rigor WCAG AA, estados de status robustos

---

## 3. Foundation (tokens, paleta, tipografia, densidade)

### 3.1 Arquitectura de tokens em 3 camadas

Padrão Carbon/Primer:

- **Camada 1 — Primitivos** (`shared/styles/tokens/primitive.css`): valores brutos sem significado. `--blue-700: #004C7B`, `--red-600: #c62828`. Nunca referenciados por componentes.
- **Camada 2 — Semânticos** (`shared/styles/tokens/semantic.css`): aliases com significado. `--fg-default`, `--bg-surface`, `--status-warning-border`. **Componentes referenciam apenas estes.**
- **Camada 3 — Componente** (inline nos files de componente): overrides locais quando necessário. `--button-primary-bg`. Normalmente só aliases dos semânticos.

### 3.2 Paleta completa (todos os hexadecimais, WCAG AA/AAA verificado)

#### Neutros (chrome)

| Token | Hex | Uso | Contraste |
|---|---|---|---|
| `--neutral-canvas` | `#f6f8fa` | Body background | — |
| `--neutral-surface` | `#ffffff` | Cards, modals, inputs | — |
| `--neutral-subtle` | `#eef2f7` | Hover, divider fundo | — |
| `--neutral-muted` | `#e1e5eb` | Borders default | — |
| `--neutral-fg` | `#24292f` | Texto primário | 13.1:1 ✓ AAA |
| `--neutral-fg-muted` | `#57606a` | Texto secundário | 5.8:1 ✓ AA |
| `--neutral-fg-subtle` | `#8b95a1` | Texto terciário | 3.5:1 ✓ large-only |

#### Brand SGA

| Token | Hex | Uso | Contraste |
|---|---|---|---|
| `--brand-primary` | `#004C7B` | Headings, links, texto institucional, faixa shell bar | 9.1:1 ✓ AAA |
| `--brand-primary-hover` | `#003a5e` | Link hover | 11.8:1 ✓ AAA |
| `--brand-secondary-fill` | `#0094CF` | **Fills**, backgrounds de botões, borders, hovers — **nunca texto** | 3.5:1 ✗ |
| `--brand-secondary-text` | `#0073a0` | Variante escurecida para texto/links secundários | 4.9:1 ✓ AA |
| `--brand-accent` | `#38C7F4` | Destaques, focus ring | — |

#### Semantic status — escala de 5 níveis

Cada nível tem **4 tokens**: `bg` (fundo subtle), `border` (aresta e status stripe), `fg` (texto sobre bg), `emphasis` (fill forte — usado em botões e banners carregados, com texto branco acima).

| Nível | `bg` | `border` | `fg` (texto sobre bg) | Contraste texto | `emphasis` (fill forte) | Texto sobre emphasis |
|---|---|---|---|---|---|---|
| `info` | `#e6f4fb` | `#0073a0` | `#003a5e` | 11.2:1 ✓ AAA | `#0073a0` | `#ffffff` (5.6:1 ✓ AA) |
| `success` | `#e8f5e9` | `#2e7d32` | `#1b5e20` | 9.7:1 ✓ AAA | `#2e7d32` | `#ffffff` (5.7:1 ✓ AA) |
| `warning` | `#fef5e7` | `#f39c12` | `#8a5a00` | 6.3:1 ✓ AA | `#f39c12` | `#1a1200` (14.5:1 ✓ AAA — amber **exige** texto escuro, não branco) |
| `alert` | `#fdecea` | `#c62828` | `#b71c1c` | 6.8:1 ✓ AA | `#c62828` | `#ffffff` (5.9:1 ✓ AA) |
| `emergency` | `#ffcdd2` | `#8b0000` (pulsante 2px) | `#8b0000` | 9.3:1 ✓ AAA | `#8b0000` | `#ffffff` (11.4:1 ✓ AAA) |

**Nota importante sobre `warning` emphasis**: o amber `#f39c12` é suficientemente brilhante para **exigir texto escuro** sobre si (o branco daria apenas 2.2:1, falha WCAG). Este é o único nível com texto escuro sobre emphasis. Para botões warning, sempre `color: #1a1200` (quase-preto quente).

Tokens por nível (nomenclatura completa):
```
--status-<level>-bg         (fundo subtle de banner/card)
--status-<level>-border     (border e status stripe 4px)
--status-<level>-fg         (texto sobre bg subtle)
--status-<level>-emphasis   (fill forte para botão/banner)
--status-<level>-on-emphasis (texto sobre emphasis)
```

**Nota sobre `success` — adição à paleta SGA**: a paleta SGA original não tem verde. Acrescentamos `#2e7d32` / `#e8f5e9` / `#1b5e20` como adição formal, justificada pela necessidade operacional (checklists completos, veículos VCI operacionais, estado "OPERACIONAL").

#### Category — branding de categoria em contactos e fluxogramas

| Token | Hex | Categoria | Ícone |
|---|---|---|---|
| `--cat-avsec-bombeiros` | `#c62828` | AVSEC / Bombeiros / SSCI | 🚒 + "SSCI" |
| `--cat-sga-interna` | `#004C7B` | SGA interna (Dir, SREA, OPS, Manut, SGSO) | ✈ + "SGA" |
| `--cat-enna-navegacao` | `#0094CF` | ENNA (TWR, AIS, Meteo) | 🗼 + "ENNA" |
| `--cat-seg-ordem` | `#5d4037` | SME, PCUA, P.Fiscal, UPSOE, SIC | 🛡 + "ORDEM" |
| `--cat-externa-emg` | `#6a1b9a` | SPCB, INEMA, PNA, Hospital | 🆘 + "EXT" |
| `--cat-operadores` | `#455a64` | TAAG, BESTFLY, Sonangol | ✈ + "OPS" |

### 3.3 Regra de ouro: cor nunca é o único canal

Cada categoria tem **cor + ícone + rótulo textual**. Cada estado semântico tem **cor + ícone + texto**. Isto protege:
- Daltónicos (~8% da população masculina)
- Operadores sob stress de ocorrência real
- Impressões a preto-e-branco
- Screens com brilho muito baixo ou muito alto

### 3.4 Tipografia

**Família principal**: Inter Variable, embutida como woff2 base64 em `shared/styles/base/fonts.css`.

```css
font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI Variable",
             "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
font-variant-numeric: tabular-nums;  /* global — tabelas alinham */
font-feature-settings: "cv11", "ss01", "ss03";  /* Inter stylistic sets */
```

**Mono**: `ui-monospace, "SF Mono", "Cascadia Mono", "Segoe UI Mono", Consolas, monospace` — system stack, zero bytes.

**Type scale** (Major Third, 1.250 ratio):

| Token | Size | Line-height | Uso |
|---|---|---|---|
| `--text-xs` | 11px | 15px | Captions, badges, metadata |
| `--text-sm` | 13px | 18px | Body secondary |
| `--text-base` | 14px (compact) / 16px (comfortable) | 21/24px | Body default |
| `--text-md` | 16px | 24px | Body emphasized |
| `--text-lg` | 20px | 26px | H3, section headings |
| `--text-xl` | 25px | 30px | H2 |
| `--text-2xl` | 31px | 38px | H1 / page title |
| `--text-3xl` | 39px | 46px | Dashboard hero numbers |

**Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold) — todos num só ficheiro Inter Variable.

**Custo no bundle**: ~150 KB (woff2 Inter Variable completo) → ~200 KB após encode base64, tolerável face aos ~4 MB actuais do COE.

### 3.5 Densidade (modo por portal)

Dois modos, escolhidos no build time por portal:

| Token | Compact (COE, futuros SOA/AVSEC) | Comfortable (SSCI, futuro DIRECÇÃO) |
|---|---|---|
| `--space-1` | 2px | 4px |
| `--space-2` | 4px | 6px |
| `--space-3` | 6px | 8px |
| `--space-4` (default stack) | 8px | 12px |
| `--space-5` | 12px | 16px |
| `--space-6` (card padding) | 16px | 24px |
| `--space-7` | 24px | 32px |
| `--space-8` | 32px | 48px |
| `--row-height` (tabela) | 32px | 40px |
| `--input-height` (form) | 32px | 40px |
| `--nav-item-height` | 36px | 44px |
| `--text-base` (body) | 14px | 16px |

O `build.py` resolve: `airport config override` → `portal.config.json` → default `compact`.

### 3.6 Elevation, radii, motion, focus

**Elevation** (shadows soft, light-theme-appropriate):
```
--shadow-1: 0 1px 2px rgba(9,30,66,0.08)    /* cards resting */
--shadow-2: 0 2px 8px rgba(9,30,66,0.12)    /* card hover, sticky header */
--shadow-3: 0 8px 24px rgba(9,30,66,0.15)   /* modal, dropdown */
--shadow-4: 0 24px 48px rgba(9,30,66,0.20)  /* full-screen modal */
```

**Border radius**:
```
--radius-sm: 3px
--radius-md: 6px
--radius-lg: 8px
--radius-pill: 9999px
```

**Motion**:
```
--transition-fast: 120ms cubic-bezier(.2,0,0,1)
--transition-base: 200ms cubic-bezier(.2,0,0,1)
--transition-slow: 320ms cubic-bezier(.2,0,0,1)
```

Respeitando `prefers-reduced-motion: reduce` (desliga transições excepto focus ring).

**Focus ring** (a11y crítico):
```css
outline: 2px solid var(--brand-secondary-text);  /* #0073a0 */
outline-offset: 2px;
```

---

## 4. Chrome (shell bar, sidebar, page grid, splash, footer)

### 4.1 Shell bar

Header fixo superior, 3 zonas horizontais, inspirado em Fiori Quartz Light + Carbon UI Shell.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ [SGA▲] Portal COE │ FNMO      │ Dashboard › Ocorrência    │ UTC 10:56:30│
│                   │           │                           │ Local 11:56 │
│                   │           │                           │ [👤 MS ▾]   │
└─────────────────────────────────────────────────────────────────────────┘
 4px faixa #004C7B (assinatura institucional SGA)
```

**Anatomia**:
- Altura: 56px (compact) ou 64px (comfortable)
- Fundo: `--neutral-surface` (`#ffffff`)
- Border-bottom: 1px `--neutral-muted`
- Sombra: `--shadow-1`
- **Faixa institucional 4px em `--brand-primary`** imediatamente abaixo — única assinatura de cor SGA no chrome, preserva identidade do COE actual dentro do light theme

**Zona esquerda** (fixa, ~280px):
- SGA mark 32x32 (símbolo só) via `<use href="#icon-sga-mark"/>` (inline SVG, zero bytes externos)
- Nome do portal em `--text-md` bold — vem do `portal.config.json`
- Separador vertical 1px
- OACI do aeroporto em `--text-sm` `--neutral-fg-muted` — vem do `airport-XXX.json`

**Zona central** (flex):
- Breadcrumb da secção actual (`Dashboard › Ocorrência Aeronáutica`)
- `--text-sm` `--neutral-fg-muted`, hover volta

**Zona direita** (fixa, ~320px):
- **UTC timestamp permanente** em mono tabular: `UTC 10:56:30` — actualiza a cada segundo
- Local time abaixo: `Local 11:56` (`--text-xs` `--neutral-fg-muted`)
- Separador vertical 1px
- User badge com dropdown: Perfil, Definições, Sair
- Em estado de ocorrência activa: **pill vermelha pulsante** `🚨 OCORRÊNCIA ACTIVA 00:02:34` à esquerda do user badge

**Responsive**: <1024px breadcrumb colapsa. <768px UTC+local combinam. Desktop-first, não parte em mobile.

### 4.2 Sidebar

**Anatomia**:
- Largura: 240px (compact) / 256px (comfortable); colapsa a 56px (ícones só)
- Fundo: `--neutral-canvas` (`#f6f8fa`) — ligeiramente mais escuro que o content (`#ffffff`) para criar separação sem cor
- Border-right: 1px `--neutral-muted`
- **Sem logo no topo** — logo vive só no shell bar
- Section group headings: `--text-xs` uppercase `--neutral-fg-muted`, letter-spacing 1px
- Nav items: altura `--nav-item-height`, ícone 20x20 + label `--text-sm`
  - Default: `--neutral-fg-muted`
  - Hover: `--neutral-subtle` bg, `--brand-primary` text
  - Active: `--neutral-surface` bg (branco), `--brand-primary` text bold, **border-left 3px `--brand-primary`**

A presença SGA na sidebar vive **só no border-left do item active**, nada mais.

### 4.3 Page grid

```
┌─ shell bar ─────────────────────────────┐
├───────┬─────────────────────────────────┤
│ side  │  Page content (canvas bg)       │
│ bar   │  ┌───────────────────────────┐  │
│       │  │ h1 Page title             │  │
│       │  │ p.page-desc               │  │
│       │  └───────────────────────────┘  │
│       │  Section cards (white)          │
│       │                                 │
│       │  footer institucional           │
└───────┴─────────────────────────────────┘
```

- Canvas: `--neutral-canvas`
- Content max-width: 1440px centrado (ou full-width por secção)
- Content padding horizontal: `--space-7`
- Page header: `h1.page-title` em `--text-2xl` `--brand-primary`; `p.page-desc` em `--text-sm` `--neutral-fg-muted`
- Section cards: `--neutral-surface`, `--radius-lg`, `--shadow-1`, padding `--space-6`, border 1px `--neutral-muted`
- Grid: `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`, gap `--space-6`

### 4.4 Splash screen

Arranque de cada portal durante ~1.5s antes do shell bar aparecer.

Conteúdo:
- Logo SGA completo (lockup) 120x120 centrado
- Nome do portal em `--text-2xl` `--brand-primary` (ex: `Portal COE`)
- Tagline DREA em `--text-sm` `--neutral-fg-muted`: `DREA · Direcção de Resposta a Emergências Aeroportuárias`
- OACI + nome do aeroporto em `--text-xs` tracked uppercase
- Versão + build date em `--text-xs`
- Faixa 4px `--brand-primary` em baixo (consistência com shell bar)

Fade-out: `@keyframes splash-out` (opacity 1→0, 400ms) após 1500ms. Bypass: `?nosplash=1` query param.

### 4.5 Footer institucional

Linha fina no fundo de cada página (do scroll do content, não do viewport):

```
SGA — Sociedade de Gestão Aeroportuária · Portal COE v2.1.0 · FNMO · 2026-04-11
```

`--text-xs` `--neutral-fg-subtle`, padding `--space-5` vertical, border-top 1px.

### 4.6 Print header

`@media print` esconde shell bar e sidebar, substitui por cabeçalho de documento em cada página:

```
┌─────────────────────────────────────────────────────────────┐
│ [SGA▲] SGA — Sociedade de Gestão Aeroportuária              │
│        Aeroporto Welwitschia Mirabilis (FNMO)               │
│        Portal COE — Verificação Mensal de Contactos         │
│        Impresso 2026-04-11 10:56 UTC · Op: Marcio Sager     │
├─────────────────────────────────────────────────────────────┤
│ (conteúdo impresso)                                         │
├─────────────────────────────────────────────────────────────┤
│ SGA · Confidencial · Página 3 de 7                          │
└─────────────────────────────────────────────────────────────┘
```

- Logo via inline SVG data URI
- Repetição em cada página via `@page { margin-top: 3cm }` + CSS Paged Media
- Numeração via `counter(page)` + `counter(pages)`
- Validado em Chrome Save-as-PDF, Edge print preview, Firefox print preview

---

## 5. Components inventory

Organização em 4 tiers. Tier 4 é domain — fica no portal mas consome tokens do DS.

### 5.1 Tier 1 — Core primitives (MVP obrigatório)

| Componente | Variantes | Estados |
|---|---|---|
| **Button** | primary, secondary, ghost, danger, success, icon-only | default, hover, focus-visible, active, disabled, loading. 3 tamanhos: sm/md/lg |
| **Input** | text, number, email, date, time, textarea | default, focus, filled, error, disabled. Error state: border `--status-alert-border` + ícone `!` + texto help |
| **Select** | native `<select>` styled | mesmos estados que input |
| **Checkbox** | default, indeterminate | unchecked, checked, indeterminate, focus, disabled. SVG inline para o check |
| **Radio** | — | unchecked, checked, focus, disabled. 16x16 |
| **Toggle** | — | off, on, focus, disabled. 32x20 pill |
| **Badge** | neutral, info, success, warning, alert, emergency + 6 category | static, dismissible. `--text-xs`, padding 2px 8px, `--radius-pill` |
| **Icon** | inline SVG sprite | via `<use href="#icon-X"/>` |
| **Form group** | field, fieldset | error state, required indicator. Wrapper label+input+help+error |
| **Divider** | horizontal, vertical, strong | 1px `--neutral-muted` |

### 5.2 Tier 2 — Layout patterns

| Componente | Variantes |
|---|---|
| **Card** | default, with-header, with-footer, with-status-stripe (border-left 4px), interactive (hover lift) |
| **Section card** | Wrapping de secção de página com h3 + badge + actions |
| **Stat card** | Dashboard métrico: default, trend-up, trend-down, com ícone grande opcional |
| **Table** | Sticky header, row hover, zebra opcional, selection checkbox, action column, responsive scroll |
| **Tabs** | horizontal (default), vertical (para settings) |
| **Dropdown menu** | menu-item, menu-item-danger, menu-divider, menu-section-heading |

### 5.3 Tier 3 — Feedback / Overlays

Extendem padrões `awm-*` **existentes** preservando classe e API JS para não partir código existente.

| Componente | Extends | Mudança |
|---|---|---|
| **awm-modal** | v8+ (focus trap, aria-labelledby) | Re-tokeniza cores, sombras, radii. API JS preservada. Variantes sm/md/lg/full |
| **awm-toast** | v6+ | Re-tokeniza. success/warning/error/info mapeiam directamente aos tokens semânticos |
| **awm-save-badge** | v6 | Re-tokeniza |
| **Skeleton** | novo | Placeholder animado para loading. Respeita prefers-reduced-motion |
| **Empty state** | novo | Ilustração SVG + título + texto + CTA opcional |

### 5.4 Tier 4 — Domain components (vivem no portal, não no DS)

| Componente | Portal | Consome |
|---|---|---|
| Contact card | COE + SSCI | Card (with-header) + Badge (category) + tokens |
| Flow node | COE | Tokens de cor + radius + shadow |
| Phase badge (alerta/resposta/operações/resolução) | COE | Badge semântico + variante custom |
| Emergency cronómetro | COE | Button + stat card patterns |
| Inspection checklist row (VCI) | SSCI | Form group + checkbox + card |
| Stock counter | SSCI | Input number + button + stat card |
| Verificação Mensal table | COE | Table Tier 2 |
| EFB form | COE | Form group + sections + tabs |

### 5.5 Icon system

**Requisito**: zero dependências, zero CDN, tudo inline.

**Solução**: inline SVG sprite em `shared/assets/icons/sprite.svg`, embutida no `<body>` pelo build, referenciada via `<svg><use href="#icon-X"/></svg>`.

**Conjunto inicial (~40 ícones)**, base Heroicons Outline (MIT):
- Navigation: home, dashboard, contacts, checklist, map, flowchart, document, settings, help, logout
- Status: check-circle, alert-triangle, x-circle, info-circle, alert-octagon (emergency), clock
- Actions: plus, pencil, trash, download, upload, print, copy, save, search, filter
- Chevrons: left, right, up, down
- Toggle: menu, close, more-horizontal, more-vertical
- Semantic: siren (emergency), shield (AVSEC), airplane, fire, phone, mail, user, users
- Domain: helmet (bombeiro), truck (VCI), runway, radar
- Brand: sga-mark (símbolo SGA)

Peso estimado: ~12 KB. `viewBox="0 0 24 24"` consistente. Cor via `currentColor`.

### 5.6 Escopo out (explicitado)

- ❌ Data visualization / charts / graphs (Tier 4 no portal, v2 do DS)
- ❌ Calendários / date pickers avançados (usa `<input type="date">` nativo)
- ❌ Rich text editor
- ❌ Drag and drop
- ❌ Animações elaboradas (só subtle hover/focus; emergency pulse é excepção documentada)
- ❌ i18n completo (PT-PT only)
- ❌ Dark mode (explicitamente descartado)
- ❌ Notificações persistentes cross-session
- ❌ Chat/mensagens

### 5.7 Total

~21 componentes genéricos (Tier 1-3) + icon sprite + re-tokenização dos domain components nos portais.

---

## 6. File organization & build pipeline

### 6.1 Estrutura expandida de `shared/`

```
shared/
├── README.md
├── assets/
│   ├── logo-sga-mark.svg                        NEW — símbolo 32x32 para shell bar
│   ├── logo-sga-full.svg                        NEW — lockup para splash
│   ├── logo-sga.png                             (existing, legacy)
│   ├── logo-sga-white.png                       (existing, deprecar)
│   ├── icons/
│   │   ├── sprite.svg                           NEW — ~40 ícones
│   │   ├── sources/                             NEW — SVGs editáveis
│   │   └── README.md                            NEW
│   └── fonts/
│       ├── Inter-VariableFont.woff2             NEW
│       ├── LICENSE-OFL.txt                      NEW
│       └── README.md                            NEW
│
├── styles/
│   ├── README.md                                NEW — governance, cascade order
│   │
│   ├── tokens/
│   │   ├── primitive.css                        NEW — Layer 1
│   │   ├── semantic.css                         NEW — Layer 2
│   │   ├── density-compact.css                  NEW
│   │   └── density-comfortable.css              NEW
│   │
│   ├── base/
│   │   ├── reset.css                            NEW
│   │   ├── fonts.css                            NEW — @font-face Inter base64
│   │   ├── typography.css                       NEW
│   │   └── global.css                           NEW
│   │
│   ├── chrome/
│   │   ├── shell-bar.css                        NEW
│   │   ├── sidebar.css                          NEW
│   │   ├── page-grid.css                        NEW
│   │   ├── splash.css                           NEW
│   │   └── footer.css                           NEW
│   │
│   ├── components/
│   │   ├── button.css                           NEW
│   │   ├── input.css                            NEW
│   │   ├── select.css                           NEW
│   │   ├── checkbox-radio.css                   NEW
│   │   ├── toggle.css                           NEW
│   │   ├── badge.css                            NEW
│   │   ├── card.css                             NEW
│   │   ├── stat-card.css                        NEW
│   │   ├── table.css                            NEW
│   │   ├── tabs.css                             NEW
│   │   ├── dropdown.css                         NEW
│   │   ├── form-group.css                       NEW
│   │   ├── divider.css                          NEW
│   │   ├── skeleton.css                         NEW
│   │   ├── empty-state.css                      NEW
│   │   ├── awm-modal.css                        NEW (refactored)
│   │   ├── awm-toast.css                        NEW (refactored)
│   │   └── awm-save-badge.css                   NEW (refactored)
│   │
│   └── print/
│       └── print.css                            NEW
│
└── scripts/
    ├── README.md                                NEW
    ├── utilities/
    │   ├── ls-wrapper.js                        NEW (extracted v9+)
    │   ├── esc-html.js                          NEW (extracted v8+)
    │   └── date-utc.js                          NEW (shell bar clock)
    ├── awm-modal.js                             NEW (extracted v8+)
    ├── awm-toast.js                             NEW (extracted v6+)
    ├── awm-save-badge.js                        NEW (extracted v6+)
    └── awm-contacts.js                          NEW (extracted v14-v19 COE)
```

### 6.2 Cascade order (determinística)

O `{{DS_CSS}}` é um blob único que o `build.py` concatena na seguinte ordem e injecta num só `<style>` no `<head>` do portal source. **Crítico para reproduzibilidade e para evitar conflitos de specificity.**

```
1. tokens/primitive.css
2. tokens/semantic.css
3. tokens/density-{compact|comfortable}.css   (só UM, escolhido pelo build)
4. base/reset.css
5. base/fonts.css                              (@font-face declarations)
6. base/typography.css
7. base/global.css
8. chrome/*.css                                (alfabética)
9. components/*.css                            (alfabética)
10. print/print.css                            (último)
```

#### Coexistência com CSS legado durante a migração (Fases 1-4)

Durante as Fases 1-4 o portal source ainda contém o seu CSS monolítico original (incluindo `:root { --dark-blue, --medium-blue, ... }` existentes) **em paralelo** com o `{{DS_CSS}}` injectado. Regras determinísticas para esta coexistência:

- **Posicionamento no HTML**: o `<style>` do `{{DS_CSS}}` é o **primeiro** `<style>` no `<head>`, **antes** do `<style>` legado do source. Isto faz o legado ganhar por ordem em caso de empate de specificity, preservando o comportamento visual do portal para componentes **ainda não migrados**.
- **Namespace `--ds-*`**: durante a transição, os tokens do DS usam o prefixo `--ds-*` (ver Secção 7) para não colidirem com `--dark-blue`, `--medium-blue` existentes.
- **Migração componente a componente**: quando um componente migra (ex: `button`), o CSS legado desse componente é **removido do source** e o componente passa a ser servido **exclusivamente pelo `{{DS_CSS}}`**. Não há duplicação nem override — há remoção limpa.
- **Fase 5**: depois de todos os componentes migrados, o `<style>` legado fica praticamente vazio (só com variáveis já não usadas) e é removido em commit atómico, junto com o rename do namespace `--ds-*` → `--*`.

**Regra**: componentes são **auto-contidos**. Dependências entre ficheiros de `components/` são proibidas. Cada componente selecciona os seus próprios tokens semânticos.

### 6.3 Per-portal config — novo `packages/portal-XXX/portal.config.json`

Introdução de fonte de verdade per-portal separada da config per-airport:

```json
// packages/portal-coe/portal.config.json
{
  "id": "portal-coe",
  "name": "Portal COE",
  "name_short": "COE",
  "tagline": "Centro de Operações de Emergência",
  "role": "Coordenador do Centro de Operações de Emergência",
  "density": "compact",
  "ui": {
    "show_utc_clock": true,
    "show_emergency_stopwatch": true,
    "show_occurrence_pill": true
  },
  "sections_enabled": ["dashboard", "ocorrencia", "contactos", ...]
}
```

```json
// packages/portal-ssci/portal.config.json
{
  "id": "portal-ssci",
  "name": "Portal SSCI",
  "density": "comfortable",
  "ui": {
    "show_utc_clock": true,
    "show_emergency_stopwatch": false,
    "show_occurrence_pill": false
  },
  ...
}
```

**Override opcional per-airport** em `config/airport-XXX.json`:
```json
{
  "airport": {...},
  "portals": {
    "portal-coe": { "density": "comfortable" }
  }
}
```

Resolução no build: `airport override` → `portal.config.json` → default `compact`.

### 6.4 Novos placeholders

**Convenção (alinhada com o `build.py` existente)**:

O `substitute_placeholders` do `build.py` actual usa duas mecânicas:
1. **Manual replacement** — blobs grandes de asset que são substituídos em linha por uma string: convenção `{{UPPER_SNAKE_CASE}}` (ex: `{{CONTACTS_JSON}}`, `{{VERSION}}`, `{{BUILD_DATE}}`)
2. **Flatten-based** — campos aninhados de um dict de config, achatados por `_flatten_dict` com separador `.` e uppercase: convenção `{{PARENT.CHILD}}` (ex: `{{AIRPORT.NAME}}`, `{{AIRPORT.OACI}}`)

Os novos placeholders seguem a mesma convenção conforme o tipo:

**Manual replacement** (blobs de asset/código, inserção directa):
| Placeholder | Conteúdo | Localização |
|---|---|---|
| `{{DS_FONTS_CSS}}` | `@font-face` Inter base64 | Topo do `<style>` principal |
| `{{DS_CSS}}` | Todo o CSS do DS concatenado em cascade order | Único `<style>` no `<head>` |
| `{{DS_JS}}` | Utilities + awm-* concatenados | Primeiro `<script>` no body |
| `{{ICON_SPRITE}}` | SVG sprite com `<symbol>`s | Primeiro elemento do `<body>`, hidden |
| `{{LOGO_SGA_MARK}}` | SVG inline do símbolo | Substitui referências no source |
| `{{LOGO_SGA_FULL}}` | SVG inline do lockup | Usado no splash |
| `{{BUILD_TIMESTAMP}}` | ISO timestamp do build | Footer, splash |

**Flatten-based** (do novo `portal.config.json`, injectado no `context` passado a `substitute_placeholders` com chave `portal`, gera placeholders `{{PORTAL.*}}`):
| Placeholder | Vem de | Exemplo |
|---|---|---|
| `{{PORTAL.ID}}` | `portal.config.json::id` | `portal-coe` |
| `{{PORTAL.NAME}}` | `portal.config.json::name` | `Portal COE` |
| `{{PORTAL.NAME_SHORT}}` | `portal.config.json::name_short` | `COE` |
| `{{PORTAL.TAGLINE}}` | `portal.config.json::tagline` | `Centro de Operações de Emergência` |
| `{{PORTAL.ROLE}}` | `portal.config.json::role` | `Coordenador do Centro de Operações de Emergência` |
| `{{PORTAL.DENSITY}}` | resolvido (airport override → portal.config.json → default) | `compact` ou `comfortable` |

Dentro do atributo `<html data-density="{{PORTAL.DENSITY}}">` o valor final escolhido é usado directamente.

### 6.5 Build pipeline — mudanças nos `build.py`

**Importante**: existem **dois** `build.py` independentes, um em `packages/portal-coe/scripts/build.py` e outro em `packages/portal-ssci/scripts/build.py`. As mudanças descritas abaixo têm que ser aplicadas a ambos, em paralelo, preservando a assinatura existente.

**Assinatura real actual** (não alterar — preserva compatibilidade com `scripts/build-all.py`):
```python
def build(
    source_path: Path,
    config_path: Path,
    output_path: Path,
    validate: bool = True,
) -> int:
```

Funções novas a adicionar (idealmente num módulo partilhado — ver nota abaixo):
- `compile_design_system_css(shared_root: Path, density: str) -> str` — lê ficheiros na cascade order e concatena
- `inline_font_face(woff2_path: Path) -> str` — base64 encode + template `@font-face`
- `compile_design_system_js(shared_root: Path) -> str` — concatena `utilities/*.js` + `awm-*.js`
- `load_portal_config(portal_config_path: Path) -> dict` — carrega `packages/portal-XXX/portal.config.json`
- `resolve_density(airport: dict, portal_config: dict, default: str = "compact") -> str` — resolve override chain

**Refactoring opcional mas recomendado**: extrair estas funções partilhadas para um novo módulo `scripts/ds_build_helpers.py` (na raiz do monorepo), importado pelos dois `build.py`, para evitar duplicação. Decisão deferida para a Fase 0 durante a implementação.

Fluxo actualizado dentro da função `build()` existente (pseudocódigo, a integrar com a função actual):

```python
def build(source_path, config_path, output_path, validate=True):
    # Existing
    version = read(REPO_ROOT / "VERSION")
    airport = json.loads(config_path.read_text(encoding="utf-8"))

    # NEW: portal config + density resolution
    portal_config_path = source_path.parent.parent / "portal.config.json"
    portal_config = load_portal_config(portal_config_path)
    density = resolve_density(airport, portal_config)

    # NEW: compile design system artefacts
    shared_root = REPO_ROOT / "shared"
    ds_css = compile_design_system_css(shared_root / "styles", density)
    ds_fonts_css = inline_font_face(shared_root / "assets" / "fonts" / "Inter-VariableFont.woff2")
    ds_js = compile_design_system_js(shared_root / "scripts")
    icon_sprite = (shared_root / "assets" / "icons" / "sprite.svg").read_text(encoding="utf-8")
    logo_mark = (shared_root / "assets" / "logo-sga-mark.svg").read_text(encoding="utf-8")
    logo_full = (shared_root / "assets" / "logo-sga-full.svg").read_text(encoding="utf-8")

    # Read source HTML (existing)
    html = source_path.read_text(encoding="utf-8")

    # NEW: manual blob placeholders (same mechanism as {{CONTACTS_JSON}})
    html = html.replace("{{DS_FONTS_CSS}}", ds_fonts_css)
    html = html.replace("{{DS_CSS}}", ds_css)
    html = html.replace("{{DS_JS}}", ds_js)
    html = html.replace("{{ICON_SPRITE}}", icon_sprite)
    html = html.replace("{{LOGO_SGA_MARK}}", logo_mark)
    html = html.replace("{{LOGO_SGA_FULL}}", logo_full)
    html = html.replace("{{BUILD_TIMESTAMP}}", datetime.now(UTC).isoformat())

    # Existing: substitute_placeholders handles flatten-based from airport config
    # NEW: include portal config under key "portal" to generate {{PORTAL.*}} placeholders
    context = {**airport, "portal": {**portal_config, "density": density}}
    html = substitute_placeholders(html, context)

    # Existing: inline base64 binaries (PDFs, maps)
    html = inline_base64_binaries(html, source_path.parent)

    # Write dist (existing)
    output_path.write_text(html, encoding="utf-8")

    if validate:
        validate_inline_scripts(html, output_path)
```

### 6.6 Boundaries de responsabilidade

| Mudança | Onde vai |
|---|---|
| Nova cor de status, ajuste de contraste | `shared/styles/tokens/semantic.css` |
| Novo ícone | `shared/assets/icons/sources/icon-X.svg` → regenerar sprite |
| Novo componente Tier 1-3 | `shared/styles/components/<name>.css` |
| Mudança específica do COE/SSCI | `packages/portal-XXX/src/` |
| Nova entidade de contacto | `config/airport-XXX.json` |
| Novo portal | `packages/portal-XXX/` + `portal.config.json` |

**Regra de ouro**: nenhum ficheiro em `shared/` pode ter código específico de um portal. Se acontecer, é bug do DS e deve ser refactored.

---

## 7. Migration strategy & validation

### 7.1 Princípios

- **Nunca ficar com um portal partido entre commits** — cada commit produz `.html` funcional
- **Foundation antes de componentes** — tokens, fontes, reset, typography primeiro, verificados inertes
- **COE primeiro, SSCI depois** — COE é maior e mais complexo, lições fluem para o SSCI

### 7.2 Estratégia: migração faseada com namespace de transição `--ds-*`, removido no final

Esta é a alternativa escolhida ao *big-bang*. O namespace `--ds-*` durante a transição permite que os tokens novos coexistam com os antigos (`--dark-blue`, `--medium-blue`) sem colisão. O rename para `--*` sem prefixo acontece na Fase 5 quando tudo estiver estável.

### 7.3 Fases

#### Fase 0 — Setup não-destrutivo (zero mudança visual)
- Criar todos os ficheiros em `shared/styles/tokens/`, `shared/styles/base/`, `shared/assets/icons/`, `shared/assets/fonts/`
- `build.py` aprende a ler os novos ficheiros mas **ainda não injecta**
- Verificar: `python scripts/build-all.py` produz HTMLs **byte-a-byte idênticos**
- Commit: `feat(ds): scaffold shared/ design system files (dormant)`

#### Fase 1 — Tokens injectados mas dormentes (zero mudança visual)
- `{{DS_CSS}}` activo, contém apenas tokens + base (não components)
- Tokens namespaced `--ds-*`
- Inter woff2 base64 embebido — `.html` cresce ~200 KB
- Sprite SVG inline no `<body>` (invisível)
- Verificar: Chrome/Edge/Firefox, render idêntico, sem erros de console
- Commit: `feat(ds): activate dormant token layer in both portals`

#### Fase 2 — Migrar componentes no COE (um por um)

Ordem (simplicidade → risco crescente):

| # | Componente | Risco |
|---|---|---|
| 1 | button (+ variants) | Baixo |
| 2 | badge | Baixo |
| 3 | form-group / input | Médio |
| 4 | card + stat-card | Médio |
| 5 | table | Médio |
| 6 | tabs | Baixo |
| 7 | dropdown / menu | Baixo |
| 8 | awm-modal | **Médio-alto** (risco de partir focus trap) |
| 9 | awm-toast | Médio |
| 10 | awm-save-badge | Baixo |
| 11 | skeleton + empty-state | Baixo (novos) |

Cada item = **um commit separado**. Processo: reescrever em `shared/styles/components/`, substituir no portal source, build, smoke test da secção afectada.

#### Fase 3 — Chrome no COE (visualmente a mudança maior)
- Criar `shared/styles/chrome/*.css` completos
- Substituir HTML da header + sidebar no COE source pelo novo shell bar + sidebar light
- Preservar JS de navegação (`data-section`, event handlers)
- Splash screen + print stylesheet em commits separados
- Commits:
  - `feat(coe): replace header+sidebar with design system shell`
  - `feat(coe): add splash screen with DREA branding`
  - `feat(coe): add print stylesheet with document header`

#### Fase 4 — Repetir Fases 2 e 3 para o SSCI
Mesma ordem, mesmo processo. O SSCI hoje não tem `awm-contacts.js` ainda — a migração de chrome arrasta a extracção de contactos do SSCI para consumir `config/airport-XXX.json` via o mesmo mecanismo que o COE.

#### Fase 5 — Remover namespace e limpar legacy
- Rename global `--ds-*` → `--*`
- Remover `:root { --dark-blue, --medium-blue, ... }` residual
- Remover CSS legacy comentado
- Remover `logo-sga-white.png`
- Remover ícones unicode substituídos por SVG sprite
- Commits:
  - `refactor(ds): drop --ds-* namespace, finalize tokens`
  - `chore(ds): remove legacy CSS and unused assets`

#### Fase 6 — Documentação e release
- `shared/styles/README.md` — governance
- `shared/scripts/README.md` — governance
- `docs/design-system-guide.md` — guia completo do DS
- Update `docs/ARCHITECTURE.md` com secção Design System
- Update `docs/CHANGELOG.md`
- Bump `VERSION` → `2.1.0-alpha.1`
- Commit final: `release: Portal DREA v2.1.0-alpha.1 — Design System SGA`

### 7.4 Isolamento: git worktree

```bash
git worktree add ../Portal_DREA-ds feat/design-system
```

Todo o trabalho de Fases 0-6 no worktree. `main` permanece em `v2.0.0-beta.1`, disponível para hotfixes. Merge para `main` apenas após Fase 6 completa e validada.

### 7.5 Validação por commit (5 níveis)

**Nível 1 — Automático**:
- `python scripts/build-all.py` → exit 0
- Validação sintáctica das secções script (existente)
- Tamanho dos HTMLs dentro de ±5% vs commit anterior, **excepto deltas intencionais pré-declarados**:
  - **Fase 1** tem delta intencional esperado: **+200 KB** por portal (Inter Variable woff2 em base64) + **~15 KB** por sprite SVG. No COE (~4 MB) isto é ~5.5% → roça o limite. No SSCI (~1.5 MB) é ~14% → excede largamente. A verificação nessa fase específica **passa** se o delta estiver dentro de `+250 KB` absoluto (não percentual) para cada portal.
  - **Fases 2-4** espera-se delta neutro ou ligeiramente negativo (componentes migrados removem CSS legado equivalente — net zero ou shrink).
  - **Fase 5** espera-se shrink: remoção de `--dark-blue`, CSS comentado, `logo-sga-white.png` → expected ~-20 KB por portal.
  - Qualquer commit fora destes padrões sem delta pré-declarado é um **warning** que requer inspecção manual antes de avançar.

**Nível 2 — Smoke test manual**:
- Abrir `dist/Portal_COE_AWM.html` em Chrome
- Login, navegar secções (Dashboard, Ocorrência, Contactos, Verif Mensal, Mapas, Fluxogramas, Config)
- Abrir/fechar modal (ESC)
- Disparar toast, ver dismiss
- Editar contacto, guardar, ver save-badge
- Repetir para `dist/Portal_PSCI_AWM.html`

**Nível 3 — Cross-browser** (fim de fase):
- Edge e Firefox
- Render de Inter, tabular-figures, focus ring
- Modals (focus trap em Firefox é historicamente mais frágil)

**Nível 4 — Print preview** (fim de fase):
- Chrome Save-as-PDF
- Print header aparece, shell bar + sidebar desaparecem
- Paginação de tabela longa (Verif Mensal 26 entidades)

**Nível 5 — WCAG** (fim de fase):
- axe DevTools em ≥3 secções (dashboard, form, table)
- 0 violations serious/critical
- Contraste manual em elementos duvidosos

### 7.6 Rollback

- Cada fase = conjunto de commits atómicos
- Falha de fase inteira: `git reset --hard <commit-anterior>`
- Falha de componente: `git revert <sha>`
- Worktree isolado → `main` nunca afectado
- `dist/` gitignored → rebuilds reproduzíveis

### 7.7 Definição de "feito"

1. Ambos os portais usam o DS completo em `shared/`
2. `--ds-*` namespace removido
3. `python scripts/build-all.py` sem warnings
4. Smoke test em Chrome + Edge + Firefox passa
5. Print preview produz PDFs correctos
6. axe DevTools → 0 violations críticas
7. `shared/styles/README.md` e `docs/design-system-guide.md` completos
8. `VERSION` e `CHANGELOG.md` actualizados
9. Merge do worktree de volta ao `main`
10. Tag `v2.1.0-alpha.1`

### 7.8 Scope out (recapitulação)

- ❌ Extrair componentes de domínio (flow-node, cronómetro, inspecção VCI) para `shared/`
- ❌ Refactoring de estrutura de secções do COE ou SSCI
- ❌ Adicionar novos portais (preparação só)
- ❌ Mudar schema de dados
- ❌ Migração para Tauri (Fase 2 do projecto, separada)
- ❌ Testes E2E automatizados

---

## 8. Open questions & deferred decisions

Items que surgiram durante o brainstorming e ficaram para decisão posterior (não são bloqueantes para a implementação):

1. **Cores de categoria SEG ORDEM (castanho) e EXTERNA-EMG (roxo)** — escolhi `#5d4037` e `#6a1b9a` por necessidade de diferenciação visual entre 6 categorias. O utilizador não validou especificamente estas duas cores — podem ser ajustadas na fase de implementação se houver convenção SGA existente.

2. **Heroicons Outline vs Phosphor vs Lucide vs desenho à mão** — escolhi Heroicons por MIT license e pragmatismo. Decisão pode ser ajustada na Fase 0 quando o sprite for realmente criado.

3. **Script auxiliar `scripts/build-sprite.py`** — usar ou montar sprite à mão? Deferido para decisão durante a implementação.

4. **Pill "ocorrência activa" no SSCI** — o SSCI não tem um estado equivalente hoje. Decisão: não adicionar pill no SSCI na v1. Pode ser "inspecção VCI em curso" na v2 se fizer sentido operacional.

5. **Footer é fixed-bottom ou scroll-bottom** — escolhi scroll-bottom por default. Pode ser mudado sem afectar tokens.

6. **Skeleton loading: só para tabelas ou também para cards** — Deferido para a fase de implementação.

7. **Empty state: ilustrações SVG próprias ou reutilizar ícones** — ilustrações próprias dariam mais identidade mas custam mais trabalho. Decisão deferida.

---

## 9. Referências

- [Pesquisa de mercado completa](../research/2026-04-11-design-system-market-research.md)
- [Portal DREA ARCHITECTURE.md](../../ARCHITECTURE.md)
- [Portal DREA CHANGELOG.md](../../CHANGELOG.md)
- SAP Fiori Quartz Light — https://experience.sap.com/fiori-design-web/
- IBM Carbon Design System — https://carbondesignsystem.com/
- GitHub Primer — https://primer.style/
- USWDS — https://designsystem.digital.gov/
- Atlassian Design System — https://atlassian.design/
- Inter (rsms) — https://rsms.me/inter/
- Heroicons — https://heroicons.com/
- WCAG 2.1 AA — https://www.w3.org/TR/WCAG21/

---

## 10. Aprovações

| Stakeholder | Papel | Data | Status |
|---|---|---|---|
| Marcio Sager | Consultor SGSO / autor do Portal DREA | 2026-04-11 | ✅ Aprovado (brainstorming session) |
| spec-document-reviewer | Subagent validation | 2026-04-11 | ✅ Aprovado com recomendações (5 issues fixed em v1.1) |
| Marcio Sager | User final review pós-fixes | 2026-04-11 | ✅ Aprovado — transição para writing-plans |
