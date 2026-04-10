# Changelog

Todas as mudanças notáveis do Portal COE são documentadas neste ficheiro.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Versionamento segue [SemVer](https://semver.org/lang/pt-BR/).

---

## [Unreleased] — Fase 1

### Em desenvolvimento
- Build script `scripts/build.py` (passthrough → modular)
- Configuração externa por aeroporto em `config/airport-XXXX.json`
- Extracção de `AWM_CONTACTS_DEFAULT` para ficheiro de config
- Footer com versão visível
- Página "Sobre" em Sistema → Sobre
- Manual de utilizador em `docs/manual-utilizador.md`

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
