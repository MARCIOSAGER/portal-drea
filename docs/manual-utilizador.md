# Manual do Utilizador — Portal DREA

> Plataforma **Direcção de Resposta a Emergências Aeroportuárias**
> Para operadores do Centro de Operações de Emergência (COE) e do Serviço de Salvamento e Combate a Incêndios (SSCI)

**Versão do manual:** `v2.0` · **Corresponde ao Portal DREA:** `v2.0.0-alpha.2` e superior

---

## Introdução

O **Portal DREA** é a plataforma digital que apoia a gestão de emergências aeroportuárias. É composto por dois produtos complementares:

- **Portal COE** — ferramenta do Coordenador do Centro de Operações de Emergência
- **Portal SSCI** — ferramenta do Chefe dos Bombeiros e do quartel SSCI

Cada produto é distribuído como um ficheiro HTML que abre em qualquer browser moderno. **Não requer instalação de software adicional, nem ligação à internet depois de aberto.**

### A quem se destina

| Portal | Utilizador principal | Local de uso típico |
|---|---|---|
| Portal COE | Coordenador COE, Oficial de turno COE, DREA | Sala do COE, PC ou tablet operacional |
| Portal SSCI | Chefe SSCI, Operador de turno, Bombeiro de reserva | PC do quartel dos bombeiros |

### O que **não** é

O Portal DREA é uma ferramenta de **apoio operacional e registo**. Não substitui sistemas certificados pela ICAO ou ANAC. Complementa-os com registo digital estruturado, consulta rápida de contactos, e documentação auditável.

---

## Parte 1 — Primeiros passos

### 1.1 Receber o ficheiro do portal

O IT do aeroporto distribui o ficheiro HTML apropriado ao teu PC ou tablet. Tipicamente receberás um de:

- `Portal_COE_AWM.html` (se és operador COE)
- `Portal_PSCI_AWM.html` (se és SSCI)

O ficheiro deve ser guardado numa pasta fixa do teu computador (ex: `C:\Portal_COE\`). **Não o apagues**, não o movas após a primeira abertura — os teus dados (configurações, histórico de ocorrências, verificações mensais) ficam associados a este ficheiro.

### 1.2 Primeira abertura

1. Duplo-clique no ficheiro HTML. Abre no teu browser padrão (Chrome, Edge, Firefox recomendados).
2. Na primeira abertura, vais ver o ecrã de **Login de Operador** com um campo para o teu nome.
3. Introduz o teu nome completo e clica **Entrar**.

> **Nota:** o login não é uma autenticação com password. Serve apenas para registar quem está a operar o portal em cada momento, para efeitos de auditoria.

### 1.3 Configuração inicial (uma única vez)

Antes de começares a usar o portal operacionalmente, vai a **Sistema → ⚙ Configurações**. Nesta área podes:

**Tab "📇 Contactos"** (Portal COE apenas): ver, editar e adicionar os 26 contactos operacionais padrão. Confirma que os nomes, telefones CISCO e celulares estão actualizados. Se alguém mudou de função ou número, corrige e clica **💾 Guardar Alterações** — a mudança propaga automaticamente a todas as secções do portal (contactos, fluxogramas, fichas, verificação mensal).

**Tab "🏢 Dados Aeroporto"**: confirma o nome, códigos OACI/IATA, pista, coordenadas. Estes valores são preenchidos automaticamente pela configuração entregue pelo IT, mas podes corrigir se necessário.

**Tab "👤 Operadores COE"**: adiciona os nomes dos operadores autorizados a usar o portal. Estes aparecem como opções no ecrã de login e como coordenadores nos formulários.

**Tab "⚙ Parâmetros"**: tempos de resposta alvo, versões dos documentos (PEA, PSCI, PCA, PSA).

Depois de editar, clica **💾 Guardar Alterações** e **⬇ Exportar JSON** para criares um backup. Guarda o JSON num pen drive ou no OneDrive do aeroporto.

---

## Parte 2 — Fluxo operacional do COE (Emergência Aeronáutica)

### 2.1 Ao receber notificação da TWR

1. **Abre o Portal COE** no PC do COE.
2. Clica em **Ocorrências → ✈ Emergência Aeronáutica → GUIA** para abrir o guia operacional.
3. No topo, clica no botão **🕐 Iniciar / Abrir Cronómetro**.
4. Na secção **Ocorrência** (Cronómetro), o sistema cria uma nova ocorrência com número automático. Preenche o **formulário EFB** (Emergency Form Block) com os dados que a TWR te transmite:
   - Hora da notificação
   - Nº Voo / Matrícula
   - Tipo de Aeronave, Companhia
   - Declaração do piloto (MAYDAY / PAN-PAN / Squawk 7700 / Nenhuma)
   - ETA (hora prevista de aterragem) e minutos até toque
   - POB (Passageiros + Tripulação)
   - Fase do voo, RWY prevista, altitude, distância
   - Nível de alarme declarado (Alerta Local / Alerta Completo / Acidente)

### 2.2 Activação das entidades

5. Com base no nível declarado, volta ao **guia (Ocorrências → Emergência → GUIA)** e segue as **4 fases**:
   - **Fase 1 — Notificação & Avaliação** (0–2 min)
   - **Fase 2 — Activação & Coordenação** (2–10 min)
   - **Fase 3 — Resposta no Local** (10 min – resolução)
   - **Fase 4 — Encerramento & Registo**
6. À medida que fazes cada acção, marca-a no **cronómetro** — isto regista a hora exacta e cria um timeline auditável.

### 2.3 Durante a ocorrência

- Consulta **Contactos** sempre que precisares de telefonar a uma entidade. Podes pesquisar por nome, entidade ou função.
- Consulta **Mapas Quadrícula** para comunicar localização exacta do sinistro.
- Consulta **Fluxogramas** para relembrar a sequência correcta de activação.
- As fichas de **Fichas de Emergência** e **Fichas de Segurança** (se for ocorrência de segurança) servem como referência das responsabilidades de cada entidade.

### 2.4 Encerramento

7. Quando a ocorrência estiver resolvida, volta à **Fase 4** do guia e segue a checklist.
8. Clica em **Ocorrências → ✈ Emergência → FICHAS** para ver o dashboard da ocorrência activa. A partir daí podes **Exportar Ocorrência Actual em PDF** e **Exportar Todas as Ocorrências em CSV**.
9. Inicia o **Relatório Pós-Ocorrência** nas 24 horas seguintes.

---

## Parte 3 — Fluxo operacional do COE (Segurança AVSEC)

A resposta a ameaças de segurança segue um padrão semelhante ao da emergência aeronáutica, mas com vocabulário AVSEC.

1. **Ao receber notificação de ameaça** (telefone, email, etc.): abre o Portal COE, vai a **Ocorrências → 🛡 Segurança → GUIA**.
2. Lê o **cartão de acção imediata** no topo e segue as instruções.
3. **IMPORTANTE**: nunca digas "bomba" em canal aberto — usa os códigos internos acordados.
4. Preenche imediatamente o **FRM-FNMO-AB-001** (10 perguntas) se a ameaça for telefónica.
5. Avalia o **nível de ameaça** (1 Baixo / 2 Médio / 3 Alto) e segue as 4 fases do guia.
6. **AVSEC é a entidade LÍDER** em incidentes de segurança. O COE coordena accionamentos externos.

Para o detalhe dos procedimentos AVSEC, consulta as fichas individuais em **Ocorrências → 🛡 Segurança → FICHAS**.

---

## Parte 4 — Verificação Mensal de Contactos (Portal COE)

A Verificação Mensal é uma **obrigação PEA**. O Coordenador COE liga mensalmente a todos os 26 contactos operacionais para confirmar telefones.

### Como fazer

1. Vai a **Principal → ✓ Verificação Mensal**.
2. Selecciona o mês actual no selector no topo.
3. Para cada contacto listado, telefona e marca o resultado:
   - ✅ **Atendeu** — contacto confirmado
   - ❌ **Não atendeu** — tentar mais tarde
   - ⚠ **Nº errado** — o número está desactualizado
   - 🔄 **Actualizado** — o contacto deu-te um novo número
4. Quando marcares **Nº errado** ou **Actualizado**, preenche o **novo telefone** no campo à direita.
5. Adiciona observações se necessário (ex: "pessoa de férias até dia 15").
6. No fim da ronda, preenche as assinaturas (Operador COE + Chefe SREA) e clica **💾 Gravar Mês**.
7. Clica **📄 Exportar PDF** para gerar o relatório mensal a arquivar.

O sistema guarda cada mês separadamente. Podes navegar o **histórico** para ver verificações anteriores.

---

## Parte 5 — Fluxo operacional do SSCI

### 5.1 Registo de serviço diário

1. No início do turno, abre o **Portal SSCI** e vai a **Registo de Serviço**.
2. Regista a hora de início do turno, nome do operador, viaturas operacionais.
3. Durante o turno, regista qualquer ocorrência real ou rotina.
4. No fim do turno, fecha o registo e assina.

### 5.2 Inspecções diárias aos VCI

Todas as manhãs:

1. **Inspecção Whisky 01** — vai a **Inspecção W01** e percorre a checklist (FR-FNMO-PSCI-011).
2. **Inspecção Whisky 02** — vai a **Inspecção W02** e percorre a checklist (FR-FNMO-PSCI-012).
3. Marca cada item como **OK** ou **NOK**. Se NOK, regista a avaria no campo de observações e vai imediatamente a **⚠ Avaria Equipamento** registar formalmente.

### 5.3 Inspecções semanais de equipamento de resgate

**Inspecção Eqp. Resgate W01** e **W02** — semanalmente verifica o equipamento de resgate a bordo de cada VCI (FR-FNMO-PSCI-017/018).

### 5.4 Testes de comunicações

**Teste Comunicações** — diariamente verifica operacionalidade de sirene, rádios, telefones (FR-FNMO-PSCI-016).

### 5.5 Outras rotinas

- **⛽ Abastecimento VCI** — regista cada abastecimento de combustível das viaturas
- **⏱ Tempo Resposta** — após cada ocorrência real, regista o tempo de resposta para análise mensal
- **✅ Lista Presença** — regista presenças em treinos, briefings, exercícios
- **📦 Controlo de Estoque** — inventário mensal de consumíveis, EPI, extintores

### 5.6 Checklists COE e PCM

- **📝 CheckList COE** — checklist de comunicação com o COE em caso de activação
- **📝 CheckList PCM** — checklist do Posto de Comando Móvel

---

## Parte 6 — Documentação técnica

### 6.1 Planos oficiais (PEA, PSCI, PCA, PSA, MOA)

Vai a **Documentação → PEA/PCA/PSA** (no Portal COE) para consultar os planos oficiais do aeroporto.

- **PEA** (Plano de Emergência Aeroportuária) — embutido no portal, clica **📖 Ver documento**
- **PSCI** (Plano de Salvamento e Combate a Incêndios) — embutido, clica **📖 Ver documento**
- **PCA, PSA, MOA** — abertos via **📂 Abrir PDF** se o ficheiro estiver na mesma pasta do portal

---

## Parte 7 — Exports, impressão e backups

### 7.1 Impressão

- Qualquer secção pode ser impressa com **Ctrl+P**.
- Secções específicas como **Fichas**, **Verificação Mensal** e **Relatório de Ocorrência** têm botões dedicados **🖨 Imprimir** ou **📄 Exportar PDF**.

### 7.2 Exports CSV / PDF

- **Histórico de Ocorrências** → Portal COE → **Ocorrências → Emergência → FICHAS** → **📊 Exportar Todas em CSV**
- **Fichas preenchidas** → secção de fichas → **📊 Exportar CSV**
- **Timeline do cronómetro** → secção Ocorrência → **📊 Exportar Relatório CSV**

### 7.3 Backup de configuração

**Imperativo operacional**: faz backup da configuração semanalmente.

1. Vai a **Sistema → Configurações → ⬇ Exportar JSON**.
2. Guarda o ficheiro `config_coe_awm_YYYY-MM-DD.json` num pen drive, Dropbox, OneDrive, ou no servidor do aeroporto.
3. Se o computador falhar ou tiveres que reinstalar o portal, podes restaurar com **⬆ Importar JSON**.

> **Aviso**: se limpares a cache do browser, os dados do localStorage são apagados. Faz export antes de limpar cache.

---

## Parte 8 — Atalhos de teclado

| Atalho | O que faz |
|---|---|
| **Ctrl+F** | Pesquisar texto em qualquer secção |
| **Ctrl+P** | Imprimir / gerar PDF da secção actual |
| **Ctrl+S** | Guardar (onde aplicável) |
| **Esc** | Fechar modal / popup activo |
| **Tab / Shift+Tab** | Navegar entre campos de formulário |
| **Enter** | Confirmar em modais |

---

## Parte 9 — Resolução de problemas comuns

### "Os meus dados desapareceram!"

Provavelmente a cache do browser foi limpa. Se tinhas um backup JSON recente, importa em **Sistema → Configurações → ⬆ Importar JSON**. Se não tinhas backup, os dados estão perdidos — é uma razão crítica para fazer exports regulares.

### "O portal não abre / ficheiro corrompido"

Verifica se o tamanho do ficheiro HTML está correcto (deve ser ~3.8 MB para o COE, ~1.5 MB para o SSCI). Se estiver muito mais pequeno, pode estar corrompido. Pede ao IT uma cópia nova.

### "Editei um contacto mas não apareceu nos fluxogramas"

Clica no botão **🔄 Actualizar Snapshot** no topo da secção onde estás. Se continuar a não aparecer, fecha e reabre a secção.

### "Preciso de usar o portal num computador novo"

1. No computador antigo, faz **Sistema → ⬇ Exportar JSON** para teres backup.
2. Copia o ficheiro `Portal_COE_AWM.html` (ou `Portal_PSCI_AWM.html`) para o computador novo.
3. Abre-o no browser.
4. Vai a **Sistema → ⬆ Importar JSON** e carrega o backup.
5. Agora o portal novo tem os teus dados.

### "Esqueci-me da password"

O Portal DREA **não usa password**. O login é apenas registo de operador. Basta introduzir o teu nome para entrar.

### "Preciso de suporte técnico"

Contacta a **equipa de TI** do teu aeroporto. Eles têm o contacto directo com o consultor responsável (Marcio Sager, SGSO).

---

## Apêndice A — Glossário

| Termo | Significado |
|---|---|
| **COE** | Centro de Operações de Emergência |
| **SSCI** | Serviço de Salvamento e Combate a Incêndios |
| **DREA** | Direcção de Resposta a Emergências Aeroportuárias |
| **PEA** | Plano de Emergência Aeroportuária |
| **PSCI** | Plano de Salvamento e Combate a Incêndios |
| **PSA** | Plano de Segurança de Aeroporto |
| **PCA** | Plano de Contingência de Aeroporto |
| **MOA** | Manual de Operações do Aeródromo |
| **TWR** | Torre de Controlo |
| **SOA** | Serviço de Operações Aeroportuárias |
| **AVSEC** | Security (Aviation Security) |
| **VCI** | Veículo de Combate a Incêndio |
| **EFB** | Emergency Form Block (formulário operacional) |
| **POB** | People On Board (passageiros + tripulação) |
| **ETA** | Estimated Time of Arrival |
| **MAYDAY** | Declaração de perigo iminente pelo piloto |
| **PAN-PAN** | Declaração de urgência pelo piloto |
| **Squawk 7700** | Código emergência do transponder |
| **NOTAM** | Notice to Airmen (aviso oficial aos pilotos) |
| **INEMA** | Instituto Nacional de Emergências Médicas |
| **SPCB** | Serviço de Protecção Civil e Bombeiros |
| **PNA** | Polícia Nacional de Angola |
| **SIC** | Serviço de Investigação Criminal |
| **ANAC** | Autoridade Nacional da Aviação Civil |
| **RAC** | Força Aérea Nacional (Região Aérea de Combate) |

---

## Apêndice B — Histórico de versões deste manual

- **v2.0** (2026-04) — Primeira versão completa escrita durante a Fase 1 Etapa 4 do projecto. Cobre Portal COE e Portal SSCI na plataforma DREA.

---

## Suporte e contacto

Para questões operacionais sobre o uso do portal, contacta o **SGSO do teu aeroporto**.

Para bugs técnicos, funcionalidades em falta, ou sugestões de melhoria, contacta o **IT do aeroporto** — que por sua vez reporta ao consultor responsável pelo Portal DREA.
