#!/usr/bin/env bash
# THYRON OS - monta o pacote thyron-desktop (.deb) a partir das fontes do repositorio.
#
# Uso:   bash packages/thyron-desktop/build.sh
# Saida: packages/thyron-desktop/dist/thyron-desktop_<versao>_all.deb  (dist/ e ignorado pelo Git)
# Opcional: OUT_DIR=/outro/caminho  para mudar a pasta de saida.
#
# Fonte unica: extensoes em desktop/gnome/extensions/, wallpapers em branding/wallpapers/.
# Nada disso e copiado para dentro de packages/ - o pacote e montado em pasta temporaria.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
OUT_DIR="${OUT_DIR:-$HERE/dist}"

EXT_SRC="$REPO/desktop/gnome/extensions"
WALL_SRC="$REPO/branding/wallpapers"

EXTENSIONS=(
  "thyron-app-launcher@thyron-os.local"
  "thyron-lockscreen@thyron-os.local"
)

# destino-no-pacote:arquivo-de-origem (em branding/wallpapers/)
WALLPAPERS=(
  "thyron-desktop.png:thyron-wallpaper-concept-wolf-lakeside.png"
  "thyron-wolf-moon-circle.png:thyron-wallpaper-concept-wolf-moon-circle.png"
)

die() { echo "ERRO: $*" >&2; exit 1; }

command -v dpkg-deb >/dev/null || die "dpkg-deb nao encontrado (pacote 'dpkg-dev' ou 'dpkg')."
command -v python3  >/dev/null || die "python3 nao encontrado."

# ---------- validacoes de origem ----------
for uuid in "${EXTENSIONS[@]}"; do
  dir="$EXT_SRC/$uuid"
  [[ -d "$dir" ]]               || die "extensao ausente: $dir"
  [[ -f "$dir/metadata.json" ]] || die "sem metadata.json: $dir"
  [[ -f "$dir/extension.js" ]]  || die "sem extension.js: $dir"
  python3 - "$dir/metadata.json" "$uuid" <<'PY' || die "metadata.json invalido em $uuid"
import json, sys
meta = json.load(open(sys.argv[1], encoding="utf-8"))
assert meta["uuid"] == sys.argv[2], f"uuid {meta['uuid']!r} difere do diretorio"
assert meta.get("shell-version"), "shell-version ausente"
PY
done

for pair in "${WALLPAPERS[@]}"; do
  src="$WALL_SRC/${pair#*:}"
  [[ -f "$src" ]] || die "wallpaper ausente: $src"
done

# Nada de lixo de desenvolvimento dentro das extensoes.
junk="$(find "$EXT_SRC" \( -name '.venv' -o -name '__pycache__' -o -name '*.egg-info' \
        -o -name '*.bak' -o -name '*.bak.*' -o -name '*.antes-*' -o -name '.git' \) -print)"
[[ -z "$junk" ]] || die "arquivos indesejados nas extensoes:"$'\n'"$junk"

# ---------- montagem em pasta temporaria ----------
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
PKG="$STAGE/pkg"

install -d "$PKG/usr/share/gnome-shell/extensions" "$PKG/usr/share/backgrounds/thyron"

for uuid in "${EXTENSIONS[@]}"; do
  cp -r --no-preserve=mode,ownership "$EXT_SRC/$uuid" "$PKG/usr/share/gnome-shell/extensions/$uuid"
done

for pair in "${WALLPAPERS[@]}"; do
  cp --no-preserve=mode,ownership "$WALL_SRC/${pair#*:}" "$PKG/usr/share/backgrounds/thyron/${pair%%:*}"
done

cp -r --no-preserve=mode,ownership "$HERE/files/." "$PKG/"
cp -r --no-preserve=mode,ownership "$HERE/DEBIAN" "$PKG/DEBIAN"

# Permissoes: diretorios 755, arquivos 644, scripts de mantenedor 755.
find "$PKG" -type d -exec chmod 755 {} +
find "$PKG" -type f -exec chmod 644 {} +
chmod 755 "$PKG/DEBIAN/postinst" "$PKG/DEBIAN/postrm"

# Installed-Size (KiB), sem contar DEBIAN.
size_kib="$(du -sk --exclude=DEBIAN "$PKG" | cut -f1)"
printf 'Installed-Size: %s\n' "$size_kib" >> "$PKG/DEBIAN/control"

# Build reprodutivel: datas fixadas no ultimo commit (ou agora, fora do Git).
SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git -C "$REPO" log -1 --format=%ct 2>/dev/null || date +%s)}"
export SOURCE_DATE_EPOCH
find "$PKG" -exec touch -h -d "@$SOURCE_DATE_EPOCH" {} +

# ---------- build ----------
version="$(sed -n 's/^Version: //p' "$PKG/DEBIAN/control")"
mkdir -p "$OUT_DIR"
deb="$OUT_DIR/thyron-desktop_${version}_all.deb"
dpkg-deb --root-owner-group -Zxz --build "$PKG" "$deb" >/dev/null

echo "Pacote gerado: $deb"
echo "SHA-256: $(sha256sum "$deb" | cut -d' ' -f1)"
echo
case "$version" in
  *~dev*) echo "AVISO: build de desenvolvimento. Wallpapers/ativos com licenca NAO confirmada (branding/ASSETS.md). Nao redistribuir." ;;
esac
