# thyron-desktop

Primeiro pacote do THYRON Desktop. **Estado (16/11/2026): construído e verificado por testes automatizados; instalação real na VM Kali ainda NÃO testada.**

## O que instala

| Destino | Conteúdo | Origem (fonte única no repositório) |
|---|---|---|
| `/usr/share/gnome-shell/extensions/thyron-app-launcher@thyron-os.local/` | Lançador de aplicativos | `desktop/gnome/extensions/` |
| `/usr/share/gnome-shell/extensions/thyron-lockscreen@thyron-os.local/` | Visual da tela de bloqueio (com `assets/`) | `desktop/gnome/extensions/` |
| `/etc/dconf/db/local.d/10-thyron-desktop` | Extensões ativas por padrão (conffile) | `packages/thyron-desktop/files/` |
| `/usr/share/backgrounds/thyron/thyron-desktop.png` | Wallpaper "wolf-lakeside" | `branding/wallpapers/` |
| `/usr/share/backgrounds/thyron/thyron-wolf-moon-circle.png` | Wallpaper "wolf-moon-circle" | `branding/wallpapers/` |
| `/usr/share/doc/thyron-desktop/copyright` | Licenças (ativos: **não confirmada**) | `packages/thyron-desktop/files/` |

O `postinst` roda `dconf update`. Se `/etc/dconf/profile/user` não existir, cria com `user-db:user` + `system-db:local`; se existir sem `system-db:local`, **só avisa** (não edita arquivo alheio).

## O que NÃO faz (de propósito)

- Não toca no GDM (`/etc/dconf/profile/gdm`, `/etc/dconf/db/gdm.d/`): tela de login segue pendente (Prompt Mestre §25.6/§26.1).
- Não altera PAM/autenticação.
- Não define o wallpaper padrão nem o do bloqueio via dconf; apenas disponibiliza os arquivos.
- Não declara dependências de Dash to Dock, DING etc.: nomes de pacote precisam ser validados no Kali fixado antes (ver `iso/kali-config/package-lists/thyron.list.chroot`).

## Build

```bash
bash packages/thyron-desktop/build.sh
# saída: packages/thyron-desktop/dist/thyron-desktop_0.1.0~dev1_all.deb  (dist/ é ignorado pelo Git)
python3 tests/integration/test_thyron_desktop_package.py -v
```

A versão fica em `DEBIAN/control`. O sufixo `~dev` faz o build imprimir o aviso de licença.

## Testar na VM Kali

1. **Remova a cópia de desenvolvimento**, senão ela vence a do sistema (mesmo UUID em `~/.local/share/gnome-shell/extensions/`):
   `bash scripts/dev-install-extensions.sh remover`
2. `bash packages/thyron-desktop/build.sh`
3. `sudo apt install ./packages/thyron-desktop/dist/thyron-desktop_0.1.0~dev1_all.deb`
4. Sair da sessão e entrar de novo (Wayland).
5. Conferir: `gnome-extensions list --enabled | grep thyron` e `journalctl -b -o cat /usr/bin/gnome-shell | grep -E "THYRON|JS ERROR"`.

### Armadilha: o padrão do sistema não vale se o usuário já tem valor próprio

Na VM, o usuário `kali` já tem `enabled-extensions` gravado em `~/.config/dconf/` (qualquer `gnome-extensions enable` grava ali). Nesse caso o padrão deste pacote **não aparece**. Para testar o padrão de verdade:

```bash
dconf reset /org/gnome/shell/enabled-extensions   # só do usuário atual; sair e entrar
```

Em usuário novo (ex.: o da ISO) o padrão vale direto.

### A lista `enabled-extensions` substitui, não soma

O arquivo traz as duas extensões THYRON **mais as 10 que a VM já tinha ativas** (Prompt Mestre §25.1), para não desligar dock e tema. Revise: `apps-menu` e `places-menu` podem ser redundantes com o lançador THYRON; `top-panel-vpnip@kali.org` é específica do Kali. UUID de extensão não instalada é ignorado pelo Shell.

## Reverter

```bash
sudo apt remove thyron-desktop      # conffile permanece
sudo apt purge thyron-desktop       # remove também /etc/dconf/db/local.d/10-thyron-desktop
```

Se a tela de bloqueio quebrar: `Ctrl+Alt+F3`, entrar e rodar `gnome-extensions disable thyron-lockscreen@thyron-os.local`.

## Pendências

- **Licença dos wallpapers e dos ativos da tela de bloqueio não confirmada** (`branding/ASSETS.md`; Prompt Mestre §23.4 proíbe `.deb`/ISO com esses PNG). Este build é interno; não redistribuir.
- Wallpapers com 1672×941 (abaixo de Full HD).
- `lock-wallpaper.png` e `thyron-logo.png` da extensão são cópias byte a byte dos conceitos em `branding/` (mesmo SHA-256); trocar por um único ativo aprovado quando houver.
- O launcher ainda tem 18 linhas de log `[THYRON]` e seu funcionamento de cliques não foi confirmado.
