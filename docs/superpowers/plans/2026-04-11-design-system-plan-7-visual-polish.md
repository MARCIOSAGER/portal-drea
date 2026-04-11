# Design System SGA — Plan 7: Visual Polish (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` (ou `superpowers:subagent-driven-development` se houver paralelismo útil) para implementar este plano task-by-task. Os passos usam checkbox (`- [ ]`) para tracking.

**Goal:** Subir a fasquia visual do Portal DREA aplicando o Design System SGA às secções de conteúdo legadas — dashboard SSCI (6 KPIs em row-grouped progress gauges) e formulário de ocorrência COE (two-col + sticky timer) — e entregar a release `v2.2.0-alpha.1`. A fundação DS existe desde v2.1.0-alpha.1; o Plan 7 **aplica** essa fundação ao conteúdo que ficou por migrar.

**Architecture:** Aditivo. Estende `shared/styles/tokens/` (elevation, status quad, motion, pill, gauge, mono font) e adiciona 6 componentes novos em `shared/styles/components/` (`stat-card-gauge`, `state-pulse`, `dash-section`, `form-banner`, `form-two-col`, `sticky-timer-card`). Refactor mínimo em `sidebar.css` (novo modifier `.nav-btn--pill`) e em `form-group.css` (novo modifier `.form-group--numeric`). Embebe `JetBrainsMono[wght].woff2` em base64 via helper novo no `ds_build_helpers.py`. Reskinnings mínimos em markup no source HTML dos dois portais — JS-load-bearing IDs/classes preservados. Tudo build-time, zero runtime deps, single-file HTML mantido.

**Tech Stack:** Python 3.8+ (`ds_build_helpers.py`), pytest (testes dos helpers novos), vanilla CSS (tokens + componentes), vanilla JS (adaptação mínima de `updateDashboardSSCI()` e criação de um chronometer minimal para `sticky-timer-card`), git worktree + tag annotated (release), Markdown (Keep a Changelog).

**Source spec:** [`docs/superpowers/specs/2026-04-11-plan-7-visual-polish-design.md`](../specs/2026-04-11-plan-7-visual-polish-design.md) (aprovado 2026-04-11 após 8 iterações no visual companion + spec-document-reviewer subagent).

**Invariant this plan must preserve:** depois de `python scripts/build-all.py` com o Plan 7 completo, abrir `dist/Portal_COE_AWM.html` e `dist/Portal_PSCI_AWM.html` em Chrome tem que mostrar:
1. Dashboard SSCI reskinned conforme o mockup `synthesis.html` do brainstorm (2 secções × 3 stat-card-gauge cada, com estados OK/unknown/critical funcionais)
2. Form COE `#emgFormBlock` reskinned para two-col + sticky timer card com cronómetro live
3. Sidebar nav items como pill active SGA sólida
4. **Zero regressões** em funcionalidade: todos os fluxos existentes (navegação, cronómetro COE legacy, contactos, checklists, form save, localStorage) continuam a funcionar exactamente como na v2.1.0-alpha.1
5. Preserved JS-load-bearing contracts: `#clockDisplay`, `#headerUTC`, `#headerDate`, `#operatorBadge`, `#psci-turno`, `.awm-modal*`, `.awm-toast*`, `.uxp-savebadge*`, `.contact-card*`, `.alarm-card*`, `.cr-chip`, `.tab-content`, `openSection(id, event)`, `updateDashboardSSCI()`, `cfgApplyToPortal()`, `window.notify()`, `window.awmAlert()`, `window.lsGet/lsSet`, `window.awmContacts.*`
6. `pytest tests/ -q` → ≥45 passed (v2.1.0-alpha.1 baseline)
7. `python scripts/build-all.py` → exit 0 ambos os portais
8. `axe DevTools` scan em 3 secções por portal → zero critical/serious violations

**Out of scope for Plan 7** (explicitamente rejeitado no brainstorm):

- ❌ COE dashboard (não havia screenshot nem queixa)
- ❌ Contacts cards redesign
- ❌ Fluxogramas redesign
- ❌ Print stylesheets alteration (além do que já existe após logo commit)
- ❌ Responsive breakpoints abaixo de 600px (tablet/mobile deferred)
- ❌ Charts de tendência (sparklines, line charts) — hipotético, deferred
- ❌ Dark mode (rejeitado desde Plan 1)
- ❌ Tauri desktop installer (Fase 2)
- ❌ Novos portais (SOA, AVSEC, DIRECÇÃO)
- ❌ Migração completa do body typography legacy → Inter
- ❌ Remoção do legacy `:root { --dark-blue, ... }`
- ❌ Shell bar mark-only (logo full está OK à escala 30px)

---

## Fact sheet — estado inicial (baseline 2026-04-11 contra commit `6cd3138`)

### Ficheiros que já existem e não são tocados pelos tasks core

- `shared/styles/tokens/primitive.css` — 114 linhas, tokens v2.1 (será **estendido** na Task 2)
- `shared/styles/tokens/semantic.css` — 80 linhas, tokens v2.1 (estendido na Task 2)
- `shared/styles/tokens/density-compact.css` — tokens por portal
- `shared/styles/tokens/density-comfortable.css` — idem
- `shared/styles/base/fonts.css` — Inter Variable embed (será **estendido** na Task 11 com JetBrains Mono)
- `shared/styles/base/global.css` — reset + global rules (keyframes adicionadas na Task 4)
- `shared/styles/chrome/shell-bar.css` — recém-modificado no commit 6cd3138 (logo real)
- `shared/styles/chrome/sidebar.css` — será refactored na Task 9
- `shared/styles/components/form-group.css` — será estendido na Task 10
- `shared/styles/components/card.css`, `button.css`, etc. — inalterados
- `shared/styles/print/print.css` — inalterado (logo já lá desde commit 3a4122b)
- `scripts/ds_build_helpers.py` — estendido na Task 1 com helper para JetBrains Mono

### Ficheiros a criar (6 componentes novos + 1 placeholder)

```
shared/styles/components/
├── stat-card-gauge.css          (Task 3)
├── state-pulse.css              (Task 4)
├── dash-section.css             (Task 5)
├── form-banner.css              (Task 6)
├── form-two-col.css             (Task 7)
└── sticky-timer-card.css        (Task 8)

shared/assets/fonts/
└── JetBrainsMono-Variable.woff2 OR JetBrainsMono-{Regular,Bold}.woff2  (Task 0 decides)
```

### JavaScript hooks preservados nos sources HTML (sagrados)

Nenhum destes pode ser renomeado ou removido. Qualquer task que toque nos source HTMLs audita primeiro:

**SSCI** (`Portal_PSCI_AWM.source.html`):
- `#psci-clock`, `#psci-turno` — id preservados no shell bar
- `updateClock()` — JS que escreve no shell bar
- `updateDashboardSSCI()` — JS que popula os KPIs (será **adaptado** na Task 15)
- `openSection(id, event)` — 2-arg contract preservado
- `window.PSCI_CFG.*`, `localStorage.psci_awm_config`

**COE** (`Portal_COE_AWM.source.html`):
- `#clockDisplay`, `#headerUTC`, `#headerDate`, `#operatorBadge` — ids preservados no shell bar
- `updateHeaderClock()` — JS que escreve no shell bar
- `openSection(id, event)` — 2-arg contract preservado
- `#emgFormBlock` — id preservado no COE form (será **reskinned**, não removido)
- `cfgApplyToPortal()` — escreve em `.header-title-small` (preservado como dual class)
- `window.notify()`, `window.awmAlert()`, `window.lsGet/lsSet`, `window.awmContacts.*`
- `.awm-modal*`, `.awm-toast*`, `.uxp-savebadge*`, `.contact-card*`, `.alarm-card*`, `.cr-chip`, `.tab-content`

### Test baseline

- **45 tests** em `tests/` passing (30 `test_ds_build_helpers.py` + 15 `test_rename_ds_namespace.py`)
- Plan 7 adiciona **1-3 tests** em `test_ds_build_helpers.py` para o helper novo de JetBrains Mono
- **Target final**: 46-48 tests passing

### Brainstorm visual references

Mockups aprovados pelo consultor vivem em:
```
d:/VSCode_Claude/03-Resende/Portal_DREA/.superpowers/brainstorm/6688-1775939283/
├── visual-direction.html       Q1 — Executive Clean ✓
├── color-identity.html         Q2 — Híbrido ✓
├── stat-card-treatment.html    Q3 — Progress gauge ✓
├── dashboard-layout.html       Q4 — Row-based grouped ✓
├── state-treatment.html        Q5 — Pulsed real-time ✓
├── form-treatment.html         Q6 — Two-col + sticky timer ✓
├── synthesis.html              síntese aprovada ✓
└── sidebar-refine.html         Q6b — Pill active SGA ✓
```

O `synthesis.html` é a **referência canónica** contra a qual o Plan 7 é visualmente validado.

---

## File structure — what will be touched

Antes das tasks, aqui está o mapa do que é criado vs modificado:

### Create (8 files)

```
shared/styles/components/stat-card-gauge.css    (Task 3, ~100 lines)
shared/styles/components/state-pulse.css        (Task 4, ~60 lines)
shared/styles/components/dash-section.css       (Task 5, ~30 lines)
shared/styles/components/form-banner.css        (Task 6, ~40 lines)
shared/styles/components/form-two-col.css       (Task 7, ~25 lines)
shared/styles/components/sticky-timer-card.css  (Task 8, ~80 lines)
shared/assets/fonts/JetBrainsMono-Variable.woff2  (Task 0/11, binary)
docs/releases/v2.2.0-alpha.1.md                 (Task 22, ~150 lines)
```

### Modify (11 files)

```
shared/styles/tokens/primitive.css                (Task 2, +30 lines)
shared/styles/tokens/semantic.css                 (Task 2, +40 lines)
shared/styles/base/fonts.css                      (Task 11, +8 lines — @font-face JetBrains Mono)
shared/styles/base/global.css                     (Task 4, +30 lines — @keyframes pulse)
shared/styles/chrome/sidebar.css                  (Task 9, +50 / −10)
shared/styles/components/form-group.css           (Task 10, +10 lines — numeric modifier)
scripts/ds_build_helpers.py                       (Task 1, +20 lines)
tests/test_ds_build_helpers.py                    (Task 1, +30 lines)
packages/portal-coe/scripts/build.py              (Task 11, +10 lines — jetbrains mono marker)
packages/portal-ssci/scripts/build.py             (Task 11, +10 lines — mirror)
packages/portal-coe/src/Portal_COE_AWM.source.html  (Task 13+14+16+17, ~150 lines markup)
packages/portal-ssci/src/Portal_PSCI_AWM.source.html (Task 12+15+17, ~150 lines markup)
VERSION                                            (Task 19, 1 line)
docs/CHANGELOG.md                                  (Task 21, ~80 lines)
README.md                                          (Task 23, ~5 lines)
docs/design-system-guide.md                        (Task 24, ~80 lines)
docs/ARCHITECTURE.md                               (Task 25, ~20 lines)
```

### Delete (0 files)

Plan 7 não apaga nada. O legacy `.dash-card` e `.occ-dash-card` no source HTML são substituídos markup-level pelos novos, não apagados de um ficheiro CSS separado (já não existe ficheiro legacy — tudo legacy está inline no source HTML desde Plans 3-5).

---

## Task 0: Prerequisites — worktree + JetBrains Mono download + font format decision

### Purpose

Assegurar que o ambiente de execução do Plan 7 está consistente. O worktree já foi criado em `../Portal_DREA-plan7` pelo agente de writing. Esta task é uma série de verificações + a **decisão crítica** do formato do JetBrains Mono (variable vs 2 estáticos, spec § 6.1).

### Steps

- [ ] **Step 1: Confirm worktree**
  ```bash
  cd d:/VSCode_Claude/03-Resende/Portal_DREA-plan7
  rtk git status
  # Expected: On branch feat/plan-7-visual-polish, clean
  rtk git log --oneline -5
  # Expected: 6cd3138 feat(brand): use real SGA logo in shell bar ...
  ```

- [ ] **Step 2: Baseline green gate**
  ```bash
  rtk python scripts/build-all.py
  rtk python -m pytest tests/ -q
  ```
  Expected: ambos os portais build OK, 45 tests passing.

- [ ] **Step 3: Baseline screenshots** (optional visual reference)
  Abrir `dist/Portal_COE_AWM.html` e `dist/Portal_PSCI_AWM.html` em Chrome. Fazer screenshot da SSCI dashboard e do COE form `#emgFormBlock` para referência "antes". Salvar em `d:/tmp/plan7-baseline-ssci-dashboard.png` e `d:/tmp/plan7-baseline-coe-form.png`.

- [ ] **Step 4: Download JetBrains Mono**
  ```bash
  # Criar directoria
  mkdir -p d:/tmp/plan7-jetbrains
  cd d:/tmp/plan7-jetbrains

  # Descobrir a última versão estável via API (evita hardcoded version)
  LATEST=$(curl -s https://api.github.com/repos/JetBrains/JetBrainsMono/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
  echo "Latest JetBrains Mono release: $LATEST"

  # Download do zip da release identificada
  curl -L -o JetBrainsMono-latest.zip "https://github.com/JetBrains/JetBrainsMono/releases/download/${LATEST}/JetBrainsMono-${LATEST#v}.zip"

  # Descompactar
  unzip -q JetBrainsMono-latest.zip

  # Listar os woff2 disponíveis (path depende da versão — pode ser fonts/webfonts/ ou webfonts/)
  find . -name "*.woff2" | head -20
  ```

  Expected:
  - `JetBrainsMono[wght].woff2` (variable, ~130 KB) — **Preferência A**
  - `JetBrainsMono-Regular.woff2` + `JetBrainsMono-Bold.woff2` (estáticos, ~29 KB cada) — **Preferência B**

  (Se `curl` falhar por network restrictions, ir directamente a https://github.com/JetBrains/JetBrainsMono/releases/latest no browser, fazer download manual e copiar o ficheiro para `d:/tmp/plan7-jetbrains/`.)

- [ ] **Step 5: Decision — Preferência A (variable) vs Preferência B (dois estáticos)**
  ```bash
  # Ver os tamanhos reais
  ls -la d:/tmp/plan7-jetbrains/fonts/webfonts/JetBrainsMono*.woff2
  ```
  Expected output (exemplo hipotético):
  ```
  JetBrainsMono[wght].woff2         130000  (variable)
  JetBrainsMono-Regular.woff2        28000
  JetBrainsMono-Bold.woff2           29000
  ```

  **Regra de decisão**:
  - Se `variable total < 60 KB`: **Preferência A** (variable)
  - Caso contrário: **Preferência B** (dois estáticos, total ~58 KB)

  Na prática o variable é ~130 KB, então vai ser **Preferência B** confirmada. Mas Step 5 existe para o caso do JetBrains publicar uma versão slim no futuro.

  Registar a decisão como comentário no topo do `shared/styles/base/fonts.css` para histórico.

- [ ] **Step 6: Copy chosen files to shared/assets/fonts/**
  ```bash
  # Preferência B (expected):
  cp d:/tmp/plan7-jetbrains/fonts/webfonts/JetBrainsMono-Regular.woff2 shared/assets/fonts/
  cp d:/tmp/plan7-jetbrains/fonts/webfonts/JetBrainsMono-Bold.woff2 shared/assets/fonts/

  # Verificar
  ls -la shared/assets/fonts/
  ```
  Expected: 3 ficheiros (`Inter-VariableFont.woff2` legacy + `JetBrainsMono-Regular.woff2` + `JetBrainsMono-Bold.woff2`).

- [ ] **Step 7: Commit**
  ```bash
  rtk git add shared/assets/fonts/JetBrainsMono-Regular.woff2 shared/assets/fonts/JetBrainsMono-Bold.woff2
  # NOTE: replace <VERSION> below with the actual $LATEST tag
  # discovered in Step 4 (e.g., "v2.304" or whatever is current)
  rtk git commit -m "$(cat <<EOF
  chore(fonts): add JetBrains Mono Regular + Bold woff2 (Plan 7 Task 0)

  JetBrains Mono ${LATEST} static weights (Regular 400 + Bold 700) for
  use as --font-mono-family in the DS. Total size ~58 KB for both.

  Decision: Preferência B over Preferência A (variable) because:
  - Variable woff2 file is ~130 KB, too heavy for our use
  - We only need 2 weights in practice (Regular + Bold)
  - 2 static files total ~58 KB, saving ~70 KB

  License: OFL-1.1 (SIL Open Font License), MIT-compatible.
  Source: https://github.com/JetBrains/JetBrainsMono/releases/tag/${LATEST}

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Task 0 completa quando os 2 ficheiros woff2 estão em `shared/assets/fonts/`, commitados, e baseline green gate verificado.

---

## Task 1: TDD — extend `ds_build_helpers.py` for JetBrains Mono embedding

### Purpose

O helper `encode_font_woff2_base64()` já é genérico e aceita qualquer `Path`. Esta task verifica que continua a funcionar para o JetBrains Mono woff2, e adiciona 2-3 tests focados em multi-font scenarios. Não há função nova — é uma expansão defensiva da suite de testes.

### Files

- Modify: `tests/test_ds_build_helpers.py` (+30 lines)

### Steps

- [ ] **Step 1: Write failing tests**

  Adicionar 3 novos tests em `tests/test_ds_build_helpers.py`, classe `TestEncodeFontWoff2Base64`:

  ```python
  def test_encodes_jetbrains_mono_regular(self, tmp_path):
      """JetBrains Mono Regular woff2 is valid base64-encodable."""
      # Simulate by writing a fake woff2 (real file will be validated in integration)
      fake = tmp_path / "JetBrainsMono-Regular.woff2"
      fake.write_bytes(b"wOF2" + b"\x00" * 100)  # woff2 signature + padding
      result = encode_font_woff2_base64(fake)
      assert result.startswith("d09G")  # "wOF2" base64-prefix
      assert len(result) > 0
      assert "=" in result or result[-1] != "="  # may or may not have padding

  def test_encodes_jetbrains_mono_bold(self, tmp_path):
      """JetBrains Mono Bold woff2 handled identically to Regular."""
      fake = tmp_path / "JetBrainsMono-Bold.woff2"
      fake.write_bytes(b"wOF2" + b"\xff" * 200)
      result = encode_font_woff2_base64(fake)
      assert len(result) > 100

  def test_multiple_fonts_independent(self, tmp_path):
      """Encoding different fonts yields different base64 outputs."""
      a = tmp_path / "a.woff2"
      b = tmp_path / "b.woff2"
      a.write_bytes(b"\x00\x01\x02\x03")
      b.write_bytes(b"\x04\x05\x06\x07")
      assert encode_font_woff2_base64(a) != encode_font_woff2_base64(b)
  ```

- [ ] **Step 2: Run tests — expected to PASS immediately**
  ```bash
  rtk python -m pytest tests/test_ds_build_helpers.py -v -k "encodes_jetbrains or multiple_fonts" 2>&1 | tail -10
  ```
  Expected: 3 passing. (O helper é genérico, os testes validam que ele continua a funcionar com novos ficheiros.)

- [ ] **Step 3: Run full suite — baseline green gate**
  ```bash
  rtk python -m pytest tests/ -q
  ```
  Expected: 48 passed (45 baseline + 3 novos).

- [ ] **Step 4: Commit**
  ```bash
  rtk git add tests/test_ds_build_helpers.py
  rtk git commit -m "$(cat <<'EOF'
  test(ds): extend encode_font_woff2_base64 tests for JetBrains Mono

  Adds 3 tests validating that the existing encode_font_woff2_base64()
  helper (generic Path-based) works correctly for:
  - JetBrains Mono Regular woff2 signature
  - JetBrains Mono Bold woff2 with different content
  - Multiple fonts yielding distinct base64 outputs

  No production code changes — the helper is already generic. These
  tests defensively lock in the "reuse for any woff2" contract before
  Plan 7 wires up the JetBrains Mono embedding in build.py.

  Test count: 45 → 48 passing.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: 48 tests passing, commit atomico.

---

## Task 2: Add new design tokens (primitive + semantic)

### Purpose

Adicionar os tokens novos ao DS: elevation scale (4 levels), status quad (critical/warning/normal/unknown), motion, pill active, gauge, mono typography. **Aditivo** — nenhum token existente é removido. Ficheiros alterados: `primitive.css` e `semantic.css`.

### Files

- Modify: `shared/styles/tokens/primitive.css` (+30 lines)
- Modify: `shared/styles/tokens/semantic.css` (+40 lines)

### Steps

- [ ] **Step 1: Extend `primitive.css`**

  Adicionar no fim do bloco `:root` (antes da linha `}`):

  ```css
  /* ---------- Plan 7: Elevation shadows (4-level scale, Dimensional Layering) ---------- */
  --shadow-elevation-1: 0 1px 2px rgba(9,30,66,0.06), 0 1px 3px rgba(9,30,66,0.04);
  --shadow-elevation-2: 0 2px 4px rgba(9,30,66,0.08), 0 4px 12px rgba(9,30,66,0.06);
  --shadow-elevation-3: 0 4px 8px rgba(9,30,66,0.12), 0 10px 24px rgba(9,30,66,0.10);
  --shadow-elevation-4: 0 8px 16px rgba(9,30,66,0.16), 0 24px 48px rgba(9,30,66,0.14);

  /* ---------- Plan 7: Status quad primitives ---------- */
  --green-600:         #22c55e;  /* status-normal gauge, pulse */
  --amber-500-bright:  #f59e0b;  /* status-warning pulse alias */
  --red-600:           #dc2626;  /* status-critical gauge, pulse */

  /* ---------- Plan 7: Typography — mono family ---------- */
  --font-mono-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Menlo', monospace;
  --font-mono-features: "tnum", "zero";  /* tabular numerals + slashed zero */
  ```

- [ ] **Step 2: Extend `semantic.css`**

  Adicionar no fim do bloco `:root` (antes da linha `}`):

  ```css
  /* ---------- Plan 7: Elevation aliases (override v2.1 placeholders) ---------- */
  --elevation-card:    var(--shadow-elevation-1);
  --elevation-hover:   var(--shadow-elevation-2);
  --elevation-overlay: var(--shadow-elevation-3);
  --elevation-modal:   var(--shadow-elevation-4);

  /* ---------- Plan 7: Status quad (monitoring-specific, distinct from v2.1 status-info/success/warning/alert/emergency) ---------- */
  /* status-normal (green): operacional */
  --status-normal-bg:            var(--green-100);
  --status-normal-border:        var(--green-600);
  --status-normal-fg:            var(--green-900);
  --status-normal-gauge:         var(--green-600);
  --status-normal-pulse:         var(--green-600);

  /* status-warning (amber): atenção — distinct from v2.1 --status-warning-emphasis
     which stays untouched. These -gauge/-pulse additions are the ones Plan 7
     components (stat-card-gauge, state-pulse) consume. The v2.1 -bg/-border/-fg
     are reused as-is (they already exist in v2.1 semantic.css). */
  --status-warning-gauge:        var(--amber-500-bright);
  --status-warning-pulse:        var(--amber-500-bright);

  /* status-unknown (gray): dados em falta, não registado ainda */
  --status-unknown-bg:           var(--neutral-subtle);
  --status-unknown-border:       var(--neutral-muted);
  --status-unknown-fg:           var(--neutral-fg-subtle);
  --status-unknown-gauge:        var(--neutral-muted);
  --status-unknown-pulse:        transparent;

  /* status-critical aliases (for gauge specifically — complements the existing v2.1 --status-alert-*) */
  --status-critical-bg:          #fef2f2;
  --status-critical-border:      var(--red-600);
  --status-critical-fg:          #991b1b;
  --status-critical-gauge:       var(--red-600);
  --status-critical-pulse:       var(--red-600);

  /* ---------- Plan 7: Motion tokens ---------- */
  --transition-hover:   120ms cubic-bezier(.2, 0, 0, 1);
  --transition-active:  80ms cubic-bezier(.2, 0, 0, 1);

  /* ---------- Plan 7: Pill active nav tokens ---------- */
  --pill-active-bg:     var(--brand-primary);       /* #004C7B */
  --pill-active-fg:     var(--white);
  --pill-active-icon:   var(--white);
  --pill-active-shadow: 0 2px 4px rgba(0,76,123,0.25);
  --pill-hover-bg:      #f1f5f9;
  --pill-hover-fg:      #0f172a;
  --pill-radius:        7px;

  /* ---------- Plan 7: Gauge tokens ---------- */
  --gauge-height:       4px;
  --gauge-bg:           #eef1f4;
  --gauge-radius:       2px;
  --gauge-fill-default: var(--brand-primary);
  --gauge-fill-ok:      var(--status-normal-gauge);
  --gauge-fill-warning: var(--status-warning-gauge);
  --gauge-fill-critical: var(--status-critical-gauge);
  --gauge-transition:   width 300ms cubic-bezier(.2, 0, 0, 1);

  /* ---------- Plan 7: Font family semantic aliases ---------- */
  --font-ui:         'Inter', -apple-system, 'Segoe UI', sans-serif;
  --font-numeric:    var(--font-mono-family);
  ```

- [ ] **Step 3: Build and verify**
  ```bash
  rtk python scripts/build-all.py 2>&1 | tail -5
  rtk python -m pytest tests/ -q
  ```
  Expected: ambos os portais build OK, 48 tests passing. **Zero diff visual** porque os novos tokens ainda não estão a ser consumidos — só existem.

- [ ] **Step 4: Commit**
  ```bash
  rtk git add shared/styles/tokens/primitive.css shared/styles/tokens/semantic.css
  rtk git commit -m "$(cat <<'EOF'
  feat(ds): add Plan 7 tokens — elevation, status quad, motion, pill, gauge, mono

  Extends the DS token system with the additions required by Plan 7:

  Primitives:
  - 4-level shadow elevation scale (shadow-elevation-1 through -4)
    based on Dimensional Layering style from UI UX Pro Max spec
  - Status quad primitive colors (green-600, amber-500-bright, red-600)
  - Mono font family and feature settings (font-mono-family,
    font-mono-features with tnum + zero)

  Semantic:
  - Elevation aliases override v2.1 placeholders with the proper scale
  - Status quad (normal / warning / unknown / critical) with gauge and
    pulse slots. Warning reuses v2.1 --status-warning-bg/-border/-fg
    (already existing) and only adds --status-warning-gauge/-pulse
    aliases to the amber-500-bright primitive, so Plan 7 components
    have a consistent API across all 4 monitoring states.
  - Motion tokens (transition-hover 120ms, transition-active 80ms)
  - Pill active nav tokens (bg, fg, icon, shadow, hover bg/fg, radius)
  - Gauge tokens (height, bg, radius, 4 fill variants, transition)
  - Font family semantic aliases (font-ui, font-numeric)

  All tokens follow the DS 3-layer contract: primitives are opaque,
  components consume only semantic. Zero existing tokens removed.
  Zero visual diff yet — tokens exist but nothing consumes them until
  the new components land in Tasks 3-8.

  Build + 48 tests green.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Task 2 completa quando os tokens estão no disk, build verde, commit atomico.

---

## Task 3: New component — `stat-card-gauge.css`

### Purpose

Criar o componente principal do Plan 7: KPI card com número grande em mono + gauge bar progress + label + sub. Auto-contido (só consome semantic tokens). Aplicado ao SSCI dashboard na Task 13.

### Files

- Create: `shared/styles/components/stat-card-gauge.css` (~100 lines)

### Steps

- [ ] **Step 1: Write the file**

  Criar `shared/styles/components/stat-card-gauge.css` com o seguinte conteúdo completo:

  ```css
  /* =========================================================================
   * Design System SGA — Component: Stat Card Gauge (Plan 7)
   * =========================================================================
   * KPI card with large mono numeric value + horizontal gauge bar + label
   * and optional sub-text. Drives the SSCI dashboard visual. Self-contained
   * (consumes only semantic tokens, never primitives directly).
   *
   * Markup:
   *   <div class="stat-card-gauge" data-state="normal">
   *     <div class="stat-card-gauge__label">Categoria SCI</div>
   *     <div class="stat-card-gauge__value">7<span class="stat-card-gauge__suffix">/10</span></div>
   *     <div class="stat-card-gauge__bar"><div class="stat-card-gauge__fill" style="--fill: 70%"></div></div>
   *     <div class="stat-card-gauge__sub">Conforme ICAO nominal</div>
   *   </div>
   *
   * data-state values: "normal" (default), "ok", "warning", "critical", "unknown"
   * ========================================================================= */

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
    font-family: var(--font-ui);
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
    margin-left: 1px;
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

  .stat-card-gauge__sub {
    font-size: var(--text-xs);
    color: var(--neutral-fg-muted);
    margin-top: var(--space-3);
    font-family: var(--font-ui);
  }

  /* ---------- State modifiers ---------- */

  /* OK — green gauge */
  .stat-card-gauge[data-state="ok"] .stat-card-gauge__fill {
    background: var(--gauge-fill-ok);
  }

  /* Warning — amber gauge */
  .stat-card-gauge[data-state="warning"] .stat-card-gauge__fill {
    background: var(--gauge-fill-warning);
  }

  /* Critical — red gauge + rose tint background + red border-left */
  .stat-card-gauge[data-state="critical"] {
    border-left: 3px solid var(--status-critical-border);
    background: var(--status-critical-bg);
  }
  .stat-card-gauge[data-state="critical"] .stat-card-gauge__value {
    color: var(--status-critical-fg);
  }
  .stat-card-gauge[data-state="critical"] .stat-card-gauge__fill {
    background: var(--gauge-fill-critical);
  }

  /* Unknown — dashed border-left + muted value */
  .stat-card-gauge[data-state="unknown"] {
    border-left: 3px dashed var(--status-unknown-border);
  }
  .stat-card-gauge[data-state="unknown"] .stat-card-gauge__value {
    color: var(--status-unknown-fg);
  }
  .stat-card-gauge[data-state="unknown"] .stat-card-gauge__suffix {
    color: var(--status-unknown-fg);
  }

  /* ---------- Focus ring (if card is focusable) ---------- */
  .stat-card-gauge:focus-visible {
    outline: var(--focus-ring-width) solid var(--focus-ring-color);
    outline-offset: var(--focus-ring-offset);
  }

  /* ---------- Motion preferences ---------- */
  @media (prefers-reduced-motion: reduce) {
    .stat-card-gauge {
      transition: none;
    }
    .stat-card-gauge:hover {
      transform: none;
    }
    .stat-card-gauge__fill {
      transition: none;
    }
  }
  ```

- [ ] **Step 2: Build and verify cascade picks it up**
  ```bash
  rtk python scripts/build-all.py 2>&1 | tail -5
  ```
  Expected: build OK. O `compile_design_system_css()` faz discovery alfabético em `components/`, portanto `stat-card-gauge.css` é incluído automaticamente. Verificar:
  ```bash
  grep -c "stat-card-gauge" packages/portal-coe/dist/Portal_COE_AWM.html
  # Expected: >= 1 (CSS presente no output)
  ```

- [ ] **Step 3: Run tests**
  ```bash
  rtk python -m pytest tests/ -q
  ```
  Expected: 48 passing.

- [ ] **Step 4: Commit**
  ```bash
  rtk git add shared/styles/components/stat-card-gauge.css
  rtk git commit -m "$(cat <<'EOF'
  feat(ds): add stat-card-gauge component (Plan 7 Task 3)

  New self-contained component for KPI cards with large mono numeric
  value + horizontal gauge bar + label and optional sub-text. Drives
  the SSCI dashboard reskinning in Task 13.

  Supports 5 data-state values: normal (default), ok, warning, critical,
  unknown. Each state changes gauge fill color and (for critical) adds
  a red border-left + rose tint background. Unknown state has a dashed
  border-left and muted values.

  Consumes only semantic tokens. Never references primitives directly.
  Respects prefers-reduced-motion for hover transforms and gauge fill
  transitions.

  Automatically picked up by compile_design_system_css() alphabetical
  discovery in shared/styles/components/.

  Build + 48 tests green.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: CSS existe em `shared/styles/components/`, presente no dist HTML, commit atomico.

---

## Task 4: New component — `state-pulse.css` + `@keyframes` in `global.css`

### Purpose

Dot pulsante para sinalização de estado critical/warning em real-time. Standalone, pode ser aplicado a qualquer elemento posicionado relativo. Respeita `prefers-reduced-motion` com fallback textual.

### Files

- Create: `shared/styles/components/state-pulse.css` (~60 lines)
- Modify: `shared/styles/base/global.css` (+30 lines — `@keyframes pulse-critical/warning`)

### Steps

- [ ] **Step 1: Add `@keyframes` to `global.css`**

  Adicionar no fim de `shared/styles/base/global.css`:

  ```css
  /* =========================================================================
   * Plan 7 — Pulse animations for state-pulse component
   * ========================================================================= */
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

  @keyframes pulse-normal {
    0%   { box-shadow: 0 0 0 0 rgba(34,197,94,0.6); }
    70%  { box-shadow: 0 0 0 6px rgba(34,197,94,0); }
    100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
  }
  ```

- [ ] **Step 2: Write `state-pulse.css`**

  Criar `shared/styles/components/state-pulse.css`:

  ```css
  /* =========================================================================
   * Design System SGA — Component: State Pulse (Plan 7)
   * =========================================================================
   * Animated dot indicator for real-time critical/warning state.
   * Standalone, absolute-positioned. Parent must have position: relative.
   *
   * Markup:
   *   <div class="state-pulse" data-level="critical" data-fallback-label="alerta"></div>
   *
   * data-level values: "normal", "warning", "critical"
   * data-fallback-label: text shown in prefers-reduced-motion mode
   * ========================================================================= */

  .state-pulse {
    position: absolute;
    top: var(--space-3);
    right: var(--space-3);
    width: 7px;
    height: 7px;
    border-radius: 50%;
    pointer-events: none;
    z-index: 1;
  }

  .state-pulse[data-level="critical"] {
    background: var(--status-critical-pulse);
    animation: pulse-critical 1.5s infinite;
  }

  .state-pulse[data-level="warning"] {
    background: var(--status-warning-pulse);
    animation: pulse-warning 2s infinite;
  }

  .state-pulse[data-level="normal"] {
    background: var(--status-normal-pulse);
    animation: pulse-normal 2.5s infinite;
  }

  /* ---------- Accessibility — prefers-reduced-motion fallback ---------- */
  @media (prefers-reduced-motion: reduce) {
    .state-pulse {
      /* Drop the animation, reveal text fallback via attribute */
      animation: none !important;
      width: auto;
      height: auto;
      border-radius: var(--radius-sm);
      padding: 1px 5px;
      top: var(--space-2);
      right: var(--space-2);
      font-size: 8px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--white);
    }
    .state-pulse::after {
      content: attr(data-fallback-label);
    }
    .state-pulse[data-level="critical"] {
      background: var(--status-critical-border);
    }
    .state-pulse[data-level="warning"] {
      background: var(--status-warning-pulse);
      color: var(--status-warning-on-emphasis);
    }
    .state-pulse[data-level="normal"] {
      background: var(--status-normal-border);
    }
  }
  ```

- [ ] **Step 3: Build and verify**
  ```bash
  rtk python scripts/build-all.py 2>&1 | tail -5
  grep -c "state-pulse\|@keyframes pulse-critical" packages/portal-coe/dist/Portal_COE_AWM.html
  ```
  Expected: build OK, grep devolve >= 2.

- [ ] **Step 4: Run tests**
  ```bash
  rtk python -m pytest tests/ -q
  ```
  Expected: 48 passing.

- [ ] **Step 5: Commit**
  ```bash
  rtk git add shared/styles/components/state-pulse.css shared/styles/base/global.css
  rtk git commit -m "$(cat <<'EOF'
  feat(ds): add state-pulse component + pulse keyframes (Plan 7 Task 4)

  New self-contained component for real-time state signalling via animated
  pulsing dot. Three levels: normal (green, slow pulse), warning (amber),
  critical (red, fast pulse).

  @keyframes pulse-{critical,warning,normal} added to base/global.css —
  shared animation definitions, referenced by state-pulse.css but belong
  in global scope so other components can reuse them in future.

  Accessibility — prefers-reduced-motion fallback:
  - Animations disabled
  - Dot morphs into a small text badge showing data-fallback-label
    (e.g., "alerta", "warning", "ok")
  - High-contrast colors preserved

  Parent element must have position: relative. Dot positions absolute
  top: 12px, right: 12px by default.

  Build + 48 tests green.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: `state-pulse.css` existe, `@keyframes` em `global.css`, presente no dist, commit atomico.

---

## Task 5: New component — `dash-section.css`

### Purpose

Agrupamento row-based para secções do dashboard. Label uppercase + grid-line decorativa + grid de 3 colunas responsivo.

### Files

- Create: `shared/styles/components/dash-section.css` (~30 lines)

### Steps

- [ ] **Step 1: Write the file**

  ```css
  /* =========================================================================
   * Design System SGA — Component: Dash Section (Plan 7)
   * =========================================================================
   * Row-based grouping for dashboard content. Section label uppercase
   * + horizontal divider gradient + responsive 3-column grid inside.
   *
   * Markup:
   *   <section class="dash-section">
   *     <div class="dash-section__label">Estado operacional SCI</div>
   *     <div class="dash-section__grid">
   *       [3 stat-card-gauge or similar cards]
   *     </div>
   *   </section>
   * ========================================================================= */

  .dash-section {
    margin-bottom: var(--space-6);
  }

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
    font-family: var(--font-ui);
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
    .dash-section__grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 600px) {
    .dash-section__grid {
      grid-template-columns: 1fr;
    }
  }
  ```

- [ ] **Step 2: Build + tests**
  ```bash
  rtk python scripts/build-all.py && rtk python -m pytest tests/ -q
  ```
  Expected: build OK, 48 tests passing.

- [ ] **Step 3: Commit**
  ```bash
  rtk git add shared/styles/components/dash-section.css
  rtk git commit -m "$(cat <<'EOF'
  feat(ds): add dash-section component (Plan 7 Task 5)

  Row-based grouping component for dashboard sections. Uppercase label
  with gradient divider line to the right + 3-column responsive grid
  inside (2 cols at 900px, 1 col at 600px).

  Used by the SSCI dashboard in Task 13 to group the 6 KPI cards into
  2 semantic sections ("Estado operacional SCI" + "Performance e
  verificação").

  Build + 48 tests green.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: CSS existe, dist contém o component, commit atomico.

---

## Task 6: New component — `form-banner.css`

### Purpose

Banner inline para avisos/contexto dentro de forms operacionais. 3 variantes: warning (default), info, critical.

### Files

- Create: `shared/styles/components/form-banner.css` (~40 lines)

### Steps

- [ ] **Step 1: Write the file**

  ```css
  /* =========================================================================
   * Design System SGA — Component: Form Banner (Plan 7)
   * =========================================================================
   * Inline banner for warnings, context, or critical notes inside forms.
   * Three variants: default (warning/amber), info (blue), critical (red).
   *
   * Markup:
   *   <div class="form-banner">
   *     <strong>ETA é crítico</strong> — posicionamento SSCI ≤2 min
   *   </div>
   *   <div class="form-banner form-banner--info">...</div>
   *   <div class="form-banner form-banner--critical">...</div>
   * ========================================================================= */

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
    font-family: var(--font-ui);
  }

  .form-banner strong {
    color: var(--amber-900);
    font-weight: 700;
  }

  .form-banner--info {
    background: var(--status-info-bg);
    border-color: var(--blue-700);
    border-left-color: var(--blue-700);
    color: var(--status-info-fg);
  }

  .form-banner--info strong {
    color: var(--blue-900);
  }

  .form-banner--critical {
    background: var(--status-critical-bg);
    border-color: var(--red-600);
    border-left-color: var(--red-600);
    color: var(--status-critical-fg);
  }

  .form-banner--critical strong {
    color: var(--red-900);
  }
  ```

- [ ] **Step 2: Build + test + commit**
  ```bash
  rtk python scripts/build-all.py && rtk python -m pytest tests/ -q
  rtk git add shared/styles/components/form-banner.css
  rtk git commit -m "feat(ds): add form-banner component (Plan 7 Task 6)

Inline contextual banner for forms with 3 variants (warning default,
info, critical). Used by the COE ocorrência form in Task 14 to surface
\"ETA é crítico\" guidance during active emergency.

Build + 48 tests green.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
  ```

**Verification**: Component no disk, dist, commit.

---

## Task 7: New component — `form-two-col.css`

### Purpose

Wrapper layout two-column para forms com sidebar sticky. Usado no COE ocorrência form (Task 14).

### Files

- Create: `shared/styles/components/form-two-col.css` (~25 lines)

### Steps

- [ ] **Step 1: Write the file**

  ```css
  /* =========================================================================
   * Design System SGA — Component: Form Two-Column Layout (Plan 7)
   * =========================================================================
   * Wrapper for forms with main fields on the left and a sticky sidebar
   * on the right (e.g., timer card, summary, auto-save indicator).
   *
   * Markup:
   *   <section class="form-two-col">
   *     <div class="form-two-col__main">[form fields]</div>
   *     <aside class="form-two-col__sidebar">[sticky-timer-card, etc.]</aside>
   *   </section>
   * ========================================================================= */

  .form-two-col {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--space-5);
    align-items: flex-start;
  }

  .form-two-col__main {
    min-width: 0;
  }

  .form-two-col__sidebar {
    min-width: 0;
  }

  @media (max-width: 900px) {
    .form-two-col {
      grid-template-columns: 1fr;
    }
    .form-two-col__sidebar {
      position: static !important;
    }
  }

  @media print {
    .form-two-col {
      display: block;
    }
    .form-two-col__sidebar {
      position: static !important;
      margin-top: var(--space-4);
    }
  }
  ```

- [ ] **Step 2: Build + test + commit**
  ```bash
  rtk python scripts/build-all.py && rtk python -m pytest tests/ -q
  rtk git add shared/styles/components/form-two-col.css
  rtk git commit -m "feat(ds): add form-two-col component (Plan 7 Task 7)

Two-column form layout wrapper (2fr:1fr) for forms with sticky sidebar.
Collapses to single column at 900px, forces static positioning in print.
Used by the COE ocorrência form reskinning in Task 14.

Build + 48 tests green.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
  ```

**Verification**: Componente existe, commit.

---

## Task 8: New component — `sticky-timer-card.css`

### Purpose

Card sticky à direita do formulário COE com cronómetro grande + summary rows + auto-save indicator. Cronómetro grande em mono.

### Files

- Create: `shared/styles/components/sticky-timer-card.css` (~80 lines)

### Steps

- [ ] **Step 1: Write the file**

  ```css
  /* =========================================================================
   * Design System SGA — Component: Sticky Timer Card (Plan 7)
   * =========================================================================
   * Operational sidebar card with large live chronometer, summary rows,
   * and auto-save indicator. Used in the COE ocorrência form.
   *
   * Markup:
   *   <div class="sticky-timer-card">
   *     <div class="sticky-timer-card__label">Cronómetro desde notif.</div>
   *     <div class="sticky-timer-card__clock">01:47</div>
   *     <div class="sticky-timer-card__active">ACTIVA</div>
   *     <div class="sticky-timer-card__row">
   *       <span class="sticky-timer-card__row-label">Occ</span>
   *       <span class="sticky-timer-card__row-value">OCC-001</span>
   *     </div>
   *     [...]
   *     <div class="sticky-timer-card__saveindicator">auto-save · há 2s</div>
   *   </div>
   * ========================================================================= */

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
    font-family: var(--font-ui);
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
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: var(--space-5);
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .sticky-timer-card__active::before {
    content: '';
    width: 7px;
    height: 7px;
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

  .sticky-timer-card__row:last-of-type {
    border-bottom: none;
  }

  .sticky-timer-card__row-label {
    color: var(--neutral-fg-muted);
    font-weight: 500;
    font-family: var(--font-ui);
  }

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
    font-family: var(--font-ui);
  }

  /* Motion preference */
  @media (prefers-reduced-motion: reduce) {
    .sticky-timer-card__active::before {
      animation: none;
    }
  }
  ```

- [ ] **Step 2: Build + test + commit**
  ```bash
  rtk python scripts/build-all.py && rtk python -m pytest tests/ -q
  rtk git add shared/styles/components/sticky-timer-card.css
  rtk git commit -m "feat(ds): add sticky-timer-card component (Plan 7 Task 8)

Operational sidebar card with large 28px mono chronometer, ACTIVA
indicator with pulsing red dot, summary rows with dashed dividers,
and auto-save indicator.

Used by the COE ocorrência form reskinning in Task 14 — provides the
operator with always-visible time-since-notification, occurrence ID,
flight, SSCI status, and save state.

Respects prefers-reduced-motion for the pulse.

Build + 48 tests green.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
  ```

**Verification**: Component existe, commit.

---

## Task 9: Refactor `sidebar.css` — add `.nav-btn--pill` modifier

### Purpose

Adicionar a variante pill active SGA ao componente sidebar existente. **NÃO remove** o estilo legacy `.nav-btn` (preserva selectors JS) — é um modifier aditivo.

### Files

- Modify: `shared/styles/chrome/sidebar.css` (+50 / -0)

### Steps

- [ ] **Step 1: Read current `sidebar.css`**
  ```bash
  rtk read shared/styles/chrome/sidebar.css
  ```
  Identificar a secção `.nav-btn`, `.nav-btn:hover`, `.nav-btn.active`.

- [ ] **Step 2: Add `.nav-btn--pill` block at the end of the file**

  Adicionar no fim do ficheiro:

  ```css
  /* =========================================================================
   * Plan 7 — Pill-active navigation modifier
   * =========================================================================
   * Alternative active state for nav items: a solid SGA-blue pill with
   * white text and soft shadow instead of the legacy border-left indicator.
   *
   * Usage: add class nav-btn--pill alongside nav-btn.
   *   <button class="nav-btn nav-btn--pill active" onclick="openSection('x', event)">
   *     <svg class="icon"><use href="#icon-home"/></svg>
   *     Dashboard
   *   </button>
   *
   * The legacy .nav-btn.active style is preserved untouched — .nav-btn--pill
   * just overrides the visual treatment when both classes are present.
   * ========================================================================= */

  .nav-btn.nav-btn--pill {
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
    border-left: none !important; /* override legacy .nav-btn border-left rule */
    background: transparent;
    text-align: left;
    width: calc(100% - var(--space-5));
    box-shadow: none;
  }

  .nav-btn.nav-btn--pill:hover {
    background: var(--pill-hover-bg);
    color: var(--pill-hover-fg);
    transform: none; /* override any legacy transform */
  }

  .nav-btn.nav-btn--pill.active {
    background: var(--pill-active-bg);
    color: var(--pill-active-fg);
    font-weight: 600;
    box-shadow: var(--pill-active-shadow);
    border-left: none !important;
  }

  .nav-btn.nav-btn--pill .icon,
  .nav-btn.nav-btn--pill svg {
    width: 15px;
    height: 15px;
    opacity: 0.6;
    flex-shrink: 0;
  }

  .nav-btn.nav-btn--pill.active .icon,
  .nav-btn.nav-btn--pill.active svg {
    opacity: 1;
    color: var(--pill-active-icon);
  }

  .nav-btn.nav-btn--pill:focus-visible {
    outline: var(--focus-ring-width) solid var(--focus-ring-color);
    outline-offset: var(--focus-ring-offset);
  }

  @media (prefers-reduced-motion: reduce) {
    .nav-btn.nav-btn--pill {
      transition: none;
    }
  }
  ```

- [ ] **Step 3: Build + test + commit**
  ```bash
  rtk python scripts/build-all.py && rtk python -m pytest tests/ -q
  rtk git add shared/styles/chrome/sidebar.css
  rtk git commit -m "$(cat <<'EOF'
  feat(ds): add nav-btn--pill modifier to sidebar (Plan 7 Task 9)

  New visual variant of sidebar nav items: solid SGA-blue pill with
  white text + soft shadow instead of the legacy border-left indicator.

  Additive — the legacy .nav-btn.active CSS is untouched. .nav-btn--pill
  takes effect only when both classes are present on the element, so
  existing JS that toggles .active continues to work unchanged.

  Applied to both portals (COE + SSCI) in Task 17 markup updates.

  Hover state: light gray bg. Active: #004C7B bg + white text + shadow.
  Respects prefers-reduced-motion.

  Build + 48 tests green.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: `nav-btn--pill` CSS presente, commit.

---

## Task 10: Extend `form-group.css` — add `.form-group--numeric` modifier

### Purpose

Modifier que aplica a font-family mono aos inputs numéricos. Usado nos campos do `#emgFormBlock` do COE (OccId, Hora, Voo, etc).

### Files

- Modify: `shared/styles/components/form-group.css` (+10 lines)

### Steps

- [ ] **Step 1: Add modifier block to the end of `form-group.css`**

  ```css
  /* =========================================================================
   * Plan 7 — Numeric modifier for form fields
   * =========================================================================
   * Applies the monospace font (JetBrains Mono) to inputs inside a
   * .form-group--numeric wrapper. Used for fields holding IDs, codes,
   * times, flight numbers — anything that benefits from tabular numerals.
   *
   * Usage:
   *   <div class="form-group form-group--numeric">
   *     <label>Nº Ocorrência *</label>
   *     <input type="text" id="emgOccId">
   *   </div>
   * ========================================================================= */

  .form-group--numeric input,
  .form-group--numeric select,
  .form-group--numeric textarea {
    font-family: var(--font-numeric);
    font-feature-settings: var(--font-mono-features);
  }
  ```

- [ ] **Step 2: Build + test + commit**
  ```bash
  rtk python scripts/build-all.py && rtk python -m pytest tests/ -q
  rtk git add shared/styles/components/form-group.css
  rtk git commit -m "feat(ds): add form-group--numeric modifier (Plan 7 Task 10)

New modifier that applies --font-numeric (JetBrains Mono) to inputs,
selects, and textareas inside .form-group--numeric. Used for fields
holding IDs, times, codes, flight numbers — anything that benefits
from tabular numerals.

Applied to COE #emgFormBlock fields in Task 14.

Build + 48 tests green.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
  ```

**Verification**: Modifier existe, commit.

---

## Task 11: Embed JetBrains Mono in `fonts.css` + both `build.py`

### Purpose

Wire up a fonte JetBrains Mono no build pipeline. Ambos os `build.py` encodam os 2 ficheiros woff2 (Regular + Bold) como base64 e substituem placeholders. `fonts.css` declara 2 `@font-face` blocks para a família "JetBrains Mono".

### Files

- Modify: `shared/styles/base/fonts.css` (+18 lines — 2 @font-face blocks)
- Modify: `packages/portal-coe/scripts/build.py` (+12 lines)
- Modify: `packages/portal-ssci/scripts/build.py` (+12 lines — mirror)

### Steps

- [ ] **Step 0: Verify existing build.py Inter two-phase pattern**

  Plan 7 assumes both `build.py` scripts already implement a two-phase replacement for Inter:
  1. `{{DS_CSS}}` replaced with compiled DS CSS (which contains `{{DS_INTER_WOFF2_BASE64}}` inside `fonts.css`)
  2. `{{DS_INTER_WOFF2_BASE64}}` replaced **after** DS_CSS inject, expecting exactly 1 occurrence

  Confirm this assumption is true before writing any new replace logic:
  ```bash
  rtk grep -n "DS_INTER_WOFF2_BASE64\|ds_inter_b64\|inter_marker" packages/portal-coe/scripts/build.py
  rtk grep -n "DS_INTER_WOFF2_BASE64\|ds_inter_b64\|inter_marker" packages/portal-ssci/scripts/build.py
  ```
  Expected output (both files): multiple hits showing the two-phase pattern — a helper call `dsh.encode_font_woff2_base64(inter_woff2_path)` earlier, and later a block that counts + replaces `{{DS_INTER_WOFF2_BASE64}}` in `source_html` **after** `{{DS_CSS}}` was injected.

  If the actual pattern is different (e.g., Inter is injected inline during `compile_design_system_css()`), **stop** and adapt the strategy: put JetBrains Mono encoding in the same place as Inter, whatever that place is. If both fonts live inside `fonts.css` with placeholders, the two-phase approach works. If Inter is already expanded during compile, JetBrains Mono should be too.

  Record the current pattern as a comment at the top of the Task 11 execution log:
  ```
  # Verified: build.py uses two-phase replacement for Inter. Plan 7
  # follows the same pattern for JetBrains Mono.
  ```

- [ ] **Step 1: Read current `fonts.css`**
  ```bash
  rtk read shared/styles/base/fonts.css
  ```

- [ ] **Step 2: Append JetBrains Mono @font-face blocks to `fonts.css`**

  ```css
  /* =========================================================================
   * Plan 7 — JetBrains Mono (Regular + Bold, static weights)
   * =========================================================================
   * Used by --font-mono-family / --font-numeric for all numeric values,
   * IDs, coordinates, times, and operational data display. Two static
   * weights chosen over variable woff2 for size (58 KB vs 130 KB).
   *
   * License: OFL-1.1, source https://github.com/JetBrains/JetBrainsMono
   * ========================================================================= */

  @font-face {
    font-family: 'JetBrains Mono';
    font-weight: 400;
    font-style: normal;
    src: url('data:font/woff2;base64,{{DS_JETBRAINS_MONO_REGULAR_WOFF2_BASE64}}') format('woff2');
    font-display: block;
    font-feature-settings: 'tnum', 'zero';
  }

  @font-face {
    font-family: 'JetBrains Mono';
    font-weight: 700;
    font-style: normal;
    src: url('data:font/woff2;base64,{{DS_JETBRAINS_MONO_BOLD_WOFF2_BASE64}}') format('woff2');
    font-display: block;
    font-feature-settings: 'tnum', 'zero';
  }
  ```

- [ ] **Step 3: Update COE `build.py`**

  Localizar o bloco "(4) Encode the Inter Variable font as base64" e adicionar a seguir:

  ```python
  # (4b) Encode JetBrains Mono Regular + Bold as base64 (Plan 7)
  jb_regular_path = SHARED_DIR / "assets" / "fonts" / "JetBrainsMono-Regular.woff2"
  jb_bold_path = SHARED_DIR / "assets" / "fonts" / "JetBrainsMono-Bold.woff2"
  if not jb_regular_path.exists():
      print(f"  [error] JetBrainsMono-Regular.woff2 não encontrado em {jb_regular_path}")
      return 1
  if not jb_bold_path.exists():
      print(f"  [error] JetBrainsMono-Bold.woff2 não encontrado em {jb_bold_path}")
      return 1
  ds_jb_regular_b64 = dsh.encode_font_woff2_base64(jb_regular_path)
  ds_jb_bold_b64 = dsh.encode_font_woff2_base64(jb_bold_path)
  print(f"  [ds] encoded JetBrainsMono-Regular ({len(ds_jb_regular_b64):,} base64 chars)")
  print(f"  [ds] encoded JetBrainsMono-Bold    ({len(ds_jb_bold_b64):,} base64 chars)")
  ```

  Depois, na zona onde `{{DS_INTER_WOFF2_BASE64}}` é substituído (two-phase after DS_CSS inject), adicionar:

  ```python
  # Plan 7: JetBrains Mono markers — same two-phase pattern as Inter
  for jb_marker, jb_value in [
      ("{{DS_JETBRAINS_MONO_REGULAR_WOFF2_BASE64}}", ds_jb_regular_b64),
      ("{{DS_JETBRAINS_MONO_BOLD_WOFF2_BASE64}}", ds_jb_bold_b64),
  ]:
      count = source_html.count(jb_marker)
      if count != 1:
          print(f"  [error] Expected exactly 1 occurrence of {jb_marker!r} after DS_CSS replace, found {count}")
          return 1
      source_html = source_html.replace(jb_marker, jb_value)
      if jb_marker in source_html:
          print(f"  [error] {jb_marker!r} still present after replacement")
          return 1
  ```

- [ ] **Step 4: Mirror changes to SSCI `build.py`**

  Mesmas alterações em `packages/portal-ssci/scripts/build.py`.

- [ ] **Step 5: Build + verify embeds**
  ```bash
  rtk python scripts/build-all.py 2>&1 | tail -15
  grep -c "JetBrains Mono" packages/portal-coe/dist/Portal_COE_AWM.html
  grep -c "font-family: 'JetBrains Mono'" packages/portal-ssci/dist/Portal_PSCI_AWM.html
  ```
  Expected: build OK, grep >= 2 (2 @font-face blocks por portal).

- [ ] **Step 6: Run tests**
  ```bash
  rtk python -m pytest tests/ -q
  ```
  Expected: 48 passing.

- [ ] **Step 7: Commit**
  ```bash
  rtk git add shared/styles/base/fonts.css packages/portal-coe/scripts/build.py packages/portal-ssci/scripts/build.py
  rtk git commit -m "$(cat <<'EOF'
  feat(ds): embed JetBrains Mono Regular + Bold in build (Plan 7 Task 11)

  Both portal build scripts now encode JetBrainsMono-{Regular,Bold}.woff2
  as base64 and substitute them into fonts.css @font-face blocks via
  two-phase placeholder replacement (same pattern as Inter Variable).

  fonts.css gains two new @font-face blocks for 'JetBrains Mono' family,
  weight 400 and 700 respectively. font-display: block to prevent FOUT
  of tabular numerals during splash screen.

  After this task, --font-mono-family (and its semantic alias
  --font-numeric) resolves to JetBrains Mono locally — all components
  referencing these tokens (stat-card-gauge value, sticky-timer-card
  clock, form-group--numeric inputs) now render with proper monospace
  tabular numerals.

  Dist size delta: approximately +90 KB per portal (2×29 KB woff2 as
  base64 grows to ~40 KB each).

  Build + 48 tests green.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Ambos os dists contêm 2 `@font-face` de JetBrains Mono, grep confirma, commit atomico.

---

## Task 12: SSCI — reskinning do dashboard (markup)

### Purpose

Substituir o markup legado do dashboard SSCI pelas novas secções `.dash-section` com 3 `.stat-card-gauge` cada. Preservar todos os IDs JS-load-bearing.

### Files

- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html` (~80 lines diff)

### Steps

- [ ] **Step 1: Audit current dashboard markup**
  ```bash
  rtk grep -n "Dashboard Operacional SSCI\|dash-card\|Categoria SCI\|Viaturas Operacionais\|Efectivo em Serviço" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  ```
  Identificar o bloco que contém os 6 KPIs. Ler as linhas identificadas para perceber a estrutura exacta + os IDs/classes existentes.

- [ ] **Step 2: Read the baseline markup**

  Ler o trecho do source HTML que mostra os 6 KPIs (CAT SCI, Viaturas, Efectivo, Resposta, Comunicações, Inspecções). Anotar numa lista explícita:
  - IDs actuais (se houver) para cada valor
  - Classes que JS usa para popular (ex: `.dash-card .value`, `#psci-cat`, etc.)
  - Texto legacy de labels e subtitles

- [ ] **Step 2b: JS contract audit — grep for every legacy ID/class found in Step 2**

  Para cada ID/class identificada no Step 2, executar grep no ficheiro para confirmar quem a usa:

  ```bash
  # Exemplo para um id legado (repetir para cada um):
  rtk grep -c "getElementById('<id>')\|querySelector('#<id>')\|document\\.<id>\|<id>" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  rtk grep -c "\\.dash-card\|\\.dash-value\|\\.dash-label" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  ```

  **Rule**: um ID/class legado pode ser apagado **apenas se** todos os usages estão dentro de `updateDashboardSSCI()` (a única função que a Task 13 vai reescrever). Se houver usages noutro lugar (save/restore, localStorage rehydrate, event handler, export JSON), então:
  - Preservar o ID no markup novo (adicionar como `id="..."` no elemento `stat-card-gauge` equivalente), OU
  - Documentar aqui a lista de handlers afectados para que a Task 13 também os adapte

  Criar uma tabela como resultado:
  ```
  | Legacy ID/class | Usage count | Functions that touch it | Action |
  |---|---|---|---|
  | #psci-cat-value | 3 | updateDashboardSSCI, exportCfg | Preserve as id on kpi-cat |
  | .dash-card      | 8 | updateDashboardSSCI only | Safe to drop |
  | ... | ... | ... | ... |
  ```

  Salvar esta tabela como comentário HTML no topo do bloco reescrito na Step 3. Isto serve de trail para Task 13 saber exactamente que selectors ajustar.

- [ ] **Step 3: Replace legacy markup with new row-grouped dashboard**

  Usar o `Edit` tool para substituir o bloco inteiro. Prefixar com o comentário HTML da tabela produzida no Step 2b (legacy ID → action mapping) — isto dá ao Task 13 um trail claro do que adaptar. Markup alvo (exactamente conforme `synthesis.html` e spec § 5.1):

  ```html
  <section class="ds-page-grid">
    <div class="ds-page-grid__content">
      <header class="content-header" style="margin-bottom: var(--space-5);">
        <h1 style="font-size: 20px; font-weight: 600; color: var(--neutral-fg); letter-spacing: -0.02em; margin: 0 0 var(--space-2) 0;">Dashboard Operacional SSCI</h1>
        <p style="font-size: var(--text-sm); color: var(--neutral-fg-muted); margin: 0;">Visão geral do estado do Serviço de Salvamento e Combate a Incêndio <span style="font-size: 10px; color: var(--neutral-fg-subtle); font-family: var(--font-numeric);"> · actualizado há <span id="updated-ago">—</span></span></p>
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

          <div class="stat-card-gauge" data-state="normal" id="kpi-resposta">
            <div class="stat-card-gauge__label">Tempo Resposta</div>
            <div class="stat-card-gauge__value" id="kpi-resposta-value">—</div>
            <div class="stat-card-gauge__bar"><div class="stat-card-gauge__fill" style="--fill: 0%"></div></div>
            <div class="stat-card-gauge__sub" id="kpi-resposta-sub">média 7d</div>
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
            <div class="stat-card-gauge__sub" id="kpi-inspec-sub">mês actual</div>
          </div>

        </div>
      </section>
    </div>
  </section>
  ```

- [ ] **Step 4: Build and verify in Chrome**
  ```bash
  rtk python scripts/build-all.py 2>&1 | tail -5
  # Expected: build OK
  ```
  Abrir `packages/portal-ssci/dist/Portal_PSCI_AWM.html` em Chrome e verificar visualmente que a secção Dashboard mostra 6 cards em 2 rows de 3, matching `synthesis.html`.

- [ ] **Step 5: Verify JS contracts not broken**

  O `updateDashboardSSCI()` legacy pode estar a escrever para elementos que já não existem. Correr o portal e verificar o console por erros JS. A **Task 13** adapta o JS — aqui só verificamos que nada crítico partiu. Se houver warnings "element not found", são esperados até Task 13.

- [ ] **Step 6: Tests + commit**
  ```bash
  rtk python -m pytest tests/ -q
  rtk git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  rtk git commit -m "$(cat <<'EOF'
  feat(ssci): reskinning dashboard to stat-card-gauge + dash-section (Plan 7 Task 12)

  Replaces the legacy flat dashboard markup (~6 KPI values in unstyled
  divs) with the new row-grouped layout using dash-section + stat-card-gauge
  components. Two semantic sections now group the KPIs:

  - "Estado operacional SCI": Categoria SCI (7/10), Viaturas (3/3),
    Efectivo (—/9 unknown state)
  - "Performance e verificação": Tempo Resposta, Comunicações,
    Inspecções Mensais

  Each card uses the new data-state API (normal/ok/unknown/warning/
  critical). Numbers render in JetBrains Mono via --font-numeric.
  Gauges show visual progress. Hover elevates with shadow.

  JS adaptation for updateDashboardSSCI() comes in Task 13 — this task
  only lands the markup. Some console warnings ("element not found")
  are expected until Task 13 lands.

  Visual matches synthesis.html mockup from brainstorming. Build + 48
  tests green.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: SSCI dashboard visualmente alinhado com mockup, JS warnings transients aceitáveis.

---

## Task 13: SSCI — adapt JavaScript `updateDashboardSSCI()` and add auto-refresh

### Purpose

Actualizar o JS que popula o dashboard SSCI para escrever nos novos IDs + adicionar o "updated há Xs" ticker. Zero funcionalidade nova — apenas adaptação dos selectors.

### Files

- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html` (JS block, ~30 lines)

### Steps

- [ ] **Step 1: Audit the existing `updateDashboardSSCI()`**
  ```bash
  rtk grep -n "updateDashboardSSCI\|function.*Dashboard\|getElementById\('kpi" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  ```
  Ler o bloco inteiro da função para entender o que popula e de onde vem.

- [ ] **Step 2: Write the applyStatState helper + adapted updateDashboardSSCI**

  Criar a função `applyStatState()` como utility (usada também na Task 17 para aria-live toggling) e depois a adaptação do `updateDashboardSSCI()`. Ambas vivem no mesmo bloco `<script>` existente do SSCI source:

  ```javascript
  /**
   * Apply a monitoring state to a stat-card-gauge element.
   * Sets data-state, toggles role=alert and aria-live coherently.
   * Must be the ONLY way stat cards transition state — Task 17
   * relies on this being centralised.
   *
   * @param {HTMLElement} el  — the .stat-card-gauge element
   * @param {string} state   — "normal" | "ok" | "warning" | "critical" | "unknown"
   */
  function applyStatState(el, state) {
    if (!el) return;
    el.setAttribute('data-state', state);
    if (state === 'critical') {
      el.setAttribute('role', 'alert');
      el.setAttribute('aria-live', 'assertive');
    } else {
      el.removeAttribute('role');
      el.setAttribute('aria-live', 'polite');
    }
  }
  // Expose for other modules (e.g., emergency triggers)
  window.applyStatState = applyStatState;

  function updateDashboardSSCI() {
    try {
      var cfg = window.PSCI_CFG || {};

      // Categoria SCI (primitive display, value + fill%)
      var cat = cfg.catSci || 7;
      var catEl = document.getElementById('kpi-cat');
      if (catEl) {
        var catValue = catEl.querySelector('.stat-card-gauge__value');
        if (catValue) catValue.innerHTML = cat + '<span class="stat-card-gauge__suffix">/10</span>';
        var catFill = catEl.querySelector('.stat-card-gauge__fill');
        if (catFill) catFill.style.setProperty('--fill', (cat / 10 * 100) + '%');
        applyStatState(catEl, 'normal');
      }

      // Viaturas (computed from arrays)
      var viatOk = (cfg.viaturas || []).filter(function(v) { return v.operacional; }).length;
      var viatTotal = (cfg.viaturas || []).length || 3;
      var viatEl = document.getElementById('kpi-viaturas');
      if (viatEl) {
        var viatVal = viatEl.querySelector('.stat-card-gauge__value');
        if (viatVal) viatVal.innerHTML = viatOk + '<span class="stat-card-gauge__suffix">/' + viatTotal + '</span>';
        var viatFill = viatEl.querySelector('.stat-card-gauge__fill');
        if (viatFill) viatFill.style.setProperty('--fill', (viatOk / viatTotal * 100) + '%');
        applyStatState(viatEl, viatOk === viatTotal ? 'ok' : 'warning');
      }

      // Efectivo — from turno registado
      var efectivo = (window.lsGet && window.lsGet('psci_efectivo', null)) || null;
      var efecEl = document.getElementById('kpi-efectivo');
      if (efecEl) {
        var efecVal = efecEl.querySelector('.stat-card-gauge__value');
        if (efecVal) {
          efecVal.innerHTML = (efectivo !== null ? efectivo : '—') + '<span class="stat-card-gauge__suffix">/9</span>';
        }
        var efecFill = efecEl.querySelector('.stat-card-gauge__fill');
        if (efecFill) efecFill.style.setProperty('--fill', efectivo !== null ? (efectivo / 9 * 100) + '%' : '0%');
        applyStatState(efecEl, efectivo === null ? 'unknown' : (efectivo >= 7 ? 'ok' : 'warning'));
      }

      // Resposta — avg from history
      var respAvg = (window.lsGet && window.lsGet('psci_resp_avg', null)) || null;
      var respEl = document.getElementById('kpi-resposta');
      if (respEl) {
        var respVal = respEl.querySelector('.stat-card-gauge__value');
        if (respVal) respVal.textContent = respAvg !== null ? respAvg : '—';
        var respFill = respEl.querySelector('.stat-card-gauge__fill');
        if (respFill) respFill.style.setProperty('--fill', respAvg !== null ? '80%' : '0%');
        applyStatState(respEl, respAvg === null ? 'unknown' : 'normal');
      }

      // Last-updated ticker
      var updEl = document.getElementById('updated-ago');
      if (updEl) {
        window.__ssciDashLastUpdate = Date.now();
        updEl.textContent = '0s';
      }
    } catch (e) {
      console.error('[dashboard-ssci] update error:', e);
    }
  }

  // Keep the "updated há Xs" counter live
  setInterval(function() {
    var updEl = document.getElementById('updated-ago');
    if (updEl && window.__ssciDashLastUpdate) {
      var diff = Math.floor((Date.now() - window.__ssciDashLastUpdate) / 1000);
      updEl.textContent = diff + 's';
    }
  }, 1000);
  ```

  Substituir a função existente pelo bloco acima usando `Edit` tool.

- [ ] **Step 3: Ensure `updateDashboardSSCI()` runs on load**

  Verificar que a função é chamada em `DOMContentLoaded` ou na inicialização do portal. Se não estiver, adicionar:
  ```javascript
  document.addEventListener('DOMContentLoaded', function() {
    if (typeof updateDashboardSSCI === 'function') updateDashboardSSCI();
  });
  ```

- [ ] **Step 4: Build + test + manual verify**
  ```bash
  rtk python scripts/build-all.py && rtk python -m pytest tests/ -q
  ```
  Abrir `dist/Portal_PSCI_AWM.html` em Chrome. Verificar:
  - Dashboard carrega sem erros no console
  - Os 6 KPIs mostram valores (mesmo que sejam defaults "—")
  - O "actualizado há Xs" incrementa a cada segundo

- [ ] **Step 5: Commit**
  ```bash
  rtk git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  rtk git commit -m "$(cat <<'EOF'
  feat(ssci): adapt updateDashboardSSCI to new stat-card-gauge markup (Plan 7 Task 13)

  Rewrites updateDashboardSSCI() to populate the new stat-card-gauge
  KPI cards instead of the legacy flat divs. Each KPI now:

  - Reads value from window.PSCI_CFG or localStorage via lsGet
  - Writes value to .stat-card-gauge__value
  - Sets --fill CSS custom property on .stat-card-gauge__fill for gauge %
  - Updates data-state attribute (normal/ok/unknown/warning) based on
    business logic (e.g., viaturas 3/3 = ok, efectivo null = unknown,
    catSci always normal)

  New "updated há Xs" ticker runs every 1s to show dashboard freshness.

  Zero new features — pure adaptation of selectors. All existing data
  sources (PSCI_CFG, localStorage) preserved. JS contracts maintained.

  Build + 48 tests green. Manual Chrome verify: dashboard loads cleanly.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Dashboard SSCI carrega limpo, KPIs populados, ticker funcional, commit.

---

## Task 14: COE — reskinning `#emgFormBlock` (markup)

### Purpose

Substituir o markup legado do form `#emgFormBlock` (classes `.efb-*` com grids próprios) pelo layout two-col + sticky timer card + form-group DS existente. Preservar id `#emgFormBlock` e todos os inputs por ID.

### Files

- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html` (~100 lines diff)

### Steps

- [ ] **Step 1: Audit `#emgFormBlock` baseline**
  ```bash
  rtk grep -n "emgFormBlock\|efb-title\|efb-grid\|efb-sub\|Emergência Aeronáutica" packages/portal-coe/src/Portal_COE_AWM.source.html | head -40
  ```
  Ler o bloco completo. Anotar:
  - Todos os `id=` dos inputs (`emgOccId`, `emgOccTime`, `emgFlightNum`, `emgAircraftType`, etc.)
  - Classes que JS usa para save/restore
  - Estrutura lógica dos grupos (dados gerais, aeronave, combustível, carga, etc.)
  - Se há já um elemento que faz chronometer para a ocorrência

- [ ] **Step 2: Replace the form block**

  Usar `Edit` tool para substituir o bloco inteiro de `#emgFormBlock`. Usar como modelo o markup da spec § 5.2 (form-two-col wrapper + form-row + form-group--numeric + sticky-timer-card na sidebar). Preservar TODOS os IDs dos inputs — apenas muda a estrutura dos wrappers, os fields ficam por baixo do mesmo `id`.

  Esqueleto (os campos específicos dependem do baseline auditado no Step 1):

  ```html
  <section class="form-two-col" id="emgFormBlock">
    <div class="form-two-col__main">
      <h3 class="efb-title" style="margin-top:0;">Dados Operacionais da Emergência Aeronáutica</h3>
      <div class="form-banner">
        <strong>ETA é crítico</strong> — indicar hora de posicionamento dos SSCI (≤2 min)
      </div>

      <div class="form-row">
        <div class="form-group form-group--numeric">
          <label>Nº Ocorrência <span style="color:var(--status-critical-fg)">*</span></label>
          <input type="text" id="emgOccId" required>
        </div>
        <div class="form-group form-group--numeric">
          <label>Hora Notificação <span style="color:var(--status-critical-fg)">*</span></label>
          <input type="text" id="emgOccTime" required>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group form-group--numeric">
          <label>Voo / Matrícula</label>
          <input type="text" id="emgFlightNum">
        </div>
        <div class="form-group">
          <label>Tipo Aeronave</label>
          <input type="text" id="emgAircraftType" placeholder="B738">
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Companhia</label>
          <input type="text" id="emgCompany">
        </div>
        <div class="form-group form-group--numeric">
          <label>Combustível (min/max)</label>
          <input type="text" id="emgFuel" placeholder="4 / 6t">
        </div>
      </div>

      <!-- Additional fields preserved from baseline (Carga Perigosa, etc.) using same form-row/form-group pattern -->

    </div>

    <aside class="form-two-col__sidebar">
      <div class="sticky-timer-card">
        <div class="sticky-timer-card__label">Cronómetro desde notif.</div>
        <div class="sticky-timer-card__clock" id="occ-chronometer">—</div>
        <div class="sticky-timer-card__active" id="occ-active">A AGUARDAR</div>

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
          <span class="sticky-timer-card__row-value">por confirmar</span>
        </div>

        <div class="sticky-timer-card__saveindicator" id="occ-autosave">sem alterações</div>
      </div>
    </aside>
  </section>
  ```

- [ ] **Step 3: Build + visual verify**
  ```bash
  rtk python scripts/build-all.py 2>&1 | tail -5
  ```
  Abrir `dist/Portal_COE_AWM.html` em Chrome, navegar até a secção de Emergência Aeronáutica, verificar visualmente:
  - Form à esquerda com fields com focus rings SGA
  - Sidebar sticky à direita com cronómetro grande
  - Banner amber com "ETA é crítico"
  - Layout colapsa bem em viewport 900px

- [ ] **Step 4: Tests + commit**
  ```bash
  rtk python -m pytest tests/ -q
  rtk git add packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk git commit -m "$(cat <<'EOF'
  feat(coe): reskinning #emgFormBlock to two-col + sticky timer (Plan 7 Task 14)

  Replaces the legacy .efb-* grid markup with:
  - .form-two-col wrapper (2fr:1fr)
  - .form-row + .form-group + .form-group--numeric for fields
  - .form-banner warning "ETA é crítico"
  - .sticky-timer-card aside with live chronometer, ACTIVA indicator,
    summary rows, and auto-save indicator

  All legacy input IDs preserved (emgOccId, emgOccTime, emgFlightNum,
  emgAircraftType, emgCompany, emgFuel, etc.) so existing save/restore
  JS continues to work. The #emgFormBlock id is preserved — it's now
  on the .form-two-col wrapper instead of the legacy container div.

  Numeric fields (Nº Ocorrência, Hora, Voo/Matrícula, Combustível) use
  form-group--numeric for JetBrains Mono rendering.

  Chronometer JS adaptation comes in Task 16 — this task lands the
  markup only. The clock initially shows "—".

  Build + 48 tests green. Manual Chrome: form renders with proper
  two-col layout and focus rings.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: COE form visualmente alinhado com mockup `form-treatment.html` (option C), IDs preservados, commit atomico.

---

## Task 15: COE — chronometer JS for `sticky-timer-card`

### Purpose

Popular o `sticky-timer-card` com cronómetro live desde que uma ocorrência é iniciada, além dos summary rows (Occ, Notif, Voo, SSCI) via bindings para os inputs do form.

### Files

- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html` (JS block, ~40 lines)

### Steps

- [ ] **Step 1: Write the chronometer + binding logic**

  Adicionar um bloco `<script>` no body (ou extender um existente de init do portal):

  ```javascript
  (function() {
    'use strict';

    var CLOCK_EL = null;
    var ACTIVE_EL = null;
    var occNotificationTime = null;

    function formatElapsed(ms) {
      if (ms < 0) return '00:00';
      var total = Math.floor(ms / 1000);
      var mm = Math.floor(total / 60);
      var ss = total % 60;
      return String(mm).padStart(2, '0') + ':' + String(ss).padStart(2, '0');
    }

    function updateChronometer() {
      if (!CLOCK_EL) CLOCK_EL = document.getElementById('occ-chronometer');
      if (!CLOCK_EL) return;
      if (occNotificationTime) {
        var elapsed = Date.now() - occNotificationTime;
        CLOCK_EL.textContent = formatElapsed(elapsed);
        if (!ACTIVE_EL) ACTIVE_EL = document.getElementById('occ-active');
        if (ACTIVE_EL) ACTIVE_EL.textContent = 'ACTIVA';
      } else {
        CLOCK_EL.textContent = '—';
      }
    }

    function bindSummary() {
      var map = [
        ['emgOccId', 'occ-id-ref'],
        ['emgOccTime', 'occ-notif-ref'],
        ['emgFlightNum', 'occ-voo-ref'],
      ];
      map.forEach(function(pair) {
        var src = document.getElementById(pair[0]);
        var dst = document.getElementById(pair[1]);
        if (src && dst) {
          src.addEventListener('input', function() {
            dst.textContent = src.value || '—';
            if (pair[0] === 'emgOccTime' && src.value) {
              occNotificationTime = Date.now();
            }
          });
        }
      });
    }

    function initOccAutosave() {
      var saveEl = document.getElementById('occ-autosave');
      if (!saveEl) return;
      var inputs = document.querySelectorAll('#emgFormBlock input, #emgFormBlock textarea, #emgFormBlock select');
      inputs.forEach(function(inp) {
        inp.addEventListener('input', function() {
          saveEl.textContent = 'a guardar…';
          setTimeout(function() { saveEl.textContent = 'guardado · agora'; }, 300);
        });
      });
    }

    document.addEventListener('DOMContentLoaded', function() {
      bindSummary();
      initOccAutosave();
      setInterval(updateChronometer, 1000);
    });
  })();
  ```

- [ ] **Step 2: Build + tests + manual verify**
  ```bash
  rtk python scripts/build-all.py && rtk python -m pytest tests/ -q
  ```
  Abrir COE dist em Chrome, ir ao `#emgFormBlock`, escrever uma Nº Ocorrência + Hora Notificação, verificar:
  - `#occ-id-ref` actualiza com o valor digitado
  - `#occ-notif-ref` mostra a hora
  - `#occ-chronometer` começa a contar assim que Hora Notificação é preenchida
  - `#occ-autosave` muda para "a guardar…" → "guardado · agora" ao digitar

- [ ] **Step 3: Commit**
  ```bash
  rtk git add packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk git commit -m "$(cat <<'EOF'
  feat(coe): add chronometer + bindings for sticky-timer-card (Plan 7 Task 15)

  New JS IIFE block that wires the sticky timer card sidebar:

  - Live chronometer #occ-chronometer updates every 1s, starts when
    Hora Notificação is populated
  - Summary rows (#occ-id-ref, #occ-notif-ref, #occ-voo-ref) bind to
    form inputs via input events — realtime mirror
  - ACTIVA indicator #occ-active turns active when chronometer starts
  - #occ-autosave shows "a guardar…" / "guardado · agora" cycle
    on any form input change (visual feedback, existing save logic
    is unchanged)

  Zero external dependencies, vanilla JS, wraps in IIFE to avoid
  polluting global namespace (except for DOMContentLoaded listener).

  Build + 48 tests green. Manual Chrome: chronometer counts, summary
  updates live.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Cronómetro live funciona, bindings ok, commit.

---

## Task 16: Sidebar markup — apply `nav-btn--pill` to both portals

### Purpose

Adicionar a classe `nav-btn--pill` a todos os nav items em ambos os portais. Additivo — `nav-btn` fica, `nav-btn--pill` entra ao lado. JS-load-bearing `.nav-btn.active` toggle continua a funcionar.

### Files

- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html` (~20 nav items diff)
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html` (~17 nav items diff)

### Steps

- [ ] **Step 1: Audit nav items in both portals**
  ```bash
  rtk grep -n 'class="nav-btn' packages/portal-coe/src/Portal_COE_AWM.source.html | head -20
  rtk grep -n 'class="nav-btn' packages/portal-ssci/src/Portal_PSCI_AWM.source.html | head -20
  ```
  Identificar todos os `<button class="nav-btn ...">`.

- [ ] **Step 2: Scripted rename — COE**

  Usar Python inline script para adicionar `nav-btn--pill` a cada elemento com class contendo `nav-btn` (como palavra separada, mesmo que não esteja em primeiro lugar). Regex usa word boundary `\bnav-btn\b` para robustez:

  ```bash
  rtk python -c "
  from pathlib import Path
  import re

  p = Path('packages/portal-coe/src/Portal_COE_AWM.source.html')
  txt = p.read_text(encoding='utf-8')

  # Match any class attribute that contains nav-btn as a whole word.
  # Captures the full class content so we can check if nav-btn--pill
  # is already present before adding it.
  pattern = re.compile(r'class=\"([^\"]*\bnav-btn\b[^\"]*)\"')

  def repl(m):
      cls = m.group(1)
      if 'nav-btn--pill' in cls:
          return m.group(0)
      return 'class=\"' + cls + ' nav-btn--pill\"'

  new = pattern.sub(repl, txt)
  n = new.count('nav-btn--pill') - txt.count('nav-btn--pill')
  print(f'Added nav-btn--pill to {n} elements')

  p.write_text(new, encoding='utf-8')
  "
  ```

  **Verify** that every matched element was updated (not just the ones with nav-btn as first class):
  ```bash
  # Count nav-btn elements:
  rtk grep -c "\\bnav-btn\\b" packages/portal-coe/src/Portal_COE_AWM.source.html
  # Count nav-btn--pill elements:
  rtk grep -c "\\bnav-btn--pill\\b" packages/portal-coe/src/Portal_COE_AWM.source.html
  ```
  Expected: **both counts equal** (or `nav-btn` > `nav-btn--pill` only if legitimate CSS class references exist outside HTML attributes, which are OK).

- [ ] **Step 3: Scripted rename — SSCI**

  Mesmo padrão, ficheiro diferente:
  ```bash
  rtk python -c "
  from pathlib import Path
  import re

  p = Path('packages/portal-ssci/src/Portal_PSCI_AWM.source.html')
  txt = p.read_text(encoding='utf-8')
  pattern = re.compile(r'class=\"([^\"]*\bnav-btn\b[^\"]*)\"')

  def repl(m):
      cls = m.group(1)
      if 'nav-btn--pill' in cls:
          return m.group(0)
      return 'class=\"' + cls + ' nav-btn--pill\"'

  new = pattern.sub(repl, txt)
  n = new.count('nav-btn--pill') - txt.count('nav-btn--pill')
  print(f'Added nav-btn--pill to {n} elements')
  p.write_text(new, encoding='utf-8')
  "
  ```

  **Verify** counts:
  ```bash
  rtk grep -c "\\bnav-btn\\b" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  rtk grep -c "\\bnav-btn--pill\\b" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  ```

- [ ] **Step 4: Build + verify nav items are pills**
  ```bash
  rtk python scripts/build-all.py 2>&1 | tail -5
  ```
  Abrir os 2 HTMLs em Chrome. Verificar que:
  - Sidebar nav items aparecem como pills
  - Item active tem fundo azul sólido `#004C7B` + texto branco + shadow
  - Hover state funciona (fundo cinza-azul claro)
  - Clicar num nav item continua a mudar de secção (`openSection(id, event)` continua a funcionar)

- [ ] **Step 5: Run tests + commit**
  ```bash
  rtk python -m pytest tests/ -q
  rtk git add packages/portal-coe/src/Portal_COE_AWM.source.html packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  rtk git commit -m "$(cat <<'EOF'
  feat(chrome): apply nav-btn--pill modifier to all sidebar nav items (Plan 7 Task 16)

  Every existing <button class="nav-btn ..."> gains an additional
  nav-btn--pill class across both Portal COE and Portal SSCI.

  Additive change: .nav-btn stays, JS toggle of .active keeps working,
  existing openSection(id, event) handlers untouched.

  Visual: sidebar active items now display as a solid SGA-blue pill
  with white text + soft shadow instead of the legacy border-left
  indicator. Hover states use light gray background.

  COE: ~20 nav items updated. SSCI: ~17 nav items updated. Applied via
  scripted regex to ensure consistency.

  Build + 48 tests green.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Sidebar pill active sólido em ambos os portais, commit.

---

## Task 17: Accessibility pass — aria-live, role=alert, prefers-reduced-motion

### Purpose

Adicionar ARIA hooks aos componentes novos para anunciar mudanças de estado em screen readers. Validar que `prefers-reduced-motion` desliga as animações sem perder informação visual.

### Files

- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html` (add role/aria-live)
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html` (add role/aria-live)

### Steps

- [ ] **Step 1: Verify `applyStatState()` exists in SSCI source from Task 13**

  A Task 13 já adicionou a função `applyStatState()` no bloco JS do SSCI source HTML e expôs como `window.applyStatState`. Confirmar:
  ```bash
  rtk grep -n "function applyStatState\|window.applyStatState" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  ```
  Expected: 2 hits (definição + exposição a window).

  Confirmar também que todas as transições de estado em `updateDashboardSSCI()` já passam por `applyStatState(el, state)` em vez de `el.setAttribute('data-state', ...)` directo:
  ```bash
  rtk grep -cn "applyStatState\|setAttribute.*data-state" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  ```
  Expected: `applyStatState` >= 4, `setAttribute('data-state'` == 0 (todas devem ter sido substituídas na Task 13).

- [ ] **Step 2: Port `applyStatState()` to COE source**

  O COE ainda não tem a função (a Task 15 só wireou o chronometer). Adicionar no mesmo bloco JS do COE source HTML (pode ser o mesmo IIFE da Task 15 ou um bloco `<script>` novo no fim do body):

  ```javascript
  /**
   * Mirror of applyStatState from SSCI — Task 17 Plan 7.
   * The COE currently has no stat-card-gauge elements in the default
   * dashboard (out of scope), but future emergency triggers may surface
   * them, and the a11y contract is the same across portals.
   */
  window.applyStatState = window.applyStatState || function(el, state) {
    if (!el) return;
    el.setAttribute('data-state', state);
    if (state === 'critical') {
      el.setAttribute('role', 'alert');
      el.setAttribute('aria-live', 'assertive');
    } else {
      el.removeAttribute('role');
      el.setAttribute('aria-live', 'polite');
    }
  };
  ```

  Localização recomendada: dentro do mesmo IIFE da Task 15 (`packages/portal-coe/src/Portal_COE_AWM.source.html`), logo antes do `document.addEventListener('DOMContentLoaded', ...)`.

- [ ] **Step 3: Verify prefers-reduced-motion fallback**

  Em Chrome DevTools → Rendering → Emulate CSS prefers-reduced-motion: reduce. Reabrir o portal. Verificar:
  - Pulse dots nos critical states não animam
  - Texto fallback "alerta"/"warning" aparece
  - Hover transforms nos stat cards desactivam
  - Sticky timer card pulse desactiva

- [ ] **Step 4: Run axe DevTools**

  Em Chrome DevTools → axe DevTools → Scan all of my page. Fazer scan em:
  - Portal SSCI Dashboard
  - Portal COE Emergency Form section
  - Portal COE Main Dashboard

  Expected: **0 critical + 0 serious** violations. Flag warnings são aceitáveis mas deve-se resolver críticos.

- [ ] **Step 5: Commit**
  ```bash
  rtk git add packages/portal-coe/src/Portal_COE_AWM.source.html packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  rtk git commit -m "$(cat <<'EOF'
  feat(a11y): add aria-live role=alert to critical stat cards (Plan 7 Task 17)

  Adds JS helper applyStatState() that toggles role="alert" and
  aria-live="assertive" when a stat card transitions to data-state="critical",
  and aria-live="polite" for other states. Screen readers now announce
  critical state changes immediately.

  prefers-reduced-motion verified:
  - state-pulse animations off → text fallback (alerta/warning) shown
  - stat-card-gauge hover transforms off
  - sticky-timer-card pulse off
  - All visual information preserved via non-animated fallbacks

  axe DevTools scan: 0 critical / 0 serious violations across SSCI
  dashboard, COE dashboard, COE emergency form.

  Build + 48 tests green.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: A11y pass, axe clean, commit.

---

## Task 18: Green gate final after all visual changes

### Purpose

Check final do estado pré-release. Tudo deve estar verde antes de avançar para release metadata.

### Steps

- [ ] **Step 1: Clean build**
  ```bash
  rtk python scripts/build-all.py 2>&1 | tail -10
  ```
  Expected: ambos os portais OK, sem erros.

- [ ] **Step 2: Full test suite**
  ```bash
  rtk python -m pytest tests/ -v 2>&1 | tail -20
  ```
  Expected: 48 passing.

- [ ] **Step 3: Manual visual smoke test em Chrome**
  - [ ] Portal COE abre, splash aparece e faz fade-out ~1500ms
  - [ ] Shell bar mostra logo SGA real + "Portal COE" + clock UTC a correr
  - [ ] Sidebar items são pills, active item azul sólido
  - [ ] Dashboard mostra KPIs em 2 secções row-grouped (se aplicável)
  - [ ] Emergência Aeronáutica form é two-col com sticky timer à direita
  - [ ] Cronómetro começa a contar quando Hora Notif. é preenchida
  - [ ] Critical state de `kpi-resposta` (se simulado) mostra pulse vermelho + tint rosa
  - [ ] Print preview (Ctrl+P) mostra logo SGA no topo da primeira página

- [ ] **Step 4: Manual visual smoke test SSCI**
  - [ ] Portal SSCI abre, splash OK
  - [ ] Shell bar mostra logo SGA real + "Portal SSCI" + clock
  - [ ] Sidebar pills OK
  - [ ] Dashboard mostra 6 KPIs em 2 secções (3+3) com gauge bars
  - [ ] Efectivo aparece em unknown state (border-left tracejado + `—/9`)
  - [ ] "Actualizado há Xs" incrementa a cada segundo

- [ ] **Step 5: Browser matrix check**
  - [ ] Chrome latest — OK
  - [ ] Edge latest — OK
  - [ ] Firefox latest — OK (pulse animations mais lentas por diferenças de engine, aceitável)

**Verification**: todos os bullets acima confirmados. Se algum falha, é blocker — resolver antes de avançar.

---

## Task 19: VERSION bump to 2.2.0-alpha.1

### Files

- Modify: `VERSION` (1 line)

### Steps

- [ ] **Step 1: Edit VERSION**
  ```bash
  echo "2.2.0-alpha.1" > VERSION
  cat VERSION
  ```

- [ ] **Step 2: Rebuild to confirm footer updates**
  ```bash
  rtk python scripts/build-all.py && grep "v2.2.0-alpha.1" packages/portal-coe/dist/Portal_COE_AWM.html | head -3
  ```
  Expected: footer do portal mostra "v2.2.0-alpha.1".

- [ ] **Step 3: Commit**
  ```bash
  rtk git add VERSION
  rtk git commit -m "chore(release): bump VERSION to 2.2.0-alpha.1 (Plan 7 Task 19)

Plan 7 Visual Polish feature-complete. Ready for documentation and
tag cutting in Tasks 20-24.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
  ```

**Verification**: VERSION bumped, build picks it up.

---

## Task 20: CHANGELOG entry for [2.2.0-alpha.1]

### Files

- Modify: `docs/CHANGELOG.md` (+80 lines)

### Steps

- [ ] **Step 1: Replace "Unreleased" section with proper [2.2.0-alpha.1] entry**

  Editar `docs/CHANGELOG.md`: mover a secção "Unreleased" (que tem o logo integration do commit 3a4122b) para formar a base da nova entrada `[2.2.0-alpha.1]`, e adicionar as features novas do Plan 7.

  Estrutura:
  ```markdown
  ## [2.2.0-alpha.1] — 2026-04-11

  ### Plan 7 — Visual Polish
  Aplicação do Design System SGA aos conteúdos operacionais legados
  (dashboard SSCI + formulário de ocorrência COE), adicionando depth,
  real-time state signalling, typography profissional, e operational
  context (sticky chronometer). Based on 8 brainstorming iterations in
  the visual companion + 7 queries to ui-ux-pro-max-skill.

  ### Added
  **New design tokens** (shared/styles/tokens/):
  - Elevation scale (shadow-elevation-1 through -4)
  - Status quad (normal/warning/critical/unknown with bg, border, fg, gauge, pulse)
  - Motion tokens (transition-hover 120ms, transition-active 80ms)
  - Pill active nav tokens (bg, fg, icon, shadow, hover, radius)
  - Gauge tokens (height, bg, radius, 4 fill variants, transition)
  - Typography tokens (font-ui, font-numeric, font-mono-family, font-mono-features)

  **New components** (shared/styles/components/):
  - stat-card-gauge — KPI card with large mono value + progress gauge
    + label + sub + 5 data-state variants
  - state-pulse — animated dot indicator for real-time critical/warning
    + prefers-reduced-motion text fallback
  - dash-section — row-based grouping with label + gradient divider +
    responsive 3-col grid
  - form-banner — inline contextual banner (warning/info/critical)
  - form-two-col — 2fr:1fr wrapper for forms with sticky sidebar
  - sticky-timer-card — chronometer + summary + auto-save indicator
  - form-group--numeric modifier on existing form-group

  **New sidebar modifier**: nav-btn--pill (solid SGA-blue pill active)

  **New fonts** (shared/assets/fonts/):
  - JetBrainsMono-Regular.woff2 (OFL, ~29 KB)
  - JetBrainsMono-Bold.woff2 (OFL, ~29 KB)
  - Embebidas via base64 em @font-face, resolvem --font-mono-family

  **New JS**:
  - applyStatState() helper with aria-live / role=alert toggling
  - COE chronometer + bindings for sticky-timer-card
  - SSCI updateDashboardSSCI() adapted for new stat-card-gauge markup
  - "updated há Xs" ticker on SSCI dashboard

  **Documentation**:
  - docs/releases/v2.2.0-alpha.1.md release notes
  - docs/design-system-guide.md updated with Plan 7 components
  - docs/ARCHITECTURE.md roadmap updated

  ### Changed
  - SSCI dashboard markup reskinned: 6 KPIs in 2 dash-sections
  - COE #emgFormBlock reskinned: two-col layout + sticky timer card
  - Both sidebars: nav items now use nav-btn--pill modifier
  - Stat cards numbers render in JetBrains Mono with tabular numerals

  ### Preserved (no breakage)
  - All JS-load-bearing IDs and classes (.awm-*, #clockDisplay, etc.)
  - openSection(id, event) contract
  - updateHeaderClock, cfgApplyToPortal, PSCI_CFG, window.notify, etc.
  - All data stores (localStorage, awmContacts schema)
  - 45 baseline tests + 3 new tests = 48 passing

  ### Test count
  - 48 tests passing (45 baseline + 3 defensive tests for JetBrains Mono embedding)

  ### Build size delta
  - COE dist: ~+90 KB (JetBrains Mono 2 weights as base64)
  - SSCI dist: ~+90 KB (mirror)
  - Acceptable given the typography upgrade benefit

  ### Known limitations carried forward from v2.1.0-alpha.1
  - Legacy :root { --dark-blue, ... } still present (180 domain consumers)
  - body font-family still Segoe UI for legacy content sections
  - Tablet/mobile responsive breakpoints (<600px) deferred to v2.3+
  - COE dashboard not reskinned (out of scope, deferred to future plan)
  - Contacts cards, fluxogramas, and other legacy sections unchanged
  ```

- [ ] **Step 2: Commit**
  ```bash
  rtk git add docs/CHANGELOG.md
  rtk git commit -m "docs(changelog): add [2.2.0-alpha.1] entry (Plan 7 Task 20)

Documents all Plan 7 additions, changes, preserved contracts, test
count, size delta, and carried-forward known limitations.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
  ```

**Verification**: CHANGELOG entry completa, commit.

---

## Task 21: Release notes `docs/releases/v2.2.0-alpha.1.md`

### Files

- Create: `docs/releases/v2.2.0-alpha.1.md` (~150 lines)

### Steps

- [ ] **Step 1: Write the narrative release notes**

  Criar o ficheiro com secções: O que é novo · Impacto visual · O que NÃO mudou · Breaking changes · Métricas · Validação próxima · Known limitations · Roadmap · Agradecimentos.

  Modelo: `docs/releases/v2.1.0-alpha.1.md` — seguir o mesmo tom narrativo europeu. Enfatizar:
  - Dashboard SSCI transformation (visual before/after screenshots mentais)
  - COE ocorrência form com cronómetro sticky
  - JetBrains Mono nos números
  - Pill active sidebar
  - Progress gauges + real-time state signalling

- [ ] **Step 2: Commit**
  ```bash
  rtk git add docs/releases/v2.2.0-alpha.1.md
  rtk git commit -m "docs(release): add v2.2.0-alpha.1 release notes (Plan 7 Task 21)

Narrative release notes matching v2.1.0-alpha.1 style. Covers Plan 7
visual polish deliverables: dashboard SSCI reskinning, COE ocorrência
form two-col layout, sticky timer card, progress gauges, real-time
state signalling, pill active sidebar, JetBrains Mono typography.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
  ```

**Verification**: Ficheiro existe, commit.

---

## Task 22: Update `docs/design-system-guide.md` with new components

### Files

- Modify: `docs/design-system-guide.md` (+80 lines)

### Steps

- [ ] **Step 1: Extend the components inventory table**

  Adicionar `stat-card-gauge`, `state-pulse`, `dash-section`, `form-banner`, `form-two-col`, `sticky-timer-card` à tabela da secção "§5 Componentes inventário".

- [ ] **Step 2: Add new token documentation**

  Na secção §3 "Catálogo de tokens", adicionar subsecções para os novos tokens (elevation scale, status quad, gauge, pill).

- [ ] **Step 3: Update §4 Typography**

  Mencionar JetBrains Mono agora disponível como `--font-numeric`.

- [ ] **Step 4: Commit**
  ```bash
  rtk git add docs/design-system-guide.md
  rtk git commit -m "docs(ds): update design-system-guide.md with Plan 7 additions (Plan 7 Task 22)

- 6 new components added to inventory table
- Token catalogue extended with elevation scale, status quad, gauge, pill
- Typography section notes JetBrains Mono availability

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
  ```

**Verification**: Guide atualizado, commit.

---

## Task 23: Update README + ARCHITECTURE for v2.2.0-alpha.1

### Files

- Modify: `README.md`
- Modify: `docs/ARCHITECTURE.md`

### Steps

- [ ] **Step 1: Bump versão em `README.md`**
  ```
  **Versão da plataforma:** `v2.1.0-alpha.1` → `v2.2.0-alpha.1`
  ```

- [ ] **Step 2: Adicionar Etapa 6 (Visual Polish) em "Estado actual"**
  ```markdown
  - [x] **Etapa 6** — **Visual Polish** (v2.2.0-alpha.1): dashboard SSCI
    com progress gauges + real-time states, COE ocorrência form com
    cronómetro sticky, JetBrains Mono nos números, sidebar pill active,
    6 novos componentes DS, logo SGA real em todo o lado
  ```

- [ ] **Step 3: Atualizar histórico em `ARCHITECTURE.md`**
  ```markdown
  - **v2.2.0-alpha.1** (2026-04-11) — **Visual Polish**: 6 novos
    componentes DS (stat-card-gauge, state-pulse, dash-section, form-
    banner, form-two-col, sticky-timer-card), token additions
    (elevation scale, status quad, motion, pill, gauge, mono
    typography), JetBrains Mono embedded, SSCI dashboard reskinning,
    COE ocorrência form two-col, sidebar pill active SGA, real logo
    SGA throughout.
  ```

- [ ] **Step 4: Commit**
  ```bash
  rtk git add README.md docs/ARCHITECTURE.md
  rtk git commit -m "docs: update README + ARCHITECTURE for v2.2.0-alpha.1 (Plan 7 Task 23)

- README version bump v2.1.0 → v2.2.0-alpha.1
- README adds Etapa 6 (Visual Polish) to 'Estado actual'
- ARCHITECTURE history gets v2.2.0-alpha.1 entry with feature summary

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
  ```

**Verification**: Files updated, commits atomicos.

---

## Task 24: Mark Plan 7 as complete + execution log

### Files

- Modify: `docs/superpowers/plans/2026-04-11-design-system-plan-7-visual-polish.md`

### Steps

- [ ] **Step 1: Add completion banner + execution log**

  Adicionar no topo do Plan 7 um banner `> **Status**: ✅ **COMPLETO**` e no fim (antes de "Summary") uma secção "Execution log" listando os commits atomicos produzidos com SHAs reais.

- [ ] **Step 2: Commit**
  ```bash
  rtk git add docs/superpowers/plans/2026-04-11-design-system-plan-7-visual-polish.md
  rtk git commit -m "docs(plan7): mark Plan 7 as complete with execution log (Plan 7 Task 24)

Adds completion banner and execution log listing the atomic commits
produced, any deviations from the plan as written, and the final green
gate state.

Plan 7 (Visual Polish) formally closed.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
  ```

**Verification**: Plan marked complete, commit.

---

## Task 25: Annotated git tag v2.2.0-alpha.1

### Steps

- [ ] **Step 1: Check clean state**
  ```bash
  rtk git status  # Expected: clean
  rtk git log --oneline -20  # Expected: ~24 commits na branch
  ```

- [ ] **Step 2: Create annotated tag**
  ```bash
  rtk git tag -a v2.2.0-alpha.1 -m "$(cat <<'EOF'
  Portal DREA v2.2.0-alpha.1 — Visual Polish

  Primeira release que aplica o Design System SGA aos conteúdos
  operacionais legados, adicionando depth (elevation scale), estados
  real-time (pulsed critical/warning/unknown), typography mono
  (JetBrains Mono para todos os números), operational context (sticky
  chronometer no COE ocorrência form), e pill active sidebar SGA.

  Product of 8 brainstorming iterations in the visual companion
  browser + 7 queries to ui-ux-pro-max-skill (161 reasoning rules,
  67 UI styles, 57 typography pairings). Executive Clean (Linear/
  Stripe) style with hybrid color identity (SGA on chrome, neutral
  content), row-based grouped layout, progress gauge stat cards,
  two-col form with sticky timer.

  6 new components added to shared/styles/components/. 7 new semantic
  token groups added. 2 JetBrains Mono woff2 files embedded. 48 tests
  passing. Zero regression in JS-load-bearing contracts.

  Pre-alpha — smoke test em ambiente de aeroporto pendente antes de
  promover para v2.2.0 estável.

  Detalhes completos: docs/releases/v2.2.0-alpha.1.md
  Design spec:        docs/superpowers/specs/2026-04-11-plan-7-visual-polish-design.md
  Plan executado:     docs/superpowers/plans/2026-04-11-design-system-plan-7-visual-polish.md
  CHANGELOG:          docs/CHANGELOG.md (entry [2.2.0-alpha.1])
  EOF
  )"
  ```

- [ ] **Step 3: Verify tag**
  ```bash
  rtk git tag -l "v2.2.0*"
  rtk git show v2.2.0-alpha.1 --stat | head -20
  ```

- [ ] **Step 4: Do NOT push yet**

  Tag local só. Push vem em Task 26 junto com a branch.

**Verification**: Tag existe localmente.

---

## Task 26: Push branch + create PR #7 + merge + cleanup

### Steps

- [ ] **Step 1: Push branch**
  ```bash
  rtk git push -u origin feat/plan-7-visual-polish
  ```

- [ ] **Step 2: Create PR**
  ```bash
  rtk gh pr create --base main --head feat/plan-7-visual-polish --title "Plan 7: Visual Polish + release v2.2.0-alpha.1" --body "$(cat <<'EOF'
  ## Summary

  Closes Plan 7 of the Portal DREA visual polish arc, cutting release
  **v2.2.0-alpha.1**. Applies the Design System SGA (built in Plans 1-6)
  to the content sections that remained in legacy CSS: SSCI dashboard
  and COE ocorrência form.

  **Key changes**:
  - 6 new DS components (stat-card-gauge, state-pulse, dash-section,
    form-banner, form-two-col, sticky-timer-card)
  - 7 new semantic token groups (elevation, status quad, motion, pill,
    gauge, mono typography + aliases)
  - JetBrains Mono embedded via 2 static woff2 files (OFL)
  - SSCI dashboard reskinning: 6 KPIs in row-grouped progress gauges
  - COE ocorrência form reskinning: two-col layout + sticky chronometer
  - Sidebar nav: nav-btn--pill modifier applied both portals
  - Accessibility: role/aria-live on critical states + prefers-reduced-motion

  Based on 8 visual brainstorm iterations + 7 ui-ux-pro-max-skill queries.

  ## Test plan

  - [x] `python scripts/build-all.py` → both portals OK
  - [x] `python -m pytest tests/ -q` → 48 passed (45 baseline + 3 new)
  - [x] `git status` clean
  - [x] Annotated tag v2.2.0-alpha.1 points at HEAD
  - [ ] Manual smoke test: SSCI dashboard matches synthesis.html
  - [ ] Manual smoke test: COE form matches form-treatment.html option C
  - [ ] axe DevTools: 0 critical/serious violations
  - [ ] Post-merge: push tag + create GitHub Release from v2.2.0-alpha.1.md

  🤖 Generated with [Claude Code](https://claude.com/claude-code)
  EOF
  )"
  ```

- [ ] **Step 3: Merge via rebase** (consistent with Plans 3-6)
  ```bash
  rtk gh pr merge --rebase --delete-branch
  ```

- [ ] **Step 4: Update local main**
  ```bash
  cd d:/VSCode_Claude/03-Resende/Portal_DREA
  rtk git fetch origin
  rtk git pull origin main
  ```

- [ ] **Step 5: Re-tag at rebased HEAD**

  Depois do rebase merge, os commits têm novos SHAs. A tag da Task 25 aponta para a branch antiga. Apagar e re-criar pointing ao HEAD actual de `main`:

  ```bash
  # Delete local tag pointing at the pre-rebase SHA
  rtk git tag -d v2.2.0-alpha.1

  # Re-create with the FULL HEREDOC message (same text as Task 25 Step 2)
  rtk git tag -a v2.2.0-alpha.1 HEAD -m "$(cat <<'EOF'
  Portal DREA v2.2.0-alpha.1 — Visual Polish

  Primeira release que aplica o Design System SGA aos conteúdos
  operacionais legados, adicionando depth (elevation scale), estados
  real-time (pulsed critical/warning/unknown), typography mono
  (JetBrains Mono para todos os números), operational context (sticky
  chronometer no COE ocorrência form), e pill active sidebar SGA.

  Product of 8 brainstorming iterations in the visual companion
  browser + 7 queries to ui-ux-pro-max-skill (161 reasoning rules,
  67 UI styles, 57 typography pairings). Executive Clean (Linear/
  Stripe) style with hybrid color identity (SGA on chrome, neutral
  content), row-based grouped layout, progress gauge stat cards,
  two-col form with sticky timer.

  6 new components added to shared/styles/components/. 7 new semantic
  token groups added. 2 JetBrains Mono woff2 files embedded. 48 tests
  passing. Zero regression in JS-load-bearing contracts.

  Pre-alpha — smoke test em ambiente de aeroporto pendente antes de
  promover para v2.2.0 estável.

  Detalhes completos: docs/releases/v2.2.0-alpha.1.md
  Design spec:        docs/superpowers/specs/2026-04-11-plan-7-visual-polish-design.md
  Plan executado:     docs/superpowers/plans/2026-04-11-design-system-plan-7-visual-polish.md
  CHANGELOG:          docs/CHANGELOG.md (entry [2.2.0-alpha.1])
  EOF
  )"

  rtk git push origin v2.2.0-alpha.1
  ```

- [ ] **Step 6: Create GitHub Release**
  ```bash
  rtk gh release create v2.2.0-alpha.1 --prerelease --title "Portal DREA v2.2.0-alpha.1 — Visual Polish" --notes-file docs/releases/v2.2.0-alpha.1.md

  rtk gh release upload v2.2.0-alpha.1 packages/portal-coe/dist/Portal_COE_AWM.html packages/portal-ssci/dist/Portal_PSCI_AWM.html
  ```

- [ ] **Step 7: Cleanup worktree**
  ```bash
  cd d:/VSCode_Claude/03-Resende/Portal_DREA
  rtk git worktree remove d:/VSCode_Claude/03-Resende/Portal_DREA-plan7
  rtk git branch -D feat/plan-7-visual-polish  # If still local
  ```

**Verification**: PR mergeado, tag pushed, GitHub Release criada com HTML builds, worktree removido.

---

## Verification checklist — final green-light

Executar depois de todas as Tasks 0-26 estarem completas.

### Build + tests
- [ ] `rtk python scripts/build-all.py` → exit 0
- [ ] `rtk python -m pytest tests/` → 48 passing
- [ ] `packages/portal-coe/dist/Portal_COE_AWM.html` existe, abre em Chrome
- [ ] `packages/portal-ssci/dist/Portal_PSCI_AWM.html` idem

### Visual validation
- [ ] SSCI dashboard matches synthesis.html (6 KPIs in 2 dash-sections)
- [ ] COE ocorrência form matches form-treatment.html option C (two-col + sticky timer)
- [ ] Sidebar pill active sólida SGA em ambos os portais
- [ ] Logo SGA real aparece no shell bar (30px) + splash (340px) + print header
- [ ] Cronómetro COE começa a contar quando Hora Notif é preenchida
- [ ] JetBrains Mono aparece em todos os números/IDs/timestamps

### State treatments
- [ ] OK state (green gauge) em Viaturas, Comunicações, Inspecções
- [ ] Unknown state (dashed border + gray value) em Efectivo
- [ ] Critical state (pulsed red dot + tint rosa) em Tempo Resposta (se simulado)
- [ ] Hover state (shadow elevation-2) em stat cards

### Accessibility
- [ ] axe DevTools: 0 critical/serious em 3 secções por portal
- [ ] prefers-reduced-motion: pulses off, text fallbacks visíveis
- [ ] Focus rings SGA em todo elemento interactivo
- [ ] aria-live="assertive" em data-state="critical"

### Release metadata
- [ ] VERSION = 2.2.0-alpha.1
- [ ] CHANGELOG [2.2.0-alpha.1] entry completa
- [ ] docs/releases/v2.2.0-alpha.1.md existe
- [ ] design-system-guide atualizado com 6 componentes novos
- [ ] README + ARCHITECTURE atualizados
- [ ] Tag annotated v2.2.0-alpha.1 existe e está pushed
- [ ] GitHub Release publicada com HTML builds anexados

### Git hygiene
- [ ] Cada task produziu 1 commit atomico (ou zero, onde indicado)
- [ ] Commit messages seguem padrão `type(scope): subject`
- [ ] Co-Authored-By trailer consistente
- [ ] PR mergeado via rebase (consistência com Plans 3-6)
- [ ] Worktree removido após merge

---

## Rollback plan

Plan 7 é aditivo e reversível por commit. Pontos de maior risco:

**Task 11 (JetBrains Mono embedding)** — máxima criticidade na mudança ao build pipeline
- Safeguard: dry run antes de commit (compilar sem substituir)
- Rollback: `git revert <SHA>` da task 11 reverte para Inter-only

**Task 12 + 14 (markup reskinning SSCI + COE)** — maior footprint de mudança
- Safeguard: preservação de IDs verificada antes de edit
- Rollback: `git revert` individual por task reverte os markups

**Task 16 (sidebar pill class mass-add)** — script modifica muitos elementos
- Safeguard: script imprime contagem das mudanças
- Rollback: `git revert` reverte a classe extra; JS contracts intactos

**Meta-rollback**: worktree vive em branch isolada `feat/plan-7-visual-polish`. Se algo corre mal, `git worktree remove + git branch -D` deita fora tudo. `main` continua em v2.1.0-alpha.1.

---

## Summary

Plan 7 é a task de polimento visual que encerra a arc de conteúdo operacional do Design System SGA. Adiciona 6 componentes novos, 7 grupos de tokens, JetBrains Mono, reskinning dos dois conteúdos legados mais visíveis (SSCI dashboard + COE ocorrência form), e release `v2.2.0-alpha.1`. O conteúdo foi desenhado em 8 iterações visuais no companion browser com research via `ui-ux-pro-max-skill`. Todas as tasks têm commits atomicos, todos os JS-load-bearing contracts são preservados, 45 → 48 tests, e a release é cortada com tag + GitHub Release com HTMLs anexados.

**Tone do plan**: build forward. Aplicar o que temos à realidade operacional.
