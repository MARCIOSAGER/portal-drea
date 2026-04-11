# shared/scripts/ — JavaScript partilhado do Design System SGA

O JavaScript de chrome e utilities partilhado entre portais vive nesta directoria. É consumido pelos `build.py` de cada portal como ficheiros inline que o próprio source HTML importa via `<script src="...">` ou por inlining directo.

Para **consumir** o DS, ver [`docs/design-system-guide.md`](../../docs/design-system-guide.md). Este README é para quem **contribui** para o DS.

---

## O que vive aqui

Na v2.1.0-alpha.1:

- `chrome/splash.js` — lifecycle do splash screen (fade-out em 1500ms, bypass `?nosplash=1`)
- `utilities/date-utc.js` — UTC clock ticker (actualiza elementos `#clockDisplay`, `#headerUTC`, `#headerDate`)

Ficheiros planeados para versões futuras (ainda inlined nas source HTMLs):

- `awm-modal.js` — lifecycle do modal `.awm-modal`
- `awm-toast.js` — sistema de toasts `window.notify()` / `window.awmAlert()`
- `awm-save-badge.js` — indicador `uxp-savebadge`
- `utilities/ls-wrapper.js` — `window.lsGet` / `window.lsSet` abstracting `localStorage`
- `utilities/esc-html.js` — `window.escHtml` para sanitização

A extracção destes ficheiros está adiada para v2.2.0 (ver [`docs/CHANGELOG.md`](../../docs/CHANGELOG.md) known limitations).

---

## Como são consumidos

Os ficheiros de `shared/scripts/` podem ser consumidos de duas formas:

1. **Inline concatenation** (padrão actual para chrome/splash.js): o `build.py` lê o ficheiro e injecta o conteúdo dentro de um `<script>` inline no `<body>` do HTML final. Isto mantém a propriedade single-file offline-capable.

2. **Placeholder substitution** (futuro para `{{DS_JS}}`): o build agrupa todos os scripts numa ordem determinística e substitui um placeholder único. Similar ao `{{DS_CSS}}` para styles.

A ordem e mecanismo estão implementados em [`scripts/ds_build_helpers.py`](../../scripts/ds_build_helpers.py).

---

## Regras de coupling

### Sem referências a globals específicos de portal

Nenhum script em `shared/scripts/` pode referir `window.AWM_CONTACTS_DEFAULT`, `window.PSCI_CFG`, ou qualquer outro global que exista apenas num portal específico. Se precisa de dados do portal, usar uma API genérica:

```js
// ❌ errado — acopla ao COE
var contactos = window.AWM_CONTACTS_DEFAULT;

// ✅ certo — usa a API que ambos os portais expõem
var contactos = window.awmContacts && window.awmContacts.getAll();
```

### Sem assumir a existência de secções

Um script não pode assumir que `document.getElementById('dashboard-coe')` existe, porque o SSCI não tem essa secção. Usar null-checks:

```js
var dashboard = document.getElementById('dashboard-coe');
if (!dashboard) return;  // SSCI — secção não existe, aborta silenciosamente
// ... código que usa dashboard ...
```

### Sem acesso directo a localStorage

Estado global é lido via `window.lsGet(key)` e escrito via `window.lsSet(key, val)`. Nunca `localStorage.getItem()` directo — isso acopla o código à implementação de persistência, que pode mudar no futuro (ver ARCHITECTURE.md para o roadmap Fase 2-3).

```js
// ❌ errado
var state = JSON.parse(localStorage.getItem('coe_awm_config') || '{}');

// ✅ certo
var state = window.lsGet('coe_awm_config', {});
```

### Sem `document.write`, `innerHTML` sem escape, ou eval

Segurança básica. Usar `textContent` para inserir texto utilizador, `window.escHtml()` se precisas de HTML, e factoring de fragmentos via DOM APIs.

### Sem dependências externas

Zero imports. Zero CDN. Tudo vanilla JavaScript compatível com Chrome 90+ / Edge 90+ / Firefox 88+.

---

## Como adicionar um novo script partilhado

1. **Criar o ficheiro** em `shared/scripts/` (ou `shared/scripts/chrome/`, `shared/scripts/utilities/`, conforme a semântica)
2. **Cabeçalho**: comentário `/*! Design System SGA — ... */` com propósito e dependências explícitas
3. **IIFE**: envolver em `(function(){ 'use strict'; ... })();` para evitar poluir o global scope (excepto para APIs explicitamente exportadas)
4. **Testar em ambos os portais** — abrir COE e SSCI, verificar comportamento e console
5. **Documentar exports** no topo do ficheiro (se exporta algo para `window.*`)
6. **Registar ordering** em `ds_build_helpers.py` se este script depende da ordem de execução relativa a outros
7. **Correr** `python scripts/build-all.py` e validar sintacticamente com `node --check` (o build já faz isto automaticamente)

### Exemplo mínimo

```js
/*!
 * Design System SGA — utilities/my-helper.js
 * ------------------------------------------------------------
 * Purpose: <one-line description>
 * Exports: window.myHelper.<methods>
 * Dependencies: none
 * ============================================================ */
(function () {
    'use strict';

    function myMethod() {
        /* ... */
    }

    window.myHelper = {
        method: myMethod
    };
})();
```

---

## Test harness

Não há testes unitários para os scripts JavaScript. As garantias actuais são:

- **Validação sintáctica** via `node --check` durante cada build (erro de sintaxe → build falha)
- **Smoke tests manuais** em Chrome, Edge, Firefox antes de cada release
- **JS-load-bearing contracts** documentados em [`docs/design-system-guide.md`](../../docs/design-system-guide.md) para classes/IDs preservados

Para v2.2.0 está previsto adicionar testes com Playwright para fluxos críticos.

---

## Links

- Consumer guide: [`docs/design-system-guide.md`](../../docs/design-system-guide.md)
- Styles README: [`shared/styles/README.md`](../styles/README.md)
- Shared root: [`shared/README.md`](../README.md)
- Build helpers: [`scripts/ds_build_helpers.py`](../../scripts/ds_build_helpers.py)
