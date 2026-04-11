# Portal DREA

> **Direcção de Resposta a Emergências Aeroportuárias** — Plataforma operacional para aeroportos SGA

**Versão da plataforma:** `v2.1.0-alpha.1` · **Aeroporto de referência:** FNMO (Namibe) · **Operador:** SGA — Sociedade de Gestão Aeroportuária

---

## O que é o Portal DREA

**Portal DREA** é uma plataforma composta por **múltiplos produtos operacionais** destinados aos diferentes intervenientes da resposta a emergências num aeroporto. Cada produto é distribuído como um HTML standalone independente, mas todos partilham a mesma identidade visual SGA, a mesma fonte de contactos operacionais, e o mesmo conjunto de componentes UX.

### Os dois portais actualmente em produção

| Módulo | Para quem | O que faz |
|---|---|---|
| **Portal COE** | Coordenador do Centro de Operações de Emergência | Activação, coordenação, cronometragem e registo de ocorrências reais. Acesso a contactos, fluxogramas, mapas de quadrícula, documentação técnica, verificação mensal. |
| **Portal SSCI** | Chefe SSCI / Bombeiros (Serviço de Salvamento e Combate a Incêndios) | Gestão operacional do quartel SSCI: registo de serviço, inspecções aos veículos VCI, checklists COE/PCM, controlo de estoque, testes de comunicações, tempos de resposta. |

### Para quem **não** é

Portal DREA é uma ferramenta de **apoio operacional**. Não substitui sistemas certificados ICAO/ANAC. Complementa-os com registo digital, consulta rápida, e documentação auditável.

---

## Arquitectura em poucas linhas

- **Monorepo** com dois packages independentes (`portal-coe` e `portal-ssci`) + camada partilhada (`shared/`)
- **Single-tenant** — cada aeroporto tem a sua própria instalação, com os seus dados
- **Configuração externa** por aeroporto em `config/airport-XXXX.json` — o mesmo código serve qualquer aeroporto mudando apenas a config
- **Single-file HTML** por portal, gerado por um build script Python a partir dos ficheiros fonte
- **Funciona 100% offline** depois de aberto — zero dependência de servidor ou internet
- **Dados persistidos em `localStorage`** do browser (com backup exportável em JSON)

Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para detalhes técnicos, justificação das escolhas, e roadmap.

---

## Estrutura do monorepo

```
Portal_DREA/
├── packages/
│   ├── portal-coe/                     Portal do Coordenador COE
│   │   ├── src/                        Código fonte (HTML, futuros módulos)
│   │   ├── scripts/build.py            Build script do COE
│   │   └── dist/                       Output (gitignored)
│   │       └── Portal_COE_AWM.html
│   └── portal-ssci/                    Portal do Chefe SSCI
│       ├── src/                        Código fonte
│       ├── scripts/build.py            Build script do SSCI
│       └── dist/                       Output (gitignored)
│           └── Portal_PSCI_AWM.html
│
├── shared/                             Design System SGA (partilhado)
│   ├── styles/                         tokens, base, chrome, components, print
│   ├── scripts/                        chrome/splash.js, utilities/date-utc.js
│   └── assets/                         fonts/Inter, icons/sprite.svg, logo-sga-*.svg
│
├── config/                             Configuração por aeroporto
│   └── airport-fnmo.json               Config do FNMO (referência)
│
├── scripts/
│   └── build-all.py                    Builda todos os packages numa só corrida
│
├── docs/
│   ├── ARCHITECTURE.md                 Decisões técnicas e modelo de distribuição
│   ├── CHANGELOG.md                    Histórico de versões
│   ├── manual-utilizador.md            Manual para operadores
│   └── reference/                      Artefactos históricos
│
├── .gitignore
├── .gitattributes
├── VERSION                             Versão semântica da plataforma DREA
└── README.md                           (este ficheiro)
```

---

## Como usar

### Para o operador do COE ou SSCI (utilizador final)

Abrir o ficheiro HTML do portal relevante num browser moderno (Chrome, Edge, Firefox):

- **Portal COE** — `Portal_COE_AWM.html` (distribuído pelo IT do aeroporto)
- **Portal SSCI** — `Portal_PSCI_AWM.html`

Consultar [docs/manual-utilizador.md](docs/manual-utilizador.md) para o fluxo operacional completo.

### Para o desenvolvedor / consultor

Para trabalhar no Design System SGA, ver [`docs/design-system-guide.md`](docs/design-system-guide.md) (consumer guide) e os READMEs de [`shared/styles/`](shared/styles/README.md) + [`shared/scripts/`](shared/scripts/README.md) (contributor guides).

**Pré-requisitos**: Python 3.8+ e Node.js 18+ (para validação sintáctica).

```bash
# Clonar o repositório
git clone https://github.com/MARCIOSAGER/portal-drea.git
cd portal-drea

# Buildar todos os portais de uma vez
python scripts/build-all.py

# Ou buildar um portal específico
python packages/portal-coe/scripts/build.py
python packages/portal-ssci/scripts/build.py

# Ou passar config de outro aeroporto
python scripts/build-all.py --config config/airport-luanda.json

# Ou buildar apenas um package
python scripts/build-all.py --only portal-coe

# Outputs ficam em:
#   packages/portal-coe/dist/Portal_COE_AWM.html
#   packages/portal-ssci/dist/Portal_PSCI_AWM.html
```

### Para o IT do aeroporto (instalação)

Ver [docs/manual-instalacao.md](docs/manual-instalacao.md) (em preparação na Etapa 4 da Fase 1).

---

## Estado actual do projecto

**Fase 1 — Preparação e profissionalização** ✅ **COMPLETA**

- [x] Estrutura monorepo (packages/ + shared/ + config/)
- [x] Build scripts individuais funcionais para ambos os portais
- [x] Script master `build-all.py` orquestra todos os packages
- [x] Repositório git + GitHub privado
- [x] Documentação base (README, ARCHITECTURE, CHANGELOG)
- [x] **Etapa 3.1** — Extracção de strings de identidade do aeroporto
- [x] **Etapa 3.2** — Extracção de `AWM_CONTACTS_DEFAULT` para config externa
- [x] **Etapa 4** — Footer de versão, manual de utilizador, checklist de validação
- [x] **Etapa 5** — **Design System SGA** (v2.1.0-alpha.1): tokens em 3 camadas, Inter Variable embebida, sprite SVG de 40+ ícones, chrome consolidado (shell bar, sidebar, splash, footer), 13 componentes partilhados, ambos os portais migrados para light theme unificado

Ver [`docs/design-system-guide.md`](docs/design-system-guide.md) para o guia completo do Design System.

**Próxima fase**: Fase 2 — Empacotamento como instaladores Windows (Tauri).

Ver [docs/CHANGELOG.md](docs/CHANGELOG.md) para histórico completo.

### Clonar para outro aeroporto

Com a Fase 1 completa, adicionar um novo aeroporto é directo:

```bash
# 1. Copiar e editar o config
cp config/airport-fnmo.json config/airport-lad.json
# Editar airport-lad.json: airport.name, oaci, iata, location, coord, etc.
# Editar airport-lad.json: contacts.items com contactos do LAD

# 2. Buildar
python scripts/build-all.py --config config/airport-lad.json

# 3. Distribuir
# packages/portal-coe/dist/Portal_COE_AWM.html  →  PC do COE do LAD
# packages/portal-ssci/dist/Portal_PSCI_AWM.html →  PC do SSCI do LAD
```

**Zero edição de HTML necessária** para identidade + contactos.

---

## Identidade visual

Cores institucionais SGA (aplicadas a ambos os portais via Design System SGA):

| Uso | Token semantic              | Hex       |
|---|--------------------------------|-----------|
| Brand primary (shell bar stripe, badges principais) | `var(--brand-primary)` → `--blue-800` | `#004C7B` |
| Brand secondary fill (fill only, não texto) | `var(--brand-secondary-fill)` → `--blue-600` | `#0094CF` |
| Brand secondary text (AA safe) | `var(--brand-secondary-text)` → `--blue-700` | `#0073a0` |
| Brand accent | `var(--brand-accent)` → `--blue-500` | `#38C7F4` |
| Status alert (emergência aeronáutica) | `var(--status-alert-emphasis)` → `--red-700` | `#c62828` |
| Status warning (AVSEC amber) | `var(--status-warning-emphasis)` → `--amber-500` | `#f39c12` |

Para o catálogo completo (primitives, semantic, densidade compact vs comfortable), ver [`docs/design-system-guide.md`](docs/design-system-guide.md).

---

## Licença e uso

Projecto proprietário desenvolvido em consultoria para a SGA — Sociedade de Gestão Aeroportuária. Consultor: **Marcio Sager** (SGSO).

Todos os direitos reservados. Uso interno SGA apenas. Documentos AVSEC contidos nos portais estão sujeitos às restrições NTA 32 da ANAC.

---

## Suporte

Para questões técnicas, reportes de bugs ou sugestões, contactar o consultor responsável.
