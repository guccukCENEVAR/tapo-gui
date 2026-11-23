#!/usr/bin/env sh
# Sanal ortamı kurar ve uygulama menüsüne kısayol ekler.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
if ! command -v uv >/dev/null 2>&1; then
    echo "uv bulunamadı. Kurmak için: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi
if ! .venv/bin/python -c "import sys" 2>/dev/null; then
    rm -rf .venv
    uv venv .venv
fi
uv pip install --python .venv/bin/python -r requirements.txt

mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/tapo-gui-dev.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=Tapo Işık Kontrol (geliştirme)
Comment=Tapo ampullerin parlaklık ve rengini kontrol et
Exec=$DIR/tapo-gui
Icon=$DIR/assets/tapo-gui.svg
Terminal=false
Categories=Utility;
DESK
echo "Kurulum tamam. Uygulama menüsünde 'Tapo Işık Kontrol (geliştirme)' olarak görünecek."
