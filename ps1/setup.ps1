# powershell -executionpolicy bypass -file "E:\git\igaponr\training\ps1\setup.ps1"
# 管理者権限チェック
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "このスクリプトは管理者権限で実行する必要があります。PowerShellを「管理者として実行」してください。"
    exit
}

# 1. Chocolateyのインストール確認と導入
if (!(Get-Command choco.exe -ErrorAction SilentlyContinue)) {
    Write-Host "Chocolateyが見つかりません。インストールを開始します..." -ForegroundColor Cyan
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

    # パスを反映させるために現在のセッションを更新
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "Chocolateyは既にインストールされています。" -ForegroundColor Green
}

# 2. 相対パスで packages.config を指定
# $PSScriptRoot はこのスクリプトがあるフォルダを指します
$configPath = Join-Path $PSScriptRoot "..\config\packages.config"

if (Test-Path $configPath) {
    Write-Host "構成ファイルを見つけました: $configPath" -ForegroundColor Cyan
    Write-Host "パッケージのインストールを開始します..." -ForegroundColor Cyan
    # フルパスで指定して実行
    choco install "$configPath" -y
} else {
    Write-Error "packages.config が見つかりませんでした。"
    Write-Host "期待されるパス: $configPath" -ForegroundColor Yellow
}

Write-Host "セットアップ処理が終了しました。" -ForegroundColor Green
# pause
