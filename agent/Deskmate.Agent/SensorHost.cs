using System.Diagnostics;
using System.Security.Principal;
using System.Text;
using System.Text.Json;
using LibreHardwareMonitor.Hardware;
using Microsoft.Win32;

namespace Deskmate.Agent;

/// <summary>
/// CPU temperature (and the GPU's extra sensors) without a separate program. Reading them needs the PawnIO driver and
/// admin rights, so the agent stays an ordinary process and a second copy of DeskmateAgent.exe does the reading:
/// <list type="bullet">
/// <item><c>--setup-sensors</c> (run elevated once, from the tray or the first-run question): installs the PawnIO driver
/// that is built into the exe and registers the scheduled task <see cref="TaskName"/> with the highest privileges.</item>
/// <item><c>--sensors</c> (started by that task, so no UAC prompt): reads the sensors with LibreHardwareMonitorLib every
/// 2 s and writes them to <see cref="DataPath"/> in LibreHardwareMonitor's own data.json layout, which
/// <see cref="SystemMonitor"/> already reads. It quits when the agent is gone.</item>
/// </list>
/// </summary>
internal static class SensorHost
{
    public const string TaskName = "Deskmate sensors";
    public static readonly string DataPath = Path.Combine(AppPaths.LocalDir, "sensors.json");
    private const string HelperMutex = @"Local\Deskmate.Sensors";
    private const string AgentMutex = @"Local\Deskmate.Agent";
    /// <summary>Marks that the first-run question was answered, either way.</summary>
    public static readonly string AskedMarker = Path.Combine(AppPaths.LocalDir, "sensors.asked");

    public static bool IsAdmin
    {
        get
        {
            using var id = WindowsIdentity.GetCurrent();
            return new WindowsPrincipal(id).IsInRole(WindowsBuiltInRole.Administrator);
        }
    }

    public static bool DriverInstalled
    {
        get
        {
            using var key = Registry.LocalMachine.OpenSubKey(@"SYSTEM\CurrentControlSet\Services\PawnIO");
            return key is not null;
        }
    }

    public static bool TaskInstalled => Schtasks($"/Query /TN \"{TaskName}\"").Exit == 0;

    /// <summary>Set up and working: the task exists and points at this exe.</summary>
    public static bool Enabled
    {
        get
        {
            var (exit, output) = Schtasks($"/Query /TN \"{TaskName}\" /XML");
            return exit == 0 && Environment.ProcessPath is { } exe && output.Contains(exe, StringComparison.OrdinalIgnoreCase);
        }
    }

    /// <summary>Asks Task Scheduler to start the helper; the task runs elevated without a prompt.</summary>
    public static void StartHelper()
    {
        if (!OperatingSystem.IsWindows()) return;
        try { Schtasks($"/Run /TN \"{TaskName}\""); } catch { }
    }

    /// <summary>Runs this exe with <c>--setup-sensors</c> through UAC. False when the user declined the prompt.</summary>
    public static bool RequestSetup()
    {
        try
        {
            using var p = Process.Start(new ProcessStartInfo(Environment.ProcessPath!, "--setup-sensors") { UseShellExecute = true, Verb = "runas" });
            p?.WaitForExit();
            return p?.ExitCode == 0;
        }
        catch (System.ComponentModel.Win32Exception) { return false; } // the UAC prompt was cancelled
    }

    /// <summary>The elevated one-time setup: driver, then the task. Exit code 0 on success.</summary>
    public static int Setup()
    {
        try
        {
            if (!IsAdmin) { Show("Setting up CPU temperature needs administrator rights."); return 2; }
            if (!DriverInstalled)
            {
                using var src = AppPaths.Resource("PawnIO_setup.exe");
                if (src is null) { Show("This build of Deskmate does not include the PawnIO driver."); return 3; }
                var setup = Path.Combine(Path.GetTempPath(), "Deskmate-PawnIO_setup.exe");
                using (var dst = File.Create(setup)) src.CopyTo(dst);
                using (var p = Process.Start(new ProcessStartInfo(setup, "-install -silent") { UseShellExecute = false, CreateNoWindow = true })!)
                {
                    p.WaitForExit();
                    if (p.ExitCode != 0 && !DriverInstalled) { Show($"The PawnIO driver did not install (exit code {p.ExitCode})."); return 4; }
                }
                try { File.Delete(setup); } catch { }
            }
            var xml = Path.Combine(Path.GetTempPath(), "Deskmate-sensors-task.xml");
            File.WriteAllText(xml, TaskXml(Environment.ProcessPath!), Encoding.Unicode);
            var (exit, output) = Schtasks($"/Create /TN \"{TaskName}\" /XML \"{xml}\" /F");
            try { File.Delete(xml); } catch { }
            if (exit != 0) { Show("Could not register the sensor task: " + output.Trim()); return 5; }
            return 0;
        }
        catch (Exception ex)
        {
            Show("Setting up CPU temperature failed: " + ex.Message);
            return 1;
        }
    }

    /// <summary>Elevated reverse of <see cref="Setup"/> for the task; the driver stays (other programs may use it).</summary>
    public static int Remove()
    {
        Schtasks($"/End /TN \"{TaskName}\"");
        return Schtasks($"/Delete /TN \"{TaskName}\" /F").Exit;
    }

    private static string TaskXml(string exe)
    {
        using var id = WindowsIdentity.GetCurrent();
        static string Esc(string s) => System.Security.SecurityElement.Escape(s);
        return $"""
            <?xml version="1.0" encoding="UTF-16"?>
            <Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
              <RegistrationInfo><Description>Reads CPU and GPU sensors for Deskmate. Started by DeskmateAgent.exe; quits when it does.</Description></RegistrationInfo>
              <Principals>
                <Principal id="Author">
                  <UserId>{Esc(id.User!.Value)}</UserId>
                  <LogonType>InteractiveToken</LogonType>
                  <RunLevel>HighestAvailable</RunLevel>
                </Principal>
              </Principals>
              <Settings>
                <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
                <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
                <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
                <AllowHardTerminate>true</AllowHardTerminate>
                <StartWhenAvailable>false</StartWhenAvailable>
                <IdleSettings><StopOnIdleEnd>false</StopOnIdleEnd><RestartOnIdle>false</RestartOnIdle></IdleSettings>
                <AllowStartOnDemand>true</AllowStartOnDemand>
                <Enabled>true</Enabled>
                <Hidden>false</Hidden>
                <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
                <Priority>7</Priority>
              </Settings>
              <Actions Context="Author">
                <Exec><Command>{Esc(exe)}</Command><Arguments>--sensors</Arguments></Exec>
              </Actions>
            </Task>
            """;
    }

    /// <summary>The helper itself (<c>--sensors</c>): reads every 2 s until the agent quits.</summary>
    public static int RunHelper()
    {
        using var single = new Mutex(false, HelperMutex);
        bool mine;
        try { mine = single.WaitOne(0); } catch (AbandonedMutexException) { mine = true; }
        if (!mine) return 0;
        Directory.CreateDirectory(AppPaths.LocalDir);
        var computer = new Computer { IsCpuEnabled = true, IsGpuEnabled = true };
        try
        {
            computer.Open();
            var missing = 0;
            while (true)
            {
                foreach (var hw in computer.Hardware) Update(hw);
                Write(computer);
                // the agent's single-instance mutex: gone for ~10 s means the agent quit (not just restarting)
                if (Mutex.TryOpenExisting(AgentMutex, out var m)) { m.Dispose(); missing = 0; }
                else if (++missing >= 5) break;
                Thread.Sleep(2000);
            }
        }
        finally
        {
            computer.Close();
            try { File.Delete(DataPath); } catch { }
        }
        return 0;
    }

    private static void Update(IHardware hw)
    {
        hw.Update();
        foreach (var sub in hw.SubHardware) Update(sub);
    }

    /// <summary>LibreHardwareMonitor's data.json shape: hardware → sensor-type groups → sensors with formatted values.</summary>
    private static void Write(Computer computer)
    {
        var tmp = DataPath + ".tmp";
        using (var stream = File.Create(tmp))
        using (var w = new Utf8JsonWriter(stream))
        {
            w.WriteStartObject();
            w.WriteString("Text", "Sensor");
            w.WriteStartArray("Children");
            foreach (var hw in computer.Hardware) WriteHardware(w, hw);
            w.WriteEndArray();
            w.WriteEndObject();
        }
        File.Move(tmp, DataPath, true);
    }

    private static void WriteHardware(Utf8JsonWriter w, IHardware hw)
    {
        w.WriteStartObject();
        w.WriteString("Text", hw.Name);
        w.WriteString("HardwareId", hw.Identifier.ToString());
        w.WriteStartArray("Children");
        foreach (var sub in hw.SubHardware) WriteHardware(w, sub);
        foreach (var group in hw.Sensors.Where(s => s.Value is not null && Unit(s.SensorType) is not null).GroupBy(s => s.SensorType))
        {
            w.WriteStartObject();
            w.WriteString("Text", GroupName(group.Key));
            w.WriteStartArray("Children");
            foreach (var s in group)
            {
                w.WriteStartObject();
                w.WriteString("Text", s.Name);
                w.WriteString("Value", s.Value!.Value.ToString("0.0", System.Globalization.CultureInfo.InvariantCulture) + " " + Unit(s.SensorType));
                w.WriteString("Type", s.SensorType.ToString());
                w.WriteString("SensorId", s.Identifier.ToString());
                w.WriteEndObject();
            }
            w.WriteEndArray();
            w.WriteEndObject();
        }
        w.WriteEndArray();
        w.WriteEndObject();
    }

    private static string? Unit(SensorType t) => t switch
    {
        SensorType.Temperature => "°C",
        SensorType.Load or SensorType.Control => "%",
        SensorType.Clock => "MHz",
        SensorType.Power => "W",
        SensorType.Fan => "RPM",
        SensorType.Data => "GB",
        SensorType.SmallData => "MB",
        _ => null,
    };

    private static string GroupName(SensorType t) => t switch
    {
        SensorType.Temperature => "Temperatures",
        SensorType.Clock => "Clocks",
        SensorType.Power => "Powers",
        SensorType.Fan => "Fans",
        SensorType.Control => "Controls",
        SensorType.SmallData => "Data",
        _ => t.ToString(),
    };

    private static (int Exit, string Output) Schtasks(string args)
    {
        var psi = new ProcessStartInfo("schtasks.exe", args)
        {
            UseShellExecute = false, CreateNoWindow = true, RedirectStandardOutput = true, RedirectStandardError = true,
        };
        using var p = Process.Start(psi)!;
        var stdout = p.StandardOutput.ReadToEndAsync();
        var stderr = p.StandardError.ReadToEnd();
        p.WaitForExit(15_000);
        return (p.HasExited ? p.ExitCode : -1, stdout.Result + stderr);
    }

    private static void Show(string message) =>
        System.Windows.Forms.MessageBox.Show(message, "Deskmate", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Warning);
}
