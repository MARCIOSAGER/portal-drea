# Design — Relatório de Operações de SCI em Aeronaves

**Data:** 2026-04-14
**Portal:** SSCI (Portal_PSCI_AWM)
**Referência oficial:** AP.04.033 # FR-FNMO-PSCI-019 — Form. Relatório de Operações de SCI em Aeronaves

## 1. Contexto e objetivo

O portal SSCI actualmente cobre três categorias de registos:

- **Formulários Diários** — rotina de serviço (Registo de Serviço, Inspecções W01/W02, Teste Comunicações)
- **Formulários Operacionais** — eventos recorrentes (Avaria, Abastecimento, Tempo Resposta, Presença)
- **Checklists Mensais** — verificações COE/PCM

O formulário oficial **AP.04.033 (FR-FNMO-PSCI-019)** não se enquadra em nenhuma destas categorias: é um **relatório pós-ocorrência** preenchido apenas quando ocorre efectivamente um acidente/emergência com aeronave no aeródromo. É um evento raro mas crítico, com um longo fluxo de preenchimento (10 secções, pode demorar horas/dias a completar após o incidente).

O objectivo deste design é integrar este formulário no portal SSCI mantendo:

- A separação visual entre rotina e eventos críticos
- O padrão DS existente (tokens, componentes, helpers de impressão)
- Offline-first (localStorage), como todos os outros forms do portal
- Rastreabilidade via **número de controlo único** por relatório finalizado

## 2. Decisões-chave (brainstorm)

| # | Decisão | Escolha |
|---|---|---|
| Q1 | Grupo no sidebar | Novo grupo "Relatórios de Ocorrência" (isolado de rotina/operacional) |
| Q2 | Persistência | Rascunho único + submissão final irreversível (1 draft de cada vez) |
| Q3 | Formato nº controlo | `{OACI}/{ANO}/{SEQ}` — ex. `FQMA/2026/001` |
| Q4 | Layout | Accordion single-page com indicador lateral sticky |
| Q5 | PDF | Usa `window.sgaPrintReport()` existente (consistência com outros forms) |
| Q6 | Após finalização | Irreversível + arquivo local (lista de finalizados, só leitura + reimprimir) |

## 3. Arquitectura

### 3.1 Sidebar

Novo grupo inserido **após "Formulários Operacionais"** e **antes de "Recursos"**, em [packages/portal-ssci/src/Portal_PSCI_AWM.source.html](packages/portal-ssci/src/Portal_PSCI_AWM.source.html):

```html
<div class="ds-sidebar__section">
    <h3 class="ds-sidebar__section-title">Relatórios de Ocorrência</h3>
    <ul class="ds-sidebar__list">
        <li><button onclick="openSection('rel-sci-aeronaves', event)"
                    class="nav-btn nav-btn--pill">🛩 Relatório Ops SCI Aeronaves</button></li>
    </ul>
</div>
```

Justificação da posição: o fluxo natural do utilizador é rotina → operacional → ocorrência → recursos; e colocar antes de Recursos mantém os itens administrativos (Stock, Checklists, Sistema) juntos no fim.

### 3.2 Estados da secção

A secção `<div id="rel-sci-aeronaves" class="section">` tem **três estados mutuamente exclusivos**. Cada estado é um sub-div com classe `rel-sci-state rel-sci-state--<nome>`, controlado via `.active`:

**Estado `lista` (default)**

- Card "Rascunho actual" — apenas visível se existir rascunho; mostra `dataInicio`, `percentualPreenchido`, botões "Continuar" / "Descartar"
- Botão "Novo Relatório" — disabled se existir rascunho
- Tabela "Relatórios Finalizados" — colunas: Nº Controlo, Data Ocorrência, Aeronave (tipo + matrícula), Acções (Ver / Reimprimir)

**Estado `editor`**

- Layout duas colunas: índice lateral sticky (esquerda, 200px) + accordion do formulário (direita)
- Barra fixa no topo: badge estado guardado, botões "Voltar à lista" / "Finalizar Relatório"
- Accordion — cada secção é `<details class="rel-sci-section" open>` com `<summary>` (título + ícone estado: ⚠ incompleto / ✓ preenchido)
- Indicador lateral `<nav class="rel-sci-toc">`: lista 1–10 com ancoras; `IntersectionObserver` destaca a secção visível

**Estado `visualizacao`**

- Renderiza relatório finalizado em modo só-leitura (todos os inputs `disabled`)
- Barra topo: "Voltar à lista" / "Imprimir" (re-invoca `sgaPrintReport`)

Transições controladas por `window.RelSciAeronaves.setState(estado, payload?)`.

### 3.3 Persistência (localStorage)

Três chaves:

| Chave | Tipo | Descrição |
|---|---|---|
| `psci.rel-sci-aeronaves.draft` | `object` ou ausente | Rascunho actual (único) |
| `psci.rel-sci-aeronaves.finalized` | `array` | Lista de relatórios finalizados, ordenada por `dataFinalizacao` desc |
| `psci.rel-sci-aeronaves.counter.<ano>` | `number` | Contador sequencial por ano (incrementa ao finalizar) |

**Schema do objecto relatório:**

```js
{
  id: '<uuid-ou-timestamp>',              // id interno (drafts)
  numeroControlo: 'FQMA/2026/001',        // só em finalizados
  dataInicio: '2026-04-14T10:32:00Z',
  dataFinalizacao: '2026-04-14T18:05:00Z',// só em finalizados
  locked: true,                           // só em finalizados
  secoes: {
    s1: { /* identificação */ },
    s2: { /* fase operação */ },
    // ...
    s10: { /* responsável */ }
  }
}
```

### 3.4 Número de controlo

Função `gerarNumeroControlo(ano)`:

```
oaci  = config.airport.oaci        // ex. "FQMA"
key   = `psci.rel-sci-aeronaves.counter.${ano}`
seq   = (localStorage.getItem(key) || 0) + 1
localStorage.setItem(key, seq)
return `${oaci}/${ano}/${String(seq).padStart(3, '0')}`
```

Contador é **por ano** e reinicia em Janeiro. Usa o ano de `dataFinalizacao` (não de `dataInicio`, pois um rascunho pode atravessar Ano Novo).

## 4. Estrutura do formulário (10 secções)

Mapeamento directo do .docx original para campos HTML:

| # | Título | Campos |
|---|---|---|
| 1 | Identificação da Ocorrência | 1.1 Aeródromo (auto=OACI config, readonly), 1.2 Província (texto), 1.3 Data do Acidente (date), 1.4 Hora Local (time), 1.5 Período (radio: dia/noite), 1.6 Tipo Aeronave (texto), 1.7 Matrícula (texto), 1.8 Empresa (texto), 1.9 Propósito da Operação (texto), 1.10 Combustível — Tipo (texto) + Quantidade kg (number), 1.11 Alerta dado por (texto), 1.12 Hora do Alerta (time) |
| 2 | Fase da Operação | 2.1–2.4 checkboxes: Pouso, Decolagem, Táxi, Estacionamento |
| 3 | Condições Meteorológicas | 3.1 Visibilidade km (number), 3.2 Condições Gerais (textarea) |
| 4 | Ocupantes e Vítimas | 4.1 Total a bordo (pax + trip), 4.2 Salvos sem ajuda (feridos + ilesos), 4.3 Resgatados vivos (feridos + ilesos), 4.4 Mortos (pax + trip), 4.5 Vítimas em terra (mortos + feridos), 4.6 Óbitos até 24h (ocupantes + vítimas terra), 4.7 Mortos por fogo (valor) |
| 5 | Tempos de Resposta | 5.1–5.8: 8 inputs `type="text"` com máscara HH:MM:SS — intervalos descritos no docx original |
| 6 | Serviço SCI | 6.1 Equipa aeródromo (6 linhas fixas: VCI/Bombeiros/Médicos/Ambulâncias/Cisterna/Outros — cada linha: tipo texto + qtd number), 6.2 Equipa externa (mesma estrutura), 6.3 Agentes extintores (6 linhas fixas: Pó Químico/CO2/LGE/Água-espuma/Água-outros/Outros — colunas: Qtd L, Razão L/min, Tempo min, Ordem emprego, Suficiente Sim/Não) |
| 7 | Descrição da Ocorrência | 7.1 Descrição Sucinta (textarea), 7.2 Relato de Combate (textarea), 7.3 Evacuação (textarea) |
| 8 | Outros Detalhes | 8.1 Comunicações/terreno/acessos (textarea) |
| 9 | Informações Adicionais | 9.1 Estado final aeronave — matriz 4 linhas × 2 colunas de checkboxes (Destruída/Grav.danificada/Poucos danos/Incólume × Pelo Acidente/Pelo Incêndio) |
| 10 | Responsável | 10.1 Local (texto, default=OACI), Data (auto=hoje), Nome (texto), Cargo (texto), Assinatura (texto) |

**Linhas "Outros" em 6.1/6.2/6.3**: linha fixa com label "Outros" + campo texto livre ao lado (permite especificar). Não há linhas dinâmicas/repetíveis — mantém o layout fiel ao docx e evita complexidade UX.

## 5. Fluxos

### 5.1 Criar rascunho

1. Utilizador clica "Novo Relatório" (estado `lista`)
2. Cria objecto `{ id, dataInicio: now(), secoes: {} }` e grava em `draft`
3. `setState('editor', { draftId: id })`
4. Scroll para topo, primeiro accordion aberto

### 5.2 Auto-save

- Cada `blur` ou `change` nos inputs dispara `saveField(path, value)`
- `saveField` actualiza o objecto em memória + `localStorage.setItem('psci.rel-sci-aeronaves.draft', ...)`
- Actualiza badge "Guardado às HH:MM" (componente `.awm-badge` já existente)
- **Debounce 500ms** para evitar gravações excessivas em textareas

### 5.3 Validação ao finalizar

Campos **obrigatórios** (bloqueiam finalização):

- Secção 1: Aeródromo, Província, Data Acidente, Hora Acidente, Tipo Aeronave, Matrícula, Empresa
- Secção 2: pelo menos uma fase marcada
- Secção 7.1: Descrição Sucinta (não vazia)
- Secção 10: Nome + Assinatura

Os restantes campos são **recomendados mas não obrigatórios** — realidade pós-incidente pode ter lacunas (ex: tempos exactos, agentes extintores) que se desconhecem no momento da redacção.

Se validação falha: mostrar toast + scroll até primeira secção com erro + highlight dos campos em falta.

### 5.4 Finalizar relatório

1. Click em "Finalizar Relatório" → valida → se ok:
2. Modal de confirmação: "Esta acção é **irreversível**. O relatório será arquivado e gera número de controlo. Confirma?"
3. Gera `numeroControlo` via `gerarNumeroControlo(ano)`
4. Mover objecto de `draft` → `finalized[]`, adicionando `numeroControlo`, `dataFinalizacao: now()`, `locked: true`
5. Remover chave `draft` do localStorage
6. Chamar `window.sgaPrintReport({ titulo, numeroControlo, secoes: [...] })`
7. `setState('visualizacao', { relatorioId: id })`

### 5.5 Reimprimir relatório finalizado

- Estado `visualizacao` tem botão "Imprimir" que re-invoca `sgaPrintReport` com os mesmos dados
- Não altera dados nem estado

## 6. Integração com `sgaPrintReport`

A chamada segue o padrão dos outros forms do portal:

```js
window.sgaPrintReport({
  titulo: 'Relatório de Operações de SCI em Aeronaves',
  subtitulo: `AP.04.033 / FR-FNMO-PSCI-019 — Nº ${numeroControlo}`,
  campos: [
    // secção 1
    { label: '1.1 Aeródromo', valor: secoes.s1.aerodromo },
    { label: '1.2 Província', valor: secoes.s1.provincia },
    // ... mapeamento de todas as secções
  ]
});
```

O helper já trata: cabeçalho SGA (logo + título), paginação, rodapé com versão/build, impressão. Não há necessidade de CSS de impressão adicional.

## 7. Estrutura de código

### 7.1 HTML (source.html)

Três blocos novos em [Portal_PSCI_AWM.source.html](packages/portal-ssci/src/Portal_PSCI_AWM.source.html):

1. **Sidebar**: `<div class="ds-sidebar__section">` com grupo "Relatórios de Ocorrência"
2. **Main content**: `<div id="rel-sci-aeronaves" class="section">` com três sub-divs de estado
3. **Script**: bloco `<script>` com módulo `window.RelSciAeronaves` (IIFE ou objecto literal)

### 7.2 Módulo JS

API pública esperada:

```js
window.RelSciAeronaves = {
  init(),                           // bootstrap: carrega draft se existir, renderiza lista
  setState(estado, payload),        // 'lista' | 'editor' | 'visualizacao'
  criarRascunho(),
  descartarRascunho(),
  saveField(path, value),           // auto-save com debounce
  finalizar(),                      // valida + gera nº controlo + move p/ finalized
  imprimir(relatorioId),            // invoca sgaPrintReport
  _render(),                        // helper interno
  _validar()                        // helper interno
};
```

`init()` é chamado em `DOMContentLoaded` (padrão dos outros módulos).

### 7.3 Testes

Adicionar [tests/test_rel_sci_aeronaves.py](tests/test_rel_sci_aeronaves.py) cobrindo:

1. Geração de nº controlo sequencial dentro do ano
2. Reinício do contador no ano seguinte
3. Validação de obrigatórios (cenários: sem data, sem descrição, sem fase)
4. Transição draft → finalized (draft removido, finalized actualizado, locked=true)
5. Bloqueio de edição após finalizar (tentativa de `saveField` em finalizado falha)

Testes em Python seguem o padrão existente em [tests/](tests/) — usam extracção de HTML + JS via `script` tags ou simulam via `jsdom` se necessário.

## 8. Build e deploy

Sem alterações ao pipeline. `npm run build` (ou `python scripts/ds_build_helpers.py` directo) trata tokens `{{VERSION}}`, `{{BUILD_DATE_SHORT}}`, `{{AIRPORT.OACI}}`, `{{AIRPORT.OPERATOR_SHORT}}` na source.html e regenera `packages/portal-ssci/dist/index.html`.

Config OACI lê de [packages/portal-ssci/portal.config.json](packages/portal-ssci/portal.config.json) — JSON key `airport.oaci`.

## 9. Commits previstos

Três commits atómicos para facilitar review:

1. `feat(ssci): add Relatórios de Ocorrência sidebar group + section scaffold` — sidebar + HTML das três views (vazias) + estado de navegação
2. `feat(ssci): implement relatório SCI aeronaves form with autosave` — módulo JS, 10 secções, validação, finalização, nº controlo
3. `test(ssci): add tests for relatório SCI aeronaves lifecycle` — testes da secção 7.3

## 10. Fora de scope (YAGNI)

- Sincronização entre dispositivos (portal é offline-first local)
- Exportação/importação de relatórios em JSON
- Pesquisa/filtro na lista de finalizados (inicialmente ordenação simples por data)
- Anexos (fotos, documentos) — pode ser added em iteração futura se for requisito operacional
- Relatório customizado fiel ao .docx — utilizador confirmou `sgaPrintReport` é suficiente
- Histórico de versões de um mesmo relatório (finalização é irreversível)

## 11. Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Utilizador perde rascunho ao limpar browser/localStorage | Aviso claro no card "Rascunho actual" + eventual botão "Exportar JSON" em iteração futura |
| Colisão de nº controlo entre dispositivos (contador local) | Aceitável — cada dispositivo mantém sequência própria; no contexto do SSCI, um só aeródromo raramente tem múltiplos dispositivos a gerar relatórios simultaneamente |
| Formulário longo intimida utilizador pós-incidente | Auto-save + accordion + indicador lateral + campos obrigatórios mínimos mitigam; utilizador pode fechar e retomar |
| Mudança no formulário oficial (nova versão do .docx) | Código dos campos (`s1.aerodromo`, etc.) é estável; estrutura localStorage pode evoluir com versão de schema se necessário |
