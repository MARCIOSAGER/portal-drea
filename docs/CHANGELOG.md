# Changelog

Todas as mudanças notáveis do **Portal DREA** (plataforma com módulos Portal COE e Portal SSCI) são documentadas neste ficheiro.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Versionamento segue [SemVer](https://semver.org/lang/pt-BR/).

---

## [Unreleased] — Fase 1 (em curso)

### Em desenvolvimento
- Extracção de `AWM_CONTACTS_DEFAULT` (Portal COE) para `config/airport-fnmo.json`
- Extracção paralela de contactos hard-coded do Portal SSCI
- Criação de `shared/scripts/awm-contacts.js` consumido por ambos os portais
- Extracção da camada UX partilhada para `shared/` (modal, toast, save badge)
- Footer com versão visível em runtime (ambos os portais)
- Página "Sobre" em Sistema → Sobre (ambos os portais)
- Manual de utilizador COE e SSCI
- Checklist de validação manual antes de cada release

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
