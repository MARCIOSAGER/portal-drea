# Portal DREA

> **Direcção de Resposta a Emergências Aeroportuárias** — Plataforma operacional para aeroportos SGA

**Versão da plataforma:** `v2.0.0-alpha.1` · **Aeroporto de referência:** FNMO (Namibe) · **Operador:** SGA — Sociedade de Gestão Aeroportuária

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
├── shared/                             Código partilhado entre packages
│   ├── assets/                         Logotipos SGA, ícones institucionais
│   ├── styles/                         CSS partilhado (modal, toast, etc.)
│   └── scripts/                        JS partilhado (awmContacts, awmModal, etc.)
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

**Fase 1 — Preparação e profissionalização** (em curso)

- [x] Estrutura monorepo (packages/ + shared/ + config/)
- [x] Build scripts individuais funcionais para ambos os portais
- [x] Script master `build-all.py` orquestra todos os packages
- [x] Repositório git + GitHub privado
- [x] Documentação base (README, ARCHITECTURE, CHANGELOG)
- [x] Logotipos SGA extraídos para `shared/assets/`
- [ ] Extracção de config externa (Etapa 3)
- [ ] Branding visível em runtime, versão no footer, página Sobre (Etapa 4)
- [ ] Manual de utilizador v1.0
- [ ] Manual de instalação para IT

**Próxima fase**: Fase 2 — Empacotamento como instaladores Windows (Tauri).

Ver [docs/CHANGELOG.md](docs/CHANGELOG.md) para histórico completo.

---

## Identidade visual

Cores institucionais SGA (aplicadas a ambos os portais):

| Uso | Cor | Hex |
|---|---|---|
| Dark blue | Header, sidebar | `#004C7B` |
| Medium blue | Botões primários, hover | `#0094CF` |
| Light cyan | Destaques | `#38C7F4` |
| Warning red | Alertas, emergência aeronáutica | `#c62828` |
| AVSEC amber | Segurança, bombeiros | `#f39c12` |

---

## Licença e uso

Projecto proprietário desenvolvido em consultoria para a SGA — Sociedade de Gestão Aeroportuária. Consultor: **Marcio Sager** (SGSO).

Todos os direitos reservados. Uso interno SGA apenas. Documentos AVSEC contidos nos portais estão sujeitos às restrições NTA 32 da ANAC.

---

## Suporte

Para questões técnicas, reportes de bugs ou sugestões, contactar o consultor responsável.
