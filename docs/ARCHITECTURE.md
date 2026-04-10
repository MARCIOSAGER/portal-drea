# Arquitectura — Portal COE

> Decisões técnicas, modelo de distribuição, e razões por trás dos trade-offs.

---

## Modelo de distribuição: **Single-tenant**

O Portal COE segue um modelo de **uma instalação isolada por aeroporto**. Não é um SaaS multi-tenant.

### Porquê single-tenant

| Razão | Detalhe |
|---|---|
| **Compliance AVSEC** | Dados AVSEC são classificados (NTA 32 ANAC). Um servidor multi-tenant que aloje dados de N aeroportos representa um risco inaceitável. Isolar por instalação respeita "need to know". |
| **Resiliência offline** | O COE precisa de funcionar mesmo sem internet (incidente na rede, cabos cortados, manutenção). Single-file HTML funciona sempre. |
| **Isolamento de incidente** | Se 1 instalação falhar, afecta 1 aeroporto. Num SaaS, 1 incidente afecta todos os clientes simultaneamente. |
| **Modelo comercial** | Licença fixa + manutenção anual é mais simples contratualmente que SaaS recorrente com SLA 24/7. |
| **Upgrades não-forçados** | Cada aeroporto decide quando aplicar um update. Num SaaS, toda a gente é forçada à mesma versão. |

### Como escalar mantendo single-tenant

A escalabilidade aqui significa **"instalar em 10 aeroportos sem multiplicar esforço por 10"**, não "1 servidor serve 1000 clientes". Para atingir isto:

1. **Código 100% agnóstico ao aeroporto** — nada hard-coded. Tudo específico do aeroporto vive em `config/airport-XXXX.json`.
2. **Instalador parametrizado** — o mesmo `.exe` funciona em qualquer aeroporto após escolher a config.
3. **Updates opt-in centralizados** — releases via GitHub Releases com notificação dentro do portal.
4. **Documentação self-service** — IT do aeroporto consegue instalar sem presença do consultor.
5. **Consolidação passiva** — KPIs mensais exportados para pasta SGA partilhada → Dashboard Power BI para vista agregada. Sem servidor central.

---

## Modelo de camadas

```
┌─────────────────────────────────────────────┐
│  APRESENTAÇÃO                               │
│  HTML semântico + CSS SGA + JS sem deps    │
│  Funciona em Chrome, Edge, Firefox modernos │
└─────────────────────────────────────────────┘
                      ↕
┌─────────────────────────────────────────────┐
│  LÓGICA DE APLICAÇÃO                        │
│  Módulos por domínio (contactos, ocorrência,│
│  verificação mensal, fluxogramas)           │
└─────────────────────────────────────────────┘
                      ↕
┌─────────────────────────────────────────────┐
│  DATA LAYER (abstracta)                     │
│  window.awmContacts.* + window.lsGet/lsSet  │
│  Hoje: localStorage                         │
│  Futuro: LAN server / cloud (trocável)      │
└─────────────────────────────────────────────┘
                      ↕
┌─────────────────────────────────────────────┐
│  PERSISTÊNCIA                               │
│  Fase 1: localStorage (browser)             │
│  Fase 2: localStorage + backup JSON export  │
│  Fase 3: LAN SQLite (opcional por aeroporto)│
└─────────────────────────────────────────────┘
```

A **camada de dados abstracta** é o que permite trocar a persistência sem reescrever a lógica. Implementada nos PATCHes v9 (`lsGet`/`lsSet`) e v14 (`window.awmContacts`).

---

## Build pipeline

```
src/               config/                   dist/
───                ──────                    ────
templates/     ┐
sections/      │
styles/        ├──→ build.py ──────────────→ Portal_COE_AWM.html
scripts/       │         ↑
assets/        ┘         │
                         │
                    airport-XXXX.json
                    (config do aeroporto)
```

**Por que Python e não Vite/webpack**:

- Python já é usado em todas as sessões para scripts de migração
- Zero dependências externas (`npm install` não é preciso)
- O ficheiro gerado é byte-a-byte previsível
- Se precisar de mudar para Vite um dia, a migração é trivial (já está tudo modularizado)

**O que o `build.py` faz**:

1. Lê `VERSION` do ficheiro raiz
2. Lê `config/airport-XXXX.json` com os dados do aeroporto
3. Lê os templates HTML em `src/templates/`
4. Lê as secções em `src/sections/`, concatena em ordem
5. Lê o CSS em `src/styles/` e inlineia em `<style>` no `<head>`
6. Lê o JavaScript em `src/scripts/` e inlineia em `<script>` antes de `</body>`
7. Substitui placeholders `{{AIRPORT.NAME}}`, `{{VERSION}}`, `{{BUILD_DATE}}`, etc.
8. Inlineia ficheiros binários do aeroporto (PDFs, imagens de mapas) como base64
9. Escreve `dist/Portal_COE_AWM.html`
10. Valida sintaticamente com `node --check` em cada bloco de script

---

## Decisões de domínio

### Fonte única de contactos

Todos os contactos do aeroporto (internos SGA + ENNA + segurança pública + entidades externas + operadores) vivem num único array dentro de `config/airport-XXXX.json`. Os consumidores (secção Contactos, Fluxogramas, Cr-chips nas fichas, Verificação Mensal, EFB) leem através de `window.awmContacts.*` — uma API única.

Histórico: esta unificação foi feita gradualmente nos PATCHes v14 (schema), v15 (secção contactos), v16 (Verificação Mensal), v17 (fluxogramas + cr-chips), v18 (editor read-only), v19 (editor editável).

### Ocorrência activa vs histórico

O portal distingue duas coisas:

- **Ocorrência activa** — o EFB (Emergency Form Block) que está a ser preenchido em tempo real no Cronómetro. Vive em inputs DOM e é espelhado para inputs legados via `bindLegacyMirror()` para preservar exports.
- **Histórico de ocorrências** — lista de ocorrências passadas em `localStorage["coe_awm_occurrences"]`, geridas por `saveOccurrence()` / `getOccurrences()` / `loadOccurrence()`.

O dashboard em Fichas de Emergência (PATCH v13) é a ponte entre os dois: mostra um snapshot estático do EFB activo + lista histórica.

### Re-foco OCORRÊNCIAS (PATCH v13)

Até à versão 1.9 (`v1.9`), o portal tinha um vocabulário misto de "simulacro" e "ocorrência real". Na v2.0.0, o grupo da sidebar passou de **SIMULACROS** para **OCORRÊNCIAS**, reflectindo o foco operacional real. Ver `CHANGELOG.md` para detalhes.

Guias de simulacro antigos (cenário EX-FNMO-PEA-001, triagem START, 12 critérios de avaliação) foram **removidos** do portal. Quem quer preparar simulacros usa os ficheiros `.docx` separados (preservados em `docs/reference/`).

---

## Dependências técnicas

### No código fonte

**Zero dependências externas**. Nem jQuery, nem frameworks, nem ícones via CDN. Tudo vanilla JS, HTML semântico, CSS moderno com flex/grid.

**Razão**: aeroporto pode ter firewall a bloquear CDNs, pode estar offline, pode ter requisitos de auditoria para saber exactamente que código corre. Zero dependências = zero surpresas.

### Nas ferramentas de build

- **Python 3.8+** — para `build.py`
- **Node.js 18+** — para validação sintáctica (`node --check`)
- **Git** — para controlo de versões

### No browser do utilizador final

- **Chrome 90+**, **Edge 90+**, **Firefox 88+** (features modernas: `fetch`, `Promise`, `MutationObserver`, `IntersectionObserver`, `<details>/<summary>`, CSS Grid, CSS Custom Properties).
- **JavaScript habilitado** (óbvio).
- **localStorage habilitado** (~5-10 MB disponíveis).

Internet Explorer **não é suportado**. Não faz sentido gastar bytes a suportar um browser descontinuado pela Microsoft.

---

## Segurança

### Dados sensíveis

- **Contactos AVSEC** (ex: Chefe de Segurança, responsável EOD) são classificados RESTRITO AVSEC.
- **Telefones diretos** de entidades externas (PNA, SPCB, INEMA, Hospital) não são públicos.
- **Procedimentos PSA** (Plano de Segurança Aeroportuária) contêm informação crítica.

### Medidas técnicas

- **Login de operador** antes de aceder (soft login — não é autenticação criptográfica forte, é controlo de acesso simples para registo de quem operou).
- **Export JSON** só pode ser feito pelo operador logado.
- **Ficheiros PDF** (PEA, PSCI) embutidos como base64 não são extraíveis sem abrir o portal.
- **Nenhuma chamada de rede externa** — o portal não envia dados a lado nenhum.

### Medidas organizacionais (responsabilidade do aeroporto)

- Instalar em máquinas com acesso controlado (login Windows protegido, screensaver bloqueado).
- Fazer backups regulares do JSON de configuração.
- Distribuir o ficheiro HTML apenas a pessoal autorizado.
- Nunca carregar o HTML em serviços cloud públicos (Google Drive partilhado, etc.).

---

## Roadmap técnico

### Fase 1 — Profissionalização (em curso)
Estruturação git, documentação, build script, config externa. **Não muda funcionalidade**, só organiza.

### Fase 2 — Instalador desktop
Empacotamento com Tauri (Rust + webview nativo, ~15 MB). Ícone Windows, menu iniciar, auto-update opcional.

### Fase 3 — Ferramentas de suporte a múltiplos aeroportos
Sistema de releases, documentação de instalação self-service, templates de config para aeroportos típicos da SGA, ferramentas de validação de config.

### Fase 4 — Opcional: servidor LAN por aeroporto
Para aeroportos grandes (10+ utilizadores COE simultâneos), instalação premium com Node.js + SQLite num PC dedicado servindo a LAN do aeroporto. Mesma UI.

---

## Decisões rejeitadas (e porquê)

| Decisão considerada | Porquê foi rejeitada |
|---|---|
| **SaaS multi-tenant cloud** | Compliance AVSEC, requisito offline, modelo comercial complexo para 1 consultor |
| **Electron para desktop** | ~150 MB vs Tauri ~15 MB. Electron morre lentamente na indústria. |
| **TypeScript** | Adiciona complexidade de build. JS vanilla é suficiente para a dimensão do projecto. |
| **React / Vue / Svelte** | Framework = dependência + bundle overhead + curva de aprendizagem. Vanilla JS + templates string é suficiente. |
| **Build com webpack/Vite** | npm/node_modules = surpresas. Python atómico e previsível é preferível. |
| **Base de dados local (IndexedDB)** | localStorage é mais que suficiente para o volume de dados (contactos, histórico de ocorrências). IndexedDB introduziria complexidade desnecessária. |
| **PWA instalável** | Complicação de service workers para pouco ganho. Tauri dá o mesmo resultado com controlo total. |

---

## Histórico de arquitectura (brief)

- **v1.x** — HTML monolítico editado directamente. Cada sessão era um "patch" numerado (v1 a v19) injectado antes de `</body>`.
- **v2.0** (esta fase) — Separação fonte/build. Configuração externa por aeroporto. Git + GitHub + documentação.
- **v2.1** (futuro) — Instalador Tauri.
- **v3.0** (futuro) — Ferramentas de suporte à escala.
