# Design System SGA — Plan 6: Cleanup, Documentation, Release (Implementation Plan)

> **Status**: ✅ **COMPLETO** (2026-04-11) — Fase 1 do Design System SGA fechada. Release `v2.1.0-alpha.1` cortada, tagged, documentada. Ver resumo de execução no fim deste ficheiro.

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` (or `superpowers:subagent-driven-development` se houver paralelismo útil) para implementar este plano task-by-task. Os passos usam checkbox (`- [ ]`) para tracking.

**Goal:** Fechar a Fase 1 do Design System SGA: retirar o namespace de transição `--ds-*`, eliminar todos os resíduos do CSS legado, escrever a documentação definitiva do sistema, e cortar a release `v2.1.0-alpha.1` com changelog, release notes e tag git. Este plano não inova — é o acto de arrumação que transforma um conjunto de migrações em produto.

**Architecture:** Depois dos Plans 1-5, ambos os portais consomem exclusivamente o Design System SGA em `shared/`. O namespace de transição `--ds-*` foi preservado até aqui para não colidir com o CSS legado do source HTML durante a migração. Agora que o legado foi removido (Plans 3-5), esse prefixo deixa de servir propósito e torna-se ruído de nomenclatura. A limpeza acontece em três movimentos distintos, cada um com o seu commit atómico: (1) rename global `--ds-*` → `--*` via script Python idempotente e reversível, (2) remoção dos resíduos do source HTML (`:root` legado, banners `PLAN 2 CONSOLIDATION`), (3) remoção de assets e scripts obsoletos. Depois da limpeza, a documentação definitiva é escrita (`docs/design-system-guide.md` novo, `docs/ARCHITECTURE.md` actualizado, READMEs finais em `shared/`). O plano termina com o bump de `VERSION` para `2.1.0-alpha.1`, entrada detalhada no `CHANGELOG.md`, release notes em directoria nova `docs/releases/`, e tag git anotada.

**Tech Stack:** Python 3.8+ (script de rename), pytest (testes do script de rename + regression gate), vanilla CSS (já migrado), git worktree + tags anotadas (release), Markdown (Keep a Changelog format).

**Source spec:** [docs/superpowers/specs/2026-04-11-design-system-sga-design.md](../specs/2026-04-11-design-system-sga-design.md) (v1.1 approved 2026-04-11). Secção 7.3 Fase 5 (rename + legacy cleanup) e Fase 6 (documentação e release) são a origem directa deste plano.

**Invariant this plan must preserve:** depois de `python scripts/build-all.py` com o Plan 6 completo, abrir `dist/Portal_COE_AWM.html` e `dist/Portal_PSCI_AWM.html` em Chrome tem que mostrar **zero diferenças visuais** face ao output do Plan 5. O rename é uma transformação textual que nunca toca valores hexadecimais ou estrutura de CSS — só identificadores. O único delta de tamanho esperado nos `.html` finais é a remoção de bytes do prefixo `ds-` (~3 bytes × número de ocorrências) menos os bytes dos banners `PLAN 2 CONSOLIDATION` removidos. `build-all.py` mantém-se green, `pytest` mantém-se green, e o smoke test manual em Chrome/Edge/Firefox valida o invariant visual.

**Out of scope for Plan 6** (explicitamente não aceites):

- ❌ Empacotamento Tauri desktop (Fase 2 do projecto — plano futuro)
- ❌ Criação dos portais futuros (SOA, AVSEC, DIRECÇÃO) — o design system preparou o terreno, mas a criação é um plano futuro separado
- ❌ LAN SQLite server (Fase 3/4 do projecto)
- ❌ Adicionar novos componentes ao DS — Plan 6 é janitorial
- ❌ Refactoring funcional de qualquer módulo dos portais
- ❌ Extracção de componentes de domínio (flow-node, cronómetro, inspecção VCI) — ficam nos portais respectivos
- ❌ Tests E2E automatizados (playwright, etc.) — smoke test manual é suficiente para esta release
- ❌ Optimização de tamanho dos `.html` (minify, gzip) — out of scope para este plano

---

## Fact sheet — resíduos a limpar (baseline inspeccionado em 2026-04-11 contra commit `bc11d89`)

Esta secção lista com precisão o que existe no repositório **no momento em que o Plan 6 começa a executar**. É a fonte de verdade sobre o que tem que desaparecer. Pressupõe que os Plans 3, 4 e 5 já mergearam na `main` e removeram o CSS de componente/chrome que estava a ser migrado — mas alguns resíduos específicos (por design do método de migração) ficaram intencionalmente para serem apagados em bloco por este plano.

### 1. Ficheiros CSS em `shared/styles/` com `--ds-*`

Todos os ficheiros abaixo contêm tokens com o prefixo `--ds-*`. A enumeração é completa e serve de input para o script de rename na Task 1:

| Ficheiro | Origem (Plan) | Tokens afectados |
|---|---|---|
| `shared/styles/tokens/primitive.css` | Plan 1 | Layer 1 — `--ds-gray-*`, `--ds-blue-*`, `--ds-amber-*`, `--ds-red-*`, `--ds-shadow-*`, `--ds-radius-*`, `--ds-transition-*`, `--ds-text-*`, `--ds-space-*`, etc. |
| `shared/styles/tokens/semantic.css` | Plan 1 | Layer 2 — `--ds-neutral-*`, `--ds-brand-*`, `--ds-status-*`, `--ds-cat-*`, `--ds-elevation-*`, `--ds-focus-ring-*` |
| `shared/styles/tokens/density-compact.css` | Plan 1 | `--ds-space-*`, `--ds-row-height`, `--ds-input-height`, `--ds-nav-item-height`, `--ds-text-base`, `--ds-line-base` |
| `shared/styles/tokens/density-comfortable.css` | Plan 1 | idem density-compact |
| `shared/styles/base/fonts.css` | Plan 1 | `@font-face` Inter — contém `--ds-*` apenas indirectamente (pode ter `var(--ds-*)` em rules auxiliares) |
| `shared/styles/base/reset.css` | Plan 2 (provável — ou Plan 3) | `var(--ds-*)` |
| `shared/styles/base/typography.css` | Plan 2/3 | `var(--ds-text-*)`, `var(--ds-line-*)`, `var(--ds-neutral-fg)`, etc. |
| `shared/styles/base/global.css` | Plan 2/3 | `var(--ds-neutral-canvas)`, etc. |
| `shared/styles/chrome/shell-bar.css` | Plan 4 | Ver capítulo de chrome |
| `shared/styles/chrome/sidebar.css` | Plan 4 | idem |
| `shared/styles/chrome/page-grid.css` | Plan 4 | idem |
| `shared/styles/chrome/splash.css` | Plan 4 | idem |
| `shared/styles/chrome/footer.css` | Plan 4 | idem |
| `shared/styles/components/button.css` | Plan 3 | Todos os componentes Tier 1-3 |
| `shared/styles/components/badge.css` | Plan 3 | idem |
| `shared/styles/components/card.css` | Plan 3 | idem |
| `shared/styles/components/stat-card.css` | Plan 3 | idem |
| `shared/styles/components/input.css` | Plan 3 | idem |
| `shared/styles/components/select.css` | Plan 3 | idem |
| `shared/styles/components/checkbox-radio.css` | Plan 3 | idem |
| `shared/styles/components/toggle.css` | Plan 3 | idem |
| `shared/styles/components/form-group.css` | Plan 3 | idem |
| `shared/styles/components/divider.css` | Plan 3 | idem |
| `shared/styles/components/table.css` | Plan 3 | idem |
| `shared/styles/components/tabs.css` | Plan 3 | idem |
| `shared/styles/components/dropdown.css` | Plan 3 | idem |
| `shared/styles/components/awm-modal.css` | Plan 3 | idem |
| `shared/styles/components/awm-toast.css` | Plan 3 | idem |
| `shared/styles/components/awm-save-badge.css` | Plan 3 | idem |
| `shared/styles/components/skeleton.css` | Plan 3 | idem |
| `shared/styles/components/empty-state.css` | Plan 3 | idem |
| `shared/styles/print/print.css` | Plan 4 | `var(--ds-neutral-*)`, `@page` rules |

**Nota**: alguns destes ficheiros podem ou não existir exactamente com estes nomes dependendo das decisões tomadas pelos Plans 3 e 4. A Task 0 começa por ler a árvore real de `shared/styles/` e gerar a lista autoritativa — a tabela acima é uma previsão baseada na spec.

### 2. Ficheiros JS em `shared/scripts/` a inspeccionar

Os scripts partilhados foram criados pelos Plans 3-5 (extracção dos helpers `awm-*` e `lsGet/lsSet`). A inspecção procura `--ds-*` dentro de strings literais (cores hard-coded, CSS injectado programaticamente) — é improvável mas tem que ser verificado:

| Ficheiro | Origem | Verificar |
|---|---|---|
| `shared/scripts/awm-modal.js` | Plan 3 | String literals com `style="--ds-..."` |
| `shared/scripts/awm-toast.js` | Plan 3 | idem |
| `shared/scripts/awm-save-badge.js` | Plan 3 | idem |
| `shared/scripts/awm-contacts.js` | Plan 5 | idem |
| `shared/scripts/utilities/ls-wrapper.js` | Plan 3 | Probably none |
| `shared/scripts/utilities/esc-html.js` | Plan 3 | Probably none |
| `shared/scripts/utilities/date-utc.js` | Plan 4 | Probably none |

### 3. Source HTMLs — consumidores e resíduos

#### `packages/portal-coe/src/Portal_COE_AWM.source.html` (15.150 linhas no baseline do Plan 2)

- **Ocorrências `var(--ds-*)`**: presentes nos pontos de consumo injectados pelos Plans 3 e 4 (markup de novo chrome, atributos inline). A contagem será feita na Task 1 antes do rename.
- **Resíduo legado em `<style>` block 1** (linhas 16-27 no baseline — o que sobra depende do que os Plans 3-4 já removeram):
  ```css
  :root {
      --dark-blue: #004C7B;
      --medium-blue: #0094CF;
      --light-blue: #38C7F4;
      --light-bg: #E8F4FD;
      --white: #ffffff;
      --gray-light: #f5f5f5;
      --gray-dark: #333333;
      --warning-red: #d32f2f;
      --success-green: #2e7d32;
      --alert-yellow: #f57f17;
  }
  ```
  **Crítico**: confirmar na Task 0 que este `:root` legado **já não tem consumidores** (nenhum `var(--dark-blue)` ou afins) antes de o remover. Se os Plans 3-4 deixaram alguns consumidores por migrar, este plano **falha e devolve para o backlog**.
- **Banners `PLAN 2 CONSOLIDATION`** (instaladas pelo Plan 2, nunca removidas):
  - Linha 14: banner de abertura de block 1
  - Linhas 1729, 1953, 2106, 2157, 2220, 2299, 2436, 2519, 2540, 2633: banners de secção interna do mesmo block
  - Linha 3136: banner de fecho "end of consolidated legacy block"
  - Linhas 11283, 11579, 11848, 12094, 12477, 12904, 13208, 13997, 14001, 14005: comentários HTML `<!-- PLAN 2 CONSOLIDATION: original block N merged into block 1 above -->` deixados como breadcrumbs nos sítios onde os blocos originais viviam
  Total: 22 banners (11 dentro do CSS + 11 comentários HTML). Fora do scope do rename (Task 1) — tratados na Task 3.

#### `packages/portal-ssci/src/Portal_PSCI_AWM.source.html` (4.140 linhas no baseline do Plan 2)

- **Ocorrências `var(--ds-*)`**: presentes nos pontos de consumo injectados pelo Plan 5.
- **Resíduo legado em `<style>` block 1**: mesmo padrão do COE, mas menor. Sub-conjunto das variáveis SGA originais. Remoção analogamente condicionada a ausência de consumidores.
- **Banners `PLAN 2 CONSOLIDATION`**: menor quantidade que o COE (SSCI consolidou `[1, 5, 6, 7]` — 4 blocos) mas mesmo padrão (banners CSS internos + comentários HTML breadcrumb).

### 4. Assets deprecados em `shared/assets/`

| Asset | Estado actual | Decisão |
|---|---|---|
| `shared/assets/logo-sga.png` (7.627 bytes) | Legacy PNG — substituído pelo SVG inline usado no Plan 4 (splash, shell bar) | **Remover** — SVG é o canonical, manter PNG duplicaria fonte de verdade. Documentar no CHANGELOG que o ficheiro existiu até `v2.0.0-beta.1` e que o utilizador pode recuperar via `git show bc11d89:shared/assets/logo-sga.png > logo-sga.png` se precisar. |
| `shared/assets/logo-sga-white.png` (10.858 bytes) | Legacy — foi feito para um dark theme que nunca vai existir (spec: light theme only) | **Remover** — sem uso possível |
| `shared/assets/fonts/Inter-VariableFont.woff2` (352.240 bytes) | Activo (consumido pelo Plan 1) | Preservar |
| `shared/assets/fonts/LICENSE-OFL.txt` | Activo | Preservar |
| `shared/assets/fonts/README.md` | Activo | Preservar (actualizar com referência ao guide) |
| `shared/assets/icons/sprite.svg` | Activo (consumido pelo Plan 1, expandido pelos Plans 3-4) | Preservar |
| `shared/assets/icons/README.md` | Activo | Preservar (actualizar) |
| `shared/assets/logo-sga-mark.svg` | Presumido criado pelo Plan 4 (shell bar) | Preservar |
| `shared/assets/logo-sga-full.svg` | Presumido criado pelo Plan 4 (splash) | Preservar |

### 5. Ícones unicode substituídos por SVG sprite

Durante os Plans 3-5, várias referências a emojis unicode (🚒, ✈, 🛡, 🆘, 🗼, ⚠, ❌, ✓) usadas em cr-chips, badges de categoria, mensagens de status, foram substituídas por `<svg><use href="#icon-..."/></svg>` a partir do sprite. Algumas referências podem ter ficado para trás por serem usadas em texto JS (dentro de template literals de PDFs, por exemplo). **A Task 5 faz uma varredura e decide caso-a-caso**: se estão em PDF export (JS string literal), ficam; se estão em HTML directo, são substituídas se houver icon equivalente — caso contrário documentadas como "intentional unicode".

### 6. Scripts em `scripts/` deprecados

| Ficheiro | Origem | Decisão |
|---|---|---|
| `scripts/build-all.py` | Etapa 2 | **Preservar** — é o orquestrador de produção |
| `scripts/ds_build_helpers.py` | Plan 1 | **Preservar** — é usado por `build.py` de ambos os portais |
| `scripts/validate_plan1_extended.py` | Plan 1 (helper local de validação) | **Remover** — era scratch para validação do Plan 1, não é importado por ninguém, já não tem sentido |
| `scripts/verify_consolidation.py` | Plan 2 (helper de verificação byte-level) | **Arquivar** — mover para `docs/reference/plan-2-tools/verify_consolidation.py` em vez de apagar, preserva contexto histórico se alguém quiser reconstruir o processo de consolidação |
| `tests/test_verify_consolidation.py` | Plan 2 | **Arquivar** — mover para `docs/reference/plan-2-tools/test_verify_consolidation.py` junto com o script. Não pode viver em `tests/` porque pytest vai tentar executá-lo e falhar (o script que ele importa deixa de estar em `scripts/`) |

A decisão de arquivar vs apagar: arquivar. O Plan 2 foi uma operação complexa com byte-level invariants; se algum dia houver regressão que force uma re-consolidação, ter o tool arquivado no repositório poupa horas. O custo é zero (4 KB).

### 7. Documentação por escrever / actualizar

| Ficheiro | Estado | Acção |
|---|---|---|
| `docs/design-system-guide.md` | Não existe | **Criar** (Task 9, ~500 linhas) |
| `docs/ARCHITECTURE.md` | Existe (v2.0.0-beta.1, não menciona DS) | **Actualizar** (Task 10) |
| `shared/styles/README.md` | Existe (versão Plan 1) | **Expandir para versão final** (Task 11) |
| `shared/scripts/README.md` | Não existe | **Criar** (Task 12) |
| `shared/README.md` | Existe (versão pré-Plan-1, obsoleta) | **Reescrever** (Task 13) |
| `README.md` (raiz) | Existe, menciona apenas Fase 1 Etapa 4 | **Actualizar** (Task 14) |
| `docs/CHANGELOG.md` | Última entrada `[2.0.0-beta.1]` | **Adicionar entrada `[2.1.0-alpha.1]` detalhada** (Task 15) |
| `docs/releases/v2.1.0-alpha.1.md` | Não existe — directoria não existe | **Criar directoria e ficheiro** (Task 16) |

### 8. Temporários de desenvolvimento (fora do repositório)

Os Plans 1 e 2 deixaram baselines em `d:/tmp/`:
- `d:/tmp/plan1-baseline/` (Plan 1)
- `d:/tmp/plan2-baseline-source/` (Plan 2)
- `d:/tmp/plan2-baseline/` (Plan 2)

Não estão no repo, não precisam de ser limpos pelo plano. O utilizador pode apagar manualmente quando quiser. **Não tocar a partir do plano.**

---

## File Structure (Plan 6 scope)

### Files to **create** (~8 novos)

```
Portal_DREA/
├── scripts/
│   └── rename_ds_namespace.py                       NEW (~120 linhas)
├── tests/
│   └── test_rename_ds_namespace.py                  NEW (~200 linhas)
├── docs/
│   ├── design-system-guide.md                       NEW (~500 linhas)
│   └── releases/
│       └── v2.1.0-alpha.1.md                        NEW (directoria nova + ficheiro)
├── shared/
│   └── scripts/
│       └── README.md                                NEW (~150 linhas)
└── docs/reference/plan-2-tools/                     NEW (directoria de arquivo)
    ├── README.md                                    NEW (explica porque está aqui)
    ├── verify_consolidation.py                      MOVED from scripts/
    └── test_verify_consolidation.py                 MOVED from tests/
```

### Files to **modify**

```
Portal_DREA/
├── VERSION                                          2.0.0-beta.1 → 2.1.0-alpha.1
├── README.md                                        status update + link to guide
├── docs/
│   ├── ARCHITECTURE.md                              nova secção Design System
│   └── CHANGELOG.md                                 entrada [2.1.0-alpha.1]
├── shared/
│   ├── README.md                                    reescrito
│   └── styles/
│       └── README.md                                expandido para versão final
│
└── (TODOS os ficheiros CSS em shared/styles/**/*.css e os 2 source HTMLs
   são modificados pelo script de rename da Task 1 — lista completa em
   Fact Sheet § 1 e § 3)
```

### Files to **delete**

```
Portal_DREA/
├── scripts/
│   └── validate_plan1_extended.py                   DELETED (Task 6)
├── shared/
│   └── assets/
│       ├── logo-sga.png                             DELETED (Task 4)
│       └── logo-sga-white.png                       DELETED (Task 4)
```

### Files to **move** (archive)

```
Portal_DREA/
├── scripts/verify_consolidation.py                  →  docs/reference/plan-2-tools/verify_consolidation.py
└── tests/test_verify_consolidation.py               →  docs/reference/plan-2-tools/test_verify_consolidation.py
```

---

## Task 0: Prerequisites — worktree setup + baseline verification

> **REQUIRED SUB-SKILL**: `superpowers:using-git-worktrees`

### Purpose

Criar um worktree isolado `../Portal_DREA-release` na branch `feat/release-v2.1.0-alpha.1`, verificar que os Plans 3-5 estão de facto mergeados na `main` (invariant: nenhum consumer de `--dark-blue` deve sobreviver), capturar baselines para as verificações de não-regressão, e garantir que `pytest` + `build-all.py` estão green antes de tocar em qualquer coisa.

**Crítico**: se qualquer check desta task falhar, o Plan 6 **não começa**. Falha aqui é sinal de que os plans anteriores deixaram trabalho por fazer — resolve-se nesses planos, não neste.

### Steps

- [ ] **Step 1: Create worktree**
  ```bash
  cd d:/VSCode_Claude/03-Resende/Portal_DREA
  rtk git status                                    # deve estar clean
  rtk git fetch origin
  rtk git worktree add ../Portal_DREA-release -b feat/release-v2.1.0-alpha.1 main
  cd ../Portal_DREA-release
  rtk git status                                    # confirmar branch nova
  ```

- [ ] **Step 2: Verify Plans 3-5 are merged**

  Confirmar que os commits finais dos Plans 3, 4 e 5 estão presentes na `main` do worktree. Os SHAs exactos dependem do trabalho feito em paralelo — usar mensagens de commit como proxy:
  ```bash
  rtk git log --oneline --grep="Plan 3" | head -5   # deve existir
  rtk git log --oneline --grep="Plan 4" | head -5   # deve existir
  rtk git log --oneline --grep="Plan 5" | head -5   # deve existir
  ```
  Se algum dos três não aparecer, **parar** e confirmar com o utilizador se os plans realmente mergearam.

- [ ] **Step 3: Verify build is green on baseline**
  ```bash
  rtk python scripts/build-all.py
  ```
  Deve sair com exit code 0. Os builds do COE e SSCI são escritos para `packages/*/dist/Portal_*_AWM.html`. Guardar os SHA-256 destes ficheiros para comparação na Task 7:
  ```bash
  rtk python -c "import hashlib, pathlib; print('COE:', hashlib.sha256(pathlib.Path('packages/portal-coe/dist/Portal_COE_AWM.html').read_bytes()).hexdigest())"
  rtk python -c "import hashlib, pathlib; print('SSCI:', hashlib.sha256(pathlib.Path('packages/portal-ssci/dist/Portal_PSCI_AWM.html').read_bytes()).hexdigest())"
  ```
  Gravar ambos os hashes num ficheiro temporário `d:/tmp/plan6-baseline-hashes.txt`. Estes **não** vão ser invariant do rename (o rename muda bytes do output) — são o snapshot "antes" para diagnóstico se alguma coisa correr mal.

- [ ] **Step 4: Verify test suite is green**
  ```bash
  rtk python -m pytest tests/ -q
  ```
  Todos os testes devem passar. Se algum falha, **parar** — não é responsabilidade deste plano arranjar testes de plans anteriores.

- [ ] **Step 5: Verify legacy `--dark-blue` has no consumers**

  Este é o check mais importante da Task 0. Os Plans 3-4 deviam ter removido todos os `var(--dark-blue)`, `var(--medium-blue)`, etc. dos dois source HTMLs. O `:root` legado ainda existe (é removido na Task 3 deste plano), mas **os consumidores** têm que estar todos migrados:
  ```bash
  # Deve devolver ZERO matches em ambos os ficheiros.
  # Se devolver qualquer coisa, é bug dos Plans 3-4 e Plan 6 não continua.
  rtk grep "var\(--dark-blue\)" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep "var\(--medium-blue\)" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep "var\(--light-blue\)" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep "var\(--warning-red\)" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep "var\(--success-green\)" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep "var\(--alert-yellow\)" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep "var\(--gray-light\)" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep "var\(--gray-dark\)" packages/portal-coe/src/Portal_COE_AWM.source.html
  ```
  Repetir para o SSCI. Se algum devolver match > 0 → **abortar Plan 6**, registar no todo backlog, voltar aos plans respectivos.

  **Nota operacional**: o `grep` acima é feito com regex de escape de parênteses porque `--dark-blue` dentro do `:root { ... }` legado ainda existe como declaração (não como `var()`). Só nos importam os **consumers** (`var(--dark-blue)`), não a declaração propriamente dita.

- [ ] **Step 6: Enumerate actual `shared/styles/` tree**

  A Fact Sheet § 1 é uma previsão baseada na spec. Agora geramos a lista autoritativa real que vai ser input do script de rename:
  ```bash
  rtk find shared/styles -name "*.css" > d:/tmp/plan6-css-files.txt
  rtk find shared/scripts -name "*.js" > d:/tmp/plan6-js-files.txt
  ```
  Comparar com a Fact Sheet — se houver discrepâncias (ficheiros que a spec dizia existirem mas não existem, ou vice-versa), actualizar os passos das tasks subsequentes antes de executar.

- [ ] **Step 7: Snapshot ocorrences of `--ds-*`**

  Contar quantas ocorrências existem em cada ficheiro — serve para validação estatística do rename:
  ```bash
  rtk grep -c "\-\-ds\-" shared/styles/tokens/primitive.css
  rtk grep -c "\-\-ds\-" shared/styles/tokens/semantic.css
  rtk grep -c "\-\-ds\-" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep -c "\-\-ds\-" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  # ... etc para todos os ficheiros na Fact Sheet
  ```
  Somar os totais num ficheiro `d:/tmp/plan6-ds-occurrences-before.txt`. Depois do rename (Task 1) o total deve ser **zero em todos eles**.

- [ ] **Step 8: Smoke test manual no browser (baseline)**

  Abrir `packages/portal-coe/dist/Portal_COE_AWM.html` e `packages/portal-ssci/dist/Portal_PSCI_AWM.html` em Chrome. Fazer login, navegar pelas secções principais (Dashboard, Contactos, Verificação Mensal no COE; Registo de Serviço, Inspecções, Stock no SSCI). Tirar **5 screenshots de referência por portal** em `d:/tmp/plan6-baseline-screenshots/`. São o ponto de comparação visual para o smoke test da Task 7.

**Verification**: Task 0 completa se:
- Worktree criado e branch `feat/release-v2.1.0-alpha.1` activa
- `build-all.py` exit 0
- `pytest` exit 0
- Zero consumers de `var(--dark-blue)` / `var(--medium-blue)` / etc. nos source HTMLs
- Lista de ficheiros CSS/JS com `--ds-*` capturada
- Hashes e screenshots baseline guardados em `d:/tmp/plan6-*`

**Commit**: Task 0 não tem commit (é setup e verificação apenas).

---

## Task 1: Rename script — TDD foundation

> **REQUIRED SUB-SKILL**: `superpowers:test-driven-development`

### Purpose

Criar `scripts/rename_ds_namespace.py` que faz a transformação textual `--ds-X` → `--X` de forma idempotente, segura, e com diff inspeccionável (`--dry-run`). A criticidade do rename justifica TDD rigoroso: um único erro de regex parte TUDO. O script é escrito **antes** de ser corrido sequer uma vez em produção.

### Design

**Algoritmo**: para cada ficheiro dado como input, aplicar a substituição regex:
- Padrão: `(--)ds-(\w)` → `\1\2`
- Isto transforma `--ds-blue-800` em `--blue-800`, `--ds-status-warning-bg` em `--status-warning-bg`, `var(--ds-x)` em `var(--x)`, etc.
- A regex exige que o caractere depois do `ds-` seja `\w` (word char), para não apanhar `--ds- ` (com espaço) ou `--ds-` no fim de linha — proteção contra edge cases.

**O que o script NÃO faz**:
- Não toca hex colors, valores, nomes de classes CSS, ou nomes de atributos HTML.
- Não toca strings dentro de comentários HTML (`<!-- ... -->`) ou CSS (`/* ... */`) — ver discussão de design abaixo.
- Não modifica ficheiros que não recebem via argumentos.

**Decisão de design sobre comentários**: o espec diz "protegendo comentários if possible". Depois de análise, **decidimos renomear DENTRO dos comentários também**. Razão:
1. Os comentários nos ficheiros `shared/styles/tokens/*.css` documentam os próprios tokens (ex: `/* ds-blue-800 is the official SGA dark blue */`) e ficariam incoerentes se não fossem actualizados.
2. Não renomear em comentários obriga o script a fazer parse CSS propriamente dito (AST), o que inflaciona complexidade e introduz risco.
3. Regex simples `(--)ds-(\w)` só apanha tokens word-boundary válidos; não corre perigo de apanhar texto prosado tipo "o nosso DS usa..." (não começa com `--`).

**Exceção importante**: o comentário descritivo em `shared/styles/tokens/primitive.css` linhas 7-9 diz literalmente "são prefixed `--ds-*` to avoid collision... The prefix is removed in Plan 5 when legacy is cleaned up." — este comentário fica **sem sentido** depois do rename (e refere-se ao plan errado — diz Plan 5 mas é este Plan 6). A Task 2 trata explicitamente de actualizar os comentários descritivos, para não deixar mensagens contraditórias no código.

### Steps

- [ ] **Step 1: Write the failing tests first (TDD Red)**

  Criar `tests/test_rename_ds_namespace.py` com os seguintes test cases:

  ```python
  """Unit tests for scripts/rename_ds_namespace.py.

  TDD guard for the Plan 6 rename operation. Every edge case that could
  go wrong in the live rename must have a corresponding test here FIRST.
  """
  import sys
  from pathlib import Path
  import pytest

  REPO_ROOT = Path(__file__).resolve().parent.parent
  sys.path.insert(0, str(REPO_ROOT / "scripts"))
  import rename_ds_namespace as rd  # noqa: E402


  class TestRenameSingleToken:
      def test_renames_ds_blue_800_declaration(self):
          css = "--ds-blue-800: #004C7B;"
          assert rd.rename_css_text(css) == "--blue-800: #004C7B;"

      def test_renames_ds_status_warning_bg_declaration(self):
          css = "--ds-status-warning-bg: #fef5e7;"
          assert rd.rename_css_text(css) == "--status-warning-bg: #fef5e7;"

      def test_renames_var_reference(self):
          css = "color: var(--ds-brand-primary);"
          assert rd.rename_css_text(css) == "color: var(--brand-primary);"

      def test_renames_multiple_vars_same_line(self):
          css = "background: var(--ds-bg); color: var(--ds-fg);"
          assert rd.rename_css_text(css) == "background: var(--bg); color: var(--fg);"

      def test_renames_var_with_fallback(self):
          css = "color: var(--ds-fg, #000);"
          assert rd.rename_css_text(css) == "color: var(--fg, #000);"

  class TestDoesNotOverreach:
      def test_preserves_non_ds_custom_property(self):
          css = "--dark-blue: #004C7B;"
          assert rd.rename_css_text(css) == "--dark-blue: #004C7B;"
          # --dark-blue does NOT match (--)ds-(\w) — stays intact.

      def test_preserves_hex_values(self):
          css = "color: #ds004C;"
          assert rd.rename_css_text(css) == "color: #ds004C;"
          # Not a custom property — no `--` prefix.

      def test_preserves_class_names(self):
          css = ".ds-button { color: red; }"
          assert rd.rename_css_text(css) == ".ds-button { color: red; }"
          # Class selectors don't start with `--`.

      def test_preserves_text_inside_strings(self):
          js = 'console.log("--ds-foo is deprecated");'
          # Debate: do we want to rename inside string literals of JS?
          # Decision: yes — because if any JS injects CSS via textContent that
          # includes a --ds-* var reference, that reference stops working.
          # The regex operates on text, not on syntax, so it DOES rename.
          # This test documents the actual behaviour and we accept it.
          assert rd.rename_css_text(js) == 'console.log("--foo is deprecated");'

      def test_preserves_non_word_suffix(self):
          # --ds- alone (no word char after) does NOT match — safety net.
          text = "this --ds- should not match"
          assert rd.rename_css_text(text) == "this --ds- should not match"

      def test_preserves_partial_prefix(self):
          # --dsfoo is NOT --ds-foo (missing hyphen) — does not match.
          text = "--dsfoo: red;"
          assert rd.rename_css_text(text) == "--dsfoo: red;"

  class TestIdempotence:
      def test_double_rename_is_safe(self):
          css = "--ds-blue-800: #004C7B;"
          once = rd.rename_css_text(css)
          twice = rd.rename_css_text(once)
          assert once == twice
          # Running the script twice must not corrupt output.
          # After first pass --blue-800 has no `ds-` prefix, so the pattern
          # doesn't match on the second pass — safe.

  class TestFileOperations:
      def test_dry_run_does_not_write(self, tmp_path: Path):
          css_file = tmp_path / "test.css"
          original = "--ds-blue-800: #004C7B;\n--ds-fg: #000;\n"
          css_file.write_text(original, encoding="utf-8")

          changes = rd.process_file(css_file, dry_run=True)

          assert changes > 0  # reports changes found
          # But file is untouched:
          assert css_file.read_text(encoding="utf-8") == original

      def test_wet_run_writes_correctly(self, tmp_path: Path):
          css_file = tmp_path / "test.css"
          css_file.write_text(
              "--ds-blue-800: #004C7B;\ncolor: var(--ds-blue-800);\n",
              encoding="utf-8",
          )

          rd.process_file(css_file, dry_run=False)

          result = css_file.read_text(encoding="utf-8")
          assert result == "--blue-800: #004C7B;\ncolor: var(--blue-800);\n"

      def test_no_occurrences_returns_zero(self, tmp_path: Path):
          css_file = tmp_path / "clean.css"
          css_file.write_text("body { color: red; }", encoding="utf-8")

          changes = rd.process_file(css_file, dry_run=False)

          assert changes == 0
          assert css_file.read_text(encoding="utf-8") == "body { color: red; }"

  class TestRealFixturesParity:
      def test_primitive_css_fixture(self, tmp_path: Path):
          """Simulates what will happen to the real primitive.css."""
          fixture = tmp_path / "primitive.css"
          fixture.write_text(
              ":root {\n  --ds-blue-800: #004C7B;\n  --ds-gray-50: #f6f8fa;\n}\n",
              encoding="utf-8",
          )
          rd.process_file(fixture, dry_run=False)
          result = fixture.read_text(encoding="utf-8")
          assert "--ds-" not in result
          assert "--blue-800: #004C7B;" in result
          assert "--gray-50: #f6f8fa;" in result
  ```

  Correr os testes: **todos devem falhar** porque `rename_ds_namespace.py` ainda não existe (ou, se existe, não tem as funções certas):
  ```bash
  rtk python -m pytest tests/test_rename_ds_namespace.py -v
  ```
  Esperado: `ModuleNotFoundError: No module named 'rename_ds_namespace'`.

- [ ] **Step 2: Write the minimum script that passes the tests (TDD Green)**

  Criar `scripts/rename_ds_namespace.py` com apenas:
  ```python
  """Rename --ds-* CSS custom properties to --* across files.

  Used once in Plan 6 to drop the transition namespace after the Design
  System migration is complete. Idempotent: running it twice is safe.

  Usage:
      python scripts/rename_ds_namespace.py --dry-run file1 file2 ...
      python scripts/rename_ds_namespace.py file1 file2 ...
  """
  from __future__ import annotations

  import argparse
  import re
  import sys
  from pathlib import Path

  _DS_PATTERN = re.compile(r"(--)ds-(\w)")


  def rename_css_text(text: str) -> str:
      """Transform --ds-X -> --X in the given string. Pure function."""
      return _DS_PATTERN.sub(r"\1\2", text)


  def process_file(path: Path, dry_run: bool) -> int:
      """Process one file. Returns the number of substitutions made (or that
      would have been made, in dry-run mode). Does NOT touch the file on disk
      if dry_run=True or if no changes are needed."""
      text = path.read_text(encoding="utf-8")
      new_text, n = _DS_PATTERN.subn(r"\1\2", text)
      if n == 0:
          return 0
      if not dry_run:
          path.write_text(new_text, encoding="utf-8")
      return n


  def main(argv: list[str] | None = None) -> int:
      parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
      parser.add_argument(
          "files",
          nargs="+",
          type=Path,
          help="Files to process (CSS, HTML, JS).",
      )
      parser.add_argument(
          "--dry-run",
          action="store_true",
          help="Report changes without writing to disk.",
      )
      args = parser.parse_args(argv)

      total = 0
      for f in args.files:
          if not f.exists():
              print(f"WARN: {f} does not exist, skipping", file=sys.stderr)
              continue
          n = process_file(f, dry_run=args.dry_run)
          status = "(dry-run)" if args.dry_run else ""
          print(f"{f}: {n} replacements {status}")
          total += n

      print(f"\nTotal: {total} replacements across {len(args.files)} files")
      return 0


  if __name__ == "__main__":
      raise SystemExit(main())
  ```

  Correr os testes — agora devem passar todos:
  ```bash
  rtk python -m pytest tests/test_rename_ds_namespace.py -v
  ```

- [ ] **Step 3: Commit the TDD package atomically**
  ```bash
  rtk git add scripts/rename_ds_namespace.py tests/test_rename_ds_namespace.py
  rtk git commit -m "$(cat <<'EOF'
  feat(ds): add rename_ds_namespace.py helper with TDD coverage

  Introduces scripts/rename_ds_namespace.py — a regex-based helper that
  transforms --ds-X → --X in CSS/HTML/JS files, idempotently and safely.
  Built TDD-first with 14 unit tests covering:

  - Basic rename (declarations and var() references)
  - Multiple replacements per line
  - var() with fallback values
  - Non-overreach (--dark-blue, hex values, class names, partial prefixes)
  - Idempotence (double rename is a no-op)
  - Dry-run mode (reports without writing)
  - Real fixture parity with primitive.css

  Used in Plan 6 Task 2 to drop the DS transition namespace once the
  migration is complete. Atomic operation.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Task 1 completa quando:
- `scripts/rename_ds_namespace.py` existe e importável
- `tests/test_rename_ds_namespace.py` existe
- `python -m pytest tests/test_rename_ds_namespace.py -v` — 14/14 passa
- Commit criado, worktree clean

---

## Task 2: Execute the rename — dry run, inspect, apply

### Purpose

Correr o script da Task 1 contra **todos** os ficheiros do Plan 6 Fact Sheet § 1-3 em **dry-run primeiro**. Inspeccionar o output. Só depois de confirmado o dry-run bate certo, aplicar o wet-run num único commit atómico. Este é o momento mais arriscado do Plan 6.

### Steps

- [ ] **Step 1: Build the file list**

  Criar um ficheiro `d:/tmp/plan6-files-to-rename.txt` com todos os paths absolutos, um por linha. Composição:
  ```bash
  # Gerar a lista a partir do snapshot da Task 0 Step 6:
  cat d:/tmp/plan6-css-files.txt > d:/tmp/plan6-files-to-rename.txt
  cat d:/tmp/plan6-js-files.txt >> d:/tmp/plan6-files-to-rename.txt
  echo "packages/portal-coe/src/Portal_COE_AWM.source.html" >> d:/tmp/plan6-files-to-rename.txt
  echo "packages/portal-ssci/src/Portal_PSCI_AWM.source.html" >> d:/tmp/plan6-files-to-rename.txt
  ```
  Rever manualmente a lista — deve ter aproximadamente 30-40 linhas. Se for muito maior, é sinal que alguma coisa da Task 0 Step 6 não foi filtrada. Se for muito menor, alguma cousa do `shared/styles/` não foi encontrada.

- [ ] **Step 2: Dry-run against all files**
  ```bash
  rtk python scripts/rename_ds_namespace.py --dry-run $(cat d:/tmp/plan6-files-to-rename.txt)
  ```
  Output esperado: uma linha por ficheiro com o número de substituições + o total acumulado no fim. Exemplo:
  ```
  shared/styles/tokens/primitive.css: 52 replacements (dry-run)
  shared/styles/tokens/semantic.css: 58 replacements (dry-run)
  shared/styles/tokens/density-compact.css: 14 replacements (dry-run)
  ...
  packages/portal-coe/src/Portal_COE_AWM.source.html: 347 replacements (dry-run)
  packages/portal-ssci/src/Portal_PSCI_AWM.source.html: 128 replacements (dry-run)

  Total: 1284 replacements across 37 files
  ```
  Comparar o total com o snapshot da Task 0 Step 7 — **têm que bater exactamente**.

- [ ] **Step 3: Inspect the expected diff manually**

  Para cada ficheiro, fazer um check surgical. Escolher 3 ficheiros representativos:
  1. `shared/styles/tokens/primitive.css` — é o ficheiro fonte de todos os primitives
  2. `shared/styles/components/button.css` (ou equivalente) — um consumer típico
  3. `packages/portal-coe/src/Portal_COE_AWM.source.html` — o consumer mais complexo

  Para cada um, correr o script com `--dry-run` + um `grep` antes/depois:
  ```bash
  rtk grep -c "\-\-ds\-" shared/styles/tokens/primitive.css
  # guardar o número
  rtk python -c "
  from pathlib import Path
  import sys
  sys.path.insert(0, 'scripts')
  import rename_ds_namespace as rd
  text = Path('shared/styles/tokens/primitive.css').read_text(encoding='utf-8')
  new = rd.rename_css_text(text)
  # contar --ds- no output
  import re
  print('remaining --ds-:', len(re.findall(r'--ds-', new)))
  print('first 500 chars of new:')
  print(new[:500])
  "
  ```
  Esperado: `remaining --ds-: 0`. Se não for 0, **parar** — há um edge case que o script não está a apanhar e os testes da Task 1 não cobriram. Voltar à Task 1 Step 1 e adicionar o test case.

- [ ] **Step 3.5: Create safety tag (pre-rename rollback anchor)**

  Antes de mutar o filesystem, criar uma tag temporária local que marca o estado pré-rename. É o handle de rollback rápido se o wet-run correr mal:
  ```bash
  rtk git tag plan6-pre-rename-safety
  # Rollback de emergência (se algum step 5-8 falhar):
  #   rtk git reset --hard plan6-pre-rename-safety
  ```
  Esta tag é apagada no fim do Plan 6 (ou manualmente depois da Task 18) — não deve aparecer em origin.

- [ ] **Step 4: Apply the wet run**
  ```bash
  rtk python scripts/rename_ds_namespace.py $(cat d:/tmp/plan6-files-to-rename.txt)
  ```
  Output idêntico ao dry-run mas sem a tag `(dry-run)`. O filesystem é modificado.

- [ ] **Step 5: Automated post-condition checks**

  Todos estes checks têm que passar. Se algum falhar, **fazer `git restore .` imediatamente** e voltar ao debug:
  ```bash
  # Check 1: zero ocorrências de --ds- em todos os ficheiros processados
  for f in $(cat d:/tmp/plan6-files-to-rename.txt); do
    count=$(rtk grep -c "\-\-ds\-" "$f" 2>/dev/null || echo 0)
    if [ "$count" != "0" ]; then
      echo "FAIL: $f still has $count --ds- occurrences"
    fi
  done

  # Check 2: a nova forma existe (sanity)
  rtk grep -c "\-\-blue-800" shared/styles/tokens/primitive.css  # deve ser > 0
  rtk grep -c "var(--brand-primary)" shared/styles/tokens/semantic.css  # deve ser > 0

  # Check 3: o ficheiro de density-compact ainda tem os 4 tokens de espaço
  rtk grep "\-\-space-" shared/styles/tokens/density-compact.css
  # deve mostrar --space-1, --space-2, etc.
  ```

- [ ] **Step 6: Rebuild and verify**
  ```bash
  rtk python scripts/build-all.py
  ```
  Deve sair com exit 0. Os `.html` em `dist/` são novos (bytes diferentes dos do Task 0 Step 3) mas o build em si tem que passar o validator de sintaxe JS.

- [ ] **Step 7: Run the test suite**
  ```bash
  rtk python -m pytest tests/ -q
  ```
  Tudo tem que passar. **Importante**: o teste da Task 1 continua a testar a função `rename_css_text` no contexto original (com `--ds-*`) — é um teste de unit da função, não de ficheiros. Os helpers da Task 1 usam fixtures tmp_path, não ficheiros reais do repo. Logo os testes continuam válidos mesmo depois do rename.

- [ ] **Step 8: Manual smoke test in Chrome**

  Abrir os dois `.html` em Chrome. Fazer os mesmos 5 fluxos capturados nos screenshots da Task 0 Step 8. Comparar a olho.

  **Esperado**: zero diferenças visuais. Se houver qualquer diferença — mesmo subtil (alinhamento, cor, spacing) — **parar e investigar**. O rename é garantidamente uma transformação textual inofensiva. Se há diff visual é porque alguma coisa na cascata ficou partida — provavelmente o script apanhou uma ocorrência que não devia, ou deixou uma ocorrência que devia.

- [ ] **Step 9: Atomic commit**
  ```bash
  rtk git add -A  # muitos ficheiros afectados
  rtk git status   # confirmar que só os ficheiros esperados estão staged
  rtk git commit -m "$(cat <<'EOF'
  refactor(ds): drop --ds-* transition namespace globally

  Now that both portals are fully migrated to the Design System SGA
  (Plans 1-5), the transition prefix on tokens is removed:

    --ds-blue-800        → --blue-800
    --ds-neutral-canvas  → --neutral-canvas
    --ds-status-warning-bg → --status-warning-bg
    ...

  Files touched (<N> files):
    - shared/styles/**/*.css (tokens, base, chrome, components, print)
    - shared/scripts/**/*.js (awm-*, utilities)
    - packages/portal-coe/src/Portal_COE_AWM.source.html
    - packages/portal-ssci/src/Portal_PSCI_AWM.source.html

  Operation: rename_ds_namespace.py with regex (--)ds-(\w) → \1\2,
  applied under 14 TDD unit tests. Verified zero visual diff against
  baseline (screenshots) for both portals in Chrome.

  Total: <N> replacements across <M> files.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Task 2 completa quando:
- Zero ocorrências `--ds-` em qualquer ficheiro do repo (Step 5 check 1)
- `build-all.py` exit 0
- `pytest` exit 0
- Smoke test manual passa com zero diffs visuais contra baseline
- Commit atómico criado, worktree clean

**Rollback se falhar**: `git reset --hard HEAD~1` volta ao estado antes do commit. Os ficheiros voltam ao estado `--ds-*`. Zero perda.

---

## Task 3: Remove legacy `:root` residual from both source HTMLs

### Purpose

O `:root { --dark-blue, --medium-blue, ... }` no bloco CSS legado de cada source HTML já não tem consumidores depois dos Plans 3-4 (verificado na Task 0 Step 5). Remover essas linhas para eliminar dead code e deixar o source mais limpo.

### Steps

- [ ] **Step 1: Re-confirm zero consumers (defensive)**

  A Task 0 já verificou isto, mas voltamos a verificar depois do rename da Task 2 — é possível (improvável mas não impossível) que a Task 2 tenha criado um `var(--dark-blue)` novo por erro:
  ```bash
  rtk grep "var(--dark-blue)" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep "var(--medium-blue)" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep "var(--dark-blue)" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  rtk grep "var(--medium-blue)" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  ```
  Todos devem ser zero.

- [ ] **Step 2: Remove `:root` block from COE source**

  Editar `packages/portal-coe/src/Portal_COE_AWM.source.html`. Remover as linhas 16-27 (baseline) do bloco `:root { ... }`. A remoção é feita com a ferramenta `Edit` numa única operação, substituindo o bloco inteiro por uma linha em branco (ou nada, ajustando o contexto acima/abaixo).

  Alternativa segura: manter o bloco `:root {}` vazio se o editor visual do contribuidor a seguir precisar de um ponto de âncora. Decisão do plano: **remover totalmente**, incluindo o `:root {}` e as suas chavetas. Dead code é dead code.

- [ ] **Step 3: Remove `:root` block from SSCI source**

  Mesma operação em `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`. As linhas exactas dependem do baseline actual mas o padrão é idêntico.

- [ ] **Step 4: Build and verify zero visual diff**
  ```bash
  rtk python scripts/build-all.py
  rtk python -m pytest tests/ -q
  ```
  Abrir ambos os `.html` em Chrome — zero diff visual. Se houver diff, é porque a Task 0 Step 5 não apanhou todos os consumidores. Investigar.

- [ ] **Step 5: Commit**
  ```bash
  rtk git add packages/portal-coe/src/Portal_COE_AWM.source.html packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  rtk git commit -m "$(cat <<'EOF'
  chore(ds): remove legacy :root block from both portal sources

  The legacy SGA palette declaration (--dark-blue, --medium-blue,
  --light-blue, --warning-red, --success-green, --alert-yellow, etc.)
  was preserved until now to give the Plans 3-4 migrations room to
  manoeuvre. All consumers (var(--dark-blue), etc.) were removed by
  those plans — verified zero hits before this commit.

  Net result: the legacy :root { ... } block is fully dead code and
  removed. Both portals now source all colours exclusively from the
  Design System tokens in shared/styles/tokens/.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Task 3 completa quando:
- Nenhum `--dark-blue`, `--medium-blue`, etc. em nenhum source HTML
- `build-all.py` exit 0, `pytest` exit 0
- Smoke test manual: zero diff visual
- Commit atómico feito

---

## Task 4: Remove `PLAN 2 CONSOLIDATION` banners

### Purpose

Os banners foram instalados pelo Plan 2 para documentar a proveniência do bloco consolidado de CSS legado. Serviram o propósito durante as Tasks de migração (Plans 3-4) porque facilitavam localizar secções específicas. Agora que esses Plans terminaram, os banners são ruído.

### Steps

- [ ] **Step 1: Confirm banner locations**
  ```bash
  rtk grep -c "PLAN 2 CONSOLIDATION" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep -c "PLAN 2 CONSOLIDATION" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  ```
  Para COE, esperar ~22 hits. Para SSCI, esperar ~10 (menor devido ao menor número de blocks originais consolidados).

- [ ] **Step 2: Remove all banner comments**

  Há dois tipos de banner:
  1. **Banners CSS** dentro do `<style>` block 1: `/* ========= * PLAN 2 CONSOLIDATION — block N ... * ========= */`
  2. **Banners HTML** onde os blocos originais estavam: `<!-- PLAN 2 CONSOLIDATION: original block N merged into block 1 above -->`

  O Python/regex mais simples para isto é um script one-off. Podemos reutilizar o padrão de `verify_consolidation.py::BANNER_PATTERN` que já remove estes banners para fins de comparação. **Decisão**: escrever um helper ad-hoc inline para este commit, não um script permanente (diferente do rename_ds_namespace.py que é reutilizável).

  ```python
  # Inline Python helper (NOT committed as a script — one-off operation):
  # d:/tmp/plan6-strip-banners.py
  import re
  from pathlib import Path

  CSS_BANNER = re.compile(
      r"^[ \t]*/\*\s*=+\s*\n[ \t]*\*\s*PLAN 2 CONSOLIDATION.*?\*/[ \t]*\n",
      re.DOTALL | re.MULTILINE,
  )
  HTML_BANNER = re.compile(
      r"^[ \t]*<!-- PLAN 2 CONSOLIDATION:.*?-->\n",
      re.MULTILINE,
  )

  for path in [
      Path("packages/portal-coe/src/Portal_COE_AWM.source.html"),
      Path("packages/portal-ssci/src/Portal_PSCI_AWM.source.html"),
  ]:
      text = path.read_text(encoding="utf-8")
      text = CSS_BANNER.sub("", text)
      text = HTML_BANNER.sub("", text)
      path.write_text(text, encoding="utf-8")
      print(f"{path}: banners stripped")
  ```

  Correr via `python d:/tmp/plan6-strip-banners.py`. Verificar:
  ```bash
  rtk grep -c "PLAN 2 CONSOLIDATION" packages/portal-coe/src/Portal_COE_AWM.source.html  # 0
  rtk grep -c "PLAN 2 CONSOLIDATION" packages/portal-ssci/src/Portal_PSCI_AWM.source.html  # 0
  ```

- [ ] **Step 3: Build and verify**
  ```bash
  rtk python scripts/build-all.py
  rtk python -m pytest tests/ -q
  ```
  Smoke test manual em Chrome — zero diff visual.

- [ ] **Step 4: Commit**
  ```bash
  rtk git add packages/portal-coe/src/Portal_COE_AWM.source.html packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  rtk git commit -m "$(cat <<'EOF'
  chore(ds): remove PLAN 2 CONSOLIDATION breadcrumb banners

  The banners installed by Plan 2 to mark the provenance of the
  consolidated legacy CSS block are no longer useful now that the
  block itself is gone (via Plans 3-4). Removing them leaves the
  source HTMLs cleaner for future contributors.

  Banners removed:
  - COE: 22 banner comments (11 CSS banners + 11 HTML breadcrumb comments)
  - SSCI: ~10 banner comments

  Zero visual diff vs previous commit (banners are comments, already
  invisible in rendered HTML).

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Task 4 completa quando:
- Zero `PLAN 2 CONSOLIDATION` em ambos os sources
- Builds + tests green
- Visual smoke test green
- Commit atómico feito

---

## Task 5: Remove deprecated PNG assets

### Purpose

Os PNGs `logo-sga.png` e `logo-sga-white.png` foram os logótipos originais da v1.x. O Plan 4 criou `logo-sga-mark.svg` e `logo-sga-full.svg` como substitutos canónicos (inline SVG via `{{LOGO_SGA_MARK}}` e `{{LOGO_SGA_FULL}}` nos sources). Os PNGs ficaram até agora como fallback mental. A Task 5 apaga-os.

**Decisão conservadora**: apagar, não arquivar. Razões:
- O SVG é matematicamente superior (escalável, base64 compacto)
- O `logo-sga-white.png` foi desenhado para um dark theme que nunca existiu
- Histórico preservado pelo próprio git (`git show bc11d89:shared/assets/logo-sga.png > recovered.png`)
- Documentar a recuperação no CHANGELOG da Task 15

### Steps

- [ ] **Step 1: Verify no consumers**
  ```bash
  rtk grep -rn "logo-sga.png" packages/ shared/
  rtk grep -rn "logo-sga-white.png" packages/ shared/
  ```
  Deve devolver zero matches fora de comentários e documentação. Se houver consumers em código activo, **parar** — os Plans 3-4 não completaram a migração.

- [ ] **Step 2: Delete the PNGs**
  ```bash
  rtk git rm shared/assets/logo-sga.png shared/assets/logo-sga-white.png
  ```

- [ ] **Step 3: Verify build still green**
  ```bash
  rtk python scripts/build-all.py
  rtk python -m pytest tests/ -q
  ```
  Smoke test manual em Chrome — logo SGA no shell bar e splash devem aparecer (são os novos SVGs). Zero diff visual.

- [ ] **Step 4: Commit**
  ```bash
  rtk git commit -m "$(cat <<'EOF'
  chore(ds): remove deprecated logo-sga PNG assets

  Plan 4 introduced logo-sga-mark.svg (shell bar) and logo-sga-full.svg
  (splash screen) as canonical inline SVG sources for the SGA logo.
  The legacy PNG assets are no longer consumed.

  Deleted:
  - shared/assets/logo-sga.png (7,627 bytes) — superseded by logo-sga-full.svg
  - shared/assets/logo-sga-white.png (10,858 bytes) — designed for dark theme
    which was explicitly rejected by the Design System spec (light theme only)

  Recovery note: if a downstream fork needs these PNGs, they can be
  retrieved from git history with:
    git show bc11d89:shared/assets/logo-sga.png > logo-sga.png
    git show bc11d89:shared/assets/logo-sga-white.png > logo-sga-white.png

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Task 5 completa quando PNGs removidos, builds green, visual smoke test green, commit atómico feito.

---

## Task 6: Clean up stale scripts and archive Plan 2 tools

### Purpose

Dois movimentos:
1. **Apagar** `scripts/validate_plan1_extended.py` — era um helper scratch do Plan 1 para validação local, sem valor futuro.
2. **Arquivar** `scripts/verify_consolidation.py` + `tests/test_verify_consolidation.py` — foram tools críticos do Plan 2 (verificação byte-level da consolidação de CSS). Manter em `docs/reference/plan-2-tools/` para posteridade.

### Steps

- [ ] **Step 1: Create archive directory**
  ```bash
  rtk ls docs/reference  # deve existir
  mkdir -p docs/reference/plan-2-tools
  ```

- [ ] **Step 2: Move Plan 2 tools into archive**
  ```bash
  rtk git mv scripts/verify_consolidation.py docs/reference/plan-2-tools/verify_consolidation.py
  rtk git mv tests/test_verify_consolidation.py docs/reference/plan-2-tools/test_verify_consolidation.py
  ```

- [ ] **Step 3: Create archive README**

  Escrever `docs/reference/plan-2-tools/README.md` a explicar:
  - O que os ficheiros fazem
  - Quando foram usados (Plan 2, 2026-04-11)
  - Porque estão aqui e não em `scripts/` ou `tests/`
  - Como reutilizá-los caso alguém precise de re-consolidar CSS no futuro

  Conteúdo sugerido (~50 linhas):
  ```markdown
  # Plan 2 Tools — Archived Reference

  These two files supported the Portal DREA Design System SGA
  migration **Plan 2: Style Block Consolidation** (2026-04-11).

  ## What they do

  - `verify_consolidation.py` — CLI + library for verifying that a
    single consolidated `<style>` block in a source HTML is byte-
    identical (modulo banner comments) to the concatenation of the
    original N blocks it replaces.
  - `test_verify_consolidation.py` — pytest unit tests for the above.

  ## Why they are archived, not deleted

  Plan 2 was a byte-level operation on ~100 KB of CSS across 11
  blocks of the COE source and 4 of the SSCI. If a future regression
  ever forces a re-consolidation (or a similar textual equivalence
  check), having these tools in-repo saves hours of rebuild. The
  cost is zero (~12 KB of text).

  ## Why they are not in scripts/ or tests/

  - `scripts/verify_consolidation.py` referenced paths that no
    longer exist after Plans 3-4 removed the legacy CSS block. It
    cannot be run against the current source HTMLs meaningfully.
  - `tests/test_verify_consolidation.py` imports the script above;
    pytest would try to collect it and fail.

  Moving both into `docs/reference/plan-2-tools/` prevents pytest
  collection and signals clearly that these are historical.

  ## Historical context

  See `docs/superpowers/plans/2026-04-11-design-system-plan-2-style-consolidation.md`
  for the full operational context.
  ```

- [ ] **Step 4: Delete `validate_plan1_extended.py`**
  ```bash
  rtk git rm scripts/validate_plan1_extended.py
  ```

- [ ] **Step 5: Verify test suite still green**
  ```bash
  rtk python -m pytest tests/ -q
  ```
  O teste do `verify_consolidation` já não será colectado (foi movido). Só ficam os tests do Plan 1 (`test_ds_build_helpers.py`) e o do Plan 6 (`test_rename_ds_namespace.py`).

- [ ] **Step 6: Commit**
  ```bash
  rtk git add docs/reference/plan-2-tools/README.md
  rtk git commit -m "$(cat <<'EOF'
  chore(repo): remove validate_plan1_extended.py, archive Plan 2 tools

  Two cleanups:

  1. scripts/validate_plan1_extended.py — deleted. Was a one-off
     local validation helper for Plan 1 (foundation dormant); not
     referenced by any script or test, no future value.

  2. scripts/verify_consolidation.py + tests/test_verify_consolidation.py
     — moved to docs/reference/plan-2-tools/. These were critical
     byte-level verification tools for Plan 2 (style block
     consolidation). Archived rather than deleted because:
       - Plan 2 was a subtle operation; the tools would save hours
         if a similar consolidation is ever needed
       - Moving out of scripts/tests/ prevents pytest collection
         errors (the script's targets no longer exist)
       - A README.md in the archive directory explains provenance

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Task 6 completa quando:
- `scripts/validate_plan1_extended.py` já não existe
- `scripts/verify_consolidation.py` e `tests/test_verify_consolidation.py` já não existem
- `docs/reference/plan-2-tools/` existe com os 3 ficheiros (2 movidos + README)
- Pytest green (só 2 test files: `test_ds_build_helpers.py` + `test_rename_ds_namespace.py`)
- Commit atómico feito

---

## Task 7: Inspect and optionally replace unicode icon residuals

### Purpose

Durante os Plans 3-5 muitas referências unicode (🚒, ✈, 🛡, 🆘, 🗼) foram substituídas por `<svg><use href="#icon-X"/></svg>`. Algumas ficaram para trás propositadamente (ex: dentro de `window.alert()`, dentro de PDFs exportados programaticamente, em templates JS de print). Esta task catalóga o que sobra e decide.

### Steps

- [ ] **Step 1: Enumerate remaining unicode icons**
  ```bash
  # Pattern: any character in the Miscellaneous Symbols / Dingbats / Emoji range
  rtk grep -Pn "[\x{1F680}-\x{1F6FF}]|[\x{2600}-\x{27BF}]|[\x{1F300}-\x{1F5FF}]|[\x{1F900}-\x{1F9FF}]" packages/portal-coe/src/Portal_COE_AWM.source.html
  rtk grep -Pn "[\x{1F680}-\x{1F6FF}]|[\x{2600}-\x{27BF}]|[\x{1F300}-\x{1F5FF}]|[\x{1F900}-\x{1F9FF}]" packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  ```

- [ ] **Step 2: Classify each hit**

  Para cada match, decidir:
  - **Intentional** (fica): está dentro de JS template literal de PDF export, `window.alert`, `console.log`, ou dentro de texto visível que propositadamente usa emoji para flavor. Exemplo: texto `"✅ Guardado"` num toast.
  - **Residual** (substituir): está em HTML markup puro onde havia um `🚒` que devia ter ficado `<svg><use href="#icon-fire-truck"/></svg>`. Exemplo: um badge de categoria no DOM.

  Registar as decisões num ficheiro temporário `d:/tmp/plan6-unicode-decisions.txt`.

- [ ] **Step 3: Apply residual replacements (if any)**

  Se houver residuais: fazer os replaces manualmente via `Edit` tool, commitando cada substituição lógica num commit separado (ou, se forem muitos pequenos e óbvios, tudo num único commit). Cada replace exige:
  - Um `icon-X` correspondente já estar no sprite.svg (Plan 1-4)
  - O substituto ser `<svg class="icon"><use href="#icon-X"/></svg>` e não quebrar o layout circundante

- [ ] **Step 4: Verify and commit**
  ```bash
  rtk python scripts/build-all.py
  rtk python -m pytest tests/ -q
  ```
  Smoke test manual em Chrome focando nas áreas afectadas. Se tudo OK:
  ```bash
  rtk git add packages/portal-coe/src/Portal_COE_AWM.source.html packages/portal-ssci/src/Portal_PSCI_AWM.source.html
  rtk git commit -m "$(cat <<'EOF'
  chore(ds): replace residual unicode emoji icons with sprite SVG

  During Plans 3-5, most unicode emoji icons were replaced with the
  canonical inline SVG sprite references. This commit catches the
  stragglers that were missed:

  [list of specific replacements]

  Intentional unicode icons (inside PDF export JS templates, console
  messages, and plain-text toasts) are preserved.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

  Se não houver residuais (tudo já foi migrado pelos Plans 3-5): a task é zero-commit, documentar no log interno.

**Verification**: Task 7 completa quando a lista de unicode remanescente está 100% classificada como "intentional" (ou os residuais foram corrigidos e commitados).

---

## Task 8: Final cleanup verification — the green gate

### Purpose

Depois das Tasks 1-7, todo o clean-up técnico está feito. Antes de avançar para a documentação, fazer uma verificação holística: builds green, tests green, zero resíduos, zero regressões visuais. Este é o **green gate** — se aqui tudo bate certo, o resto do Plan 6 é "só documentação e release" e é relativamente livre de risco.

### Steps

- [ ] **Step 1: Full clean build**
  ```bash
  rm -rf packages/portal-coe/dist packages/portal-ssci/dist
  rtk python scripts/build-all.py
  ```
  Deve sair exit 0.

- [ ] **Step 2: Full test suite**
  ```bash
  rtk python -m pytest tests/ -v
  ```
  Todos verdes. Contar quantos: esperar ~35 tests (20 do Plan 1 via `test_ds_build_helpers.py` + 13 do Plan 2 se ainda estiverem em `tests/` — mas já não estão (Task 6 moveu-os) + 14 do Plan 6 `test_rename_ds_namespace.py`). Número final: ~34 tests (20 + 14).

  **Nota**: se os Plans 3-5 adicionaram testes próprios (ex: `test_button_component.py`), contam também. O número exacto depende do estado da `main` na altura.

- [ ] **Step 3: Zero-residuo audit**
  ```bash
  # Nenhum --ds- residual
  rtk grep -rn "\-\-ds\-" shared/ packages/*/src/ | head -20

  # Nenhum --dark-blue, --medium-blue residual
  rtk grep -rn "var(--dark-blue)\|var(--medium-blue)\|var(--light-blue)\|var(--warning-red)" packages/ | head -20

  # Nenhum banner PLAN 2 CONSOLIDATION
  rtk grep -rn "PLAN 2 CONSOLIDATION" packages/ | head -20

  # Nenhum PNG logo remanescente
  rtk ls shared/assets/  # não deve incluir logo-sga.png ou logo-sga-white.png

  # Scripts arquivados
  rtk ls scripts/  # deve ter só build-all.py, ds_build_helpers.py, rename_ds_namespace.py
  ```
  Todas estas queries devem dar output vazio ou o esperado.

- [ ] **Step 4: Cross-browser smoke test**

  Smoke test manual em:
  1. **Chrome** — os 5 fluxos de referência por portal
  2. **Edge** — mesmo
  3. **Firefox** — mesmo, com foco nos modais (focus trap é historicamente frágil em Firefox)

  Comparar com os screenshots do Task 0 Step 8 — zero diff visual em todos os 3 browsers.

- [ ] **Step 5: Print preview validation**

  Em Chrome, abrir cada portal e fazer "Print" (Ctrl+P). Confirmar que:
  - Shell bar e sidebar desaparecem
  - Aparece o print header com logo SGA, nome do aeroporto, nome do portal, data, operador
  - Numeração de página funciona (`Página N de M`)
  - Tabelas longas (Verificação Mensal no COE) paginam correctamente

- [ ] **Step 6: axe DevTools WCAG scan**

  Em Chrome com axe DevTools extension, correr scan em 3 secções de cada portal:
  - **COE**: Dashboard, Contactos, Verificação Mensal
  - **SSCI**: Dashboard, Registo de Serviço, Stock

  **Esperado**: 0 violations serious/critical. Violations minor (ex: contraste de texto subtle em ~3.5:1 sob background colorido) são aceitáveis se estiverem documentadas na spec como "large-text only".

- [ ] **Step 7: Build output size sanity check**
  ```bash
  ls -la packages/portal-coe/dist/Portal_COE_AWM.html
  ls -la packages/portal-ssci/dist/Portal_PSCI_AWM.html
  ```
  Comparar com o baseline do Task 0 Step 3. Esperado:
  - Ambos os `.html` ligeiramente **mais pequenos** que o baseline (remoção de bytes dos prefixos `ds-`, banners `PLAN 2`, `:root` legado, PNGs)
  - Delta esperado: **-15 a -25 KB** por portal (muito aproximado, depende dos volumes exactos)
  - Se o delta for **positivo** (ficheiro cresceu), alguma coisa correu mal — investigar

**Verification**: Task 8 completa quando:
- Full build green, full pytest green
- Zero resíduos técnicos
- Cross-browser smoke test green (Chrome + Edge + Firefox)
- Print preview verificado
- axe DevTools sem violations críticas
- Tamanhos dos `.html` consistentes com o esperado

**Commit**: sem commit (é uma task de gate de verificação).

**Se Task 8 falhar em qualquer step**: **parar o Plan 6** e investigar. Não avançar para documentação e release se o software não está tecnicamente são.

---

## Task 9: Write `docs/design-system-guide.md`

### Purpose

Criar o guia canónico do Design System SGA — ~500 linhas em European Portuguese, cobrindo todo o DS do ponto de vista de quem o consome (outros programadores, o próprio utilizador num futuro, e agentes a portar o DS para novos portais).

### Content outline

O guia tem ~10 secções:

1. **Introdução** (~30 linhas): o que é o DS SGA, para quem, quando usar. Referência à spec original (`docs/superpowers/specs/2026-04-11-design-system-sga-design.md`) como fonte de design rationale.

2. **Arquitectura em 3 camadas** (~40 linhas): primitive / semantic / component. Regra de ouro: componentes só consomem semantic. Diagrama ASCII da cascata. Explicação de porquê.

3. **Catálogo de tokens** (~120 linhas): referência completa. **Não duplicar a spec** — copiar as tabelas canónicas da Secção 3 da spec com nota "fonte de verdade: `shared/styles/tokens/primitive.css` e `shared/styles/tokens/semantic.css`". Incluir:
   - Neutros / chrome
   - Brand SGA
   - Status (info, success, warning, alert, emergency)
   - Category (avsec-bombeiros, sga-interna, enna-navegacao, seg-ordem, externa-emg, operadores)
   - Elevation (shadows)
   - Radii
   - Motion (transitions)
   - Focus ring
   - Type scale
   - Density tokens (compact vs comfortable)

4. **Tipografia — Inter Variable** (~30 linhas): como está embebida em base64, font-feature-settings, tabular figures. Como actualizar Inter (baixar woff2 da fonte oficial, meter em `shared/assets/fonts/`, re-build).

5. **Componentes inventário** (~80 linhas): listar cada componente Tier 1-3 com:
   - Nome
   - Ficheiro (`shared/styles/components/X.css`)
   - Variantes
   - Estados
   - Exemplo de markup mínimo

6. **Chrome (shell bar, sidebar, splash, print header, footer)** (~60 linhas): HTML skeletons de cada elemento de chrome, com tokens de semantic usados, e referência aos ficheiros em `shared/styles/chrome/`.

7. **Ícones — sprite SVG inline** (~40 linhas):
   - Como funciona (`<svg><use href="#icon-X"/></svg>` + sprite em `<body>`)
   - Lista de ícones disponíveis (ou referência a `shared/assets/icons/README.md`)
   - Como adicionar um novo ícone: baixar SVG do source (Heroicons), colar em `shared/assets/icons/sources/`, regenerar sprite (manual ou script), rebuild

8. **Modos de densidade** (~30 linhas): compact (COE) vs comfortable (SSCI). Como um portal escolhe (via `portal.config.json::density`). Como um aeroporto override (via `airport-XXX.json::portals.<id>.density`).

9. **Como adicionar um novo portal** (~50 linhas): template passo-a-passo para quem vai criar Portal SOA, AVSEC ou DIRECÇÃO:
   - Criar `packages/portal-XXX/`
   - Criar `portal.config.json`
   - Criar `src/Portal_XXX_AWM.source.html` baseado num template mínimo
   - Criar `scripts/build.py` (cópia do COE/SSCI adaptada)
   - Registar em `scripts/build-all.py`
   - Correr build, confirmar

10. **WCAG compliance + testing** (~30 linhas): contrastes documentados, regra "cor nunca é o único canal", como usar axe DevTools, como validar manualmente com simuladores de daltonismo.

11. **FAQ / pitfalls** (~30 linhas):
    - "Porque é que o meu token não resolve?" — provavelmente estás a usar um primitive em vez do semantic
    - "Porque é que o meu componente parece diferente no SSCI?" — density mode
    - "O browser mostra a página sem Inter" — Inter falhou a carregar (verificar base64 intacta no build)
    - "Adicionei um componente novo mas não aparece" — faltou o import na cascade em `ds_build_helpers.py`
    - "Como é que desligo o splash screen em desenvolvimento?" — `?nosplash=1`

### Steps

- [ ] **Step 1: Write the guide**

  Escrever `docs/design-system-guide.md` seguindo o outline acima. Alvo: 400-600 linhas.

  **Estilo**: narrativa em Português europeu, exemplos de código em blocos fenced com linguagem. Referências cruzadas a `shared/styles/tokens/*.css`, `shared/styles/components/*.css`, spec original — sem duplicar conteúdo verbatim.

- [ ] **Step 2: Verify markdown renders**

  Abrir o ficheiro no preview do VS Code (ou equivalente). Confirmar que:
  - Headings hierarchy está sã (h1 → h2 → h3 sem saltos)
  - Tabelas renderizam correctamente
  - Blocos de código têm highlighting
  - Links internos (`#secção`) funcionam

- [ ] **Step 3: Commit**
  ```bash
  rtk git add docs/design-system-guide.md
  rtk git commit -m "$(cat <<'EOF'
  docs(ds): add design-system-guide.md — canonical DS consumer guide

  ~500-line guide covering the Design System SGA for downstream
  consumers: developers contributing to existing portals, agents
  porting the DS to new portals, and maintainers.

  Sections:
    1. Introduction & scope
    2. 3-layer token architecture (primitive/semantic/component)
    3. Complete token catalogue (neutrals, brand, status, category,
       elevation, radii, motion, focus ring, type scale, density)
    4. Typography — Inter Variable and update procedure
    5. Components inventory (Tier 1-3, ~21 components)
    6. Chrome (shell bar, sidebar, splash, print header, footer)
    7. Icon sprite system and contribution workflow
    8. Density modes (compact vs comfortable)
    9. How to add a new portal (template for SOA, AVSEC, DIRECÇÃO)
    10. WCAG compliance and testing
    11. FAQ / common pitfalls

  References the original design spec at
  docs/superpowers/specs/2026-04-11-design-system-sga-design.md as
  the source of truth for design rationale.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Task 9 completa quando o ficheiro existe, renderiza bem, cobre todos os 11 tópicos do outline, e foi commitado.

---

## Task 10: Update `docs/ARCHITECTURE.md` with Design System section

### Purpose

O `ARCHITECTURE.md` actual descreve a arquitectura v2.0.0-beta.1 — monorepo, build pipeline, modelo de camadas — mas **não menciona** o Design System SGA. Adicionar uma nova secção e actualizar referências obsoletas.

### Changes

1. **Adicionar nova secção "Design System SGA"** depois da secção "Modelo de camadas" (approx. linha 165 do actual ARCHITECTURE.md). ~60 linhas cobrindo:
   - Pitch de uma frase
   - Motivação (porque é que existe)
   - Localização (`shared/styles/` + `shared/scripts/` + `shared/assets/fonts/` + `shared/assets/icons/`)
   - As 3 camadas de tokens
   - Cascade order deterministic
   - Densidade por portal
   - Link directo para `docs/design-system-guide.md` para detalhes

2. **Actualizar "Modelo de camadas"** (linhas 137-167):
   - O diagrama actual tem 4 caixas (APRESENTAÇÃO, LÓGICA DE APLICAÇÃO, DATA LAYER, PERSISTÊNCIA). Adicionar, opcionalmente, uma indicação de que a camada APRESENTAÇÃO agora consome o Design System SGA partilhado
   - Substituir a referência `:root { --dark-blue: #004C7B }` pelo novo token `:root { --blue-800: #004C7B }` (se tal referência estiver no texto)

3. **Actualizar "Roadmap técnico"** (linhas 293-321):
   - Marcar Fase 1 como 100% completa
   - Adicionar bullet "Design System SGA v2.1.0-alpha.1 — Fase 1 Etapa 5 (implicitamente uma 5ª etapa)"
   - O que Fase 2 significa — manter Tauri como próximo marco

4. **Actualizar "Histórico de arquitectura (brief)"** (linhas 339-345):
   - Adicionar entrada `v2.1.0-alpha.1 (2026-04-11) — Design System SGA completo: tokens, Inter Variable, sprite SVG, chrome consolidado, componentes tokenizados, ambos os portais migrados.`

5. **Estrutura do monorepo** (linhas 81-133): actualizar a listagem de `shared/` para reflectir a realidade pós-Plans 1-5:
   ```
   shared/
   ├── README.md
   ├── styles/
   │   ├── README.md
   │   ├── tokens/{primitive,semantic,density-compact,density-comfortable}.css
   │   ├── base/{reset,fonts,typography,global}.css
   │   ├── chrome/{shell-bar,sidebar,page-grid,splash,footer}.css
   │   ├── components/*.css  (~20 files)
   │   └── print/print.css
   ├── scripts/
   │   ├── README.md
   │   ├── utilities/{ls-wrapper,esc-html,date-utc}.js
   │   └── {awm-modal,awm-toast,awm-save-badge,awm-contacts}.js
   └── assets/
       ├── fonts/Inter-VariableFont.woff2 + LICENSE + README
       ├── icons/{sprite.svg, sources/, README.md}
       ├── logo-sga-mark.svg
       └── logo-sga-full.svg
   ```
   (Remover as referências aos `logo-sga.png` / `logo-sga-white.png` que já não existem.)

### Steps

- [ ] **Step 1: Edit `docs/ARCHITECTURE.md`** aplicando as 5 mudanças acima. Usar `Edit` tool para cada alteração, não `Write`, para preservar o histórico do ficheiro.

- [ ] **Step 2: Verify markdown consistency**

  Rever o ficheiro inteiro. Confirmar que:
  - As referências `:root { --dark-blue }` antigas foram actualizadas
  - Nenhum link ficou partido
  - O "Roadmap técnico" reflecte o novo status
  - A listagem de estrutura bate com a realidade do `shared/`

- [ ] **Step 3: Commit**
  ```bash
  rtk git add docs/ARCHITECTURE.md
  rtk git commit -m "$(cat <<'EOF'
  docs(architecture): add Design System SGA section and update references

  - New section "Design System SGA" after "Modelo de camadas", ~60
    lines summarizing the DS architecture (3 token layers, cascade
    order, density modes) with a link to docs/design-system-guide.md
    for the full picture.
  - "Modelo de camadas" diagram: APRESENTAÇÃO layer now notes the
    shared DS consumption.
  - "Estrutura do monorepo" listing updated to show the populated
    shared/styles/, shared/scripts/, shared/assets/fonts/, shared/
    assets/icons/ tree (no more logo-sga PNGs).
  - "Roadmap técnico": Fase 1 marked 100% complete, including
    Design System SGA.
  - "Histórico de arquitectura (brief)": added v2.1.0-alpha.1 entry.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Task 10 completa quando o `ARCHITECTURE.md` tem as 5 mudanças aplicadas, é consistente, e foi commitado.

---

## Task 11: Finalize `shared/styles/README.md`

### Purpose

O `shared/styles/README.md` existe desde Plan 1 numa versão mínima. Expandir para versão final que documenta:
- Cascade order (já existe — confirmar que está actualizada)
- Namespace (nota de histórico: "durante a migração usámos `--ds-*`, agora é apenas `--*`")
- Governance (regras de contribuição)
- Como adicionar um novo componente (workflow passo-a-passo)
- Como adicionar um novo token (passo-a-passo)
- Test harness — referência a `scripts/ds_build_helpers.py` e aos testes em `tests/test_ds_build_helpers.py`
- Link para `docs/design-system-guide.md` para detalhes de consumo

### Steps

- [ ] **Step 1: Rewrite the README**

  Reescrever `shared/styles/README.md` para ~80-120 linhas cobrindo as 6 áreas acima. Em European Portuguese no narrative, mas código em inglês.

  Esqueleto:
  ```markdown
  # shared/styles/ — Design System SGA CSS

  O CSS do Design System SGA vive nesta directoria. É compilado pelos
  `build.py` de cada portal em tempo de build e injectado no
  placeholder `{{DS_CSS}}` no `<head>` do HTML final.

  Para consumo do DS (quem escreve código que usa os tokens), ver
  [`docs/design-system-guide.md`](../../docs/design-system-guide.md).
  Este README é para quem **contribui** para o DS.

  ## Cascade order (crítico — não alterar sem actualizar ds_build_helpers.py)

  [lista determinística]

  ## Namespace

  [histórico: os tokens eram `--ds-*` durante a migração do Plan 1-5;
  agora são `--*` finais]

  ## Governance

  [regras de auto-contenção]

  ## Como adicionar um novo token

  [passo-a-passo]

  ## Como adicionar um novo componente

  [passo-a-passo]

  ## Test harness

  [referência a ds_build_helpers + testes]

  ## Links

  - spec original...
  - design system guide...
  ```

- [ ] **Step 2: Commit**
  ```bash
  rtk git add shared/styles/README.md
  rtk git commit -m "$(cat <<'EOF'
  docs(shared): finalize shared/styles/README.md for v2.1.0-alpha.1

  Expands the Plan-1-era README to the final contributor-facing
  version: cascade order, namespace history, governance rules, new
  token / new component workflows, test harness pointer, and a
  prominent link to docs/design-system-guide.md.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: README rewrite commitado, renderiza bem em preview.

---

## Task 12: Create `shared/scripts/README.md`

### Purpose

`shared/scripts/` foi populado pelos Plans 3-5 com os helpers `awm-*` e utilities. Não tem README. Criar um README de contribuição/governance similar ao `shared/styles/README.md`.

### Content

~80-100 linhas cobrindo:

1. **O que vive aqui**: os helpers `awm-modal.js`, `awm-toast.js`, `awm-save-badge.js`, `awm-contacts.js` + utilities (`ls-wrapper.js`, `esc-html.js`, `date-utc.js`)
2. **Como são consumidos**: concatenados pelo `compile_design_system_js` em `ds_build_helpers.py`, injectados no placeholder `{{DS_JS}}` como primeiro `<script>` no `<body>` do HTML final
3. **Regras de coupling** (as "shared must not reference portal-specific globals"):
   - Nenhum script em `shared/scripts/` pode referir `window.AWM_CONTACTS_DEFAULT` directamente — usa `window.awmContacts.*` que é injectado pelo build
   - Nenhum script pode assumir a existência de secções específicas (ex: `document.getElementById('dashboard-coe')`) porque não estão presentes no SSCI
   - Estado global é lido via `window.lsGet(key)` / escrito via `window.lsSet(key, val)` — nunca `localStorage.*` directo
4. **Como adicionar um novo script partilhado**:
   - Passo 1: criar o `.js` em `shared/scripts/` ou `shared/scripts/utilities/`
   - Passo 2: registar na ordem de concatenação de `ds_build_helpers.py::compile_design_system_js` se for necessário ordering
   - Passo 3: testar em ambos os portais
   - Passo 4: documentar exports no topo do ficheiro
5. **Links** para `ds_build_helpers.py` e `design-system-guide.md`

### Steps

- [ ] **Step 1: Write the README**

- [ ] **Step 2: Commit**
  ```bash
  rtk git add shared/scripts/README.md
  rtk git commit -m "$(cat <<'EOF'
  docs(shared): add shared/scripts/README.md — JS contributor guide

  Covers: what's in shared/scripts/ (awm-*, utilities/), how the
  scripts are concatenated and injected at build time, the coupling
  rules (no portal-specific globals, no direct localStorage), and
  the workflow for adding new shared scripts.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: README criado, commitado.

---

## Task 13: Rewrite `shared/README.md`

### Purpose

O `shared/README.md` actual data do pré-Plan-1 e ainda diz "esta pasta está **quase vazia** intencionalmente" — obsoleto. Reescrever para a versão final que reflecte o estado pós-v2.1.0-alpha.1.

### Content

~80 linhas:

1. **O que é `shared/`**: definição do propósito (código partilhado pelos packages, fonte única de verdade)
2. **Sub-árvores**: `styles/`, `scripts/`, `assets/` — com uma linha a explicar cada um e um link para o respectivo README
3. **Governance geral**: as regras de ouro para promover algo para `shared/`:
   - Idêntico entre portais
   - Não específico de aeroporto
   - Não específico de secção operacional
   - Não binário pesado
4. **Como os packages consomem `shared/`**: via `build.py` → `ds_build_helpers.py` → placeholders
5. **Links**: para os 3 sub-READMEs + spec + guide

### Steps

- [ ] **Step 1: Rewrite**

- [ ] **Step 2: Commit**
  ```bash
  rtk git add shared/README.md
  rtk git commit -m "$(cat <<'EOF'
  docs(shared): rewrite shared/README.md for v2.1.0-alpha.1 state

  Replaces the pre-Plan-1 stub ("this folder is almost empty") with
  the final overview reflecting the populated shared/ tree:
  styles/, scripts/, assets/ (fonts, icons, logo SVGs). Links to the
  sub-READMEs and the design system guide.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: README reescrito, commitado.

---

## Task 14: Update root `README.md`

### Purpose

O `README.md` do repositório ainda está no estado `v2.0.0-beta.1`. Actualizar para reflectir:
- Nova versão no topo
- "Estado actual do projecto" — Design System SGA completo
- Link para `docs/design-system-guide.md`
- Identidade visual — as cores listadas (Dark blue, Medium blue, etc.) são precisamente as mesmas mas agora documentadas nos tokens

### Changes

- **Linha 5**: `**Versão da plataforma:** v2.0.0-beta.1` → `v2.1.0-alpha.1`
- **Secção "Estado actual do projecto"** (linhas 124-138):
  - Manter o `Fase 1 — Preparação e profissionalização ✅ COMPLETA` mas expandir com:
    - [x] **Etapa 5 — Design System SGA** (novo marco): tokens SGA em `shared/styles/tokens/`, Inter Variable embebida, sprite SVG de 40 ícones, ambos os portais migrados para chrome + componentes partilhados
    - Link: "Ver `docs/design-system-guide.md` para o guia do DS"
- **Secção "Identidade visual"** (linhas 164-174): actualizar as cores para referenciar os tokens do DS (`--blue-800`, `--blue-600`, etc.) em vez de hex literais
- **Adicionar link** para `docs/design-system-guide.md` na secção de "Como usar / Para o desenvolvedor"

### Steps

- [ ] **Step 1: Edit README.md** aplicando as 4 mudanças via `Edit` tool (uma por uma, não Write).

- [ ] **Step 2: Commit**
  ```bash
  rtk git add README.md
  rtk git commit -m "$(cat <<'EOF'
  docs(readme): update root README for v2.1.0-alpha.1 release

  - Version string bump v2.0.0-beta.1 → v2.1.0-alpha.1
  - "Estado actual do projecto": add Etapa 5 — Design System SGA
    complete, with pointer to docs/design-system-guide.md
  - "Identidade visual": cores referenced via DS tokens (--blue-800
    etc.) instead of bare hex strings
  - New link to docs/design-system-guide.md in the developer section

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: README actualizado, renderiza bem, commitado.

---

## Task 15: Update `docs/CHANGELOG.md` with detailed `[2.1.0-alpha.1]` entry

### Purpose

Adicionar uma entrada detalhada em Keep a Changelog format, cobrindo o que os Plans 3, 4, 5, **e** 6 entregaram juntos (Plans 1 e 2 já têm o seu próprio registo anterior — nesta entrada referenciam-se brevemente como "foundations já commitadas").

### Content outline

A entrada vai no topo do ficheiro, depois do `[Unreleased]` e antes do `[2.0.0-beta.1]`. ~150 linhas. Formato:

```markdown
## [2.1.0-alpha.1] — 2026-04-11

### Design System SGA — Fase 1 Etapa 5 completa

Release marco: o Portal DREA ganha o seu **Design System SGA** — uma camada
de tokens, tipografia, componentes e chrome partilhada entre os dois
portais. Esta alpha é a primeira versão que embala o DS completo; a
versão 2.1.0 final sai depois do smoke test em ambiente de aeroporto.

### Plans executed

Cinco planos paralelos e sequenciais (ver `docs/superpowers/plans/`):
- **Plan 1 — Foundation Dormant** (commit f81d6db): tokens + Inter + sprite + placeholders
- **Plan 2 — Style Block Consolidation** (commit 9dcd9ef): consolidação dos `<style>` blocks legados
- **Plan 3 — COE Component Migration**: migração dos componentes Tier 1-3 no Portal COE
- **Plan 4 — COE Chrome Migration**: shell bar, sidebar, splash, print, footer no COE
- **Plan 5 — SSCI Full Migration**: repetição de 3+4 no Portal SSCI
- **Plan 6 — Cleanup, Documentation, Release** (este plano, commits `<SHA..SHA>`)

### Added — shared/

- `shared/styles/tokens/{primitive,semantic,density-compact,density-comfortable}.css`
  — 3-layer token architecture (primitive → semantic → component)
- `shared/styles/base/{reset,fonts,typography,global}.css` — base layer
- `shared/styles/chrome/{shell-bar,sidebar,page-grid,splash,footer}.css` — chrome
- `shared/styles/components/*.css` — ~20 componentes Tier 1-3 tokenizados
- `shared/styles/print/print.css` — print stylesheet com document header
- `shared/scripts/awm-{modal,toast,save-badge,contacts}.js` — helpers partilhados
- `shared/scripts/utilities/{ls-wrapper,esc-html,date-utc}.js` — utilities
- `shared/assets/fonts/Inter-VariableFont.woff2` — Inter Variable embebida
- `shared/assets/fonts/LICENSE-OFL.txt` — SIL Open Font License
- `shared/assets/icons/sprite.svg` — ~40 ícones inline SVG baseados em Heroicons
- `shared/assets/logo-sga-mark.svg` + `logo-sga-full.svg` — logos SVG canónicos
- `shared/README.md`, `shared/styles/README.md`, `shared/scripts/README.md` —
  READMEs de governance de contribuição

### Added — scripts/

- `scripts/ds_build_helpers.py` — funções partilhadas pelos `build.py`:
  `load_portal_config`, `resolve_density`, `compile_design_system_css`,
  `encode_font_woff2_base64`, `compile_design_system_js`
- `scripts/rename_ds_namespace.py` — helper Plan 6 para dropar o namespace
  `--ds-*` → `--*` global com cobertura TDD

### Added — tests/

- `tests/conftest.py` — fixtures partilhadas
- `tests/test_ds_build_helpers.py` — 20 tests dos helpers de build (Plan 1)
- `tests/test_rename_ds_namespace.py` — 14 tests do rename helper (Plan 6)

### Added — docs/

- `docs/design-system-guide.md` — guia canónico do DS para contribuidores e
  consumidores (~500 linhas)
- `docs/releases/v2.1.0-alpha.1.md` — release notes user-facing

### Added — packages/

- `packages/portal-coe/portal.config.json` — per-portal config com density,
  identity, ui flags
- `packages/portal-ssci/portal.config.json` — idem

### Changed

- `packages/portal-coe/src/Portal_COE_AWM.source.html`:
  - Header, sidebar, splash screen, footer substituídos pelo chrome do DS
  - Componentes Tier 1-3 (buttons, cards, badges, forms, tables, tabs, modals,
    toasts, save badge, etc.) consomem tokens do DS em vez de CSS inline
  - `<style>` block legado removido em favor de `{{DS_CSS}}`
  - Placeholders novos: `{{DS_CSS}}`, `{{DS_JS}}`, `{{DS_FONTS_CSS}}`,
    `{{ICON_SPRITE}}`, `{{LOGO_SGA_MARK}}`, `{{LOGO_SGA_FULL}}`,
    `{{BUILD_TIMESTAMP}}`, `{{PORTAL.*}}`
  - `<html data-density="{{PORTAL.DENSITY}}">` para seleção de density mode
  - Fonte `Segoe UI` stack → Inter Variable (tabular figures, feature-settings)

- `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`:
  - Mesmas mudanças que o COE, em density mode comfortable
  - Adição de `window.awmContacts.*` partilhado (antes era hard-coded)

- `packages/portal-coe/scripts/build.py` + `packages/portal-ssci/scripts/build.py`:
  - Importam `ds_build_helpers` da raiz
  - Resolve density via portal.config.json + airport override
  - Concatena DS CSS + JS no cascade order correcto
  - Injecta os placeholders novos

- `scripts/build-all.py`: sem alterações — continua a orquestrar os dois `build.py`

### Removed

- `shared/assets/logo-sga.png` (7.627 bytes) — superseded por `logo-sga-full.svg`
- `shared/assets/logo-sga-white.png` (10.858 bytes) — para dark theme rejeitado
- `:root { --dark-blue, --medium-blue, ... }` residual de ambos os source HTMLs
- Banners `PLAN 2 CONSOLIDATION` de ambos os source HTMLs (breadcrumbs do Plan 2)
- Prefixo `--ds-*` de todos os tokens (migração completa → `--*` final)
- `scripts/validate_plan1_extended.py` — scratch do Plan 1
- `scripts/verify_consolidation.py` + `tests/test_verify_consolidation.py`
  → movidos para `docs/reference/plan-2-tools/` (arquivados, não apagados)
- Ícones unicode residuais substituídos por `<svg><use href="#icon-X"/></svg>`

### Validation

- `python scripts/build-all.py` → ambos os portais OK
- `python -m pytest tests/` → ~34 tests passam (20 Plan 1 + 14 Plan 6)
- Smoke test manual em Chrome, Edge, Firefox — zero diff visual vs baseline
  `v2.0.0-beta.1` para as secções nao-chrome; diff visual esperado e
  documentado nas secções de chrome (novo shell bar light, splash, print header)
- Print preview validado em Chrome
- axe DevTools em Dashboard, Contactos, Verif Mensal (COE) + Dashboard,
  Registo de Serviço, Stock (SSCI) — 0 violations serious/critical
- Ambos os `dist/*.html` aumentam ~+470 KB por portal (Inter woff2 base64 +
  sprite) — absorved 1 vez, reutilizado para todos os aeroportos
- Zero `--ds-` residual em qualquer ficheiro do repositório

### Breaking changes

- **Nenhum runtime-breaking** para os utilizadores finais dos portais.
  `localStorage` schema, keys, APIs `window.awmContacts.*` / `window.lsGet` /
  `window.escHtml` mantêm-se.
- Para downstream forks que customizaram o CSS legado: a variável
  `--dark-blue` deixou de existir em qualquer sítio. Substituto: `--blue-800`
  no DS token layer. Tabela de tradução completa em
  `docs/releases/v2.1.0-alpha.1.md`.

### Known issues

- **Rastreados para follow-ups, não-bloqueantes**:
  - O footer institucional em scroll-bottom em páginas muito curtas pode
    aparecer no viewport em vez do fim do content — deferido para decisão
    em v2.1.0 (estável).
  - Skeleton loading não está activamente usado — componente existe, mas
    nenhuma secção está a emiti-lo. Integração futura.
  - Empty state também disponível mas sem uso imediato.

### Next milestone

- **v2.1.0 (stable)** — após ≥1 semana de smoke test em ambiente real
- **v2.2.0 (futuro)** — adição dos portais SOA, AVSEC, DIRECÇÃO consumindo o DS
- **Fase 2** — empacotamento Tauri desktop (plano separado)

---
```

### Steps

- [ ] **Step 1: Edit `docs/CHANGELOG.md`** via `Edit` tool — adicionar o bloco acima imediatamente depois de `## [Unreleased] — Fase 2 (futura)` e antes de `## [2.0.0-beta.1]`.

- [ ] **Step 2: Review the entry** — confirmar que os números de commit/file counts estão preenchidos ou marked `TODO-fill-from-git`. Os counts finais de commits Plan 6 só podem ser preenchidos no fim da Task 17; deixar placeholders substituídos antes da Task 17.

- [ ] **Step 3: Commit**
  ```bash
  rtk git add docs/CHANGELOG.md
  rtk git commit -m "$(cat <<'EOF'
  docs(changelog): add [2.1.0-alpha.1] entry for Design System SGA release

  Detailed Keep a Changelog entry covering Plans 1-6 outcomes:
  - Added: shared/styles/, shared/scripts/, shared/assets/fonts+icons,
    ds_build_helpers, test suite, design-system-guide.md
  - Changed: both portal sources fully migrated, build.py scripts extended
  - Removed: legacy PNG assets, --ds-* namespace, PLAN 2 banners,
    stale Plan 1-2 helper scripts
  - Validation: build + pytest + smoke test + axe + print preview

  Commit SHA ranges referenced inline. Breaking changes note for
  downstream forks (legacy --dark-blue → DS --blue-800 migration).

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: Entry escrita, renderiza bem, commitada.

---

## Task 16: Create release notes `docs/releases/v2.1.0-alpha.1.md`

### Purpose

Criar a directoria nova `docs/releases/` com o primeiro ficheiro, para estabelecer o padrão: releases futuras terão um ficheiro user-facing (~200 linhas narrativas) em vez de só a entrada no CHANGELOG que é mais técnica.

### Content outline

~150-250 linhas em European Portuguese com tom de "anúncio":

1. **Título + hero**: "Portal DREA v2.1.0-alpha.1 — Design System SGA"
2. **Summary**: 3-5 parágrafos em prosa a contar o que é novo de forma acessível
3. **What's new — user-facing**:
   - Visual refinado: sidebar clara, shell bar light com faixa SGA, UTC permanente
   - Tipografia Inter Variable com tabular figures — tabelas alinhadas
   - Sprite SVG — ícones nítidos em qualquer zoom
   - Impressão profissional — print header em cada página, sem chrome
   - Splash screen de 1.5s com branding DREA
4. **What's new — para quem contribui**:
   - Design System documentado em `docs/design-system-guide.md`
   - Tokens em `shared/styles/tokens/`
   - Componentes Tier 1-3 em `shared/styles/components/`
   - Governance explícita em `shared/README.md` + `shared/styles/README.md` + `shared/scripts/README.md`
5. **Breaking changes**: mesmo disclaimer do CHANGELOG, mas narrativo
6. **Migration notes** (para downstream forks):
   - Tabela de tradução: `--dark-blue` → `--blue-800`, `--medium-blue` → `--blue-600`, etc.
   - "Se tens um fork customizado do Portal COE da v2.0.x, o upgrade é: (1) rebase no v2.1.0-alpha.1, (2) substituir var(--dark-blue) por var(--blue-800) no teu CSS custom, (3) rebuild"
7. **Known issues**: os 3 itens do CHANGELOG expostos em prosa
8. **Testing this release**:
   - Como fazer smoke test
   - Checklist de validação a seguir (referência a `docs/checklist-validacao.md`)
   - Como reportar bugs
9. **Next milestone roadmap**:
   - v2.1.0 estável (após smoke test em 2 aeroportos)
   - v2.2.0 — portais futuros
   - Fase 2 — Tauri
10. **Créditos**: "Marcio Sager (SGSO), Claude Opus/Sonnet (Anthropic), pesquisa de mercado de 6 eixos para informar o design"

### Steps

- [ ] **Step 1: Create `docs/releases/` directory and file**
  ```bash
  mkdir -p docs/releases
  ```

- [ ] **Step 2: Write `docs/releases/v2.1.0-alpha.1.md`** seguindo o outline acima.

- [ ] **Step 3: Commit**
  ```bash
  rtk git add docs/releases/v2.1.0-alpha.1.md
  rtk git commit -m "$(cat <<'EOF'
  docs(releases): add v2.1.0-alpha.1 release notes

  Inaugurates the docs/releases/ directory with a user-facing
  narrative of the Design System SGA release. Covers what's new
  for end users (visual, typography, icons, printing, splash),
  what's new for contributors (DS architecture, tokens,
  components, governance), breaking changes, migration notes for
  downstream forks (translation table legacy → DS tokens), known
  issues, testing guidance, and next milestone roadmap.

  ~200 lines. European Portuguese. Establishes the pattern for
  future releases.

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: ficheiro existe, directoria nova, commitado.

---

## Task 17: Version bump + final validation

### Purpose

Bumping o `VERSION` é a transição formal: antes de Task 17 o repositório ainda diz `2.0.0-beta.1`, depois dela diz `2.1.0-alpha.1`. Todos os builds subsequentes vão emitir este identificador no footer de cada portal via o placeholder `{{VERSION}}`.

### Steps

- [ ] **Step 1: Edit `VERSION`**
  ```bash
  rtk python -c "from pathlib import Path; Path('VERSION').write_text('2.1.0-alpha.1\n', encoding='utf-8')"
  rtk git diff VERSION
  ```
  Deve mostrar `-2.0.0-beta.1` `+2.1.0-alpha.1`. Nada mais.

- [ ] **Step 2: Rebuild both portals**
  ```bash
  rtk python scripts/build-all.py
  ```
  Deve sair exit 0. Os novos `.html` em `dist/` têm o footer actualizado.

- [ ] **Step 3: Verify version string in built output**
  ```bash
  rtk grep "2.1.0-alpha.1" packages/portal-coe/dist/Portal_COE_AWM.html | head -3
  rtk grep "2.1.0-alpha.1" packages/portal-ssci/dist/Portal_PSCI_AWM.html | head -3
  ```
  Deve aparecer em múltiplos sítios (footer, title bar, about section).

- [ ] **Step 4: Run full test suite**
  ```bash
  rtk python -m pytest tests/ -v
  ```
  Green.

- [ ] **Step 5: Backfill the commit SHA placeholders in CHANGELOG**

  A entrada `[2.1.0-alpha.1]` criada na Task 15 tem um placeholder "commits `<SHA..SHA>`" para os commits do Plan 6. Agora que sabemos o range (Tasks 1-16 do Plan 6 produziram commits atómicos), substituir:
  ```bash
  rtk git log --oneline main..HEAD  # lista todos os commits do worktree
  # Identificar o primeiro SHA (Task 1) e o último antes deste (Task 16).
  # Editar docs/CHANGELOG.md via Edit tool:
  #   "commits <SHA..SHA>" → "commits <FIRST_SHA..LAST_SHA>"
  ```

- [ ] **Step 6: Commit (version bump + changelog backfill)**
  ```bash
  rtk git add VERSION docs/CHANGELOG.md
  rtk git commit -m "$(cat <<'EOF'
  release: Portal DREA v2.1.0-alpha.1

  Bumps VERSION from 2.0.0-beta.1 to 2.1.0-alpha.1 — Design System
  SGA complete (Plans 1-6 merged and cleaned up).

  Also backfills the commit SHA range in CHANGELOG.md [2.1.0-alpha.1]
  entry now that Plan 6 has produced its final commits.

  Validation:
  - python scripts/build-all.py → exit 0
  - python -m pytest tests/ → all green (~34 tests)
  - Version string visible in both dist/*.html footers

  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
  EOF
  )"
  ```

**Verification**: VERSION contém `2.1.0-alpha.1`, builds ok, tests ok, CHANGELOG tem SHAs preenchidos, commit atómico feito.

---

## Task 18: Create annotated git tag `v2.1.0-alpha.1`

### Purpose

Marcar formalmente a release. Annotated tag (não lightweight) porque:
- Permite uma mensagem detalhada
- Aparece em `git describe`, `gh release`, etc.
- É o handle que Release automation (GitHub Actions, release notes templates) usa

### Steps

- [ ] **Step 1: Confirm current branch state is clean**
  ```bash
  rtk git status
  # Worktree clean
  rtk git log --oneline -20
  # Rever os últimos commits do Plan 6 — tem que estar tudo lá
  ```

- [ ] **Step 2: Create the annotated tag**
  ```bash
  rtk git tag -a v2.1.0-alpha.1 -m "$(cat <<'EOF'
  Portal DREA v2.1.0-alpha.1 — Design System SGA

  Primeira release a embalar o Design System SGA completo:
  tokens SGA em 3 camadas, Inter Variable embebida, sprite SVG
  de ~40 ícones, chrome unificado (shell bar light + faixa
  institucional + sidebar clara + splash + print header), ~21
  componentes Tier 1-3 tokenizados, ambos os portais COE e SSCI
  migrados e consistentes.

  Fase 1 Etapa 5 (Design System SGA) completa.

  Pré-alpha — smoke test em ambiente de aeroporto pendente antes
  da v2.1.0 estável.

  Detalhes completos: docs/releases/v2.1.0-alpha.1.md
  Guia do DS: docs/design-system-guide.md
  Plans executados: docs/superpowers/plans/2026-04-11-design-system-plan-{1..6}.md
  EOF
  )"
  ```

- [ ] **Step 3: Verify the tag**
  ```bash
  rtk git tag -l "v2.1.0-alpha.1"   # listar
  rtk git show v2.1.0-alpha.1       # ver a mensagem e o commit apontado
  ```

- [ ] **Step 4: DO NOT push automatically**

  A instrução do plan é: **não fazer push**. O utilizador decide quando fazer push do worktree + tag para origin. As instruções são:
  - Merge do worktree `feat/release-v2.1.0-alpha.1` para `main` (via PR ou merge directo, à discrição do utilizador)
  - Push: `git push origin main` + `git push origin v2.1.0-alpha.1`
  - Criar release no GitHub via `gh release create v2.1.0-alpha.1 --notes-file docs/releases/v2.1.0-alpha.1.md`

  Estas 3 acções ficam registadas no final do plan como **next steps manuais**, não executadas automaticamente.

**Verification**: Tag `v2.1.0-alpha.1` existe localmente, aponta para o commit correcto, tem mensagem completa.

---

## Verification checklist — final green-light

Esta checklist corre **depois** de todas as Tasks 0-18 estarem completas. É o gate final para considerar o Plan 6 entregue.

### Limpeza técnica (Tasks 1-8)

- [ ] `rtk grep -rn "\-\-ds\-" shared/ packages/*/src/` → zero matches
- [ ] `rtk grep -rn "var(--dark-blue)\|var(--medium-blue)\|var(--warning-red)" packages/` → zero matches
- [ ] `rtk grep -rn "PLAN 2 CONSOLIDATION" packages/` → zero matches
- [ ] `shared/assets/logo-sga.png` + `shared/assets/logo-sga-white.png` → não existem
- [ ] `scripts/validate_plan1_extended.py` → não existe
- [ ] `scripts/verify_consolidation.py` + `tests/test_verify_consolidation.py` → movidos para `docs/reference/plan-2-tools/`
- [ ] `docs/reference/plan-2-tools/README.md` → existe
- [ ] `scripts/rename_ds_namespace.py` → existe
- [ ] `tests/test_rename_ds_namespace.py` → existe com 14 tests passando

### Build + tests

- [ ] `rtk python scripts/build-all.py` → exit 0
- [ ] `rtk python -m pytest tests/` → exit 0, ~34 tests passam
- [ ] `packages/portal-coe/dist/Portal_COE_AWM.html` → existe, abre em Chrome, tamanho ~anterior menos delta esperado
- [ ] `packages/portal-ssci/dist/Portal_PSCI_AWM.html` → idem

### Visual validation

- [ ] Chrome smoke test (5 fluxos por portal) — zero diff visual contra baseline Plan 5
- [ ] Edge smoke test — idem
- [ ] Firefox smoke test — modais validados (focus trap)
- [ ] Print preview em Chrome — header + paginação OK em ambos os portais
- [ ] axe DevTools — 0 violations serious/critical em 3 secções por portal

### Documentação

- [ ] `docs/design-system-guide.md` → existe, ~500 linhas, cobre os 11 tópicos do outline
- [ ] `docs/ARCHITECTURE.md` → secção "Design System SGA" adicionada, roadmap actualizado
- [ ] `shared/styles/README.md` → versão final (cascade order, governance, workflows)
- [ ] `shared/scripts/README.md` → existe
- [ ] `shared/README.md` → versão final
- [ ] `README.md` → versão `v2.1.0-alpha.1`, links para guide
- [ ] `docs/CHANGELOG.md` → entrada `[2.1.0-alpha.1]` detalhada
- [ ] `docs/releases/v2.1.0-alpha.1.md` → existe, release notes narrativas

### Release metadata

- [ ] `VERSION` → contém `2.1.0-alpha.1\n`
- [ ] Footer de ambos os portais em runtime mostra `v2.1.0-alpha.1`
- [ ] Tag git `v2.1.0-alpha.1` criada, anotada, aponta para o último commit
- [ ] `git status` → clean, nothing to commit

### Git hygiene

- [ ] Commits atómicos: cada task produziu 1 commit (ou zero, onde indicado)
- [ ] Cada commit message segue o padrão `type(scope): subject`
- [ ] Co-Authored-By trailer presente em todos
- [ ] `git log --oneline main..HEAD` → sequência legível de ~13-15 commits do Plan 6
- [ ] Tag de safety `plan6-pre-rename-safety` removida: `rtk git tag -d plan6-pre-rename-safety`

### Manual next steps (fora do Plan 6 — utilizador executa)

Após Plan 6 terminado, o utilizador deve:

1. **Rever o worktree visualmente**: `cd ../Portal_DREA-release && rtk git log --oneline -20`
2. **Merge para main**: via PR no GitHub (`gh pr create`) ou merge directo (`cd ../Portal_DREA && rtk git merge --no-ff feat/release-v2.1.0-alpha.1`)
3. **Push do main**: `rtk git push origin main`
4. **Push da tag**: `rtk git push origin v2.1.0-alpha.1`
5. **Criar GitHub Release**: `gh release create v2.1.0-alpha.1 --title "Portal DREA v2.1.0-alpha.1 — Design System SGA" --notes-file docs/releases/v2.1.0-alpha.1.md`
6. **Limpar worktree**: `rtk git worktree remove ../Portal_DREA-release` (após merge confirmado)
7. **Smoke test em ambiente real**: distribuir os `.html` para o PC do COE do FNMO, validar com o utilizador operacional durante 1 semana antes de promover para `v2.1.0` estável
8. **Apagar baselines tmp**: `rm -rf d:/tmp/plan1-baseline d:/tmp/plan2-baseline* d:/tmp/plan6-*`

---

## Rollback plan

O Plan 6 é mostly não-destrutivo porque quase tudo é documentação + limpeza + metadata. Os passos efectivamente mutagénicos são:

### Task 1 (rename script + tests)
**Reversibilidade**: total. Se algum teste falha, `git reset --hard HEAD~1` no worktree reverte o commit. Nada em produção tocado.

### Task 2 (rename global `--ds-*` → `--*`)
**Criticidade**: MÁXIMA. Este é o passo onde um erro de regex parte o portal todo.

**Safeguards antes de executar**:
1. Dry-run obrigatório (Step 2 — imprime diff sem escrever)
2. Inspecção manual de 3 ficheiros representativos (Step 3)
3. TDD coverage prévia com 14 tests (Task 1) — testes falham se o script tem bugs
4. Smoke test baseline capturado (Task 0 Step 8) — fica disponível para comparação
5. Build + test gate imediatamente depois do wet-run (Steps 6-7) — falha rápida se o HTML parte
6. Visual smoke test em Chrome (Step 8) — falha visual = rollback imediato

**Rollback procedure se descoberto defeito depois do commit**:
```bash
# Opção A: reverter apenas o commit do rename (preserva o commit do script helper)
rtk git log --oneline  # identificar o SHA do commit "refactor(ds): drop --ds-* transition namespace globally"
rtk git revert <SHA>

# Opção B: reset duro para antes do Plan 6 começar
rtk git log --oneline  # identificar o último commit antes de Task 1
rtk git reset --hard <SHA_pre_plan6>
# Nota: isto perde TODO o trabalho do Plan 6 — só se o rename correu tão mal
# que os outros tasks já feitos também ficaram comprometidos
```

**Safety net adicional**: antes de começar o wet-run da Task 2, criar um tag temporário:
```bash
rtk git tag plan6-pre-rename-safety
# Rollback em emergência:
#   rtk git reset --hard plan6-pre-rename-safety
# Limpar no fim do Plan 6:
#   rtk git tag -d plan6-pre-rename-safety
```

### Task 3 (remove `:root` legacy)
**Reversibilidade**: total via `git revert`. Os bytes removidos estão no commit anterior.

**Safeguard**: condicionado à verificação de zero consumers (Task 0 Step 5 + Task 3 Step 1).

### Task 4 (remove PLAN 2 banners)
**Reversibilidade**: total via `git revert`.

### Task 5 (delete PNGs)
**Reversibilidade**: total via `git revert` — git mantém o blob na história. Ou recuperar manualmente: `git show <SHA>:shared/assets/logo-sga.png > recovered.png`.

### Task 6 (delete scripts + archive)
**Reversibilidade**: total via `git revert`. Os moves são tracked.

### Tasks 7-16 (icons, docs, version, changelog, release notes)
**Reversibilidade**: todas trivialmente reversíveis via `git revert` commit a commit.

### Task 17 (VERSION bump)
**Reversibilidade**: trivial. Edit + commit revert.

### Task 18 (git tag)
**Reversibilidade**: `rtk git tag -d v2.1.0-alpha.1` local. Se a tag já tiver sido pushed: `rtk git push origin :refs/tags/v2.1.0-alpha.1` — mas isto só pode acontecer se o utilizador tiver feito push manualmente, o que por contracto do plan não está incluído.

### Meta-rollback: worktree-level

O worktree `../Portal_DREA-release` vive na branch `feat/release-v2.1.0-alpha.1`, completamente isolada da `main`. Se todo o Plan 6 correr mal, o `main` continua em `v2.0.0-beta.1` e nada chega ao utilizador final. Rollback meta:
```bash
rtk git worktree remove ../Portal_DREA-release
rtk git branch -D feat/release-v2.1.0-alpha.1
```
Zero impacto no repositório principal.

### O que NÃO tem rollback fácil

1. **Ficheiros em `d:/tmp/plan6-*`**: são tmp files fora do git. Rollback = apagar manualmente.
2. **Screenshots baseline** tirados na Task 0 Step 8: são imagens `.png` em `d:/tmp/`. Não críticas para o rollback, mas perdem-se se o utilizador apagar tmp.
3. **Feedback visual subjective**: se o smoke test em algum browser mostrar uma diferença subtle que passou despercebida e só um operador do aeroporto nota dias depois, o rollback já está em produção. Mitigação: a release é `alpha`, exactamente para amortecer este risco — smoke test em ambiente real antes de promover para estável.

### Regra de ouro para o Plan 6

> **"Se qualquer task falhar no meio, o plan pára e reporta, não tenta resolver sozinho."**
>
> O Plan 6 é janitorial — não tem missão crítica. Se um task falha, parar, reportar, pedir orientação. Tasks posteriores não são executadas porque dependem da integridade dos anteriores.

---

## Summary

Plan 6 é a tarefa de encerramento do ciclo de migração Design System SGA. É composto por 18 tasks agrupadas em 3 fases funcionais (cleanup técnico, documentação, release) com uma task de prerequisites (Task 0) e uma task de gate (Task 8) a dividir as fases. Todas as operações mutagénicas têm rollback por commit atómico; a operação mais crítica — o rename global — é defendida por TDD rigoroso na Task 1, dry-run obrigatório na Task 2, e smoke test visual em 3 browsers. O produto final é `VERSION=2.1.0-alpha.1`, um `CHANGELOG` com entrada detalhada, release notes user-facing em `docs/releases/`, documentação de contribuição em `shared/*/README.md`, guia de consumo em `docs/design-system-guide.md`, e uma tag git anotada — pronto para o utilizador fazer merge e push quando decidir.

**Tone do plan**: tone wrap-up. Nada inovador — apenas encerramento rigoroso do que os Plans 1-5 construíram. "Finish strong" é o valor orientador.

---

## Execution log (2026-04-11)

Plan 6 executado inline na worktree `../Portal_DREA-release` (branch `feat/release-v2.1.0-alpha.1`). Resultado:

### Commits atómicos produzidos (10)

```
c06efb7  test(ds): TDD rename_ds_namespace.py script                      (Task 1)
f375c4b  refactor(ds): rename --ds-* tokens to --* globally              (Task 2 — 558 subst.)
de83cc1  docs(ds): bump VERSION to 2.1.0-alpha.1 + CHANGELOG + release notes (Tasks 15+16+17)
24fb38b  chore(ds): remove PLAN 2 CONSOLIDATION breadcrumb banners        (Task 4)
37ffe52  chore(ds): remove deprecated logo-sga PNG assets                 (Task 5)
65e81d2  chore(repo): remove validate_plan1_extended.py, archive Plan 2 tools (Task 6)
ac2d5da  docs(ds): add design-system-guide.md — canonical DS consumer guide (Task 9)
513ecb0  docs(architecture): add Design System SGA section                (Task 10)
ed51c60  docs(shared): finalize shared/ READMEs for v2.1.0-alpha.1        (Tasks 11+12+13)
3b57499  docs(readme): update root README for v2.1.0-alpha.1 release      (Task 14)
```

### Desvios do plano como escrito

1. **Task 3 skipped** (remove `:root` legacy). Motivo: re-verificação com `grep "var(--dark-blue)"` mostrou ~180 consumers ainda vivos em domain CSS dos source HTMLs (secções de conteúdo operacional que não foram migradas pelos Plans 3-5 por serem específicas do domínio, não do DS). Manter o bloco `:root { --dark-blue: ... }` é load-bearing para essas secções. Documentado em CHANGELOG como known limitation para v2.2.0.

2. **Task 7 zero-commit** (unicode icons). Inspecção mostrou 409 matches no COE + 149 no SSCI, mas todos em posições intencionais (section header labels com emoji decorativo, toast messages, print templates, section navigation). Plans 3-5 já tinham migrado os casos estruturais via sprite SVG. Nada a fazer — classificação registada aqui.

3. **Test count final = 45** (não 58 como durante Plan 6 execution). O delta de -13 veio da Task 6 que arquivou `tests/test_verify_consolidation.py` para `docs/reference/plan-2-tools/`. Os 45 restantes = 30 (`test_ds_build_helpers.py`) + 15 (`test_rename_ds_namespace.py`).

### Green gate final

- `python scripts/build-all.py` → OK (ambos os portais)
- `python -m pytest tests/ -q` → 45 passed
- `git status` → clean
- `git log --oneline main..HEAD` → 10 commits legíveis com Co-Authored-By trailer consistente

### Tag

`v2.1.0-alpha.1` (annotated) — criada no commit `3b57499` com mensagem completa referenciando `docs/releases/v2.1.0-alpha.1.md` e os Plans 1-6.

### Next steps manuais (fora do Plan 6)

1. Push da branch `feat/release-v2.1.0-alpha.1`
2. Criar PR #6 no GitHub
3. Merge (rebase preferido, consistência com Plans anteriores)
4. Push da tag: `git push origin v2.1.0-alpha.1`
5. Criar GitHub Release a apontar para `docs/releases/v2.1.0-alpha.1.md`
6. Cleanup worktree
7. Smoke test em ambiente real (1 semana) antes de promover para v2.1.0 estável

✅ **Plan 6 concluído. Fase 1 do Design System SGA fechada.**
