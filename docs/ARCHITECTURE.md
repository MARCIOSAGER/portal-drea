# Arquitectura — Portal DREA

> Plataforma de **Direcção de Resposta a Emergências Aeroportuárias** para aeroportos SGA
> Decisões técnicas, modelo de distribuição, e razões por trás dos trade-offs.

---

## Visão geral

**Portal DREA** é uma plataforma composta por múltiplos produtos operacionais. Cada produto serve um papel específico dentro da estrutura de resposta a emergências do aeroporto, mas todos partilham a mesma identidade visual SGA, a mesma fonte de contactos operacionais, e o mesmo conjunto de componentes UX.

### Produtos actualmente no monorepo

| Módulo | Package | Utilizador |
|---|---|---|
| Portal COE | `packages/portal-coe` | Coordenador do Centro de Operações de Emergência |
| Portal SSCI | `packages/portal-ssci` | Chefe SSCI / Bombeiros |

### Produtos potenciais futuros

- **Portal SOA** — Serviço de Operações Aeroportuárias
- **Portal AVSEC** — Security dedicado
- **Portal DIRECÇÃO** — vista executiva para Director do Aeroporto

Cada um seria um novo `packages/portal-XXX/` com o mesmo padrão.

---

## Modelo de distribuição: **Single-tenant por módulo**

O Portal DREA segue um modelo de **instalação isolada por aeroporto, por papel operacional**. Não é um SaaS multi-tenant.

### Decisões-chave

1. **Cada aeroporto tem a sua instalação** (single-tenant por aeroporto)
2. **Cada papel operacional tem o seu portal dedicado** (COE, SSCI, futuros)
3. **Os portais partilham código via monorepo** (pasta `shared/`)
4. **A configuração específica do aeroporto é externa** (`config/airport-XXXX.json`)

### Porquê single-tenant

| Razão | Detalhe |
|---|---|
| **Compliance AVSEC** | Dados AVSEC são classificados (NTA 32 ANAC). Um servidor multi-tenant que aloje dados de N aeroportos representa um risco inaceitável. Isolar por instalação respeita o princípio de "need to know". |
| **Resiliência offline** | O COE e o SSCI precisam de funcionar mesmo sem internet (incidente na rede, cabos cortados, manutenção). Single-file HTML funciona sempre. |
| **Isolamento de incidente** | Se 1 instalação falhar, afecta 1 aeroporto. Num SaaS, 1 incidente afecta todos os clientes simultaneamente. |
| **Modelo comercial** | Licença fixa + manutenção anual é mais simples contratualmente que SaaS recorrente com SLA 24/7. |
| **Upgrades não-forçados** | Cada aeroporto decide quando aplicar um update. |

### Porquê portais separados por papel

| Razão | Detalhe |
|---|---|
| **Separação de responsabilidades** | O SSCI não precisa de ver a parte de Segurança AVSEC. O Coordenador COE não precisa de ver o detalhe das inspecções aos VCI. Cada papel tem só o que lhe serve. |
| **Compliance AVSEC reforçado** | Dados de segurança só existem fisicamente no Portal COE (ou no futuro Portal AVSEC). O PC do quartel dos bombeiros não é um ponto de acesso potencial. |
| **Instalações leves** | Cada portal tem só o código que precisa. Tablet do SSCI não carrega o EFB. PC do COE não carrega checklist de VCI. |
| **Actualizações independentes** | Melhoria ao SSCI não força reinstalação do COE e vice-versa. |

### Porquê monorepo (vs 2 repositórios separados)

| Vantagem | Detalhe |
|---|---|
| **Fonte única de verdade** | `shared/awm-contacts.js` + `config/airport-fnmo.json` são lidos pelos dois portais. Editar contactos num sítio propaga aos dois. |
| **Sem divergência de código** | A camada UX (modais, toasts, a11y) vive em `shared/`. Um bug corrigido lá beneficia os dois portais simultaneamente. |
| **Versionamento coerente** | O commit X do monorepo define uma versão consistente dos dois portais. Release `v2.1` é `v2.1` para ambos. |
| **Um único sítio para documentação** | README, ARCHITECTURE, CHANGELOG centralizados. Consultor não anda a saltar entre repos. |
| **Preparado para escalar** | Adicionar um terceiro portal (SOA, AVSEC, etc.) é apenas criar um novo `packages/portal-XXX/`. |

### Como escalar mantendo single-tenant

A escalabilidade aqui significa **"instalar em 10 aeroportos sem multiplicar esforço por 10"**, não "1 servidor serve 1000 clientes". Para atingir isto:

1. **Código 100% agnóstico ao aeroporto** — nada hard-coded. Tudo específico do aeroporto vive em `config/airport-XXXX.json`.
2. **Instaladores parametrizados** — o mesmo `.exe` (por portal) funciona em qualquer aeroporto após escolher a config.
3. **Updates opt-in centralizados** — releases via GitHub Releases com notificação dentro de cada portal.
4. **Documentação self-service** — IT do aeroporto consegue instalar sem presença do consultor.
5. **Consolidação passiva** — KPIs mensais exportados para pasta SGA partilhada → Dashboard Power BI para vista agregada. Sem servidor central.

---

## Estrutura do monorepo

```
Portal_DREA/
│
├── VERSION                        Versão semântica da plataforma DREA
├── README.md                      Visão geral + instruções de uso
├── .gitignore, .gitattributes     Higiene do repositório
│
├── packages/                      Produtos independentes
│   ├── portal-coe/
│   │   ├── README.md              Readme específico do módulo COE
│   │   ├── src/
│   │   │   └── Portal_COE_AWM.source.html
│   │   ├── scripts/
│   │   │   └── build.py           Build script do COE
│   │   └── dist/                  Output (gitignored)
│   │       └── Portal_COE_AWM.html
│   │
│   └── portal-ssci/
│       ├── README.md              Readme específico do módulo SSCI
│       ├── src/
│       │   └── Portal_PSCI_AWM.source.html
│       ├── scripts/
│       │   └── build.py           Build script do SSCI
│       └── dist/                  Output (gitignored)
│           └── Portal_PSCI_AWM.html
│
├── shared/                        Código partilhado entre packages
│   ├── README.md                  Governance do que vai para shared/
│   ├── assets/
│   │   ├── logo-sga.png
│   │   └── logo-sga-white.png
│   ├── styles/                    (futuro) awm-modal.css, awm-toast.css, etc.
│   └── scripts/                   (futuro) awm-modal.js, awm-contacts.js, etc.
│
├── config/                        Configuração por aeroporto (single-tenant)
│   └── airport-fnmo.json          Config do FNMO (referência)
│
├── scripts/
│   └── build-all.py               Builda todos os packages numa só corrida
│
└── docs/
    ├── ARCHITECTURE.md            (este ficheiro)
    ├── CHANGELOG.md               Histórico de versões
    ├── manual-utilizador.md       Manual para operadores
    └── reference/                 Artefactos históricos
        ├── CONTEXTO_CLAUDE_CODE.md
        ├── AUDITORIA_PORTAL_COE.md
        ├── Portal_PSCI_AWM.html   (snapshot pré-monorepo)
        ├── Portal_Simulacros_AWM.html
        └── *.docx (fichas, guias originais)
```

---

## Modelo de camadas (aplicado a cada portal)

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
│  verificação mensal, fluxogramas, fichas)   │
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

A **camada de dados abstracta** é o que permite trocar a persistência sem reescrever a lógica. Implementada nos PATCHes v9/v4 (`lsGet`/`lsSet`) e v14 (`window.awmContacts`) do portal COE. A migração paralela no SSCI está prevista para a Fase 1 Etapa 3.

---

## Build pipeline

```
Portal_DREA/
├── VERSION ─────────────────────┐
├── config/airport-fnmo.json ────┤
├── shared/ ─────────────────────┤
│                                │
│  ┌─────────────────────────────┼─────────────────────────────┐
│  │                             │                             │
│  ▼                             ▼                             │
│ packages/portal-coe/          packages/portal-ssci/          │
│ ├── src/                       ├── src/                      │
│ └── scripts/build.py           └── scripts/build.py          │
│              │                              │                │
│              ▼                              ▼                │
│ packages/portal-coe/dist/     packages/portal-ssci/dist/    │
│ Portal_COE_AWM.html           Portal_PSCI_AWM.html          │
│                                                              │
└──────────── scripts/build-all.py (orquestra) ────────────────┘
```

### Por que Python e não Vite/webpack

- Python já é usado para scripts auxiliares (migração, auditoria)
- Zero dependências externas (`npm install` não é preciso)
- O ficheiro gerado é byte-a-byte previsível
- Se precisar de mudar para Vite um dia, a migração é trivial (já está tudo modularizado)

### O que o `build.py` de cada package faz

1. Lê `VERSION` do ficheiro raiz (versão da plataforma DREA)
2. Lê `config/airport-XXXX.json` com os dados do aeroporto
3. Lê os templates HTML / secções / CSS / JS do package
4. Lê o código partilhado de `shared/` (quando aplicável, futuro)
5. Substitui placeholders `{{AIRPORT.NAME}}`, `{{VERSION}}`, `{{BUILD_DATE}}`, etc.
6. Inlineia ficheiros binários do aeroporto (PDFs, imagens de mapas) como base64
7. Escreve `packages/portal-XXX/dist/Portal_XXX_AWM.html`
8. Valida sintaticamente com `node --check` em cada bloco de script

### O que `scripts/build-all.py` faz

Orquestra a execução sequencial dos `build.py` de todos os packages. Passa os mesmos argumentos (`--config`, `--no-validate`) a cada um. Apresenta um sumário final com status OK/FAIL por package. Falha com código != 0 se qualquer package falhar.

Uso típico:
```bash
python scripts/build-all.py                      # build completo
python scripts/build-all.py --no-validate        # mais rápido
python scripts/build-all.py --only portal-coe    # só um package
python scripts/build-all.py --config config/airport-luanda.json
```

---

## Decisões de domínio

### Fonte única de contactos (em progresso)

Todos os contactos do aeroporto devem viver num único array dentro de `config/airport-XXXX.json`. Os consumidores (secções Contactos, Fluxogramas, Cr-chips nas fichas, Verificação Mensal, EFB) lêem através de uma API única que será exposta em `shared/scripts/awm-contacts.js`.

**Estado actual**:
- **Portal COE** já tem o schema unificado implementado internamente (PATCH v14-v19). O `AWM_CONTACTS_DEFAULT` vive dentro do HTML como JavaScript.
- **Portal SSCI** ainda tem contactos hard-coded.
- **Próximo passo**: extrair `AWM_CONTACTS_DEFAULT` do COE para `config/airport-fnmo.json`, criar `shared/scripts/awm-contacts.js` que lê de lá, e fazer ambos os portais consumirem via build.

### Re-foco OCORRÊNCIAS (Portal COE)

Até à versão 1.9, o Portal COE tinha um vocabulário misto de "simulacro" e "ocorrência real". Na v2.0.0, o grupo da sidebar passou de **SIMULACROS** para **OCORRÊNCIAS**, reflectindo o foco operacional real.

Guias de simulacro antigos foram **removidos** do portal. Quem quer preparar simulacros usa os ficheiros `.docx` separados (preservados em `docs/reference/`).

---

## Dependências técnicas

### No código fonte

**Zero dependências externas** nos portais. Nem jQuery, nem frameworks, nem ícones via CDN. Tudo vanilla JS, HTML semântico, CSS moderno com flex/grid.

**Razão**: aeroporto pode ter firewall a bloquear CDNs, pode estar offline, pode ter requisitos de auditoria para saber exactamente que código corre. Zero dependências = zero surpresas.

### Nas ferramentas de build

- **Python 3.8+** — para `build.py` e `build-all.py`
- **Node.js 18+** — para validação sintáctica (`node --check`)
- **Git** — para controlo de versões
- **GitHub CLI (`gh`)** — opcional, para gestão do repositório remoto

### No browser do utilizador final

- **Chrome 90+**, **Edge 90+**, **Firefox 88+**
- **JavaScript habilitado**
- **localStorage habilitado** (~5-10 MB disponíveis)

Internet Explorer **não é suportado**.

---

## Segurança

### Dados sensíveis

- **Contactos AVSEC** (Chefe de Segurança, responsável EOD) são classificados RESTRITO AVSEC
- **Telefones diretos** de entidades externas (PNA, SPCB, INEMA, Hospital) não são públicos
- **Procedimentos PSA** contêm informação crítica

### Medidas técnicas

- **Login de operador** antes de aceder (controlo de acesso simples para registo de quem operou)
- **Export JSON** só pode ser feito pelo operador logado
- **Ficheiros PDF** embutidos como base64 não são extraíveis sem abrir o portal
- **Nenhuma chamada de rede externa** — os portais não enviam dados a lado nenhum

### Medidas organizacionais (responsabilidade do aeroporto)

- Instalar em máquinas com acesso controlado (login Windows protegido, screensaver bloqueado)
- Fazer backups regulares do JSON de configuração
- Distribuir os ficheiros HTML apenas a pessoal autorizado
- Nunca carregar os HTMLs em serviços cloud públicos

---

## Roadmap técnico

### Fase 1 — Profissionalização (em curso)

- [x] **Etapa 1**: Estrutura git, repositório GitHub, documentação inicial, logos extraídos
- [x] **Etapa 2**: Build scripts passthrough funcionais (COE + SSCI + build-all)
- [ ] **Etapa 3**: Extracção de config externa (`AWM_CONTACTS_DEFAULT` → `config/airport-fnmo.json`)
- [ ] **Etapa 4**: Branding visível em runtime (footer com versão, página Sobre), manual de utilizador, checklist de validação

### Fase 2 — Instalador desktop

- Empacotamento de cada portal com **Tauri** (Rust + webview nativo, ~15 MB por portal)
- Ícones Windows, menu iniciar, auto-update opcional
- **2 instaladores distintos**: `Portal_DREA-COE_setup.exe` e `Portal_DREA-SSCI_setup.exe`
- Cada um pode ser instalado independentemente no PC relevante

### Fase 3 — Ferramentas de suporte a múltiplos aeroportos

- Sistema de releases via GitHub Releases
- Documentação de instalação self-service para IT do aeroporto
- Templates de config para aeroportos típicos da SGA (Luanda, Lubango, Huambo, etc.)
- Ferramentas de validação de config (detectar campos em falta)
- Export automático de KPIs mensais para pasta partilhada SGA

### Fase 4 — Opcional: servidor LAN por aeroporto

Para aeroportos grandes com 10+ utilizadores COE simultâneos, instalação premium com Node.js + SQLite num PC dedicado servindo a LAN. Mesma UI.

---

## Decisões rejeitadas (e porquê)

| Decisão considerada | Porquê foi rejeitada |
|---|---|
| **SaaS multi-tenant cloud** | Compliance AVSEC, requisito offline, modelo comercial complexo |
| **Fundir COE + SSCI num único portal** | Viola separação de responsabilidades, complica compliance AVSEC |
| **2 repositórios separados (portal-coe e portal-ssci)** | Duplicação garantida, divergência inevitável, manutenção dupla |
| **Electron para desktop** | ~150 MB vs Tauri ~15 MB |
| **TypeScript** | Adiciona complexidade de build |
| **React / Vue / Svelte** | Framework = dependência + bundle overhead |
| **Build com webpack/Vite** | npm/node_modules = surpresas |
| **Base de dados local (IndexedDB)** | localStorage é mais que suficiente |
| **PWA instalável** | Complicação de service workers para pouco ganho |

---

## Histórico de arquitectura (brief)

- **v1.0 — v1.19** (2025–2026 Q1) — Portais monolíticos single-file editados directamente. Cada sessão era um "patch" numerado injectado antes de `</body>`. Portal COE e Portal PSCI evoluíram em paralelo mas independentemente.
- **v2.0.0-alpha.1** (2026-04-10) — Monorepo Portal DREA criado, packages separados, git + GitHub privado, build pipeline Python, documentação profissional.
- **v2.0** (previsto) — Fase 1 completa: config externa por aeroporto, branding visível, manuais.
- **v2.1** (futuro) — Fase 2: instaladores Tauri.
- **v3.0** (futuro) — Fase 3: ferramentas de suporte à escala.
