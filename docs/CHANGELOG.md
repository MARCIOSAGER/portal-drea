# Changelog

Todas as mudanças notáveis do **Portal DREA** (plataforma com módulos Portal COE e Portal SSCI) são documentadas neste ficheiro.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Versionamento segue [SemVer](https://semver.org/lang/pt-BR/).

---

## [Unreleased] — Fase 2 (futura)

### Previsto
- Empacotamento dos portais como instaladores Windows via Tauri
- Ícones nativos + auto-update opcional
- Assinatura digital do `.exe` para evitar avisos de antivírus
- Instaladores separados: `Portal_DREA-COE_setup.exe` e `Portal_DREA-SSCI_setup.exe`

---

## [2.1.0-alpha.1] — 2026-04-11

### Design System SGA — Fundação completa entregue

Marco importante: Portal COE e Portal SSCI partilham agora uma fundação
visual unificada (Design System SGA), com chrome Shell Bar light +
4px stripe institucional, sidebar light, splash screen, sistema de
tokens em 3 camadas (primitivos → semânticos → densidade), e 13
componentes CSS partilhados. A partir desta versão, criar um novo
portal (Portal SOA, AVSEC, DIRECÇÃO) consiste em escrever apenas o
HTML de secções e consumir a fundação partilhada.

A migração foi executada em 6 plans atómicos (1-6), cada um num
PR separado e mergeado via rebase para preservar o histórico
bisectable.

### Added

**Plan 1 — Foundation Dormant**
- `shared/styles/tokens/{primitive,semantic,density-compact,density-comfortable}.css`
- `shared/styles/base/fonts.css` com Inter Variable embebido em base64
- `shared/assets/fonts/Inter-VariableFont.woff2` (SIL OFL)
- `shared/assets/icons/sprite.svg` (3 ícones seed: sga-mark, menu, close)
- `scripts/ds_build_helpers.py` com 4 helpers (load_portal_config,
  resolve_density, compile_design_system_css, encode_font_woff2_base64)
- `packages/portal-{coe,ssci}/portal.config.json` per-portal identity
  (density, tagline, UI feature flags)
- `tests/test_ds_build_helpers.py` — 20 pytest tests

**Plan 2 — Style Block Consolidation**
- `scripts/verify_consolidation.py` + 13 pytest tests
- COE: 18 → 8 style blocks (10 real CSS consolidated into block 1)
- SSCI: 8 → 5 style blocks (4 real CSS consolidated)

**Plan 3 — COE Component Migration**
- 13 component CSS files in `shared/styles/components/`:
  button, badge, form-group, card, table, tabs, dropdown, awm-modal,
  awm-toast, uxp-savebadge, skeleton, empty-state, stat-card
- `compile_design_system_css()` extended to discover `components/*.css`
- 5 new pytest tests

**Plan 4 — COE Chrome Migration**
- `shared/styles/base/{reset,typography,global}.css`
- `shared/styles/chrome/{shell-bar,sidebar,page-grid,splash,footer}.css`
- `shared/styles/print/print.css`
- `shared/assets/logo-sga-{mark,full}.svg` (stub placeholders)
- `shared/assets/icons/sprite.svg` expanded with `icon-siren`
- `shared/scripts/chrome/splash.js` + `shared/scripts/utilities/date-utc.js`
- COE HTML surgery: legacy header + sidebar + main-container replaced
  with Shell Bar + DS sidebar + page-grid + splash + footer. 14 nav-btn
  preserved, 6 critical IDs preserved.

**Plan 5 — SSCI Full Migration**
- SSCI consumes the same shared chrome + components as COE
- 17 nav-btn with 2-arg `openSection(id, event)` signature
- SSCI-specific: emergency pill omitted (config flag), psci-turno in
  operator slot, comfortable density, psci-clock legacy hidden dual
- `updateClock()` rewritten to tick 1s + write to shell bar IDs

**Plan 6 — Cleanup + Release**
- `scripts/rename_ds_namespace.py` + 15 pytest tests
- Global `--ds-*` → `--*` rename (558 replacements across 24 files)
- VERSION: 2.0.0-beta.1 → 2.1.0-alpha.1
- `docs/releases/v2.1.0-alpha.1.md` (first release notes file)

### Changed

- `scripts/ds_build_helpers.py::compile_design_system_css()` evolved
  from hardcoded file list to alphabetical directory discovery
- Both `build.py` scripts inject DS payload via new placeholder set
  (`{{DS_CSS}}`, `{{DS_INTER_WOFF2_BASE64}}`, `{{ICON_SPRITE}}`,
  `{{PORTAL.*}}`)
- COE dist: 3.8 MB → 4.47 MB (Inter Variable base64 + DS CSS propagation)
- SSCI dist: 1.5 MB → 2.09 MB (same propagation pattern)

### Removed

- Duplicated component CSS in COE block 1 (now in shared/components/)
- Duplicated component CSS in SSCI block 1 (now consumed from same shared)
- `--ds-*` namespace globally (renamed to `--*` in Plan 6)

### Validation

- `python scripts/build-all.py` → both portals OK, 19 blocks COE + 8 SSCI
- `python -m pytest tests/ -v` → **58 tests passing**
- `node --check` passes on all inline scripts
- Both dist HTMLs verified programmatically: data-density attribute
  present, all JS-load-bearing class names preserved, no unresolved
  `{{...}}` markers, body font-family still legacy Segoe UI stack
  (Inter loaded but dormant — the final typography switch is deferred
  to a future minor release)

### Known limitations

- Logo SGA is a stub SVG (triangle + text) — replace with real
  vectorised SGA lockup when available
- `date-utc.js` produced but not consumed (legacy `updateHeaderClock`
  in COE and rewritten `updateClock` in SSCI handle clocks inline)
- `ls-wrapper.js`, `esc-html.js`, `awm-modal.js`, `awm-toast.js`,
  `awm-save-badge.js` NOT extracted — SSCI still has inline
  implementations. Deferred to Fase 2+
- Legacy `:root` tokens (`--dark-blue`, `--medium-blue`, etc.) in
  SSCI block 1 retained because domain CSS (.result-toggle,
  #tr-occ-real-block, UXP layer) still references them

---

## [2.0.0-beta.1] — 2026-04-10

### Fase 1 essencialmente completa

Marco importante: o projecto passou de "HTML editado à mão" para "plataforma profissional
versionada, com build pipeline, configuração externa por aeroporto, documentação completa
e checklist de validação". A partir daqui, a Fase 1 é considerada **feature-complete** —
qualquer trabalho futuro é refinement ou Fase 2+.

### Added — Etapa 4 (branding visível + documentação)

- **Footer de versão** discreto no fim da sidebar de ambos os portais, mostrando:
  - Nome do produto (Portal COE / Portal SSCI)
  - Versão semântica (ex: `v2.0.0-beta.1`)
  - Data do build (`YYYY-MM-DD`)
  - OACI · operador (ex: `FNMO · SGA`)
  - Todos os valores resolvidos pelo build via placeholders
- **Manual do utilizador completo** em `docs/manual-utilizador.md` (~400 linhas), cobrindo:
  - Primeiros passos + configuração inicial
  - Fluxo operacional COE — Emergência Aeronáutica
  - Fluxo operacional COE — Segurança AVSEC
  - Verificação Mensal de Contactos
  - Fluxo operacional SSCI (registo de serviço, inspecções, testes, avarias, estoque)
  - Documentação técnica
  - Exports, impressão, backups
  - Atalhos de teclado
  - Troubleshooting de 5 problemas comuns
  - Glossário de 24 termos
- **Manual de instalação** em `docs/manual-instalacao.md` para o IT do aeroporto:
  - Requisitos hardware/software
  - Instalação passo-a-passo
  - Configurações do browser recomendadas
  - Política de updates e backups
  - Troubleshooting de 6 problemas de instalação
  - Estrutura interna do portal (informativo)
  - Lista de localStorage keys
- **Checklist de validação** em `docs/checklist-validacao.md` com 16 blocos de verificação:
  - Build e sintaxe
  - Abertura, login, sidebar (ambos os portais)
  - Todas as secções principais
  - Editor de contactos com casos de teste
  - Modais, save badge, toasts, impressão
  - Persistência e backup/restore
  - Diferenciação entre aeroportos
  - Secção de registo de problemas e assinaturas

### Changed

- `README.md` actualizado com novo status (Etapas 3 e 4 completas)
- `VERSION` bump: `2.0.0-alpha.2` → `2.0.0-beta.1`
- `docs/CHANGELOG.md` entrada desta versão

### Validation

- `python scripts/build-all.py` → ambos OK (18 + 7 blocks, 0 errors)
- Footers de versão aparecem correctamente no output HTML, com placeholders resolvidos
- 3 manuais escritos completamente (sem placeholders, prontos a distribuir)

---

## [2.0.0-alpha.4] — 2026-04-10

### Etapa 3.2 — Extracção de AWM_CONTACTS_DEFAULT para config

### Added

- **Campo `contacts.items`** em `config/airport-fnmo.json` com os 26 contactos operacionais do FNMO em JSON estruturado. Cada contacto tem `id`, `legacyId`, `cat`, `label`, `nome`, `funcao`, `cisco`, `cel`, `cel2`, `quente`, `email`, `tags`.
- **Placeholder `{{CONTACTS_JSON}}`** no source HTML do COE substituindo o array literal de ~7 KB que estava hard-coded.
- **Lógica especial no `build.py`** de ambos os portais para serializar `config.contacts.items` como JSON compacto (sem espaços, sem indentação) e injectar no placeholder.

### Changed

- `packages/portal-coe/src/Portal_COE_AWM.source.html` — 30 linhas de literal JS substituídas por uma única linha com placeholder (7.1 KB economizados no source)
- `_flatten_dict()` nos build scripts agora ignora chaves com prefixo `_` (metadados) e valores do tipo lista

### Impact

- Runtime do Portal COE é **idêntico** ao pré-extracção
- `window.awmContacts` continua a funcionar sem mudanças
- Editor unificado em Configurações continua a editar via overlay
- A única diferença é **onde** os defaults vivem: antes inline JS, agora injectado pelo build

### Cloning process

Adicionar um novo aeroporto agora é:
1. Copiar `config/airport-fnmo.json` → `config/airport-XXX.json`
2. Editar `airport.*` e `contacts.items` com dados do novo aeroporto
3. Correr `python scripts/build-all.py --config config/airport-XXX.json`
4. Distribuir os HTMLs em `packages/*/dist/`

**Zero edição de HTML necessária** para identidade + contactos.

---

## [2.0.0-alpha.3] — 2026-04-10

### Etapa 3.1 — Extracção de strings de identidade do aeroporto

Ambos os portais passam a referenciar o aeroporto via placeholders `{{AIRPORT.*}}` resolvidos no build a partir de `config/airport-fnmo.json`. Clonar o Portal DREA para um segundo aeroporto passa a requerer apenas copiar e editar este ficheiro de config (para os campos de identidade).

### Scope (conservador)

Apenas "strings de identidade visível" foram extraídas:
- `AIRPORT.NAME`, `NAME_SHORT`, `OACI`, `IATA`
- `AIRPORT.LOCATION`, `LOCATION_SHORT`
- `AIRPORT.OPERATOR`, `OPERATOR_SHORT`, `OPERATOR_LONG`
- `AIRPORT.COORD`, `ELEVATION_M`, `RUNWAY`, `SCI_CATEGORY`
- `VERSION` e `BUILD_DATE_SHORT`

### Not extracted (decisão documentada)

- Códigos de documentos (`PL-FNMO-PEA-001`, `FRM-FNMO-*`, `MQ-FNMO-*`, `PR-FNMO-*`, `OCC-FNMO-*`)
- localStorage keys (`coe_awm_config`, `psci_awm_config`)

### Bug fix incluído

Linha 10916 do Portal COE tinha `"Aeroporto Welwitschia Mirabilis (FNMO) — Ondjiva"`. Ondjiva é cidade na província de Cunene (norte de Angola), não Namibe. Corrigido para usar `{{AIRPORT.LOCATION_SHORT}}` que resolve para "Namibe".

### Changed

- Portal COE: 17 sites modificados (title, header, footer, PDF generators, CSV headers, DEFAULT_CFG, about)
- Portal SSCI: 7 sites modificados (title, header, suporte, about, PDF headers)

---

## [2.0.0-alpha.2] — 2026-04-10

### Reorganização para monorepo Portal DREA

Esta versão **não muda funcionalidade** dos portais — apenas reorganiza o repositório para acomodar o Portal SSCI como segundo módulo da plataforma **Portal DREA** (Direcção de Resposta a Emergências Aeroportuárias).

### Motivação

A `v2.0.0-alpha.1` criou o repositório apenas para o Portal COE, tratando o Portal PSCI como "artefacto histórico" em `docs/reference/`. Esta decisão foi identificada como incorrecta após discussão com o utilizador: o PSCI é um produto activo com utilizadores reais, e tratá-lo como histórico criaria dívida técnica grave (duplicação de código, divergência inevitável).

Decisão: reorganizar como **monorepo** com dois packages independentes mais uma camada partilhada, tudo sob a marca unificada **Portal DREA**.

### Changed

- **Repositório GitHub renomeado** de `portal-coe` para `portal-drea`
- **Pasta local renomeada** de `Portal_COE/` para `Portal_DREA/`
- **Estrutura reorganizada**:
  - `src/` → `packages/portal-coe/src/`
  - `scripts/build.py` → `packages/portal-coe/scripts/build.py`
  - `dist/` → `packages/portal-coe/dist/` (continua gitignored)
  - `src/assets/logo-sga*.png` → `shared/assets/` (promoção a código partilhado)
- **Build script do Portal COE** actualizado para reconhecer `PACKAGE_ROOT` vs `REPO_ROOT`, com helper `_rel()` para prints relativos
- **`README.md` e `docs/ARCHITECTURE.md`** reescritos para narrativa da plataforma DREA com 2+ portais

### Added

- **Package `packages/portal-ssci/`** com estrutura paralela ao COE:
  - `src/Portal_PSCI_AWM.source.html` (cópia do portal activo PSCI)
  - `scripts/build.py` (adaptado do COE para o SSCI)
  - `README.md` específico do módulo SSCI
  - `dist/` (gitignored)
- **`scripts/build-all.py`** — orquestrador que builda todos os packages em sequência com argumentos uniformes (`--config`, `--no-validate`, `--only`)
- **`shared/README.md`** — governance do que vai para a camada partilhada
- **`packages/portal-coe/README.md`** — readme específico do módulo COE
- **`packages/portal-ssci/README.md`** — readme específico do módulo SSCI

### Validação

Ambos os builds passam na nova localização:
- `python packages/portal-coe/scripts/build.py` → 18 blocks, 0 errors
- `python packages/portal-ssci/scripts/build.py` → 7 blocks, 0 errors
- `python scripts/build-all.py` → ambos OK

Os HTMLs gerados são **byte-a-byte idênticos** aos que estavam antes da reorganização — zero alteração funcional.

---

## [2.0.0-alpha.1] — 2026-04-10

### Marco inicial do repositório

Primeira versão committada ao controlo de versões git. O portal atingiu maturidade funcional suficiente para justificar separação de fonte e build, versionamento semântico, e documentação profissional.

### Added
- Estrutura de repositório profissional (src/, config/, dist/, docs/, scripts/)
- `README.md` com visão geral do projecto
- `docs/ARCHITECTURE.md` com decisões técnicas e modelo de distribuição single-tenant
- `docs/CHANGELOG.md` (este ficheiro)
- `.gitignore` configurado para proteger ficheiros binários do aeroporto e outputs de build
- Ficheiro `VERSION` na raiz com a versão semântica actual
- Cópia do portal actual em `src/Portal_COE_AWM.source.html` como ponto de partida
- Cópia de `CONTEXTO_CLAUDE_CODE.md` e artefactos históricos em `docs/reference/`

### Histórico acumulado (trabalho pré-2.0.0)

As versões seguintes listam o trabalho feito **antes** do repositório existir, reconstruído a partir do `CONTEXTO_CLAUDE_CODE.md`. Estas versões não têm tags git, são apenas registo histórico.

---

## [1.19.0] — 2026-04 (pre-git)

### Fix B completo — Editor unificado de contactos editável

- **PATCH v19** — Editor unificado passou de read-only para totalmente editável
- Tabs clássicos "Contactos Internos" e "Contactos Externos" **removidos**
- Novo campo `CURRENT_CFG.contactos` (full overlay) como fonte editável
- Tab "📇 Contactos" passa a ser default em Sistema → Configurações
- Botão "💾 Guardar Alterações" + "+ Adicionar" + "✕" por linha
- Propagação automática de edições a todas as secções consumidoras

### Changed
- `applyOverlay()` no schema v14 ganha Priority 1 para `cfg.contactos` (novo) sobre Priority 2 legacy (`contactosInternos`/`contactosExternos`)
- `cfgSaveAll` com guards para não sobrescrever com arrays vazios quando os tbody int/ext não existem

### Removed
- `cfg-tab-int` e `cfg-tab-ext` do HTML de Configurações
- Botões de tabs correspondentes

### Deprecated
- Funções `cfgRenderTable('int'|'ext')`, `cfgCollectTable('int'|'ext')`, `cfgAddRow('int'|'ext')`, `cfgDelRow('int'|'ext')` — mantidas como dead code protegido por guards

---

## [1.18.0] — 2026-04 (pre-git)

### Fix B editor unificado read-only

- **PATCH v17** — Renderizador `data-awm-contact` para fluxogramas (20 sites) e cr-chips (64 sites)
- **PATCH v18** — Tab "Contactos (Unificado)" em Configurações com filtro, pesquisa e tabela read-only

---

## [1.17.0] — 2026-04 (pre-git)

### Fix B fundação (schema + integrações principais)

- **PATCH v14** — Schema `AWM_CONTACTS_DEFAULT` com 26 contactos normalizados em 5 categorias
- **PATCH v15** — Renderização dinâmica da secção `contactos` (remove 230+ linhas hard-coded)
- **PATCH v16** — Sincronização de `VERIF_ENTIDADES` com o schema unificado
- Backup automático da config antiga em `localStorage["coe_awm_config_backup_pre_v14"]`
- API `window.awmContacts.*` exposta globalmente

---

## [1.13.0] — 2026-04 (pre-git)

### Re-foco OCORRÊNCIAS (grande mudança estrutural)

- **PATCH v13** — Grupo sidebar "SIMULACROS" renomeado para "OCORRÊNCIAS"
- Secção `guia-emg` reescrita: cartão de acção imediata + 4 fases accordion + referências rápidas
- Secção `guia-seg` reescrita: banner RESTRITO AVSEC + aviso código comunicação + 4 fases
- Secção `fichas-emg` transformada em dashboard do EFB (status + histórico + ferramentas)
- Novo vocabulário CSS `.occ-*` para componentes operacionais
- Eliminado conteúdo de simulacro (cenário EX-FNMO-PEA-001, triagem START, 12 critérios)

---

## [1.12.0] — 2026-04 (pre-git)

### Redesign visual do grupo SIMULACROS (pré-re-foco)

- **PATCH v12** — Tracks coloridos Emergência (`#c62828`) / Segurança (`#f39c12`) no grupo da sidebar
- "Guia de Utilização" removido do menu; cross-link card dentro da secção `ajuda`
- Ícones ✈ / 🛡 consistentes com o vocabulário operacional

---

## [1.11.0] — 2026-04 (pre-git)

- **PATCH v11** (COE) / **PATCH v5** (PSCI) — Print safety CSS para esconder UXP chrome em impressão

---

## [1.10.0] — 2026-04 (pre-git)

### Performance

- **PATCH v10** — PDFs base64 (`DOC_PDF_B64`, ~1.71 MB) movidos para fim do documento via atomic replace. Parser HTML renderiza dashboard antes de processar o literal, melhorando First Paint.

---

## [1.9.0] — 2026-04 (pre-git)

### Acessibilidade e persistência

- **PATCH v9** (COE) / **PATCH v4** (PSCI) — `lsGet`/`lsSet`/`lsRemove` wrapper com schema versionado v1 + quota guard + migração legacy
- Section change announcer com `aria-live="polite"` + focus no h2 da secção activa

---

## [1.8.0] — 2026-04 (pre-git)

### Acessibilidade modal + XSS guard

- **PATCH v8** (COE) / **PATCH v3** (PSCI) — `window.escHtml(s)` helper global
- Focus trap nos `.awm-modal-overlay`
- Restauração de foco ao fechar modal
- `aria-labelledby` / `aria-describedby` automáticos

---

## [1.7.0] — 2026-03 (pre-git)

### Verificação Mensal de Contactos

- **PATCH v7** — Nova secção `#verif-contactos` com tabela de 26 entidades, chips de status, persistência mensal em `localStorage`, histórico navegável, export PDF

---

## [1.6.0] — 2026-03 (pre-git)

### UX / A11Y baseline

- **PATCH v6** — Camada UXP base (save badge, toasts, skip link, shortcuts)

---

## [1.5.0] — 2026-03 (pre-git)

### Emergência aeronáutica — expansão dinâmica

- **PATCH v5** — Bloco `#emgFormBlock` (EFB) com dados operacionais TWR completos (declaração MAYDAY/PAN-PAN/Squawk, ETA, fase do voo, POB, meteo)

---

## [1.4.0] — 2026-03 (pre-git)

### Ocorrência dinâmica

- **PATCH v4** — Formulário de ocorrência com expansão dinâmica por tipo (Emergência vs Segurança)

---

## [1.2.0 – 1.3.0] — 2026-02/03 (pre-git)

### Fichas de Segurança redesign

- **PATCH v2** — Chip navigation agrupada (Líder/Coordenação/Operacionais/Externas) para fichas-seg
- **PATCH v3** — Consulta e impressão em pack (briefing)

---

## [1.0.0] — 2025 (pre-git)

### Versão original

Portal monolítico single-file criado para o FNMO. Contém:

- Dashboard, Contactos, Mapas Quadrícula, Fluxogramas
- Guias e Fichas de Emergência e Segurança
- Documentação PEA/PCA/PSA/PSCI/MOA
- Cronómetro de activação
- Configurações com tabs Internos/Externos/Operadores/Parâmetros
- Login de operador
- Sistema de modais custom (`awm-modal-*`)
