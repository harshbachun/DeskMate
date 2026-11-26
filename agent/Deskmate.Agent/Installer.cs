using System.Diagnostics;
using System.Windows.Forms;

namespace Deskmate.Agent;

/// <summary>
/// DeskmateAgent.exe is the whole download: opened from anywhere else (Downloads, a USB stick), it copies itself into
/// %LOCALAPPDATA%\Deskmate\app, adds Start menu and "start with Windows" shortcuts the first time, and starts that copy.
/// Opening a newer download later replaces the installed copy the same way (the running agent is closed first).
/// <c>--portable</c> runs the exe where it is, without installing.
/// </summary>
internal static class Installer
{
    private static string Target => Path.Combine(AppPaths.InstallDir, "DeskmateAgent.exe");

    private static readonly string StartMenuShortcut = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.Programs), AppPaths.AppName + ".lnk");

    public static bool ShouldInstall(string[] args)
    {
        if (!OperatingSystem.IsWindows() || !UpdateService.SingleFile) return false; // a build folder (dotnet run) never installs
        if (args.Contains("--portable") || args.Contains("--config") || args.Contains("--port") || args.Contains("--restart")) return false;
        return Environment.ProcessPath is { } exe
            && !string.Equals(Path.GetFullPath(exe), Path.GetFullPath(Target), StringComparison.OrdinalIgnoreCase);
    }

    public static void Run()
    {
        var source = Environment.ProcessPath!;
        var firstInstall = !File.Exists(Target);
        try
        {
            if (!firstInstall)
            {
                var installed = FileVersionInfo.GetVersionInfo(Target).ProductVersion?.Split('+')[0] ?? "?";
                var question = installed == AppPaths.Version
                    ? $"Deskmate {installed} is already installed. Reinstall it from this file?"
                    : $"Replace Deskmate {installed} with {AppPaths.Version}?";
                if (MessageBox.Show(question + "\n\nDeskmate will close and start again; your settings are kept.", "Deskmate",
                        MessageBoxButtons.OKCancel, MessageBoxIcon.Question) != DialogResult.OK) return;
                StopRunningAgents();
                // the sensor reader may still be running from the old file (elevated, so it can't be closed from
                // here); Windows lets a running exe be renamed, and the agent deletes *.old files later
                var old = Target + ".old";
                try { File.Delete(old); } catch { }
                File.Move(Target, old);
            }
            Directory.CreateDirectory(AppPaths.InstallDir);
            File.Copy(source, Target, true);
            if (firstInstall)
            {
                Shortcut(StartMenuShortcut);
                Shortcut(AppPaths.StartupShortcut);
            }
            Process.Start(new ProcessStartInfo(Target) { UseShellExecute = false, WorkingDirectory = AppPaths.InstallDir });
            if (firstInstall)
                MessageBox.Show("Deskmate is installed and running: look for its icon in the taskbar's notification area.\n\n" +
                    "Next: install the Deskmate app on your Android phone. Turn on USB debugging on the phone (Settings › " +
                    "Developer options), plug it in with USB and accept the prompt on the phone; Deskmate installs the app by itself.\n\n" +
                    "Deskmate starts with Windows. You can find it in the Start menu, too.", "Deskmate", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Deskmate could not be installed: " + ex.Message + "\n\nTo run it without installing, start it with --portable.",
                "Deskmate", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }
    }

    /// <summary>Closes agents running from the install folder (not the elevated sensor reader, which quits by itself).</summary>
    private static void StopRunningAgents()
    {
        foreach (var p in Process.GetProcessesByName("DeskmateAgent"))
        {
            using (p)
            {
                if (p.Id == Environment.ProcessId) continue;
                try
                {
                    if (!string.Equals(p.MainModule?.FileName, Target, StringComparison.OrdinalIgnoreCase)) continue;
                    p.Kill();
                    p.WaitForExit(10_000);
                }
                catch { } // elevated (the sensor reader) or already gone
            }
        }
    }

    private static void Shortcut(string path)
    {
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            var shellType = Type.GetTypeFromProgID("WScript.Shell")!;
            dynamic shell = Activator.CreateInstance(shellType)!;
            dynamic lnk = shell.CreateShortcut(path);
            lnk.TargetPath = Target;
            lnk.WorkingDirectory = AppPaths.InstallDir;
            lnk.Description = "Deskmate";
            lnk.Save();
        }
        catch { } // a missing shortcut is not worth failing the install over
    }
}
