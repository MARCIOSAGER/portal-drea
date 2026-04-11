# shared/styles/ — Design System SGA CSS

O CSS do Design System SGA vive nesta directoria. É compilado pelos `build.py` de cada portal em tempo de build e injectado no placeholder `{{DS_CSS}}` no `<head>` do HTML final.

Para **consumir** o DS (escrever código que usa tokens), ver [`docs/design-system-guide.md`](../../docs/design-system-guide.md). Este README é para quem **contribui** para o DS.

---

## Cascade order (crítico — não alterar sem actualizar `ds_build_helpers.py`)

O `compile_design_system_css()` em [`scripts/ds_build_helpers.py`](../../scripts/ds_build_helpers.py) concatena os ficheiros nesta ordem determinística:

1. `tokens/primitive.css` — Layer 1, valores crús. Nunca referenciados por componentes.
2. `tokens/semantic.css` — Layer 2, aliases com significado. Apenas estes são referenciados por componentes.
3. `tokens/density-compact.css` **OU** `tokens/density-comfortable.css` — só um é incluído, escolhido pelo build a partir de `portal.config.json::density`.
4. `base/*.css` — alfabética: `fonts.css`, `global.css`, `reset.css`, `typography.css`.
5. `chrome/*.css` — alfabética: `footer.css`, `page-grid.css`, `shell-bar.css`, `sidebar.css`, `splash.css`.
6. `components/*.css` — alfabética: `awm-modal.css`, `awm-toast.css`, `badge.css`, `button.css`, `card.css`, ...
7. `print/print.css` — sempre último.

Adicionar um ficheiro novo a `base/`, `chrome/`, ou `components/` é automático — o discovery é alfabético. Adicionar uma pasta nova requer actualizar `ds_build_helpers.py` e os testes.

---

## Namespace

**Histórico**: durante a migração (Plans 1-5, 2026-04-11), todos os tokens usavam o prefixo `--ds-*` para evitar colisão com variáveis legadas (`--dark-blue`, `--medium-blue`) ainda presentes nas source HTMLs. No Plan 6 o prefixo foi removido globalmente — 558 substituições em 24 ficheiros.

**Agora**: todos os tokens DS são `--foo` sem prefixo. Tokens legados como `--dark-blue` continuam a existir nas source HTMLs (não nos ficheiros partilhados) para servir domain CSS que ainda não foi totalmente migrado. Estes legados **não devem** ser adicionados a `shared/styles/` — usar apenas os novos.

---

## Governance

### Componentes são auto-contidos

Um ficheiro em `components/` **nunca** depende de outro ficheiro em `components/`. Cada componente selecciona os seus próprios tokens semantic. Exemplo errado:

```css
/* ❌ badge.css */
.badge { composes: btn from './button.css'; }
```

Exemplo certo:

```css
/* ✅ badge.css */
.badge {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-xs);
  border-radius: var(--radius-pill);
}
```

### Primitives são opacos

Componentes referenciam **apenas** tokens semantic, nunca primitives:

```css
/* ❌ errado — acopla o componente a uma cor específica */
.my-button { background: var(--blue-800); }

/* ✅ certo — desacopla via semantic */
.my-button { background: var(--brand-primary); }
```

Se o semantic apropriado não existe, adicioná-lo primeiro em `semantic.css`, **depois** usá-lo no componente.

### Sem `@import`

Ficheiros CSS nesta directoria não usam `@import`. O build concatena-os. Adicionar um `@import` quebra a previsibilidade.

### Sem preprocessadores

Sem Sass, sem PostCSS, sem nada. CSS nativo moderno com custom properties. Isto é deliberado: zero dependências, zero surpresas, zero configuração.

---

## Como adicionar um novo token

### Caso 1: novo valor primitive (ex: uma nova cor)

1. Adicionar em `tokens/primitive.css` dentro do bloco apropriado (blues, greens, grays, ...)
2. Verificar contraste vs backgrounds semelhantes com [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
3. Se tem significado semantic (ex: "é a nova cor de warning"), alias em `tokens/semantic.css`
4. Se apenas decorativo, pode ficar só em primitives
5. Correr `pytest tests/ -q` — os testes verificam a cascade order

### Caso 2: novo alias semantic (valor já existe em primitive)

1. Adicionar em `tokens/semantic.css` dentro do bloco apropriado (status, brand, elevation, ...)
2. Documentar com comentário inline se for crítico (ex: contraste rácio, "FILL ONLY")
3. Usar o novo token num componente

---

## Como adicionar um novo componente

1. Criar `components/<nome>.css`
2. Top do ficheiro: comentário `/* Component: <nome> — purpose */`
3. Selector root: classe única `.ds-<nome>` ou `.<nome>` (consistência com existentes)
4. Referenciar **apenas** tokens semantic:
   ```css
   .my-component {
     padding: var(--space-4);
     background: var(--neutral-surface);
     border: 1px solid var(--neutral-muted);
     border-radius: var(--radius-md);
     color: var(--neutral-fg);
   }
   ```
5. Estados: `:hover`, `:focus-visible`, `[aria-disabled="true"]`, etc. — usar `--focus-ring-*` tokens para focus
6. Variantes: modifiers `.ds-<nome>--primary`, `.ds-<nome>--compact`
7. Correr `python scripts/build-all.py` — o ficheiro é auto-descoberto
8. Verificar output em ambos os portais (`packages/*/dist/*.html`)
9. Se precisa de ordering específica (ex: tem de vir antes de `button.css`), **não adicionar** — auto-containment é obrigatório. Se ordering parece necessária, é sinal que o componente não está auto-contido.

---

## Test harness

Os ficheiros CSS são cobertos indirectamente pelos testes Python em [`tests/test_ds_build_helpers.py`](../../tests/test_ds_build_helpers.py):

- `test_compile_*` — verifica cascade order
- `test_density_selection` — verifica que o density correcto é incluído
- `test_encode_font_woff2_base64` — verifica a embed da Inter

Correr:
```bash
python -m pytest tests/ -q
```

Testes visuais são **manuais**: abrir o HTML gerado em Chrome e inspeccionar. Não há snapshot testing porque o output é um single-file HTML ~2 MB que mudaria constantemente.

---

## Links

- Spec canónica: [`docs/superpowers/specs/2026-04-11-design-system-sga-design.md`](../../docs/superpowers/specs/2026-04-11-design-system-sga-design.md)
- Consumer guide: [`docs/design-system-guide.md`](../../docs/design-system-guide.md)
- Scripts README: [`shared/scripts/README.md`](../scripts/README.md)
- Shared root: [`shared/README.md`](../README.md)
