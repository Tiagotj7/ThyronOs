
# Registro de ativos

Regra: nenhum ativo é redistribuído na ISO sem origem, autor e licença confirmados.
Os arquivos abaixo foram fornecidos pelo responsável do projeto em 09/11/2026.
**Autor/origem e licença ainda não foram confirmados** (o método de criação das imagens não está registrado).
Por isso, todos constam como *conceito/referência* e **não** como ativos finais aprovados.

Legenda de status:
- **Conceito (raster)**: imagem de partida; o ativo final deverá ser recriado (ex.: logotipo em vetor SVG).
- **Referência de design**: mockup que orienta a implementação. Não é evidência de implementação.
- **Pendente**: licença/autoria a confirmar antes de qualquer redistribuição.

## Logotipo (`branding/logo/`)

| Arquivo | Dimensões | Conteúdo | Autor/origem | Licença | Status |
|---|---|---|---|---|---|
| `thyron-logo-concept-transparent.png` | 1672×941, RGBA | Logo "T" prateado/azul com anel + wordmark THYRON OS, fundo transparente | Fornecido pelo responsável; autoria a confirmar | A confirmar | Conceito (raster) — Pendente |
| `thyron-logo-concept-banner.png` | 1672×941, RGB | Logo com slogan LIBERDADE • DESEMPENHO • INOVAÇÃO sobre fundo azul | Fornecido pelo responsável; autoria a confirmar | A confirmar | Conceito (raster) — Pendente |

Observação: as duas versões diferem no desenho do "T" (a primeira com barra superior prateada, a segunda com barra superior azul).
Escolher a versão oficial antes de vetorizar (M2).

## Wallpapers (`branding/wallpapers/`)

| Arquivo | Dimensões | Conteúdo | Autor/origem | Licença | Status |
|---|---|---|---|---|---|
| `thyron-wallpaper-concept-wolf-moon-circle.png` | 1672×941 | Lobo de frente, anel luminoso, lua e montanhas | Fornecido; autoria a confirmar | A confirmar | Conceito — Pendente |
| `thyron-wallpaper-concept-wolf-lakeside.png` | 1672×941 | Lobo à esquerda sobre rochas, lua, montanhas e lago (base da tela de login/bloqueio e do desktop) | Fornecido; autoria a confirmar | A confirmar | Conceito — Pendente |

Resolução 1672×941 é inferior a Full HD; será necessário versão em resolução maior ou recriação.

## Referências de design (`branding/references/`)

| Arquivo | Dimensões | Mostra | Status |
|---|---|---|---|
| `ref-01-planning-infographic.png` | 1024×1536 | Infográfico de planejamento (versão anterior com KDE) | Referência — **desatualizada** (ver divergências) |
| `ref-02-desktop-start-menu.png` | 1672×941 | Desktop com ícones, menu iniciar e dock inferior | Referência de design |
| `ref-03-activities-overview.png` | 1672×941 | Visão geral de atividades/espaços de trabalho, barra superior e dock | Referência de design (mais próxima do GNOME) |
| `ref-04-login-screen.png` | 1672×941 | Tela de login (lobo à esquerda, autenticação à direita) | Referência de design |
| `ref-05-lock-and-desktop-wide.png` | 1672×941 | Bloqueio (parte superior) e desktop com menu (parte inferior), variante ultrawide | Referência de design |
| `ref-06-style-center-board.png` | 1536×1024 | THYRON Style Center, seis estilos, bloqueio e desktop Modern | Referência de design |
| `ref-07-store-all-apps.png` | 1536×1024 | Central de aplicativos — aba "Todos" | Referência — contém apps KDE |
| `ref-08-store-installed-apps.png` | 1536×1024 | THYRON Store — aba "Instalados" com painel de detalhes | Referência — contém apps KDE e aba Snap |

## Divergências entre as referências e as decisões oficiais

As imagens são conceitos e **não prevalecem** sobre o Prompt Mestre:

1. `ref-01` cita KDE Plasma, KWin, SDDM, Calamares e Oh My Zsh. A decisão oficial é **GNOME/Mutter/GDM**; instalador e shell ainda a validar.
2. `ref-02`, `ref-05`, `ref-07`, `ref-08` exibem aplicativos KDE (Dolphin, Konsole, Kate, Discover, KCalc etc.). No GNOME usar Nautilus, GNOME Terminal, GNOME Text Editor, etc. (Prompt Mestre §10.7).
3. `ref-07` mostra o Discover. O Discover **não** será a central principal.
4. `ref-08` mostra uma aba **Snap**. Snap **não** será habilitado por padrão.
5. `ref-02` e `ref-05` usam menu iniciar tradicional estilo KDE/Zorin; no GNOME a visão de Atividades deve ser preservada (menu próprio é opcional).
6. As datas nas imagens (08/11/2025) e os valores de requisitos do `ref-01` (40 GB) divergem do planejamento atual (mínimo proposto 30 GB). Valem os valores do Prompt Mestre, ainda não validados.
7. Dados exibidos nas imagens (quantidade de apps, uso de disco, clima, versões) são fictícios.
