<#
.SYNOPSIS
    Tapo Işık Kontrol uygulamasını Windows 11 için PyInstaller ile derler.
.DESCRIPTION
    Çıktı (varsayılan --onedir): dist\tapo-gui\tapo-gui.exe
    Tek dosya (--onefile) için:  .\build.ps1 -OneFile
#>
param(
    [switch]$OneFile
)

$ErrorActionPreference = "Stop"
$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $Dir

try {
    $VenvDir = Join-Path $Dir ".venv-win"
    $VenvPy  = Join-Path $VenvDir "Scripts\python.exe"

    if (-not (Test-Path $VenvPy)) {
        Write-Host "Windows sanal ortamı (.venv-win) oluşturuluyor..." -ForegroundColor Cyan
        python -m venv $VenvDir
    }

    Write-Host "Bağımlılıklar kuruluyor..." -ForegroundColor Cyan
    & $VenvPy -m pip install --upgrade --quiet pip
    & $VenvPy -m pip install --quiet -r requirements.txt pyinstaller

    # SVG'den çoklu çözünürlüklü Windows .ico dosyası üret (yoksa veya SVG güncellendiyse)
    $SvgPath = Join-Path $Dir "assets\tapo-gui.svg"
    $IcoPath = Join-Path $Dir "assets\tapo-gui.ico"
    if ((-not (Test-Path $IcoPath)) -or ((Get-Item $SvgPath).LastWriteTime -gt (Get-Item $IcoPath).LastWriteTime)) {
        Write-Host "Windows ikonu (assets\tapo-gui.ico) oluşturuluyor..." -ForegroundColor Cyan
        & $VenvPy -c @"
import struct, sys
from pathlib import Path
from PySide6.QtCore import QBuffer, QIODevice, QRectF, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

app = QGuiApplication(sys.argv)
renderer = QSvgRenderer(r'$SvgPath')
sizes = [16, 24, 32, 48, 64, 128, 256]
pngs = []
for s in sizes:
    img = QImage(s, s, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.SmoothPixmapTransform, True)
    renderer.render(p, QRectF(0, 0, s, s))
    p.end()
    buf = QBuffer()
    buf.open(QIODevice.WriteOnly)
    img.save(buf, 'PNG')
    pngs.append((s, bytes(buf.data())))

# ICO başlığı + dizin girdileri + PNG verileri
header = struct.pack('<HHH', 0, 1, len(pngs))
offset = 6 + 16 * len(pngs)
entries = bytearray()
body = bytearray()
for s, data in pngs:
    dim = 0 if s == 256 else s
    entries += struct.pack('<BBBBHHII', dim, dim, 0, 0, 1, 32, len(data), offset)
    body += data
    offset += len(data)
Path(r'$IcoPath').write_bytes(header + entries + body)
"@
    }

    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist")  { Remove-Item -Recurse -Force "dist" }

    $ModeFlag = if ($OneFile) { "--onefile" } else { "--onedir" }

    Write-Host "PyInstaller ile derleniyor ($ModeFlag)..." -ForegroundColor Cyan
    & $VenvPy -m PyInstaller `
        --noconfirm --clean --log-level WARN `
        $ModeFlag --windowed `
        --name tapo-gui `
        --icon "$IcoPath" `
        --add-data "assets;assets" `
        --collect-submodules tapo `
        tapo_gui.py

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller derlemesi başarısız oldu (çıkış kodu: $LASTEXITCODE)."
    }

    $OutExe = if ($OneFile) {
        Join-Path $Dir "dist\tapo-gui.exe"
    } else {
        Join-Path $Dir "dist\tapo-gui\tapo-gui.exe"
    }

    Write-Host ""
    Write-Host "Derleme tamamlandı: $OutExe" -ForegroundColor Green
}
finally {
    Pop-Location
}
