#!/usr/bin/env sh
# Uygulamayı PyInstaller ile Python gerektirmeyen bağımsız bir programa dönüştürür.
# Çıktı: dist/tapo-gui/tapo-gui
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if ! .venv/bin/python -c "import sys" 2>/dev/null; then
    uv venv .venv
fi
uv pip install --python .venv/bin/python -q -r requirements.txt pyinstaller

rm -rf build dist
.venv/bin/python -m PyInstaller \
    --noconfirm --clean --log-level WARN \
    --onedir --windowed \
    --name tapo-gui \
    --add-data "assets:assets" \
    --collect-submodules tapo \
    tapo_gui.py

# Derleme Ubuntu (distrobox) konteynerinde yapılıyor. Konteynerin sistem kütüphaneleri
# (font, GTK, X11, glib, libstdc++…) CachyOS'takilerle çakışabildiği için pakete koyma;
# program çalışırken bunları ana sistemden kullansın. Qt, Python, PySide ve OpenSSL pakette kalır.
INTERNAL="$DIR/dist/tapo-gui/_internal"
for pat in \
    'libX*' 'libxcb*' 'libxkbcommon*' \
    'libgtk-3*' 'libgdk*' 'libatk*' 'libatspi*' 'libcairo*' 'libpango*' 'libharfbuzz*' 'libfribidi*' \
    'libthai*' 'libdatrie*' 'libgraphite2*' 'libpixman*' 'libepoxy*' \
    'libglib-2*' 'libgio-2*' 'libgobject-2*' 'libgmodule-2*' 'libgthread-2*' 'libffi*' 'libpcre2*' \
    'libfontconfig*' 'libfreetype*' 'libexpat*' 'libpng16*' 'libjpeg*' 'libbrotli*' \
    'libbz2*' 'libz.so*' 'libzstd*' 'liblzma*' 'liblz4*' \
    'libdbus-1*' 'libsystemd*' 'libcap.so*' 'libgcrypt*' 'libgpg-error*' 'libselinux*' 'libmount*' 'libblkid*' \
    'libkrb5*' 'libgssapi*' 'libk5crypto*' 'libcom_err*' 'libkeyutils*' 'libbsd*' 'libmd.so*' \
    'libstdc++*' 'libgcc_s*' 'libicu*'; do
    rm -f "$INTERNAL"/$pat
done

echo "Derleme tamam: $DIR/dist/tapo-gui/tapo-gui"
echo "Sisteme kurmak için: ./install-app.sh"
