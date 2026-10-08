#!/usr/bin/env bash
# Existing VPS/site deployment. Uses its current Compose project/volumes.
set -Eeuo pipefail
cd "$(dirname "$0")/../.."
proxy_override="${SARATHI_PROXY_OVERRIDE:-overrides/compose.existing-traefik.yaml}"
compose=(docker compose --env-file "${SARATHI_ENV_FILE:-.env}"
  -f compose.yaml -f overrides/compose.mariadb.yaml -f overrides/compose.redis.yaml
  -f overrides/compose.sarathi-production.yaml -f "$proxy_override")
"${compose[@]}" config --quiet
site=$("${compose[@]}" config --format json | python3 -c 'import sys,json; print(json.load(sys.stdin)["services"]["frontend"]["environment"]["FRAPPE_SITE_NAME_HEADER"])')
base_url=$("${compose[@]}" config --format json | python3 -c 'import sys,json; from resources.sarathi.environments import origin; print(origin(json.load(sys.stdin)["services"]["backend"]["environment"]["SARATHI_BASE_URL"]))')
[[ "$base_url" == https://* ]] || { echo 'Production base URL must use HTTPS.' >&2; exit 1; }
state=".sarathi-deploy/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$state"
chmod 700 .sarathi-deploy "$state"
umask 077
# Fail before changing services if the existing site/backend cannot be reached.
"${compose[@]}" exec -T backend bench --site "$site" list-apps --format json > "$state/apps-before.json"
old_container=$("${compose[@]}" ps -q backend)
docker inspect --format '{{.Image}}' "$old_container" > "$state/image-before.txt"
# Build with no source/asset mounts; both apps and their assets are baked in.
"${compose[@]}" build backend
"${compose[@]}" exec -T backend bench --site "$site" set-maintenance-mode on
trap 'echo "Deployment stopped. Maintenance remains enabled; inspect migration logs and use the saved backup/image before resuming. State: $state" >&2' ERR
"${compose[@]}" stop scheduler queue-short queue-long
"${compose[@]}" exec -T backend bench --site "$site" backup --with-files
"${compose[@]}" run --rm --no-deps configurator
"${compose[@]}" up -d --no-deps backend websocket
installed=$("${compose[@]}" exec -T backend bench --site "$site" list-apps --format json)
for app in sarathi_visibility sarathi_owner; do
  if ! printf '%s' "$installed" | python3 -c 'import json,sys; sys.exit(0 if sys.argv[1] in json.load(sys.stdin)[sys.argv[2]] else 1)' "$app" "$site"; then
    "${compose[@]}" exec -T backend bench --site "$site" install-app "$app"
  fi
done
"${compose[@]}" exec -T backend bench --site "$site" set-config host_name "$base_url"
"${compose[@]}" exec -T backend bench --site "$site" migrate
"${compose[@]}" exec -T backend bench --site "$site" clear-cache
"${compose[@]}" exec -T backend bench --site "$site" execute sarathi_owner.api.module_catalog.inventory > "$state/metadata-after.json"
"${compose[@]}" up -d --no-deps frontend queue-short queue-long scheduler
# Re-resolve backend/websocket addresses even if the proxy container was reused.
"${compose[@]}" exec -T frontend nginx -s reload
"${compose[@]}" exec -T backend bench --site "$site" set-maintenance-mode off
trap - ERR
echo "Both Sarathi dashboards deployed for $base_url. Metadata audit: $state/metadata-after.json"
echo 'Run the authenticated production browser smoke check to verify both dashboards.'
