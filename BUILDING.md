# Building Deskmate

Needs the .NET 10 SDK, JDK 17 and the Android SDK.

```powershell
$env:JAVA_HOME = '<path to JDK 17>'; $env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
.\build-release.ps1 -Signing <folder with signing.properties>   # → dist\DeskmateAgent.exe, dist\Deskmate-<version>.apk
```

- `signing.properties` holds `storeFile`, `storePassword`, `keyAlias` and `keyPassword` for the phone app's release key. Keep that folder out of the repo. The script refuses an APK that ended up debug-signed.
- The script downloads two things into `agent/Deskmate.Agent/bundle/` (ignored by git): adb (Google's platform-tools) and the PawnIO setup, whose signature it checks. It then builds both apps and embeds the phone app, adb and PawnIO in the exe.

## Layout

- **Phone app** (`android/`): a full-screen Android app, `app.deskmate.panel`. The panel itself is plain HTML/JS in `android/app/src/main/assets/www`.
- **PC app** (`agent/Deskmate.Agent`): a .NET 10 Windows tray app. It serves the phone over USB (`adb reverse`) or Wi-Fi (HTTPS, port 8766), and the settings page at http://127.0.0.1:8765.
  - `Installer.cs`: installs the exe on first run.
  - `SensorHost.cs`: the elevated CPU-temperature reader.
  - `UpdateService.cs`: installs the built-in APK on phones that have an older app.

## Releasing

1. Raise the version: `Version` in `agent/Deskmate.Agent/Deskmate.Agent.csproj`, and `versionName` and `versionCode` in `android/app/build.gradle.kts`.
2. Run `build-release.ps1`.
3. Set `RELEASE` in `tools/make_badges.py` and run `python tools/make_badges.py`, so the README's release button shows the new version.
4. Create a GitHub release and attach `dist\DeskmateAgent.exe`, the APK and `THIRD-PARTY-NOTICES.txt`.
