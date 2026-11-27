<div align="center">

# DeskMate

**Turn an old Android phone into a desk panel for your Windows PC.**

[![Latest release](docs/images/badge-release.svg)](https://github.com/harshbachun/Deskmate/releases/latest)
![Windows 10/11](docs/images/badge-pc.svg)
![Android 5+](docs/images/badge-phone.svg)
[![MIT license](docs/images/badge-license.svg)](LICENSE)

<a href="https://github.com/harshbachun/Deskmate/releases/latest/download/DeskmateAgent.exe"><img alt="Download DeskmateAgent.exe" src="docs/images/download-button.svg"></a>

<img src="docs/images/hero.png" alt="DeskMate's VALORANT page on a phone: live match on Icebox, mic, save-clip and hold-to-talk buttons, and GPU stats" width="820">

</div>

## What it does

- **Live PC stats:** `CPU`, `GPU`, `RAM`, network, temperatures and the processes using the most.
- **AI usage limits:** your `Claude` and `Codex` quotas as bars, with reset times.
- **Discord voice:** mute, deafen and hang up, see who's talking, jump between your favourite servers.
- **VALORANT page:** opens by itself when the game starts. Shows the match, has buttons to save a clip and hold to talk, and lists your stats.
- **Media and shortcuts:** control any music player, and launch apps or lock the PC with one tap.

The phone connects over **USB or Wi-Fi**. You only download **one file**: the PC app has the phone app, the USB tool and the temperature driver built in.

## Install in 3 steps

1. **Download and open [DeskmateAgent.exe](https://github.com/harshbachun/Deskmate/releases/latest/download/DeskmateAgent.exe).**
   It installs itself, starts with Windows, and puts an icon in the system tray.
2. **Turn on USB debugging on your phone.**
   Settings › About phone › Software information › tap **Build number** 7 times. Then Settings › Developer options › **USB debugging**.
3. **Plug the phone into the PC.**
   Accept *Allow USB debugging?* on the phone (tick *Always allow*). DeskMate installs the phone app and opens the panel.

To change the layout, pages, shortcuts and more, double-click the tray icon. It opens the settings page at http://127.0.0.1:8765.

## Pages

| | |
|:---:|:---:|
| <img src="docs/images/home.png" alt="Home page"><br>**Home**: clock, weather, music, calendar, temperatures | <img src="docs/images/ai-quotas.png" alt="AI quotas page"><br>**AI quotas**: `Claude` and `Codex` limits, and when they reset |
| <img src="docs/images/system.png" alt="System page"><br>**System**: `CPU`, `GPU`, memory and network graphs | <img src="docs/images/processes.png" alt="Processes page"><br>**Processes**: what's using your PC; tap one to close it |
| <img src="docs/images/shortcuts.png" alt="Shortcuts page"><br>**Shortcuts**: one-tap apps, mute, screen off and lock | <img src="docs/images/discord.png" alt="Discord page"><br>**Discord**: voice controls, your servers, OBS scenes |
| <img src="docs/images/valorant.png" alt="VALORANT page"><br>**VALORANT**: live match, mic, save clip, hold to talk, `GPU` stats | <img src="docs/images/music.png" alt="Music page"><br>**Music**: big player controls for whatever is playing |
| <img src="docs/images/sessions.png" alt="Sessions page"><br>**Sessions**: your `Claude Code` and `Codex` sessions, and GitHub | |

*The VALORANT, Shortcuts and Music screenshots are from a real PC; the others use made-up data.*

## Requirements

- **PC:** `Windows 10/11` (`64-bit`).
- **Phone:** any Android phone or tablet with `Android 5.0` or later, and a USB cable. After setup you can use Wi-Fi instead.

## FAQ

<details>
<summary><b>Windows says "Windows protected your PC"</b></summary>

The exe isn't code-signed, so SmartScreen warns about it. Click **More info › Run anyway**.
</details>

<details>
<summary><b>The phone app didn't install</b></summary>

- Check that **USB debugging** is on, and that you accepted the prompt on the phone.
- Try another cable or port; some cables only charge.
- On the phone, set the USB mode to **File transfer**.
- Settings › General › **Install the phone app** tries again.
</details>

<details>
<summary><b><code>CPU</code> temperature doesn't show</b></summary>

Reading it needs a small sensor driver (PawnIO), which is built into DeskMate. Tray icon › **Set up CPU temperature…** then click **Yes** on the Windows admin prompt. You only do this once.
</details>

<details>
<summary><b>Can I use Wi-Fi instead of USB?</b></summary>

Yes. Go to Settings › General › Wi-Fi › **Pair a phone over Wi-Fi**, and scan the QR code with the phone. When Windows Firewall asks, allow DeskMate on **Private** networks. The PC and the phone must be on the same network.
</details>

<details>
<summary><b>How do I set up Discord?</b></summary>

DeskMate talks to the Discord app on your PC. Send your Discord username to whoever shared DeskMate with you so they can add you to DeskMate's tester list, accept the invite, then turn on **Settings › General › Discord › Connect to Discord** and click **Authorize** in Discord. Details: [docs/DISCORD.md](docs/DISCORD.md).
</details>

<details>
<summary><b>How do I update?</b></summary>

Download the new DeskmateAgent.exe and open it. Your settings are kept. The next time the phone is plugged in, it gets the matching phone app.
</details>

<details>
<summary><b>How do I uninstall?</b></summary>

1. Tray icon › **Quit**.
2. Delete `%LOCALAPPDATA%\Deskmate` and `%APPDATA%\Deskmate` (your settings).
3. Delete the DeskMate shortcuts in the Start menu and the Startup folder.
4. Uninstall the app on the phone.
5. If you set up `CPU` temperature, also run `schtasks /Delete /TN "Deskmate sensors" /F` in an admin terminal. Remove **PawnIO** from Installed apps if nothing else uses it.
</details>

<details>
<summary><b>Does it send my data anywhere?</b></summary>

No. DeskMate has no account and no server of its own: the phone talks only to your PC. A few optional widgets fetch public data, such as the weather. See [PRIVACY.md](PRIVACY.md).
</details>

## Credits

DeskMate is based on [PhoneBox](https://github.com/ersinkoc/phonebox) by Ersin Koç (MIT, see [LICENSE](LICENSE)). The third-party parts are listed in [THIRD-PARTY-NOTICES.txt](agent/Deskmate.Agent/THIRD-PARTY-NOTICES.txt). Want to build it yourself? See [BUILDING.md](BUILDING.md).
