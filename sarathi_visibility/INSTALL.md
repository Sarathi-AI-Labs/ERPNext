# Installing Sarathi Visibility With Frappe Docker

Build a custom ERPNext image that includes the dashboard app:

```sh
docker build -f sarathi_visibility/Containerfile `
  --build-arg ERPNEXT_VERSION=v16.33.0 `
  -t sarathi/erpnext-sarathi:v16.33.0 .
```

Use the custom image with the normal production Compose files from PowerShell:

```sh
$env:CUSTOM_IMAGE="sarathi/erpnext-sarathi"
$env:CUSTOM_TAG="v16.33.0"
docker compose --env-file example.env `
  -f compose.yaml `
  -f overrides/compose.mariadb.yaml `
  -f overrides/compose.redis.yaml `
  -f overrides/compose.noproxy.yaml `
  up -d
```

Install the app on the ERPNext site:

```sh
docker compose --env-file example.env `
  -f compose.yaml `
  -f overrides/compose.mariadb.yaml `
  -f overrides/compose.redis.yaml `
  -f overrides/compose.noproxy.yaml `
  exec backend bench --site <site-name> install-app sarathi_visibility
```

After install, open:

```text
/desk/sarathicontroltower
```

The local `pwd.yml` stack uses the same custom image for all Frappe services. Build it with the command above before starting that stack.

After source changes, rebuild the image and update the running local stack:

```powershell
docker compose -f pwd.yml up -d --no-deps backend frontend websocket queue-short queue-long scheduler
docker compose -f pwd.yml exec backend bench --site frontend migrate
docker compose -f pwd.yml exec backend bench --site frontend clear-cache
```

Reload the dashboard with Ctrl+Shift+R. The stylesheet is served at
`/assets/sarathi_visibility/css/sarathi_control_tower.css`.
The image copies the app's plain CSS and JavaScript into its assets directory;
these files do not require JavaScript bundling.

## Existing installations with the former app name

Back up the site before upgrading. The `setup/rename_legacy.py` migration
renames the existing DocTypes, module, workspace, role assignments and installed
app registration while retaining their data. Run its `execute` function while
the former package is still available, before replacing those containers with
the Sarathi image. The migration is also registered as a `before_migrate` hook
and can be rerun. Old names appear only in this migration to identify records
that need upgrading. ERPNext company and transaction names are business data
and are not changed by the app rename.
