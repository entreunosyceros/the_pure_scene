# Empaqueta The Pure Scene en un .exe con Flet/PyInstaller.
# Ejecutar en Windows (PowerShell) desde la raíz del repo:
#   powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$Version = if ($env:VERSION) { $env:VERSION } else { "1.0.0" }
$Dist = Join-Path $Root "dist"
New-Item -ItemType Directory -Force -Path $Dist | Out-Null

Write-Host "==> Preparando icono .ico"
$IconPng = Join-Path $Root "assets\tray-icon.png"
$IconIco = Join-Path $Root "assets\the-pure-scene.ico"
if (Test-Path $IconPng) {
    python -c @"
from PIL import Image
img = Image.open(r'$IconPng').convert('RGBA')
sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
img.save(r'$IconIco', sizes=sizes)
print('ico ok')
"@
}

Write-Host "==> Instalando herramientas de empaquetado"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install "pyinstaller>=6.0" "flet-cli==0.28.3"

Write-Host "==> Empaquetando con flet pack"
$IconArg = @()
if (Test-Path $IconIco) { $IconArg = @("-i", $IconIco) }

python -m flet pack main.py `
  -n "ThePureScene" `
  -y `
  --distpath $Dist `
  --product-name "The Pure Scene" `
  --file-description "The Pure Scene - quitar fondo de imagenes" `
  --product-version $Version `
  --file-version "$Version.0" `
  --company-name "entreunosyceros" `
  --copyright "GPL-3.0" `
  --add-data "assets;assets" `
  --hidden-import rembg `
  --hidden-import onnxruntime `
  --hidden-import pystray `
  --hidden-import PIL `
  --hidden-import numpy `
  @IconArg

# Renombrar a nombre con versión
$Exe = Join-Path $Dist "ThePureScene.exe"
$Out = Join-Path $Dist "ThePureScene-$Version-windows-x64.exe"
if (Test-Path $Exe) {
    Copy-Item -Force $Exe $Out
    Write-Host "Listo: $Out"
    Get-Item $Out | Format-List Name, Length, FullName
} else {
    Write-Host "Buscando ejecutable en $Dist"
    Get-ChildItem $Dist -Recurse -Filter *.exe | ForEach-Object { $_.FullName }
    throw "No se encontró ThePureScene.exe"
}
