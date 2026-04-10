# Portal COE

> Módulo do **Portal DREA** — Centro de Operações de Emergência

**Utilizador alvo:** Coordenador do COE (Centro de Operações de Emergência) do aeroporto.

---

## O que faz

- **Dashboard operacional** com estado da ocorrência activa, relógio sincronizado, estado de prontidão
- **Coordenação de ocorrência** via EFB (Emergency Form Block) com dados TWR em tempo real
- **Cronómetro** com marcação cronológica de eventos durante a ocorrência
- **Consulta centralizada de contactos** — 26 entidades operacionais em 5 categorias
- **Mapas de quadrícula** (MQ-FNMO-PEA-001/002) para localização de sinistros
- **Fluxogramas de activação** — Emergência Aeronáutica e Segurança AVSEC
- **Guias de ocorrência** com fases estruturadas (notificação, activação, resposta, encerramento)
- **Fichas operacionais** para cada entidade participante
- **Verificação mensal de contactos** — rotina obrigatória PEA
- **Documentação técnica** (PEA, PSCI, PCA, PSA, MOA)
- **Exports** em PDF, CSV, JSON

## Como buildar

```bash
# A partir da raiz do monorepo
python packages/portal-coe/scripts/build.py

# Ou com config de outro aeroporto
python packages/portal-coe/scripts/build.py --config config/airport-luanda.json

# Output: packages/portal-coe/dist/Portal_COE_AWM.html
```

## Estrutura

```
packages/portal-coe/
├── README.md               (este ficheiro)
├── src/
│   └── Portal_COE_AWM.source.html   Fonte única (futuro: partida em módulos)
├── scripts/
│   └── build.py            Build script específico do COE
└── dist/                   Output (gitignored)
    └── Portal_COE_AWM.html
```

## Histórico

Este portal começou em 2025 como HTML monolítico e evoluiu através de 19 PATCHes iterativos (v1 a v19) até atingir maturidade na versão 2.0. O histórico detalhado está em [docs/CHANGELOG.md](../../docs/CHANGELOG.md) e no `docs/reference/CONTEXTO_CLAUDE_CODE.md`.

**Destaques da evolução**:

- **v1.7** — Verificação Mensal de Contactos (PATCH v7)
- **v1.13** — Re-foco OCORRÊNCIAS (vs simulacro) com cartões de acção imediata + 4 fases accordion
- **v1.14 a v1.19** — Fix B (schema unificado de contactos → editor unificado editável)
- **v2.0** — Monorepo Portal DREA, build script, documentação profissional
