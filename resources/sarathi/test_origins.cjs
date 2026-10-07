// Execute the real shared browser URL logic under both origins without networking.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const root = path.resolve(__dirname, "../..");
const code = fs.readFileSync(
  path.join(
    root,
    "sarathi_owner/sarathi_owner/public/js/sarathi_module_browser.js"
  ),
  "utf8"
);

(async () => {
  for (const origin of [
    "http://localhost:8080",
    "https://erp.sarathiailabs.com",
  ]) {
    const frame = { addEventListener() {} };
    const context = {
      URL,
      location: { origin },
      frappe: {},
      document: { createElement: () => frame },
    };
    vm.runInNewContext(code, context);
    const browser = Object.create(
      context.frappe.SarathiModuleBrowser.prototype
    );
    browser.catalog = {
      modules: [
        {
          id: "invoicing",
          entries: [
            { id: "invoice", route: "/desk/sales-invoice", filters: {} },
          ],
        },
      ],
    };
    let selected;
    browser.open = async (module) => assert.equal(module, "invoicing");
    browser.selectEntry = (entry) => {
      selected = entry;
    };
    assert.equal(browser.openAction({ route: "/app/sales-invoice" }), true);
    await Promise.resolve();
    assert.equal(selected, "invoice");
    browser.detail = {
      entry: { route: "/desk/sales-invoice", label: "Sales Invoice" },
    };
    browser.name = "INV/2026 001";
    const host = {
      html() {},
      append() {},
      find: () => ({ on() {} }),
      0: { scrollIntoView() {} },
    };
    browser.host = { find: () => host };
    browser.openNative();
    assert.equal(new URL(frame.src, origin).origin, origin);
    assert.equal(frame.src, "/desk/sales-invoice/INV%2F2026%20001");
    console.log(`PASS shared dashboard routes: ${origin}`);
  }
  for (const file of [
    "sarathi_owner/sarathi_owner/public/js/sarathi_owner_dashboard.js",
    "sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js",
  ]) {
    assert.match(
      fs.readFileSync(path.join(root, file), "utf8"),
      /new frappe\.SarathiModuleBrowser\(this,/
    );
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
