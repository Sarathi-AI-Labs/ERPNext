# Local Docker/WSL startup failure — 13 October 2026

Status: unresolved pending a Windows restart. This is runtime recovery, not dashboard implementation.

## Observed evidence

- Docker Desktop initially could not communicate with WSL; `wsl --list --verbose` timed out, and Docker returned unable-to-start errors.
- Docker logs showed `HCS_E_CONNECTION_TIMEOUT` and failures reaching its Linux engine. ERPNext's nginx returned 504 before the engine stopped responding altogether.
- A normal Docker restart and `wsl --shutdown` initially failed/timed out. An administrator WSL service restart was stuck in Stop Pending; stopping the confirmed WSL service process restored WSL command responses.
- Subsequent Docker startup reported `ERROR_SHARING_VIOLATION` attaching the existing `D:\Docker\WSL\disk\docker_data.vhdx`. The disk exists (34,102,837,248 bytes); existence does not establish filesystem integrity or a backup.
- WSL shutdown subsequently returned success, but Windows compute inspection retained a VM in Unknown state and its old worker process. Targeted HCS termination did not clear the stale process/disk attachment. Targeted WSL disk detach returned file-not-found for the attachment; the disk file itself still exists.
- Administrator recovery stopped WSL and Windows compute services; compute remained Start Pending during the subsequent bounded observation. Docker/ERPNext recovery is not verified.

No volumes, distributions, disk files, images or ERPNext/Frappe source were deleted or recreated. No Docker factory reset, WSL unregister, migration, build or database initialization was performed. Administrator actions used Windows consent prompts.

## Next recovery step

1. Save work and use **Windows Start > Power > Restart**. A Windows restart is the next recovery step for the remaining stuck compute/VM state; it has not been performed by the agent.
2. Open Docker Desktop and wait for the engine to start.
3. Verify `wsl --list --verbose` and `docker version` return promptly and Docker reports a server version.
4. Start the existing ERPNext containers, without invoking create-site/configurator, rebuilding or deleting volumes. Verify database/backend/frontend health and `http://localhost:8080/desk` before claiming resolution.
5. If the disk sharing violation persists after reboot, investigate the lock owner and preserve/back up the existing VHD before considering additional changes. Do not use reset/unregister/delete as a shortcut.

The [recovery script](../resources/sarathi/recover-local-runtime.ps1) now bounds normal WSL service stopping and can target its confirmed process when stuck Stop Pending. Docker readiness requires a nonempty actual server version, rather than a successful client-only command. PowerShell syntax was checked; full successful recovery has not been demonstrated.

Ignored diagnostic output is in `scratch/docker-*.log*` and `scratch/docker-compute-detail.json`. Do not treat partial helper completion or service Running status alone as proof that Docker or ERPNext is healthy.

References: [Microsoft WSL shutdown/command documentation](https://learn.microsoft.com/en-us/windows/wsl/basic-commands) and [Docker's WSL backend documentation](https://docs.docker.com/desktop/features/wsl/).
