# Extensões GNOME Shell do THYRON OS

Alvo: **GNOME Shell 50** (`shell-version: ["50"]`). Não há garantia para outras versões.

| Extensão | O que faz | Estado (16/11/2026) |
|---|---|---|
| `thyron-app-launcher@thyron-os.local` | Lançador de aplicativos (overlay com categorias, busca, modo Iniciante/Avançado e painel de detalhes). | Em desenvolvimento. Versão v8 ou mais nova, instalada na VM. Funcionamento completo dos cliques **não confirmado**. Ainda contém logs de depuração `[THYRON]`. 211 de 259 apps caem em "Outros". |
| `thyron-lockscreen@thyron-os.local` | Visual da tela de **bloqueio**: fundo próprio, logo, relógio, slogan e logo THYRON no lugar do avatar. Não altera autenticação (PAM/GDM). | v3. Instalação e funcionamento básico confirmados pelo usuário em 16/11/2026. |

A tela de **login (GDM)** não é coberta por estas extensões e continua pendente.

## Regras

- No Wayland, a extensão só recarrega depois de **sair da sessão e entrar de novo**.
- Faça backup antes de alterar. O `dev-install-extensions.sh` já guarda a versão anterior.
- Não reinicie o GDM em sessão ativa.
- Os ativos de `thyron-lockscreen/assets/` (logo e fundo) têm **autoria e licença ainda não confirmadas** (ver `branding/ASSETS.md`). Não distribuir em ISO pública antes disso.

## Instalação para desenvolvimento

```bash
bash scripts/dev-install-extensions.sh            # instala as duas
bash scripts/dev-install-extensions.sh remover    # remove as duas
```

Depois: sair da sessão, entrar de novo e `gnome-extensions enable <uuid>`.

Na ISO, a instalação será pelo pacote `thyron-desktop` (`packages/thyron-desktop/`, em `/usr/share/gnome-shell/extensions/`), não por este script. O pacote já pode ser construído (`bash packages/thyron-desktop/build.sh`); instalação real na VM ainda não testada. Antes de testá-lo, rode `dev-install-extensions.sh remover` (a cópia de `~/.local` tem prioridade sobre a do sistema).
