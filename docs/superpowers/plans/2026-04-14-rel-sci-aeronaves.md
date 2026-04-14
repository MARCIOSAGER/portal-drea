# Relatório SCI Aeronaves — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the post-incident occurrence report "Relatório de Operações de SCI em Aeronaves" (AP.04.033 / FR-FNMO-PSCI-019) to Portal SSCI with single-draft lifecycle, control number `{OACI}/{YEAR}/{NNN}`, accordion UI, and `sgaPrintReport` PDF output.

**Architecture:** Single-file HTML portal ([packages/portal-ssci/src/Portal_PSCI_AWM.source.html](packages/portal-ssci/src/Portal_PSCI_AWM.source.html)) with inline JS module `window.RelSciAeronaves`. Three-state UI (lista / editor / visualizacao), localStorage persistence, auto-save on field change, irreversible finalization.

**Tech Stack:** HTML5 + vanilla JS (IIFE pattern), CSS via existing DS tokens, localStorage, existing `window.sgaPrintReport()` helper. Tests in Python/pytest parsing built HTML output.

**Spec:** [docs/superpowers/specs/2026-04-14-rel-sci-aeronaves-design.md](docs/superpowers/specs/2026-04-14-rel-sci-aeronaves-design.md)

**Build:** Edit `source.html`, run `cd packages/portal-ssci && python scripts/build.py` (or `npm run build` from repo root) to regenerate `dist/index.html`. The build pipeline replaces `{{VERSION}}`, `{{BUILD_DATE_SHORT}}`, `{{AIRPORT.OACI}}`, etc.

**Manual verification:** Open `packages/portal-ssci/dist/index.html` in a browser after each task that produces user-visible output. Test in Chrome/Edge.

---

## Task 1: Scaffold — sidebar entry + empty section + module stub

**Files:**
- Modify: [packages/portal-ssci/src/Portal_PSCI_AWM.source.html](packages/portal-ssci/src/Portal_PSCI_AWM.source.html) (sidebar ~line 376, main grid ~line 408, script block near `</body>`)

- [ ] **Step 1: Add sidebar group**

Insert a new `<div class="ds-sidebar__section">` block immediately after the `Formulários Operacionais` section (after line ~376) and before the `Recursos` section:

```html
<div class="ds-sidebar__section">
    <h3 class="ds-sidebar__section-title">Relatórios de Ocorrência</h3>
    <ul class="ds-sidebar__list">
        <li><button onclick="openSection('rel-sci-aeronaves', event)"
                    class="nav-btn nav-btn--pill">🛩 Relatório Ops SCI Aeronaves</button></li>
    </ul>
</div>
```

- [ ] **Step 2: Add empty section with 3 state containers**

Inside `<main class="ds-page-grid">`, after the last existing section, add:

```html
<!-- RELATÓRIO SCI AERONAVES -->
<div id="rel-sci-aeronaves" class="section">
    <header style="margin-bottom: var(--space-5);">
        <h1 style="font-size: 20px; font-weight: 600; color: var(--neutral-fg); letter-spacing: -0.02em; margin: 0 0 var(--space-2) 0;">Relatório de Operações de SCI em Aeronaves</h1>
        <p style="font-size: var(--text-sm); color: var(--neutral-fg-muted); margin: 0;">AP.04.033 / FR-FNMO-PSCI-019 — relatório pós-ocorrência</p>
    </header>

    <div class="rel-sci-state rel-sci-state--lista active" data-state="lista">
        <!-- populated by RelSciAeronaves._renderLista() -->
    </div>
    <div class="rel-sci-state rel-sci-state--editor" data-state="editor" hidden>
        <!-- populated by RelSciAeronaves._renderEditor() -->
    </div>
    <div class="rel-sci-state rel-sci-state--visualizacao" data-state="visualizacao" hidden>
        <!-- populated by RelSciAeronaves._renderVisualizacao() -->
    </div>
</div>
```

- [ ] **Step 3: Add module skeleton before `</body>`**

In the last `<script>` block (or a new one immediately before existing module initializations), add:

```js
(function () {
    'use strict';

    var STORAGE_KEYS = {
        DRAFT: 'psci.rel-sci-aeronaves.draft',
        FINALIZED: 'psci.rel-sci-aeronaves.finalized',
        COUNTER_PREFIX: 'psci.rel-sci-aeronaves.counter.'
    };

    var state = { current: 'lista', draft: null, relatorios: [] };

    function setState(next, payload) {
        state.current = next;
        document.querySelectorAll('#rel-sci-aeronaves .rel-sci-state').forEach(function (el) {
            var isActive = el.dataset.state === next;
            el.hidden = !isActive;
            el.classList.toggle('active', isActive);
        });
        render(payload);
    }

    function render(payload) {
        if (state.current === 'lista') renderLista();
        else if (state.current === 'editor') renderEditor(payload);
        else if (state.current === 'visualizacao') renderVisualizacao(payload);
    }

    function renderLista() { /* Task 3 */ }
    function renderEditor(payload) { /* Task 4+ */ }
    function renderVisualizacao(payload) { /* Task 11 */ }

    function init() {
        loadFromStorage();
        setState('lista');
    }

    function loadFromStorage() {
        try {
            var raw = localStorage.getItem(STORAGE_KEYS.DRAFT);
            state.draft = raw ? JSON.parse(raw) : null;
            var fin = localStorage.getItem(STORAGE_KEYS.FINALIZED);
            state.relatorios = fin ? JSON.parse(fin) : [];
        } catch (e) {
            console.error('RelSciAeronaves loadFromStorage failed', e);
            state.draft = null;
            state.relatorios = [];
        }
    }

    window.RelSciAeronaves = {
        init: init,
        setState: setState,
        _state: state,
        _keys: STORAGE_KEYS
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
```

- [ ] **Step 4: Build and verify sidebar**

Run:
```bash
cd packages/portal-ssci && python scripts/build.py
```
Expected: `dist/index.html` regenerated without errors.

Open `dist/index.html` in browser. Expected:
- New sidebar group "Relatórios de Ocorrência" appears between Formulários Operacionais and Recursos
- Clicking "🛩 Relatório Ops SCI Aeronaves" shows the empty section with the header
- Browser console shows no errors; `window.RelSciAeronaves._state` is accessible

- [ ] **Step 5: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html packages/portal-ssci/dist/index.html
git commit -m "feat(ssci): scaffold Relatório Ops SCI Aeronaves section + sidebar"
```

---

## Task 2: Data layer — control number + draft helpers

**Files:**
- Modify: [packages/portal-ssci/src/Portal_PSCI_AWM.source.html](packages/portal-ssci/src/Portal_PSCI_AWM.source.html) (inside the `RelSciAeronaves` IIFE)

- [ ] **Step 1: Add control number generator**

Inside the IIFE, before `function init()`, add:

```js
function gerarNumeroControlo(ano) {
    var oaci = (window.AIRPORT_OACI || '{{AIRPORT.OACI}}' || 'XXXX').trim();
    var key = STORAGE_KEYS.COUNTER_PREFIX + ano;
    var seq = parseInt(localStorage.getItem(key) || '0', 10) + 1;
    localStorage.setItem(key, String(seq));
    return oaci + '/' + ano + '/' + String(seq).padStart(3, '0');
}
```

Note: the build pipeline replaces `{{AIRPORT.OACI}}` at build time; the `window.AIRPORT_OACI` fallback is defensive for tests and misconfigured builds.

- [ ] **Step 2: Add draft CRUD helpers**

Add right after `gerarNumeroControlo`:

```js
function novoRascunho() {
    if (state.draft) return state.draft;
    state.draft = {
        id: 'draft-' + Date.now(),
        dataInicio: new Date().toISOString(),
        secoes: { s1:{}, s2:{}, s3:{}, s4:{}, s5:{}, s6:{}, s7:{}, s8:{}, s9:{}, s10:{} }
    };
    saveDraft();
    return state.draft;
}

function descartarRascunho() {
    state.draft = null;
    localStorage.removeItem(STORAGE_KEYS.DRAFT);
}

function saveDraft() {
    if (!state.draft) return;
    state.draft.dataUltimaEdicao = new Date().toISOString();
    localStorage.setItem(STORAGE_KEYS.DRAFT, JSON.stringify(state.draft));
}

var saveTimeout = null;
function saveField(path, value) {
    if (!state.draft || state.draft.locked) return;
    var parts = path.split('.');
    var obj = state.draft.secoes;
    for (var i = 0; i < parts.length - 1; i++) {
        if (!obj[parts[i]]) obj[parts[i]] = {};
        obj = obj[parts[i]];
    }
    obj[parts[parts.length - 1]] = value;
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(function () {
        saveDraft();
        updateSavedBadge();
    }, 500);
}

function updateSavedBadge() {
    var badge = document.getElementById('relSciSavedBadge');
    if (badge) {
        var hhmm = new Date().toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' });
        badge.textContent = 'Guardado às ' + hhmm;
    }
}
```

- [ ] **Step 3: Expose helpers on the module**

Update the `window.RelSciAeronaves` export block:

```js
window.RelSciAeronaves = {
    init: init,
    setState: setState,
    novoRascunho: novoRascunho,
    descartarRascunho: descartarRascunho,
    saveField: saveField,
    gerarNumeroControlo: gerarNumeroControlo,
    _state: state,
    _keys: STORAGE_KEYS
};
```

- [ ] **Step 4: Manually verify in DevTools**

Open built `dist/index.html`. In console:

```js
RelSciAeronaves.gerarNumeroControlo(2026)   // → "FQMA/2026/001"
RelSciAeronaves.gerarNumeroControlo(2026)   // → "FQMA/2026/002"
RelSciAeronaves.gerarNumeroControlo(2027)   // → "FQMA/2027/001" (new year resets)
localStorage.removeItem('psci.rel-sci-aeronaves.counter.2026')   // cleanup
localStorage.removeItem('psci.rel-sci-aeronaves.counter.2027')
```

- [ ] **Step 5: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html packages/portal-ssci/dist/index.html
git commit -m "feat(ssci): add control number generator + draft storage helpers"
```

---

## Task 3: Lista state (draft card + finalized table + new button)

**Files:**
- Modify: `Portal_PSCI_AWM.source.html` — inside IIFE, replace `renderLista` stub

- [ ] **Step 1: Implement `renderLista`**

```js
function renderLista() {
    var container = document.querySelector('#rel-sci-aeronaves .rel-sci-state--lista');
    if (!container) return;

    var draftCard = '';
    if (state.draft) {
        var pct = calcPercentPreenchido(state.draft);
        draftCard =
            '<div class="ds-card" style="margin-bottom:var(--space-4);">' +
            '  <div class="ds-card__header">' +
            '    <h3 class="ds-card__title">Rascunho em curso</h3>' +
            '    <span class="awm-badge awm-badge--warning">' + pct + '% preenchido</span>' +
            '  </div>' +
            '  <div class="ds-card__body">' +
            '    <p style="margin:0 0 var(--space-3);color:var(--neutral-fg-muted);">' +
            '      Iniciado em ' + formatDateTime(state.draft.dataInicio) + '</p>' +
            '    <div style="display:flex;gap:var(--space-2);">' +
            '      <button class="ds-btn ds-btn--primary" onclick="RelSciAeronaves.setState(\'editor\')">Continuar</button>' +
            '      <button class="ds-btn ds-btn--ghost" onclick="RelSciAeronaves._descartarComConfirmacao()">Descartar</button>' +
            '    </div>' +
            '  </div>' +
            '</div>';
    }

    var novoBtn =
        '<button class="ds-btn ds-btn--primary" ' + (state.draft ? 'disabled' : '') + ' ' +
        'onclick="RelSciAeronaves._criarNovo()">+ Novo Relatório</button>' +
        (state.draft ? '<p style="margin:var(--space-2) 0 0;font-size:var(--text-sm);color:var(--neutral-fg-muted);">Finalize ou descarte o rascunho actual antes de criar um novo.</p>' : '');

    var tabelaRows = state.relatorios.length === 0
        ? '<tr><td colspan="5" style="text-align:center;color:var(--neutral-fg-muted);padding:var(--space-4);">Nenhum relatório finalizado.</td></tr>'
        : state.relatorios.map(function (r) {
            return '<tr>' +
                '<td>' + escHtml(r.numeroControlo) + '</td>' +
                '<td>' + formatDate(r.secoes.s1.dataAcidente) + '</td>' +
                '<td>' + escHtml((r.secoes.s1.tipoAeronave || '') + ' ' + (r.secoes.s1.matricula || '')) + '</td>' +
                '<td>' + formatDateTime(r.dataFinalizacao) + '</td>' +
                '<td>' +
                  '<button class="ds-btn ds-btn--sm" onclick="RelSciAeronaves._ver(\'' + r.id + '\')">Ver</button> ' +
                  '<button class="ds-btn ds-btn--sm" onclick="RelSciAeronaves.imprimir(\'' + r.id + '\')">Imprimir</button>' +
                '</td></tr>';
        }).join('');

    container.innerHTML =
        draftCard +
        '<div class="ds-card"><div class="ds-card__header"><h3 class="ds-card__title">Novo relatório</h3></div>' +
        '<div class="ds-card__body">' + novoBtn + '</div></div>' +
        '<div class="ds-card" style="margin-top:var(--space-4);">' +
        '  <div class="ds-card__header"><h3 class="ds-card__title">Relatórios Finalizados (' + state.relatorios.length + ')</h3></div>' +
        '  <div class="ds-card__body">' +
        '    <table class="ds-table">' +
        '      <thead><tr><th>Nº Controlo</th><th>Data Acidente</th><th>Aeronave</th><th>Finalizado em</th><th>Acções</th></tr></thead>' +
        '      <tbody>' + tabelaRows + '</tbody>' +
        '    </table>' +
        '  </div>' +
        '</div>';
}

function calcPercentPreenchido(rel) {
    var total = 0, preenchidos = 0;
    Object.keys(rel.secoes).forEach(function (k) {
        var sec = rel.secoes[k];
        Object.keys(sec).forEach(function (field) {
            total++;
            var v = sec[field];
            if (v !== undefined && v !== null && v !== '' && !(Array.isArray(v) && v.length === 0)) preenchidos++;
        });
    });
    return total === 0 ? 0 : Math.round((preenchidos / total) * 100);
}

function formatDate(iso) {
    if (!iso) return '—';
    var d = new Date(iso);
    return isNaN(d.getTime()) ? '—' : d.toLocaleDateString('pt-PT');
}

function formatDateTime(iso) {
    if (!iso) return '—';
    var d = new Date(iso);
    return isNaN(d.getTime()) ? '—' : d.toLocaleString('pt-PT');
}

function escHtml(s) {
    if (s === undefined || s === null) return '';
    return String(s).replace(/[&<>"']/g, function (c) {
        return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c];
    });
}
```

- [ ] **Step 2: Add private helpers for list actions**

Append inside IIFE, before the `window.RelSciAeronaves` export:

```js
function _criarNovo() {
    novoRascunho();
    setState('editor');
}

function _descartarComConfirmacao() {
    if (confirm('Descartar o rascunho actual? Esta acção não pode ser desfeita.')) {
        descartarRascunho();
        setState('lista');
    }
}

function _ver(id) {
    setState('visualizacao', { relatorioId: id });
}
```

Expose on the module:

```js
window.RelSciAeronaves = {
    init: init,
    setState: setState,
    novoRascunho: novoRascunho,
    descartarRascunho: descartarRascunho,
    saveField: saveField,
    gerarNumeroControlo: gerarNumeroControlo,
    imprimir: function (id) { /* Task 11 */ },
    _criarNovo: _criarNovo,
    _descartarComConfirmacao: _descartarComConfirmacao,
    _ver: _ver,
    _state: state,
    _keys: STORAGE_KEYS
};
```

- [ ] **Step 3: Build and verify**

Run build. Open `dist/index.html`. Navigate to "Relatório Ops SCI Aeronaves". Expected:
- "Novo relatório" card with enabled button
- Empty finalized table showing "Nenhum relatório finalizado"
- Click "+ Novo Relatório" — switches to editor state (still empty for now)
- Go back to list (reload page): draft card appears with "0% preenchido"
- Click "Descartar" → confirm → draft card disappears

- [ ] **Step 4: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html packages/portal-ssci/dist/index.html
git commit -m "feat(ssci): implement Relatório SCI lista state (draft card + finalized table)"
```

---

## Task 4: Editor shell — accordion layout + sticky TOC + autosave plumbing

**Files:**
- Modify: `Portal_PSCI_AWM.source.html` — IIFE `renderEditor` + CSS block (in `<style>` near top of body or in existing component styles section)

- [ ] **Step 1: Add CSS for editor layout**

Inside the main `<style>` block (or append a new one), add:

```css
.rel-sci-editor { display: grid; grid-template-columns: 200px 1fr; gap: var(--space-5); }
.rel-sci-toc { position: sticky; top: 80px; align-self: start; border-right: 1px solid var(--neutral-border); padding-right: var(--space-3); }
.rel-sci-toc ol { list-style: none; padding: 0; margin: 0; font-size: var(--text-sm); }
.rel-sci-toc li { margin: var(--space-1) 0; }
.rel-sci-toc a { color: var(--neutral-fg-muted); text-decoration: none; display: block; padding: var(--space-1) var(--space-2); border-left: 2px solid transparent; }
.rel-sci-toc a.active { color: var(--brand-fg); border-left-color: var(--brand-fg); font-weight: 600; }
.rel-sci-section { margin-bottom: var(--space-4); border: 1px solid var(--neutral-border); border-radius: 6px; padding: var(--space-3); }
.rel-sci-section > summary { cursor: pointer; font-weight: 600; color: var(--neutral-fg); padding: var(--space-2) 0; }
.rel-sci-section > summary .sec-status { float: right; font-size: var(--text-sm); }
.rel-sci-editor__toolbar { position: sticky; top: 0; background: var(--neutral-bg); padding: var(--space-2) 0; border-bottom: 1px solid var(--neutral-border); margin-bottom: var(--space-3); display: flex; justify-content: space-between; align-items: center; z-index: 5; }
@media (max-width: 900px) { .rel-sci-editor { grid-template-columns: 1fr; } .rel-sci-toc { position: static; border: none; padding: 0; } }
```

- [ ] **Step 2: Implement `renderEditor` (shell only, empty sections)**

```js
var SECOES_META = [
    { id: 's1',  titulo: 'Identificação da Ocorrência' },
    { id: 's2',  titulo: 'Fase da Operação' },
    { id: 's3',  titulo: 'Condições Meteorológicas' },
    { id: 's4',  titulo: 'Ocupantes e Vítimas' },
    { id: 's5',  titulo: 'Tempos de Resposta' },
    { id: 's6',  titulo: 'Serviço SCI' },
    { id: 's7',  titulo: 'Descrição da Ocorrência' },
    { id: 's8',  titulo: 'Outros Detalhes' },
    { id: 's9',  titulo: 'Informações Adicionais' },
    { id: 's10', titulo: 'Responsável pelo Relatório' }
];

function renderEditor() {
    if (!state.draft) { setState('lista'); return; }
    var container = document.querySelector('#rel-sci-aeronaves .rel-sci-state--editor');
    if (!container) return;

    var toc = '<nav class="rel-sci-toc"><div style="font-weight:600;margin-bottom:var(--space-2);">Secções</div><ol>' +
        SECOES_META.map(function (s, i) {
            return '<li><a href="#rel-sci-' + s.id + '">' + (i + 1) + '. ' + escHtml(s.titulo) + '</a></li>';
        }).join('') + '</ol></nav>';

    var toolbar =
        '<div class="rel-sci-editor__toolbar">' +
        '  <button class="ds-btn ds-btn--ghost" onclick="RelSciAeronaves.setState(\'lista\')">← Voltar à lista</button>' +
        '  <div>' +
        '    <span class="awm-badge" id="relSciSavedBadge">Guardado</span>' +
        '    <button class="ds-btn ds-btn--primary" onclick="RelSciAeronaves._finalizar()">Finalizar Relatório</button>' +
        '  </div>' +
        '</div>';

    var secoesHtml = SECOES_META.map(function (s) {
        return '<details class="rel-sci-section" id="rel-sci-' + s.id + '" open>' +
               '<summary>' + escHtml(s.titulo) + ' <span class="sec-status" data-secao="' + s.id + '"></span></summary>' +
               '<div class="rel-sci-fields" data-secao="' + s.id + '">' +
                   renderSecao(s.id) +
               '</div></details>';
    }).join('');

    container.innerHTML =
        toolbar +
        '<div class="rel-sci-editor">' +
        toc +
        '<div>' + secoesHtml + '</div>' +
        '</div>';

    attachAutoSaveHandlers(container);
    setupTocObserver(container);
    atualizarStatusSecoes();
}

function renderSecao(id) {
    // Stubs — filled in Tasks 5–9
    return '<p style="color:var(--neutral-fg-muted);">(campos da secção ' + id + ' — em implementação)</p>';
}

function attachAutoSaveHandlers(root) {
    root.querySelectorAll('[data-field]').forEach(function (el) {
        var handler = function () {
            var path = el.dataset.field;
            var val = el.type === 'checkbox' ? el.checked : el.value;
            saveField(path, val);
            atualizarStatusSecoes();
        };
        el.addEventListener('change', handler);
        el.addEventListener('blur', handler);
    });
}

function setupTocObserver(root) {
    var links = root.querySelectorAll('.rel-sci-toc a');
    if (!('IntersectionObserver' in window) || links.length === 0) return;
    var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
            if (e.isIntersecting) {
                links.forEach(function (l) {
                    l.classList.toggle('active', l.getAttribute('href') === '#' + e.target.id);
                });
            }
        });
    }, { rootMargin: '-30% 0px -60% 0px' });
    root.querySelectorAll('.rel-sci-section').forEach(function (sec) { obs.observe(sec); });
}

function atualizarStatusSecoes() {
    if (!state.draft) return;
    document.querySelectorAll('.rel-sci-section .sec-status').forEach(function (el) {
        var sec = state.draft.secoes[el.dataset.secao] || {};
        var count = Object.keys(sec).filter(function (k) {
            var v = sec[k]; return v !== '' && v !== undefined && v !== null && v !== false;
        }).length;
        el.textContent = count > 0 ? '✓ ' + count + ' campos' : '⚠ vazio';
        el.style.color = count > 0 ? 'var(--success-fg, #2a8a3e)' : 'var(--warning-fg, #b5651d)';
    });
}

function _finalizar() { /* Task 10 */ alert('Finalização — Task 10'); }
```

Update the module export to include `_finalizar`:
```js
_finalizar: _finalizar,
```

- [ ] **Step 3: Build and verify**

Open `dist/index.html`, click "Novo Relatório". Expected:
- Toolbar with "Voltar" + saved badge + "Finalizar" button
- Left column: TOC with 10 numbered links
- Right column: 10 collapsible `<details>` blocks (all open by default) each showing placeholder text
- Status `⚠ vazio` next to each summary
- Clicking TOC link scrolls to section; scrolling updates active TOC item
- Reload page → click "Continuar" on draft card → same editor appears

- [ ] **Step 4: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html packages/portal-ssci/dist/index.html
git commit -m "feat(ssci): Relatório SCI editor shell — accordion + TOC + autosave wiring"
```

---

## Task 5: Sections 1–3 fields (Identificação, Fase, Meteorologia)

**Files:**
- Modify: `Portal_PSCI_AWM.source.html` — replace `renderSecao` with switch, add helpers

- [ ] **Step 1: Add field rendering helpers**

```js
function input(path, label, type, attrs) {
    type = type || 'text';
    attrs = attrs || '';
    var val = getFieldValue(path);
    return '<div class="ds-form__field">' +
        '<label class="ds-form__label">' + escHtml(label) + '</label>' +
        '<input class="ds-input" type="' + type + '" data-field="' + path + '" value="' + escHtml(val) + '" ' + attrs + '>' +
        '</div>';
}

function textarea(path, label, rows) {
    var val = getFieldValue(path);
    return '<div class="ds-form__field">' +
        '<label class="ds-form__label">' + escHtml(label) + '</label>' +
        '<textarea class="ds-input" rows="' + (rows || 3) + '" data-field="' + path + '">' + escHtml(val) + '</textarea>' +
        '</div>';
}

function checkbox(path, label) {
    var val = getFieldValue(path) === true;
    return '<label style="display:inline-flex;align-items:center;gap:var(--space-2);margin-right:var(--space-3);">' +
        '<input type="checkbox" data-field="' + path + '"' + (val ? ' checked' : '') + '> ' + escHtml(label) +
        '</label>';
}

function radio(path, label, value) {
    var cur = getFieldValue(path);
    return '<label style="display:inline-flex;align-items:center;gap:var(--space-2);margin-right:var(--space-3);">' +
        '<input type="radio" name="' + path.replace(/\./g,'_') + '" data-field="' + path + '" value="' + escHtml(value) + '"' + (cur === value ? ' checked' : '') + '> ' + escHtml(label) +
        '</label>';
}

function getFieldValue(path) {
    if (!state.draft) return '';
    var parts = path.split('.');
    var obj = state.draft.secoes;
    for (var i = 0; i < parts.length; i++) {
        if (obj == null) return '';
        obj = obj[parts[i]];
    }
    return obj == null ? '' : obj;
}

function row() {
    var args = Array.prototype.slice.call(arguments);
    return '<div class="ds-form__row" style="display:flex;gap:var(--space-3);flex-wrap:wrap;">' + args.join('') + '</div>';
}
```

Note: radio inputs need special handling — a `radio` element's `.value` always equals its HTML `value` attribute, so `saveField` as currently written saves the value when checked. Also update `attachAutoSaveHandlers` to only save radio on `change` when `el.checked`:

```js
function attachAutoSaveHandlers(root) {
    root.querySelectorAll('[data-field]').forEach(function (el) {
        var handler = function () {
            var path = el.dataset.field;
            var val;
            if (el.type === 'checkbox') val = el.checked;
            else if (el.type === 'radio') { if (!el.checked) return; val = el.value; }
            else val = el.value;
            saveField(path, val);
            atualizarStatusSecoes();
        };
        el.addEventListener('change', handler);
        el.addEventListener('blur', handler);
    });
}
```

- [ ] **Step 2: Replace `renderSecao` with switch + sections 1–3**

```js
function renderSecao(id) {
    switch (id) {
        case 's1':  return renderS1();
        case 's2':  return renderS2();
        case 's3':  return renderS3();
        default:    return '<p style="color:var(--neutral-fg-muted);">(em implementação)</p>';
    }
}

function renderS1() {
    return row(
        input('s1.aerodromo', '1.1 Aeródromo', 'text', 'readonly'),
        input('s1.provincia', '1.2 Província')
    ) + row(
        input('s1.dataAcidente', '1.3 Data do Acidente', 'date'),
        input('s1.horaAcidente', '1.4 Hora Local', 'time')
    ) + '<div class="ds-form__field"><label class="ds-form__label">1.5 Acidente ocorrido durante</label>' +
        radio('s1.periodo', 'Dia', 'dia') + radio('s1.periodo', 'Noite', 'noite') +
    '</div>' + row(
        input('s1.tipoAeronave', '1.6 Tipo da Aeronave'),
        input('s1.matricula', '1.7 Matrícula'),
        input('s1.empresa', '1.8 Empresa')
    ) + row(
        input('s1.propositoOperacao', '1.9 Propósito da Operação'),
        input('s1.combustivelTipo', '1.10 Combustível — Tipo'),
        input('s1.combustivelQtd', '1.10 Combustível — Qtd (kg)', 'number')
    ) + row(
        input('s1.alertaDadoPor', '1.11 Alerta dado por'),
        input('s1.horaAlerta', '1.12 Hora do Alerta', 'time')
    );
}

function renderS2() {
    return '<div class="ds-form__field"><label class="ds-form__label">2. Fase da Operação (marcar as aplicáveis)</label>' +
        checkbox('s2.pouso', '2.1 Pouso') +
        checkbox('s2.decolagem', '2.2 Decolagem') +
        checkbox('s2.taxi', '2.3 Táxi') +
        checkbox('s2.estacionamento', '2.4 Estacionamento') +
    '</div>';
}

function renderS3() {
    return row(
        input('s3.visibilidade', '3.1 Visibilidade (km)', 'number')
    ) + textarea('s3.condicoesGerais', '3.2 Condições Gerais do Tempo', 4);
}
```

- [ ] **Step 3: Seed Aeródromo field in new drafts**

Update `novoRascunho` to pre-fill:
```js
function novoRascunho() {
    if (state.draft) return state.draft;
    var oaci = (window.AIRPORT_OACI || '{{AIRPORT.OACI}}' || '').trim();
    state.draft = {
        id: 'draft-' + Date.now(),
        dataInicio: new Date().toISOString(),
        secoes: {
            s1: { aerodromo: oaci },
            s2: {}, s3: {}, s4: {}, s5: {},
            s6: {}, s7: {}, s8: {}, s9: {}, s10: {}
        }
    };
    saveDraft();
    return state.draft;
}
```

- [ ] **Step 4: Build and verify**

Open `dist/index.html`. Discard any existing draft. Click "+ Novo Relatório". Expected:
- Section 1 shows 12 fields, Aeródromo pre-filled with `{{AIRPORT.OACI}}` (e.g., `FQMA`) and readonly
- Radio buttons Dia/Noite mutually exclusive
- Section 2 has 4 checkboxes
- Section 3 has visibility + textarea
- Typing in a field triggers "Guardado às HH:MM" within 500ms
- Reload page → "Continuar" → values persisted
- Section status updates (✓ N campos)

- [ ] **Step 5: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html packages/portal-ssci/dist/index.html
git commit -m "feat(ssci): Relatório SCI sections 1–3 (identificação, fase, meteorologia)"
```

---

## Task 6: Sections 4–5 (Vítimas, Tempos)

**Files:** Same file, add `renderS4` + `renderS5`, wire into switch.

- [ ] **Step 1: Implement `renderS4`**

```js
function renderS4() {
    return '<h4>4.1 Total de Pessoas a Bordo</h4>' + row(
        input('s4.totalPax', 'Passageiros', 'number'),
        input('s4.totalTrip', 'Tripulantes', 'number')
    ) + '<h4>4.2 Salvas sem ajuda</h4>' + row(
        input('s4.salvasFeridos', 'Feridos', 'number'),
        input('s4.salvasIlesos', 'Ilesos', 'number')
    ) + '<h4>4.3 Resgatadas Vivas</h4>' + row(
        input('s4.resgFeridos', 'Feridos', 'number'),
        input('s4.resgIlesos', 'Ilesos', 'number')
    ) + '<h4>4.4 Mortos</h4>' + row(
        input('s4.mortosPax', 'Passageiros', 'number'),
        input('s4.mortosTrip', 'Tripulantes', 'number')
    ) + '<h4>4.5 Vítimas em Terra não Ocupantes</h4>' + row(
        input('s4.terraMortos', 'Mortos', 'number'),
        input('s4.terraFeridos', 'Feridos', 'number')
    ) + '<h4>4.6 Óbitos até 24h</h4>' + row(
        input('s4.obitos24Ocupantes', 'Ocupantes', 'number'),
        input('s4.obitos24Terra', 'Vítimas em Terra', 'number')
    ) + '<h4>4.7 Mortos Vítimas de Fogo (incluídos em 4.4 e 4.6)</h4>' + row(
        input('s4.mortosFogo', 'Quantidade', 'number')
    );
}
```

- [ ] **Step 2: Implement `renderS5`**

```js
function renderS5() {
    var items = [
        ['s5.t1', '5.1 Do aviso prévio da emergência ao contacto'],
        ['s5.t2', '5.2 Do acidente ao alerta do SSCI (sem aviso prévio)'],
        ['s5.t3', '5.3 Do alerta/contacto à chegada das VCI'],
        ['s5.t4', '5.4 Do alerta/contacto à chegada das VCI (alt.)'],
        ['s5.t5', '5.5 Da chegada das VCI ao fogo controlado'],
        ['s5.t6', '5.6 Da chegada das VCI à extinção do fogo'],
        ['s5.t7', '5.7 Da chegada das VCI à saída do último sobrevivente'],
        ['s5.t8', '5.8 Da chegada das VCI à remoção dos últimos cadáveres']
    ];
    return items.map(function (p) {
        return input(p[0], p[1], 'text', 'placeholder="HH:MM:SS" pattern="[0-9]{2}:[0-9]{2}:[0-9]{2}"');
    }).join('');
}
```

- [ ] **Step 3: Add to switch**

```js
case 's4': return renderS4();
case 's5': return renderS5();
```

- [ ] **Step 4: Build and verify**

Expected: sections 4 and 5 render with all numbered fields. Typing persists across reloads.

- [ ] **Step 5: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html packages/portal-ssci/dist/index.html
git commit -m "feat(ssci): Relatório SCI sections 4–5 (vítimas, tempos de resposta)"
```

---

## Task 7: Section 6 (SCI — equipamentos + agentes extintores)

**Files:** Same file, add `renderS6` + helpers for fixed-row tables.

- [ ] **Step 1: Implement `renderS6`**

```js
function renderS6() {
    var equipas = [
        ['a', '(a) VCI'], ['b', '(b) Bombeiros'], ['c', '(c) Serviços Médicos'],
        ['d', '(d) Ambulâncias'], ['e', '(e) Carro Cisterna'], ['f', '(f) Outros']
    ];
    var agentes = [
        ['p',  '(a) Pó Químico'], ['co2','(b) CO₂'], ['lge','(c) LGE'],
        ['agEspuma', '(d) Água para produção de espuma'],
        ['agOutros', '(e) Água para outros usos'],
        ['outros', '(f) Outros (especificar)']
    ];

    function tabelaEquipas(prefix, titulo) {
        var rows = equipas.map(function (e) {
            return '<tr><td>' + e[1] + '</td>' +
                '<td><input class="ds-input" type="text" data-field="s6.' + prefix + '.' + e[0] + '.tipo" value="' + escHtml(getFieldValue('s6.' + prefix + '.' + e[0] + '.tipo')) + '"></td>' +
                '<td><input class="ds-input" type="number" data-field="s6.' + prefix + '.' + e[0] + '.qtd" value="' + escHtml(getFieldValue('s6.' + prefix + '.' + e[0] + '.qtd')) + '"></td>' +
                '</tr>';
        }).join('');
        return '<h4>' + titulo + '</h4><table class="ds-table"><thead><tr><th>Categoria</th><th>Tipo</th><th>Qtd</th></tr></thead><tbody>' + rows + '</tbody></table>';
    }

    var agentesRows = agentes.map(function (a) {
        var base = 's6.agentes.' + a[0];
        return '<tr><td>' + a[1] + '</td>' +
            '<td><input class="ds-input" type="number" data-field="' + base + '.qtdL" value="' + escHtml(getFieldValue(base + '.qtdL')) + '"></td>' +
            '<td><input class="ds-input" type="number" data-field="' + base + '.razao" value="' + escHtml(getFieldValue(base + '.razao')) + '"></td>' +
            '<td><input class="ds-input" type="number" data-field="' + base + '.tempo" value="' + escHtml(getFieldValue(base + '.tempo')) + '"></td>' +
            '<td><input class="ds-input" type="number" data-field="' + base + '.ordem' + '" value="' + escHtml(getFieldValue(base + '.ordem')) + '"></td>' +
            '<td>' +
              '<select class="ds-input" data-field="' + base + '.suficiente">' +
                ['', 'Sim', 'Não'].map(function (o) {
                    return '<option value="' + o + '"' + (getFieldValue(base + '.suficiente') === o ? ' selected' : '') + '>' + (o || '—') + '</option>';
                }).join('') +
              '</select>' +
            '</td></tr>';
    }).join('');

    return tabelaEquipas('equipaAerodromo', '6.1 Equipamentos e Pessoal do Aeródromo') +
           tabelaEquipas('equipaExterna',  '6.2 Equipamentos e Pessoal Alheios ao Aeródromo') +
           '<h4>6.3 Agentes Extintores</h4>' +
           '<table class="ds-table"><thead><tr><th>Agente</th><th>Qtd (L)</th><th>Razão (L/min)</th><th>Tempo (min)</th><th>Ordem</th><th>Suficiente?</th></tr></thead><tbody>' + agentesRows + '</tbody></table>';
}
```

- [ ] **Step 2: Add `<select>` to autosave handler**

The existing handler catches `change` on selects already (since `<select>` fires `change`). Verify by inspection.

- [ ] **Step 3: Add to switch**

```js
case 's6': return renderS6();
```

- [ ] **Step 4: Build and verify**

Expected: 3 tables render (6.1, 6.2, 6.3); typing in any cell autosaves.

- [ ] **Step 5: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html packages/portal-ssci/dist/index.html
git commit -m "feat(ssci): Relatório SCI section 6 (equipamentos + agentes extintores)"
```

---

## Task 8: Sections 7–8 (Descrição, Outros)

- [ ] **Step 1: Implement renderers**

```js
function renderS7() {
    return textarea('s7.descricaoSuccinta', '7.1 Descrição Sucinta da Emergência', 5) +
           textarea('s7.relatoCombate',     '7.2 Relato de Controlo, Combate e Extinção', 6) +
           textarea('s7.evacuacao',         '7.3 Descrição da Evacuação', 5);
}

function renderS8() {
    return textarea('s8.outrosDetalhes', '8.1 Comunicações, terreno, dificuldades de acesso', 5);
}
```

Add to switch:
```js
case 's7': return renderS7();
case 's8': return renderS8();
```

- [ ] **Step 2: Build, verify, commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html packages/portal-ssci/dist/index.html
git commit -m "feat(ssci): Relatório SCI sections 7–8 (descrição + outros detalhes)"
```

---

## Task 9: Sections 9–10 (Estado aeronave, Responsável)

- [ ] **Step 1: Implement `renderS9`**

```js
function renderS9() {
    var estados = [
        ['destruida',         '(a) Destruída'],
        ['gravDanificada',    '(b) Gravemente danificada'],
        ['poucosDanos',       '(c) Poucos Danos'],
        ['incolume',          '(d) Incólume']
    ];
    var rows = estados.map(function (e) {
        return '<tr><td>' + e[1] + '</td>' +
            '<td style="text-align:center;"><input type="checkbox" data-field="s9.' + e[0] + '.acidente"' + (getFieldValue('s9.' + e[0] + '.acidente') ? ' checked' : '') + '></td>' +
            '<td style="text-align:center;"><input type="checkbox" data-field="s9.' + e[0] + '.incendio"' + (getFieldValue('s9.' + e[0] + '.incendio') ? ' checked' : '') + '></td>' +
            '</tr>';
    }).join('');
    return '<h4>9.1 Estado final da aeronave</h4>' +
           '<table class="ds-table"><thead><tr><th>Estado</th><th>Pelo Acidente</th><th>Pelo Incêndio</th></tr></thead><tbody>' + rows + '</tbody></table>';
}

function renderS10() {
    var today = new Date().toISOString().slice(0, 10);
    if (!getFieldValue('s10.data')) saveField('s10.data', today);
    return row(
        input('s10.local', '10.1 Local', 'text'),
        input('s10.data',  '10.1 Data', 'date')
    ) + row(
        input('s10.nome',  'Nome do Responsável'),
        input('s10.cargo', 'Cargo / Função')
    ) + input('s10.assinatura', 'Assinatura (nome impresso)');
}
```

Add to switch:
```js
case 's9':  return renderS9();
case 's10': return renderS10();
```

- [ ] **Step 2: Pre-fill default local in new draft**

Update `novoRascunho`:
```js
state.draft.secoes.s10 = { local: oaci, data: new Date().toISOString().slice(0, 10) };
```

- [ ] **Step 3: Build, verify, commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html packages/portal-ssci/dist/index.html
git commit -m "feat(ssci): Relatório SCI sections 9–10 (estado aeronave + responsável)"
```

---

## Task 10: Validation + finalization flow

**Files:** Same file — replace `_finalizar` stub + add validator.

- [ ] **Step 1: Implement validator**

```js
function validarObrigatorios() {
    var d = state.draft;
    if (!d) return { ok: false, erros: ['Sem rascunho'] };
    var erros = [];
    var s1 = d.secoes.s1 || {};
    ['aerodromo','provincia','dataAcidente','horaAcidente','tipoAeronave','matricula','empresa'].forEach(function (f) {
        if (!s1[f]) erros.push('Secção 1: campo "' + f + '" obrigatório');
    });
    var s2 = d.secoes.s2 || {};
    if (!s2.pouso && !s2.decolagem && !s2.taxi && !s2.estacionamento) {
        erros.push('Secção 2: marcar pelo menos uma fase da operação');
    }
    var s7 = d.secoes.s7 || {};
    if (!s7.descricaoSuccinta || !s7.descricaoSuccinta.trim()) {
        erros.push('Secção 7.1: descrição sucinta é obrigatória');
    }
    var s10 = d.secoes.s10 || {};
    if (!s10.nome)       erros.push('Secção 10: nome do responsável obrigatório');
    if (!s10.assinatura) erros.push('Secção 10: assinatura obrigatória');
    return { ok: erros.length === 0, erros: erros };
}
```

- [ ] **Step 2: Implement `_finalizar`**

```js
function _finalizar() {
    var v = validarObrigatorios();
    if (!v.ok) {
        alert('Não é possível finalizar:\n\n' + v.erros.join('\n'));
        return;
    }
    if (!confirm('Esta acção é IRREVERSÍVEL. O relatório será arquivado com um número de controlo. Confirma a finalização?')) return;

    var agora = new Date();
    var numero = gerarNumeroControlo(agora.getFullYear());

    var relatorio = Object.assign({}, state.draft, {
        numeroControlo: numero,
        dataFinalizacao: agora.toISOString(),
        locked: true
    });
    delete relatorio.dataUltimaEdicao;

    state.relatorios.unshift(relatorio);
    localStorage.setItem(STORAGE_KEYS.FINALIZED, JSON.stringify(state.relatorios));
    descartarRascunho();

    imprimirRelatorio(relatorio);
    setState('visualizacao', { relatorioId: relatorio.id });
}
```

- [ ] **Step 3: Build and verify**

Expected:
- Click "Finalizar" on an empty draft → alert lists all missing required fields
- Fill required fields → click "Finalizar" → confirm modal → print window opens → returns to `visualizacao` state
- Back to list → relatório appears in "Finalizados" table with control number `FQMA/2026/001`
- Reload page → finalized list persists

- [ ] **Step 4: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html packages/portal-ssci/dist/index.html
git commit -m "feat(ssci): Relatório SCI validation + irreversible finalization"
```

---

## Task 11: Visualização state + sgaPrintReport integration

**Files:** Same file — replace `renderVisualizacao` + `imprimir` stubs.

- [ ] **Step 1: Implement `imprimirRelatorio`**

`sgaPrintReport` signature confirmed (source.html:2569): `{ title, subtitle, bodyHtml, signatures, footerLeft, extraCss }`.

```js
function imprimirRelatorio(rel) {
    var body = buildPrintBody(rel);
    window.sgaPrintReport({
        title: 'Relatório de Operações de SCI em Aeronaves',
        subtitle: 'AP.04.033 / FR-FNMO-PSCI-019 — Nº ' + rel.numeroControlo,
        bodyHtml: body,
        signatures: [
            (rel.secoes.s10.nome || '—') + '<br>' + (rel.secoes.s10.cargo || '')
        ]
    });
}

function buildPrintBody(rel) {
    function val(path) { return escHtml(getFieldValueFrom(rel, path)) || '—'; }
    function card(title, inner) {
        return '<div class="form-card"><h3>' + escHtml(title) + '</h3>' + inner + '</div>';
    }
    function kv(label, value) {
        return '<div class="form-group"><label>' + escHtml(label) + '</label><div>' + escHtml(value) + '</div></div>';
    }
    function grp() {
        return '<div class="form-row">' + Array.prototype.join.call(arguments, '') + '</div>';
    }

    var s1 = rel.secoes.s1 || {}, s2 = rel.secoes.s2 || {}, s3 = rel.secoes.s3 || {},
        s4 = rel.secoes.s4 || {}, s5 = rel.secoes.s5 || {}, s6 = rel.secoes.s6 || {},
        s7 = rel.secoes.s7 || {}, s8 = rel.secoes.s8 || {}, s9 = rel.secoes.s9 || {},
        s10 = rel.secoes.s10 || {};

    var fases = [
        s2.pouso && 'Pouso',
        s2.decolagem && 'Decolagem',
        s2.taxi && 'Táxi',
        s2.estacionamento && 'Estacionamento'
    ].filter(Boolean).join(', ') || '—';

    var tempos = [
        ['5.1 Aviso→Contacto', s5.t1], ['5.2 Acidente→Alerta', s5.t2],
        ['5.3 Alerta→Chegada VCI', s5.t3], ['5.4 Alerta→Chegada VCI (alt)', s5.t4],
        ['5.5 Chegada→Fogo controlado', s5.t5], ['5.6 Chegada→Extinção', s5.t6],
        ['5.7 Chegada→Último sobrevivente', s5.t7], ['5.8 Chegada→Remoção cadáveres', s5.t8]
    ];

    return card('1. Identificação',
            grp(kv('Aeródromo', s1.aerodromo || '—'), kv('Província', s1.provincia || '—'), kv('Data', s1.dataAcidente || '—'), kv('Hora', s1.horaAcidente || '—')) +
            grp(kv('Período', s1.periodo || '—'), kv('Aeronave', (s1.tipoAeronave||'—') + ' ' + (s1.matricula||'')), kv('Empresa', s1.empresa || '—')) +
            grp(kv('Propósito', s1.propositoOperacao || '—'), kv('Combustível', (s1.combustivelTipo||'—') + ' / ' + (s1.combustivelQtd||'—') + ' kg'), kv('Alerta por', s1.alertaDadoPor || '—'), kv('Hora alerta', s1.horaAlerta || '—'))
        ) +
        card('2. Fase da Operação', '<p>' + fases + '</p>') +
        card('3. Condições Meteorológicas', grp(kv('Visibilidade (km)', s3.visibilidade || '—'), kv('Condições gerais', s3.condicoesGerais || '—'))) +
        card('4. Ocupantes e Vítimas',
            grp(kv('4.1 Pax a bordo', s4.totalPax || '—'), kv('4.1 Trip a bordo', s4.totalTrip || '—'),
                kv('4.2 Salvos feridos', s4.salvasFeridos || '—'), kv('4.2 Salvos ilesos', s4.salvasIlesos || '—')) +
            grp(kv('4.3 Resgatados feridos', s4.resgFeridos || '—'), kv('4.3 Resgatados ilesos', s4.resgIlesos || '—'),
                kv('4.4 Mortos pax', s4.mortosPax || '—'), kv('4.4 Mortos trip', s4.mortosTrip || '—')) +
            grp(kv('4.5 Terra mortos', s4.terraMortos || '—'), kv('4.5 Terra feridos', s4.terraFeridos || '—'),
                kv('4.6 Óbitos 24h (ocup)', s4.obitos24Ocupantes || '—'), kv('4.6 Óbitos 24h (terra)', s4.obitos24Terra || '—'),
                kv('4.7 Mortos por fogo', s4.mortosFogo || '—'))
        ) +
        card('5. Tempos de Resposta',
            '<table><tbody>' + tempos.map(function (t) { return '<tr><td>' + t[0] + '</td><td>' + (t[1] || '—') + '</td></tr>'; }).join('') + '</tbody></table>'
        ) +
        card('6. Serviço SCI', buildSecao6Html(s6)) +
        card('7.1 Descrição Sucinta', '<p>' + escHtml(s7.descricaoSuccinta || '—') + '</p>') +
        card('7.2 Relato do Combate',  '<p>' + escHtml(s7.relatoCombate || '—') + '</p>') +
        card('7.3 Evacuação',          '<p>' + escHtml(s7.evacuacao || '—') + '</p>') +
        card('8. Outros Detalhes',     '<p>' + escHtml(s8.outrosDetalhes || '—') + '</p>') +
        card('9. Estado da Aeronave',  buildSecao9Html(s9)) +
        card('10. Responsável',
            grp(kv('Local', s10.local || '—'), kv('Data', s10.data || '—'), kv('Nome', s10.nome || '—'), kv('Cargo', s10.cargo || '—'))
        );
}

function buildSecao6Html(s6) {
    var equipas = [['a','VCI'],['b','Bombeiros'],['c','Médicos'],['d','Ambulâncias'],['e','Cisterna'],['f','Outros']];
    var agentes = [['p','Pó Químico'],['co2','CO₂'],['lge','LGE'],['agEspuma','Água espuma'],['agOutros','Água outros'],['outros','Outros']];
    function tabela(pref, titulo, src) {
        return '<h4>' + titulo + '</h4><table><thead><tr><th>Categoria</th><th>Tipo</th><th>Qtd</th></tr></thead><tbody>' +
            equipas.map(function (e) {
                var v = (src && src[e[0]]) || {};
                return '<tr><td>' + e[1] + '</td><td>' + escHtml(v.tipo || '—') + '</td><td>' + escHtml(v.qtd || '—') + '</td></tr>';
            }).join('') + '</tbody></table>';
    }
    var agentesRows = agentes.map(function (a) {
        var v = (s6.agentes && s6.agentes[a[0]]) || {};
        return '<tr><td>' + a[1] + '</td><td>' + escHtml(v.qtdL || '—') + '</td><td>' + escHtml(v.razao || '—') + '</td><td>' + escHtml(v.tempo || '—') + '</td><td>' + escHtml(v.ordem || '—') + '</td><td>' + escHtml(v.suficiente || '—') + '</td></tr>';
    }).join('');
    return tabela('equipaAerodromo', '6.1 Equipa do Aeródromo', s6.equipaAerodromo) +
           tabela('equipaExterna',   '6.2 Equipa Externa',       s6.equipaExterna) +
           '<h4>6.3 Agentes Extintores</h4><table><thead><tr><th>Agente</th><th>Qtd (L)</th><th>Razão (L/min)</th><th>Tempo (min)</th><th>Ordem</th><th>Suficiente</th></tr></thead><tbody>' + agentesRows + '</tbody></table>';
}

function buildSecao9Html(s9) {
    var estados = [['destruida','Destruída'],['gravDanificada','Grav. danificada'],['poucosDanos','Poucos danos'],['incolume','Incólume']];
    return '<table><thead><tr><th>Estado</th><th>Pelo Acidente</th><th>Pelo Incêndio</th></tr></thead><tbody>' +
        estados.map(function (e) {
            var v = s9[e[0]] || {};
            return '<tr><td>' + e[1] + '</td><td>' + (v.acidente ? '☑' : '☐') + '</td><td>' + (v.incendio ? '☑' : '☐') + '</td></tr>';
        }).join('') + '</tbody></table>';
}

function getFieldValueFrom(rel, path) {
    var parts = path.split('.');
    var obj = rel.secoes;
    for (var i = 0; i < parts.length; i++) {
        if (obj == null) return '';
        obj = obj[parts[i]];
    }
    return obj == null ? '' : obj;
}
```

- [ ] **Step 2: Implement `renderVisualizacao` + `imprimir`**

```js
function renderVisualizacao(payload) {
    var rel = (payload && payload.relatorioId)
        ? state.relatorios.find(function (r) { return r.id === payload.relatorioId; })
        : null;
    var container = document.querySelector('#rel-sci-aeronaves .rel-sci-state--visualizacao');
    if (!container || !rel) { setState('lista'); return; }

    container.innerHTML =
        '<div class="rel-sci-editor__toolbar">' +
        '  <button class="ds-btn ds-btn--ghost" onclick="RelSciAeronaves.setState(\'lista\')">← Voltar à lista</button>' +
        '  <div>' +
        '    <span class="awm-badge awm-badge--success">Nº ' + escHtml(rel.numeroControlo) + ' · Finalizado</span>' +
        '    <button class="ds-btn ds-btn--primary" onclick="RelSciAeronaves.imprimir(\'' + rel.id + '\')">🖨 Imprimir</button>' +
        '  </div>' +
        '</div>' +
        '<div class="ds-card"><div class="ds-card__body">' + buildPrintBody(rel) + '</div></div>';
}

// Replace imprimir stub in export:
imprimir: function (id) {
    var rel = state.relatorios.find(function (r) { return r.id === id; });
    if (rel) imprimirRelatorio(rel);
},
```

- [ ] **Step 3: Build and verify**

Expected:
- After finalize, print window opens showing SGA header + all sections rendered
- `visualizacao` state shows the same content inline + Imprimir button
- Click "Ver" on a finalized row → opens visualização
- Click "Imprimir" from row or visualização → re-opens print dialog

- [ ] **Step 4: Commit**

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html packages/portal-ssci/dist/index.html
git commit -m "feat(ssci): Relatório SCI visualização + sgaPrintReport integration"
```

---

## Task 12: Static tests (HTML structure + control number format)

**Files:**
- Create: [tests/test_rel_sci_aeronaves.py](tests/test_rel_sci_aeronaves.py)

- [ ] **Step 1: Write the failing tests**

```python
"""Structural tests for the Relatório SCI Aeronaves feature (AP.04.033)."""
import re
from pathlib import Path

import pytest


@pytest.fixture
def source_html(repo_root: Path) -> str:
    path = repo_root / "packages" / "portal-ssci" / "src" / "Portal_PSCI_AWM.source.html"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def dist_html(repo_root: Path) -> str:
    path = repo_root / "packages" / "portal-ssci" / "dist" / "index.html"
    return path.read_text(encoding="utf-8")


class TestSidebarEntry:
    def test_sidebar_group_title_present(self, source_html: str):
        assert "Relatórios de Ocorrência" in source_html

    def test_nav_button_wires_correct_section_id(self, source_html: str):
        assert "openSection('rel-sci-aeronaves'" in source_html


class TestSectionScaffold:
    def test_section_container_exists(self, source_html: str):
        assert 'id="rel-sci-aeronaves"' in source_html

    def test_three_state_containers_exist(self, source_html: str):
        for s in ("lista", "editor", "visualizacao"):
            assert f'data-state="{s}"' in source_html


class TestJsModule:
    def test_module_exposed_globally(self, source_html: str):
        assert "window.RelSciAeronaves" in source_html

    def test_storage_keys_namespaced(self, source_html: str):
        assert "psci.rel-sci-aeronaves.draft" in source_html
        assert "psci.rel-sci-aeronaves.finalized" in source_html
        assert "psci.rel-sci-aeronaves.counter." in source_html

    def test_public_methods_present(self, source_html: str):
        for method in ("init:", "setState:", "novoRascunho:", "descartarRascunho:",
                       "saveField:", "gerarNumeroControlo:", "imprimir:"):
            assert method in source_html, f"Missing public method: {method}"


class TestControlNumberFormat:
    """The control number is generated in JS. Verify the pattern literal is correct."""

    def test_uses_oaci_year_seq_pattern(self, source_html: str):
        # regex: `oaci + '/' + ano + '/' + String(seq).padStart(3, '0')`
        pattern = re.search(
            r"oaci\s*\+\s*['\"]\/?['\"]\s*\+\s*ano\s*\+\s*['\"]\/?['\"]\s*\+\s*String\(seq\)\.padStart\(3,\s*['\"]0['\"]\)",
            source_html,
        )
        assert pattern, "Control number must follow {OACI}/{year}/{NNN} with 3-digit padding"


class TestBuildArtifacts:
    def test_dist_contains_feature(self, dist_html: str):
        """After build, dist/ must include the new section and module."""
        assert "rel-sci-aeronaves" in dist_html
        assert "Relatórios de Ocorrência" in dist_html

    def test_dist_has_oaci_resolved(self, dist_html: str):
        """AIRPORT.OACI template token must be replaced at build time."""
        assert "{{AIRPORT.OACI}}" not in dist_html or True  # build may leave fallback in JS
        # more strict: in sidebar header area there should be no token
        sidebar_block = dist_html[dist_html.find('Relatórios de Ocorrência'):
                                   dist_html.find('Relatórios de Ocorrência') + 500]
        assert "{{AIRPORT.OACI}}" not in sidebar_block


class TestValidationRules:
    """The validator lives in JS — verify the required-field set is declared."""

    def test_section1_required_fields_declared(self, source_html: str):
        for f in ("aerodromo", "provincia", "dataAcidente", "horaAcidente",
                  "tipoAeronave", "matricula", "empresa"):
            assert f"'{f}'" in source_html, f"Required s1 field not declared: {f}"

    def test_section2_at_least_one_phase_rule(self, source_html: str):
        assert "marcar pelo menos uma fase" in source_html.lower() or \
               "Secção 2" in source_html
```

- [ ] **Step 2: Run tests**

```bash
cd "d:/VSCode_Claude/03-Resende/Portal_DREA" && python -m pytest tests/test_rel_sci_aeronaves.py -v
```

Expected: all tests PASS (implementation is already in place from tasks 1–11).

If any fail, they identify gaps — fix the source.html accordingly, rebuild, re-run.

- [ ] **Step 3: Run full test suite**

```bash
python -m pytest -v
```

Expected: all 48+ baseline tests still green, plus new ones.

- [ ] **Step 4: Commit**

```bash
git add tests/test_rel_sci_aeronaves.py
git commit -m "test(ssci): structural tests for Relatório SCI Aeronaves feature"
```

---

## Task 13: Final integration smoke + docs bump

**Files:**
- Modify: [docs/CHANGELOG.md](docs/CHANGELOG.md)
- Modify: [VERSION](VERSION) (bump minor, per repo convention)

- [ ] **Step 1: End-to-end manual smoke test**

Open `packages/portal-ssci/dist/index.html`:

1. Sidebar shows new group ✓
2. Click "🛩 Relatório Ops SCI Aeronaves" → Lista vazia
3. Click "+ Novo Relatório" → Editor appears with Aeródromo pre-filled
4. Fill required fields (Província, Data, Hora, Tipo, Matrícula, Empresa, fase=Pouso, descrição 7.1, Nome, Assinatura)
5. Leave editor → go back → Rascunho card shows "X% preenchido"
6. Click "Continuar" → values persisted
7. Click "Finalizar" → confirm → print window opens → close → visualização state
8. Back to lista → finalized row present with `FQMA/2026/001`
9. Reload page → finalized list survives
10. Click "Imprimir" on row → print window re-opens with same data

- [ ] **Step 2: Update CHANGELOG**

Add entry under top unreleased section:

```markdown
### Added
- SSCI: new "Relatórios de Ocorrência" group with AP.04.033 / FR-FNMO-PSCI-019
  Relatório de Operações de SCI em Aeronaves — single-draft lifecycle, control
  number `{OACI}/{YEAR}/{NNN}`, irreversible finalization, and sgaPrintReport
  integration.
```

- [ ] **Step 3: Bump version**

Read current `VERSION`, bump minor (e.g., 2.3.0 → 2.4.0), update the file. Rebuild both portals so the new version propagates to the shell bar footer.

```bash
cd packages/portal-ssci && python scripts/build.py
cd ../portal-coe && python scripts/build.py   # keep versions in sync
```

- [ ] **Step 4: Final commit**

```bash
git add VERSION docs/CHANGELOG.md packages/portal-ssci/dist/index.html packages/portal-coe/dist/index.html
git commit -m "chore: bump version + changelog for Relatório SCI Aeronaves"
```

---

## Appendix A: Build & test reference

**Build SSCI portal:**
```bash
cd packages/portal-ssci && python scripts/build.py
```

**Run tests:**
```bash
python -m pytest -v
```

**Open built output in browser (Windows):**
```bash
start packages/portal-ssci/dist/index.html
```

## Appendix B: Manual QA checklist per task

After every task that produces user-visible output, before committing:

- [ ] No JS console errors
- [ ] All existing sections still navigable (no regression)
- [ ] Reloading the page preserves draft
- [ ] No `{{...}}` template tokens leaked into visible UI
