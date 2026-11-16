#!/usr/bin/env bash
# THYRON OS - instala as extensões GNOME do repositório na sessão do usuário (desenvolvimento).
# Uso:  bash scripts/dev-install-extensions.sh [instalar|remover]
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO/desktop/gnome/extensions"
DEST="$HOME/.local/share/gnome-shell/extensions"
BACKUP="$HOME/.local/share/thyron-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
ACTION="${1:-instalar}"

mkdir -p "$DEST" "$BACKUP"
found=0
for dir in "$SRC"/*@*/; do
  [[ -d "$dir" ]] || continue
  found=1
  uuid="$(basename "$dir")"
  target="$DEST/$uuid"

  if [[ -d "$target" ]]; then
    gnome-extensions disable "$uuid" 2>/dev/null || true
    mv "$target" "$BACKUP/$uuid.$STAMP"
    echo "Versão anterior de $uuid guardada em $BACKUP/$uuid.$STAMP"
  fi

  if [[ "$ACTION" == "instalar" ]]; then
    cp -a "$dir" "$target"
    echo "Instalada: $uuid"
  fi
done

[[ $found -eq 1 ]] || { echo "Nenhuma extensão encontrada em $SRC"; exit 1; }

if [[ "$ACTION" == "instalar" ]]; then
  cat <<MSG

Próximos passos:
  1. Saia da sessão e entre de novo (no Wayland, só assim o Shell enxerga o código novo).
  2. gnome-extensions enable thyron-app-launcher@thyron-os.local
     gnome-extensions enable thyron-lockscreen@thyron-os.local
  3. Erros:  journalctl -b -o cat /usr/bin/gnome-shell | grep -E "THYRON|JS ERROR"
  Se o bloqueio quebrar: Ctrl+Alt+F3, entre e rode  gnome-extensions disable thyron-lockscreen@thyron-os.local
MSG
else
  echo "Removidas. Saia da sessão e entre de novo."
fi
