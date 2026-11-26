# Deskmate

Turn an old Android phone into a desk panel for your Windows PC: CPU, GPU and RAM, your AI usage limits, Discord voice controls, a VALORANT match page, media controls, shortcut keys and more.

Deskmate has two parts:

- **DeskmateAgent.exe**, the PC app. It is the only thing you download. It runs in the system tray and has everything built in: the phone app, the USB connection tool (adb) and the CPU temperature driver. You don't need to install anything else.
- **The Deskmate phone app** (Android 5 or later). The PC app installs it on your phone over USB.

## Install

1. Download **DeskmateAgent.exe** from the [latest release](https://github.com/harshbachun/Deskmate/releases/latest) and open it.
   Windows SmartScreen may say it "protected your PC", because the file isn't code-signed. Click **More info › Run anyway**.
   Deskmate installs itself into `%LOCALAPPDATA%\Deskmate`, starts with Windows, and shows its icon in the tray.
2. On the phone, turn on **Developer options**: Settings › About phone › Software information, then tap **Build number** 7 times. Then turn on **USB debugging** in Settings › Developer options.
3. Plug the phone into the PC with USB and accept the **Allow USB debugging?** prompt on the phone (tick *Always allow*).
   Deskmate installs the phone app and opens the panel.
4. When Deskmate asks *Show your CPU temperature?*, click **Yes** and accept the Windows admin prompt. This sets up the PawnIO sensor driver once. You can also do it later from the tray icon.

Open **Settings** (double-click the tray icon, or go to http://127.0.0.1:8765) to edit pages, shortcuts, Discord, Wi-Fi pairing and so on.

**Wi-Fi instead of USB:** Settings › General › Wi-Fi › **Pair a phone over Wi-Fi**, and scan the QR code with the phone. Windows Firewall asks once; allow Deskmate on **Private** networks.

**Updating:** download the new DeskmateAgent.exe and open it. Your settings are kept. The next time the phone is on USB, it gets the matching phone app.

**Uninstalling:** tray icon › Quit. Then delete `%LOCALAPPDATA%\Deskmate`, `%APPDATA%\Deskmate` (your settings) and the Deskmate shortcuts in the Start menu and the Startup folder. Uninstall the phone app as usual. If you set up CPU temperature, also run `schtasks /Delete /TN "Deskmate sensors" /F` from an admin terminal, and remove PawnIO from Installed apps if nothing else uses it.

## Build from source

Needs the .NET 10 SDK, JDK 17 and the Android SDK.

```powershell
$env:JAVA_HOME = '<path to JDK 17>'; $env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
.\build-release.ps1 -Signing <folder with signing.properties>   # → dist\DeskmateAgent.exe, dist\Deskmate-<version>.apk
```

`signing.properties` holds `storeFile`, `storePassword`, `keyAlias` and `keyPassword` for the phone app's release key. Keep that folder out of the repo. The script downloads adb (Google's platform-tools) and the PawnIO setup into `agent/Deskmate.Agent/bundle/`, then builds both apps.

- Phone app: `android/`. The panel itself is plain HTML/JS in `android/app/src/main/assets/www`.
- PC app: `agent/Deskmate.Agent`, a .NET 10 Windows tray app. It serves the phone over USB (`adb reverse`) or Wi-Fi (HTTPS, port 8766), and the settings page at http://127.0.0.1:8765.

## Credit

Deskmate is based on [PhoneBox](https://github.com/ersinkoc/phonebox) by Ersin Koç (MIT license, see [LICENSE](LICENSE)). Third-party components in the PC app are listed in [THIRD-PARTY-NOTICES.txt](agent/Deskmate.Agent/THIRD-PARTY-NOTICES.txt).
