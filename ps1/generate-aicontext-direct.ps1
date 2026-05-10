# powershell -ExecutionPolicy Bypass -File E:\git\igaponr\training\ps1\generate-aicontext-direct.ps1
# 1. スクリプトがあるフォルダのパスを取得
$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) {
    $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
}

# 2. パスの設定
$configFile = Join-Path $ScriptRoot "..\config\config.json"
$outputFile = Join-Path $ScriptRoot "ai_context_direct.md"

# 設定ファイルの存在確認
if (-not (Test-Path $configFile)) {
    Write-Error "Error: Configuration file not found at: $configFile"
    exit
}

# JSONの読み込み (ここでもUTF8を明示)
try {
    $jsonRaw = Get-Content $configFile -Raw -Encoding UTF8 -ErrorAction Stop
    $config = $jsonRaw | ConvertFrom-Json
} catch {
    Write-Error "Error: Failed to parse JSON. Path: $configFile"
    exit
}

# 出力ファイルを初期化 (BOM付きUTF8で作成される)
"" | Out-File -FilePath $outputFile -Encoding UTF8 -Force

Write-Host "--- Process Started (Direct Folder Only / UTF-8 Fix) ---" -ForegroundColor Cyan

foreach ($folderPath in $config.folders) {
    # 相対パスを絶対パスに変換
    $absoluteFolder = $folderPath
    if (-not [System.IO.Path]::IsPathRooted($folderPath)) {
        $absoluteFolder = [System.IO.Path]::GetFullPath((Join-Path $ScriptRoot $folderPath))
    }

    if (-not (Test-Path $absoluteFolder)) {
        Write-Warning "Folder not found: $absoluteFolder"
        continue
    }

    Write-Host "Scanning: $absoluteFolder" -ForegroundColor Yellow

    foreach ($ext in $config.extensions) {
        # フォルダ直下のファイルのみ取得
        $files = Get-ChildItem -Path $absoluteFolder -Filter "*$ext" -File -ErrorAction SilentlyContinue

        foreach ($file in $files) {
            Write-Host "  Adding: $($file.Name)"

            $fullPath = $file.FullName

            # 【重要】 -Encoding UTF8 を追加して文字化けを防止
            # PowerShell 5.1 はこれがないと Shift-JIS と判定して日本語が化けます
            $content = Get-Content $fullPath -Raw -Encoding UTF8 -ErrorAction SilentlyContinue

            if ($null -eq $content) { continue }

            $lang = $ext.Replace(".", "")
            $mdHeader = "`n---`n### File: $($fullPath)`n" + "``````$lang`n"
            $mdFooter = "`n``````"

            # 追記もすべてUTF8で統一
            $mdHeader | Out-File -FilePath $outputFile -Append -Encoding UTF8
            $content  | Out-File -FilePath $outputFile -Append -Encoding UTF8
            $mdFooter  | Out-File -FilePath $outputFile -Append -Encoding UTF8
        }
    }
}

Write-Host "`nSuccessfully completed!" -ForegroundColor Green
