# Registro de decisões (ADR)

Este arquivo registra decisões de produto e arquitetura para evitar mudanças implícitas.

## ADR-001 — Base do sistema

- **Status:** Aceita
- **Decisão:** Kali Linux.
- **Motivo:** decisão estabelecida no documento mestre do projeto.
- **Consequência:** preservar compatibilidade com APT, infraestrutura Debian e repositórios Kali; acompanhar a natureza rolling release da base.

## ADR-002 — Ambiente gráfico

- **Status:** Aceita
- **Decisão:** GNOME como ambiente principal.
- **Consequência:** usar GJS para extensões e GTK/GSettings conforme compatibilidade; não desenvolver a experiência principal para KDE Plasma.

## ADR-003 — Identidade visual

- **Status:** Aceita
- **Decisão:** Electric Blue; THYRON Modern como perfil inicial; modo escuro por padrão.
- **Cores:** `#050914`, `#0B1425`, `#075BFF`, `#00C8FF`, `#DCE5F2`.

## ADR-004 — Estratégia do repositório

- **Status:** Aceita
- **Decisão:** repositório público e estrutura completa desde o início.
- **Interpretação:** criar todos os diretórios e documentos planejados agora, mas implementar os componentes por marcos pequenos e verificáveis. "Complete" não significa tentar implementar todos os recursos antes do primeiro teste.

## ADR-005 — Primeira entrega

- **Status:** Aceita
- **Decisão:** priorizar ISO Live experimental.
- **Fora do escopo inicial:** instalador definitivo, personalização profunda de GDM e Store completa.

## ADR-006 — Preservação do ambiente de desenvolvimento

- **Status:** Aceita
- **Decisão:** não substituir a distribuição instalada no computador de desenvolvimento e não realizar alterações destrutivas.
- **Prática:** diagnóstico antes de instalar dependências; testes iniciais em máquina virtual.

## ADR-007 — Licenças e marcas

- **Status:** Em validação
- **Decisão provisória:** código original sob GPL-3.0-or-later; ativos e componentes de terceiros terão licença/atribuição própria.
- **Ação:** confirmar compatibilidade de licenças e avisos antes de distribuir qualquer ISO.
