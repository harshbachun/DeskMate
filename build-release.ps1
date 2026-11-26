# Builds the release: dist/DeskmateAgent.exe (everything built in) and dist/Deskmate-<version>.apk.
#
#   .\build-release.ps1 -Signing <folder with signing.properties>
#
# signing.properties (kept outside the repo) holds storeFile, storePassword, keyAlias, keyPassword for the phone app's
# release key. Needs: .NET 10 SDK, JDK 17 (JAVA_HOME) and the Android SDK (ANDROID_HOME).
# Downloads into agent/Deskmate.Agent/bundle (ignored by git): Google's adb (platform-tools) and the PawnIO setup.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Signing,
    [switch]$SkipApk
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$bundle = Join-Path $root 'agent/Deskmate.Agent/bundle'
$dist = Join-Path $root 'dist'
New-Item -ItemType Directory -Force (Join-Path $bundle 'adb'), $dist | Out-Null

# --- adb (USB link) --------------------------------------------------------------------------------------------------
$adbDir = Join-Path $bundle 'adb'
if (-not (Test-Path (Join-Path $adbDir 'adb.exe'))) {
    $zip = Join-Path $env:TEMP 'deskmate-platform-tools.zip'
    $tmp = Join-Path $env:TEMP 'deskmate-platform-tools'
    Invoke-WebRequest -UseBasicParsing 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip' -OutFile $zip
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    Expand-Archive $zip $tmp
    foreach ($f in 'adb.exe', 'AdbWinApi.dll', 'AdbWinUsbApi.dll', 'NOTICE.txt') {
        Copy-Item (Join-Path $tmp "platform-tools/$f") (Join-Path $adbDir $f)
    }
    Move-Item -Force (Join-Path $adbDir 'NOTICE.txt') (Join-Path $bundle 'adb-NOTICE.txt')
    Remove-Item -Recurse -Force $tmp, $zip
}

# --- PawnIO (CPU temperature driver) ---------------------------------------------------------------------------------
$pawn = Join-Path $bundle 'PawnIO_setup.exe'
if (-not (Test-Path $pawn)) {
    Invoke-WebRequest -UseBasicParsing 'https://github.com/namazso/PawnIO.Setup/releases/latest/download/PawnIO_setup.exe' -OutFile $pawn
}
$sig = Get-AuthenticodeSignature $pawn
if ($sig.Status -ne 'Valid') { throw "PawnIO_setup.exe is not validly signed ($($sig.Status))." }

# --- phone app ---------------------------------------------------------------------------------------------------------
$Signing = (Resolve-Path $Signing).Path
$props = @{}
Get-Content (Join-Path $Signing 'signing.properties') | Where-Object { $_ -match '^\s*([^#=]+?)\s*=\s*(.*)$' } |
    ForEach-Object { $props[$Matches[1]] = $Matches[2] }
$store = $props.storeFile
if (-not [IO.Path]::IsPathRooted($store)) { $store = Join-Path $Signing $store }
if (-not (Test-Path $store)) { throw "Signing key not found: $store" }
$version = (Select-String -Path (Join-Path $root 'android/app/build.gradle.kts') -Pattern 'versionName\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value
$apkOut = Join-Path $root 'android/app/build/outputs/apk/release/app-release.apk'
if (-not $SkipApk) {
    $env:DESKMATE_STORE_FILE = $store
    $env:DESKMATE_STORE_PASSWORD = $props.storePassword
    $env:DESKMATE_KEY_ALIAS = $props.keyAlias
    $env:DESKMATE_KEY_PASSWORD = $props.keyPassword
    try {
        Push-Location (Join-Path $root 'android')
        & .\gradlew.bat assembleRelease --console=plain
        if ($LASTEXITCODE) { throw 'The phone app build failed.' }
    } finally {
        Pop-Location
        'DESKMATE_STORE_FILE', 'DESKMATE_STORE_PASSWORD', 'DESKMATE_KEY_ALIAS', 'DESKMATE_KEY_PASSWORD' |
            ForEach-Object { Remove-Item "env:$_" -ErrorAction SilentlyContinue }
    }
}
# the Gradle build quietly falls back to the debug key when it can't use the release key: refuse that APK
$buildTools = Get-ChildItem (Join-Path $env:ANDROID_HOME 'build-tools') -Directory | Sort-Object { [version]($_.Name -replace '-.*') } | Select-Object -Last 1
$certs = & (Join-Path $buildTools.FullName 'apksigner.bat') verify --print-certs $apkOut
if ($LASTEXITCODE -or ($certs -match 'CN=Android Debug')) { throw 'The phone app is not signed with the release key.' }
Copy-Item $apkOut (Join-Path $bundle 'Deskmate.apk') -Force
Copy-Item $apkOut (Join-Path $dist "Deskmate-$version.apk") -Force

# --- PC app ------------------------------------------------------------------------------------------------------------
dotnet publish (Join-Path $root 'agent/Deskmate.Agent') -c Release -r win-x64 --self-contained true `
    -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -p:EnableCompressionInSingleFile=true `
    -p:DebugType=none -o (Join-Path $root 'agent/publish')
if ($LASTEXITCODE) { throw 'The PC app build failed.' }
Copy-Item (Join-Path $root 'agent/publish/DeskmateAgent.exe') (Join-Path $dist 'DeskmateAgent.exe') -Force

Get-ChildItem $dist | ForEach-Object { '{0,-28} {1,8:N1} MB  {2}' -f $_.Name, ($_.Length / 1MB), (Get-FileHash $_.FullName).Hash }
