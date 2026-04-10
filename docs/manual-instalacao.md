# Manual de Instalação — Portal DREA

> Para o responsável de TI do aeroporto
> Plataforma **Direcção de Resposta a Emergências Aeroportuárias**

**Versão:** `v2.0` · **Corresponde ao Portal DREA:** `v2.0.0-alpha.2` e superior

---

## Público-alvo

Este manual destina-se ao **técnico de TI responsável pela instalação e manutenção** do Portal DREA em aeroportos da SGA. Assume conhecimentos básicos de administração Windows, manipulação de ficheiros, e browsers.

**Não é** um manual de utilizador — para isso consulta [manual-utilizador.md](manual-utilizador.md).

---

## Requisitos do sistema

### Hardware mínimo

- **CPU**: qualquer dual-core x86-64 (i3, Ryzen 3, ou equivalente)
- **RAM**: 4 GB
- **Disco**: 500 MB livres
- **Display**: 1280×720 mínimo, 1920×1080 recomendado

### Sistema operativo

- **Windows 10** build 1909+ (recomendado: Windows 11)
- **Windows Server 2016+** (para instalação em PC partilhado)
- Outras plataformas (Linux, macOS) funcionam mas não são oficialmente suportadas

### Browser

O Portal DREA é um HTML standalone que corre em qualquer browser moderno:

| Browser | Versão mínima | Recomendado |
|---|---|---|
| **Microsoft Edge** | 90+ | Sim — vem com o Windows |
| **Google Chrome** | 90+ | Sim |
| **Mozilla Firefox** | 88+ | Sim |
| Opera, Brave, outros Chromium | — | Compatíveis |
| **Internet Explorer** | — | ❌ Não suportado |

### Rede

**Funciona 100% offline** após a primeira abertura. Não requer ligação à internet para operar.

A única dependência de rede é:
- **No momento de receber o ficheiro** (email do consultor, pen drive, partilha de ficheiros do aeroporto)
- **No momento de actualizar para versão nova** (receber o novo ficheiro)

---

## Instalação passo-a-passo

### Passo 1 — Receber o ficheiro do portal

O consultor responsável envia um pack de instalação contendo:

```
Portal_DREA_vX.X.X_FNMO.zip
├── Portal_COE_AWM.html          (3.8 MB) — para o PC do COE
├── Portal_PSCI_AWM.html         (1.5 MB) — para o PC do SSCI
├── manual-utilizador.pdf         — para distribuição aos operadores
├── manual-instalacao.pdf         — este ficheiro
├── checklist-validacao.pdf       — para verificar a instalação
└── config_backup.json            — cópia de segurança da configuração
```

> **Alternativa**: em vez de ZIP, podes receber os ficheiros via OneDrive SharePoint do aeroporto ou pen drive selado.

### Passo 2 — Escolher onde instalar

**Para o PC do COE** (normalmente um PC fixo na sala de operações):

1. Cria a pasta `C:\Portal_COE\` (ou `D:\Portal_COE\` se tiveres segundo disco).
2. Copia para lá o `Portal_COE_AWM.html`.
3. Adiciona a pasta à lista de pastas excluídas do antivírus (para não bloquear o localStorage ou a impressão).

**Para o PC do SSCI** (normalmente no quartel dos bombeiros):

1. Cria a pasta `C:\Portal_SSCI\`.
2. Copia para lá o `Portal_PSCI_AWM.html`.
3. Mesma exclusão de antivírus.

### Passo 3 — Criar atalhos no ambiente de trabalho

Para facilitar o acesso dos operadores:

1. Clica direito no `Portal_COE_AWM.html` → **Enviar para → Ambiente de trabalho (criar atalho)**.
2. Muda o nome do atalho para **"Portal COE"** (sem extensão).
3. Clica direito no atalho → **Propriedades → Alterar Ícone** e escolhe um ícone SGA ou um emoji-like adequado.
4. Fixa o atalho na barra de tarefas: clica direito no atalho → **Fixar na barra de tarefas**.

Repete para o Portal SSCI no PC do quartel.

### Passo 4 — Primeira abertura e validação

1. Duplo-clique no atalho **Portal COE**.
2. O browser padrão abre o portal.
3. Verifica que:
   - O header no topo mostra "Centro de Operações de Emergência" + nome do aeroporto
   - A sidebar à esquerda tem os grupos PRINCIPAL, OCORRÊNCIAS, DOCUMENTAÇÃO, SISTEMA
   - O rodapé da sidebar mostra a versão (ex: `Portal COE v2.0.0-alpha.2 · 2026-04-10 · FNMO · SGA`)
   - Aparece o ecrã de login pedindo nome de operador
4. Introduz um nome de teste (ex: "Técnico TI") e clica **Entrar**.
5. Clica **Sistema → ⚙ Configurações** para ver se o tab **📇 Contactos** mostra 26 entradas.
6. Faz logout e fecha o browser.

Repete para o Portal SSCI.

### Passo 5 — Importar a configuração de backup (opcional mas recomendado)

Se o consultor te enviou um `config_backup.json`, importa-o para preservar configurações anteriores:

1. Abre o Portal COE.
2. Faz login como "Técnico TI".
3. Vai a **Sistema → Configurações → ⬆ Importar JSON**.
4. Selecciona o `config_backup.json`.
5. Confirma no modal "Substituir configuração actual?".
6. Verifica que os contactos, operadores, e parâmetros foram restaurados.

---

## Configurações do browser recomendadas

Para os utilizadores finais terem a melhor experiência, configura o browser do PC do COE/SSCI:

### Microsoft Edge

1. Abre o Edge.
2. Vai a **Definições → Cookies e permissões do site → Armazenamento local** e confirma que está **permitido**.
3. Vai a **Definições → Descarregamentos** e define a pasta de descargas para `C:\Portal_COE\Exports\` (cria se não existir).
4. Vai a **Definições → Impressoras** e define a impressora padrão do aeroporto como padrão.

### Chrome / Firefox

Configurações equivalentes nas respectivas áreas de configurações.

---

## Política de actualizações

### Quando actualizar

O consultor responsável envia notificações de novas versões. Recebes um email com:
- Notas da release (o que mudou, o que foi corrigido)
- Novo ficheiro HTML (ou pack ZIP completo)
- Recomendação de quando aplicar (urgente / recomendado / quando conveniente)

### Como actualizar

**Procedimento seguro (recomendado)**:

1. **Avisa os operadores** que vai haver update em X minutos.
2. **Faz backup da configuração actual**: Portal COE → Sistema → Configurações → ⬇ Exportar JSON. Guarda o ficheiro com nome descritivo (ex: `backup_pre_v2.1_2026-05-15.json`).
3. **Copia o ficheiro HTML actual** para uma subpasta de segurança (ex: `C:\Portal_COE\archive\Portal_COE_AWM_v2.0.html`). **NÃO o apagas** — fica como fallback se o update falhar.
4. **Substitui o ficheiro** `C:\Portal_COE\Portal_COE_AWM.html` pelo novo.
5. **Abre o portal** e verifica:
   - Versão no rodapé da sidebar está actualizada
   - Contactos continuam a aparecer
   - Login funciona
   - Todas as secções da sidebar abrem
6. Se algo estiver errado:
   - Restaura o ficheiro antigo de `archive/`
   - Importa o backup JSON
   - Notifica o consultor

**Procedimento simplificado (apenas para patches de segurança)**:

Substituir o ficheiro directamente. O localStorage do browser preserva automaticamente os dados do utilizador.

### Política de backups

**Frequência mínima**:

- **Backup de configuração**: semanal (Sexta-feira, ao fim do turno)
- **Backup completo de pasta**: mensal (primeiro dia do mês)

**Onde guardar**:

- **Cópia 1**: pen drive dedicado do aeroporto (rotação de 4 pen drives, um por semana)
- **Cópia 2**: OneDrive / SharePoint do aeroporto (pasta restrita a IT e operadores COE)
- **Cópia 3 mensal**: servidor do aeroporto (se existir) ou HDD externo offline

**Retenção**:

- Últimas 4 semanas de backups semanais (rolling)
- Últimos 12 meses de backups mensais
- Backups anuais arquivados por 3 anos mínimo

---

## Troubleshooting

### O ficheiro HTML não abre

- **Sintoma**: duplo-clique não abre nada, ou abre como texto bruto
- **Causa provável**: associação de ficheiros .html quebrada
- **Solução**: clica direito no ficheiro → **Abrir com → Microsoft Edge** → marca **"Usar sempre esta aplicação"**

### O portal abre mas está em branco

- **Sintoma**: browser abre, página branca
- **Causa provável**: JavaScript desabilitado
- **Solução**: Edge → Definições → Cookies e permissões → JavaScript → permitir

### "localStorage is full" ou os dados não gravam

- **Sintoma**: mensagens de erro ao gravar contactos, ocorrências desaparecem
- **Causa**: quota do localStorage do browser esgotada (5-10 MB)
- **Solução**:
  1. Fazer export JSON antes de limpar
  2. Limpar localStorage do site (Edge: F12 → Application → Storage → Clear site data)
  3. Reimportar JSON

### "Mixed content" ou avisos de segurança

- **Sintoma**: cadeado vermelho na barra do browser, avisos de "não seguro"
- **Causa**: abrir o HTML via `file://` é normal — não é https
- **Solução**: ignorar. O Portal DREA funciona correctamente via `file://` porque é single-file e offline.

### Impressão corta conteúdo ou sai mal formatada

- **Sintoma**: imprimir um relatório sai incompleto ou com layout partido
- **Causa provável**: impressora com drivers antigos ou papel errado
- **Solução**:
  1. Verificar que o papel é A4
  2. No dialog de impressão, escolher "Ajustar à página"
  3. Se persistir, usar **Microsoft Print to PDF** como intermediário

### Antivírus bloqueia o ficheiro

- **Sintoma**: o ficheiro HTML é apagado ou colocado em quarentena
- **Causa**: falso positivo por ser um HTML grande com JavaScript
- **Solução**: adicionar a pasta `C:\Portal_COE\` e `C:\Portal_SSCI\` às excepções do antivírus. Se for política de segurança que impede excepções, contactar o consultor para obter versão assinada digitalmente.

---

## Desinstalação

Para remover o Portal DREA de um PC:

1. **Fazer backup final** da configuração (Exportar JSON).
2. Apagar a pasta `C:\Portal_COE\` (ou `C:\Portal_SSCI\`).
3. Limpar localStorage do browser (Edge: Definições → Cookies → Ver todas as cookies → procurar `file://` → apagar).
4. Remover atalhos do ambiente de trabalho e barra de tarefas.

---

## Contactos

**Consultor responsável pelo Portal DREA**: Marcio Sager (SGSO / FNMO)

**Para questões técnicas de instalação**: contactar via email ou através do canal oficial SGA.

**Para bugs urgentes durante operação**: deve existir um canal directo de escalação definido pela direcção do aeroporto.

---

## Apêndice A — Estrutura interna de ficheiros (informativo)

Se precisares de inspeccionar o conteúdo do portal para auditoria:

```
Portal_COE_AWM.html     (~3.8 MB)
├── <head>
│   ├── <title>                Portal COE — Aeroporto [NOME]
│   ├── <meta>                 charset, viewport, no-cache
│   └── <style>                CSS inline (~15 blocos)
├── <body>
│   ├── <div class="sidebar">  Navegação lateral
│   ├── <div class="main">     Secções operacionais
│   │   ├── Dashboard
│   │   ├── Cronómetro
│   │   ├── Contactos
│   │   ├── Verificação Mensal
│   │   ├── Mapas Quadrícula
│   │   ├── Fluxogramas
│   │   ├── Guias Emergência/Segurança
│   │   ├── Fichas Emergência/Segurança
│   │   ├── Documentação
│   │   ├── Guia Rápido
│   │   └── Configurações
│   └── <script>               JavaScript inline (18 blocos, ~250 KB total)
```

O ficheiro é **self-contained** — zero dependências externas, zero chamadas de rede.

## Apêndice B — localStorage keys usadas

| Chave | Conteúdo | Tamanho típico |
|---|---|---|
| `coe_awm_config` | Configuração do aeroporto + contactos | 20-50 KB |
| `coe_awm_occurrences` | Histórico de ocorrências | Variável |
| `coe_verif_contactos_YYYY-MM` | Verificação mensal por mês | ~5 KB/mês |
| `coe_awm_config_backup_pre_v14` | Backup automático pré-v14 | 20-30 KB |
| `psci_awm_config` | Config SSCI (no Portal SSCI) | 10-20 KB |

Para inspeccionar localStorage manualmente no Edge/Chrome: **F12 → Application → Storage → Local Storage → file://**.
