# Contexto para o Claude Code — Simulacros Emergência & Segurança FNMO

> Instruções para o Claude Code (VS Code) continuar o trabalho sem perder contexto.
> **Primeira coisa a fazer numa sessão nova:** ler este ficheiro por inteiro antes de qualquer edição.

---

## 1. O que é este projecto

Portais HTML standalone (single-file, CSS/JS embutido) para o **Aeroporto Welwitschia Mirabilis (FNMO / Namibe, Angola)**, usados pelo SGSO como suporte operacional durante simulacros e ocorrências reais de:

- **Emergência Aeronáutica** (PEA — Plano de Emergência Aeroportuária)
- **Segurança / Ameaça de Bomba** (PSA / PCA — RESTRITO AVSEC)
- **Salvamento e Combate a Incêndios** (PSCI)

Utilizador principal: **Marcio Sager** — SGSO / Safety Officer do aeroporto.

Identidade visual SGA: `#004C7B` (dark blue), `#0094CF` (mid blue), `#38C7F4` (light cyan), `#c62828` (warning red).

## 2. Ficheiros chave

| Ficheiro | O quê |
|---|---|
| `Portal_COE_AWM.html` | Portal principal do Centro de Operações de Emergência (~3.7 MB, ~12.900 linhas, PDFs em base64 inline) |
| `Portal_PSCI_AWM.html` | Portal do Plano de Salvamento e Combate a Incêndios (~1.5 MB) |
| `Portal_Simulacros_AWM.html` | Página índice |
| `Fichas_Funcao_Emergencia_AWM.docx` | Fichas de função (referência) |
| `Fichas_Funcao_Seguranca_AWM.docx` | Fichas de função RESTRITO AVSEC |
| `Guia_Geral_Simulacro_Emergencia_AWM.docx` | Guia geral do simulacro de emergência |
| `Guia_Geral_Simulacro_Seguranca_AWM.docx` | Guia geral do simulacro de segurança |
| `PPT_Briefing_Emergencia_AWM.pptx` | Briefing em PowerPoint |
| `AUDITORIA_PORTAL_COE.md` | Notas de auditoria anteriores |

## 3. Convenções do projecto (IMPORTANTE — seguir sempre)

### 3.1 Edição aditiva, não invasiva
Quando possível, **patches novos vão em blocos CSS+JS injectados antes de `</body>`**, marcados com comentários tipo `<!-- ===== PATCH vN ===== -->`. Não reescrever secções antigas se der para aumentar por cima — isto preserva referências dispersas e evita regressões.

### 3.2 Diálogos nativos **proibidos** — usar wrappers
- Em vez de `confirm(msg)` → `await window.awmConfirm(msg, { title, variant: 'warning'|'danger', okText, cancelText })`
- Em vez de `alert(msg)` → `window.awmAlert(msg, 'ok'|'warning'|'err')`
- Call-sites com `awmConfirm` têm de ser `async` e usar `await`.
- Estes wrappers já existem em ambos os portais, injectados antes do `</body>`.

### 3.3 Validação obrigatória após edições grandes
Depois de qualquer mudança significativa em `Portal_COE_AWM.html` ou `Portal_PSCI_AWM.html`, validar a sintaxe de todos os `<script>` inline. Script Python de referência:

```python
import re, subprocess, tempfile, os
with open('Portal_COE_AWM.html','r',encoding='utf-8') as f:
    html = f.read()
pattern = re.compile(r'<script(?![^>]*\ssrc=)[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
blocks = pattern.findall(html)
errors = 0
for i, block in enumerate(blocks, 1):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf:
        tf.write(block); tmp = tf.name
    r = subprocess.run(['node','--check',tmp], capture_output=True, text=True)
    if r.returncode != 0:
        errors += 1; print(f'Block #{i}:', r.stderr[:500])
    os.unlink(tmp)
print(f'{len(blocks)} blocks, {errors} errors')
```

O COE deve ter **18 blocks, 0 errors** (era 9 antes do PATCH v7; v7 → 10; v8/v9/v10 → 13; v13 → 14; v14 → 15; v15 → 16; v17 → 17; v18 → 18; v19 substitui v18 in-place, não adiciona block). O PSCI deve ter **7 blocks, 0 errors**. Nota: PATCH v5 (PSCI), PATCH v11 (COE) e PATCH v12 (COE) são style-only. PATCH v13/v14/v15/v17 adicionam 1 script block cada. PATCH v18 foi substituído pelo v19 (mesmo block, novo conteúdo). PATCH v16 é monkey-patch in-place do script v7.

> Nota: o Block #1 do COE contém o script principal. Se for validado com extensão `.mjs` (strict mode) dá falso positivo por redeclaração de `formatElapsed` — é um padrão legado do ficheiro. Usar SEMPRE extensão `.js` no tempfile para manter coerência com a validação anterior.

### 3.4 Ficheiros grandes
Os portais têm PDFs codificados em base64 (`DOC_PDF_B64`, ~MB cada). Não usar `cat`, `sed` ou `grep -A/B` sem `head_limit` nestes ficheiros — vais encher o terminal. Usar `Read` com `offset`/`limit` ou `Grep` com ranges específicos.

## 4. Histórico do que já foi feito (sessões anteriores)

### 4.1 Migração de diálogos nativos → wrappers brandizados
Todos os `confirm()` e `alert()` de ambos os portais foram convertidos para `awmConfirm` / `awmAlert`. Pontos-chave já migrados:

- **COE**: `limparFichaGeral`, `cfgDelRow`, `cfgImportJSON`, `cfgResetDefaults`, `window.ufClear` (confirms); mais 13 sites de alert (gravação, export, PDF viewer errors, popup blocker, etc.)
- **PSCI**: `psciCfgDel`, `psciCfgPersist`, `psciCfgSaveAll`, `psciCfgImportJSON`, `psciCfgReset`, `stkSaveAll`, `stkImportJSON`, `stkReset`

### 4.2 Save badge "Guardado" auto-hide
O `.uxp-savebadge` estava a ficar fixo no ecrã. Solução: classe `.visible` + transição opacity/transform + `saveBadgeHideTimer` com `setTimeout(..., 2800)` que remove a classe. Aplicado em ambos os portais.

### 4.3 Card MOA na secção Documentação Técnica (COE)
Adicionado 5.º card **MOA — Manual de Operações do Aeródromo** ao lado de PEA, PCA, PSA, PSCI. Borda superior `#6c3483` (roxo). Usa picker (`<input type="file">` oculto + botão) porque não temos PDF embutido. Entry `moa` adicionada ao `DOC_TITLES`. Banner informativo e Guia Rápido actualizados.

### 4.4 Unificação do formulário de Emergência Aeronáutica (COE)
**Problema**: havia duplicação visual — o `realOccurrenceFields > .info-card` mostrava o formulário legado (Nº Ocorrência, Nº Voo, POB, etc.) **E** o bloco EFB `#emgFormBlock` era injectado no mesmo card, com fields sobrepostos.

**Solução**:
1. CSS esconde o h3 e todos os divs directos do info-card no modo `mode-emergencia`, excepto `#emgFormBlock`:
   ```css
   #realOccurrenceFields.mode-emergencia > .info-card > h3,
   #realOccurrenceFields.mode-emergencia > .info-card > div:not(#emgFormBlock):not(#bombaFormBlock) {
       display: none !important;
   }
   ```
2. Adicionada nova secção **"Identificação da Ocorrência e Aeronave"** no topo do EFB com: Nº Ocorrência (readonly), Hora Notificação, Nº Voo/Matrícula, Tipo Aeronave, Companhia Aérea, Combustível (min + litros), Carga Perigosa + tipo DG opcional.
3. **`bindLegacyMirror(newId, oldId)`** copia valores dos novos inputs EFB para os inputs legados (`realOccFlight`, `realOccAcType`, etc.) que continuam no DOM ocultos. Isto preserva `_snapshotToOcc()`, autosave debounced (`_debouncedSave` em `realOccFieldIds`), CSV export e PDF export sem alterações.

### 4.5 Bug dos chips de Natureza Específica (COE)
**Causa**: `<label class="efb-chip"><input type="checkbox">...</label>` — clicar no label accionava o toggle nativo do browser, e depois o handler JS fazia `cb.checked = !cb.checked` que cancelava o toggle.

**Fix**: elemento passou a `<span class="efb-chip" role="button" tabindex="0" aria-pressed="false">`, com `ev.preventDefault()` no click handler e suporte a `Space`/`Enter`. Visual melhorado (checkmark `✓` no estado activo, hover vermelho claro, sombra).

### 4.7 PATCH v8 / v3 — escHtml helper + awm-modal focus trap / a11y (COE + PSCI — MIRROR)
**Aditivo, zero edições destrutivas**. Injectado antes de `</body>` em ambos os portais com marker "UXP MIRROR LAYER" explicando que o código é idêntico nos dois ficheiros (há que sincronizar manualmente).

1. **`window.escHtml(s)`** — helper global que escapa `& < > " '`. Guard `if (typeof !== 'function')` para ser idempotente. Disponível para novos sites de `innerHTML`; adopção progressiva — não toca nos 66+37 sites existentes.
2. **Focus trap nos modais** via listener global de `keydown` em capture phase. Só intercepta `Tab`/`Shift+Tab` quando `.awm-modal-overlay` está visível (reconhece tanto `.awm-modal-closing` do COE como `.leaving` do PSCI). Ciclo de foco dentro do modal; se o foco escapar programaticamente, é empurrado de volta.
3. **Restauração de foco** via `MutationObserver` em `document.body` — guarda `document.activeElement` ao inserir `.awm-modal-overlay`, restaura ao remover o último.
4. **`aria-labelledby` / `aria-describedby` automáticos** ligando `.awm-modal-title` e `.awm-modal-body`/`.awm-modal-message` ao `.awm-modal` com ids auto-gerados.

Trabalha com `confirmModal`/`alertModal` do COE e `makeModal` do PSCI sem modificar a lógica existente.

### 4.8 PATCH v9 / v4 — lsGet/lsSet wrapper + section a11y (COE + PSCI — MIRROR)
**Aditivo**. Mesmo padrão mirror-layer.

1. **`window.lsGet(key, def)` / `window.lsSet(key, data)` / `window.lsRemove(key)`** — wrapper `localStorage` com schema versionado (`{__v:1, ts, data}`) e quota guard. Em `QuotaExceededError` notifica via `awmAlert`. **Adopção progressiva**: não toca nos 22+11 call-sites directos de `localStorage` existentes; futuros sites devem usar o wrapper.
2. **Section change announcer** — cria div visually-hidden com `aria-live="polite"`/`aria-atomic="true"`. Um `MutationObserver` observa todas as `.section` para mudanças de classe; quando uma ganha `.active`, anuncia o heading (`h2, h1.page-title, h1`).
3. **Focus no heading** da secção activa a partir da segunda mudança (evita disrupção no load inicial). Usa `tabindex="-1"` se necessário, `preventScroll: false` para levar o conteúdo para vista.

### 4.9 PATCH v10 — PDF base64 lazy populate (COE only)
**Parcialmente invasivo** — necessário mover ~1.71 MB de dados. Aplicado via script Python com temp file + atomic replace porque o Edit tool não consegue manipular blocos multi-MB.

**Mudança**: o literal `var DOC_PDF_B64 = { pea: '...', psci: '...' };` no script block central (linha ~10643) foi substituído por um stub `var DOC_PDF_B64 = {}; // [PATCH v10]`, e a data real foi movida para um novo IIFE antes de `</body>` que faz `window.DOC_PDF_B64 = {...}`.

**Razão**: o HTML parser pode agora renderizar todas as secções UI (dashboard, contactos, fichas, etc.) ANTES de processar o literal de 1.71 MB. Reduz tempo até First Paint. `docViewInline()` continua a ler `DOC_PDF_B64[kind]` — por altura do clique do user, o PATCH v10 já executou.

Funções `docViewInline`, `docViewerClose`, `docViewerDownload`, `docOpenLocal`, `DOC_BLOB_CACHE`, `DOC_CURRENT_KIND` **inalteradas**.

### 4.10 PATCH v11 / v5 — Print safety CSS rede (COE + PSCI — MIRROR)
**Aditivo, defensivo**. Um bloco `<style>` com `@media print` que só ADICIONA hides globais para UI chrome:
- `.uxp-savebadge`, `.uxp-toasts`, `.uxp-toast`, `.uxp-totop`, `.uxp-skip`
- `.awm-modal-overlay`, `#awm-section-announcer`, `.no-print`
- `body { background: #ffffff !important; }` como fallback

**Não toca** nos 27 `@media print` existentes das fichas/cartões — apenas rede de segurança global.

### 4.11 Rename `openSec` → `openSection` (PSCI)
22 ocorrências renomeadas em 2 passagens (primeiro `window.openSec` → `window.openSection`, depois `openSec(` → `openSection(`). Motivo: consistência de nomes entre COE e PSCI — ambos os portais têm agora `openSection()` como handler de navegação.

### 4.12 Console.log cleanup mínimo
Removidos os 2 logs puros de status (`[UXP v6] Initialised` no COE, `[UXP-PSCI v2] Initialised` no PSCI). Todos os outros `console.error` / `console.warn` estão dentro de `catch` blocks e foram **mantidos** como diagnóstico legítimo.

### 4.17 PATCH v19 — Editor unificado editável + remoção dos tabs clássicos (Fix B final)

**Motivação**: o editor read-only do PATCH v18 causava confusão porque o tab "Contactos (Unificado)" mostrava 26 contactos, mas os tabs clássicos "Contactos Internos" (9 linhas com 4 vazias) e "Contactos Externos" (6 linhas) eram o único sítio editável — e não tinham tabs para ENNA/Segurança-Ordem/Operadores (11 contactos órfãos). O utilizador notou que editar um contacto no clássico só funcionava se ele tivesse "slot" (ex: Director 01), e os contactos restantes eram read-only de facto.

**Decisão**: promover o editor unificado a fonte única editável e **remover** os tabs "Contactos Internos" + "Contactos Externos". O tab "Operadores COE" **fica** porque tem lógica específica de login (populá-lo com os 26 contactos não faz sentido — só operadores do COE devem aparecer no login).

**Decisões operacionais** (registadas no brainstorming):
- **1a)** Tab Operadores COE mantido separado (não fundir no unificado).
- **2a)** Full overlay — cada edição grava o array inteiro em `CURRENT_CFG.contactos` (novo campo v19). Simples, robusto, fácil de debugar.
- **Pergunta 2 → A**: tab "Contactos" é o **default** quando abres Configurações.
- **Pergunta 3 → B**: botão **"💾 Guardar Alterações"** explícito (não auto-save).

**Mudanças concretas**:

1. **PATCH v14 estendido** — `applyOverlay()` ganha nova prioridade:
   - **Priority 1**: `cfg.contactos` (array completo) se existir → merge com defaults por `id`, e **adiciona** contactos novos que não existam nos defaults.
   - **Priority 2** (legacy): `cfg.contactosInternos` / `cfg.contactosExternos` (tabs clássicos) → compatibilidade para dados antigos de utilizadores que ainda não gravaram via v19.
   - Novo helper `saveUnified(contactsArray)` — persiste o array completo em `CURRENT_CFG.contactos` e chama `cfgPersist()`. Exposto via `window.awmContacts.saveUnified`.
   - `_version` bump de 14 → 19.

2. **HTML Configurações**:
   - Sub-tabs reduzidos de 6 para 4: `📇 Contactos` (novo default, era `📇 Contactos (Unificado)`), `🏢 Dados Aeroporto`, `👤 Operadores COE`, `⚙ Parâmetros`.
   - Tab buttons "Contactos Internos" e "Contactos Externos" **removidos**.
   - Tab contents `cfg-tab-int` e `cfg-tab-ext` **removidos** (substituídos por comentário HTML explicativo).
   - `cfg-tab-aeroporto` muda de `display:block` para `display:none`.
   - `cfg-tab-unified` muda de `display:none` para `display:block` (default).
   - Header do tab atualizado: "📇 Contactos" (não mais "Unificado" — é o único agora), texto explicativo muda para "Fonte única de todos os contactos do portal...", botões novos `+ Adicionar` e `💾 Guardar Alterações`.
   - Tabela ganha coluna "Acção" no fim (botão ✕ vermelho por linha).

3. **PATCH v19 JS** substitui PATCH v18 inteiro (mesma localização, antes de `</body>`):
   - `workingSet` — snapshot local do array de contactos que o utilizador está a editar. Só é persistido ao clicar Guardar.
   - `renderTable()` agora gera **inputs editáveis** em cada célula (`<input data-fld="FIELD">`) em vez de texto estático. A célula da categoria usa `<select>` com opções do `getCategories()`.
   - `collectFromDOM()` — lê todos os inputs e actualiza `workingSet` (chamado antes de filter/search/add/save).
   - `handleAdd()` — adiciona linha nova com ID auto-gerado (primeiro ID livre `01`, `02`, ...).
   - `handleSave()` — chama `collectFromDOM()` + `awmContacts.saveUnified(workingSet)` + re-render de todos os consumidores (`awmContactsRender`, `awmContactsRenderAll`) + toast "✓ Contactos guardados".
   - Botão `✕` por linha pede confirmação via `awmConfirm` e apenas remove do `workingSet` local — não persiste até o utilizador clicar Guardar.
   - Filter + search mantêm o workingSet intacto (chamam `collectFromDOM()` antes de re-renderizar para preservar edições em progresso).

4. **`cfgSaveAll()` defensivo** — a função global de guardar configurações é chamada pelos botões de topo (Guardar, Exportar, etc.). Antes, fazia `CURRENT_CFG.contactosInternos = cfgCollectTable('int')` sem guard, o que poderia sobrescrever dados com array vazio agora que os tbody já não existem. Fix: envolve as 3 linhas em `if (document.querySelector('#cfg-tbl-int tbody')) { ... }` — só colecta se o tbody existir.

**Funções legadas inertes** (mantidas mas não invocadas):
- `cfgRenderTable('int')` / `('ext')` — guard `if (!tbody) return` já existe, não crasha.
- `cfgCollectTable('int')` / `('ext')` — devolve `[]` se tbody não existir.
- `cfgAddRow('int')` / `('ext')` — nunca mais é chamado porque não há botões que a invoquem.
- `cfgDelRow('int')` / `('ext')` — idem.
- Removi as chamadas problemáticas em `cfgSaveAll` mas **não apaguei as funções** — ficam como dead code protegido por guards caso algum ficheiro JSON importado ainda tenha os campos antigos (`contactosInternos`/`contactosExternos`).

**Compatibilidade regressiva**:
- Utilizadores que tinham dados gravados na versão v14–v18 (schema com `contactosInternos`/`contactosExternos` editados pelos tabs clássicos) continuam a ver esses dados no editor unificado via Priority 2 do overlay.
- Ao **Guardar** no editor unificado, as edições passam a ser gravadas em `cfg.contactos` (Priority 1) — a partir desse momento, as entradas legacy em `contactosInternos`/`contactosExternos` são **ignoradas**.
- Import JSON de ficheiros antigos continua a funcionar (lê campos legacy).
- Export JSON agora inclui `cfg.contactos` (campo novo) além dos campos legacy.

**Validação**: 18 blocks / 0 errors (mesmo count que v18 — não adicionou novo script block, apenas substituiu o conteúdo do bloco existente).

**Onde olhar**:
- Schema v19: `AWM_CONTACTS_DEFAULT` no PATCH v14 (inalterado) + `applyOverlay()` agora com Priority 1.
- Sub-tabs: [Portal_COE_AWM.html:8366](Portal_COE_AWM.html#L8366) (4 tabs agora, em vez de 6).
- Tab unificado editável: procurar `cfg-tab-unified` ou `awm-unified-save`.
- Script v19: procurar `PATCH v19` antes de `</body>`.
- Guards `cfgSaveAll`: procurar `PATCH v19: os tbody 'int' e 'ext' já não existem`.

### 4.16 PATCH v17 / v18 — Fix B completo (cr-chips, fluxogramas, editor unificado)

Continuação directa de §4.15 (PATCH v14/v15/v16). Esta sessão concluiu os itens que ficaram como DEFERRED em §5.2:

#### PATCH v17 — Renderizador de data-awm-contact (B2.2 + B2.3)

**Edições HTML** — substitui os sites hard-coded por marcadores declarativos:

1. **Fluxogramas** (20 ocorrências, secção `#fluxogramas`):
   - Pattern antigo: `<div class="flow-node ...">LABEL<span class="flow-phone">TELEFONE HARD-CODED</span></div>`
   - Pattern novo: `<div class="flow-node ..." data-awm-contact="ID" data-awm-format="FMT">LABEL<span class="flow-phone"></span></div>`
   - A `flow-phone` span fica **vazia** — é populada pelo renderer.
   - Formatos usados: `full`, `cel-cisco`, `cel`, `cel-cel2`, `cisco-quente`, `quente`, `quente-name-cel`, `name-cel-cisco`.

2. **cr-chips** (64 ocorrências efectivas, ~13 padrões únicos, secções `#cronometro` e secções narrativas):
   - Pattern antigo: `<span class="cr-chip"><b>LABEL</b> NOME <span class="cr-tel">TELEFONE HARD-CODED</span></span>`
   - Pattern novo: `<span class="cr-chip" data-awm-contact="ID" data-awm-label="LABEL" data-awm-format="FMT"></span>`
   - Atributos opcionais adicionais: `data-awm-name` (override do nome, usado para "Hosp. Ngola Kimbanda", "Catraio Luís (RAC)", "PNA — Jaime de Brito" no chip EOD).
   - Formatos usados: `chip-full`, `chip-cisco-cel`, `chip-cel`.

**Script PATCH v17** (~160 linhas, injectado antes de `</body>`):
- `formatContact(c, fmt)` — função pura que retorna a string formatada para cada formato suportado (8 variantes para flow-nodes + 3 para chips + `short` default).
- `renderFlowNodes()` — varre `.flow-node[data-awm-contact]`, obtém o contacto via `window.awmContacts.getById()`, popula o `.flow-phone` interno.
- `renderCrChips()` — varre `.cr-chip[data-awm-contact]`, suporta `data-awm-label`/`data-awm-name`/`data-awm-format` overrides, substitui `innerHTML` com `<b>label</b> nome <span class="cr-tel">formatted</span>`.
- `renderAll()` exposto como `window.awmContactsRenderAll` — chamado no init + pelos MutationObservers em `#fluxogramas` e `#fichas-seg` (re-render quando a secção fica `.active`).
- Fallback gracioso: se `window.awmContacts` não estiver disponível, os chips ficam vazios mas o portal não crasha.

**Resultado**: todos os telefones nos fluxogramas e cr-chips passam a ler do schema unificado. Edita o Director em Configurações → actualiza em todos os chips + fluxogramas sem refresh.

#### PATCH v18 — Editor unificado (B3)

**Novo tab** "📇 Contactos (Unificado)" adicionado à barra de tabs de Configurações, posicionado **entre "🏢 Dados Aeroporto" e "📞 Contactos Internos"**. Os 3 tabs antigos (Internos/Externos/Operadores) **permanecem funcionais** — foi decisão explícita não os substituir para preservar a lógica de add/remove/persist já testada.

**Componente** (~100 linhas de HTML + ~140 linhas de JS):
- `<div id="cfg-tab-unified">` com cartão contendo:
  - Descrição breve ("read-only por agora" — edições continuam nos tabs clássicos)
  - `<input type="text" id="awm-unified-search">` — pesquisa case-insensitive em `id`, `legacyId`, `label`, `nome`, `funcao`, `cisco`, `cel`, `cel2`, `quente`, `email`.
  - `<select id="awm-unified-filter-cat">` — populado dinamicamente via `window.awmContacts.getCategories()`.
  - Contador de resultados `#awm-unified-stats`.
  - `<table id="cfg-tbl-unified">` com 10 colunas (ID, Categoria, Entidade, Nome, Função, CISCO, Cel, Cel 2, Quente, Email).

**JS PATCH v18**:
- `populateCategoryFilter()` — injecta as 5 categorias do schema como `<option>` (idempotente).
- `renderTable()` — aplica filtros e regenera `<tbody>`. Categoria longa é truncada a 32 chars para caber.
- `wireHandlers()` — liga `input` (debounced implicitamente pelo browser) e `change` do filtro a `renderTable()`. Marcada via `dataset.awmWired` para idempotência.
- `watchTabVisibility()` — `MutationObserver` em `#cfg-tab-unified` detecta mudança de `style.display` e re-renderiza quando fica visível (útil se o utilizador edita noutro tab e volta a este).

**Read-only por design**: esta primeira iteração do editor unificado **não permite edição inline**. Os tabs clássicos (Internos/Externos/Operadores) continuam a ser o caminho para modificar contactos; as edições propagam-se automaticamente ao schema via overlay do PATCH v14. Se no futuro quiseres editor unificado com inputs editáveis + add/remove, é extensão natural do v18 mas requer:
- Lidar com schema heterogéneo (sga-interna tem `funcao`, externa-emg tem `contacto`, etc.)
- Invalidar/re-merge com overlay quando o utilizador guarda.

**Onde olhar**:
- Tab button: [Portal_COE_AWM.html:8368](Portal_COE_AWM.html#L8368).
- Tab content: procurar `cfg-tab-unified` no HTML.
- Script: procurar `PATCH v18` antes de `</body>`.
- Schema source: `AWM_CONTACTS_DEFAULT` dentro do PATCH v14.

### 4.15 PATCH v14 / v15 / v16 — Schema unificado de contactos (COE — fundação B1 + B2 parcial)

**Motivação**: o Portal COE tinha **4 fontes duplicadas** para os mesmos contactos, não sincronizadas entre si. O editor em Configurações → Contactos Externos mostrava apenas 3 telefones simbólicos (115/113/112) enquanto o `VERIF_ENTIDADES` (PATCH v7), a secção `contactos` hard-coded e os `cr-chips` espalhados tinham os **26 contactos reais com nomes + telefones**. Editar no editor não tinha efeito em lado nenhum.

**Objectivo acordado**: Fix B — unificar as fontes numa única "source of truth". O utilizador aprovou executar "tudo sem checkpoints". Para gerir o risco sem quebrar o portal, o trabalho foi dividido em 3 patches com scope progressivo:

#### PATCH v14 — Fundação do schema unificado (invisível)
- Novo array `AWM_CONTACTS_DEFAULT` com **26 entradas normalizadas** consolidadas de 3 fontes: `VERIF_ENTIDADES` (fonte mais completa) + secção `contactos` hard-coded (emails + funções) + `DEFAULT_CFG.contactosInternos` (edições do utilizador).
- Schema por entrada: `{ id, legacyId, cat, label, nome, funcao, cisco, cel, cel2, quente, email, tags }`. `legacyId` preserva os IDs originais (ex: `01E`, `17-18`) para rastreabilidade; `tags` permite pesquisa cruzada por função (ex: `chefia`, `eod`, `bombeiros`).
- **5 categorias** normalizadas: `sga-interna` (7), `enna` (3), `seg-ordem` (5), `externa-emg` (8), `operadores` (3).
- **Overlay system**: edições guardadas em `CURRENT_CFG.contactosInternos` / `contactosExternos` (pelo editor antigo de Configurações) **tomam precedência** sobre os defaults, via função `applyOverlay()` que faz match por `num` ↔ `id`. O editor antigo continua 100% funcional e as suas edições propagam-se automaticamente ao schema unificado.
- **Backup automático**: primeira execução do v14 guarda o payload antigo de `localStorage["coe_awm_config"]` em `localStorage["coe_awm_config_backup_pre_v14"]` com timestamp. Rede de segurança caso algo corra mal.
- **API pública exposta** em `window.awmContacts`:
  - `getAll()` — 26 entradas com overlay aplicado
  - `getById(id)` — aceita id novo ou legacyId
  - `getByCategory(cat)` — filtra por key de categoria
  - `getByTag(tag)` — filtra por tag (útil para cr-chips)
  - `getCategories()` — lista das 5 categorias
  - `getCategoryLabel(key)` — display label
  - `formatShort(contact)` — string formatada tipo "CISCO 1946 | 935 645 456" para uso em chips
- **Não toca em nada visível**. Injectado antes de `</body>`, apenas estabelece a infra-estrutura.

#### PATCH v15 — Renderização dinâmica da secção `contactos` (B2.1)
- **Edição directa** da secção `contactos` ([Portal_COE_AWM.html:5589](Portal_COE_AWM.html#L5589)): as ~230 linhas de `<div class="contact-card">` hard-coded foram substituídas por um único container `<div id="awm-contactos-dynamic-root">` + a tabela "LINHAS DIRECTAS — CISCO INTERNOS" (mantida estática porque é metadata do sistema, não contactos).
- **Script de renderização** `window.awmContactsRender()` injectado via PATCH v15: lê `window.awmContacts.getAll()`, agrupa por categoria via `getCategories()` + `getByCategory()`, e gera os cards com classes CSS idênticas às do original (`.contact-card`, `.contact-card-header` com variants `internal`/`authority`/`external`, `.contact-field`). **Visual idêntico ao original** — única diferença é que agora vem do schema.
- **MutationObserver** em `#contactos` re-renderiza quando a secção ganha `.active` — garante que se o utilizador editar contactos em Configurações, abrir Contactos mostra valores actualizados sem refresh da página.
- Botão novo "🔄 Actualizar" no topo da secção — chama `awmContactsRender()` explicitamente.
- **Validação visível**: editar um contacto no editor de Configurações → abrir a secção Contactos → ver a mudança reflectida. O overlay do PATCH v14 garante sincronização.

#### PATCH v16 — Sincronização de `VERIF_ENTIDADES` (B2.4)
- **Edição in-place** no script do PATCH v7 (linha ~12978): adicionada a função `syncVerifEntidadesFromSchema()` no topo do `init()`.
- A função verifica se `window.awmContacts` está disponível e, se sim, **sobrescreve o array `VERIF_ENTIDADES`** (`.length = 0` + push loop) com os dados do schema unificado, mapeando o formato v14 (`{id, legacyId, cat, label, nome, cisco, cel, cel2, quente}`) para o formato esperado pelo verif-contactos (`{id, cat (display label), label, nome, cisco, cel}`).
- Formatações específicas preservadas: `cisco/quente` combinados como `"48/38"`, dois celulares combinados como `"933 439 480 / 923 622 001"`.
- O literal `VERIF_ENTIDADES = [ ... ]` original fica como **fallback** — se `window.awmContacts` não estiver disponível por qualquer razão, a Verificação Mensal continua a funcionar com os dados hard-coded.
- **Resultado**: editar um contacto em Configurações → Verificação Mensal mostra o contacto editado na próxima abertura da secção.

#### O que ficou DEFERRED (ver §5.2)
Estes dois itens constavam do plano Fix B original mas foram **adiados por razões de risco**. Num único ciclo "sem checkpoints", o volume de alterações pontuais nos 50+15 sites aumentaria exponencialmente o risco de regressão visual sem possibilidade de testes intermédios:

- **B2.2** — cr-chips nas ~50 fichas (FICHA-SEC-01 AVSEC, FICHA-SEC-02 COE, etc., todo o narrative text das fichas). Cada chip tem contexto ligeiramente diferente (entidade + nome + CISCO ou celular ou ambos) e a migração tem de ser cirúrgica site-a-site.
- **B2.3** — fluxogramas com ~15 `flow-node` + `flow-phone` hard-coded.
- **B3** — novo editor de Configurações com tabela unificada filtrável (o editor antigo com 3 tabs separados continua funcional, só é menos ergonómico).

**Onde olhar**:
- Schema: [Portal_COE_AWM.html](Portal_COE_AWM.html) — procurar `AWM_CONTACTS_DEFAULT` antes de `</body>`.
- Helpers: `window.awmContacts.*` (exposto globalmente).
- Secção contactos nova: [Portal_COE_AWM.html:5589](Portal_COE_AWM.html#L5589) (container `#awm-contactos-dynamic-root`).
- Renderer: procurar `PATCH v15` antes de `</body>`.
- Sync VERIF_ENTIDADES: procurar `syncVerifEntidadesFromSchema` dentro do script do PATCH v7.
- Backup da config antiga: `localStorage["coe_awm_config_backup_pre_v14"]`.

### 4.14 PATCH v13 — Re-foco OCORRÊNCIAS (COE — mudança estrutural grande)
**Mudança estrutural invasiva** — edição directa de HTML em 3 secções + injecção de 1 bloco CSS/JS novo. Motivação: o utilizador concluiu que os guias focados em *simulacro* (cenário, triagem START, 12 critérios de avaliação, avaliação por entidade) não serviam o propósito real do Portal COE, que é **Centro de Operações de Emergência** — ferramenta operacional para ocorrências reais, não para preparar exercícios.

**Decisões no brainstorming** (registadas aqui para referência em futuras sessões):
- **D)** Substituir o grupo SIMULACROS inteiro por OCORRÊNCIAS com conteúdo 100% operacional.
- **A (conteúdo simulacro antigo)**: eliminar. Quem quer preparar simulacros usa os `.docx` na pasta do projecto.
- **D (estrutura dos guias)**: híbrido — cartão de acção imediata + 4 fases estruturadas.
- **A (fichas operacionais)**: substituir `fichas-emg` por um dashboard que aponta para o EFB existente em `cronometro`, sem duplicar o formulário.

**O que mudou concretamente**:

1. **Sidebar** — `<h3>Simulacros</h3>` → `<h3>Ocorrências</h3>` em [Portal_COE_AWM.html:1776](Portal_COE_AWM.html#L1776). Labels dos 4 itens mantidos (Emergência Guia/Fichas, Segurança Guia/Fichas) — **paridade visual absoluta** (decisão A2 na sub-pergunta de labels).

2. **`guia-emg` inteiramente reescrito** (~156 linhas eliminadas, ~170 linhas novas):
   - **Cartão de Acção Imediata vermelho** no topo com 3 botões: Cronómetro / Formulário EFB / Contactos TWR, e um quadro de 3 níveis (Alerta Local / Alerta Completo / Acidente).
   - **4 cards `<details>` accordion** numerados: Fase 1 — Notificação & Avaliação (0–2 min), Fase 2 — Activação & Coordenação (2–10 min), Fase 3 — Resposta no Local (10 min – resolução), Fase 4 — Encerramento & Registo.
   - **Card de Referências rápidas** com 4 botões: Mapas Quadrícula, Contactos, PEA/PCA/PSA/MOA, Verificação Mensal.
   - **Eliminado**: enquadramento legal + referências normativas, cenário EX-FNMO-PEA-001, triagem START tabela, zonas operacionais tabela, 12 critérios de avaliação.

3. **`guia-seg` inteiramente reescrito** (~579 linhas eliminadas, ~200 linhas novas):
   - **Banner RESTRITO AVSEC** no topo.
   - **Cartão de Acção Imediata âmbar** com 3 botões: Cronómetro / Fichas AVSEC / Contactos PNA/AVSEC, e aviso em destaque sobre comunicação em código ("nunca dizer 'bomba' em canal aberto").
   - **4 cards accordion**: Fase 1 — Recepção da Ameaça (FRM-FNMO-AB-001 com as 10 perguntas), Fase 2 — Activação do Protocolo, Fase 3 — Busca & Gestão (objecto suspeito → raio 100 m, telemóveis/rádios a ≥25 m), Fase 4 — Resolução & Registo.
   - **Referências rápidas**: Fichas AVSEC, Contactos AVSEC/PNA, PSA/PEA, Verificação Mensal.
   - **Eliminado**: enquadramento doutrinário longo, descrições estendidas de cada nível.

4. **`fichas-emg` transformado em DASHBOARD** (~432 linhas eliminadas, ~60 linhas novas):
   - Novo título: "FORMULÁRIO OPERACIONAL — EMERGÊNCIA AERONÁUTICA".
   - **Card 1 — Ocorrência Activa**: `#occDashActiveCard` com snapshot estático (decisão B2) dos campos EFB principais (Nº Ocorrência, Nº Voo, Tipo Aeronave, Companhia, Declaração Piloto, Nível, Hora TWR, RWY, POB). Botão grande **"📋 Abrir Formulário Operacional (EFB)"** chama `occDashOpenEFB()` → `openSection('cronometro', null)` + auto-scroll suave para `#emgFormBlock`. Botão **"🔄 Actualizar Snapshot"** chama `occDashRefresh()`.
   - **Card 2 — Histórico de Ocorrências**: `#occDashHistory` lista até 10 ocorrências mais recentes de `localStorage["coe_awm_occurrences"]` (a mesma chave usada por `saveOccurrence`/`getOccurrences` em [Portal_COE_AWM.html:3748](Portal_COE_AWM.html#L3748)). Cada item mostra Nº Ocorrência (monospace), Nº Voo + Tipo Aeronave, data/hora formatada pt-PT, badge colorido para a declaração (MAYDAY vermelho / PAN-PAN laranja / SQUAWK roxo), e botão "📂 Abrir" que chama `loadOccurrence()` se disponível.
   - **Card 3 — Ferramentas**: botões para exportar PDF da actual (redirige para o cronómetro), exportar todas em CSV (gera ficheiro directamente, com BOM UTF-8), e limpar ocorrência activa (com `awmConfirm` danger, limpa campos EFB + inputs legados + chips + botões de declaração).
   - **Eliminado**: Partes 1/2/3/... do formulário de exercício (dados gerais, tabela de avaliação por entidade, avaliação global). As funções JS legadas (`exportFichaGeralCSV`, `exportFichaGeralPDF`, `limparFichaGeral`) **continuam a existir** nos script blocks mas ficam **inertes** — todos os `document.getElementById('fg-*')` retornam null, protegidos por guards `if (el)`. Zero risco de crash.

5. **PATCH v13 CSS + JS** (injectado antes de `</body>`, depois de PATCH v12):
   - **CSS** (~420 linhas): vocabulário de classes `occ-*` para todos os novos componentes:
     - `.occ-action-card` (+ variants `-emg` vermelho, `-seg` âmbar) com header ícone/título/sub, grid de botões, quadro de níveis coloridos (verde/laranja/vermelho para níveis 1/2/3).
     - `.occ-phase` usando `<details>` HTML5 nativo com header custom (número circular, título, badge de tempo), body com `.occ-phase-h4` / `.occ-phase-p` / `.occ-list` / `.occ-phase-hint`.
     - `.occ-refs` + `.occ-ref-card` para os cards de referência rápida (flex column, ícone grande, label bold, hint pequeno).
     - `.occ-dash-*` completo para o dashboard fichas-emg (card, head, preview grid, actions, history items com badges).
     - Responsive `@media (max-width: 720px)` e print `@media print` (esconde botões, evita quebras de página em cards accordion abertos).
   - **JS** (~240 linhas, IIFE strict): `readOccurrences()`, `readActiveEFB()` (tenta campos `efb-*` primeiro, fallback para `realOcc*` legados), `renderActivePreview()`, `renderHistory()`, e os handlers expostos `occDashOpenEFB`, `occDashRefresh`, `occDashExportActivePDF`, `occDashExportAllCSV`, `occDashClearActive`. Um `MutationObserver` em `#fichas-emg` re-renderiza o snapshot sempre que a secção ganha `.active` — garante que ao abrir o dashboard o utilizador vê dados frescos.

6. **Cross-link card em `ajuda`** — texto actualizado para mencionar "fluxo operacional de ocorrências" em vez de apenas "estrutura do portal".

**Validação**: COE 14 blocks / 0 errors. PSCI inalterado a 7/0.

**Onde olhar se algo mudar**:
- Sidebar grupo Ocorrências: [Portal_COE_AWM.html:1775](Portal_COE_AWM.html#L1775).
- `guia-emg` reescrito: [Portal_COE_AWM.html:6378](Portal_COE_AWM.html#L6378) + fases accordion.
- `guia-seg` reescrito: procurar "GUIA DE OCORRÊNCIA — SEGURANÇA (AVSEC)".
- `fichas-emg` dashboard: procurar `occDashActiveCard`.
- PATCH v13 styles+script: final do ficheiro antes de `</body>`.
- Funções JS inertes legadas: `exportFichaGeralCSV`, `exportFichaGeralPDF`, `limparFichaGeral` — não as apagar sem verificar se algo externo ao `fichas-emg` ainda as invoca (eu apenas verifiquei que os callers directos estavam dentro da secção eliminada).

### 4.13 PATCH v12 — Redesign do grupo SIMULACROS na sidebar (COE)
**Edição mista** (HTML directo + CSS aditivo). Motivação: o utilizador classificou a área como "confusa e sem padronização" — 5 itens achatados, ordem pouco clara, "Guia de Utilização" misturado com fichas operacionais, sem paridade visual entre Emergência e Segurança.

**O que mudou**:

1. **HTML da sidebar** (lines ~1775–1808) — edição directa:
   - O `<div class="sidebar-section">` ganhou classe adicional `sidebar-section-simulacros` para scope do CSS novo.
   - **"Guia de Utilização" removido** do menu (decisão C3 — não apagado do DOM, só removido da sidebar; fica acessível via card dentro do `ajuda`).
   - Ficam 4 itens simétricos organizados em 2 tracks: **Emergência Aeronáutica** (2 itens) + **Segurança AVSEC** (2 itens).
   - Cada `<li>` tem uma classe de track (`.sim-track-emg` / `.sim-track-seg`) e uma marca opcional `.sim-track-first` no primeiro item de cada par.
   - Cada `<a>` tem classe `.sim-item` com estrutura `<span class="sim-ico">✈ ou 🛡</span> <span class="sim-label"><span class="sim-label-main">Emergência|Segurança</span><span class="sim-label-sub">Guia|Fichas</span></span>`.
   - **Nenhuma alteração aos `onclick="openSection(...)"`** — os IDs das secções (`guia-emg`, `fichas-emg`, `guia-seg`, `fichas-seg`) são os mesmos; zero risco de regressão em deep-links ou call-sites JS.

2. **Cross-link card** dentro da secção `ajuda` (logo após o parágrafo intro, antes do card "🚀 O que é este portal?"): um `info-card` com fundo `#f5fbff` e borda `var(--medium-blue)` que tem título "📖 Estrutura Completa do Portal", descrição breve, e botão `.btn-primary` que chama `openSection('guia-uso', null)`. Reutiliza `.info-card` e `.btn-primary` — zero CSS novo.

3. **PATCH v12 CSS block** (injectado antes de `</body>`, depois de PATCH v11):
   - Todas as regras scoped a `.sidebar-section-simulacros` — os outros 3 grupos (Principal/Documentação/Sistema) ficam rigorosamente idênticos.
   - Layout flex do `.sim-item` com ícone + label de duas linhas (`sim-label-main` grande + `sim-label-sub` pequena uppercase).
   - **Track Emergência**: borda lateral de 3 px `#c62828` (a mesma cor usada em `.efb-chip.active` e banners de Emergência noutros sítios do portal). Hover/active: `rgba(198,40,40,0.28)` com borda `#ff5252`.
   - **Track Segurança**: borda lateral de 3 px `#f39c12` (a mesma cor usada em `fichas-seg` PATCH). Hover/active: `rgba(243,156,18,0.28)` com borda `#ffb74d`.
   - Separador horizontal entre tracks: `border-top: 1px solid rgba(255,255,255,0.1)` + padding/margin em `.sim-track-seg.sim-track-first`.
   - `@media print` esconde a régua do separador.
   - Override do `.sidebar-menu a` padding para `.sim-item` ter controlo total do seu padding. `border-radius: 0 4px 4px 0` para cantos arredondados apenas no lado direito (a borda lateral esquerda fica quadrada).

**Critérios respeitados** (os 4 do debate inicial):
- **A) Clareza operacional** ✅ — 4 itens em vez de 5; cor identifica track sem ler texto.
- **B) Paridade Emergência ↔ Segurança** ✅ — estrutura idêntica, 2 itens por track, cores distintas, separados.
- **C) Elegância / profissionalismo** ✅ — ícones alinhados, hierarquia tipográfica, hover translúcido.
- **D) Compatibilidade com resto da sidebar** ✅ — CSS inteiramente scoped, zero regras globais novas.

**Onde olhar se algo mudar**: [Portal_COE_AWM.html:1775](Portal_COE_AWM.html#L1775) (sidebar HTML), [Portal_COE_AWM.html:9145](Portal_COE_AWM.html#L9145) (cross-link card), PATCH v12 no final antes de `</body>`.

### 4.6 PATCH v7 — Verificação Mensal de Contactos (COE)
Nova secção `#verif-contactos` (item de menu "✓ Verificação Mensal" entre Contactos e Mapas). Implementa a atribuição COE de ligar mensalmente a todos os 26 contactos operacionais para confirmar telefones.

**Características**:
- Tabela com 26 entidades agrupadas por categoria (SGA Internas / ENNA / Segurança / Externas / Operadores), vindo de constante `VERIF_ENTIDADES` (fonte de verdade single, embebida no patch).
- Selector `<input type="month">` no topo, auto-carrega o mês corrente.
- Por linha: telefones actuais (CISCO + Cel) read-only, 4 chips de status (Atendeu / Não atendeu / Nº errado / Actualizado), campo "telefone confirmado/novo", observações, e coluna auto-preenchida com data/hora/operador (timestamp automático ao interagir).
- Cards de estatísticas no topo (Total, Verificados X/26, Atendeu, Não atendeu, Nº errado, Actualizados) actualizadas em tempo real.
- Bloco de assinaturas no fim: Operador COE + Chefe SREA.
- Persistência: `localStorage["coe_verif_contactos_YYYY-MM"]` com schema `{rows:{id:{status,novoTel,obs,dt,op}}, operador, chefe, savedAt}`.
- Histórico navegável: painel "📅 Histórico de Verificações Mensais" lista todos os meses gravados em ordem decrescente, com stats (X/26 verificados, Y actualizados). Clicar carrega o mês para edição/consulta.
- Export PDF: reutiliza `openPdfWindow()` existente → cabeçalho SGA + header/footer/operador automáticos, tabela resumida + tabela detalhada + linhas de assinatura.
- Usa `awmConfirm`/`awmAlert` (não diálogos nativos).
- A secção é injectada dinamicamente via JS em `DOMContentLoaded` dentro de `.content`, compatível com `openSection()` existente.

## 5. Tarefas em aberto / ideias do utilizador

### 5.2 ✅ Fix B — COMPLETO
Todos os itens do Fix B (unificação de contactos) foram concluídos em sessões sucessivas:

- **B1** (fundação) — PATCH v14 ✅
- **B2.1** (secção `contactos`) — PATCH v15 ✅
- **B2.2** (cr-chips, ~64 sites) — PATCH v17 ✅
- **B2.3** (fluxogramas, ~20 sites) — PATCH v17 ✅
- **B2.4** (VERIF_ENTIDADES) — PATCH v16 ✅
- **B3** (editor unificado read-only) — PATCH v18 ✅
- **B4** (editor unificado **editável** + remoção dos tabs Internos/Externos) — PATCH v19 ✅

Ver §4.15, §4.16 e §4.17 para detalhes. Possíveis extensões futuras (não urgentes):
- Extrair `AWM_CONTACTS_DEFAULT` para ficheiro externo editável via utilitário — actualmente está inline no PATCH v14, o que significa que adicionar/remover um contacto à lista padrão requer edição do HTML.
- Fundir "Operadores COE" no schema unificado (Decisão 1b que foi rejeitada em v19 — o tab Operadores mantém-se separado por razões de login).
- Editor avançado: drag-and-drop para reordenar linhas, bulk edit, validação de formato de telefone.

### 5.1 ⏳ Rebranding do guia de Emergência no estilo AVSEC

> **IMPORTANTE — correcção da versão anterior deste ficheiro**: a camada AVSEC está em `Portal_COE_AWM.html` (secção `fichas-seg`, linha ~7527, com chip navigation por função adicionada por PATCH v2), **não** em `Portal_PSCI_AWM.html`. O Portal PSCI é operacional do SCI e não contém fichas de segurança AVSEC.

> **⚠ BLOQUEADOR IDENTIFICADO**: não existem `FICHA-EMG-01/02/...` no COE. A secção `fichas-emg` (linha 6514) é um **formulário único** de registo do exercício (`FICHA DE REGISTO — EXERCÍCIO DE EMERGÊNCIA` com partes 1, 2, 3...), **não** um conjunto de fichas-por-papel como `fichas-seg` (FICHA-SEC-01 AVSEC, FICHA-SEC-02 COE, etc.). A secção `guia-emg` (linha 6356) é um documento com enquadramento legal, triagem START, zonas operacionais e critérios de avaliação — não tem fichas individuais. Para executar #5.1 o utilizador precisa de **definir primeiro** quais os papéis individuais do lado de Emergência Aeronáutica (provavelmente: COE, TWR, SSCI, SOA, INEMA, PNA, SPCB, SIC, ANAC, Direcção, CARFA, etc.), a missão de cada um, quem os activa, e quem eles activam — isto é trabalho editorial/operacional que só o SGSO pode definir.

O utilizador gosta mais do layout visual do guia AVSEC do `Portal_COE_AWM.html` (secção `fichas-seg` com o bloco **"GUIAS E FICHAS — SIMULACRO DE SEGURANÇA (RESTRITO AVSEC)"**) do que do guia de Emergência actual.

Elementos visuais do AVSEC a replicar no guia de Emergência:
- Banner **"FLUXO OPERACIONAL — SEQUÊNCIA DE ACTIVAÇÃO"** com 6 caixas numeradas em linha (1 Recepção → 2 Activação → 3 Operação → 4 Evacuação → 5 Perímetro → 6 Notificação), com setas entre elas.
- Chips por coluna agrupados em **LÍDER / COORDENAÇÃO / OPERACIONAIS / EXTERNAS**.
- Cada ficha numerada (`FICHA-EMG-01`, etc.) com badge de título colorido, banner de responsabilidade, caixas **"← QUEM ACTIVA ESTE PAPEL"** e **"QUEM ESTE PAPEL ACTIVA →"**.
- Botões **"Imprimir esta ficha"** e **"Imprimir pack completo (briefing)"** no topo.

**Prompt sugerido para pedir ao Claude Code**:
> "Abre `Portal_COE_AWM.html`, procura a secção do guia de Emergência Aeronáutica (procurar por 'Guia' ou 'Ficha-EMG' ou 'FICHAS-EMG'). Reformula-a visualmente para seguir o mesmo padrão do guia AVSEC do `Portal_PSCI_AWM.html` (procurar por 'GUIAS E FICHAS — SIMULACRO DE SEGURANÇA'): fluxo operacional 1-6 no topo, chips de entidades por coluna (Líder / Coordenação / Operacionais / Externas), fichas numeradas com banner de responsabilidade e as caixas 'quem activa este papel' / 'quem este papel activa'. Mantém toda a informação operacional já existente, só muda o layout visual. Valida a sintaxe JS dos 9 script blocks no fim."

## 6. Como começar uma nova sessão (checklist)

1. Abrir a pasta `Simulacros Emergência e Segurança` no VS Code.
2. Abrir o painel Claude Code (Ctrl+Esc).
3. Pedir: **"Lê primeiro `CONTEXTO_CLAUDE_CODE.md` por inteiro antes de qualquer edição."**
4. Só depois descrever a tarefa nova.

---

*Ficheiro mantido por Claude (Cowork) — actualizar sempre que houver mudanças estruturais ou novas convenções.*
