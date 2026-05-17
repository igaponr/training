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

# 2. Chocolateyによるパッケージインストール (packages.config)
$configPath = Join-Path $PSScriptRoot "..\config\packages.config"
if (Test-Path $configPath) {
    Write-Host "構成ファイルを見つけました: $configPath" -ForegroundColor Cyan
    Write-Host "Chocolateyパッケージのインストールを開始します..." -ForegroundColor Cyan
    choco install "$configPath" -y
} else {
    Write-Error "packages.config が見つかりませんでした。"
    Write-Host "期待されるパス: $configPath" -ForegroundColor Yellow
}

# --- 追加セクション：ここから ---
# 3. Pythonの requirements.txt からのインストール
$requirementsPath = Join-Path $PSScriptRoot "..\config\requirements.txt"
if (Test-Path $requirementsPath) {
    Write-Host "Pythonの構成ファイルを見つけました: $requirementsPath" -ForegroundColor Cyan
    # 最新のパスを再読込（chocoでpythonをいれた直後の場合、反映が必要なため）
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    # Python または Python3 が実行可能かチェック
    $pythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } elseif (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { $null }
    if ($pythonCmd) {
        Write-Host "Pythonパッケージのインストールを開始します..." -ForegroundColor Cyan
        # python -m pip を使用するのが最も確実です
        & $pythonCmd -m pip install --upgrade pip
        & $pythonCmd -m pip install -r "$requirementsPath"
    } else {
        Write-Warning "Pythonが見つからないため、pipインストールをスキップしました。"
        Write-Host "Pythonをインストールしてから再度実行するか、環境変数を確認してください。" -ForegroundColor Yellow
    }
} else {
    Write-Host "requirements.txt が見つかりませんでした（$requirementsPath）。スキップします。" -ForegroundColor Yellow
}
# --- 追加セクション：ここまで ---

Write-Host "セットアップ処理が終了しました。" -ForegroundColor Green
# pause