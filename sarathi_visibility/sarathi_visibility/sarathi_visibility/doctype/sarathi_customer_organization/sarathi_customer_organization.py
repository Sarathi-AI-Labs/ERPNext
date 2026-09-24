import hashlib

import frappe
from frappe.model.document import Document


class SarathiCustomerOrganization(Document):
    def autoname(self):
        self.name = hashlib.sha256(
            (self.company + "\n" + self.customer).encode()
        ).hexdigest()[:32]

    def validate(self):
        for dt, name in (("Company", self.company), ("Customer", self.customer)):
            frappe.get_doc(dt, name).check_permission("read")
        existing = frappe.db.exists(
            self.doctype,
            {
                "company": self.company,
                "customer": self.customer,
                "name": ["!=", self.name or ""],
            },
        )
        if existing:
            frappe.throw("This customer is already associated with this organization.")
