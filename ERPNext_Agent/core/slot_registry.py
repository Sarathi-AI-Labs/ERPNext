"""Dynamic Live Metadata Slot Engine for Sarathi ERPNext AI Agent.

Discovers and constructs interactive slot intake schemas, dropdown options, and field definitions
100% dynamically from live ERPNext system metadata (frappe.get_meta).
Zero hardcoded module schemas: all field definitions, mandatory constraints (*),
live Select options, and live Link targets (currencies, countries, companies, UOMs)
are queried directly from the running ERPNext instance at runtime.
"""

import re
from typing import Any, Dict, List, Optional, Set

from ERPNext_Agent.core.metadata_service import MetadataService
from ERPNext_Agent.tools.client import FrappeClient

# Fields excluded from user confirmation cards (internal system & accounting flags)
EXCLUDE_FROM_CONFIRMATION: set[str] = {
	"doctype",
	"name",
	"is_group",
	"allow_account_creation_against_child_company",
	"book_advance_payments_in_separate_party_account",
	"reconcile_on_advance_payment_date",
	"reconciliation_takes_effect_on",
	"auto_exchange_rate_revaluation",
	"submit_err_jv",
	"enable_perpetual_inventory",
	"enable_item_wise_inventory_account",
	"enable_provisional_accounting_for_non_stock_items",
	"valuation_method",
	"idx",
	"docstatus",
	"naming_series",
	"lft",
	"rgt",
	"old_parent",
	"disabled",
	"owner",
	"creation",
	"modified",
	"modified_by",
	"_comments",
	"_assign",
	"_liked_by",
	"parent",
	"parenttype",
	"parentfield",
	"_user_tags",
	"amended_from",
}

# System/framework fields that must never appear in slot intake cards
SYSTEM_INTERNAL_FIELDS: set[str] = {
	"idx",
	"docstatus",
	"naming_series",
	"lft",
	"rgt",
	"old_parent",
	"disabled",
	"owner",
	"creation",
	"modified",
	"modified_by",
	"_comments",
	"_assign",
	"_liked_by",
	"_user_tags",
	"amended_from",
	"parent",
	"parenttype",
	"parentfield",
}

# Core entity fields to display alongside mandatory fields in intake cards
CORE_ENTITY_FIELDS: set[str] = {
	"company_name",
	"abbr",
	"default_currency",
	"country",
	"default_letter_head",
	"customer_name",
	"customer_type",
	"customer_group",
	"territory",
	"item_code",
	"item_name",
	"item_group",
	"stock_uom",
	"is_stock_item",
	"project_name",
	"company",
	"status",
	"expected_start_date",
	"expected_end_date",
	"supplier_name",
	"supplier_type",
	"supplier_group",
	"warehouse_name",
	"parent_warehouse",
	"lead_name",
	"email_id",
	"mobile_no",
	"description",
	"title",
	"subject",
	"first_name",
	"last_name",
	"gender",
	"date_of_birth",
	"date_of_joining",
}


def auto_generate_abbr(name: str) -> str:
	"""Generate abbreviation taking first letter of each word (preserves case, e.g. GMplc or gmpl)."""
	if not name:
		return ""
	words = [w for w in re.split(r"[\s\-_]+", name.strip()) if w]
	if not words:
		return ""
	abbr = "".join(w[0] for w in words if w[0].isalnum())
	if len(abbr) < 2 and len(words[0]) >= 2:
		abbr = words[0][:3].upper()
	return abbr


def get_clean_pending_values(values: dict[str, Any]) -> dict[str, Any]:
	"""Filter out internal Frappe boolean flags and system fields to ensure pristine presentation."""
	return {
		k: v
		for k, v in values.items()
		if k.lower() not in EXCLUDE_FROM_CONFIRMATION and v is not None and v != ""
	}


def _slot_sort_key(s: dict[str, Any]) -> tuple:
	"""Sort intake slots logically: primary identifiers first, abbr next, then other mandatory, then optional."""
	is_reqd = bool(s.get("reqd"))
	fname = s.get("field", "")
	if fname in (
		"company_name",
		"customer_name",
		"item_code",
		"project_name",
		"supplier_name",
		"warehouse_name",
	):
		priority = 0
	elif fname in ("abbr", "item_name"):
		priority = 1
	elif is_reqd:
		priority = 2
	else:
		priority = 3
	return (priority, fname)


def get_slots_for_doctype(
	doctype: str, live_meta: dict[str, Any] | None = None, client: FrappeClient | None = None
) -> list[dict[str, Any]]:
	"""Construct dynamic slot intake schema for any DocType directly from live ERPNext metadata."""
	if not doctype:
		return []

	client_inst = client or FrappeClient()
	meta_service = MetadataService(client_inst)

	meta = live_meta
	if not meta or not meta.get("fields"):
		meta = meta_service.get_doctype_meta(doctype)

	if not meta or not meta.get("success", True):
		return []

	raw_fields = meta.get("fields_list") or meta.get("fields") or []
	if isinstance(raw_fields, dict):
		raw_fields = list(raw_fields.values())

	slots: list[dict[str, Any]] = []
	seen_fnames: set[str] = set()

	# Determine if DocType has small number of fields (include all non-system editable fields)
	editable_count = sum(
		1
		for f in raw_fields
		if f.get("fieldtype") not in ("Section Break", "Column Break", "Tab Break")
		and not f.get("read_only")
		and f.get("fieldname") not in SYSTEM_INTERNAL_FIELDS
	)
	is_small_doctype = editable_count <= 15

	for f in raw_fields:
		fname = f.get("fieldname")
		if not fname or fname in seen_fnames or fname in SYSTEM_INTERNAL_FIELDS:
			continue

		ftype = f.get("fieldtype", "Data")
		if ftype in ("Section Break", "Column Break", "Tab Break"):
			continue

		read_only = bool(f.get("read_only"))
		reqd = bool(f.get("reqd"))
		is_custom = bool(f.get("is_custom")) or fname.startswith("custom_")

		# Inclusion rule:
		# 1. Any mandatory field (reqd=True)
		# 2. Any custom field added in ERPNext Desk
		# 3. Known core entity fields
		# 4. Small doctype editable fields
		should_include = reqd or is_custom or (fname in CORE_ENTITY_FIELDS) or is_small_doctype

		# Skip read-only fields unless explicitly mandatory, and non-included optional fields
		if not should_include or (read_only and not reqd):
			continue

		seen_fnames.add(fname)
		label = f.get("label") or fname.replace("_", " ").title()
		opts = f.get("options")
		default_val = f.get("default")

		# Resolve options dynamically from live ERPNext
		parsed_opts = None
		if ftype == "Select":
			if isinstance(opts, list):
				parsed_opts = opts
			elif opts:
				parsed_opts = [o.strip() for o in str(opts).splitlines() if o.strip()]
			else:
				parsed_opts = []
		elif ftype == "Link" and opts:
			target_dt = str(opts).strip()
			# Fetch live records from MariaDB for this Link target
			parsed_opts = meta_service.get_link_options(target_dt, limit=50)
			if not parsed_opts:
				parsed_opts = target_dt
		else:
			parsed_opts = opts

		# Build dynamic hint
		hint = f.get("description") or ""
		if not hint:
			if fname == "abbr":
				hint = "Unique abbreviation code (auto-generated e.g. from company name)"
			elif fname in ("company_name", "customer_name", "item_name", "supplier_name", "project_name"):
				hint = f"Full name of the {doctype}"
			elif ftype == "Link":
				hint = f"Select from existing {opts} records in ERPNext"
			elif ftype == "Select":
				hint = (
					f"Select an option ({', '.join(parsed_opts[:3])}...)"
					if isinstance(parsed_opts, list) and parsed_opts
					else "Select option"
				)
			else:
				hint = f"Fieldtype: {ftype}"

		slots.append(
			{
				"field": fname,
				"label": label,
				"fieldtype": ftype,
				"reqd": reqd,
				"options": parsed_opts,
				"default": default_val,
				"hint": hint,
			}
		)

	# Sort slots so primary identifiers appear first, abbr next, then other mandatory, then optional
	slots.sort(key=_slot_sort_key)
	return slots


class _DynamicSlotRegistry(dict):
	"""Backwards-compatible dynamic slot registry that resolves DocType slots on the fly."""

	def __getitem__(self, doctype: str) -> dict[str, Any]:
		slots = get_slots_for_doctype(doctype)
		return {"module": "General", "description": f"Dynamic live schema for {doctype}", "fields": slots}

	def get(self, doctype: str, default: Any = None) -> Any:
		try:
			return self[doctype]
		except Exception:
			return default

	def __contains__(self, doctype: object) -> bool:
		return True


MODULE_SLOT_REGISTRY: dict[str, Any] = _DynamicSlotRegistry()
CURRENCY_LIST: list[str] = []
COUNTRY_LIST: list[str] = []
COMPANY_LIST: list[str] = []
LETTER_HEAD_LIST: list[str] = []
