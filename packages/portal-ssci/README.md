# Portal SSCI

> Módulo do **Portal DREA** — Serviço de Salvamento e Combate a Incêndios

**Utilizador alvo:** Chefe SSCI, Comandante de Bombeiros, Operador de turno do quartel.

---

## O que faz

- **Dashboard** com estado operacional do quartel e dos veículos VCI
- **Registo de serviço** — abertura/fecho de turnos, ocorrências, relatórios
- **Inspecção Whisky 01 e Whisky 02** (VCI — Veículos de Combate a Incêndios)
- **Inspecção de equipamento de resgate** (EPI, ferramentas, materiais)
- **Teste de comunicações** — verificação periódica de rádios, CISCO, alertas
- **Avaria de equipamento** — registo de anomalias
- **Abastecimento VCI** — controlo de combustível e consumos
- **Tempo de resposta** — registo e análise dos tempos em ocorrências reais
- **Lista de presença** do pessoal SSCI
- **Controlo de estoque** — consumíveis, EPI, extintores
- **Checklists COE e PCM** — listas de verificação operacionais

## Como buildar

```bash
# A partir da raiz do monorepo
python packages/portal-ssci/scripts/build.py

# Ou com config de outro aeroporto
python packages/portal-ssci/scripts/build.py --config config/airport-luanda.json

# Output: packages/portal-ssci/dist/Portal_PSCI_AWM.html
```

## Estrutura

```
packages/portal-ssci/
├── README.md               (este ficheiro)
├── src/
│   └── Portal_PSCI_AWM.source.html   Fonte única (futuro: partida em módulos)
├── scripts/
│   └── build.py            Build script específico do SSCI
└── dist/                   Output (gitignored)
    └── Portal_PSCI_AWM.html
```

## Histórico

Portal SSCI começou como produto autónomo paralelo ao Portal COE. Sofreu uma evolução menos intensa (5 PATCHes históricos) focada principalmente em UX, acessibilidade e a11y modal:

- **PATCH v1** — Tempo resposta / ocorrência real
- **PATCH v2** — UX / A11Y baseline
- **PATCH v3** — `escHtml` + focus trap nos modais (mirror do COE PATCH v8)
- **PATCH v4** — `lsGet`/`lsSet` + section announcer (mirror do COE PATCH v9)
- **PATCH v5** — Print safety CSS (mirror do COE PATCH v11)

## Relação com o Portal COE

Os dois portais estão **intencionalmente separados** no monorepo Portal DREA para reflectir a realidade operacional:

- O Coordenador COE usa o **Portal COE** no seu PC/tablet
- O Chefe SSCI usa o **Portal SSCI** no PC do quartel dos bombeiros
- Não há acesso cruzado entre os papéis

**Mas partilham fundações**: contactos operacionais (schema único em `config/airport-fnmo.json`), camada UX (modais, toasts, save badge), identidade visual SGA. A camada partilhada vive em [../../shared/](../../shared/).

## Nota sobre o Fix B (contactos unificados)

O **Portal COE** já tem o schema unificado de contactos implementado (PATCH v14-v19, ~26 contactos em `AWM_CONTACTS_DEFAULT`). O **Portal SSCI ainda não** — continua com os seus próprios hard-coded.

**Próxima evolução**: migrar o Portal SSCI para consumir `shared/scripts/awm-contacts.js` e a mesma fonte de config. Isto está previsto para a Fase 1 Etapa 3 ou Fase 2.
