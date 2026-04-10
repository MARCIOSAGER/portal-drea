# Portal COE

> Centro de Operações de Emergência — Portal operacional para aeroportos da SGA

**Versão actual:** `v2.0.0-alpha.1` · **Aeroporto de referência:** FNMO (Namibe) · **Operador:** SGA — Sociedade de Gestão Aeroportuária

---

## O que é o Portal COE

Portal HTML standalone que equipa o **Centro de Operações de Emergência** de um aeroporto com as ferramentas necessárias para:

- **Coordenar resposta a ocorrências reais** (Emergência Aeronáutica e Segurança AVSEC)
- **Registar e cronometrar** o desenrolar de cada ocorrência
- **Consultar contactos operacionais** centralizados numa fonte única
- **Seguir fluxogramas** de activação de entidades (internas e externas)
- **Gerar relatórios e exports** (PDF, CSV) para auditoria e debriefing
- **Consultar documentação técnica** (PEA, PSCI, PCA, PSA, MOA)
- **Executar verificação mensal** dos contactos conforme obrigação PEA

É uma ferramenta de **apoio operacional** ao Coordenador COE. Não substitui sistemas certificados ICAO/ANAC; complementa-os.

---

## Arquitectura em poucas linhas

- **Single-file HTML** (`Portal_COE_AWM.html`) gerado por um build script a partir de ficheiros fonte em `src/`.
- **Configuração externa por aeroporto** em `config/airport-XXXX.json` — o mesmo código serve qualquer aeroporto mudando apenas a config.
- **Funciona 100% offline** depois de aberto — zero dependência de servidor ou internet.
- **Dados persistidos em `localStorage`** do browser (com backup exportável em JSON).
- **Distribuição single-tenant**: cada aeroporto tem a sua instalação independente.

Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para detalhes técnicos completos.

---

## Estrutura do projecto

```
Portal_COE/
├── src/                       Código fonte
│   ├── sections/              HTML de cada secção do portal
│   ├── styles/                CSS por componente
│   ├── scripts/               JavaScript por módulo
│   ├── templates/             Header, footer, layout base
│   └── assets/                Logotipos, ícones
├── config/                    Configuração por aeroporto (1 ficheiro JSON por instalação)
│   └── airport-fnmo.json      Configuração de referência para o FNMO
├── dist/                      Output do build (gitignored)
│   └── Portal_COE_AWM.html    HTML final distribuível
├── docs/                      Documentação
│   ├── ARCHITECTURE.md        Decisões técnicas e diagramas
│   ├── CHANGELOG.md           Histórico de versões
│   ├── manual-utilizador.md   Manual do operador COE
│   └── reference/             Artefactos históricos e referências
├── scripts/                   Ferramentas de build
│   └── build.py               Build script: src/ + config/ → dist/
├── .gitignore
├── VERSION
└── README.md                  (este ficheiro)
```

---

## Como usar

### Para o operador do COE (utilizador final)

1. Abrir o ficheiro `Portal_COE_AWM.html` num browser moderno (Chrome, Edge, Firefox).
2. Na primeira utilização, ir a **Sistema → Configurações** e preencher os dados do aeroporto.
3. Consultar o [Manual do Utilizador](docs/manual-utilizador.md) para o fluxo operacional completo.

### Para o desenvolvedor / consultor

**Pré-requisitos**: Python 3.8+ e Node.js 18+ (para validação sintáctica).

```bash
# Clonar o repositório
git clone https://github.com/MARCIOSAGER/portal-coe.git
cd portal-coe

# Gerar o HTML final a partir dos ficheiros fonte
python scripts/build.py --config config/airport-fnmo.json

# Output fica em dist/Portal_COE_AWM.html
# Abrir no browser para testar
```

### Para o IT do aeroporto (instalação)

Ver [docs/manual-instalacao.md](docs/manual-instalacao.md) (em preparação).

---

## Estado actual do projecto

**Fase 1 — Preparação e profissionalização** (em curso)

- [x] Repositório git criado e versionado
- [x] Estrutura de pastas estabelecida
- [ ] Build script passthrough (Etapa 2)
- [ ] Configuração externa por aeroporto (Etapa 3)
- [ ] Branding, versão visível, página Sobre (Etapa 4)
- [ ] Manual de utilizador v1.0

**Próxima fase**: Fase 2 — Empacotamento como instalador Windows (Tauri).

Ver [docs/CHANGELOG.md](docs/CHANGELOG.md) para histórico completo.

---

## Identidade visual

Cores institucionais SGA:

| Uso | Cor | Hex |
|---|---|---|
| Dark blue | Header, sidebar | `#004C7B` |
| Medium blue | Botões, hover | `#0094CF` |
| Light cyan | Destaques | `#38C7F4` |
| Warning red | Alertas, emergência | `#c62828` |
| AVSEC amber | Segurança | `#f39c12` |

---

## Licença e uso

Projecto proprietário desenvolvido para a SGA — Sociedade de Gestão Aeroportuária. Consultor: **Marcio Sager** (SGSO / FNMO).

Todos os direitos reservados. Uso interno SGA apenas. Documentos AVSEC contidos no portal estão sujeitos às restrições NTA 32 da ANAC.

---

## Suporte

Para questões técnicas, reportes de bugs ou sugestões, contactar o consultor responsável.
