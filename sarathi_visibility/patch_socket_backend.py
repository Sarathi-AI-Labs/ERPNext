"""Route socket authentication inside Docker while retaining browser origin checks."""

from pathlib import Path

root = Path("/home/frappe/frappe-bench/apps/frappe/realtime")
patches = {
    root
    / "utils.js": [
        (
            "let url = socket.request.headers.origin;",
            "let url = process.env.SARATHI_SOCKET_BACKEND_URL || socket.request.headers.origin;",
        ),
        (
            "if (conf.developer_mode)",
            "if (conf.developer_mode && !process.env.SARATHI_SOCKET_BACKEND_URL)",
        ),
    ],
    root
    / "middlewares/authenticate.js": [
        (
            "let headers = {};",
            'let headers = { "Connection": "close" };\n\t\tif (process.env.SARATHI_SOCKET_BACKEND_URL) {\n\t\t\theaders["X-Frappe-Site-Name"] = socket.site_name;\n\t\t}',
        ),
    ],
}
for path, replacements in patches.items():
    source = path.read_text()
    for old, new in replacements:
        if source.count(old) != 1:
            raise RuntimeError(f"Frappe socket source changed: {path}: {old}")
        source = source.replace(old, new, 1)
    path.write_text(source)
