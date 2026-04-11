# shared/ — Código partilhado entre packages

Esta pasta contém recursos que são usados por **múltiplos packages** do monorepo Portal DREA, evitando duplicação entre `packages/portal-coe`, `packages/portal-ssci` e portais futuros.

Desde v2.1.0-alpha.1, `shared/` é o coração do **Design System SGA**: tokens, componentes, chrome, tipografia, ícones, logótipos — tudo vive aqui, tudo é consumido pelo build de cada portal.

---

## Estrutura

```
shared/
├── README.md                 ← este ficheiro (overview + governance)
│
├── styles/                   Design System SGA CSS
│   ├── README.md             ← contributor guide (cascade, governance)
│   ├── tokens/               primitive.css, semantic.css, density-*.css
│   ├── base/                 reset.css, fonts.css, typography.css, global.css
│   ├── chrome/               shell-bar.css, sidebar.css, page-grid.css, splash.css, footer.css
│   ├── components/           button.css, badge.css, card.css, ... (13 ficheiros)
│   └── print/print.css       @media print + @page institucional
│
├── scripts/                  JavaScript partilhado
│   ├── README.md             ← contributor guide (coupling rules, workflow)
│   ├── chrome/splash.js      splash screen lifecycle
│   └── utilities/date-utc.js UTC clock ticker
│
└── assets/                   Binaries partilhados
    ├── fonts/                Inter-VariableFont.woff2 + LICENSE + README
    ├── icons/                sprite.svg (40+ ícones) + sources/
    ├── logo-sga-mark.svg     logo SGA para shell bar
    └── logo-sga-full.svg     logo SGA + tagline para splash
```

Para detalhes operacionais:

- **Consumir** o DS: [`docs/design-system-guide.md`](../docs/design-system-guide.md)
- **Contribuir** CSS: [`shared/styles/README.md`](styles/README.md)
- **Contribuir** JavaScript: [`shared/scripts/README.md`](scripts/README.md)

---

## Como os packages consomem `shared/`

O fluxo é:

```
packages/portal-XXX/
├── scripts/build.py  ─── usa ─── scripts/ds_build_helpers.py
└── src/Portal_XXX.source.html  (tem placeholders {{DS_CSS}}, {{DS_SPRITE}}, ...)
```

No build, `ds_build_helpers.py` é responsável por:

1. **Compilar o CSS** do DS via `compile_design_system_css(styles_root, density)` — concatena tokens → base → chrome → components → print na ordem determinística. Retorna o CSS completo como string.
2. **Compilar o JS** do DS via lógica similar (ainda em evolução na v2.1.0-alpha.1).
3. **Embebar a Inter Variable** em base64 via `encode_font_woff2_base64()`.
4. **Ler o sprite SVG** de `shared/assets/icons/sprite.svg`.
5. **Ler os logótipos** `logo-sga-mark.svg` e `logo-sga-full.svg`.

Os `build.py` de cada portal substituem os placeholders no source HTML pelo conteúdo compilado, produzindo um ficheiro `.html` final auto-contido.

**Resultado**: um bug corrigido em `shared/` propaga-se automaticamente aos dois portais no próximo build. Esta é a razão principal de existir o monorepo.

---

## Princípio de governance

**Só vai para `shared/` o que é:**

1. **Idêntico entre os portais** (byte a byte, ou quase). Se há variantes por portal, usar tokens de densidade ou config, **não** duplicar ficheiros.
2. **Não específico de um aeroporto** (não depende de contactos, nomes, códigos OACI). Isso é `packages/portal-XXX/config/airport-*.json`.
3. **Não específico de uma secção operacional** (Contactos, Fluxogramas, Fichas). Essas coisas vivem no source HTML de cada portal.
4. **Não são ficheiros binários pesados** além do estritamente necessário (Inter ~280 KB é aceitável; 10 MB de PDFs não é).

Em caso de dúvida, a regra é: **começar no package específico**, e só promover para `shared/` quando for usado por 2+ packages.

---

## Histórico

- **v2.0.0-alpha.1**: criada a directoria, apenas logotipos PNG.
- **v2.1.0-alpha.1**: Design System SGA — tokens, componentes, chrome, Inter Variable, sprite SVG, logótipos em formato SVG. Ambos os portais migrados.
- **v2.2.0** (previsto): extracção dos JS utilities (`awm-modal.js`, `awm-toast.js`, etc.) actualmente inlined nas source HTMLs.
- **v3.0.0** (previsto): Tauri desktop installers.
