# shared/ — Código partilhado entre packages

Esta pasta contém recursos que são usados por **múltiplos packages** do monorepo Portal DREA, evitando duplicação entre `packages/portal-coe` e `packages/portal-ssci`.

## Estado actual

Esta pasta está **quase vazia** intencionalmente. Apenas os logotipos SGA foram extraídos por agora:

```
shared/
├── README.md             (este ficheiro)
├── assets/
│   ├── logo-sga.png      ← logo SGA colorido
│   └── logo-sga-white.png ← logo SGA para fundos escuros
├── styles/               (vazio — preparado para Fase 2)
└── scripts/              (vazio — preparado para Fase 2)
```

## O que vai acabar aqui

Nas etapas seguintes da Fase 1 e na Fase 2, vou mover para aqui o código que é **idêntico** entre os dois portais:

### Candidatos para `shared/scripts/`

- **`awm-modal.js`** — `confirmModal`, `alertModal`, `awmConfirm`, `awmAlert`, focus trap, aria-labelledby (PATCH v8 / v3 do COE/PSCI)
- **`awm-toast.js`** — `uxpToast`, save badge, toast queue
- **`awm-data-layer.js`** — `lsGet`, `lsSet`, `lsRemove` (PATCH v9 / v4)
- **`awm-contacts.js`** — `window.awmContacts` schema unificado (PATCH v14-v19 do COE, a ser replicado para SSCI)
- **`awm-a11y.js`** — skip link, focus heading on section change, live announcer
- **`awm-print.js`** — print CSS reset rules

### Candidatos para `shared/styles/`

- **`awm-modal.css`** — `.awm-modal-overlay`, `.awm-modal`, `.awm-modal-header`, etc.
- **`awm-toast.css`** — `.uxp-toasts`, `.uxp-toast`, `.uxp-savebadge`
- **`awm-sidebar.css`** — estilos base da sidebar (cada portal customiza)
- **`awm-print.css`** — reset geral de impressão
- **`awm-sga-brand.css`** — paleta SGA, variáveis CSS custom properties

### Candidatos para `shared/assets/`

- **Logotipos SGA** (já aqui)
- **Ícones institucionais**
- **Fontes custom** (se vierem a ser usadas)

## Como os packages consomem `shared/`

Hoje (Etapa 2 — passthrough): **ainda não consomem**. Cada package tem o seu source HTML completo e independente.

Amanhã (Etapas 3 e 4): os `build.py` de cada package serão estendidos para lerem ficheiros de `shared/` e inlineá-los no HTML final. Por exemplo:

```python
# packages/portal-coe/scripts/build.py (pseudo-código futuro)
shared_css = (REPO_ROOT / "shared" / "styles" / "awm-modal.css").read_text()
shared_js = (REPO_ROOT / "shared" / "scripts" / "awm-modal.js").read_text()

html = html.replace("{{SHARED_MODAL_CSS}}", shared_css)
html = html.replace("{{SHARED_MODAL_JS}}", shared_js)
```

Assim, **um bug corrigido em `shared/` propaga-se automaticamente aos dois portais** no próximo build. Esta é a razão principal de existir o monorepo.

## Princípio de governance

**Só vai para `shared/` o que é:**

1. **Idêntico entre os portais** (byte a byte, ou quase). Se há variantes, **não é shared** — é específico do package.
2. **Não específico de um aeroporto** (não depende de contactos, nomes, códigos OACI, etc.). Isso é `config/`.
3. **Não específico de uma secção operacional** (Contactos, Fluxogramas, Fichas, etc.). Essas coisas vivem nos packages.
4. **Não são ficheiros binários pesados** (PDFs, áudios, vídeos). Esses ficam em `config/` ou fora do repositório.

Em caso de dúvida, a regra é: **começar no package específico**, e só promover para `shared/` quando for usado por 2+ packages.
