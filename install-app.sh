#!/usr/bin/env sh
# build.sh ile derlenen uygulamayı kullanıcıya kurar (sudo gerekmez):
#   ~/.local/opt/tapo-gui/      program
#   ~/.local/bin/tapo-gui       komut satırından başlatma
#   uygulama menüsü kısayolu ve simgesi
# Kaldırmak için: ./install-app.sh --uninstall
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
OPT="$HOME/.local/opt/tapo-gui"
BIN="$HOME/.local/bin/tapo-gui"
APPS="$HOME/.local/share/applications"
ICONS="$HOME/.local/share/icons/hicolor/scalable/apps"

if [ "$1" = "--uninstall" ]; then
    rm -rf "$OPT" "$BIN" "$APPS/tapo-gui.desktop" "$ICONS/tapo-gui.svg"
    command -v update-desktop-database >/dev/null && update-desktop-database "$APPS" 2>/dev/null || true
    echo "Kaldırıldı. (Ayarlarınız ~/.config/tapo-gui içinde duruyor.)"
    exit 0
fi

if [ ! -x "$DIR/dist/tapo-gui/tapo-gui" ]; then
    echo "Önce derleyin: ./build.sh" >&2
    exit 1
fi

rm -rf "$OPT"
mkdir -p "$(dirname "$OPT")" "$(dirname "$BIN")" "$APPS" "$ICONS"
cp -r "$DIR/dist/tapo-gui" "$OPT"
ln -sf "$OPT/tapo-gui" "$BIN"
cp "$DIR/assets/tapo-gui.svg" "$ICONS/tapo-gui.svg"

cat > "$APPS/tapo-gui.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=Tapo Işık Kontrol
GenericName=Akıllı ışık kontrolü
Comment=Tapo ışıkların parlaklık ve rengini kontrol et
Exec=$OPT/tapo-gui
Icon=tapo-gui
Terminal=false
Categories=Utility;
Keywords=tapo;ışık;lamba;ampul;led;light;
StartupWMClass=tapo-gui
DESK

command -v update-desktop-database >/dev/null && update-desktop-database "$APPS" 2>/dev/null || true
command -v kbuildsycoca6 >/dev/null && kbuildsycoca6 >/dev/null 2>&1 || true
echo "Kuruldu: uygulama menüsünde 'Tapo Işık Kontrol' olarak görünecek."
echo "Terminalden: tapo-gui"
