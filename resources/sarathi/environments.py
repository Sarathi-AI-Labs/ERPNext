"""Explicit targets for tooling; dashboard runtime uses the current browser origin."""
import os
from urllib.parse import urlsplit

ENVIRONMENTS = {
	"local": {"url": "http://localhost:8080", "site": "frontend"},
	"production": {"url": "https://erp.sarathiailabs.com", "site": "erp.sarathiailabs.com"},
}


def origin(value):
	parsed = urlsplit(value)
	if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
		raise ValueError("Use an http(s) site URL without credentials.")
	if parsed.path not in ("", "/", "/desk", "/desk/") or parsed.query or parsed.fragment:
		raise ValueError("Use the site origin or its /desk/ URL.")
	return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def resolve(environment="local", url=None, site=None):
	profile = ENVIRONMENTS[environment]
	base = origin(url or os.environ.get("SARATHI_BASE_URL") or profile["url"])
	if environment == "production" and urlsplit(base).scheme != "https":
		raise ValueError("Production requires HTTPS.")
	return {"url": base, "site": site or os.environ.get("SARATHI_SITE") or profile["site"]}
