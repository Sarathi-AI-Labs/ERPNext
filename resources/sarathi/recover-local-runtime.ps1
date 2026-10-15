# Restore the existing local Docker/ERPNext runtime after a WSL connection timeout.
# Run in an Administrator PowerShell. No image builds, volume deletion, or core edits.
[CmdletBinding()]
param(
    [string]$DockerDesktopPath = 'D:\Docker\DockerDesktop\Docker Desktop.exe',
    [string]$LogPath = ''
)

$ErrorActionPreference = 'Stop'
if ($LogPath) {
    Start-Transcript -Path $LogPath -Append | Out-Null
}
$principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Open PowerShell as Administrator and run this script again. Restarting WslService requires administrator rights.'
}
if (-not (Test-Path -LiteralPath $DockerDesktopPath -PathType Leaf)) {
    throw "Docker Desktop executable not found: $DockerDesktopPath. Pass -DockerDesktopPath with its installed location."
}

Get-Process -Name 'Docker Desktop', 'com.docker.backend', 'com.docker.build' -ErrorAction SilentlyContinue |
    Stop-Process -Force
Write-Host 'Restarting WSL service...'
$wslService = Get-Service -Name WslService
if ($wslService.Status -ne [ServiceProcess.ServiceControllerStatus]::Stopped) {
    if ($wslService.Status -ne [ServiceProcess.ServiceControllerStatus]::StopPending) {
        $wslService.Stop()
    }
    try {
        $wslService.WaitForStatus([ServiceProcess.ServiceControllerStatus]::Stopped, [TimeSpan]::FromSeconds(30))
    } catch {
        # A wedged service can remain StopPending indefinitely. Target only its
        # confirmed executable/PID, without terminating other VM services.
        $serviceInfo = Get-CimInstance Win32_Service -Filter "Name='WslService'"
        if ($serviceInfo.State -ne 'Stop Pending') { throw }
        $serviceProcess = Get-Process -Id $serviceInfo.ProcessId
        if ($serviceProcess.ProcessName -ne 'wslservice') {
            throw 'Unexpected WSL service executable. Recovery stopped.'
        }
        Write-Host 'Graceful WSL stop timed out; stopping its confirmed service process.'
        Stop-Process -Id $serviceProcess.Id -Force
        $wslService.WaitForStatus([ServiceProcess.ServiceControllerStatus]::Stopped, [TimeSpan]::FromSeconds(20))
    }
}
Start-Service -Name WslService
Start-Process -FilePath $DockerDesktopPath -WindowStyle Hidden

# Use a bounded subprocess: docker.exe can otherwise hang while WSL is starting.
function Invoke-DockerBounded {
    param([string[]]$Arguments, [int]$TimeoutSeconds = 15)
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = 'docker.exe'
    # All callers below pass fixed service names or simple CLI flags without spaces.
    $start.Arguments = $Arguments -join ' '
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    try {
        [void]$process.Start()
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            $process.Kill()
            $process.WaitForExit()
            return $false
        }
        $output = $stdout.GetAwaiter().GetResult()
        $errorOutput = $stderr.GetAwaiter().GetResult()
        # Docker Desktop may return success with an empty formatted server value
        # while its engine is unavailable. Require the actual server value too.
        if ($Arguments[0] -eq 'version') {
            return ($process.ExitCode -eq 0 -and -not [string]::IsNullOrWhiteSpace($output) -and [string]::IsNullOrWhiteSpace($errorOutput))
        }
        return ($process.ExitCode -eq 0)
    } finally {
        $process.Dispose()
    }
}

Write-Host 'Waiting for Docker engine...'
$deadline = [DateTime]::UtcNow.AddSeconds(120)
$ready = $false
while ([DateTime]::UtcNow -lt $deadline) {
    if (Invoke-DockerBounded -Arguments @('version', '--format', '{{.Server.Version}}') -TimeoutSeconds 5) {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 3
}
if (-not $ready) {
    throw 'Docker engine did not recover. Restart Windows, open Docker Desktop, and rerun this script. Do not reset Docker data.'
}

# Start only existing runtime containers; do not invoke configurator/create-site services.
$containers = @(
    'frappe_docker_main-db-1',
    'frappe_docker_main-redis-cache-1',
    'frappe_docker_main-redis-queue-1',
    'frappe_docker_main-backend-1',
    'frappe_docker_main-websocket-1',
    'frappe_docker_main-queue-short-1',
    'frappe_docker_main-queue-long-1',
    'frappe_docker_main-scheduler-1',
    'frappe_docker_main-frontend-1'
)
foreach ($container in $containers) {
    Write-Host "Starting $container..."
    if (-not (Invoke-DockerBounded -Arguments @('start', $container) -TimeoutSeconds 30)) {
        throw "Could not start existing container $container. Check Docker Desktop; no replacement or data reset was attempted."
    }
}

Write-Host 'Waiting for ERPNext HTTP response...'
$deadline = [DateTime]::UtcNow.AddSeconds(90)
while ([DateTime]::UtcNow -lt $deadline) {
    try {
        $response = Invoke-WebRequest -Uri 'http://localhost:8080/desk' -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host 'ERPNext responds successfully. Open http://localhost:8080/desk and sign in.'
            exit 0
        }
    } catch {
        # Containers may still be starting; retry only the read request.
    }
    Start-Sleep -Seconds 3
}
throw 'Docker recovered but ERPNext did not return HTTP 200. Inspect backend/frontend/database logs before making further changes.'
