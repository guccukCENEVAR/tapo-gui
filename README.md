# Tapo Light Control

> 🇹🇷 Türkçe dokümantasyon için: [README.tr.md](README.tr.md)

A fast, modern desktop application for controlling **TP-Link Tapo smart lights** (L510, L520, L530, L535, L610, L630, L900/L920/L930 light strips, etc.) on **Windows 11** and **Linux**.

All commands run directly over your **local network (LAN)** — nothing goes through the cloud.

---

## Features

- **Local LAN control** with modern TPAP encryption via the [`tapo`](https://github.com/mihai-dinculescu/tapo) library.
- **Interactive light tiles**: each active tile glows in the light's current color and fills from bottom to top according to its brightness level.
- **Gesture & mouse controls**:
  - **Hold & drag up/down** (or scroll with the mouse wheel) on a tile to adjust brightness directly; drag to the bottom to turn off.
  - **Right-click** any tile for a quick popup panel (power, brightness, preset & custom colors, white temperatures, rename).
  - **Click** a tile for the full detail view (hue, saturation, color temperature in Kelvin, color picker, keyboard numeric entry).
- **Custom color presets**: save your own favorite colors (`+` button); right-click a saved color to rename or delete it.
- **Local device aliases**: rename lights locally inside the app without altering their names in the Tapo mobile app.
- **Live language switcher**: instant **English / Turkish** (`EN` / `TR`) toggle built right into the top bar, persisted in config.
- **Cross-platform**: standalone builds for both **Windows 11** and **Linux**.

---

## Installation & Building

### Windows 11

Requires [Python 3.10+](https://www.python.org/downloads/).

**Build a standalone app (recommended):**

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

This creates `.venv-win`, generates `assets\tapo-gui.ico` from the SVG icon, and produces:
`dist\tapo-gui\tapo-gui.exe`

To build a single portable `.exe` file (`--onefile`) instead:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1 -OneFile
```

**Run from source:**

```powershell
python -m venv .venv-win
.\.venv-win\Scripts\pip install -r requirements.txt
.\.venv-win\Scripts\python tapo_gui.py
```

### Linux

**Build a standalone app:**

```sh
./build.sh           # builds dist/tapo-gui/tapo-gui
./install-app.sh     # installs to ~/.local and adds a desktop menu entry
```

To uninstall:

```sh
./install-app.sh --uninstall
```

**Run from source (development):**

```sh
./install.sh         # sets up .venv via uv and adds a launcher
./tapo-gui
```

---

## Usage

1. On first launch, enter the **TP-Link / Tapo email and password** you use in the Tapo mobile app (Tapo devices require authentication even on local LAN).
2. Click **Scan network** to discover lights on your local subnet, or **Add by IP** to connect directly to a known IP address.
3. Click the **EN / TR** button in the top-right corner at any time to switch between English and Turkish.
4. Navigation shortcuts on the light detail page: `Esc`, `Alt+Left`, or the mouse **Back** button returns to the main screen.

---

## Configuration

Settings, saved hosts, custom colors, aliases, and language preference are stored locally in:

- **Windows:** `%APPDATA%\tapo-gui\config.json`
- **Linux:** `~/.config/tapo-gui/config.json` (permissions set to `600`)

---

## Troubleshooting

- **Network discovery:** Discovery sends both broadcast packets and individual probes across your local `/24` subnet so devices are still found even if a firewall blocks UDP broadcasts. Scanning takes roughly 10–15 seconds.
- **Authentication error:** Make sure your email and password match the Tapo app (*Account* button). If authentication still fails, open the Tapo mobile app and toggle *Me → Third-Party Services → Third-Party Compatibility* off and back on.
- **Windows Firewall:** On first launch, allow private network access if prompted by Windows Defender Firewall so local discovery and device communication work properly.

---

## License

This project is licensed under the [MIT License](LICENSE).
