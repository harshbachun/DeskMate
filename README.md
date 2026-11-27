<div align="center">

<img src="docs/images/site-banner.svg" alt="DeskMate: turn an old Android phone into a desk panel for your Windows PC" width="100%">

<br>

[![Latest release](docs/images/badge-release.svg)](https://github.com/harshbachun/Deskmate/releases/latest)
![Windows 10/11](docs/images/badge-pc.svg)
![Android 5+](docs/images/badge-phone.svg)
[![MIT license](docs/images/badge-license.svg)](LICENSE)

<a href="https://github.com/harshbachun/Deskmate/releases/latest/download/DeskmateAgent.exe"><img alt="Download DeskmateAgent.exe" src="docs/images/download-button.svg"></a>

<br>

<img src="docs/images/hero.png" alt="DeskMate's VALORANT page on a phone: live match on Icebox, mic, save-clip and hold-to-talk buttons, and GPU stats" width="820">

</div>

<br>

<h2 align="center">Features</h2>
<p align="center">Everything your PC is doing, on a screen that sits next to your keyboard.</p>

<img src="docs/images/site-features.svg" alt="Live PC stats: CPU, GPU, RAM, network and temperatures. AI usage limits: Claude and Codex quotas with reset times. Discord voice: mute, deafen, hang up, see who's talking. VALORANT page: opens when the game starts, with save clip and hold to talk. Media and shortcuts: control music, launch apps, lock the PC. One download: the phone app, USB tool and temperature driver are built in." width="100%">

<br>

<h2 align="center">Install</h2>
<p align="center">Three steps, about two minutes. No other installs.</p>

<img src="docs/images/site-steps.svg" alt="Step 1: download and open DeskmateAgent.exe. Step 2: turn on USB debugging on the phone. Step 3: plug the phone in and allow USB debugging." width="100%">

<details>
<summary><b>Step by step</b></summary>

1. **Download and open [DeskmateAgent.exe](https://github.com/harshbachun/Deskmate/releases/latest/download/DeskmateAgent.exe).**
   It installs itself, starts with Windows, and puts an icon in the system tray.
2. **Turn on USB debugging on your phone.**
   Settings › About phone › Software information › tap **Build number** 7 times. Then Settings › Developer options › **USB debugging**.
3. **Plug the phone into the PC.**
   Accept *Allow USB debugging?* on the phone (tick *Always allow*). DeskMate installs the phone app and opens the panel.

To change the layout, pages, shortcuts and more, double-click the tray icon. It opens the settings page at http://127.0.0.1:8765.
</details>

<br>

<h2 align="center">Pages</h2>
<p align="center">Swipe between them on the phone, or pick which ones you want in the settings.</p>

| | |
|:---:|:---:|
| <img src="docs/images/home.png" alt="Home page"><br>**Home**: clock, weather, music, calendar, temperatures | <img src="docs/images/ai-quotas.png" alt="AI quotas page"><br>**AI quotas**: `Claude` and `Codex` limits, and when they reset |
| <img src="docs/images/system.png" alt="System page"><br>**System**: `CPU`, `GPU`, memory and network graphs | <img src="docs/images/processes.png" alt="Processes page"><br>**Processes**: what's using your PC; tap one to close it |
| <img src="docs/images/shortcuts.png" alt="Shortcuts page"><br>**Shortcuts**: one-tap apps, mute, screen off and lock | <img src="docs/images/discord.png" alt="Discord page"><br>**Discord**: voice controls, your servers, OBS scenes |
| <img src="docs/images/valorant.png" alt="VALORANT page"><br>**VALORANT**: live match, mic, save clip, hold to talk, `GPU` stats | <img src="docs/images/music.png" alt="Music page"><br>**Music**: big player controls for whatever is playing |
| <img src="docs/images/sessions.png" alt="Sessions page"><br>**Sessions**: your `Claude Code` and `Codex` sessions, and GitHub | |

<p align="center"><sub>The VALORANT, Shortcuts and Music screenshots are from a real PC; the others use made-up data.</sub></p>

<br>

<h2 align="center">Requirements</h2>

<table align="center">
<tr>
<td align="center" width="50%"><h3>PC</h3><code>Windows 10/11</code> · <code>64-bit</code><br><sub>Nothing else to install</sub></td>
<td align="center" width="50%"><h3>Phone</h3><code>Android 5.0</code> or later<br><sub>Any phone or tablet, plus a USB cable. Wi-Fi works after setup.</sub></td>
</tr>
</table>

<br>

<h2 align="center">FAQ</h2>

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

<br>

---

<p align="center">
<sub>DeskMate is based on <a href="https://github.com/ersinkoc/phonebox">PhoneBox</a> by Ersin Koç · <a href="LICENSE">MIT license</a> · <a href="agent/Deskmate.Agent/THIRD-PARTY-NOTICES.txt">Third-party notices</a> · <a href="BUILDING.md">Build it yourself</a></sub>
</p>
