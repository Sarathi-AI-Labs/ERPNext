# Master Field & Form Reference: All 13 Modules in Frappe / ERPNext

This document provides an exhaustive, field-by-field, form-by-form, tab-by-tab, and button-by-button breakdown of all 13 modules accessible in this Frappe Docker ERPNext environment.

## Module: Organization
*Legal entity governance, multi-company setups, departments, branches, letterheads, user credentials, and Sarathi customer-company isolation.*

### Summary of DocTypes in Organization:
- **Company**: 93 fields | Submittable: No
- **Letter Head**: 18 fields | Submittable: No
- **Department**: 8 fields | Submittable: No
- **Branch**: 1 fields | Submittable: No
- **User**: 78 fields | Submittable: No
- **Email Account**: 65 fields | Submittable: No
- **Sarathi Customer Organization**: 2 fields | Submittable: No

### DocType: `Company`
- **Submittable**: No
- **Total Data Fields**: 93

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company_name` | Company | Data | ✓ Mandatory | `-` | - |
| `abbr` | Abbr | Data | ✓ Mandatory | `-` | - |
| `default_currency` | Default Currency | Link | ✓ Mandatory | `-` | Currency |
| `country` | Country | Link | ✓ Mandatory | `-` | Country |
| `is_group` | Is Group | Check | Optional | `0` | - |
| `default_holiday_list` | Default Holiday List | Link | Optional | `-` | Holiday List |
| `default_letter_head` | Default Letter Head | Link | Optional | `-` | Letter Head |
| `tax_id` | Tax ID | Data | Optional | `-` | - |
| `domain` | Domain | Data | Optional | `-` | - |
| `date_of_establishment` | Date of Establishment | Date | Optional | `-` | - |
| `parent_company` | Parent Company | Link | Optional | `-` | Company |
| `reporting_currency` | Reporting Currency | Link | Optional | `-` | Currency |
| `company_logo` | Company Logo | Attach Image | Optional | `-` | - |
| `date_of_incorporation` | Date of Incorporation | Date | Optional | `-` | - |
| `phone_no` | Phone No | Data | Optional | `-` | Phone |
| `email` | Email | Data | Optional | `-` | Email |
| `company_description` | Company Description | Text Editor | Optional | `-` | - |
| `date_of_commencement` | Date of Commencement | Date | Optional | `-` | - |
| `fax` | Fax | Data | Optional | `-` | Phone |
| `website` | Website | Data | Optional | `-` | - |
| `address_html` | address_html | HTML | Optional | `-` | - |
| `registration_details` | Registration Details | Code | Optional | `-` | - |
| `lft` | Lft | Int | Optional | `-` | - |
| `rgt` | Rgt | Int | Optional | `-` | - |
| `old_parent` | old_parent | Data | Optional | `-` | - |
| `create_chart_of_accounts_based_on` | Create Chart Of Accounts Based On | Select | Optional | `-` | Standard Template, Existing Company |
| `existing_company` | Existing Company  | Link | Optional | `-` | Company |
| `chart_of_accounts` | Chart Of Accounts Template | Select | Optional | `-` | - |
| `default_bank_account` | Default Bank Account | Link | Optional | `-` | Account |
| `default_cash_account` | Default Cash Account | Link | Optional | `-` | Account |
| `default_receivable_account` | Default Receivable Account | Link | Optional | `-` | Account |
| `default_payable_account` | Default Payable Account | Link | Optional | `-` | Account |
| `write_off_account` | Write Off Account | Link | Optional | `-` | Account |
| `unrealized_profit_loss_account` | Unrealized Profit / Loss Account | Link | Optional | `-` | Account |
| `allow_account_creation_against_child_company` | Allow Account Creation Against Child Company | Check | Optional | `0` | - |
| `default_expense_account` | Default Cost of Goods Sold Account | Link | Optional | `-` | Account |
| `default_income_account` | Default Income Account | Link | Optional | `-` | Account |
| `default_discount_account` | Default Payment Discount Account | Link | Optional | `-` | Account |
| `payment_terms` | Default Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `cost_center` | Default Cost Center | Link | Optional | `-` | Cost Center |
| `default_finance_book` | Default Finance Book | Link | Optional | `-` | Finance Book |
| `exchange_gain_loss_account` | Exchange Gain / Loss Account | Link | Optional | `-` | Account |
| `unrealized_exchange_gain_loss_account` | Unrealized Exchange Gain/Loss Account | Link | Optional | `-` | Account |
| `round_off_account` | Round Off Account | Link | Optional | `-` | Account |
| `round_off_cost_center` | Round Off Cost Center | Link | Optional | `-` | Cost Center |
| `round_off_for_opening` | Round Off for Opening | Link | Optional | `-` | Account |
| `default_deferred_revenue_account` | Default Deferred Revenue Account | Link | Optional | `-` | Account |
| `default_deferred_expense_account` | Default Deferred Expense Account | Link | Optional | `-` | Account |
| `book_advance_payments_in_separate_party_account` | Book Advance Payments in Separate Party Account | Check | Optional | `0` | - |
| `reconcile_on_advance_payment_date` | Reconcile on Advance Payment Date | Check | Optional | `0` | - |
| `reconciliation_takes_effect_on` | Reconciliation Takes Effect On | Select | Optional | `Oldest Of Invoice Or Advance` | Advance Payment Date, Oldest Of Invoice Or Advance, Reconciliation Date |
| `default_advance_received_account` | Default Advance Received Account | Link | Optional | `-` | Account |
| `default_advance_paid_account` | Default Advance Paid Account | Link | Optional | `-` | Account |
| `auto_exchange_rate_revaluation` | Auto Create Exchange Rate Revaluation | Check | Optional | `0` | - |
| `auto_err_frequency` | Frequency | Select | Optional | `-` | Daily, Weekly, Monthly |
| `submit_err_jv` | Submit ERR Journals? | Check | Optional | `0` | - |
| `exception_budget_approver_role` | Exception Budget Approver Role | Link | Optional | `-` | Role |
| `accumulated_depreciation_account` | Accumulated Depreciation Account | Link | Optional | `-` | Account |
| `depreciation_expense_account` | Depreciation Expense Account | Link | Optional | `-` | Account |
| `series_for_depreciation_entry` | Series for Asset Depreciation Entry (Journal Entry) | Data | Optional | `-` | - |
| `disposal_account` | Gain/Loss Account on Asset Disposal | Link | Optional | `-` | Account |
| `depreciation_cost_center` | Asset Depreciation Cost Center | Link | Optional | `-` | Cost Center |
| `capital_work_in_progress_account` | Capital Work In Progress Account | Link | Optional | `-` | Account |
| `asset_received_but_not_billed` | Asset Received But Not Billed | Link | Optional | `-` | Account |
| `accounts_frozen_till_date` | Accounts Frozen Till Date | Date | Optional | `-` | - |
| `role_allowed_for_frozen_entries` | Roles Allowed to Set and Edit Frozen Account Entries | Link | Optional | `-` | Role |
| `default_buying_terms` | Default Buying Terms | Link | Optional | `-` | Terms and Conditions |
| `sales_monthly_history` | Sales Monthly History | Small Text | Optional | `-` | - |
| `monthly_sales_target` | Monthly Sales Target | Currency | Optional | `-` | default_currency |
| `total_monthly_sales` | Total Monthly Sales | Currency | Optional | `-` | default_currency |
| `default_selling_terms` | Default Selling Terms | Link | Optional | `-` | Terms and Conditions |
| `default_sales_contact` | Default Sales Contact | Link | Optional | `-` | Contact |
| `default_warehouse_for_sales_return` | Default Warehouse for Sales Return | Link | Optional | `-` | Warehouse |
| `credit_limit` | Credit Limit | Currency | Optional | `-` | default_currency |
| `transactions_annual_history` | Transactions Annual History | Code | Optional | `-` | - |
| `purchase_expense_account` | Purchase Expense Account | Link | Optional | `-` | Account |
| `service_expense_account` | Service Expense Account | Link | Optional | `-` | Account |
| `purchase_expense_contra_account` | Purchase Expense Contra Account | Link | Optional | `-` | Account |
| `expenses_added_to_stock_account` | Expenses Added To Stock Account | Link | Optional | `-` | Account |
| `expenses_added_to_stock_contra_account` | Expenses Added To Stock Contra Account | Link | Optional | `-` | Account |
| `enable_perpetual_inventory` | Enable Perpetual Inventory | Check | Optional | `1` | - |
| `enable_item_wise_inventory_account` | Enable Item-wise Inventory Account | Check | Optional | `0` | - |
| `enable_provisional_accounting_for_non_stock_items` | Enable Provisional Accounting For Non Stock Items | Check | Optional | `0` | - |
| `default_inventory_account` | Default Inventory Account | Link | Optional | `-` | Account |
| `valuation_method` | Default Stock Valuation Method | Select | ✓ Mandatory | `FIFO` | FIFO, Moving Average, LIFO |
| `stock_adjustment_account` | Stock Adjustment Account | Link | Optional | `-` | Account |
| `stock_received_but_not_billed` | Stock Received But Not Billed | Link | Optional | `-` | Account |
| `default_provisional_account` | Default Provisional Account | Link | Optional | `-` | Account |
| `default_in_transit_warehouse` | Default In-Transit Warehouse | Link | Optional | `-` | Warehouse |
| `default_operating_cost_account` | Default Operating Cost Account | Link | Optional | `-` | Account |
| `default_wip_warehouse` |  Default Work In Progress Warehouse  | Link | Optional | `-` | Warehouse |
| `default_fg_warehouse` | Default Finished Goods Warehouse | Link | Optional | `-` | Warehouse |
| `default_scrap_warehouse` | Default Scrap Warehouse | Link | Optional | `-` | Warehouse |

### DocType: `Letter Head`
- **Submittable**: No
- **Total Data Fields**: 18

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `letter_head_name` | Letter Head Name | Data | ✓ Mandatory | `-` | - |
| `source` | Letter Head Based On | Select | Optional | `-` | Image, HTML |
| `footer_source` | Footer Based On | Select | Optional | `HTML` | Image, HTML |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `is_default` | Default Letter Head | Check | Optional | `0` | - |
| `image` | Image | Attach Image | Optional | `-` | - |
| `image_height` | Image Height (px) | Float | Optional | `-` | - |
| `image_width` | Image Width (px) | Float | Optional | `-` | - |
| `align` | Align | Select | Optional | `Left` | Left, Right, Center |
| `content` | Header HTML | HTML Editor | Optional | `-` | - |
| `footer` | Footer HTML | HTML Editor | Optional | `-` | - |
| `footer_image` | Image | Attach Image | Optional | `-` | - |
| `footer_image_height` | Image Height (px) | Float | Optional | `-` | - |
| `footer_image_width` | Image Width (px) | Float | Optional | `-` | - |
| `footer_align` | Align | Select | Optional | `-` | Left, Right, Center |
| `header_script` | Header Script | Code | Optional | `-` | Javascript |
| `footer_script` | Footer Script | Code | Optional | `-` | Javascript |
| `instructions` | Instructions | HTML | Optional | `-` | - |

### DocType: `Department`
- **Submittable**: No
- **Total Data Fields**: 8

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `department_name` | Department | Data | ✓ Mandatory | `-` | - |
| `parent_department` | Parent Department | Link | Optional | `-` | Department |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `is_group` | Is Group | Check | Optional | `0` | - |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `lft` | lft | Int | Optional | `-` | - |
| `rgt` | rgt | Int | Optional | `-` | - |
| `old_parent` | Old Parent | Data | Optional | `-` | - |

### DocType: `Branch`
- **Submittable**: No
- **Total Data Fields**: 1

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `branch` | Branch | Data | ✓ Mandatory | `-` | - |

### DocType: `User`
- **Submittable**: No
- **Total Data Fields**: 78

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `enabled` | Enabled | Check | Optional | `1` | - |
| `email` | Email | Data | ✓ Mandatory | `-` | Email |
| `first_name` | First Name | Data | ✓ Mandatory | `-` | - |
| `middle_name` | Middle Name | Data | Optional | `-` | - |
| `last_name` | Last Name | Data | Optional | `-` | - |
| `full_name` | Full Name | Data | Optional | `-` | - |
| `username` | Username | Data | Optional | `-` | - |
| `language` | Language | Link | Optional | `-` | Language |
| `time_zone` | Time Zone | Autocomplete | Optional | `-` | - |
| `send_welcome_email` | Send Welcome Email | Check | Optional | `1` | - |
| `unsubscribed` | Unsubscribed | Check | Optional | `0` | - |
| `user_image` | User Image | Attach Image | Optional | `-` | - |
| `role_profile_name` | Role Profile | Link | Optional | `-` | Role Profile |
| `role_profiles` | Role Profiles | Table MultiSelect | Optional | `-` | User Role Profile |
| `roles_html` | Roles HTML | HTML | Optional | `-` | - |
| `roles` | Roles Assigned | Table | Optional | `-` | Has Role |
| `module_profile` | Module Profile | Link | Optional | `-` | Module Profile |
| `modules_html` | Modules HTML | HTML | Optional | `-` | - |
| `block_modules` | Block Modules | Table | Optional | `-` | Block Module |
| `home_settings` | Home Settings | Code | Optional | `-` | - |
| `gender` | Gender | Link | Optional | `-` | Gender |
| `birth_date` | Birth Date | Date | Optional | `-` | - |
| `interest` | Interests | Small Text | Optional | `-` | - |
| `phone` | Phone | Data | Optional | `-` | Phone |
| `location` | Location | Data | Optional | `-` | - |
| `bio` | Bio | Small Text | Optional | `-` | - |
| `mobile_no` | Mobile No | Data | Optional | `-` | Phone |
| `mute_sounds` | Mute Sounds | Check | Optional | `0` | - |
| `desk_theme` | Desk Theme | Select | Optional | `-` | Light, Dark, Automatic |
| `code_editor_type` | Code Editor Type | Select | Optional | `vscode` | vscode, vim, emacs |
| `banner_image` | Banner Image | Attach Image | Optional | `-` | - |
| `search_bar` | Search Bar | Check | Optional | `1` | - |
| `notifications` | Notifications | Check | Optional | `1` | - |
| `list_sidebar` | Sidebar | Check | Optional | `1` | - |
| `bulk_actions` | Bulk Actions | Check | Optional | `1` | - |
| `view_switcher` | View Switcher | Check | Optional | `1` | - |
| `form_sidebar` | Sidebar | Check | Optional | `1` | - |
| `form_navigation_buttons` | Navigation Buttons | Check | Optional | `1` | - |
| `timeline` | Timeline | Check | Optional | `1` | - |
| `dashboard` | Dashboard | Check | Optional | `1` | - |
| `show_absolute_datetime_in_timeline` | Show Absolute Datetime in Timeline | Check | Optional | `0` | - |
| `new_password` | Set New Password | Password | Optional | `-` | - |
| `logout_all_sessions` | Logout From All Devices After Changing Password | Check | Optional | `1` | - |
| `reset_password_key` | Reset Password Key | Data | Optional | `-` | - |
| `last_reset_password_key_generated_on` | Last Reset Password Key Generated On | Datetime | Optional | `-` | - |
| `last_password_reset_date` | Last Password Reset Date | Date | Optional | `-` | - |
| `redirect_url` | Redirect URL | Small Text | Optional | `-` | - |
| `document_follow_notify` | Send Notifications For Documents Followed By Me | Check | Optional | `0` | - |
| `document_follow_frequency` | Frequency | Select | Optional | `Daily` | Hourly, Daily, Weekly |
| `follow_created_documents` | Auto follow documents that you create | Check | Optional | `0` | - |
| `follow_commented_documents` | Auto follow documents that you comment on | Check | Optional | `0` | - |
| `follow_liked_documents` | Auto follow documents that you Like | Check | Optional | `0` | - |
| `follow_assigned_documents` | Auto follow documents that are assigned to you | Check | Optional | `0` | - |
| `follow_shared_documents` | Auto follow documents that are shared with you | Check | Optional | `0` | - |
| `email_signature` | Email Signature | Text Editor | Optional | `-` | - |
| `thread_notify` | Send Notifications For Email Threads | Check | Optional | `1` | - |
| `send_me_a_copy` | Send Me A Copy of Outgoing Emails | Check | Optional | `0` | - |
| `allowed_in_mentions` | Allowed In Mentions | Check | Optional | `1` | - |
| `user_emails` | User Emails | Table | Optional | `-` | User Email |
| `default_workspace` | Default Workspace | Link | Optional | `-` | Workspace |
| `default_app` | Default App | Select | Optional | `-` | - |
| `defaults` | User Defaults | Table | Optional | `-` | DefaultValue |
| `simultaneous_sessions` | Simultaneous Sessions | Int | Optional | `2` | - |
| `restrict_ip` | Restrict IP | Small Text | Optional | `-` | - |
| `last_ip` | Last IP | Read Only | Optional | `-` | - |
| `login_after` | Login After | Int | Optional | `-` | - |
| `user_type` | User Type | Link | Optional | `System User` | User Type |
| `last_active` | Last Active | Datetime | Optional | `-` | - |
| `login_before` | Login Before | Int | Optional | `-` | - |
| `bypass_restrict_ip_check_if_2fa_enabled` | Bypass Restricted IP Address Check If Two Factor Auth Enabled | Check | Optional | `0` | - |
| `last_login` | Last Login | Read Only | Optional | `-` | - |
| `last_known_versions` | Last Known Versions | Text | Optional | `-` | - |
| `social_logins` | Social Logins | Table | Optional | `-` | User Social Login |
| `api_key` | API Key | Data | Optional | `-` | - |
| `generate_keys` | Generate Keys | Button | Optional | `-` | - |
| `api_secret` | API Secret | Password | Optional | `-` | - |
| `onboarding_status` | Onboarding Status | Small Text | Optional | `{}` | - |
| `active_sessions` | Active Sessions | Table | Optional | `-` | User Session Display |

### DocType: `Email Account`
- **Submittable**: No
- **Total Data Fields**: 65

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `email_id` | Email Address | Data | ✓ Mandatory | `-` | Email |
| `company` | Company | Link | Optional | `-` | Company |
| `email_account_name` | Email Account Name | Data | Optional | `-` | - |
| `enable_incoming` | Enable Incoming | Check | Optional | `0` | - |
| `enable_outgoing` | Enable Outgoing | Check | Optional | `0` | - |
| `service` | Service | Select | Optional | `-` | Frappe Mail, GMail, Sendgrid, SparkPost, Yahoo Mail, Outlook.com, Yandex.Mail |
| `domain` | Domain | Link | Optional | `-` | Email Domain |
| `frappe_mail_site` | Frappe Mail Site | Data | Optional | `https://frappemail.com` | - |
| `auth_method` | Method | Select | Optional | `Basic` | Basic, OAuth |
| `backend_app_flow` | Authenticate as Service Principal | Check | Optional | `0` | - |
| `authorize_api_access` | Authorize API Access | Button | Optional | `-` | - |
| `validate_frappe_mail_settings` | Validate Frappe Mail Settings | Button | Optional | `-` | - |
| `password` | Password | Password | Optional | `-` | - |
| `awaiting_password` | Awaiting password | Check | Optional | `0` | - |
| `ascii_encode_password` | Use ASCII encoding for password | Check | Optional | `0` | - |
| `api_key` | API Key | Data | Optional | `-` | - |
| `api_secret` | API Secret | Password | Optional | `-` | - |
| `connected_app` | Connected App | Link | Optional | `-` | Connected App |
| `connected_user` | Connected User | Link | Optional | `-` | User |
| `login_id_is_different` | Use different Email ID | Check | Optional | `0` | - |
| `login_id` | Alternative Email ID | Data | Optional | `-` | - |
| `default_incoming` | Default Incoming | Check | Optional | `0` | - |
| `attachment_limit` | Attachment Limit (MB) | Int | Optional | `-` | - |
| `last_received_at` | Last Received At | Datetime | Optional | `-` | - |
| `use_imap` | Use IMAP | Check | Optional | `0` | - |
| `use_ssl` | Use SSL | Check | Optional | `0` | - |
| `validate_ssl_certificate` | Validate SSL Certificate | Check | Optional | `1` | - |
| `use_starttls` | Use STARTTLS | Check | Optional | `0` | - |
| `email_server` | Incoming Server | Data | Optional | `-` | - |
| `incoming_port` | Port | Data | Optional | `-` | - |
| `email_sync_option` | Email Sync Option | Select | Optional | `UNSEEN` | ALL, UNSEEN |
| `initial_sync_count` | Initial Sync Count | Select | Optional | `250` | 100, 250, 500 |
| `imap_folder` | IMAP Folder | Table | Optional | `-` | IMAP Folder |
| `append_emails_to_sent_folder` | Append Emails to Sent Folder | Check | Optional | `0` | - |
| `sent_folder_name` | Sent Folder Name | Data | Optional | `-` | - |
| `append_to` | Append To | Link | Optional | `-` | DocType |
| `create_contact` | Create Contacts from Incoming Emails | Check | Optional | `1` | - |
| `enable_automatic_linking` | Enable Automatic Linking in Documents | Check | Optional | `0` | - |
| `notify_if_unreplied` | Notify if unreplied | Check | Optional | `0` | - |
| `unreplied_for_mins` | Notify if unreplied for (in mins) | Int | Optional | `30` | - |
| `send_notification_to` | Send Notification to | Small Text | Optional | `-` | - |
| `default_outgoing` | Default Outgoing | Check | Optional | `0` | - |
| `always_use_account_email_id_as_sender` | Always use this email address as sender address | Check | Optional | `0` | - |
| `always_use_account_name_as_sender_name` | Always use this name as sender name | Check | Optional | `0` | - |
| `send_unsubscribe_message` | Send unsubscribe message in email | Check | Optional | `1` | - |
| `track_email_status` | Track Email Status | Check | Optional | `1` | - |
| `add_x_original_from` | Add X-Original-From header | Check | Optional | `1` | - |
| `add_reply_to_header` | Add Reply-To header | Check | Optional | `1` | - |
| `reply_to_addresses` | Reply-To Addresses | Table | Optional | `-` | Reply To Address |
| `use_tls` | Use TLS | Check | Optional | `0` | - |
| `use_ssl_for_outgoing` | Use SSL | Check | Optional | `0` | - |
| `smtp_server` | Outgoing Server | Data | Optional | `-` | - |
| `smtp_port` | Port | Data | Optional | `-` | - |
| `no_smtp_authentication` | Disable SMTP server authentication | Check | Optional | `0` | - |
| `dsn_notify_type` | Delivery Status Notification Type | Select | Optional | `-` | SUCCESS, FAILURE, DELAY, SUCCESS,FAILURE, SUCCESS,FAILURE,DELAY, NEVER |
| `always_bcc` | Always BCC Address | Data | Optional | `-` | Email |
| `add_signature` | Add Signature | Check | Optional | `0` | - |
| `signature` | Signature | Text Editor | Optional | `-` | - |
| `enable_auto_reply` | Enable Auto Reply | Check | Optional | `0` | - |
| `auto_reply_message` | Auto Reply Message | Text Editor | Optional | `-` | - |
| `footer` | Footer Content | Text Editor | Optional | `-` | - |
| `brand_logo` | Brand Logo | Attach Image | Optional | `-` | - |
| `uidvalidity` | UIDVALIDITY | Data | Optional | `-` | - |
| `uidnext` | UIDNEXT | Int | Optional | `-` | - |
| `no_failed` | no failed attempts | Int | Optional | `-` | - |

### DocType: `Sarathi Customer Organization`
- **Submittable**: No
- **Total Data Fields**: 2

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Organization | Link | ✓ Mandatory | `-` | Company |
| `customer` | Customer | Link | ✓ Mandatory | `-` | Customer |

## Module: Assets
*Fixed asset capitalization, straight-line/WDV depreciation schedules, maintenance teams, maintenance logs, and asset repair workflows.*

### Summary of DocTypes in Assets:
- **Asset**: 53 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Asset Depreciation Schedule**: 20 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Asset Capitalization**: 22 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Asset Movement**: 7 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Asset Maintenance Team**: 5 fields | Submittable: No
- **Asset Maintenance**: 9 fields | Submittable: No
- **Asset Maintenance Log**: 19 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Asset Value Adjustment**: 12 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Asset Repair**: 20 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Asset Category**: 5 fields | Submittable: No
- **Location**: 12 fields | Submittable: No

### DocType: `Asset`
- **Submittable**: Yes
- **Total Data Fields**: 53

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | Optional | `-` | ACC-ASS-.YYYY.- |
| `item_code` | Item Code | Link | ✓ Mandatory | `-` | Item |
| `item_name` | Item Name | Read Only | Optional | `-` | - |
| `asset_name` | Asset Name | Data | ✓ Mandatory | `-` | - |
| `location` | Location | Link | ✓ Mandatory | `-` | Location |
| `image` | Image | Attach Image | Optional | `-` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `asset_category` | Asset Category | Link | Optional | `-` | Asset Category |
| `asset_type` | Asset Type | Select | Optional | `-` | Existing Asset, Composite Asset, Composite Component |
| `maintenance_required` | Maintenance Required | Check | Optional | `0` | - |
| `calculate_depreciation` | Calculate Depreciation | Check | Optional | `0` | - |
| `purchase_receipt` | Purchase Receipt | Link | Optional | `-` | Purchase Receipt |
| `purchase_receipt_item` | Purchase Receipt Item | Data | Optional | `-` | - |
| `purchase_invoice` | Purchase Invoice | Link | Optional | `-` | Purchase Invoice |
| `purchase_invoice_item` | Purchase Invoice Item | Data | Optional | `-` | - |
| `purchase_date` | Purchase Date | Date | ✓ Mandatory | `-` | - |
| `available_for_use_date` | Available for Use Date | Date | Optional | `-` | - |
| `disposal_date` | Disposal Date | Date | Optional | `-` | - |
| `net_purchase_amount` | Net Purchase Amount | Currency | Optional | `-` | currency |
| `purchase_amount` | Purchase Amount | Currency | Optional | `-` | - |
| `asset_quantity` | Asset Quantity | Int | Optional | `1` | - |
| `additional_asset_cost` | Additional Asset Cost | Currency | Optional | `0` | Company:company:default_currency |
| `total_asset_cost` | Total Asset Cost | Currency | Optional | `-` | Company:company:default_currency |
| `opening_accumulated_depreciation` | Opening Accumulated Depreciation | Currency | Optional | `-` | Company:company:default_currency |
| `is_fully_depreciated` | Is Fully Depreciated | Check | Optional | `0` | - |
| `opening_number_of_booked_depreciations` | Opening Number of Booked Depreciations | Int | Optional | `-` | - |
| `finance_books` | Finance Books | Table | Optional | `-` | Asset Finance Book |
| `depreciation_method` | Depreciation Method | Select | Optional | `-` | Straight Line, Double Declining Balance, Written Down Value, Manual |
| `value_after_depreciation` | Value After Depreciation | Currency | Optional | `-` | Company:company:default_currency |
| `frequency_of_depreciation` | Frequency of Depreciation (Months) | Int | Optional | `-` | - |
| `next_depreciation_date` | Next Depreciation Date | Date | Optional | `-` | - |
| `total_number_of_depreciations` | Total Number of Depreciations | Int | Optional | `-` | - |
| `depreciation_schedule_view` | Depreciation Schedule View | HTML | Optional | `-` | - |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `asset_owner` | Asset Owner | Select | Optional | `Company` | Company, Supplier, Customer |
| `asset_owner_company` | Asset Owner Company | Link | Optional | `-` | Company |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `supplier` | Supplier | Link | Optional | `-` | Supplier |
| `policy_number` | Policy number | Data | Optional | `-` | - |
| `insurer` | Insurer | Data | Optional | `-` | - |
| `insured_value` | Insured value | Data | Optional | `-` | - |
| `insurance_start_date` | Insurance Start Date | Date | Optional | `-` | - |
| `insurance_end_date` | Insurance End Date | Date | Optional | `-` | - |
| `comprehensive_insurance` | Comprehensive Insurance | Data | Optional | `-` | - |
| `status` | Status | Select | Optional | `Draft` | Draft, Submitted, Cancelled, Partially Depreciated, Fully Depreciated, Sold, ... |
| `custodian` | Custodian | Link | Optional | `-` | Employee |
| `department` | Department | Link | Optional | `-` | Department |
| `default_finance_book` | Default Finance Book | Link | Optional | `-` | Finance Book |
| `depr_entry_posting_status` | Depreciation Entry Posting Status | Select | Optional | `-` | Successful, Failed |
| `journal_entry_for_scrap` | Journal Entry for Scrap | Link | Optional | `-` | Journal Entry |
| `split_from` | Split From | Link | Optional | `-` | Asset |
| `amended_from` | Amended From | Link | Optional | `-` | Asset |
| `booked_fixed_asset` | Booked Fixed Asset | Check | Optional | `0` | - |

### DocType: `Asset Depreciation Schedule`
- **Submittable**: Yes
- **Total Data Fields**: 20

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `asset` | Asset | Link | ✓ Mandatory | `-` | Asset |
| `naming_series` | Naming Series | Select | Optional | `-` | ACC-ADS-.YYYY.- |
| `company` | Company | Link | Optional | `-` | Company |
| `net_purchase_amount` | Net Purchase Amount | Currency | Optional | `-` | Company:company:default_currency |
| `opening_accumulated_depreciation` | Opening Accumulated Depreciation | Currency | Optional | `-` | Company:company:default_currency |
| `opening_number_of_booked_depreciations` | Opening Number of Booked Depreciations | Int | Optional | `-` | - |
| `finance_book` | Finance Book | Link | Optional | `-` | Finance Book |
| `finance_book_id` | Finance Book Id | Int | Optional | `-` | - |
| `depreciation_method` | Depreciation Method | Select | Optional | `-` | Straight Line, Double Declining Balance, Written Down Value, Manual |
| `total_number_of_depreciations` | Total Number of Depreciations | Int | Optional | `-` | - |
| `rate_of_depreciation` | Rate of Depreciation | Percent | Optional | `-` | - |
| `daily_prorata_based` | Depreciate based on daily pro-rata | Check | Optional | `0` | - |
| `shift_based` | Depreciate based on shifts | Check | Optional | `0` | - |
| `frequency_of_depreciation` | Frequency of Depreciation (Months) | Int | Optional | `-` | - |
| `expected_value_after_useful_life` | Expected Value After Useful Life | Currency | Optional | `-` | Company:company:default_currency |
| `value_after_depreciation` | Value After Depreciation | Currency | Optional | `-` | - |
| `depreciation_schedule` | Depreciation Schedule | Table | Optional | `-` | Depreciation Schedule |
| `notes` | Notes | Small Text | Optional | `-` | - |
| `status` | Status | Select | Optional | `-` | Draft, Active, Cancelled |
| `amended_from` | Amended From | Link | Optional | `-` | Asset Depreciation Schedule |

### DocType: `Asset Capitalization`
- **Submittable**: Yes
- **Total Data Fields**: 22

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `title` | Title | Data | Optional | `-` | - |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | ACC-ASC-.YYYY.- |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `target_asset` | Target Asset | Link | Optional | `-` | Asset |
| `target_asset_name` | Asset Name | Data | Optional | `-` | - |
| `finance_book` | Finance Book | Link | Optional | `-` | Finance Book |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `posting_time` | Posting Time | Time | ✓ Mandatory | `Now` | - |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `target_item_code` | Target Item Code | Link | Optional | `-` | Item |
| `amended_from` | Amended From | Link | Optional | `-` | Asset Capitalization |
| `stock_items` | Stock Items | Table | Optional | `-` | Asset Capitalization Stock Item |
| `stock_items_total` | Consumed Stock Total Value | Currency | Optional | `-` | Company:company:default_currency |
| `asset_items` | Assets | Table | Optional | `-` | Asset Capitalization Asset Item |
| `asset_items_total` | Consumed Asset Total Value | Currency | Optional | `-` | Company:company:default_currency |
| `service_items` | Services | Table | Optional | `-` | Asset Capitalization Service Item |
| `service_items_total` | Service Expense Total Amount | Currency | Optional | `-` | Company:company:default_currency |
| `total_value` | Total Value | Currency | Optional | `-` | Company:company:default_currency |
| `target_incoming_rate` | Target Incoming Rate | Currency | Optional | `-` | Company:company:default_currency |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `target_fixed_asset_account` | Target Fixed Asset Account | Link | Optional | `-` | Account |

### DocType: `Asset Movement`
- **Submittable**: Yes
- **Total Data Fields**: 7

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `purpose` | Purpose | Select | ✓ Mandatory | `-` | Issue, Receipt, Transfer, Transfer and Issue |
| `transaction_date` | Transaction Date | Datetime | ✓ Mandatory | `Now` | - |
| `assets` | Assets | Table | ✓ Mandatory | `-` | Asset Movement Item |
| `reference_doctype` | Reference Document Type | Link | Optional | `-` | DocType |
| `reference_name` | Reference Document Name | Dynamic Link | Optional | `-` | reference_doctype |
| `amended_from` | Amended From | Link | Optional | `-` | Asset Movement |

### DocType: `Asset Maintenance Team`
- **Submittable**: No
- **Total Data Fields**: 5

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `maintenance_team_name` | Maintenance Team Name | Data | ✓ Mandatory | `-` | - |
| `maintenance_manager` | Maintenance Manager | Link | Optional | `-` | User |
| `maintenance_manager_name` | Maintenance Manager Name | Read Only | Optional | `-` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `maintenance_team_members` | Maintenance Team Members | Table | ✓ Mandatory | `-` | Maintenance Team Member |

### DocType: `Asset Maintenance`
- **Submittable**: No
- **Total Data Fields**: 9

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `asset_name` | Asset Name | Link | ✓ Mandatory | `-` | Asset |
| `asset_category` | Asset Category | Read Only | Optional | `-` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `item_code` | Item Code | Read Only | Optional | `-` | - |
| `item_name` | Item Name | Read Only | Optional | `-` | - |
| `maintenance_team` | Maintenance Team | Link | ✓ Mandatory | `-` | Asset Maintenance Team |
| `maintenance_manager` | Maintenance Manager | Data | Optional | `-` | - |
| `maintenance_manager_name` | Maintenance Manager Name | Read Only | Optional | `-` | - |
| `asset_maintenance_tasks` | Maintenance Tasks | Table | ✓ Mandatory | `-` | Asset Maintenance Task |

### DocType: `Asset Maintenance Log`
- **Submittable**: Yes
- **Total Data Fields**: 19

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `asset_maintenance` | Asset Maintenance | Link | Optional | `-` | Asset Maintenance |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | ACC-AML-.YYYY.- |
| `asset_name` | Asset Name | Read Only | Optional | `-` | - |
| `item_code` | Item Code | Read Only | Optional | `-` | - |
| `item_name` | Item Name | Read Only | Optional | `-` | - |
| `task` | Task | Link | Optional | `-` | Asset Maintenance Task |
| `task_name` | Task Name | Data | Optional | `-` | - |
| `maintenance_type` | Maintenance Type | Read Only | Optional | `-` | - |
| `periodicity` | Periodicity | Data | Optional | `-` | - |
| `has_certificate` | Has Certificate  | Check | Optional | `0` | - |
| `certificate_attachement` | Certificate | Attach | Optional | `-` | - |
| `maintenance_status` | Maintenance Status | Select | ✓ Mandatory | `-` | Planned, Completed, Cancelled, Overdue |
| `assign_to_name` | Assign To | Read Only | Optional | `-` | - |
| `task_assignee_email` | Task Assignee Email | Data | Optional | `-` | - |
| `due_date` | Due Date | Date | Optional | `-` | - |
| `completion_date` | Completion Date | Date | Optional | `-` | - |
| `description` | Description | Read Only | Optional | `-` | - |
| `actions_performed` | Actions performed | Text Editor | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Asset Maintenance Log |

### DocType: `Asset Value Adjustment`
- **Submittable**: Yes
- **Total Data Fields**: 12

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | Optional | `-` | Company |
| `asset` | Asset | Link | ✓ Mandatory | `-` | Asset |
| `asset_category` | Asset Category | Read Only | Optional | `-` | - |
| `date` | Date | Date | ✓ Mandatory | `-` | - |
| `finance_book` | Finance Book | Link | Optional | `-` | Finance Book |
| `amended_from` | Amended From | Link | Optional | `-` | Asset Value Adjustment |
| `current_asset_value` | Current Asset Value | Currency | ✓ Mandatory | `-` | - |
| `new_asset_value` | New Asset Value | Currency | ✓ Mandatory | `-` | - |
| `difference_amount` | Difference Amount | Currency | Optional | `-` | - |
| `difference_account` | Difference Account | Link | ✓ Mandatory | `-` | Account |
| `journal_entry` | Journal Entry | Link | Optional | `-` | Journal Entry |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |

### DocType: `Asset Repair`
- **Submittable**: Yes
- **Total Data Fields**: 20

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | ACC-ASR-.YYYY.- |
| `company` | Company | Link | Optional | `-` | Company |
| `asset` | Asset | Link | ✓ Mandatory | `-` | Asset |
| `asset_name` | Asset Name | Read Only | Optional | `-` | - |
| `repair_status` | Repair Status | Select | Optional | `Pending` | Pending, Completed, Cancelled |
| `failure_date` | Failure Date | Datetime | ✓ Mandatory | `-` | - |
| `completion_date` | Completion Date | Datetime | Optional | `-` | - |
| `downtime` | Downtime | Data | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Asset Repair |
| `description` | Error Description | Long Text | Optional | `-` | - |
| `actions_performed` | Actions performed | Long Text | Optional | `-` | - |
| `invoices` | Repair Purchase Invoices | Table | Optional | `-` | Asset Repair Purchase Invoice |
| `repair_cost` | Repair Cost | Currency | Optional | `0` | - |
| `stock_items` | Stock Items | Table | Optional | `-` | Asset Repair Consumed Item |
| `consumed_items_cost` | Consumed Items Cost | Currency | Optional | `-` | - |
| `capitalize_repair_cost` | Capitalize Repair Cost | Check | Optional | `0` | - |
| `increase_in_asset_life` | Increase In Asset Life(Months) | Int | Optional | `-` | - |
| `total_repair_cost` | Total Repair Cost | Currency | Optional | `-` | - |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |

### DocType: `Asset Category`
- **Submittable**: No
- **Total Data Fields**: 5

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `asset_category_name` | Asset Category Name | Data | ✓ Mandatory | `-` | - |
| `enable_cwip_accounting` | Enable Capital Work in Progress Accounting | Check | Optional | `0` | - |
| `non_depreciable_category` | Non Depreciable Category | Check | Optional | `0` | - |
| `finance_books` | Finance Books | Table | Optional | `-` | Asset Finance Book |
| `accounts` | Accounts | Table | ✓ Mandatory | `-` | Asset Category Account |

### DocType: `Location`
- **Submittable**: No
- **Total Data Fields**: 12

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `location_name` | Location Name | Data | ✓ Mandatory | `-` | - |
| `parent_location` | Parent Location | Link | Optional | `-` | Location |
| `is_container` | Is Container | Check | Optional | `0` | - |
| `is_group` | Is Group | Check | Optional | `0` | - |
| `latitude` | Latitude | Float | Optional | `-` | - |
| `longitude` | Longitude | Float | Optional | `-` | - |
| `area` | Area | Float | Optional | `-` | - |
| `area_uom` | Area UOM | Link | Optional | `-` | UOM |
| `location` | Location | Geolocation | Optional | `-` | - |
| `lft` | lft | Int | Optional | `-` | - |
| `rgt` | rgt | Int | Optional | `-` | - |
| `old_parent` | Old Parent | Data | Optional | `-` | - |

## Module: Buying
*Procurement lifecycle, Material Requests, Supplier Quotations, Purchase Orders with project auto-propagation, Purchase Invoices, and supplier scorecards.*

### Summary of DocTypes in Buying:
- **Material Request**: 25 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Request for Quotation**: 31 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Supplier Quotation**: 74 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Purchase Order**: 106 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Purchase Invoice**: 137 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Supplier**: 44 fields | Submittable: No
- **Supplier Group**: 8 fields | Submittable: No
- **Price List**: 7 fields | Submittable: No
- **Supplier Scorecard**: 16 fields | Submittable: No
- **Buying Settings**: 31 fields | Submittable: No

### DocType: `Material Request`
- **Submittable**: Yes
- **Total Data Fields**: 25

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | MAT-MR-.YYYY.- |
| `title` | Title | Data | Optional | `{material_request_type}` | - |
| `material_request_type` | Purpose | Select | ✓ Mandatory | `-` | Purchase, Material Transfer, Material Issue, Manufacture, Subcontracting, Cus... |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `auto_created_via_reorder` | Auto Created (Reorder) | Check | Optional | `0` | - |
| `transaction_date` | Transaction Date | Date | ✓ Mandatory | `Today` | - |
| `schedule_date` | Required By | Date | Optional | `-` | - |
| `buying_price_list` | Price List | Link | Optional | `-` | Price List |
| `amended_from` | Amended From | Link | Optional | `-` | Material Request |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `set_from_warehouse` | Set Source Warehouse | Link | Optional | `-` | Warehouse |
| `set_warehouse` | Set Target Warehouse | Link | Optional | `-` | Warehouse |
| `items` | Items | Table | ✓ Mandatory | `-` | Material Request Item |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions Content | Text Editor | Optional | `-` | - |
| `status` | Status | Select | Optional | `-` | Draft, Submitted, Stopped, Cancelled, Pending, Partially Ordered, Partially R... |
| `per_ordered` | % Ordered | Percent | Optional | `-` | - |
| `transfer_status` | Transfer Status | Select | Optional | `-` | Not Started, In Transit, Completed |
| `per_received` | % Received | Percent | Optional | `-` | - |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `job_card` | Job Card | Link | Optional | `-` | Job Card |
| `work_order` | Work Order | Link | Optional | `-` | Work Order |

### DocType: `Request for Quotation`
- **Submittable**: Yes
- **Total Data Fields**: 31

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | PUR-RFQ-.YYYY.- |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `vendor` | Supplier | Link | Optional | `-` | Supplier |
| `transaction_date` | Date | Date | ✓ Mandatory | `Today` | - |
| `schedule_date` | Required Date | Date | Optional | `-` | - |
| `status` | Status | Select | ✓ Mandatory | `-` | Draft, Submitted, Cancelled |
| `has_unit_price_items` | Has Unit Price Items | Check | Optional | `0` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Request for Quotation |
| `suppliers` | Suppliers | Table | ✓ Mandatory | `-` | Request for Quotation Supplier |
| `items` | Items | Table | ✓ Mandatory | `-` | Request for Quotation Item |
| `email_template` | Email Template | Link | Optional | `-` | Email Template |
| `preview` | Preview Email | Button | Optional | `-` | - |
| `html_llwp` | html_llwp | HTML | Optional | `-` | <p>In your <b>Email Template</b>, you can use the following special variables... |
| `send_attached_files` | Send Attached Files | Check | Optional | `1` | - |
| `send_document_print` | Send Document Print | Check | Optional | `0` | - |
| `subject` | Subject | Data | ✓ Mandatory | `Request for Quotation` | - |
| `use_html` | Use HTML | Check | Optional | `0` | - |
| `message_for_supplier` | Message for Supplier | Text Editor | Optional | `Please supply the specified items at the best possible rates` | - |
| `mfs_html` | Message for Supplier | Code | Optional | `-` | - |
| `incoterm` | Incoterm | Link | Optional | `-` | Incoterm |
| `named_place` | Named Place | Data | Optional | `-` | - |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions | Text Editor | Optional | `-` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `opportunity` | Opportunity | Link | Optional | `-` | Opportunity |
| `title` | Title | Data | Optional | `-` | - |
| `billing_address` | Company Billing Address | Link | Optional | `-` | Address |
| `billing_address_display` | Billing Address Details | Text Editor | Optional | `-` | - |
| `shipping_address` | Company Shipping Address | Link | Optional | `-` | Address |
| `shipping_address_display` | Shipping Address Details | Text Editor | Optional | `-` | - |

### DocType: `Supplier Quotation`
- **Submittable**: Yes
- **Total Data Fields**: 74

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | PUR-SQTN-.YYYY.- |
| `supplier` | Supplier | Link | ✓ Mandatory | `-` | Supplier |
| `supplier_name` | Supplier Name | Data | Optional | `-` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `status` | Status | Select | ✓ Mandatory | `-` | Draft, Submitted, Stopped, Cancelled, Expired |
| `transaction_date` | Date | Date | ✓ Mandatory | `Today` | - |
| `valid_till` | Valid Till | Date | Optional | `-` | - |
| `quotation_number` | Quotation Number | Data | Optional | `-` | - |
| `has_unit_price_items` | Has Unit Price Items | Check | Optional | `0` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Supplier Quotation |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `conversion_rate` | Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `buying_price_list` | Price List | Link | Optional | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | Optional | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | Optional | `-` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `items` | Items | Table | ✓ Mandatory | `-` | Supplier Quotation Item |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total_net_weight` | Total Net Weight | Float | Optional | `-` | - |
| `base_total` | Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_net_total` | Net Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total` | Total | Currency | Optional | `-` | currency |
| `net_total` | Net Total | Currency | Optional | `-` | currency |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes_and_charges` | Purchase Taxes and Charges Template | Link | Optional | `-` | Purchase Taxes and Charges Template |
| `shipping_rule` | Shipping Rule | Link | Optional | `-` | Shipping Rule |
| `incoterm` | Incoterm | Link | Optional | `-` | Incoterm |
| `named_place` | Named Place | Data | Optional | `-` | - |
| `taxes` | Purchase Taxes and Charges | Table | Optional | `-` | Purchase Taxes and Charges |
| `base_taxes_and_charges_added` | Taxes and Charges Added (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_taxes_and_charges_deducted` | Taxes and Charges Deducted (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `taxes_and_charges_added` | Taxes and Charges Added | Currency | Optional | `-` | currency |
| `taxes_and_charges_deducted` | Taxes and Charges Deducted | Currency | Optional | `-` | currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | currency |
| `apply_discount_on` | Apply Additional Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `base_discount_amount` | Additional Discount Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `additional_discount_percentage` | Additional Discount Percentage | Float | Optional | `-` | - |
| `discount_amount` | Additional Discount Amount | Currency | Optional | `-` | currency |
| `base_grand_total` | Grand Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounding_adjustment` | Rounding Adjustment (Company Currency | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounded_total` | Rounded Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_in_words` | In Words (Company Currency) | Data | Optional | `-` | - |
| `grand_total` | Grand Total | Currency | Optional | `-` | currency |
| `rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | currency |
| `rounded_total` | Rounded Total | Currency | Optional | `-` | currency |
| `in_words` | In Words | Data | Optional | `-` | - |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `other_charges_calculation` | Taxes and Charges Calculation | Text Editor | Optional | `-` | - |
| `item_wise_tax_details` | Item Wise Tax Details | Table | Optional | `-` | Item Wise Tax Detail |
| `pricing_rules` | Pricing Rule Detail | Table | Optional | `-` | Pricing Rule Detail |
| `supplier_address` | Supplier Address | Link | Optional | `-` | Address |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `contact_person` | Contact Person | Link | Optional | `-` | Contact |
| `contact_display` | Contact | Small Text | Optional | `-` | - |
| `contact_mobile` | Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Data | Optional | `-` | Email |
| `shipping_address` | Shipping Address | Link | Optional | `-` | Address |
| `shipping_address_display` | Shipping Address Details | Text Editor | Optional | `-` | - |
| `billing_address` | Company Billing Address | Link | Optional | `-` | Address |
| `billing_address_display` | Billing Address Details | Text Editor | Optional | `-` | - |
| `tc_name` | Terms Template | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions | Text Editor | Optional | `-` | - |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `group_same_items` | Group same items | Check | Optional | `0` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `language` | Print Language | Data | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `update_auto_repeat_reference` | Update Auto Repeat Reference | Button | Optional | `-` | - |
| `is_subcontracted` | Is Subcontracted | Check | Optional | `0` | - |
| `title` | Title | Data | Optional | `-` | - |
| `opportunity` | Opportunity | Link | Optional | `-` | Opportunity |

### DocType: `Purchase Order`
- **Submittable**: Yes
- **Total Data Fields**: 106

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | PUR-ORD-.YYYY.- |
| `supplier` | Supplier | Link | ✓ Mandatory | `-` | Supplier |
| `supplier_name` | Supplier Name | Data | Optional | `-` | - |
| `order_confirmation_no` | Order Confirmation No | Data | Optional | `-` | - |
| `order_confirmation_date` | Order Confirmation Date | Date | Optional | `-` | - |
| `transaction_date` | Date | Date | ✓ Mandatory | `Today` | - |
| `transaction_time` | Time | Time | Optional | `Now` | - |
| `schedule_date` | Required By | Date | Optional | `-` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `is_subcontracted` | Is Subcontracted | Check | Optional | `0` | - |
| `has_unit_price_items` | Has Unit Price Items | Check | Optional | `0` | - |
| `supplier_warehouse` | Supplier Warehouse | Link | Optional | `-` | Warehouse |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `conversion_rate` | Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `buying_price_list` | Price List | Link | Optional | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | Optional | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | Optional | `-` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `set_from_warehouse` | Set From Warehouse | Link | Optional | `-` | Warehouse |
| `set_warehouse` | Set Target Warehouse | Link | Optional | `-` | Warehouse |
| `items` | Items | Table | ✓ Mandatory | `-` | Purchase Order Item |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total_net_weight` | Total Net Weight | Float | Optional | `-` | - |
| `base_total` | Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_net_total` | Net Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total` | Total | Currency | Optional | `-` | currency |
| `net_total` | Net Total | Currency | Optional | `-` | currency |
| `pricing_rules` | Purchase Order Pricing Rule | Table | Optional | `-` | Pricing Rule Detail |
| `set_reserve_warehouse` | Set Reserve Warehouse | Link | Optional | `-` | Warehouse |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes_and_charges` | Purchase Taxes and Charges Template | Link | Optional | `-` | Purchase Taxes and Charges Template |
| `shipping_rule` | Shipping Rule | Link | Optional | `-` | Shipping Rule |
| `incoterm` | Incoterm | Link | Optional | `-` | Incoterm |
| `named_place` | Named Place | Data | Optional | `-` | - |
| `taxes` | Purchase Taxes and Charges | Table | Optional | `-` | Purchase Taxes and Charges |
| `base_taxes_and_charges_added` | Taxes and Charges Added (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_taxes_and_charges_deducted` | Taxes and Charges Deducted (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `taxes_and_charges_added` | Taxes and Charges Added | Currency | Optional | `-` | currency |
| `taxes_and_charges_deducted` | Taxes and Charges Deducted | Currency | Optional | `-` | currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | currency |
| `grand_total` | Grand Total | Currency | Optional | `-` | currency |
| `in_words` | In Words | Data | Optional | `-` | - |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | currency |
| `rounded_total` | Rounded Total | Currency | Optional | `-` | currency |
| `base_grand_total` | Grand Total | Currency | Optional | `-` | Company:company:default_currency |
| `base_in_words` | In Words | Data | Optional | `-` | - |
| `base_rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounded_total` | Rounded Total | Currency | Optional | `-` | Company:company:default_currency |
| `advance_paid` | Advance Paid (Company Currency) | Currency | Optional | `-` | party_account_currency |
| `apply_discount_on` | Apply Additional Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `base_discount_amount` | Additional Discount Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `additional_discount_percentage` | Additional Discount Percentage | Float | Optional | `-` | - |
| `discount_amount` | Additional Discount Amount | Currency | Optional | `-` | currency |
| `other_charges_calculation` | Taxes and Charges Calculation | Text Editor | Optional | `-` | - |
| `item_wise_tax_details` | Item Wise Tax Details | Table | Optional | `-` | Item Wise Tax Detail |
| `supplier_address` | Supplier Address | Link | Optional | `-` | Address |
| `address_display` | Supplier Address Details | Text Editor | Optional | `-` | - |
| `supplier_group` | Supplier Group | Link | Optional | `-` | Supplier Group |
| `contact_person` | Supplier Contact | Link | Optional | `-` | Contact |
| `contact_display` | Contact Name | Small Text | Optional | `-` | - |
| `contact_mobile` | Contact Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Small Text | Optional | `-` | Email |
| `dispatch_address` | Dispatch Address | Link | Optional | `-` | Address |
| `dispatch_address_display` | Dispatch Address Details | Text Editor | Optional | `-` | - |
| `shipping_address` | Shipping Address | Link | Optional | `-` | Address |
| `shipping_address_display` | Shipping Address Details | Text Editor | Optional | `-` | - |
| `billing_address` | Company Billing Address | Link | Optional | `-` | Address |
| `billing_address_display` | Billing Address Details | Text Editor | Optional | `-` | - |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `customer_name` | Customer Name | Data | Optional | `-` | - |
| `customer_contact_person` | Customer Contact | Link | Optional | `-` | Contact |
| `customer_contact_display` | Customer Contact | Small Text | Optional | `-` | - |
| `customer_contact_mobile` | Customer Mobile No | Small Text | Optional | `-` | Phone |
| `customer_contact_email` | Customer Contact Email | Code | Optional | `-` | Email |
| `payment_terms_template` | Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `payment_schedule` | Payment Schedule | Table | Optional | `-` | Payment Schedule |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions | Text Editor | Optional | `-` | - |
| `status` | Status | Select | ✓ Mandatory | `Draft` | Draft, On Hold, To Receive and Bill, To Bill, To Receive, Completed, Cancelle... |
| `advance_payment_status` | Advance Payment Status | Select | Optional | `-` | Not Initiated, Initiated, Partially Paid, Fully Paid |
| `per_billed` | % Billed | Percent | Optional | `-` | - |
| `per_received` | % Received | Percent | Optional | `-` | - |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `group_same_items` | Group same items | Check | Optional | `0` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `language` | Print Language | Data | Optional | `-` | - |
| `from_date` | From Date | Date | Optional | `-` | - |
| `to_date` | To Date | Date | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `update_auto_repeat_reference` | Update Auto Repeat Reference | Button | Optional | `-` | - |
| `title` | Title | Data | Optional | `-` | - |
| `party_account_currency` | Party Account Currency | Link | Optional | `-` | Currency |
| `represents_company` | Represents Company | Link | Optional | `-` | Company |
| `ref_sq` | Supplier Quotation | Link | Optional | `-` | Supplier Quotation |
| `amended_from` | Amended From | Link | Optional | `-` | Purchase Order |
| `mps` | MPS | Link | Optional | `-` | Master Production Schedule |
| `is_internal_supplier` | Is Internal Supplier | Check | Optional | `0` | - |
| `inter_company_order_reference` | Inter Company Order Reference | Link | Optional | `-` | Sales Order |
| `is_old_subcontracting_flow` | Is Old Subcontracting Flow | Check | Optional | `0` | - |
| `supplied_items` | Supplied Items | Table | Optional | `-` | Purchase Order Item Supplied |

### DocType: `Purchase Invoice`
- **Submittable**: Yes
- **Total Data Fields**: 137

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | ACC-PINV-.YYYY.-, ACC-PINV-RET-.YYYY.- |
| `supplier` | Supplier | Link | ✓ Mandatory | `-` | Supplier |
| `supplier_name` | Supplier Name | Data | Optional | `-` | - |
| `tax_id` | Tax Id | Read Only | Optional | `-` | - |
| `company` | Company | Link | Optional | `-` | Company |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `posting_time` | Posting Time | Time | Optional | `Now` | - |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `due_date` | Due Date | Date | Optional | `-` | - |
| `is_paid` | Is Paid | Check | Optional | `0` | - |
| `is_return` | Is Return (Debit Note) | Check | Optional | `0` | - |
| `return_against` | Return Against Purchase Invoice | Link | Optional | `-` | Purchase Invoice |
| `update_outstanding_for_self` | Update Outstanding for Self | Check | Optional | `1` | - |
| `update_billed_amount_in_purchase_order` | Update Billed Amount in Purchase Order | Check | Optional | `0` | - |
| `update_billed_amount_in_purchase_receipt` | Update Billed Amount in Purchase Receipt | Check | Optional | `1` | - |
| `apply_tds` | Consider for Tax Withholding | Check | Optional | `0` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Purchase Invoice |
| `bill_no` | Supplier Invoice No | Data | Optional | `-` | - |
| `bill_date` | Supplier Invoice Date | Date | Optional | `-` | - |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `currency` | Currency | Link | Optional | `-` | Currency |
| `conversion_rate` | Exchange Rate | Float | Optional | `-` | - |
| `use_transaction_date_exchange_rate` | Use Transaction Date Exchange Rate | Check | Optional | `0` | - |
| `buying_price_list` | Price List | Link | Optional | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | Optional | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | Optional | `-` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `update_stock` | Update Stock | Check | Optional | `0` | - |
| `set_warehouse` | Set Accepted Warehouse | Link | Optional | `-` | Warehouse |
| `set_from_warehouse` | Set From Warehouse | Link | Optional | `-` | Warehouse |
| `is_subcontracted` | Is Subcontracted | Check | Optional | `0` | - |
| `rejected_warehouse` | Rejected Warehouse | Link | Optional | `-` | Warehouse |
| `supplier_warehouse` | Supplier Warehouse | Link | Optional | `-` | Warehouse |
| `items` | Items | Table | ✓ Mandatory | `-` | Purchase Invoice Item |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total_net_weight` | Total Net Weight | Float | Optional | `-` | - |
| `base_total` | Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_net_total` | Net Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `claimed_landed_cost_amount` | Claimed Landed Cost Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total` | Total | Currency | Optional | `-` | currency |
| `net_total` | Net Total | Currency | Optional | `-` | currency |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes_and_charges` | Purchase Taxes and Charges Template | Link | Optional | `-` | Purchase Taxes and Charges Template |
| `shipping_rule` | Shipping Rule | Link | Optional | `-` | Shipping Rule |
| `incoterm` | Incoterm | Link | Optional | `-` | Incoterm |
| `named_place` | Named Place | Data | Optional | `-` | - |
| `taxes` | Purchase Taxes and Charges | Table | Optional | `-` | Purchase Taxes and Charges |
| `base_taxes_and_charges_added` | Taxes and Charges Added (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_taxes_and_charges_deducted` | Taxes and Charges Deducted (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `taxes_and_charges_added` | Taxes and Charges Added | Currency | Optional | `-` | currency |
| `taxes_and_charges_deducted` | Taxes and Charges Deducted | Currency | Optional | `-` | currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | currency |
| `use_company_roundoff_cost_center` | Use Company Default Round Off Cost Center | Check | Optional | `0` | - |
| `grand_total` | Grand Total | Currency | Optional | `-` | currency |
| `in_words` | In Words | Data | Optional | `-` | - |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | currency |
| `rounded_total` | Rounded Total | Currency | Optional | `-` | currency |
| `base_grand_total` | Grand Total | Currency | Optional | `-` | Company:company:default_currency |
| `base_in_words` | In Words | Data | Optional | `-` | - |
| `base_rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounded_total` | Rounded Total | Currency | Optional | `-` | Company:company:default_currency |
| `total_advance` | Total Advance | Currency | Optional | `-` | party_account_currency |
| `outstanding_amount` | Outstanding Amount | Currency | Optional | `-` | party_account_currency |
| `tax_withholding_group` | Tax Withholding Group | Link | Optional | `-` | Tax Withholding Group |
| `ignore_tax_withholding_threshold` | Ignore Tax Withholding Threshold | Check | Optional | `0` | - |
| `override_tax_withholding_entries` | Edit Tax Withholding Entries | Check | Optional | `0` | - |
| `tax_withholding_entries` | Tax Withholding Entries | Table | Optional | `-` | Tax Withholding Entry |
| `apply_discount_on` | Apply Additional Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `base_discount_amount` | Additional Discount Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `additional_discount_percentage` | Additional Discount Percentage | Float | Optional | `-` | - |
| `discount_amount` | Additional Discount Amount | Currency | Optional | `-` | currency |
| `other_charges_calculation` | Taxes and Charges Calculation | Text Editor | Optional | `-` | - |
| `item_wise_tax_details` | Item Wise Tax Details | Table | Optional | `-` | Item Wise Tax Detail |
| `pricing_rules` | Pricing Rule Detail | Table | Optional | `-` | Pricing Rule Detail |
| `supplied_items` | Supplied Items | Table | Optional | `-` | Purchase Receipt Item Supplied |
| `mode_of_payment` | Mode of Payment | Link | Optional | `-` | Mode of Payment |
| `base_paid_amount` | Paid Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `clearance_date` | Clearance Date | Date | Optional | `-` | - |
| `cash_bank_account` | Cash/Bank Account | Link | Optional | `-` | Account |
| `paid_amount` | Paid Amount | Currency | Optional | `-` | currency |
| `allocate_advances_automatically` | Set Advances and Allocate (FIFO) | Check | Optional | `0` | - |
| `only_include_allocated_payments` | Only Include Allocated Payments | Check | Optional | `0` | - |
| `get_advances` | Get Advances Paid | Button | Optional | `-` | set_advances |
| `advances` | Advances | Table | Optional | `-` | Purchase Invoice Advance |
| `write_off_amount` | Write Off Amount | Currency | Optional | `-` | currency |
| `base_write_off_amount` | Write Off Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `write_off_account` | Write Off Account | Link | Optional | `-` | Account |
| `write_off_cost_center` | Write Off Cost Center | Link | Optional | `-` | Cost Center |
| `supplier_address` | Select Supplier Address | Link | Optional | `-` | Address |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `contact_person` | Contact Person | Link | Optional | `-` | Contact |
| `contact_display` | Contact | Small Text | Optional | `-` | - |
| `contact_mobile` | Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Small Text | Optional | `-` | Email |
| `dispatch_address` | Select Dispatch Address  | Link | Optional | `-` | Address |
| `dispatch_address_display` | Dispatch Address | Text Editor | Optional | `-` | - |
| `shipping_address` | Select Shipping Address | Link | Optional | `-` | Address |
| `shipping_address_display` | Shipping Address | Text Editor | Optional | `-` | - |
| `billing_address` | Select Billing Address | Link | Optional | `-` | Address |
| `billing_address_display` | Billing Address | Text Editor | Optional | `-` | - |
| `payment_terms_template` | Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `ignore_default_payment_terms_template` | Ignore Default Payment Terms Template | Check | Optional | `0` | - |
| `payment_schedule` | Payment Schedule | Table | Optional | `-` | Payment Schedule |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions | Text Editor | Optional | `-` | - |
| `status` | Status | Select | Optional | `Draft` | Draft, Return, Debit Note Issued, Submitted, Paid, Partly Paid, Unpaid, Overd... |
| `per_received` | Per Received | Percent | Optional | `-` | - |
| `credit_to` | Credit To | Link | ✓ Mandatory | `-` | Account |
| `party_account_currency` | Party Account Currency | Link | Optional | `-` | Currency |
| `is_opening` | Is Opening Entry | Select | Optional | `No` | No, Yes |
| `against_expense_account` | Against Expense Account | Small Text | Optional | `-` | - |
| `unrealized_profit_loss_account` | Unrealized Profit / Loss Account | Link | Optional | `-` | Account |
| `subscription` | Subscription | Link | Optional | `-` | Subscription |
| `from_date` | From Date | Date | Optional | `-` | - |
| `to_date` | To Date | Date | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `update_auto_repeat_reference` | Update Auto Repeat Reference | Button | Optional | `-` | - |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `group_same_items` | Group same items | Check | Optional | `0` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `language` | Print Language | Data | Optional | `-` | - |
| `on_hold` | Hold Invoice | Check | Optional | `0` | - |
| `release_date` | Release Date | Date | Optional | `-` | - |
| `hold_comment` | Reason For Putting On Hold | Small Text | Optional | `-` | - |
| `is_internal_supplier` | Is Internal Supplier | Check | Optional | `0` | - |
| `title` | Title | Data | Optional | `-` | - |
| `represents_company` | Represents Company | Link | Optional | `-` | Company |
| `supplier_group` | Supplier Group | Link | Optional | `-` | Supplier Group |
| `sender` | Sender | Data | Optional | `-` | Email |
| `inter_company_invoice_reference` | Inter Company Invoice Reference | Link | Optional | `-` | Sales Invoice |
| `is_old_subcontracting_flow` | Is Old Subcontracting Flow | Check | Optional | `0` | - |
| `remarks` | Remarks | Small Text | Optional | `-` | - |

### DocType: `Supplier`
- **Submittable**: No
- **Total Data Fields**: 44

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | Optional | `-` | SUP-.YYYY.- |
| `supplier_name` | Supplier Name | Data | ✓ Mandatory | `-` | - |
| `supplier_type` | Supplier Type | Select | ✓ Mandatory | `Company` | Company, Individual, Partnership |
| `alias` | Alias | Data | Optional | `-` | - |
| `gender` | Gender | Link | Optional | `-` | Gender |
| `supplier_group` | Supplier Group | Link | Optional | `-` | Supplier Group |
| `country` | Country | Link | Optional | `-` | Country |
| `image` | Image | Attach Image | Optional | `-` | - |
| `default_currency` | Billing Currency | Link | Optional | `-` | Currency |
| `default_bank_account` | Company Bank Account | Link | Optional | `-` | Bank Account |
| `default_price_list` | Price List | Link | Optional | `-` | Price List |
| `payment_terms` | Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `address_html` | Address HTML | HTML | Optional | `-` | - |
| `contact_html` | Contact HTML | HTML | Optional | `-` | - |
| `supplier_primary_address` | Primary Address | Link | Optional | `-` | Address |
| `primary_address` | Primary Address Preview | Text Editor | Optional | `-` | - |
| `supplier_primary_contact` | Primary Contact | Link | Optional | `-` | Contact |
| `mobile_no` | Mobile No | Read Only | Optional | `-` | - |
| `email_id` | Email ID | Read Only | Optional | `-` | - |
| `accounts` | Per-Company Accounts | Table | Optional | `-` | Party Account |
| `is_internal_supplier` | Is Internal Supplier | Check | Optional | `0` | - |
| `represents_company` | Represents Company | Link | Optional | `-` | Company |
| `companies` | Allowed to transact with | Table | Optional | `-` | Allowed To Transact With |
| `tax_id` | Tax ID | Data | Optional | `-` | - |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `tax_withholding_category` | Tax Withholding Category | Link | Optional | `-` | Tax Withholding Category |
| `tax_withholding_group` | Tax Withholding Group | Link | Optional | `-` | Tax Withholding Group |
| `is_transporter` | Is Transporter | Check | Optional | `0` | - |
| `allow_purchase_invoice_creation_without_purchase_order` | Allow purchase invoice creation without purchase order | Check | Optional | `0` | - |
| `allow_purchase_invoice_creation_without_purchase_receipt` | Allow purchase invoice creation without purchase receipt | Check | Optional | `0` | - |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `is_frozen` | Is Frozen | Check | Optional | `0` | - |
| `on_hold` | Block Supplier | Check | Optional | `0` | - |
| `hold_type` | Hold Type | Select | Optional | `All` | All, Invoices, Payments |
| `release_date` | Release Date | Date | Optional | `-` | - |
| `warn_rfqs` | Warn RFQs | Check | Optional | `0` | - |
| `prevent_rfqs` | Prevent RFQs | Check | Optional | `0` | - |
| `warn_pos` | Warn POs | Check | Optional | `0` | - |
| `prevent_pos` | Prevent POs | Check | Optional | `0` | - |
| `portal_users` | Supplier Portal Users | Table | Optional | `-` | Portal User |
| `website` | Website | Data | Optional | `-` | - |
| `language` | Print Language | Link | Optional | `-` | Language |
| `supplier_details` | Supplier Details | Text | Optional | `-` | - |
| `customer_numbers` | Customer Numbers | Table | Optional | `-` | Customer Number At Supplier |

### DocType: `Supplier Group`
- **Submittable**: No
- **Total Data Fields**: 8

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `supplier_group_name` | Supplier Group Name | Data | ✓ Mandatory | `-` | - |
| `parent_supplier_group` | Parent Supplier Group | Link | Optional | `-` | Supplier Group |
| `is_group` | Is Group | Check | Optional | `0` | - |
| `payment_terms` | Default Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `accounts` | Accounts | Table | Optional | `-` | Party Account |
| `lft` | lft | Int | Optional | `-` | - |
| `rgt` | rgt | Int | Optional | `-` | - |
| `old_parent` | Old Parent | Link | Optional | `-` | Supplier Group |

### DocType: `Price List`
- **Submittable**: No
- **Total Data Fields**: 7

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `enabled` | Enabled | Check | Optional | `1` | - |
| `price_list_name` | Price List Name | Data | ✓ Mandatory | `-` | - |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `buying` | Buying | Check | Optional | `0` | - |
| `selling` | Selling | Check | Optional | `0` | - |
| `price_not_uom_dependent` | Price Not UOM Dependent | Check | Optional | `0` | - |
| `countries` | Applicable for Countries | Table | Optional | `-` | Price List Country |

### DocType: `Supplier Scorecard`
- **Submittable**: No
- **Total Data Fields**: 16

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `supplier` | Supplier | Link | Optional | `-` | Supplier |
| `supplier_score` | Supplier Score | Data | Optional | `-` | - |
| `indicator_color` | Indicator Color | Data | Optional | `-` | - |
| `status` | Status | Data | Optional | `-` | - |
| `period` | Evaluation Period | Select | ✓ Mandatory | `Per Month` | Per Week, Per Month, Per Year |
| `weighting_function` | Weighting Function | Small Text | ✓ Mandatory | `{total_score} * max( 0, min ( 1 , (12 - {period_number}) / 12) )` | - |
| `standings` | Scoring Standings | Table | ✓ Mandatory | `-` | Supplier Scorecard Scoring Standing |
| `load_criteria` | Load All Criteria | Button | Optional | `-` | - |
| `criteria` | Scoring Criteria | Table | ✓ Mandatory | `-` | Supplier Scorecard Scoring Criteria |
| `warn_rfqs` | Warn for new Request for Quotations | Check | Optional | `0` | - |
| `warn_pos` | Warn for new Purchase Orders | Check | Optional | `0` | - |
| `prevent_rfqs` | Prevent RFQs | Check | Optional | `0` | - |
| `prevent_pos` | Prevent POs | Check | Optional | `0` | - |
| `notify_supplier` | Notify Supplier | Check | Optional | `0` | - |
| `notify_employee` | Notify Employee | Check | Optional | `0` | - |
| `employee` | Employee | Link | Optional | `-` | Employee |

### DocType: `Buying Settings`
- **Submittable**: No
- **Total Data Fields**: 31

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `supp_master_name` | Supplier Naming By | Select | Optional | `Supplier Name` | Supplier Name, Naming Series, Auto Name |
| `naming_series_details` | Naming Series options | Small Text | Optional | `-` | - |
| `configure` | Configure Series | Button | Optional | `-` | - |
| `supplier_group` | Default Supplier Group | Link | Optional | `-` | Supplier Group |
| `buying_price_list` | Default Buying Price List | Link | Optional | `-` | Price List |
| `maintain_same_rate` | Maintain same rate throughout the purchase  cycle | Check | Optional | `0` | - |
| `set_landed_cost_based_on_purchase_invoice_rate` | Set Landed Cost Based on Purchase Invoice Rate | Check | Optional | `0` | - |
| `maintain_same_rate_action` | Action if same rate is not maintained | Select | Optional | `Stop` | Stop, Warn |
| `role_to_override_stop_action` | Role allowed to override stop action | Link | Optional | `-` | Role |
| `po_required` | Is Purchase Order required for Purchase Invoice & Receipt creation? | Select | Optional | `-` | No, Yes |
| `pr_required` | Is Purchase Receipt required for Purchase Invoice creation? | Select | Optional | `-` | No, Yes |
| `project_update_frequency` | How often should project be updated of Total Purchase Cost ? | Select | Optional | `Each Transaction` | Each Transaction, Manual |
| `over_order_allowance` | Over Order Allowance (%) | Float | Optional | `-` | - |
| `allow_multiple_items` | Allow Item to be added multiple times in a transaction | Check | Optional | `0` | - |
| `allow_negative_rates_for_items` | Allow negative rates for Items | Check | Optional | `0` | - |
| `set_valuation_rate_for_rejected_materials` | Set valuation rate for rejected Materials | Check | Optional | `0` | - |
| `disable_last_purchase_rate` | Disable last purchase rate | Check | Optional | `0` | - |
| `show_pay_button` | Show pay button in Purchase Order portal | Check | Optional | `1` | - |
| `bill_for_rejected_quantity_in_purchase_invoice` | Bill for rejected quantity in Purchase Invoice | Check | Optional | `1` | - |
| `use_transaction_date_exchange_rate` | Use Transaction Date Exchange Rate | Check | Optional | `0` | - |
| `allow_zero_qty_in_supplier_quotation` | Allow Supplier Quotation with Zero Quantity | Check | Optional | `0` | - |
| `allow_zero_qty_in_request_for_quotation` | Allow Request for Quotation with Zero Quantity | Check | Optional | `0` | - |
| `allow_zero_qty_in_purchase_order` | Allow Purchase Order with Zero Quantity | Check | Optional | `0` | - |
| `blanket_order_allowance` | Blanket Order Allowance (%) | Float | Optional | `0` | - |
| `backflush_raw_materials_of_subcontract_based_on` | Backflush raw materials of subcontract based on | Select | Optional | `BOM` | BOM, Material Transferred for Subcontract |
| `over_transfer_allowance` | Over Transfer Allowance (%) | Float | Optional | `-` | - |
| `validate_consumed_qty` | Validate consumed quantity (as per BOM) | Check | Optional | `0` | - |
| `auto_create_subcontracting_order` | Auto create Subcontracting Order | Check | Optional | `0` | - |
| `auto_create_purchase_receipt` | Auto create Purchase Receipt | Check | Optional | `0` | - |
| `fixed_email` | Fixed Outgoing Email Account | Link | Optional | `-` | Email Account |
| `transaction_naming_html` | transaction_naming_html | HTML | Optional | `-` | - |

## Module: Manufacturing
*Discrete and project-based manufacturing, multi-level BOMs with custom Sarathi project locking, Work Orders, Job Card time logs driving live status, workstations, and routing.*

### Summary of DocTypes in Manufacturing:
- **BOM**: 58 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Work Order**: 59 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Job Card**: 59 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Stock Entry**: 60 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Item Lead Time**: 13 fields | Submittable: No
- **Production Plan**: 42 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Master Production Schedule**: 15 fields | Submittable: No
- **Sales Forecast**: 12 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **BOM Creator**: 24 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Downtime Entry**: 8 fields | Submittable: No
- **Operation**: 8 fields | Submittable: No
- **Workstation**: 16 fields | Submittable: No
- **Workstation Type**: 4 fields | Submittable: No
- **Plant Floor**: 5 fields | Submittable: No
- **Routing**: 3 fields | Submittable: No
- **Manufacturing Settings**: 19 fields | Submittable: No

### DocType: `BOM`
- **Submittable**: Yes
- **Total Data Fields**: 58

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `custom_sarathi_project` | Sarathi Project | Link | Optional | `-` | Project |
| `item` | Item to Manufacture | Link | ✓ Mandatory | `-` | Item |
| `quantity` | Quantity (Output Qty) | Float | ✓ Mandatory | `1` | - |
| `uom` | Unit Of Measure | Link | Optional | `-` | UOM |
| `cost_allocation_per` | % Cost Allocation | Percent | Optional | `100` | - |
| `cost_allocation` | Cost Allocation | Currency | Optional | `-` | currency |
| `process_loss_percentage` | % Process Loss | Percent | Optional | `-` | - |
| `process_loss_qty` | Process Loss Qty | Float | Optional | `-` | - |
| `with_operations` | With Operations | Check | Optional | `0` | - |
| `track_semi_finished_goods` | Track Semi Finished Goods | Check | Optional | `0` | - |
| `transfer_material_against` | Transfer Material Against | Select | Optional | `Work Order` | Work Order, Job Card |
| `routing` | Routing | Link | Optional | `-` | Routing |
| `fg_based_operating_cost` | Finished Goods based Operating Cost | Check | Optional | `0` | - |
| `operating_cost_per_bom_quantity` | Operating Cost Per BOM Quantity | Currency | Optional | `-` | - |
| `operations` | Operations | Table | Optional | `-` | BOM Operation |
| `items` | Components | Table | ✓ Mandatory | `-` | BOM Item |
| `secondary_items` | Secondary Items | Table | Optional | `-` | BOM Secondary Item |
| `is_active` | Is Active | Check | Optional | `1` | - |
| `is_default` | Is Default | Check | Optional | `1` | - |
| `set_rate_of_sub_assembly_item_based_on_bom` | Set rate of sub-assembly item based on BOM | Check | Optional | `1` | - |
| `is_phantom_bom` | Is Phantom BOM | Check | Optional | `0` | - |
| `allow_alternative_item` | Allow Alternative Item | Check | Optional | `0` | - |
| `inspection_required` | Quality Inspection Required | Check | Optional | `0` | - |
| `quality_inspection_template` | Quality Inspection Template | Link | Optional | `-` | Quality Inspection Template |
| `default_source_warehouse` | Default Source Warehouse | Link | Optional | `-` | Warehouse |
| `default_target_warehouse` | Default Target Warehouse | Link | Optional | `-` | Warehouse |
| `backflush_based_on` | Based On | Select | Optional | `-` | BOM, Material Transferred for Manufacture |
| `operating_cost` | Operating Cost | Currency | Optional | `-` | currency |
| `raw_material_cost` | Raw Material Cost | Currency | Optional | `-` | currency |
| `secondary_items_cost` | Secondary Items Cost | Currency | Optional | `-` | currency |
| `base_operating_cost` | Operating Cost (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_raw_material_cost` | Raw Material Cost (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_secondary_items_cost` | Secondary Items Cost (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total_cost` | Total Cost | Currency | Optional | `-` | currency |
| `base_total_cost` | Total Cost (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `rm_cost_as_per` | Rate Of Materials Based On | Select | Optional | `Valuation Rate` | Valuation Rate, Last Purchase Rate, Price List |
| `buying_price_list` | Price List | Link | Optional | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | Optional | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | Optional | `-` | - |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `conversion_rate` | Conversion Rate | Float | ✓ Mandatory | `1` | - |
| `item_name` | Item Name | Data | Optional | `-` | - |
| `image` | Image | Attach Image | Optional | `-` | image |
| `description` | Item Description | Small Text | Optional | `-` | - |
| `has_variants` | Has Variants | Check | Optional | `0` | - |
| `project` | Project | Link | Optional | `-` | Project |
| `exploded_items` | Exploded Items | Table | Optional | `-` | BOM Explosion Item |
| `show_in_website` | Show in Website | Check | Optional | `0` | - |
| `route` | Route | Small Text | Optional | `-` | - |
| `website_image` | Website Image | Attach Image | Optional | `-` | - |
| `thumbnail` | Thumbnail | Data | Optional | `-` | - |
| `show_items` | Show Items | Check | Optional | `0` | - |
| `show_operations` | Show Operations | Check | Optional | `0` | - |
| `web_long_description` | Website Description | Text Editor | Optional | `-` | - |
| `bom_creator` | BOM Creator | Link | Optional | `-` | BOM Creator |
| `bom_creator_item` | BOM Creator Item | Data | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | BOM |

### DocType: `Work Order`
- **Submittable**: Yes
- **Total Data Fields**: 59

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | MFG-WO-.YYYY.- |
| `production_item` | Item To Manufacture | Link | ✓ Mandatory | `-` | Item |
| `bom_no` | BOM No | Link | ✓ Mandatory | `-` | BOM |
| `qty` | Qty To Manufacture | Float | ✓ Mandatory | `1.0` | - |
| `sales_order` | Sales Order | Link | Optional | `-` | Sales Order |
| `reserve_stock` | Reserve Stock | Check | Optional | `0` | - |
| `max_producible_qty` | Max Producible Qty | Float | Optional | `-` | - |
| `material_transferred_for_manufacturing` | Material Transferred for Manufacturing | Float | Optional | `0` | - |
| `additional_transferred_qty` | Additional Transferred Qty | Float | Optional | `0` | - |
| `produced_qty` | Manufactured Qty | Float | Optional | `0` | - |
| `process_loss_qty` | Process Loss Qty | Float | Optional | `-` | - |
| `disassembled_qty` | Disassembled Qty | Float | Optional | `-` | - |
| `source_warehouse` | Source Warehouse | Link | Optional | `-` | Warehouse |
| `wip_warehouse` | Work-in-Progress Warehouse | Link | Optional | `-` | Warehouse |
| `fg_warehouse` | Target Warehouse | Link | Optional | `-` | Warehouse |
| `scrap_warehouse` | Scrap Warehouse | Link | Optional | `-` | Warehouse |
| `transfer_material_against` | Transfer Material Against | Select | Optional | `-` | Work Order, Job Card |
| `operations` | Operations | Table | Optional | `-` | Work Order Operation |
| `required_items` | required_items | Table | Optional | `-` | Work Order Item |
| `allow_alternative_item` | Allow Alternative Item | Check | Optional | `0` | - |
| `use_multi_level_bom` | Use Multi-Level BOM | Check | Optional | `1` | - |
| `skip_transfer` | Skip Material Transfer to WIP Warehouse | Check | Optional | `0` | - |
| `from_wip_warehouse` | Backflush Raw Materials From Work-in-Progress Warehouse | Check | Optional | `0` | - |
| `update_consumed_material_cost_in_project` | Update Consumed Material Cost In Project | Check | Optional | `1` | - |
| `planned_start_date` | Planned Start Date | Datetime | ✓ Mandatory | `now` | - |
| `planned_end_date` | Planned End Date | Datetime | Optional | `-` | - |
| `expected_delivery_date` | Expected Delivery Date | Date | Optional | `-` | - |
| `actual_start_date` | Actual Start Date | Datetime | Optional | `-` | - |
| `actual_end_date` | Actual End Date | Datetime | Optional | `-` | - |
| `lead_time` | Lead Time | Float | Optional | `-` | - |
| `planned_operating_cost` | Planned Operating Cost | Currency | Optional | `-` | Company:company:default_currency |
| `actual_operating_cost` | Actual Operating Cost | Currency | Optional | `-` | Company:company:default_currency |
| `additional_operating_cost` | Additional Operating Cost | Currency | Optional | `-` | Company:company:default_currency |
| `corrective_operation_cost` | Corrective Operation Cost | Currency | Optional | `-` | - |
| `total_operating_cost` | Total Operating Cost | Currency | Optional | `-` | Company:company:default_currency |
| `image` | Image | Attach Image | Optional | `-` | image |
| `item_name` | Item Name | Data | Optional | `-` | - |
| `stock_uom` | Stock UOM | Link | Optional | `-` | UOM |
| `description` | Item Description | Small Text | Optional | `-` | - |
| `has_serial_no` | Has Serial No | Check | Optional | `0` | - |
| `has_batch_no` | Has Batch No | Check | Optional | `0` | - |
| `batch_size` | Batch Size | Float | Optional | `0` | - |
| `non_stock_items` | Additional Costs (as per BOM) | Table | Optional | `-` | Work Order Additional Item |
| `secondary_items` | Secondary Items (as per BOM) | Table | Optional | `-` | Work Order Additional Item |
| `project` | Project | Link | Optional | `-` | Project |
| `subcontracting_inward_order` | Subcontracting Inward Order | Link | Optional | `-` | Subcontracting Inward Order |
| `production_plan` | Production Plan | Link | Optional | `-` | Production Plan |
| `mps` | MPS | Link | Optional | `-` | Master Production Schedule |
| `material_request` | Material Request | Link | Optional | `-` | Material Request |
| `material_request_item` | Material Request Item | Data | Optional | `-` | - |
| `subcontracting_inward_order_item` | Subcontracting Inward Order Item | Data | Optional | `-` | - |
| `sales_order_item` | Sales Order Item | Data | Optional | `-` | - |
| `production_plan_sub_assembly_item` | Production Plan Sub Assembly Item | Data | Optional | `-` | - |
| `production_plan_item` | Production Plan Item | Data | Optional | `-` | - |
| `product_bundle_item` | Product Bundle Item | Link | Optional | `-` | Item |
| `status` | Status | Select | ✓ Mandatory | `Draft` | Draft, Submitted, Not Started, In Process, Stock Reserved, Stock Partially Re... |
| `track_semi_finished_goods` | Track Semi Finished Goods | Check | Optional | `0` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Work Order |

### DocType: `Job Card`
- **Submittable**: Yes
- **Total Data Fields**: 59

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `job_card_dashboard` | job_card_dashboard | HTML | Optional | `-` | - |
| `work_order` | Work Order | Link | ✓ Mandatory | `-` | Work Order |
| `production_item` | Final Product | Link | Optional | `-` | Item |
| `bom_no` | Final BOM | Link | Optional | `-` | BOM |
| `for_quantity` | Qty To Manufacture | Float | Optional | `-` | - |
| `stock_uom` | Stock UOM | Link | Optional | `-` | UOM |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `naming_series` | Naming Series | Select | ✓ Mandatory | `PO-JOB.#####` | PO-JOB.##### |
| `posting_date` | Posting Date | Date | Optional | `Today` | - |
| `finished_good` | Item to Manufacture | Link | Optional | `-` | Item |
| `semi_fg_bom` | Manufacturing BOM | Link | Optional | `-` | BOM |
| `pending_qty` | Pending Qty | Float | Optional | `-` | - |
| `process_loss_qty` | Process Loss Qty | Float | Optional | `-` | - |
| `total_completed_qty` | Total Completed Qty | Float | Optional | `0` | - |
| `transferred_qty` | Transferred Raw Materials | Float | Optional | `0` | - |
| `manufactured_qty` | Manufactured Qty | Float | Optional | `-` | - |
| `operation` | Operation | Link | ✓ Mandatory | `-` | Operation |
| `source_warehouse` | Source Warehouse | Link | Optional | `-` | Warehouse |
| `wip_warehouse` | WIP Warehouse | Link | Optional | `-` | Warehouse |
| `skip_material_transfer` | Skip Material Transfer to WIP | Check | Optional | `0` | - |
| `backflush_from_wip_warehouse` | Backflush Materials From WIP Warehouse | Check | Optional | `0` | - |
| `workstation_type` | Workstation Type | Link | Optional | `-` | Workstation Type |
| `workstation` | Workstation | Link | ✓ Mandatory | `-` | Workstation |
| `target_warehouse` | Target Warehouse | Link | Optional | `-` | Warehouse |
| `employee` | Employee | Table MultiSelect | Optional | `-` | Job Card Time Log |
| `items` | Items | Table | Optional | `-` | Job Card Item |
| `quality_inspection_template` | Quality Inspection Template | Link | Optional | `-` | Quality Inspection Template |
| `quality_inspection` | Quality Inspection | Link | Optional | `-` | Quality Inspection |
| `expected_start_date` | Expected Start Date | Datetime | Optional | `-` | - |
| `time_required` | Expected Time Required (In Mins) | Float | Optional | `-` | - |
| `expected_end_date` | Expected End Date | Datetime | Optional | `-` | - |
| `scheduled_time_logs` | Scheduled Time Logs | Table | Optional | `-` | Job Card Scheduled Time |
| `actual_start_date` | Actual Start Date | Datetime | Optional | `-` | - |
| `total_time_in_mins` | Total Time in Mins | Float | Optional | `-` | - |
| `actual_end_date` | Actual End Date | Datetime | Optional | `-` | - |
| `time_logs` | Time Logs | Table | Optional | `-` | Job Card Time Log |
| `sub_operations` | Sub Operations | Table | Optional | `-` | Job Card Operation |
| `secondary_items` | Secondary Items | Table | Optional | `-` | Job Card Secondary Item |
| `for_job_card` | For Job Card | Link | Optional | `-` | Job Card |
| `is_corrective_job_card` | Is Corrective Job Card | Check | Optional | `0` | - |
| `hour_rate` | Hour Rate | Currency | Optional | `-` | - |
| `for_operation` | For Operation | Link | Optional | `-` | Operation |
| `item_name` | Item Name | Read Only | Optional | `-` | - |
| `requested_qty` | Requested Qty | Float | Optional | `0` | - |
| `is_paused` | Is Paused | Check | Optional | `0` | - |
| `is_subcontracted` |  Is Subcontracted | Check | Optional | `0` | - |
| `track_semi_finished_goods` | Track Semi Finished Goods | Check | Optional | `0` | - |
| `project` | Project | Link | Optional | `-` | Project |
| `remarks` | Remarks | Small Text | Optional | `-` | - |
| `status` | Status | Select | Optional | `Open` | Open, Work In Progress, Partially Transferred, Material Transferred, On Hold,... |
| `operation_row_id` | Operation Row ID | Int | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Job Card |
| `operation_row_number` | Operation Row Number | Select | Optional | `-` | - |
| `operation_id` | Operation ID | Data | Optional | `-` | - |
| `sequence_id` | Sequence Id | Int | Optional | `-` | - |
| `serial_no` | Serial No | Small Text | Optional | `-` | - |
| `serial_and_batch_bundle` | Serial and Batch Bundle | Link | Optional | `-` | Serial and Batch Bundle |
| `barcode` | Barcode | Barcode | Optional | `-` | - |
| `batch_no` | Batch No | Link | Optional | `-` | Batch |

### DocType: `Stock Entry`
- **Submittable**: Yes
- **Total Data Fields**: 60

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | MAT-STE-.YYYY.- |
| `stock_entry_type` | Stock Entry Type | Link | ✓ Mandatory | `-` | Stock Entry Type |
| `purpose` | Purpose | Select | Optional | `-` | Material Issue, Material Receipt, Material Transfer, Material Transfer for Ma... |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `posting_date` | Posting Date | Date | Optional | `Today` | - |
| `posting_time` | Posting Time | Time | Optional | `Now` | - |
| `add_to_transit` | Add to Transit | Check | Optional | `0` | - |
| `apply_putaway_rule` | Apply Putaway Rule | Check | Optional | `0` | - |
| `inspection_required` | Inspection Required | Check | Optional | `0` | - |
| `work_order` | Work Order | Link | Optional | `-` | Work Order |
| `subcontracting_order` | Subcontracting Order | Link | Optional | `-` | Subcontracting Order |
| `outgoing_stock_entry` | Stock Entry (Outward GIT) | Link | Optional | `-` | Stock Entry |
| `source_stock_entry` | Source Stock Entry (Manufacture) | Link | Optional | `-` | Stock Entry |
| `from_bom` | From BOM | Check | Optional | `0` | - |
| `use_multi_level_bom` | Use Multi-Level BOM | Check | Optional | `1` | - |
| `bom_no` | BOM No | Link | Optional | `-` | BOM |
| `fg_completed_qty` | Finished Good Quantity  | Float | Optional | `-` | - |
| `get_items` | Get Items | Button | Optional | `-` | - |
| `process_loss_percentage` | % Process Loss | Percent | Optional | `-` | - |
| `process_loss_qty` | Process Loss Qty | Float | Optional | `-` | - |
| `from_warehouse` | Default Source Warehouse | Link | Optional | `-` | Warehouse |
| `source_warehouse_address` | Source Warehouse Address Link | Link | Optional | `-` | Address |
| `source_address_display` | Source Warehouse Address | Text Editor | Optional | `-` | - |
| `to_warehouse` | Default Target Warehouse | Link | Optional | `-` | Warehouse |
| `target_warehouse_address` | Target Warehouse Address Link | Link | Optional | `-` | Address |
| `target_address_display` | Target Warehouse Address | Text Editor | Optional | `-` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `items` | Items | Table | ✓ Mandatory | `-` | Stock Entry Detail |
| `get_stock_and_rate` | Update Rate and Availability | Button | Optional | `-` | get_stock_and_rate |
| `total_outgoing_value` | Total Outgoing Value (Consumption) | Currency | Optional | `-` | Company:company:default_currency |
| `total_incoming_value` | Total Incoming Value (Receipt) | Currency | Optional | `-` | Company:company:default_currency |
| `value_difference` | Total Value Difference (Incoming - Outgoing) | Currency | Optional | `-` | Company:company:default_currency |
| `additional_costs` | Additional Costs | Table | Optional | `-` | Landed Cost Taxes and Charges |
| `total_additional_costs` | Total Additional Costs | Currency | Optional | `-` | Company:company:default_currency |
| `supplier` | Supplier | Link | Optional | `-` | Supplier |
| `supplier_name` | Supplier Name | Data | Optional | `-` | - |
| `supplier_address` | Supplier Address | Link | Optional | `-` | Address |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `project` | Project | Link | Optional | `-` | Project |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `delivery_note_no` | Delivery Note No | Link | Optional | `-` | Delivery Note |
| `sales_invoice_no` | Sales Invoice No | Link | Optional | `-` | Sales Invoice |
| `job_card` | Job Card | Link | Optional | `-` | Job Card |
| `pick_list` | Pick List | Link | Optional | `-` | Pick List |
| `asset_repair` | Asset Repair | Link | Optional | `-` | Asset Repair |
| `purchase_receipt_no` | Purchase Receipt No | Link | Optional | `-` | Purchase Receipt |
| `purchase_order` | Purchase Order | Link | Optional | `-` | Purchase Order |
| `subcontracting_inward_order` | Subcontracting Inward Order | Link | Optional | `-` | Subcontracting Inward Order |
| `is_additional_transfer_entry` | Is Additional Transfer Entry | Check | Optional | `0` | - |
| `is_opening` | Is Opening | Select | Optional | `-` | No, Yes |
| `remarks` | Remarks | Text | Optional | `-` | - |
| `per_transferred` | Per Transferred | Percent | Optional | `-` | - |
| `total_amount` | Total Amount | Currency | Optional | `-` | Company:company:default_currency |
| `amended_from` | Amended From | Link | Optional | `-` | Stock Entry |
| `credit_note` | Credit Note | Link | Optional | `-` | Journal Entry |
| `is_return` | Is Return | Check | Optional | `0` | - |

### DocType: `Item Lead Time`
- **Submittable**: No
- **Total Data Fields**: 13

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `item_code` | Item Code | Link | Optional | `-` | Item |
| `shift_time_in_hours` | Shift Time (In Hours) | Int | Optional | `-` | - |
| `no_of_workstations` | No of Workstations | Int | Optional | `-` | - |
| `no_of_shift` | No of Shift | Int | Optional | `1` | - |
| `total_workstation_time` | Total Workstation Time (In Hours) | Int | Optional | `-` | - |
| `manufacturing_time_in_mins` | Manufacturing Time | Int | Optional | `-` | - |
| `no_of_units_produced` | No of Units Produced | Int | Optional | `-` | - |
| `daily_yield` | Daily Yield (%) | Percent | Optional | `90` | - |
| `capacity_per_day` | Capacity | Int | Optional | `-` | - |
| `purchase_time` | Purchase Time | Int | Optional | `-` | - |
| `buffer_time` | Buffer Time | Int | Optional | `-` | - |
| `item_name` | Item Name | Data | Optional | `-` | - |
| `stock_uom` | Stock UOM | Link | Optional | `-` | UOM |

### DocType: `Production Plan`
- **Submittable**: Yes
- **Total Data Fields**: 42

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Naming Series | Select | ✓ Mandatory | `-` | MFG-PP-.YYYY.- |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `get_items_from` | Get Items From | Select | Optional | `-` | Sales Order, Material Request |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `reserve_stock` | Reserve Stock | Check | Optional | `0` | - |
| `item_code` | Item Code | Link | Optional | `-` | Item |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `warehouse` | Warehouse | Link | Optional | `-` | Warehouse |
| `project` | Project | Link | Optional | `-` | Project |
| `sales_order_status` | Sales Order Status | Select | Optional | `-` | To Deliver and Bill, To Bill, To Deliver |
| `from_date` | From Date | Date | Optional | `-` | - |
| `to_date` | To Date | Date | Optional | `-` | - |
| `from_delivery_date` | From Delivery Date | Date | Optional | `-` | - |
| `to_delivery_date` | To Delivery Date | Date | Optional | `-` | - |
| `combine_items` | Consolidate Sales Order Items | Check | Optional | `0` | - |
| `get_sales_orders` | Get Sales Orders | Button | Optional | `-` | - |
| `sales_orders` | Sales Orders | Table | Optional | `-` | Production Plan Sales Order |
| `get_material_request` | Get Material Request | Button | Optional | `-` | - |
| `material_requests` | Material Requests | Table | Optional | `-` | Production Plan Material Request |
| `get_items` | Get Finished Goods | Button | Optional | `-` | - |
| `po_items` | Assembly Items | Table | ✓ Mandatory | `-` | Production Plan Item |
| `prod_plan_references` | Production Plan Item Reference | Table | Optional | `-` | Production Plan Item Reference |
| `sub_assembly_warehouse` | Sub Assembly Warehouse | Link | Optional | `-` | Warehouse |
| `skip_available_sub_assembly_item` | Consider Projected Qty in Calculation | Check | Optional | `1` | - |
| `combine_sub_items` | Consolidate Sub Assembly Items | Check | Optional | `0` | - |
| `get_sub_assembly_items` | Get Sub Assembly Items | Button | Optional | `-` | - |
| `sub_assembly_items` | sub_assembly_items | Table | Optional | `-` | Production Plan Sub Assembly Item |
| `download_materials_required` | Download Required Materials | Button | Optional | `-` | - |
| `include_non_stock_items` | Include Non Stock Items | Check | Optional | `1` | - |
| `include_subcontracted_items` | Include Subcontracted Items | Check | Optional | `1` | - |
| `consider_minimum_order_qty` | Consider Minimum Order Qty | Check | Optional | `0` | - |
| `include_safety_stock` | Include Safety Stock in Required Qty Calculation | Check | Optional | `0` | - |
| `ignore_existing_ordered_qty` | Consider Projected Qty in Calculation (RM) | Check | Optional | `1` | - |
| `for_warehouse` | For Warehouse | Link | Optional | `-` | Warehouse |
| `get_items_for_mr` | Get Items for Purchase Only | Button | Optional | `-` | - |
| `transfer_materials` | Get Items for Purchase / Transfer | Button | Optional | `-` | - |
| `mr_items` | Raw Materials | Table | Optional | `-` | Material Request Plan Item |
| `total_planned_qty` | Total Planned Qty | Float | Optional | `0` | - |
| `total_produced_qty` | Total Produced Qty | Float | Optional | `0` | - |
| `status` | Status | Select | Optional | `Draft` | Draft, Submitted, Not Started, In Process, Completed, Closed, Cancelled, Mate... |
| `warehouses` | Warehouses | Table MultiSelect | Optional | `-` | Production Plan Material Request Warehouse |
| `amended_from` | Amended From | Link | Optional | `-` | Production Plan |

### DocType: `Master Production Schedule`
- **Submittable**: No
- **Total Data Fields**: 15

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Naming Series | Select | ✓ Mandatory | `MPS.YY.-.######` | MPS.YY.-.###### |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `from_date` | From Date | Date | ✓ Mandatory | `-` | - |
| `to_date` | To Date | Date | Optional | `-` | - |
| `select_items` | Select Items | Table MultiSelect | Optional | `-` | Master Production Schedule Item |
| `parent_warehouse` | Parent Warehouse | Link | Optional | `-` | Warehouse |
| `get_sales_orders` | Get Sales Orders | Button | Optional | `-` | - |
| `sales_orders` | Sales Orders | Table | Optional | `-` | Production Plan Sales Order |
| `get_material_requests` | Get Material Requests | Button | Optional | `-` | - |
| `material_requests` | Material Requests | Table | Optional | `-` | Production Plan Material Request |
| `get_actual_demand` | Get Actual Demand | Button | Optional | `-` | - |
| `items` | Items | Table | Optional | `-` | Master Production Schedule Item |
| `sales_forecast` | Sales Forecast | Link | Optional | `-` | Sales Forecast |
| `amended_from` | Amended From | Link | Optional | `-` | Master Production Schedule |

### DocType: `Sales Forecast`
- **Submittable**: Yes
- **Total Data Fields**: 12

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Naming Series | Select | ✓ Mandatory | `SF.YY.-.######` | SF.YY.-.###### |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `posting_date` | Posting Date | Date | Optional | `Today` | - |
| `from_date` | From Date | Date | ✓ Mandatory | `Today` | - |
| `frequency` | Frequency | Select | ✓ Mandatory | `Monthly` | Weekly, Monthly |
| `demand_number` | Number of Weeks / Months | Int | ✓ Mandatory | `6` | - |
| `selected_items` | Select Items | Table MultiSelect | ✓ Mandatory | `-` | Sales Forecast Item |
| `parent_warehouse` | Parent Warehouse | Link | ✓ Mandatory | `-` | Warehouse |
| `generate_demand` | Generate Demand | Button | Optional | `-` | - |
| `items` | Items | Table | Optional | `-` | Sales Forecast Item |
| `amended_from` | Amended From | Link | Optional | `-` | Sales Forecast |
| `status` | Status | Select | Optional | `-` | Planned, MPS Generated, Cancelled |

### DocType: `BOM Creator`
- **Submittable**: Yes
- **Total Data Fields**: 24

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `bom_creator` | bom_creator | HTML | Optional | `-` | - |
| `item_code` | Finished Good | Link | ✓ Mandatory | `-` | Item |
| `is_phantom` | Is Phantom Item | Check | Optional | `0` | - |
| `item_name` | Item Name | Data | Optional | `-` | - |
| `item_group` | Item Group | Link | Optional | `-` | Item Group |
| `qty` | Quantity | Float | ✓ Mandatory | `-` | - |
| `project` | Project | Link | Optional | `-` | Project |
| `uom` | UOM | Link | Optional | `-` | UOM |
| `routing` | Routing | Link | Optional | `-` | Routing |
| `rm_cost_as_per` | Rate Of Materials Based On | Select | ✓ Mandatory | `Valuation Rate` | Valuation Rate, Last Purchase Rate, Price List |
| `set_rate_based_on_warehouse` | Set Valuation Rate Based on Source Warehouse | Check | Optional | `0` | - |
| `buying_price_list` | Price List | Link | Optional | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | Optional | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | Optional | `-` | - |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `conversion_rate` | Conversion Rate | Float | Optional | `1` | - |
| `default_warehouse` | Default Source Warehouse | Link | Optional | `-` | Warehouse |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `items` | Items | Table | Optional | `-` | BOM Creator Item |
| `raw_material_cost` | Total Cost | Currency | Optional | `-` | currency |
| `remarks` | Remarks | Text Editor | Optional | `-` | - |
| `status` | Status | Select | Optional | `Draft` | Draft, Submitted, In Progress, Completed, Failed, Cancelled |
| `error_log` | Error Log | Text | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | BOM Creator |

### DocType: `Downtime Entry`
- **Submittable**: No
- **Total Data Fields**: 8

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Naming Series | Select | ✓ Mandatory | `-` | DT- |
| `workstation` | Workstation / Machine | Link | ✓ Mandatory | `-` | Workstation |
| `operator` | Operator | Link | ✓ Mandatory | `-` | Employee |
| `from_time` | From Time | Datetime | ✓ Mandatory | `-` | - |
| `to_time` | To Time | Datetime | ✓ Mandatory | `-` | - |
| `downtime` | Downtime | Float | Optional | `-` | - |
| `stop_reason` | Stop Reason | Select | ✓ Mandatory | `-` | Excessive machine set up time, Unplanned machine maintenance, On-machine pres... |
| `remarks` | Remarks | Text | Optional | `-` | - |

### DocType: `Operation`
- **Submittable**: No
- **Total Data Fields**: 8

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `workstation` | Default Workstation | Link | Optional | `-` | Workstation |
| `is_corrective_operation` | Is Corrective Operation | Check | Optional | `0` | - |
| `create_job_card_based_on_batch_size` | Create Job Card based on Batch Size | Check | Optional | `0` | - |
| `quality_inspection_template` | Quality Inspection Template | Link | Optional | `-` | Quality Inspection Template |
| `batch_size` | Batch Size | Int | Optional | `1` | - |
| `sub_operations` | sub_operations | Table | Optional | `-` | Sub Operation |
| `total_operation_time` | Total Operation Time | Float | Optional | `-` | - |
| `description` | Description | Text | Optional | `-` | - |

### DocType: `Workstation`
- **Submittable**: No
- **Total Data Fields**: 16

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `workstation_dashboard` | Workstation Dashboard | HTML | Optional | `-` | - |
| `workstation_name` | Workstation Name | Data | ✓ Mandatory | `-` | - |
| `workstation_type` | Workstation Type | Link | Optional | `-` | Workstation Type |
| `plant_floor` | Plant Floor | Link | Optional | `-` | Plant Floor |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `production_capacity` | Job Capacity | Int | ✓ Mandatory | `1` | - |
| `warehouse` | Warehouse | Link | Optional | `-` | Warehouse |
| `status` | Status | Select | Optional | `-` | Production, Off, Idle, Problem, Maintenance, Setup |
| `on_status_image` | Active Status | Attach Image | Optional | `-` | - |
| `off_status_image` | Inactive Status | Attach Image | Optional | `-` | - |
| `workstation_costs` | Operating Components Cost | Table | Optional | `-` | Workstation Cost |
| `hour_rate` | Net Hour Rate | Currency | Optional | `-` | - |
| `description` | Description | Text | Optional | `-` | - |
| `holiday_list` | Holiday List | Link | Optional | `-` | Holiday List |
| `working_hours` | Working Hours | Table | Optional | `-` | Workstation Working Hour |
| `total_working_hours` | Total Working Hours | Float | Optional | `-` | - |

### DocType: `Workstation Type`
- **Submittable**: No
- **Total Data Fields**: 4

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `workstation_type` | Workstation Type | Data | ✓ Mandatory | `-` | - |
| `workstation_costs` | Operating Components Cost | Table | Optional | `-` | Workstation Cost |
| `hour_rate` | Net Hour Rate | Currency | Optional | `-` | - |
| `description` | Description | Small Text | Optional | `-` | - |

### DocType: `Plant Floor`
- **Submittable**: No
- **Total Data Fields**: 5

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `plant_dashboard` | Plant Dashboard | HTML | Optional | `-` | - |
| `stock_summary` | Stock Summary | HTML | Optional | `-` | - |
| `floor_name` | Floor Name | Data | Optional | `-` | - |
| `company` | Company | Link | Optional | `-` | Company |
| `warehouse` | Warehouse | Link | Optional | `-` | Warehouse |

### DocType: `Routing`
- **Submittable**: No
- **Total Data Fields**: 3

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `routing_name` | Routing Name | Data | Optional | `-` | - |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `operations` | BOM Operation | Table | Optional | `-` | BOM Operation |

### DocType: `Manufacturing Settings`
- **Submittable**: No
- **Total Data Fields**: 19

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `material_consumption` | Allow Continuous Material Consumption | Check | Optional | `0` | - |
| `get_rm_cost_from_consumption_entry` | Get Raw Materials Cost from Consumption Entry | Check | Optional | `0` | - |
| `backflush_raw_materials_based_on` | Backflush Raw Materials Based On | Select | Optional | `BOM` | BOM, Material Transferred for Manufacture |
| `validate_components_quantities_per_bom` | Validate Components and Quantities Per BOM | Check | Optional | `0` | - |
| `update_bom_costs_automatically` | Update BOM Cost Automatically | Check | Optional | `0` | - |
| `allow_editing_of_items_and_quantities_in_work_order` | Allow Editing of Items and Quantities in Work Order | Check | Optional | `0` | - |
| `overproduction_percentage_for_sales_order` | Overproduction Percentage For Sales Order | Percent | Optional | `-` | - |
| `overproduction_percentage_for_work_order` | Overproduction Percentage For Work Order | Percent | Optional | `-` | - |
| `transfer_extra_materials_percentage` | Transfer Extra Raw Materials to WIP (%) | Percent | Optional | `-` | - |
| `add_corrective_operation_cost_in_finished_good_valuation` | Add Corrective Operation Cost in Finished Good Valuation | Check | Optional | `0` | - |
| `enforce_time_logs` | Enforce Time Logs | Check | Optional | `0` | - |
| `job_card_excess_transfer` | Allow Excess Material Transfer | Check | Optional | `0` | - |
| `disable_capacity_planning` | Disable Capacity Planning | Check | Optional | `0` | - |
| `allow_overtime` | Allow Overtime | Check | Optional | `0` | - |
| `allow_production_on_holidays` | Allow Production on Holidays | Check | Optional | `0` | - |
| `capacity_planning_for_days` | Capacity Planning For (Days) | Int | Optional | `30` | - |
| `mins_between_operations` | Time Between Operations (Mins) | Int | Optional | `-` | - |
| `set_op_cost_and_secondary_items_from_sub_assemblies` | Set Operating Cost / Secondary Items From Sub-assemblies | Check | Optional | `0` | - |
| `make_serial_no_batch_from_work_order` | Make Serial No / Batch from Work Order | Check | Optional | `0` | - |

## Module: Projects
*Work Breakdown Structure (WBS), project templates, task dependencies, timesheets, costing/billing amounts, and Sarathi manufacturing project flags.*

### Summary of DocTypes in Projects:
- **Project**: 45 fields | Submittable: No
- **Task**: 36 fields | Submittable: No
- **Timesheet**: 28 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Activity Type**: 4 fields | Submittable: No
- **Activity Cost**: 7 fields | Submittable: No
- **Project Template**: 3 fields | Submittable: No
- **Project Type**: 2 fields | Submittable: No
- **Project Update**: 7 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Projects Settings**: 4 fields | Submittable: No

### DocType: `Project`
- **Submittable**: No
- **Total Data Fields**: 45

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | PROJ-.#### |
| `project_name` | Project Name | Data | ✓ Mandatory | `-` | - |
| `status` | Status | Select | Optional | `Open` | Open, On hold, Completed, Cancelled |
| `project_type` | Project Type | Link | Optional | `-` | Project Type |
| `custom_sarathi_manufacturing` | Sarathi Manufacturing Project | Check | Optional | `-` | - |
| `percent_complete_method` | % Complete Method | Select | Optional | `Task Completion` | Manual, Task Completion, Task Progress, Task Weight |
| `project_template` | From Template | Link | Optional | `-` | Project Template |
| `priority` | Priority | Select | Optional | `-` | Medium, Low, High |
| `department` | Department | Link | Optional | `-` | Department |
| `is_active` | Is Active | Select | Optional | `-` | Yes, No |
| `percent_complete` | % Completed | Percent | Optional | `-` | - |
| `expected_start_date` | Expected Start Date | Date | Optional | `-` | - |
| `actual_start_date` | Actual Start Date (via Timesheet) | Date | Optional | `-` | - |
| `actual_time` | Actual Time in Hours (via Timesheet) | Float | Optional | `-` | - |
| `expected_end_date` | Expected End Date | Date | Optional | `-` | - |
| `actual_end_date` | Actual End Date (via Timesheet) | Date | Optional | `-` | - |
| `estimated_costing` | Estimated Cost | Currency | Optional | `-` | Company:company:default_currency |
| `total_costing_amount` | Total Costing Amount (via Timesheet) | Currency | Optional | `-` | - |
| `total_purchase_cost` | Total Purchase Cost (via Purchase Invoice) | Currency | Optional | `-` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `total_sales_amount` | Total Sales Amount (via Sales Order) | Currency | Optional | `-` | - |
| `total_billable_amount` | Total Billable Amount (via Timesheet) | Currency | Optional | `-` | - |
| `total_billed_amount` | Total Billed Amount (via Sales Invoice) | Currency | Optional | `-` | - |
| `total_consumed_material_cost` | Total Consumed Material Cost (via Stock Entry) | Currency | Optional | `-` | - |
| `cost_center` | Default Cost Center | Link | Optional | `-` | Cost Center |
| `gross_margin` | Gross Margin | Currency | Optional | `-` | Company:company:default_currency |
| `per_gross_margin` | Gross Margin % | Percent | Optional | `-` | - |
| `collect_progress` | Collect Progress | Check | Optional | `0` | - |
| `holiday_list` | Holiday List | Link | Optional | `-` | Holiday List |
| `frequency` | Frequency To Collect Progress | Select | Optional | `-` | Hourly, Twice Daily, Daily, Weekly |
| `from_time` | From Time | Time | Optional | `-` | - |
| `to_time` | To Time | Time | Optional | `-` | - |
| `first_email` | First Email | Time | Optional | `-` | - |
| `second_email` | Second Email | Time | Optional | `-` | - |
| `daily_time_to_send` | Daily Time to send | Time | Optional | `-` | - |
| `day_to_send` | Day to Send | Select | Optional | `-` | Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday |
| `weekly_time_to_send` | Weekly Time to send | Time | Optional | `-` | - |
| `subject` | Subject | Data | Optional | `-` | - |
| `message` | Message | Text | Optional | `-` | - |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `custom_sarathi_bom` | Main BOM | Link | Optional | `-` | BOM |
| `sales_order` | Sales Order | Link | Optional | `-` | Sales Order |
| `users` | Users | Table | Optional | `-` | Project User |
| `copied_from` | Copied From | Data | Optional | `-` | - |
| `notes` | Notes | Text Editor | Optional | `-` | - |

### DocType: `Task`
- **Submittable**: No
- **Total Data Fields**: 36

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `subject` | Subject | Data | ✓ Mandatory | `-` | - |
| `project` | Project | Link | Optional | `-` | Project |
| `issue` | Issue | Link | Optional | `-` | Issue |
| `type` | Type | Link | Optional | `-` | Task Type |
| `color` | Color | Color | Optional | `-` | - |
| `is_group` | Is Group | Check | Optional | `0` | - |
| `status` | Status | Select | Optional | `-` | Open, Working, Pending Review, Overdue, Template, Completed, Cancelled |
| `priority` | Priority | Select | Optional | `-` | Low, Medium, High, Urgent |
| `task_weight` | Weight | Float | Optional | `-` | - |
| `parent_task` | Parent Task | Link | Optional | `-` | Task |
| `completed_by` | Completed By | Link | Optional | `-` | User |
| `completed_on` | Completed On | Date | Optional | `-` | - |
| `is_template` | Is Template | Check | Optional | `0` | - |
| `start` | Begin On (Days) | Int | Optional | `-` | - |
| `duration` | Duration (Days) | Int | Optional | `-` | - |
| `exp_start_date` | Expected Start Date | Datetime | Optional | `-` | - |
| `expected_time` | Expected Time (in hours) | Float | Optional | `0` | - |
| `exp_end_date` | Expected End Date | Datetime | Optional | `-` | - |
| `progress` | % Progress | Percent | Optional | `-` | - |
| `is_milestone` | Is Milestone | Check | Optional | `0` | - |
| `description` | Task Description | Text Editor | Optional | `-` | - |
| `depends_on` | Dependent Tasks | Table | Optional | `-` | Task Depends On |
| `depends_on_tasks` | Depends on Tasks | Code | Optional | `-` | - |
| `act_start_date` | Actual Start Date (via Timesheet) | Date | Optional | `-` | - |
| `actual_time` | Actual Time in Hours (via Timesheet) | Float | Optional | `-` | - |
| `act_end_date` | Actual End Date (via Timesheet) | Date | Optional | `-` | - |
| `total_costing_amount` | Total Costing Amount (via Timesheet) | Currency | Optional | `-` | Company:company:default_currency |
| `total_billing_amount` | Total Billable Amount (via Timesheet) | Currency | Optional | `-` | - |
| `company` | Company | Link | Optional | `-` | Company |
| `review_date` | Review Date | Date | Optional | `-` | - |
| `closing_date` | Closing Date | Date | Optional | `-` | - |
| `department` | Department | Link | Optional | `-` | Department |
| `lft` | lft | Int | Optional | `-` | - |
| `rgt` | rgt | Int | Optional | `-` | - |
| `old_parent` | Old Parent | Data | Optional | `-` | - |
| `template_task` | Template Task | Data | Optional | `-` | - |

### DocType: `Timesheet`
- **Submittable**: Yes
- **Total Data Fields**: 28

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `title` | Title | Data | Optional | `{employee_name}` | - |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | TS-.YYYY.- |
| `company` | Company | Link | Optional | `-` | Company |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `currency` | Currency | Link | Optional | `-` | Currency |
| `exchange_rate` | Exchange Rate | Float | Optional | `1` | - |
| `sales_invoice` | Sales Invoice | Link | Optional | `-` | Sales Invoice |
| `status` | Status | Select | Optional | `Draft` | Draft, Submitted, Partially Billed, Billed, Payslip, Completed, Cancelled |
| `parent_project` | Project | Link | Optional | `-` | Project |
| `user` | User | Link | Optional | `-` | User |
| `start_date` | Start Date | Date | Optional | `-` | - |
| `end_date` | End Date | Date | Optional | `-` | - |
| `employee` | Employee | Link | Optional | `-` | Employee |
| `department` | Department | Link | Optional | `-` | Department |
| `employee_name` | Employee Name | Data | Optional | `-` | - |
| `time_logs` | Time Sheets | Table | ✓ Mandatory | `-` | Timesheet Detail |
| `total_hours` | Total Working Hours | Float | Optional | `0` | - |
| `total_billable_hours` | Total Billable Hours | Float | Optional | `-` | - |
| `total_billable_amount` | Total Billable Amount | Currency | Optional | `0` | currency |
| `total_costing_amount` | Total Costing Amount | Currency | Optional | `-` | currency |
| `base_total_billable_amount` | Base Total Billable Amount | Currency | Optional | `-` | - |
| `base_total_costing_amount` | Base Total Costing Amount | Currency | Optional | `-` | - |
| `total_billed_hours` | Total Billed Hours | Float | Optional | `-` | - |
| `total_billed_amount` | Total Billed Amount | Currency | Optional | `-` | currency |
| `base_total_billed_amount` | Base Total Billed Amount | Currency | Optional | `-` | - |
| `per_billed` | % Amount Billed | Percent | Optional | `-` | - |
| `note` | Note | Text Editor | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Timesheet |

### DocType: `Activity Type`
- **Submittable**: No
- **Total Data Fields**: 4

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `activity_type` | Activity Type | Data | ✓ Mandatory | `-` | - |
| `costing_rate` | Default Costing Rate | Currency | Optional | `-` | - |
| `billing_rate` | Default Billing Rate | Currency | Optional | `-` | - |
| `disabled` | Disabled | Check | Optional | `0` | - |

### DocType: `Activity Cost`
- **Submittable**: No
- **Total Data Fields**: 7

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `activity_type` | Activity Type | Link | ✓ Mandatory | `-` | Activity Type |
| `employee` | Employee | Link | Optional | `-` | Employee |
| `employee_name` | Employee Name | Data | Optional | `-` | - |
| `department` | Department | Link | Optional | `-` | Department |
| `billing_rate` | Billing Rate | Currency | Optional | `0` | - |
| `costing_rate` | Costing Rate | Currency | Optional | `0` | - |
| `title` | title | Data | Optional | `-` | - |

### DocType: `Project Template`
- **Submittable**: No
- **Total Data Fields**: 3

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `project_type` | Project Type | Link | Optional | `-` | Project Type |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `tasks` | Tasks | Table | ✓ Mandatory | `-` | Project Template Task |

### DocType: `Project Type`
- **Submittable**: No
- **Total Data Fields**: 2

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `project_type` | Project Type | Data | ✓ Mandatory | `-` | - |
| `description` | Description | Text | Optional | `-` | - |

### DocType: `Project Update`
- **Submittable**: Yes
- **Total Data Fields**: 7

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Data | Optional | `-` | PROJ-UPD-.YYYY.- |
| `project` | Project | Link | ✓ Mandatory | `-` | Project |
| `sent` | Sent | Check | Optional | `0` | - |
| `date` | Date | Date | Optional | `-` | - |
| `time` | Time | Time | Optional | `-` | - |
| `users` | Users | Table | Optional | `-` | Project User |
| `amended_from` | Amended From | Link | Optional | `-` | Project Update |

### DocType: `Projects Settings`
- **Submittable**: No
- **Total Data Fields**: 4

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `ignore_workstation_time_overlap` | Ignore Workstation Time Overlap | Check | Optional | `0` | - |
| `ignore_user_time_overlap` | Ignore User Time Overlap | Check | Optional | `0` | - |
| `ignore_employee_time_overlap` | Ignore Employee Time Overlap | Check | Optional | `0` | - |
| `fetch_timesheet_in_sales_invoice` | Fetch Timesheet in Sales Invoice | Check | Optional | `0` | - |

## Module: Quality
*Quality inspection parameters, incoming/in-process/outgoing inspections, tolerance readings 1-10, non-conformance reports, and CAPA actions.*

### Summary of DocTypes in Quality:
- **Quality Inspection**: 23 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Quality Goal**: 6 fields | Submittable: No
- **Quality Review**: 6 fields | Submittable: No
- **Quality Action**: 8 fields | Submittable: No
- **Non Conformance**: 8 fields | Submittable: No
- **Quality Feedback**: 4 fields | Submittable: No
- **Quality Meeting**: 3 fields | Submittable: No
- **Quality Procedure**: 9 fields | Submittable: No
- **Quality Feedback Template**: 2 fields | Submittable: No
- **Quality Inspection Template**: 2 fields | Submittable: No

### DocType: `Quality Inspection`
- **Submittable**: Yes
- **Total Data Fields**: 23

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | MAT-QA-.YYYY.- |
| `company` | Company | Link | Optional | `-` | Company |
| `report_date` | Report Date | Date | ✓ Mandatory | `Today` | - |
| `status` | Status | Select | ✓ Mandatory | `Accepted` | Accepted, Rejected, Cancelled |
| `child_row_reference` | Child Row Reference | Data | Optional | `-` | - |
| `inspection_type` | Inspection Type | Select | ✓ Mandatory | `-` | Incoming, Outgoing, In Process |
| `reference_type` | Reference Type | Select | ✓ Mandatory | `-` | Purchase Receipt, Purchase Invoice, Subcontracting Receipt, Delivery Note, Sa... |
| `reference_name` | Reference Name | Dynamic Link | ✓ Mandatory | `-` | reference_type |
| `item_code` | Item Code | Link | ✓ Mandatory | `-` | Item |
| `item_serial_no` | Item Serial No | Link | Optional | `-` | Serial No |
| `batch_no` | Batch No | Link | Optional | `-` | Batch |
| `sample_size` | Sample Size | Float | ✓ Mandatory | `-` | - |
| `item_name` | Item Name | Data | Optional | `-` | - |
| `description` | Description | Small Text | Optional | `-` | - |
| `bom_no` | BOM No | Link | Optional | `-` | BOM |
| `quality_inspection_template` | Quality Inspection Template | Link | Optional | `-` | Quality Inspection Template |
| `manual_inspection` | Manual Inspection | Check | Optional | `0` | - |
| `readings` | Readings | Table | Optional | `-` | Quality Inspection Reading |
| `inspected_by` | Inspected By | Link | ✓ Mandatory | `user` | User |
| `verified_by` | Verified By | Data | Optional | `-` | - |
| `remarks` | Remarks | Text | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Quality Inspection |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |

### DocType: `Quality Goal`
- **Submittable**: No
- **Total Data Fields**: 6

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `goal` | Goal | Data | ✓ Mandatory | `-` | - |
| `frequency` | Monitoring Frequency | Select | Optional | `None` | None, Daily, Weekly, Monthly, Quarterly |
| `procedure` | Procedure | Link | Optional | `-` | Quality Procedure |
| `weekday` | Weekday | Select | Optional | `-` | Monday, Tuesday, Wednesday, Thursday, Friday, Saturday |
| `date` | Date | Select | Optional | `-` | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22... |
| `objectives` | Objectives | Table | Optional | `-` | Quality Goal Objective |

### DocType: `Quality Review`
- **Submittable**: No
- **Total Data Fields**: 6

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `goal` | Goal | Link | ✓ Mandatory | `-` | Quality Goal |
| `date` | Date | Date | Optional | `Today` | - |
| `procedure` | Procedure | Link | Optional | `-` | Quality Procedure |
| `status` | Status | Select | Optional | `Open` | Open, Passed, Failed |
| `reviews` | Reviews | Table | Optional | `-` | Quality Review Objective |
| `additional_information` | Additional Information | Text | Optional | `-` | - |

### DocType: `Quality Action`
- **Submittable**: No
- **Total Data Fields**: 8

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `corrective_preventive` | Corrective/Preventive | Select | ✓ Mandatory | `Corrective` | Corrective, Preventive |
| `review` | Review | Link | Optional | `-` | Quality Review |
| `feedback` | Feedback | Link | Optional | `-` | Quality Feedback |
| `status` | Status | Select | Optional | `Open` | Open, Completed |
| `date` | Date | Date | Optional | `Today` | - |
| `goal` | Goal | Link | Optional | `-` | Quality Goal |
| `procedure` | Procedure | Link | Optional | `-` | Quality Procedure |
| `resolutions` | Resolutions | Table | Optional | `-` | Quality Action Resolution |

### DocType: `Non Conformance`
- **Submittable**: No
- **Total Data Fields**: 8

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `subject` | Subject | Data | ✓ Mandatory | `-` | - |
| `procedure` | Procedure | Link | ✓ Mandatory | `-` | Quality Procedure |
| `process_owner` | Process Owner | Data | Optional | `-` | - |
| `full_name` | Full Name | Data | Optional | `-` | - |
| `status` | Status | Select | ✓ Mandatory | `-` | Open, Resolved, Cancelled |
| `details` | Details | Text Editor | Optional | `-` | - |
| `corrective_action` | Corrective Action | Text Editor | Optional | `-` | - |
| `preventive_action` | Preventive Action | Text Editor | Optional | `-` | - |

### DocType: `Quality Feedback`
- **Submittable**: No
- **Total Data Fields**: 4

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `template` | Template | Link | ✓ Mandatory | `-` | Quality Feedback Template |
| `document_type` | Type | Select | ✓ Mandatory | `-` | User, Customer |
| `document_name` | Feedback By | Dynamic Link | ✓ Mandatory | `-` | document_type |
| `parameters` | Parameters | Table | Optional | `-` | Quality Feedback Parameter |

### DocType: `Quality Meeting`
- **Submittable**: No
- **Total Data Fields**: 3

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `status` | Status | Select | Optional | `Open` | Open, Closed |
| `agenda` | Agenda | Table | Optional | `-` | Quality Meeting Agenda |
| `minutes` | Minutes | Table | Optional | `-` | Quality Meeting Minutes |

### DocType: `Quality Procedure`
- **Submittable**: No
- **Total Data Fields**: 9

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `quality_procedure_name` | Quality Procedure | Data | ✓ Mandatory | `-` | - |
| `process_owner` | Process Owner | Link | Optional | `-` | User |
| `process_owner_full_name` | Process Owner Full Name | Data | Optional | `-` | - |
| `processes` | Processes | Table | Optional | `-` | Quality Procedure Process |
| `parent_quality_procedure` | Parent Procedure | Link | Optional | `-` | Quality Procedure |
| `is_group` | Is Group | Check | Optional | `0` | - |
| `rgt` | Right Index | Int | Optional | `-` | - |
| `lft` | Left Index | Int | Optional | `-` | - |
| `old_parent` | old_parent | Data | Optional | `-` | - |

### DocType: `Quality Feedback Template`
- **Submittable**: No
- **Total Data Fields**: 2

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `template` | Template Name | Data | ✓ Mandatory | `-` | - |
| `parameters` | Parameters | Table | ✓ Mandatory | `-` | Quality Feedback Template Parameter |

### DocType: `Quality Inspection Template`
- **Submittable**: No
- **Total Data Fields**: 2

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `quality_inspection_template_name` | Quality Inspection Template Name | Data | ✓ Mandatory | `-` | - |
| `item_quality_inspection_parameter` | Item Quality Inspection Parameter | Table | ✓ Mandatory | `-` | Item Quality Inspection Parameter |

## Module: Selling
*Quotations, Sales Orders with automated downstream Work Order and Delivery Note creation, POS registers, blanket orders, customer credit limits, and pricing rules.*

### Summary of DocTypes in Selling:
- **Quotation**: 87 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Sales Order**: 113 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Sales Invoice**: 158 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **POS Profile**: 43 fields | Submittable: No
- **POS Invoice**: 129 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **POS Opening Entry**: 11 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **POS Closing Entry**: 19 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Loyalty Program**: 15 fields | Submittable: No
- **Blanket Order**: 15 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Customer**: 51 fields | Submittable: No
- **Customer Group**: 10 fields | Submittable: No
- **Selling Settings**: 34 fields | Submittable: No

### DocType: `Quotation`
- **Submittable**: Yes
- **Total Data Fields**: 87

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | SAL-QTN-.YYYY.- |
| `quotation_to` | Quotation To | Link | ✓ Mandatory | `Customer` | DocType |
| `party_name` | Party | Dynamic Link | Optional | `-` | quotation_to |
| `customer_name` | Customer Name | Data | Optional | `-` | - |
| `transaction_date` | Date | Date | ✓ Mandatory | `Today` | - |
| `valid_till` | Valid Till | Date | Optional | `-` | - |
| `order_type` | Order Type | Select | ✓ Mandatory | `Sales` | Sales, Maintenance, Shopping Cart |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `has_unit_price_items` | Has Unit Price Items | Check | Optional | `0` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Quotation |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `conversion_rate` | Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `selling_price_list` | Price List | Link | ✓ Mandatory | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | ✓ Mandatory | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `items` | Items | Table | ✓ Mandatory | `-` | Quotation Item |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total_net_weight` | Total Net Weight | Float | Optional | `-` | - |
| `base_total` | Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_net_total` | Net Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total` | Total | Currency | Optional | `-` | currency |
| `net_total` | Net Total | Currency | Optional | `-` | currency |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes_and_charges` | Sales Taxes and Charges Template | Link | Optional | `-` | Sales Taxes and Charges Template |
| `shipping_rule` | Shipping Rule | Link | Optional | `-` | Shipping Rule |
| `incoterm` | Incoterm | Link | Optional | `-` | Incoterm |
| `named_place` | Named Place | Data | Optional | `-` | - |
| `taxes` | Sales Taxes and Charges | Table | Optional | `-` | Sales Taxes and Charges |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | currency |
| `base_grand_total` | Grand Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounding_adjustment` | Rounding Adjustment (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounded_total` | Rounded Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_in_words` | In Words (Company Currency) | Data | Optional | `-` | - |
| `grand_total` | Grand Total | Currency | Optional | `-` | currency |
| `rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | currency |
| `rounded_total` | Rounded Total | Currency | Optional | `-` | currency |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `in_words` | In Words | Data | Optional | `-` | - |
| `apply_discount_on` | Apply Additional Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `base_discount_amount` | Additional Discount Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `coupon_code` | Coupon Code | Link | Optional | `-` | Coupon Code |
| `additional_discount_percentage` | Additional Discount Percentage | Float | Optional | `-` | - |
| `discount_amount` | Additional Discount Amount | Currency | Optional | `-` | currency |
| `referral_sales_partner` | Referral Sales Partner | Link | Optional | `-` | Sales Partner |
| `other_charges_calculation` | Taxes and Charges Calculation | Text Editor | Optional | `-` | - |
| `item_wise_tax_details` | Item Wise Tax Details | Table | Optional | `-` | Item Wise Tax Detail |
| `packed_items` | Bundle Items | Table | Optional | `-` | Packed Item |
| `pricing_rules` | Pricing Rule Detail | Table | Optional | `-` | Pricing Rule Detail |
| `customer_address` | Customer Address | Link | Optional | `-` | Address |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `contact_person` | Contact Person | Link | Optional | `-` | Contact |
| `contact_display` | Contact | Small Text | Optional | `-` | - |
| `contact_mobile` | Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Data | Optional | `-` | Email |
| `shipping_address_name` | Shipping Address | Link | Optional | `-` | Address |
| `shipping_address` | Shipping Address | Text Editor | Optional | `-` | - |
| `company_address` | Company Address Name | Link | Optional | `-` | Address |
| `company_address_display` | Company Address | Text Editor | Optional | `-` | - |
| `company_contact_person` | Company Contact Person | Link | Optional | `-` | Contact |
| `payment_terms_template` | Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `payment_schedule` | Payment Schedule | Table | Optional | `-` | Payment Schedule |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Term Details | Text Editor | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `update_auto_repeat_reference` | Update Auto Repeat Reference | Button | Optional | `-` | - |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `group_same_items` | Group same items | Check | Optional | `0` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `language` | Print Language | Link | Optional | `-` | Language |
| `lost_reasons` | Lost Reasons | Table MultiSelect | Optional | `-` | Quotation Lost Reason Detail |
| `competitors` | Competitors | Table MultiSelect | Optional | `-` | Competitor Detail |
| `order_lost_reason` | Detailed Reason | Small Text | Optional | `-` | - |
| `utm_source` | Source | Link | Optional | `-` | UTM Source |
| `utm_medium` | Medium | Link | Optional | `-` | UTM Medium |
| `utm_campaign` | Campaign | Link | Optional | `-` | UTM Campaign |
| `utm_content` | Content | Data | Optional | `-` | - |
| `status` | Status | Select | ✓ Mandatory | `Draft` | Draft, Open, Replied, Partially Ordered, Ordered, Lost, Cancelled, Expired |
| `customer_group` | Customer Group | Link | Optional | `-` | Customer Group |
| `territory` | Territory | Link | Optional | `-` | Territory |
| `title` | Title | Data | Optional | `-` | - |
| `opportunity` | Opportunity | Link | Optional | `-` | Opportunity |
| `enq_det` | Opportunity Item | Text | Optional | `-` | - |
| `supplier_quotation` | Supplier Quotation | Link | Optional | `-` | Supplier Quotation |

### DocType: `Sales Order`
- **Submittable**: Yes
- **Total Data Fields**: 113

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | SAL-ORD-.YYYY.- |
| `customer` | Customer | Link | ✓ Mandatory | `-` | Customer |
| `customer_name` | Customer Name | Data | Optional | `-` | - |
| `order_type` | Order Type | Select | ✓ Mandatory | `Sales` | Sales, Maintenance, Shopping Cart |
| `transaction_date` | Date | Date | ✓ Mandatory | `Today` | - |
| `transaction_time` | Time | Time | Optional | `Now` | - |
| `delivery_date` | Delivery Date | Date | Optional | `-` | - |
| `tax_id` | Tax Id | Data | Optional | `-` | - |
| `skip_delivery_note` | Skip Delivery Note | Check | Optional | `0` | - |
| `has_unit_price_items` | Has Unit Price Items | Check | Optional | `0` | - |
| `is_subcontracted` | Is Subcontracted | Check | Optional | `0` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Sales Order |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `conversion_rate` | Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `selling_price_list` | Price List | Link | ✓ Mandatory | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | ✓ Mandatory | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `set_warehouse` | Set Source Warehouse | Link | Optional | `-` | Warehouse |
| `reserve_stock` | Reserve Stock | Check | Optional | `0` | - |
| `items` | Items | Table | ✓ Mandatory | `-` | Sales Order Item |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total_net_weight` | Total Net Weight | Float | Optional | `-` | - |
| `base_total` | Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_net_total` | Net Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total` | Total | Currency | Optional | `-` | currency |
| `net_total` | Net Total | Currency | Optional | `-` | currency |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes_and_charges` | Sales Taxes and Charges Template | Link | Optional | `-` | Sales Taxes and Charges Template |
| `shipping_rule` | Shipping Rule | Link | Optional | `-` | Shipping Rule |
| `incoterm` | Incoterm | Link | Optional | `-` | Incoterm |
| `named_place` | Named Place | Data | Optional | `-` | - |
| `taxes` | Sales Taxes and Charges | Table | Optional | `-` | Sales Taxes and Charges |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | currency |
| `grand_total` | Grand Total | Currency | Optional | `-` | currency |
| `in_words` | In Words | Data | Optional | `-` | - |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | currency |
| `rounded_total` | Rounded Total | Currency | Optional | `-` | currency |
| `base_grand_total` | Grand Total | Currency | Optional | `-` | Company:company:default_currency |
| `base_in_words` | In Words | Data | Optional | `-` | - |
| `base_rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounded_total` | Rounded Total | Currency | Optional | `-` | Company:company:default_currency |
| `advance_paid` | Advance Paid | Currency | Optional | `-` | party_account_currency |
| `apply_discount_on` | Apply Additional Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `base_discount_amount` | Additional Discount Amount | Currency | Optional | `-` | Company:company:default_currency |
| `coupon_code` | Coupon Code | Link | Optional | `-` | Coupon Code |
| `additional_discount_percentage` | Additional Discount Percentage | Float | Optional | `-` | - |
| `discount_amount` | Additional Discount Amount | Currency | Optional | `-` | currency |
| `other_charges_calculation` | Taxes and Charges Calculation | Text Editor | Optional | `-` | - |
| `item_wise_tax_details` | Item Wise Tax Details | Table | Optional | `-` | Item Wise Tax Detail |
| `packed_items` | Packed Items | Table | Optional | `-` | Packed Item |
| `pricing_rules` | Pricing Rule Detail | Table | Optional | `-` | Pricing Rule Detail |
| `customer_address` | Customer Address | Link | Optional | `-` | Address |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `customer_group` | Customer Group | Link | Optional | `-` | Customer Group |
| `territory` | Territory | Link | Optional | `-` | Territory |
| `contact_person` | Contact Person | Link | Optional | `-` | Contact |
| `contact_display` | Contact | Small Text | Optional | `-` | - |
| `contact_phone` | Phone | Data | Optional | `-` | Phone |
| `contact_mobile` | Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Data | Optional | `-` | Email |
| `shipping_address_name` | Shipping Address Name | Link | Optional | `-` | Address |
| `shipping_address` | Shipping Address | Text Editor | Optional | `-` | - |
| `dispatch_address_name` | Dispatch Address Name | Link | Optional | `-` | Address |
| `dispatch_address` | Dispatch Address | Text Editor | Optional | `-` | - |
| `company_address` | Company Address Name | Link | Optional | `-` | Address |
| `company_address_display` | Company Address | Text Editor | Optional | `-` | - |
| `company_contact_person` | Company Contact Person | Link | Optional | `-` | Contact |
| `ignore_default_payment_terms_template` | Ignore Default Payment Terms Template | Check | Optional | `0` | - |
| `payment_terms_template` | Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `payment_schedule` | Payment Schedule | Table | Optional | `-` | Payment Schedule |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions Details | Text Editor | Optional | `-` | - |
| `status` | Status | Select | ✓ Mandatory | `Draft` | Draft, On Hold, To Pay, To Deliver and Bill, To Bill, To Deliver, Completed, ... |
| `delivery_status` | Delivery Status | Select | Optional | `-` | Not Delivered, Fully Delivered, Partly Delivered, Closed, Not Applicable |
| `per_delivered` | %  Delivered | Percent | Optional | `-` | - |
| `per_billed` | % Amount Billed | Percent | Optional | `-` | - |
| `per_picked` | % Picked | Percent | Optional | `-` | - |
| `billing_status` | Billing Status | Select | Optional | `-` | Not Billed, Fully Billed, Partly Billed, Closed |
| `advance_payment_status` | Advance Payment Status | Select | Optional | `-` | Not Requested, Requested, Partially Paid, Fully Paid |
| `sales_partner` | Sales Partner | Link | Optional | `-` | Sales Partner |
| `amount_eligible_for_commission` | Amount Eligible for Commission | Currency | Optional | `-` | Company:company:default_currency |
| `commission_rate` | Commission Rate | Float | Optional | `-` | - |
| `total_commission` | Total Commission | Currency | Optional | `-` | Company:company:default_currency |
| `sales_team` | Sales Team | Table | Optional | `-` | Sales Team |
| `loyalty_points` | Loyalty Points | Int | Optional | `-` | - |
| `loyalty_amount` | Loyalty Amount | Currency | Optional | `-` | Company:company:default_currency |
| `from_date` | From Date | Date | Optional | `-` | - |
| `to_date` | To Date | Date | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `update_auto_repeat_reference` | Update Auto Repeat Reference | Button | Optional | `-` | - |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `group_same_items` | Group same items | Check | Optional | `0` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `language` | Print Language | Link | Optional | `-` | Language |
| `utm_source` | Source | Link | Optional | `-` | UTM Source |
| `utm_medium` | Medium | Link | Optional | `-` | UTM Medium |
| `utm_campaign` | Campaign | Link | Optional | `-` | UTM Campaign |
| `utm_content` | Content | Data | Optional | `-` | - |
| `is_internal_customer` | Is Internal Customer | Check | Optional | `0` | - |
| `po_no` | Customer's Purchase Order | Data | Optional | `-` | - |
| `po_date` | Customer's Purchase Order Date | Date | Optional | `-` | - |
| `represents_company` | Represents Company | Link | Optional | `-` | Company |
| `title` | Title | Data | Optional | `-` | - |
| `inter_company_order_reference` | Inter Company Order Reference | Link | Optional | `-` | Purchase Order |
| `party_account_currency` | Party Account Currency | Link | Optional | `-` | Currency |

### DocType: `Sales Invoice`
- **Submittable**: Yes
- **Total Data Fields**: 158

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `company_tax_id` | Company Tax ID | Data | Optional | `-` | - |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | ACC-SINV-.YYYY.-, ACC-SINV-RET-.YYYY.- |
| `customer` | Customer | Link | ✓ Mandatory | `-` | Customer |
| `customer_name` | Customer Name | Small Text | Optional | `-` | - |
| `tax_id` | Tax Id | Data | Optional | `-` | - |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `posting_time` | Posting Time | Time | Optional | `Now` | - |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `due_date` | Payment Due Date | Date | Optional | `-` | - |
| `is_pos` | Include Payment (POS) | Check | Optional | `0` | - |
| `pos_profile` | POS Profile | Link | Optional | `-` | POS Profile |
| `is_consolidated` | Is Consolidated | Check | Optional | `0` | - |
| `is_return` | Is Return (Credit Note) | Check | Optional | `0` | - |
| `return_against` | Return Against | Link | Optional | `-` | Sales Invoice |
| `update_outstanding_for_self` | Update Outstanding for Self | Check | Optional | `1` | - |
| `update_billed_amount_in_sales_order` | Update Billed Amount in Sales Order | Check | Optional | `0` | - |
| `update_billed_amount_in_delivery_note` | Update Billed Amount in Delivery Note | Check | Optional | `1` | - |
| `is_debit_note` | Is Rate Adjustment Entry (Debit Note) | Check | Optional | `0` | - |
| `apply_tds` | Consider for Tax Withholding | Check | Optional | `0` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Sales Invoice |
| `is_created_using_pos` | Is created using POS | Check | Optional | `0` | - |
| `pos_closing_entry` | POS Closing Entry | Link | Optional | `-` | POS Closing Entry |
| `has_subcontracted` | Has Subcontracted | Check | Optional | `0` | - |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `conversion_rate` | Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `selling_price_list` | Price List | Link | ✓ Mandatory | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | ✓ Mandatory | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `update_stock` | Update Stock | Check | Optional | `0` | - |
| `set_warehouse` | Source Warehouse | Link | Optional | `-` | Warehouse |
| `set_target_warehouse` | Set Target Warehouse | Link | Optional | `-` | Warehouse |
| `items` | Items | Table | ✓ Mandatory | `-` | Sales Invoice Item |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total_net_weight` | Total Net Weight | Float | Optional | `-` | - |
| `base_total` | Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_net_total` | Net Total (Company Currency) | Currency | ✓ Mandatory | `-` | Company:company:default_currency |
| `total` | Total | Currency | Optional | `-` | currency |
| `net_total` | Net Total | Currency | Optional | `-` | currency |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes_and_charges` | Sales Taxes and Charges Template | Link | Optional | `-` | Sales Taxes and Charges Template |
| `shipping_rule` | Shipping Rule | Link | Optional | `-` | Shipping Rule |
| `incoterm` | Incoterm | Link | Optional | `-` | Incoterm |
| `named_place` | Named Place | Data | Optional | `-` | - |
| `taxes` | Sales Taxes and Charges | Table | Optional | `-` | Sales Taxes and Charges |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | currency |
| `use_company_roundoff_cost_center` | Use Company default Cost Center for Round off | Check | Optional | `0` | - |
| `grand_total` | Grand Total | Currency | ✓ Mandatory | `-` | currency |
| `in_words` | In Words | Small Text | Optional | `-` | - |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | currency |
| `rounded_total` | Rounded Total | Currency | Optional | `-` | currency |
| `base_grand_total` | Grand Total (Company Currency | Currency | ✓ Mandatory | `-` | Company:company:default_currency |
| `base_in_words` | In Words | Small Text | Optional | `-` | - |
| `base_rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounded_total` | Rounded Total | Currency | Optional | `-` | Company:company:default_currency |
| `total_advance` | Total Advance | Currency | Optional | `-` | party_account_currency |
| `outstanding_amount` | Outstanding Amount | Currency | Optional | `-` | party_account_currency |
| `tax_withholding_group` | Tax Withholding Group | Link | Optional | `-` | Tax Withholding Group |
| `ignore_tax_withholding_threshold` | Ignore Tax Withholding Threshold | Check | Optional | `0` | - |
| `override_tax_withholding_entries` | Edit Tax Withholding Entries | Check | Optional | `0` | - |
| `tax_withholding_entries` | Tax Withholding Entries | Table | Optional | `-` | Tax Withholding Entry |
| `apply_discount_on` | Apply Additional Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `base_discount_amount` | Additional Discount Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `coupon_code` | Coupon Code | Link | Optional | `-` | Coupon Code |
| `additional_discount_percentage` | Additional Discount Percentage | Float | Optional | `-` | - |
| `discount_amount` | Additional Discount Amount | Currency | Optional | `-` | currency |
| `is_cash_or_non_trade_discount` | Is Cash or Non Trade Discount | Check | Optional | `0` | - |
| `additional_discount_account` | Discount Account | Link | Optional | `-` | Account |
| `other_charges_calculation` | Taxes and Charges Calculation | Text Editor | Optional | `-` | - |
| `item_wise_tax_details` | Item Wise Tax Details | Table | Optional | `-` | Item Wise Tax Detail |
| `pricing_rules` | Pricing Rule Detail | Table | Optional | `-` | Pricing Rule Detail |
| `packed_items` | Packed Items | Table | Optional | `-` | Packed Item |
| `product_bundle_help` | Product Bundle Help | HTML | Optional | `-` | - |
| `timesheets` | Time Sheets | Table | Optional | `-` | Sales Invoice Timesheet |
| `total_billing_hours` | Total Billing Hours | Float | Optional | `-` | - |
| `total_billing_amount` | Total Billing Amount | Currency | Optional | `0` | currency |
| `cash_bank_account` | Cash/Bank Account | Link | Optional | `-` | Account |
| `payments` | Sales Invoice Payment | Table | Optional | `-` | Sales Invoice Payment |
| `base_paid_amount` | Paid Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `paid_amount` | Paid Amount | Currency | Optional | `-` | currency |
| `base_change_amount` | Base Change Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `change_amount` | Change Amount | Currency | Optional | `-` | currency |
| `account_for_change_amount` | Account for Change Amount | Link | Optional | `-` | Account |
| `allocate_advances_automatically` | Allocate Advances Automatically (FIFO) | Check | Optional | `0` | - |
| `only_include_allocated_payments` | Only Include Allocated Payments | Check | Optional | `0` | - |
| `get_advances` | Get Advances Received | Button | Optional | `-` | set_advances |
| `advances` | Advances | Table | Optional | `-` | Sales Invoice Advance |
| `write_off_amount` | Write Off Amount | Currency | Optional | `-` | currency |
| `base_write_off_amount` | Write Off Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `write_off_outstanding_amount_automatically` | Write Off Outstanding Amount | Check | Optional | `0` | - |
| `write_off_account` | Write Off Account | Link | Optional | `-` | Account |
| `write_off_cost_center` | Write Off Cost Center | Link | Optional | `-` | Cost Center |
| `redeem_loyalty_points` | Redeem Loyalty Points | Check | Optional | `0` | - |
| `loyalty_points` | Loyalty Points | Int | Optional | `-` | - |
| `loyalty_amount` | Loyalty Amount | Currency | Optional | `-` | Company:company:default_currency |
| `loyalty_program` | Loyalty Program | Link | Optional | `-` | Loyalty Program |
| `dont_create_loyalty_points` | Don't Create Loyalty Points | Check | Optional | `0` | - |
| `loyalty_redemption_account` | Redemption Account | Link | Optional | `-` | Account |
| `loyalty_redemption_cost_center` | Redemption Cost Center | Link | Optional | `-` | Cost Center |
| `customer_address` | Customer Address | Link | Optional | `-` | Address |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `contact_person` | Contact Person | Link | Optional | `-` | Contact |
| `contact_display` | Contact | Small Text | Optional | `-` | - |
| `contact_mobile` | Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Data | Optional | `-` | Email |
| `territory` | Territory | Link | Optional | `-` | Territory |
| `shipping_address_name` | Shipping Address Name | Link | Optional | `-` | Address |
| `shipping_address` | Shipping Address | Text Editor | Optional | `-` | - |
| `dispatch_address_name` | Dispatch Address Name | Link | Optional | `-` | Address |
| `dispatch_address` | Dispatch Address | Text Editor | Optional | `-` | - |
| `company_address` | Company Address Name | Link | Optional | `-` | Address |
| `company_address_display` | Company Address | Text Editor | Optional | `-` | - |
| `company_contact_person` | Company Contact Person | Link | Optional | `-` | Contact |
| `ignore_default_payment_terms_template` | Ignore Default Payment Terms Template | Check | Optional | `0` | - |
| `payment_terms_template` | Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `payment_schedule` | Payment Schedule | Table | Optional | `-` | Payment Schedule |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions Details | Text Editor | Optional | `-` | - |
| `po_no` | Customer's Purchase Order | Data | Optional | `-` | - |
| `po_date` | Customer's Purchase Order Date | Date | Optional | `-` | - |
| `debit_to` | Debit To | Link | ✓ Mandatory | `-` | Account |
| `party_account_currency` | Party Account Currency | Link | Optional | `-` | Currency |
| `is_opening` | Is Opening Entry | Select | Optional | `No` | No, Yes |
| `unrealized_profit_loss_account` | Unrealized Profit / Loss Account | Link | Optional | `-` | Account |
| `against_income_account` | Against Income Account | Small Text | Optional | `-` | - |
| `sales_partner` | Sales Partner | Link | Optional | `-` | Sales Partner |
| `amount_eligible_for_commission` | Amount Eligible for Commission | Currency | Optional | `-` | Company:company:default_currency |
| `commission_rate` | Commission Rate (%) | Float | Optional | `-` | - |
| `total_commission` | Total Commission | Currency | Optional | `-` | Company:company:default_currency |
| `sales_team` | Sales Contributions and Incentives | Table | Optional | `-` | Sales Team |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `group_same_items` | Group same items | Check | Optional | `0` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `language` | Print Language | Link | Optional | `-` | Language |
| `subscription` | Subscription | Link | Optional | `-` | Subscription |
| `from_date` | From Date | Date | Optional | `-` | - |
| `to_date` | To Date | Date | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `update_auto_repeat_reference` | Update Auto Repeat Reference | Button | Optional | `-` | - |
| `utm_source` | Source | Link | Optional | `-` | UTM Source |
| `utm_medium` | Medium | Link | Optional | `-` | UTM Medium |
| `utm_campaign` | Campaign | Link | Optional | `-` | UTM Campaign |
| `utm_content` | Content | Data | Optional | `-` | - |
| `status` | Status | Select | Optional | `Draft` | Draft, Return, Credit Note Issued, Submitted, Paid, Partly Paid, Unpaid, Unpa... |
| `remarks` | Remarks | Small Text | Optional | `-` | - |
| `customer_group` | Customer Group | Link | Optional | `-` | Customer Group |
| `title` | Title | Data | Optional | `-` | - |
| `is_internal_customer` | Is Internal Customer | Check | Optional | `0` | - |
| `represents_company` | Represents Company | Link | Optional | `-` | Company |
| `inter_company_invoice_reference` | Inter Company Invoice Reference | Link | Optional | `-` | Purchase Invoice |
| `is_discounted` | Is Discounted | Check | Optional | `0` | - |

### DocType: `POS Profile`
- **Submittable**: No
- **Total Data Fields**: 43

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `country` | Country | Read Only | Optional | `-` | - |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `warehouse` | Warehouse | Link | ✓ Mandatory | `-` | Warehouse |
| `company_address` | Company Address | Link | Optional | `-` | Address |
| `payments` | Payment Methods | Table | ✓ Mandatory | `-` | POS Payment Method |
| `set_grand_total_to_default_mop` | Set Grand Total to Default Payment Method | Check | Optional | `1` | - |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `selling_price_list` | Price List | Link | Optional | `-` | Price List |
| `write_off_account` | Write Off Account | Link | ✓ Mandatory | `-` | Account |
| `write_off_cost_center` | Write Off Cost Center | Link | ✓ Mandatory | `-` | Cost Center |
| `write_off_limit` | Write Off Limit | Currency | ✓ Mandatory | `1` | - |
| `income_account` | Income Account | Link | Optional | `-` | Account |
| `expense_account` | Expense Account | Link | Optional | `-` | Account |
| `taxes_and_charges` | Taxes and Charges | Link | Optional | `-` | Sales Taxes and Charges Template |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `account_for_change_amount` | Account for Change Amount | Link | Optional | `-` | Account |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `apply_discount_on` | Apply Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `allow_partial_payment` | Allow Partial Payment | Check | Optional | `0` | - |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `action_on_new_invoice` | Action on New Invoice | Select | Optional | `Always Ask` | Always Ask, Save Changes and Load New Invoice, Discard Changes and Load New I... |
| `validate_stock_on_save` | Validate Stock on Save | Check | Optional | `0` | - |
| `update_stock` | Update Stock | Check | Optional | `1` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `print_receipt_on_order_complete` | Print Receipt on Order Complete | Check | Optional | `0` | - |
| `hide_images` | Hide Images | Check | Optional | `0` | - |
| `hide_unavailable_items` | Hide Unavailable Items | Check | Optional | `0` | - |
| `auto_add_item_to_cart` | Automatically Add Filtered Item To Cart | Check | Optional | `0` | - |
| `allow_rate_change` | Allow User to Edit Rate | Check | Optional | `0` | - |
| `allow_discount_change` | Allow User to Edit Discount | Check | Optional | `0` | - |
| `applicable_for_users` | Applicable for Users | Table | Optional | `-` | POS Profile User |
| `item_groups` | Item Groups | Table | Optional | `-` | POS Item Group |
| `customer_groups` | Customer Groups | Table | Optional | `-` | POS Customer Group |
| `print_format` | Print Format | Link | Optional | `-` | Print Format |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `tc_name` | Terms and Conditions | Link | Optional | `-` | Terms and Conditions |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `utm_source` | Source | Link | Optional | `-` | UTM Source |
| `utm_campaign` | Campaign | Link | Optional | `-` | UTM Campaign |
| `utm_medium` | Medium | Link | Optional | `-` | UTM Campaign |

### DocType: `POS Invoice`
- **Submittable**: Yes
- **Total Data Fields**: 129

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | ACC-PSINV-.YYYY.- |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `customer_name` | Customer Name | Data | Optional | `-` | - |
| `tax_id` | Tax Id | Data | Optional | `-` | - |
| `pos_profile` | POS Profile | Link | Optional | `-` | POS Profile |
| `consolidated_invoice` | Consolidated Sales Invoice | Link | Optional | `-` | Sales Invoice |
| `is_pos` | Include Payment (POS) | Check | ✓ Mandatory | `1` | - |
| `is_return` | Is Return (Credit Note) | Check | Optional | `0` | - |
| `update_billed_amount_in_sales_order` | Update Billed Amount in Sales Order | Check | Optional | `0` | - |
| `update_billed_amount_in_delivery_note` | Update Billed Amount in Delivery Note | Check | Optional | `1` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `posting_date` | Date | Date | ✓ Mandatory | `Today` | - |
| `posting_time` | Posting Time | Time | Optional | `Now` | - |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `due_date` | Payment Due Date | Date | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | POS Invoice |
| `return_against` | Return Against | Link | Optional | `-` | POS Invoice |
| `project` | Project | Link | Optional | `-` | Project |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `conversion_rate` | Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `selling_price_list` | Price List | Link | ✓ Mandatory | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | ✓ Mandatory | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `set_warehouse` | Source Warehouse | Link | Optional | `-` | Warehouse |
| `update_stock` | Update Stock | Check | Optional | `0` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `items` | Items | Table | ✓ Mandatory | `-` | POS Invoice Item |
| `pricing_rules` | Pricing Rule Detail | Table | Optional | `-` | Pricing Rule Detail |
| `packed_items` | Packed Items | Table | Optional | `-` | Packed Item |
| `product_bundle_help` | Product Bundle Help | HTML | Optional | `-` | - |
| `timesheets` | Time Sheets | Table | Optional | `-` | Sales Invoice Timesheet |
| `total_billing_amount` | Total Billing Amount | Currency | Optional | `0` | currency |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `base_total` | Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_net_total` | Net Total (Company Currency) | Currency | ✓ Mandatory | `-` | Company:company:default_currency |
| `total` | Total | Currency | Optional | `-` | currency |
| `net_total` | Net Total | Currency | Optional | `-` | currency |
| `total_net_weight` | Total Net Weight | Float | Optional | `-` | - |
| `taxes_and_charges` | Sales Taxes and Charges Template | Link | Optional | `-` | Sales Taxes and Charges Template |
| `shipping_rule` | Shipping Rule | Link | Optional | `-` | Shipping Rule |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes` | Sales Taxes and Charges | Table | Optional | `-` | Sales Taxes and Charges |
| `other_charges_calculation` | Taxes and Charges Calculation | Text Editor | Optional | `-` | - |
| `item_wise_tax_details` | Item Wise Tax Details | Table | Optional | `-` | Item Wise Tax Detail |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | currency |
| `coupon_code` | Coupon Code | Link | Optional | `-` | Coupon Code |
| `apply_discount_on` | Apply Additional Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `base_discount_amount` | Additional Discount Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `additional_discount_percentage` | Additional Discount Percentage | Float | Optional | `-` | - |
| `discount_amount` | Additional Discount Amount | Currency | Optional | `-` | currency |
| `base_grand_total` | Grand Total (Company Currency) | Currency | ✓ Mandatory | `-` | Company:company:default_currency |
| `base_rounding_adjustment` | Rounding Adjustment (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounded_total` | Rounded Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_in_words` | In Words (Company Currency) | Data | Optional | `-` | - |
| `grand_total` | Grand Total | Currency | ✓ Mandatory | `-` | currency |
| `rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | currency |
| `rounded_total` | Rounded Total | Currency | Optional | `-` | currency |
| `in_words` | In Words | Data | Optional | `-` | - |
| `total_advance` | Total Advance | Currency | Optional | `-` | party_account_currency |
| `outstanding_amount` | Outstanding Amount | Currency | Optional | `-` | party_account_currency |
| `cash_bank_account` | Cash/Bank Account | Link | Optional | `-` | Account |
| `payments` | Sales Invoice Payment | Table | Optional | `-` | Sales Invoice Payment |
| `base_paid_amount` | Paid Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `paid_amount` | Paid Amount | Currency | Optional | `-` | currency |
| `base_change_amount` | Base Change Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `change_amount` | Change Amount | Currency | Optional | `-` | currency |
| `account_for_change_amount` | Account for Change Amount | Link | Optional | `-` | Account |
| `allocate_advances_automatically` | Allocate Advances Automatically (FIFO) | Check | Optional | `0` | - |
| `get_advances` | Get Advances Received | Button | Optional | `-` | set_advances |
| `advances` | Advances | Table | Optional | `-` | Sales Invoice Advance |
| `write_off_amount` | Write Off Amount | Currency | Optional | `-` | currency |
| `base_write_off_amount` | Write Off Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `write_off_outstanding_amount_automatically` | Write Off Outstanding Amount | Check | Optional | `0` | - |
| `write_off_account` | Write Off Account | Link | Optional | `-` | Account |
| `write_off_cost_center` | Write Off Cost Center | Link | Optional | `-` | Cost Center |
| `loyalty_points` | Loyalty Points | Int | Optional | `-` | - |
| `loyalty_amount` | Loyalty Amount | Currency | Optional | `-` | Company:company:default_currency |
| `redeem_loyalty_points` | Redeem Loyalty Points | Check | Optional | `0` | - |
| `loyalty_program` | Loyalty Program | Link | Optional | `-` | Loyalty Program |
| `loyalty_redemption_account` | Redemption Account | Link | Optional | `-` | Account |
| `loyalty_redemption_cost_center` | Redemption Cost Center | Link | Optional | `-` | Cost Center |
| `customer_address` | Customer Address | Link | Optional | `-` | Address |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `contact_person` | Contact Person | Link | Optional | `-` | Contact |
| `contact_display` | Contact | Small Text | Optional | `-` | - |
| `contact_mobile` | Mobile No | Data | Optional | `-` | Phone |
| `contact_email` | Contact Email | Data | Optional | `-` | Email |
| `territory` | Territory | Link | Optional | `-` | Territory |
| `shipping_address_name` | Shipping Address Name | Link | Optional | `-` | Address |
| `shipping_address` | Shipping Address | Text Editor | Optional | `-` | - |
| `company_address` | Company Address Name | Link | Optional | `-` | Address |
| `company_address_display` | Company Address | Text Editor | Optional | `-` | - |
| `company_contact_person` | Company Contact Person | Link | Optional | `-` | Contact |
| `payment_terms_template` | Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `payment_schedule` | Payment Schedule | Table | Optional | `-` | Payment Schedule |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions Details | Text Editor | Optional | `-` | - |
| `po_no` | Customer's Purchase Order | Data | Optional | `-` | - |
| `po_date` | Customer's Purchase Order Date | Date | Optional | `-` | - |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `group_same_items` | Group same items | Check | Optional | `0` | - |
| `language` | Print Language | Data | Optional | `-` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `utm_source` | Source | Link | Optional | `-` | UTM Source |
| `utm_medium` | Medium | Link | Optional | `-` | UTM Medium |
| `utm_campaign` | Campaign | Link | Optional | `-` | UTM Campaign |
| `inter_company_invoice_reference` | Inter Company Invoice Reference | Link | Optional | `-` | Purchase Invoice |
| `customer_group` | Customer Group | Link | Optional | `-` | Customer Group |
| `is_discounted` | Is Discounted | Check | Optional | `0` | - |
| `status` | Status | Select | Optional | `Draft` | Draft, Return, Credit Note Issued, Consolidated, Submitted, Paid, Partly Paid... |
| `title` | Title | Data | Optional | `-` | - |
| `debit_to` | Debit To | Link | ✓ Mandatory | `-` | Account |
| `party_account_currency` | Party Account Currency | Link | Optional | `-` | Currency |
| `is_opening` | Is Opening Entry | Select | Optional | `No` | No, Yes |
| `remarks` | Remarks | Small Text | Optional | `-` | - |
| `sales_partner` | Sales Partner | Link | Optional | `-` | Sales Partner |
| `amount_eligible_for_commission` | Amount Eligible for Commission | Currency | Optional | `-` | Company:company:default_currency |
| `commission_rate` | Commission Rate (%) | Float | Optional | `-` | - |
| `total_commission` | Total Commission | Currency | Optional | `-` | Company:company:default_currency |
| `sales_team` | Sales Team | Table | Optional | `-` | Sales Team |
| `from_date` | From Date | Date | Optional | `-` | - |
| `to_date` | To Date | Date | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `update_auto_repeat_reference` | Update Auto Repeat Reference | Button | Optional | `-` | - |
| `against_income_account` | Against Income Account | Small Text | Optional | `-` | - |

### DocType: `POS Opening Entry`
- **Submittable**: Yes
- **Total Data Fields**: 11

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `period_start_date` | Period Start Date | Datetime | ✓ Mandatory | `-` | - |
| `period_end_date` | Period End Date | Date | Optional | `-` | - |
| `status` | Status | Select | Optional | `Draft` | Draft, Open, Closed, Cancelled |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `set_posting_date` | Set Posting Date | Check | Optional | `0` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `pos_profile` | POS Profile | Link | ✓ Mandatory | `-` | POS Profile |
| `pos_closing_entry` | POS Closing Entry | Data | Optional | `-` | - |
| `user` | Cashier | Link | ✓ Mandatory | `-` | User |
| `balance_details` | Opening Balance Details | Table | ✓ Mandatory | `-` | POS Opening Entry Detail |
| `amended_from` | Amended From | Link | Optional | `-` | POS Opening Entry |

### DocType: `POS Closing Entry`
- **Submittable**: Yes
- **Total Data Fields**: 19

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `period_start_date` | Period Start Date | Datetime | ✓ Mandatory | `-` | - |
| `period_end_date` | Period End Date | Datetime | ✓ Mandatory | `Today` | - |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `posting_time` | Posting Time | Time | ✓ Mandatory | `Now` | - |
| `pos_opening_entry` | POS Opening Entry | Link | ✓ Mandatory | `-` | POS Opening Entry |
| `status` | Status | Select | Optional | `Draft` | Draft, Submitted, Queued, Failed, Cancelled |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `pos_profile` | POS Profile | Link | ✓ Mandatory | `-` | POS Profile |
| `user` | Cashier | Link | ✓ Mandatory | `-` | User |
| `pos_invoices` | POS Transactions | Table | Optional | `-` | POS Invoice Reference |
| `sales_invoices` | Sales Invoice Transactions | Table | Optional | `-` | Sales Invoice Reference |
| `taxes` | Taxes | Table | Optional | `-` | POS Closing Entry Taxes |
| `total_quantity` | Total Quantity | Float | Optional | `-` | - |
| `net_total` | Net Total | Currency | Optional | `0` | - |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | - |
| `grand_total` | Grand Total | Currency | Optional | `0` | - |
| `payment_reconciliation` | Payment Reconciliation | Table | Optional | `-` | POS Closing Entry Detail |
| `error_message` | Error | Small Text | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | POS Closing Entry |

### DocType: `Loyalty Program`
- **Submittable**: No
- **Total Data Fields**: 15

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `loyalty_program_name` | Loyalty Program Name | Data | ✓ Mandatory | `-` | - |
| `loyalty_program_type` | Loyalty Program Type | Select | Optional | `-` | Single Tier Program, Multiple Tier Program |
| `from_date` | From Date | Date | ✓ Mandatory | `-` | - |
| `to_date` | To Date | Date | Optional | `-` | - |
| `customer_group` | Customer Group | Link | Optional | `-` | Customer Group |
| `customer_territory` | Customer Territory | Link | Optional | `-` | Territory |
| `auto_opt_in` | Auto Opt In (For all customers) | Check | Optional | `0` | - |
| `collection_rules` | Collection Rules | Table | ✓ Mandatory | `-` | Loyalty Program Collection |
| `conversion_factor` | Conversion Factor | Float | Optional | `-` | - |
| `expiry_duration` | Expiry Duration (in days) | Int | Optional | `-` | - |
| `expense_account` | Expense Account | Link | Optional | `-` | Account |
| `company` | Company | Link | Optional | `-` | Company |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `loyalty_program_help` | Loyalty Program Help | HTML | Optional | `-` | - |

### DocType: `Blanket Order`
- **Submittable**: Yes
- **Total Data Fields**: 15

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | MFG-BLR-.YYYY.- |
| `blanket_order_type` | Order Type | Select | ✓ Mandatory | `-` | Selling, Purchasing |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `customer_name` | Customer Name | Data | Optional | `-` | - |
| `supplier` | Supplier | Link | Optional | `-` | Supplier |
| `supplier_name` | Supplier Name | Data | Optional | `-` | - |
| `order_no` | Order No | Data | Optional | `-` | - |
| `order_date` | Order Date | Date | Optional | `-` | - |
| `from_date` | From Date | Date | ✓ Mandatory | `-` | - |
| `to_date` | To Date | Date | ✓ Mandatory | `-` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `items` | Item | Table | ✓ Mandatory | `-` | Blanket Order Item |
| `amended_from` | Amended From | Link | Optional | `-` | Blanket Order |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions Details | Text Editor | Optional | `-` | - |

### DocType: `Customer`
- **Submittable**: No
- **Total Data Fields**: 51

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | Optional | `-` | CUST-.YYYY.- |
| `customer_name` | Customer Name | Data | ✓ Mandatory | `-` | - |
| `customer_type` | Customer Type | Select | ✓ Mandatory | `Company` | Company, Individual, Partnership |
| `alias` | Alias | Data | Optional | `-` | - |
| `gender` | Gender | Link | Optional | `-` | Gender |
| `customer_group` | Customer Group | Link | Optional | `-` | Customer Group |
| `territory` | Territory | Link | Optional | `-` | Territory |
| `image` | Image | Attach Image | Optional | `-` | - |
| `default_currency` | Billing Currency | Link | Optional | `-` | Currency |
| `default_bank_account` | Company Bank Account | Link | Optional | `-` | Bank Account |
| `default_price_list` | Price List | Link | Optional | `-` | Price List |
| `payment_terms` | Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `loyalty_program` | Loyalty Program | Link | Optional | `-` | Loyalty Program |
| `loyalty_program_tier` | Loyalty Program Tier | Data | Optional | `-` | - |
| `address_html` | Address HTML | HTML | Optional | `-` | - |
| `contact_html` | Contact HTML | HTML | Optional | `-` | - |
| `customer_primary_address` | Customer Primary Address | Link | Optional | `-` | Address |
| `primary_address` | Primary Address | Text Editor | Optional | `-` | - |
| `customer_primary_contact` | Customer Primary Contact | Link | Optional | `-` | Contact |
| `mobile_no` | Mobile No | Read Only | Optional | `-` | Mobile |
| `email_id` | Email Id | Read Only | Optional | `-` | Email |
| `first_name` | First Name | Read Only | Optional | `-` | - |
| `last_name` | Last Name | Read Only | Optional | `-` | - |
| `accounts` | Default Accounts | Table | Optional | `-` | Party Account |
| `credit_limits` | Credit & Overdue Limits | Table | Optional | `-` | Customer Credit Limit |
| `is_internal_customer` | Is Internal Customer | Check | Optional | `0` | - |
| `represents_company` | Represents Company | Link | Optional | `-` | Company |
| `companies` | Allowed to transact with | Table | Optional | `-` | Allowed To Transact With |
| `tax_id` | Tax ID | Data | Optional | `-` | - |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `tax_withholding_group` | Tax Withholding Group | Link | Optional | `-` | Tax Withholding Group |
| `tax_withholding_category` | Tax Withholding Category | Link | Optional | `-` | Tax Withholding Category |
| `so_required` | Allow sales invoice creation without sales order | Check | Optional | `0` | - |
| `dn_required` | Allow sales invoice creation without delivery note | Check | Optional | `0` | - |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `is_frozen` | Is Frozen | Check | Optional | `0` | - |
| `account_manager` | Account Manager | Link | Optional | `-` | User |
| `sales_team` | Sales Team | Table | Optional | `-` | Sales Team |
| `default_sales_partner` | Sales Partner | Link | Optional | `-` | Sales Partner |
| `default_commission_rate` | Commission Rate | Float | Optional | `-` | - |
| `portal_users` | Customer Portal Users | Table | Optional | `-` | Portal User |
| `lead_name` | Lead | Link | Optional | `-` | Lead |
| `opportunity_name` | Opportunity | Link | Optional | `-` | Opportunity |
| `prospect_name` | Prospect | Link | Optional | `-` | Prospect |
| `market_segment` | Market Segment | Link | Optional | `-` | Market Segment |
| `industry` | Industry | Link | Optional | `-` | Industry Type |
| `website` | Website | Data | Optional | `-` | - |
| `language` | Print Language | Link | Optional | `-` | Language |
| `customer_pos_id` | Customer POS ID | Data | Optional | `-` | - |
| `customer_details` | Customer Details | Text | Optional | `-` | - |
| `supplier_numbers` | Supplier Numbers | Table | Optional | `-` | Supplier Number At Customer |

### DocType: `Customer Group`
- **Submittable**: No
- **Total Data Fields**: 10

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `customer_group_name` | Customer Group Name | Data | ✓ Mandatory | `-` | - |
| `parent_customer_group` | Parent Customer Group | Link | Optional | `-` | Customer Group |
| `is_group` | Is Group | Check | Optional | `0` | - |
| `default_price_list` | Default Price List | Link | Optional | `-` | Price List |
| `payment_terms` | Default Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `lft` | lft | Int | Optional | `-` | - |
| `rgt` | rgt | Int | Optional | `-` | - |
| `old_parent` | old_parent | Link | Optional | `-` | Customer Group |
| `accounts` | Accounts | Table | Optional | `-` | Party Account |
| `credit_limits` | Credit & Overdue Limits | Table | Optional | `-` | Customer Credit Limit |

### DocType: `Selling Settings`
- **Submittable**: No
- **Total Data Fields**: 34

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `cust_master_name` | Customer Naming By | Select | Optional | `Customer Name` | Customer Name, Naming Series, Auto Name |
| `naming_series_details` | Naming Series options | Small Text | Optional | `-` | - |
| `configure` | Configure Series | Button | Optional | `-` | - |
| `customer_group` | Default Customer Group | Link | Optional | `-` | Customer Group |
| `territory` | Default Territory | Link | Optional | `-` | Territory |
| `selling_price_list` | Default Price List | Link | Optional | `-` | Price List |
| `fallback_to_default_price_list` | Use prices from Default Price List as fallback | Check | Optional | `0` | - |
| `editable_price_list_rate` | Allow editing Price List rate in transactions | Check | Optional | `0` | - |
| `maintain_same_sales_rate` | Maintain same rate throughout sales cycle | Check | Optional | `0` | - |
| `maintain_same_rate_action` | Action if same rate is not maintained throughout sales cycle | Select | Optional | `Stop` | Stop, Warn |
| `role_to_override_stop_action` | Role allowed to override stop action | Link | Optional | `-` | Role |
| `validate_selling_price` | Validate selling price for Item against purchase or valuation rate | Check | Optional | `0` | - |
| `editable_bundle_item_rates` | Calculate Product Bundle price based on child Item's rates | Check | Optional | `0` | - |
| `allow_negative_rates_for_items` | Allow negative rates for Items | Check | Optional | `0` | - |
| `so_required` | Is Sales Order required to create Sales Invoice/Delivery Note? | Select | Optional | `-` | No, Yes |
| `dn_required` | Is Delivery Note required to create Sales Invoice? | Select | Optional | `-` | No, Yes |
| `sales_update_frequency` | How often should sales data be updated in Company/Project? | Select | ✓ Mandatory | `Daily` | Monthly, Each Transaction, Daily |
| `allow_multiple_items` | Allow same Item to be added multiple times in a transaction | Check | Optional | `0` | - |
| `allow_against_multiple_purchase_orders` | Allow multiple Sales Orders against a customer's Purchase Order | Check | Optional | `0` | - |
| `hide_tax_id` | Hide Customer's Tax ID from sales transactions | Check | Optional | `0` | - |
| `allow_sales_order_creation_for_expired_quotation` | Allow Sales Order creation for expired Quotation | Check | Optional | `0` | - |
| `dont_reserve_sales_order_qty_on_sales_return` | Don't reserve Sales Order qty on sales return | Check | Optional | `0` | - |
| `enable_cutoff_date_on_bulk_delivery_note_creation` | Enable cut-off date on creating bulk Delivery Notes | Check | Optional | `0` | - |
| `set_zero_rate_for_expired_batch` | Set incoming rate as zero for expired Batch | Check | Optional | `0` | - |
| `allow_zero_qty_in_quotation` | Allow Quotation with zero quantity | Check | Optional | `0` | - |
| `allow_zero_qty_in_sales_order` | Allow Sales Order with zero quantity | Check | Optional | `0` | - |
| `blanket_order_allowance` | Blanket Order Allowance (%) | Float | Optional | `-` | - |
| `enable_tracking_sales_commissions` | Enable tracking sales commissions | Check | Optional | `0` | - |
| `enable_discount_accounting` | Enable discount accounting for selling | Check | Optional | `0` | - |
| `enable_utm` | Enable UTM | Check | Optional | `0` | - |
| `use_legacy_js_reactivity` | Use Legacy (Client side) Reactivity | Check | Optional | `0` | - |
| `allow_delivery_of_overproduced_qty` | Allow delivery of overproduced quantity | Check | Optional | `0` | - |
| `deliver_secondary_items` | Deliver secondary Items | Check | Optional | `0` | - |
| `transaction_naming_html` | transaction_naming_html | HTML | Optional | `-` | - |

## Module: Subcontracting
*Outward job work, Subcontracting BOMs, supplying raw materials to vendors, and receiving finished assemblies with simultaneous component consumption.*

### Summary of DocTypes in Subcontracting:
- **Subcontracting BOM**: 9 fields | Submittable: No
- **Subcontracting Inward Order**: 22 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Subcontracting Order**: 39 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Subcontracting Receipt**: 54 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)

### DocType: `Subcontracting BOM`
- **Submittable**: No
- **Total Data Fields**: 9

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `is_active` | Is Active | Check | Optional | `1` | - |
| `finished_good` | Finished Good | Link | ✓ Mandatory | `-` | Item |
| `finished_good_qty` | Finished Good Qty | Float | ✓ Mandatory | `1` | - |
| `finished_good_uom` | Finished Good UOM | Link | Optional | `-` | UOM |
| `finished_good_bom` | Finished Good BOM | Link | ✓ Mandatory | `-` | BOM |
| `service_item` | Service Item | Link | ✓ Mandatory | `-` | Item |
| `service_item_qty` | Service Item Qty | Float | ✓ Mandatory | `1` | - |
| `service_item_uom` | Service Item UOM | Link | ✓ Mandatory | `-` | UOM |
| `conversion_factor` | Conversion Factor | Float | Optional | `-` | - |

### DocType: `Subcontracting Inward Order`
- **Submittable**: Yes
- **Total Data Fields**: 22

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | SCI-ORD-.YYYY.- |
| `sales_order` | Subcontracting Sales Order | Link | ✓ Mandatory | `-` | Sales Order |
| `customer` | Customer | Link | ✓ Mandatory | `-` | Customer |
| `customer_name` | Customer Name | Data | ✓ Mandatory | `-` | - |
| `currency` | Customer Currency | Link | Optional | `-` | Currency |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `transaction_date` | Date | Date | ✓ Mandatory | `Today` | - |
| `customer_warehouse` | Customer Warehouse | Link | ✓ Mandatory | `-` | Warehouse |
| `amended_from` | Amended From | Link | Optional | `-` | Subcontracting Inward Order |
| `set_delivery_warehouse` | Set Delivery Warehouse | Link | Optional | `-` | Warehouse |
| `items` | Items | Table | ✓ Mandatory | `-` | Subcontracting Inward Order Item |
| `received_items` | Required Items | Table | Optional | `-` | Subcontracting Inward Order Received Item |
| `secondary_items` | Secondary Items | Table | Optional | `-` | Subcontracting Inward Order Secondary Item |
| `service_items` | Service Items | Table | ✓ Mandatory | `-` | Subcontracting Inward Order Service Item |
| `title` | Title | Data | Optional | `-` | - |
| `status` | Status | Select | ✓ Mandatory | `Draft` | Draft, Open, Ongoing, Produced, Delivered, Returned, Cancelled, Closed |
| `per_raw_material_received` | % Raw Material Received | Percent | Optional | `-` | - |
| `per_produced` | % Produced | Percent | Optional | `-` | - |
| `per_delivered` | % Delivered | Percent | Optional | `-` | - |
| `per_raw_material_returned` | % Raw Material Returned | Percent | Optional | `-` | - |
| `per_process_loss` | % Process Loss | Percent | Optional | `-` | - |
| `per_returned` | % Returned | Percent | Optional | `-` | - |

### DocType: `Subcontracting Order`
- **Submittable**: Yes
- **Total Data Fields**: 39

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | SC-ORD-.YYYY.- |
| `purchase_order` | Subcontracting Purchase Order | Link | ✓ Mandatory | `-` | Purchase Order |
| `supplier` | Job Worker | Link | ✓ Mandatory | `-` | Supplier |
| `supplier_name` | Job Worker Name | Data | ✓ Mandatory | `-` | - |
| `supplier_warehouse` | Job Worker Warehouse | Link | ✓ Mandatory | `-` | Warehouse |
| `supplier_currency` | Job Worker Currency | Link | Optional | `-` | Currency |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `transaction_date` | Date | Date | ✓ Mandatory | `Today` | - |
| `schedule_date` | Required By | Date | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Subcontracting Order |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `set_warehouse` | Set Target Warehouse | Link | Optional | `-` | Warehouse |
| `items` | Items | Table | ✓ Mandatory | `-` | Subcontracting Order Item |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total` | Total | Currency | Optional | `-` | Company:company:default_currency |
| `service_items` | Service Items | Table | ✓ Mandatory | `-` | Subcontracting Order Service Item |
| `set_reserve_warehouse` | Set Reserve Warehouse | Link | Optional | `-` | Warehouse |
| `reserve_stock` | Reserve Stock | Check | Optional | `0` | - |
| `supplied_items` | Supplied Items | Table | Optional | `-` | Subcontracting Order Supplied Item |
| `supplier_address` | Job Worker Address | Link | Optional | `-` | Address |
| `address_display` | Job Worker Address Details | Text Editor | Optional | `-` | - |
| `contact_person` | Job Worker Contact | Link | Optional | `-` | Contact |
| `contact_display` | Contact Name | Small Text | Optional | `-` | - |
| `contact_mobile` | Contact Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Small Text | Optional | `-` | Email |
| `shipping_address` | Company Shipping Address | Link | Optional | `-` | Address |
| `shipping_address_display` | Shipping Address Details | Text Editor | Optional | `-` | - |
| `billing_address` | Company Billing Address | Link | Optional | `-` | Address |
| `billing_address_display` | Billing Address Details | Text Editor | Optional | `-` | - |
| `distribute_additional_costs_based_on` | Distribute Additional Costs Based On  | Select | Optional | `Qty` | Qty, Amount |
| `additional_costs` | Additional Costs | Table | Optional | `-` | Landed Cost Taxes and Charges |
| `total_additional_costs` | Total Additional Costs | Currency | Optional | `-` | Company:company:default_currency |
| `title` | Title | Data | Optional | `-` | - |
| `status` | Status | Select | ✓ Mandatory | `Draft` | Draft, Open, Partially Received, Completed, Material Transferred, Partial Mat... |
| `per_received` | % Received | Percent | Optional | `-` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `production_plan` | Production Plan | Data | Optional | `-` | - |

### DocType: `Subcontracting Receipt`
- **Submittable**: Yes
- **Total Data Fields**: 54

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `title` | Title | Data | Optional | `{supplier_name}` | - |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | MAT-SCR-.YYYY.-, MAT-SCR-RET-.YYYY.- |
| `supplier` | Job Worker | Link | ✓ Mandatory | `-` | Supplier |
| `supplier_name` | Job Worker Name | Data | Optional | `-` | - |
| `supplier_delivery_note` | Job Worker Delivery Note | Data | Optional | `-` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `posting_date` | Date | Date | ✓ Mandatory | `Today` | - |
| `posting_time` | Posting Time | Time | ✓ Mandatory | `Now` | - |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `is_return` | Is Return | Check | Optional | `0` | - |
| `return_against` | Return Against Subcontracting Receipt | Link | Optional | `-` | Subcontracting Receipt |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `set_warehouse` | Accepted Warehouse | Link | Optional | `-` | Warehouse |
| `rejected_warehouse` | Rejected Warehouse | Link | Optional | `-` | Warehouse |
| `supplier_warehouse` | Job Worker Warehouse | Link | Optional | `-` | Warehouse |
| `items` | Items | Table | ✓ Mandatory | `-` | Subcontracting Receipt Item |
| `get_secondary_items` | Get Secondary Items | Button | Optional | `-` | get_secondary_items |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total` | Total | Currency | Optional | `-` | Company:company:default_currency |
| `reset_raw_materials_table` | Reset Raw Materials Table | Button | Optional | `-` | - |
| `get_current_stock` | Get Current Stock | Button | Optional | `-` | get_current_stock |
| `supplied_items` | Consumed Items | Table | Optional | `-` | Subcontracting Receipt Supplied Item |
| `in_words` | In Words | Data | Optional | `-` | - |
| `bill_no` | Bill No | Data | Optional | `-` | - |
| `bill_date` | Bill Date | Date | Optional | `-` | - |
| `supplier_address` | Select Job Worker Address | Link | Optional | `-` | Address |
| `contact_person` | Contact Person | Link | Optional | `-` | Contact |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `contact_display` | Contact | Small Text | Optional | `-` | - |
| `contact_mobile` | Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Small Text | Optional | `-` | Email |
| `shipping_address` | Select Shipping Address | Link | Optional | `-` | Address |
| `shipping_address_display` | Shipping Address | Text Editor | Optional | `-` | - |
| `billing_address` | Select Billing Address | Link | Optional | `-` | Address |
| `billing_address_display` | Billing Address | Text Editor | Optional | `-` | - |
| `distribute_additional_costs_based_on` | Distribute Additional Costs Based On  | Select | Optional | `Qty` | Qty, Amount |
| `additional_costs` | Additional Costs | Table | Optional | `-` | Landed Cost Taxes and Charges |
| `total_additional_costs` | Total Additional Costs | Currency | Optional | `-` | Company:company:default_currency |
| `amended_from` | Amended From | Link | Optional | `-` | Subcontracting Receipt |
| `range` | Range | Data | Optional | `-` | - |
| `represents_company` | Represents Company | Link | Optional | `-` | Company |
| `status` | Status | Select | ✓ Mandatory | `Draft` | Draft, Completed, Return, Return Issued, Cancelled, Closed |
| `per_returned` | % Returned | Percent | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `language` | Print Language | Data | Optional | `-` | - |
| `instructions` | Instructions | Small Text | Optional | `-` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `other_details` | Other Details | HTML | Optional | `-` | <div class="columnHeading">Other Details</div> |
| `remarks` | Remarks | Small Text | Optional | `-` | - |
| `transporter_name` | Transporter Name | Data | Optional | `-` | - |
| `lr_no` | Vehicle Number | Data | Optional | `-` | - |
| `lr_date` | Vehicle Date | Date | Optional | `-` | - |

## Module: Accounting
*Complete finance suite with 9 dedicated submodules: Invoicing, Payments, Financial Reports (P&L, Balance Sheet, Cash Flow), Accounts Setup, Taxes, Banking, Budget, Subscription, and Share Management.*

### Summary of DocTypes in Accounting:
- **Sales Invoice**: 158 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Purchase Invoice**: 137 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Payment Entry**: 70 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Journal Entry**: 52 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Payment Request**: 43 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Payment Order**: 10 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Payment Reconciliation**: 23 fields | Submittable: No
- **Account**: 18 fields | Submittable: No
- **Cost Center**: 9 fields | Submittable: No
- **Fiscal Year**: 7 fields | Submittable: No
- **Currency**: 8 fields | Submittable: No
- **Sales Taxes and Charges Template**: 6 fields | Submittable: No
- **Purchase Taxes and Charges Template**: 6 fields | Submittable: No
- **Tax Rule**: 25 fields | Submittable: No
- **Tax Withholding Category**: 8 fields | Submittable: No
- **Bank**: 7 fields | Submittable: No
- **Bank Account**: 21 fields | Submittable: No
- **Bank Clearance**: 8 fields | Submittable: No
- **Bank Transaction**: 25 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Budget**: 29 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Monthly Distribution**: 3 fields | Submittable: No
- **Subscription Plan**: 11 fields | Submittable: No
- **Subscription**: 25 fields | Submittable: No
- **Shareholder**: 9 fields | Submittable: No
- **Share Transfer**: 17 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)

### DocType: `Sales Invoice`
- **Submittable**: Yes
- **Total Data Fields**: 158

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `company_tax_id` | Company Tax ID | Data | Optional | `-` | - |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | ACC-SINV-.YYYY.-, ACC-SINV-RET-.YYYY.- |
| `customer` | Customer | Link | ✓ Mandatory | `-` | Customer |
| `customer_name` | Customer Name | Small Text | Optional | `-` | - |
| `tax_id` | Tax Id | Data | Optional | `-` | - |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `posting_time` | Posting Time | Time | Optional | `Now` | - |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `due_date` | Payment Due Date | Date | Optional | `-` | - |
| `is_pos` | Include Payment (POS) | Check | Optional | `0` | - |
| `pos_profile` | POS Profile | Link | Optional | `-` | POS Profile |
| `is_consolidated` | Is Consolidated | Check | Optional | `0` | - |
| `is_return` | Is Return (Credit Note) | Check | Optional | `0` | - |
| `return_against` | Return Against | Link | Optional | `-` | Sales Invoice |
| `update_outstanding_for_self` | Update Outstanding for Self | Check | Optional | `1` | - |
| `update_billed_amount_in_sales_order` | Update Billed Amount in Sales Order | Check | Optional | `0` | - |
| `update_billed_amount_in_delivery_note` | Update Billed Amount in Delivery Note | Check | Optional | `1` | - |
| `is_debit_note` | Is Rate Adjustment Entry (Debit Note) | Check | Optional | `0` | - |
| `apply_tds` | Consider for Tax Withholding | Check | Optional | `0` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Sales Invoice |
| `is_created_using_pos` | Is created using POS | Check | Optional | `0` | - |
| `pos_closing_entry` | POS Closing Entry | Link | Optional | `-` | POS Closing Entry |
| `has_subcontracted` | Has Subcontracted | Check | Optional | `0` | - |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `conversion_rate` | Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `selling_price_list` | Price List | Link | ✓ Mandatory | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | ✓ Mandatory | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `update_stock` | Update Stock | Check | Optional | `0` | - |
| `set_warehouse` | Source Warehouse | Link | Optional | `-` | Warehouse |
| `set_target_warehouse` | Set Target Warehouse | Link | Optional | `-` | Warehouse |
| `items` | Items | Table | ✓ Mandatory | `-` | Sales Invoice Item |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total_net_weight` | Total Net Weight | Float | Optional | `-` | - |
| `base_total` | Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_net_total` | Net Total (Company Currency) | Currency | ✓ Mandatory | `-` | Company:company:default_currency |
| `total` | Total | Currency | Optional | `-` | currency |
| `net_total` | Net Total | Currency | Optional | `-` | currency |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes_and_charges` | Sales Taxes and Charges Template | Link | Optional | `-` | Sales Taxes and Charges Template |
| `shipping_rule` | Shipping Rule | Link | Optional | `-` | Shipping Rule |
| `incoterm` | Incoterm | Link | Optional | `-` | Incoterm |
| `named_place` | Named Place | Data | Optional | `-` | - |
| `taxes` | Sales Taxes and Charges | Table | Optional | `-` | Sales Taxes and Charges |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | currency |
| `use_company_roundoff_cost_center` | Use Company default Cost Center for Round off | Check | Optional | `0` | - |
| `grand_total` | Grand Total | Currency | ✓ Mandatory | `-` | currency |
| `in_words` | In Words | Small Text | Optional | `-` | - |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | currency |
| `rounded_total` | Rounded Total | Currency | Optional | `-` | currency |
| `base_grand_total` | Grand Total (Company Currency | Currency | ✓ Mandatory | `-` | Company:company:default_currency |
| `base_in_words` | In Words | Small Text | Optional | `-` | - |
| `base_rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounded_total` | Rounded Total | Currency | Optional | `-` | Company:company:default_currency |
| `total_advance` | Total Advance | Currency | Optional | `-` | party_account_currency |
| `outstanding_amount` | Outstanding Amount | Currency | Optional | `-` | party_account_currency |
| `tax_withholding_group` | Tax Withholding Group | Link | Optional | `-` | Tax Withholding Group |
| `ignore_tax_withholding_threshold` | Ignore Tax Withholding Threshold | Check | Optional | `0` | - |
| `override_tax_withholding_entries` | Edit Tax Withholding Entries | Check | Optional | `0` | - |
| `tax_withholding_entries` | Tax Withholding Entries | Table | Optional | `-` | Tax Withholding Entry |
| `apply_discount_on` | Apply Additional Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `base_discount_amount` | Additional Discount Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `coupon_code` | Coupon Code | Link | Optional | `-` | Coupon Code |
| `additional_discount_percentage` | Additional Discount Percentage | Float | Optional | `-` | - |
| `discount_amount` | Additional Discount Amount | Currency | Optional | `-` | currency |
| `is_cash_or_non_trade_discount` | Is Cash or Non Trade Discount | Check | Optional | `0` | - |
| `additional_discount_account` | Discount Account | Link | Optional | `-` | Account |
| `other_charges_calculation` | Taxes and Charges Calculation | Text Editor | Optional | `-` | - |
| `item_wise_tax_details` | Item Wise Tax Details | Table | Optional | `-` | Item Wise Tax Detail |
| `pricing_rules` | Pricing Rule Detail | Table | Optional | `-` | Pricing Rule Detail |
| `packed_items` | Packed Items | Table | Optional | `-` | Packed Item |
| `product_bundle_help` | Product Bundle Help | HTML | Optional | `-` | - |
| `timesheets` | Time Sheets | Table | Optional | `-` | Sales Invoice Timesheet |
| `total_billing_hours` | Total Billing Hours | Float | Optional | `-` | - |
| `total_billing_amount` | Total Billing Amount | Currency | Optional | `0` | currency |
| `cash_bank_account` | Cash/Bank Account | Link | Optional | `-` | Account |
| `payments` | Sales Invoice Payment | Table | Optional | `-` | Sales Invoice Payment |
| `base_paid_amount` | Paid Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `paid_amount` | Paid Amount | Currency | Optional | `-` | currency |
| `base_change_amount` | Base Change Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `change_amount` | Change Amount | Currency | Optional | `-` | currency |
| `account_for_change_amount` | Account for Change Amount | Link | Optional | `-` | Account |
| `allocate_advances_automatically` | Allocate Advances Automatically (FIFO) | Check | Optional | `0` | - |
| `only_include_allocated_payments` | Only Include Allocated Payments | Check | Optional | `0` | - |
| `get_advances` | Get Advances Received | Button | Optional | `-` | set_advances |
| `advances` | Advances | Table | Optional | `-` | Sales Invoice Advance |
| `write_off_amount` | Write Off Amount | Currency | Optional | `-` | currency |
| `base_write_off_amount` | Write Off Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `write_off_outstanding_amount_automatically` | Write Off Outstanding Amount | Check | Optional | `0` | - |
| `write_off_account` | Write Off Account | Link | Optional | `-` | Account |
| `write_off_cost_center` | Write Off Cost Center | Link | Optional | `-` | Cost Center |
| `redeem_loyalty_points` | Redeem Loyalty Points | Check | Optional | `0` | - |
| `loyalty_points` | Loyalty Points | Int | Optional | `-` | - |
| `loyalty_amount` | Loyalty Amount | Currency | Optional | `-` | Company:company:default_currency |
| `loyalty_program` | Loyalty Program | Link | Optional | `-` | Loyalty Program |
| `dont_create_loyalty_points` | Don't Create Loyalty Points | Check | Optional | `0` | - |
| `loyalty_redemption_account` | Redemption Account | Link | Optional | `-` | Account |
| `loyalty_redemption_cost_center` | Redemption Cost Center | Link | Optional | `-` | Cost Center |
| `customer_address` | Customer Address | Link | Optional | `-` | Address |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `contact_person` | Contact Person | Link | Optional | `-` | Contact |
| `contact_display` | Contact | Small Text | Optional | `-` | - |
| `contact_mobile` | Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Data | Optional | `-` | Email |
| `territory` | Territory | Link | Optional | `-` | Territory |
| `shipping_address_name` | Shipping Address Name | Link | Optional | `-` | Address |
| `shipping_address` | Shipping Address | Text Editor | Optional | `-` | - |
| `dispatch_address_name` | Dispatch Address Name | Link | Optional | `-` | Address |
| `dispatch_address` | Dispatch Address | Text Editor | Optional | `-` | - |
| `company_address` | Company Address Name | Link | Optional | `-` | Address |
| `company_address_display` | Company Address | Text Editor | Optional | `-` | - |
| `company_contact_person` | Company Contact Person | Link | Optional | `-` | Contact |
| `ignore_default_payment_terms_template` | Ignore Default Payment Terms Template | Check | Optional | `0` | - |
| `payment_terms_template` | Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `payment_schedule` | Payment Schedule | Table | Optional | `-` | Payment Schedule |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions Details | Text Editor | Optional | `-` | - |
| `po_no` | Customer's Purchase Order | Data | Optional | `-` | - |
| `po_date` | Customer's Purchase Order Date | Date | Optional | `-` | - |
| `debit_to` | Debit To | Link | ✓ Mandatory | `-` | Account |
| `party_account_currency` | Party Account Currency | Link | Optional | `-` | Currency |
| `is_opening` | Is Opening Entry | Select | Optional | `No` | No, Yes |
| `unrealized_profit_loss_account` | Unrealized Profit / Loss Account | Link | Optional | `-` | Account |
| `against_income_account` | Against Income Account | Small Text | Optional | `-` | - |
| `sales_partner` | Sales Partner | Link | Optional | `-` | Sales Partner |
| `amount_eligible_for_commission` | Amount Eligible for Commission | Currency | Optional | `-` | Company:company:default_currency |
| `commission_rate` | Commission Rate (%) | Float | Optional | `-` | - |
| `total_commission` | Total Commission | Currency | Optional | `-` | Company:company:default_currency |
| `sales_team` | Sales Contributions and Incentives | Table | Optional | `-` | Sales Team |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `group_same_items` | Group same items | Check | Optional | `0` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `language` | Print Language | Link | Optional | `-` | Language |
| `subscription` | Subscription | Link | Optional | `-` | Subscription |
| `from_date` | From Date | Date | Optional | `-` | - |
| `to_date` | To Date | Date | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `update_auto_repeat_reference` | Update Auto Repeat Reference | Button | Optional | `-` | - |
| `utm_source` | Source | Link | Optional | `-` | UTM Source |
| `utm_medium` | Medium | Link | Optional | `-` | UTM Medium |
| `utm_campaign` | Campaign | Link | Optional | `-` | UTM Campaign |
| `utm_content` | Content | Data | Optional | `-` | - |
| `status` | Status | Select | Optional | `Draft` | Draft, Return, Credit Note Issued, Submitted, Paid, Partly Paid, Unpaid, Unpa... |
| `remarks` | Remarks | Small Text | Optional | `-` | - |
| `customer_group` | Customer Group | Link | Optional | `-` | Customer Group |
| `title` | Title | Data | Optional | `-` | - |
| `is_internal_customer` | Is Internal Customer | Check | Optional | `0` | - |
| `represents_company` | Represents Company | Link | Optional | `-` | Company |
| `inter_company_invoice_reference` | Inter Company Invoice Reference | Link | Optional | `-` | Purchase Invoice |
| `is_discounted` | Is Discounted | Check | Optional | `0` | - |

### DocType: `Purchase Invoice`
- **Submittable**: Yes
- **Total Data Fields**: 137

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | ACC-PINV-.YYYY.-, ACC-PINV-RET-.YYYY.- |
| `supplier` | Supplier | Link | ✓ Mandatory | `-` | Supplier |
| `supplier_name` | Supplier Name | Data | Optional | `-` | - |
| `tax_id` | Tax Id | Read Only | Optional | `-` | - |
| `company` | Company | Link | Optional | `-` | Company |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `posting_time` | Posting Time | Time | Optional | `Now` | - |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `due_date` | Due Date | Date | Optional | `-` | - |
| `is_paid` | Is Paid | Check | Optional | `0` | - |
| `is_return` | Is Return (Debit Note) | Check | Optional | `0` | - |
| `return_against` | Return Against Purchase Invoice | Link | Optional | `-` | Purchase Invoice |
| `update_outstanding_for_self` | Update Outstanding for Self | Check | Optional | `1` | - |
| `update_billed_amount_in_purchase_order` | Update Billed Amount in Purchase Order | Check | Optional | `0` | - |
| `update_billed_amount_in_purchase_receipt` | Update Billed Amount in Purchase Receipt | Check | Optional | `1` | - |
| `apply_tds` | Consider for Tax Withholding | Check | Optional | `0` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Purchase Invoice |
| `bill_no` | Supplier Invoice No | Data | Optional | `-` | - |
| `bill_date` | Supplier Invoice Date | Date | Optional | `-` | - |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `currency` | Currency | Link | Optional | `-` | Currency |
| `conversion_rate` | Exchange Rate | Float | Optional | `-` | - |
| `use_transaction_date_exchange_rate` | Use Transaction Date Exchange Rate | Check | Optional | `0` | - |
| `buying_price_list` | Price List | Link | Optional | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | Optional | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | Optional | `-` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `update_stock` | Update Stock | Check | Optional | `0` | - |
| `set_warehouse` | Set Accepted Warehouse | Link | Optional | `-` | Warehouse |
| `set_from_warehouse` | Set From Warehouse | Link | Optional | `-` | Warehouse |
| `is_subcontracted` | Is Subcontracted | Check | Optional | `0` | - |
| `rejected_warehouse` | Rejected Warehouse | Link | Optional | `-` | Warehouse |
| `supplier_warehouse` | Supplier Warehouse | Link | Optional | `-` | Warehouse |
| `items` | Items | Table | ✓ Mandatory | `-` | Purchase Invoice Item |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total_net_weight` | Total Net Weight | Float | Optional | `-` | - |
| `base_total` | Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_net_total` | Net Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `claimed_landed_cost_amount` | Claimed Landed Cost Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total` | Total | Currency | Optional | `-` | currency |
| `net_total` | Net Total | Currency | Optional | `-` | currency |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes_and_charges` | Purchase Taxes and Charges Template | Link | Optional | `-` | Purchase Taxes and Charges Template |
| `shipping_rule` | Shipping Rule | Link | Optional | `-` | Shipping Rule |
| `incoterm` | Incoterm | Link | Optional | `-` | Incoterm |
| `named_place` | Named Place | Data | Optional | `-` | - |
| `taxes` | Purchase Taxes and Charges | Table | Optional | `-` | Purchase Taxes and Charges |
| `base_taxes_and_charges_added` | Taxes and Charges Added (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_taxes_and_charges_deducted` | Taxes and Charges Deducted (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `taxes_and_charges_added` | Taxes and Charges Added | Currency | Optional | `-` | currency |
| `taxes_and_charges_deducted` | Taxes and Charges Deducted | Currency | Optional | `-` | currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | currency |
| `use_company_roundoff_cost_center` | Use Company Default Round Off Cost Center | Check | Optional | `0` | - |
| `grand_total` | Grand Total | Currency | Optional | `-` | currency |
| `in_words` | In Words | Data | Optional | `-` | - |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | currency |
| `rounded_total` | Rounded Total | Currency | Optional | `-` | currency |
| `base_grand_total` | Grand Total | Currency | Optional | `-` | Company:company:default_currency |
| `base_in_words` | In Words | Data | Optional | `-` | - |
| `base_rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounded_total` | Rounded Total | Currency | Optional | `-` | Company:company:default_currency |
| `total_advance` | Total Advance | Currency | Optional | `-` | party_account_currency |
| `outstanding_amount` | Outstanding Amount | Currency | Optional | `-` | party_account_currency |
| `tax_withholding_group` | Tax Withholding Group | Link | Optional | `-` | Tax Withholding Group |
| `ignore_tax_withholding_threshold` | Ignore Tax Withholding Threshold | Check | Optional | `0` | - |
| `override_tax_withholding_entries` | Edit Tax Withholding Entries | Check | Optional | `0` | - |
| `tax_withholding_entries` | Tax Withholding Entries | Table | Optional | `-` | Tax Withholding Entry |
| `apply_discount_on` | Apply Additional Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `base_discount_amount` | Additional Discount Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `additional_discount_percentage` | Additional Discount Percentage | Float | Optional | `-` | - |
| `discount_amount` | Additional Discount Amount | Currency | Optional | `-` | currency |
| `other_charges_calculation` | Taxes and Charges Calculation | Text Editor | Optional | `-` | - |
| `item_wise_tax_details` | Item Wise Tax Details | Table | Optional | `-` | Item Wise Tax Detail |
| `pricing_rules` | Pricing Rule Detail | Table | Optional | `-` | Pricing Rule Detail |
| `supplied_items` | Supplied Items | Table | Optional | `-` | Purchase Receipt Item Supplied |
| `mode_of_payment` | Mode of Payment | Link | Optional | `-` | Mode of Payment |
| `base_paid_amount` | Paid Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `clearance_date` | Clearance Date | Date | Optional | `-` | - |
| `cash_bank_account` | Cash/Bank Account | Link | Optional | `-` | Account |
| `paid_amount` | Paid Amount | Currency | Optional | `-` | currency |
| `allocate_advances_automatically` | Set Advances and Allocate (FIFO) | Check | Optional | `0` | - |
| `only_include_allocated_payments` | Only Include Allocated Payments | Check | Optional | `0` | - |
| `get_advances` | Get Advances Paid | Button | Optional | `-` | set_advances |
| `advances` | Advances | Table | Optional | `-` | Purchase Invoice Advance |
| `write_off_amount` | Write Off Amount | Currency | Optional | `-` | currency |
| `base_write_off_amount` | Write Off Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `write_off_account` | Write Off Account | Link | Optional | `-` | Account |
| `write_off_cost_center` | Write Off Cost Center | Link | Optional | `-` | Cost Center |
| `supplier_address` | Select Supplier Address | Link | Optional | `-` | Address |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `contact_person` | Contact Person | Link | Optional | `-` | Contact |
| `contact_display` | Contact | Small Text | Optional | `-` | - |
| `contact_mobile` | Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Small Text | Optional | `-` | Email |
| `dispatch_address` | Select Dispatch Address  | Link | Optional | `-` | Address |
| `dispatch_address_display` | Dispatch Address | Text Editor | Optional | `-` | - |
| `shipping_address` | Select Shipping Address | Link | Optional | `-` | Address |
| `shipping_address_display` | Shipping Address | Text Editor | Optional | `-` | - |
| `billing_address` | Select Billing Address | Link | Optional | `-` | Address |
| `billing_address_display` | Billing Address | Text Editor | Optional | `-` | - |
| `payment_terms_template` | Payment Terms Template | Link | Optional | `-` | Payment Terms Template |
| `ignore_default_payment_terms_template` | Ignore Default Payment Terms Template | Check | Optional | `0` | - |
| `payment_schedule` | Payment Schedule | Table | Optional | `-` | Payment Schedule |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions | Text Editor | Optional | `-` | - |
| `status` | Status | Select | Optional | `Draft` | Draft, Return, Debit Note Issued, Submitted, Paid, Partly Paid, Unpaid, Overd... |
| `per_received` | Per Received | Percent | Optional | `-` | - |
| `credit_to` | Credit To | Link | ✓ Mandatory | `-` | Account |
| `party_account_currency` | Party Account Currency | Link | Optional | `-` | Currency |
| `is_opening` | Is Opening Entry | Select | Optional | `No` | No, Yes |
| `against_expense_account` | Against Expense Account | Small Text | Optional | `-` | - |
| `unrealized_profit_loss_account` | Unrealized Profit / Loss Account | Link | Optional | `-` | Account |
| `subscription` | Subscription | Link | Optional | `-` | Subscription |
| `from_date` | From Date | Date | Optional | `-` | - |
| `to_date` | To Date | Date | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `update_auto_repeat_reference` | Update Auto Repeat Reference | Button | Optional | `-` | - |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `group_same_items` | Group same items | Check | Optional | `0` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `language` | Print Language | Data | Optional | `-` | - |
| `on_hold` | Hold Invoice | Check | Optional | `0` | - |
| `release_date` | Release Date | Date | Optional | `-` | - |
| `hold_comment` | Reason For Putting On Hold | Small Text | Optional | `-` | - |
| `is_internal_supplier` | Is Internal Supplier | Check | Optional | `0` | - |
| `title` | Title | Data | Optional | `-` | - |
| `represents_company` | Represents Company | Link | Optional | `-` | Company |
| `supplier_group` | Supplier Group | Link | Optional | `-` | Supplier Group |
| `sender` | Sender | Data | Optional | `-` | Email |
| `inter_company_invoice_reference` | Inter Company Invoice Reference | Link | Optional | `-` | Sales Invoice |
| `is_old_subcontracting_flow` | Is Old Subcontracting Flow | Check | Optional | `0` | - |
| `remarks` | Remarks | Small Text | Optional | `-` | - |

### DocType: `Payment Entry`
- **Submittable**: Yes
- **Total Data Fields**: 70

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | ACC-PAY-.YYYY.- |
| `payment_type` | Payment Type | Select | ✓ Mandatory | `-` | Receive, Pay, Internal Transfer |
| `payment_order_status` | Payment Order Status | Select | Optional | `-` | Initiated, Payment Ordered |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `mode_of_payment` | Mode of Payment | Link | Optional | `-` | Mode of Payment |
| `party_type` | Party Type | Link | Optional | `-` | DocType |
| `party` | Party | Dynamic Link | Optional | `-` | party_type |
| `party_name` | Party Name | Data | Optional | `-` | - |
| `book_advance_payments_in_separate_party_account` | Book Advance Payments in Separate Party Account | Check | Optional | `0` | - |
| `reconcile_on_advance_payment_date` | Reconcile on Advance Payment Date | Check | Optional | `0` | - |
| `apply_tds` | Consider for Tax Withholding | Check | Optional | `0` | - |
| `tax_withholding_category` | Tax Withholding Category | Link | Optional | `-` | Tax Withholding Category |
| `bank_account` | Company Bank Account | Link | Optional | `-` | Bank Account |
| `party_bank_account` | Party Bank Account | Link | Optional | `-` | Bank Account |
| `contact_person` | Contact | Link | Optional | `-` | Contact |
| `contact_email` | Email | Data | Optional | `-` | Email |
| `paid_from` | Account Paid From | Link | ✓ Mandatory | `-` | Account |
| `paid_from_account_type` | Paid From Account Type | Data | Optional | `-` | - |
| `paid_from_account_currency` | Account Currency (From) | Link | ✓ Mandatory | `-` | Currency |
| `paid_to` | Account Paid To | Link | ✓ Mandatory | `-` | Account |
| `paid_to_account_type` | Paid To Account Type | Data | Optional | `-` | - |
| `paid_to_account_currency` | Account Currency (To) | Link | ✓ Mandatory | `-` | Currency |
| `paid_amount` | Paid Amount | Currency | ✓ Mandatory | `-` | paid_from_account_currency |
| `paid_amount_after_tax` | Paid Amount After Tax | Currency | Optional | `-` | paid_from_account_currency |
| `source_exchange_rate` | Source Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `base_paid_amount` | Paid Amount (Company Currency) | Currency | ✓ Mandatory | `-` | Company:company:default_currency |
| `base_paid_amount_after_tax` | Paid Amount After Tax (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `received_amount` | Received Amount | Currency | ✓ Mandatory | `-` | paid_to_account_currency |
| `received_amount_after_tax` | Received Amount After Tax | Currency | Optional | `-` | paid_to_account_currency |
| `target_exchange_rate` | Target Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `base_received_amount` | Received Amount (Company Currency) | Currency | ✓ Mandatory | `-` | Company:company:default_currency |
| `base_received_amount_after_tax` | Received Amount After Tax (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `get_outstanding_invoices` | Get Outstanding Invoices | Button | Optional | `-` | - |
| `get_outstanding_orders` | Get Outstanding Orders | Button | Optional | `-` | - |
| `references` | Payment References | Table | Optional | `-` | Payment Entry Reference |
| `total_allocated_amount` | Total Allocated Amount | Currency | Optional | `-` | - |
| `base_total_allocated_amount` | Total Allocated Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `unallocated_amount` | Unallocated Amount | Currency | Optional | `-` | - |
| `difference_amount` | Difference Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `write_off_difference_amount` | Write Off Difference Amount | Button | Optional | `-` | - |
| `purchase_taxes_and_charges_template` | Purchase Taxes and Charges Template | Link | Optional | `-` | Purchase Taxes and Charges Template |
| `sales_taxes_and_charges_template` | Sales Taxes and Charges Template | Link | Optional | `-` | Sales Taxes and Charges Template |
| `taxes` | Advance Taxes and Charges | Table | Optional | `-` | Advance Taxes and Charges |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | - |
| `deductions` | Payment Deductions or Loss | Table | Optional | `-` | Payment Entry Deduction |
| `tax_withholding_group` | Tax Withholding Group | Link | Optional | `-` | Tax Withholding Group |
| `ignore_tax_withholding_threshold` | Ignore Tax Withholding Threshold | Check | Optional | `0` | - |
| `override_tax_withholding_entries` | Edit Tax Withholding Entries | Check | Optional | `0` | - |
| `tax_withholding_entries` | Tax Withholding Entries | Table | Optional | `-` | Tax Withholding Entry |
| `reference_no` | Cheque/Reference No | Data | Optional | `-` | - |
| `reference_date` | Cheque/Reference Date | Date | Optional | `-` | - |
| `clearance_date` | Clearance Date | Date | Optional | `-` | - |
| `project` | Project | Link | Optional | `-` | Project |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `status` | Status | Select | Optional | `Draft` | Draft, Submitted, Cancelled |
| `custom_remarks` | Custom Remarks | Check | Optional | `0` | - |
| `remarks` | Remarks | Small Text | Optional | `-` | - |
| `base_in_words` | In Words (Company Currency) | Small Text | Optional | `-` | - |
| `is_opening` | Is Opening | Select | Optional | `No` | No, Yes |
| `title` | Title | Data | Optional | `-` | - |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `bank` | Bank | Read Only | Optional | `-` | - |
| `bank_account_no` | Bank Account No | Read Only | Optional | `-` | - |
| `payment_order` | Payment Order | Link | Optional | `-` | Payment Order |
| `in_words` | In Words | Small Text | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Payment Entry |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |

### DocType: `Journal Entry`
- **Submittable**: Yes
- **Total Data Fields**: 52

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `voucher_type` | Entry Type | Select | ✓ Mandatory | `Journal Entry` | Journal Entry, Inter Company Journal Entry, Bank Entry, Cash Entry, Credit Ca... |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | ACC-JV-.YYYY.- |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `-` | - |
| `multi_currency` | Multi Currency | Check | Optional | `0` | - |
| `apply_tds` | Consider for Tax Withholding  | Check | Optional | `0` | - |
| `tax_withholding_category` | Tax Withholding Category | Link | Optional | `-` | Tax Withholding Category |
| `is_system_generated` | Is System Generated | Check | Optional | `0` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Journal Entry |
| `for_all_stock_asset_accounts` | For All Stock Asset Accounts | Check | Optional | `1` | - |
| `stock_asset_account` | Stock Asset Account | Link | Optional | `-` | Account |
| `periodic_entry_difference_account` | Periodic Entry Difference Account | Link | Optional | `-` | Account |
| `get_balance_for_periodic_accounting` | Get Balance | Button | Optional | `-` | - |
| `accounts` | Accounting Entries | Table | ✓ Mandatory | `-` | Journal Entry Account |
| `total_debit` | Total Debit | Currency | Optional | `-` | Company:company:default_currency |
| `total_credit` | Total Credit | Currency | Optional | `-` | Company:company:default_currency |
| `difference` | Difference (Dr - Cr) | Currency | Optional | `-` | Company:company:default_currency |
| `get_balance` | Make Difference Entry | Button | Optional | `-` | - |
| `cheque_no` | Reference Number | Data | Optional | `-` | - |
| `cheque_date` | Reference Date | Date | Optional | `-` | - |
| `clearance_date` | Clearance Date | Date | Optional | `-` | - |
| `user_remark` | User Remark | Small Text | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `tax_withholding_group` | Tax Withholding Group | Link | Optional | `-` | Tax Withholding Group |
| `ignore_tax_withholding_threshold` | Ignore Tax Withholding Threshold | Check | Optional | `0` | - |
| `override_tax_withholding_entries` | Edit Tax Withholding Entries | Check | Optional | `0` | - |
| `tax_withholding_entries` | Tax Withholding Entries | Table | Optional | `-` | Tax Withholding Entry |
| `bill_no` | Bill No | Data | Optional | `-` | - |
| `bill_date` | Bill Date | Date | Optional | `-` | - |
| `due_date` | Due Date | Date | Optional | `-` | - |
| `inter_company_journal_entry_reference` | Inter Company Journal Entry Reference | Link | Optional | `-` | Journal Entry |
| `process_deferred_accounting` | Process Deferred Accounting | Link | Optional | `-` | Process Deferred Accounting |
| `reversal_of` | Reversal Of | Link | Optional | `-` | Journal Entry |
| `payment_order` | Payment Order | Link | Optional | `-` | Payment Order |
| `stock_entry` | Stock Entry | Link | Optional | `-` | Stock Entry |
| `pay_to_recd_from` | Pay To / Recd From | Data | Optional | `-` | - |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `total_amount_currency` | Total Amount Currency | Link | Optional | `-` | Currency |
| `total_amount` | Total Amount | Currency | Optional | `-` | total_amount_currency |
| `total_amount_in_words` | Total Amount in Words | Data | Optional | `-` | - |
| `write_off_based_on` | Write Off Based On | Select | Optional | `Accounts Receivable` | Accounts Receivable, Accounts Payable |
| `get_outstanding_invoices` | Get Outstanding Invoices | Button | Optional | `-` | get_outstanding_invoices |
| `write_off_amount` | Write Off Amount | Currency | Optional | `-` | Company:company:default_currency |
| `is_opening` | Is Opening | Select | Optional | `No` | No, Yes |
| `finance_book` | Finance Book | Link | Optional | `-` | Finance Book |
| `from_template` | From Template | Link | Optional | `-` | Journal Entry Template |
| `title` | Title | Data | Optional | `-` | - |
| `custom_remark` | Custom Remark | Check | Optional | `0` | - |
| `remark` | Remark | Small Text | Optional | `-` | - |
| `mode_of_payment` | Mode of Payment | Link | Optional | `-` | Mode of Payment |
| `party_not_required` | Party Not Required | Check | Optional | `0` | - |

### DocType: `Payment Request`
- **Submittable**: Yes
- **Total Data Fields**: 43

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `payment_request_type` | Payment Request Type | Select | ✓ Mandatory | `Inward` | Outward, Inward |
| `transaction_date` | Transaction Date | Date | Optional | `-` | - |
| `failed_reason` | Reason for Failure | Data | Optional | `-` | - |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | ACC-PRQ-.YYYY.- |
| `company` | Company | Link | Optional | `-` | Company |
| `mode_of_payment` | Mode of Payment | Link | Optional | `-` | Mode of Payment |
| `party_type` | Party Type | Link | Optional | `-` | DocType |
| `party` | Party | Dynamic Link | Optional | `-` | party_type |
| `party_name` | Party Name | Data | Optional | `-` | - |
| `reference_doctype` | Reference Doctype | Link | Optional | `-` | DocType |
| `reference_name` | Reference Name | Dynamic Link | Optional | `-` | reference_doctype |
| `payment_reference` | Payment Reference | Table | Optional | `-` | Payment Reference |
| `grand_total` | Amount | Currency | ✓ Mandatory | `-` | currency |
| `currency` | Transaction Currency | Link | Optional | `-` | Currency |
| `is_a_subscription` | Is a Subscription | Check | Optional | `0` | - |
| `outstanding_amount` | Outstanding Amount | Currency | Optional | `-` | party_account_currency |
| `party_account_currency` | Party Account Currency | Link | Optional | `-` | Currency |
| `subscription_plans` | Subscription Plans | Table | Optional | `-` | Subscription Plan Detail |
| `bank_account` | Bank Account | Link | Optional | `-` | Bank Account |
| `bank` | Bank | Link | Optional | `-` | Bank |
| `bank_account_no` | Bank Account No | Read Only | Optional | `-` | - |
| `account` | Account | Read Only | Optional | `-` | - |
| `iban` | IBAN | Read Only | Optional | `-` | IBAN |
| `branch_code` | Branch Code | Read Only | Optional | `-` | - |
| `swift_number` | SWIFT Number | Read Only | Optional | `-` | - |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `print_format` | Print Format | Select | Optional | `-` | - |
| `email_to` | To | Data | Optional | `-` | - |
| `subject` | Subject | Data | Optional | `-` | - |
| `payment_gateway_account` | Payment Gateway Account | Link | Optional | `-` | Payment Gateway Account |
| `status` | Status | Select | Optional | `Draft` | Draft, Requested, Initiated, Partially Paid, Payment Ordered, Paid, Failed, C... |
| `make_sales_invoice` | Make Sales Invoice | Check | Optional | `0` | - |
| `message` | Message | Text | Optional | `-` | - |
| `message_examples` | Message Examples | HTML | Optional | `-` | <pre><h5>Message Example</h5>, &lt;p&gt;Dear {{ doc.contact_person }},&lt;/p&... |
| `mute_email` | Mute Email | Check | Optional | `0` | - |
| `payment_gateway` | Payment Gateway | Read Only | Optional | `-` | - |
| `payment_account` | Payment Account | Read Only | Optional | `-` | - |
| `payment_channel` | Payment Channel | Select | Optional | `-` | Email, Phone, Other |
| `payment_order` | Payment Order | Link | Optional | `-` | Payment Order |
| `amended_from` | Amended From | Link | Optional | `-` | Payment Request |
| `payment_url` | Payment URL | Data | Optional | `-` | URL |
| `phone_number` | Phone Number | Data | Optional | `-` | - |

### DocType: `Payment Order`
- **Submittable**: Yes
- **Total Data Fields**: 10

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `PMO-` | PMO- |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `payment_order_type` | Payment Order Type | Select | ✓ Mandatory | `-` | Payment Request, Payment Entry |
| `party` | Supplier | Link | Optional | `-` | Supplier |
| `posting_date` | Posting Date | Date | Optional | `Today` | - |
| `company_bank` | Bank | Link | Optional | `-` | Bank |
| `company_bank_account` | Company Bank Account | Link | ✓ Mandatory | `-` | Bank Account |
| `account` | Account | Data | Optional | `-` | - |
| `references` | Payment Order Reference | Table | ✓ Mandatory | `-` | Payment Order Reference |
| `amended_from` | Amended From | Link | Optional | `-` | Payment Order |

### DocType: `Payment Reconciliation`
- **Submittable**: No
- **Total Data Fields**: 23

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `party_type` | Party Type | Link | ✓ Mandatory | `-` | DocType |
| `party` | Party | Dynamic Link | ✓ Mandatory | `-` | party_type |
| `receivable_payable_account` | Receivable / Payable Account | Link | ✓ Mandatory | `-` | Account |
| `default_advance_account` | Default Advance Account | Link | Optional | `-` | Account |
| `from_invoice_date` | From Invoice Date | Date | Optional | `-` | - |
| `from_payment_date` | From Payment Date | Date | Optional | `-` | - |
| `minimum_invoice_amount` | Minimum Invoice Amount | Currency | Optional | `-` | - |
| `minimum_payment_amount` | Minimum Payment Amount | Currency | Optional | `-` | - |
| `to_invoice_date` | To Invoice Date | Date | Optional | `-` | - |
| `to_payment_date` | To Payment Date | Date | Optional | `-` | - |
| `maximum_invoice_amount` | Maximum Invoice Amount | Currency | Optional | `-` | - |
| `maximum_payment_amount` | Maximum Payment Amount | Currency | Optional | `-` | - |
| `invoice_limit` | Invoice Limit | Int | Optional | `50` | - |
| `payment_limit` | Payment Limit | Int | Optional | `50` | - |
| `bank_cash_account` | Bank / Cash Account | Link | Optional | `-` | Account |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `invoice_name` | Filter on Invoice | Data | Optional | `-` | - |
| `invoices` | Invoices | Table | Optional | `-` | Payment Reconciliation Invoice |
| `payment_name` | Filter on Payment | Data | Optional | `-` | - |
| `payments` | Payments | Table | Optional | `-` | Payment Reconciliation Payment |
| `allocation` | Allocation | Table | Optional | `-` | Payment Reconciliation Allocation |

### DocType: `Account`
- **Submittable**: No
- **Total Data Fields**: 18

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `disabled` | Disable | Check | Optional | `0` | - |
| `account_name` | Account Name | Data | ✓ Mandatory | `-` | - |
| `account_number` | Account Number | Data | Optional | `-` | - |
| `is_group` | Is Group | Check | Optional | `0` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `root_type` | Root Type | Select | Optional | `-` | Asset, Liability, Income, Expense, Equity |
| `report_type` | Report Type | Select | Optional | `-` | Balance Sheet, Profit and Loss |
| `account_currency` | Currency | Link | Optional | `-` | Currency |
| `parent_account` | Parent Account | Link | ✓ Mandatory | `-` | Account |
| `account_category` | Account Category | Link | Optional | `-` | Account Category |
| `account_type` | Account Type | Select | Optional | `-` | Accumulated Depreciation, Asset Received But Not Billed, Bank, Cash, Chargeab... |
| `tax_rate` | Tax Rate | Float | Optional | `-` | - |
| `freeze_account` | Frozen | Select | Optional | `-` | No, Yes |
| `balance_must_be` | Balance must be | Select | Optional | `-` | Debit, Credit |
| `lft` | Lft | Int | Optional | `-` | - |
| `rgt` | Rgt | Int | Optional | `-` | - |
| `old_parent` | Old Parent | Data | Optional | `-` | - |
| `include_in_gross` | Include in gross | Check | Optional | `0` | - |

### DocType: `Cost Center`
- **Submittable**: No
- **Total Data Fields**: 9

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `cost_center_name` | Cost Center Name | Data | ✓ Mandatory | `-` | - |
| `cost_center_number` | Cost Center Number | Data | Optional | `-` | - |
| `parent_cost_center` | Parent Cost Center | Link | ✓ Mandatory | `-` | Cost Center |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `is_group` | Is Group | Check | Optional | `0` | - |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `lft` | lft | Int | Optional | `-` | - |
| `rgt` | rgt | Int | Optional | `-` | - |
| `old_parent` | old_parent | Link | Optional | `-` | Cost Center |

### DocType: `Fiscal Year`
- **Submittable**: No
- **Total Data Fields**: 7

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `year` | Year Name | Data | ✓ Mandatory | `-` | - |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `is_short_year` | Is Short/Long Year | Check | Optional | `0` | - |
| `year_start_date` | Year Start Date | Date | ✓ Mandatory | `-` | - |
| `year_end_date` | Year End Date | Date | ✓ Mandatory | `-` | - |
| `companies` | Companies | Table | Optional | `-` | Fiscal Year Company |
| `auto_created` | Auto Created | Check | Optional | `0` | - |

### DocType: `Currency`
- **Submittable**: No
- **Total Data Fields**: 8

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `currency_name` | Currency Name | Data | ✓ Mandatory | `-` | - |
| `enabled` | Enabled | Check | Optional | `0` | - |
| `fraction` | Fraction | Data | Optional | `-` | - |
| `fraction_units` | Fraction Units | Int | Optional | `-` | - |
| `smallest_currency_fraction_value` | Smallest Currency Fraction Value | Currency | Optional | `-` | - |
| `symbol` | Symbol | Data | Optional | `-` | - |
| `symbol_on_right` | Show Currency Symbol on Right Side | Check | Optional | `0` | - |
| `number_format` | Number Format | Select | Optional | `-` | #,###.##, #.###,##, # ###.##, # ###,##, #'###.##, #, ###.##, #,##,###.##, #,#... |

### DocType: `Sales Taxes and Charges Template`
- **Submittable**: No
- **Total Data Fields**: 6

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `title` | Title | Data | ✓ Mandatory | `-` | - |
| `is_default` | Default | Check | Optional | `0` | - |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes` | Sales Taxes and Charges | Table | Optional | `-` | Sales Taxes and Charges |

### DocType: `Purchase Taxes and Charges Template`
- **Submittable**: No
- **Total Data Fields**: 6

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `title` | Title | Data | ✓ Mandatory | `-` | - |
| `is_default` | Default | Check | Optional | `0` | - |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes` | Purchase Taxes and Charges | Table | Optional | `-` | Purchase Taxes and Charges |

### DocType: `Tax Rule`
- **Submittable**: No
- **Total Data Fields**: 25

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `tax_type` | Tax Type | Select | Optional | `Sales` | Sales, Purchase |
| `use_for_shopping_cart` | Use for Shopping Cart | Check | Optional | `1` | - |
| `sales_tax_template` | Sales Tax Template | Link | Optional | `-` | Sales Taxes and Charges Template |
| `purchase_tax_template` | Purchase Tax Template | Link | Optional | `-` | Purchase Taxes and Charges Template |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `supplier` | Supplier | Link | Optional | `-` | Supplier |
| `item` | Item | Link | Optional | `-` | Item |
| `billing_city` | Billing City | Data | Optional | `-` | - |
| `billing_county` | Billing County | Data | Optional | `-` | - |
| `billing_state` | Billing State | Data | Optional | `-` | - |
| `billing_zipcode` | Billing Zipcode | Data | Optional | `-` | - |
| `billing_country` | Billing Country | Link | Optional | `-` | Country |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `customer_group` | Customer Group | Link | Optional | `-` | Customer Group |
| `supplier_group` | Supplier Group | Link | Optional | `-` | Supplier Group |
| `item_group` | Item Group | Link | Optional | `-` | Item Group |
| `shipping_city` | Shipping City | Data | Optional | `-` | - |
| `shipping_county` | Shipping County | Data | Optional | `-` | - |
| `shipping_state` | Shipping State | Data | Optional | `-` | - |
| `shipping_zipcode` | Shipping Zipcode | Data | Optional | `-` | - |
| `shipping_country` | Shipping Country | Link | Optional | `-` | Country |
| `from_date` | From Date | Date | Optional | `-` | - |
| `to_date` | To Date | Date | Optional | `-` | - |
| `priority` | Priority | Int | Optional | `1` | - |
| `company` | Company | Link | Optional | `-` | Company |

### DocType: `Tax Withholding Category`
- **Submittable**: No
- **Total Data Fields**: 8

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `category_name` | Category Name | Data | Optional | `-` | - |
| `tax_deduction_basis` | Deduct Tax On Basis | Select | ✓ Mandatory | `Net Total` | Gross Total, Net Total |
| `round_off_tax_amount` | Round Off Tax Amount | Check | Optional | `0` | - |
| `tax_on_excess_amount` | Only Deduct Tax On Excess Amount  | Check | Optional | `0` | - |
| `disable_cumulative_threshold` | Disable Cumulative Threshold | Check | Optional | `0` | - |
| `disable_transaction_threshold` | Disable Transaction Threshold | Check | Optional | `0` | - |
| `rates` | Rates | Table | ✓ Mandatory | `-` | Tax Withholding Rate |
| `accounts` | Accounts | Table | ✓ Mandatory | `-` | Tax Withholding Account |

### DocType: `Bank`
- **Submittable**: No
- **Total Data Fields**: 7

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `bank_name` | Bank Name | Data | ✓ Mandatory | `-` | - |
| `swift_number` | SWIFT number | Data | Optional | `-` | - |
| `website` | Website | Data | Optional | `-` | - |
| `address_html` | Address HTML | HTML | Optional | `-` | - |
| `contact_html` | Contact HTML | HTML | Optional | `-` | - |
| `bank_transaction_mapping` | Bank Transaction Mapping | Table | Optional | `-` | Bank Transaction Mapping |
| `plaid_access_token` | Plaid Access Token | Data | Optional | `-` | - |

### DocType: `Bank Account`
- **Submittable**: No
- **Total Data Fields**: 21

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `account_name` | Account Name | Data | ✓ Mandatory | `-` | - |
| `account` | Company Account | Link | Optional | `-` | Account |
| `bank` | Bank | Link | ✓ Mandatory | `-` | Bank |
| `account_type` | Account Type | Link | Optional | `-` | Bank Account Type |
| `account_subtype` | Account Subtype | Link | Optional | `-` | Bank Account Subtype |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `is_default` | Is Default Account | Check | Optional | `0` | - |
| `is_company_account` | Is Company Account | Check | Optional | `0` | - |
| `company` | Company | Link | Optional | `-` | Company |
| `is_credit_card` | Is Credit Card | Check | Optional | `0` | - |
| `party_type` | Party Type | Link | Optional | `-` | DocType |
| `party` | Party | Dynamic Link | Optional | `-` | party_type |
| `iban` | IBAN | Data | Optional | `-` | IBAN |
| `branch_code` | Branch Code | Data | Optional | `-` | - |
| `bank_account_no` | Bank Account No | Data | Optional | `-` | - |
| `statement_password` | Statement PDF Password | Password | Optional | `-` | - |
| `address_html` | Address HTML | HTML | Optional | `-` | - |
| `contact_html` | Contact HTML | HTML | Optional | `-` | - |
| `integration_id` | Integration ID | Data | Optional | `-` | - |
| `last_integration_date` | Last Integration Date | Date | Optional | `-` | - |
| `mask` | Mask | Data | Optional | `-` | - |

### DocType: `Bank Clearance`
- **Submittable**: No
- **Total Data Fields**: 8

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `account` | Account | Link | ✓ Mandatory | `-` | Account |
| `account_currency` | Account Currency | Link | Optional | `-` | Currency |
| `from_date` | From Date | Date | ✓ Mandatory | `-` | - |
| `to_date` | To Date | Date | ✓ Mandatory | `-` | - |
| `bank_account` | Bank Account | Link | Optional | `-` | Bank Account |
| `include_reconciled_entries` | Include Reconciled Entries | Check | Optional | `0` | - |
| `include_pos_transactions` | Include POS Transactions | Check | Optional | `0` | - |
| `payment_entries` | Payment Entries | Table | Optional | `-` | Bank Clearance Detail |

### DocType: `Bank Transaction`
- **Submittable**: Yes
- **Total Data Fields**: 25

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `ACC-BTN-.YYYY.-` | ACC-BTN-.YYYY.- |
| `date` | Date | Date | Optional | `-` | - |
| `is_rule_evaluated` | Is Rule Evaluated | Check | Optional | `0` | - |
| `matched_transaction_rule` | Matched Transaction Rule | Link | Optional | `-` | Bank Transaction Rule |
| `status` | Status | Select | Optional | `Pending` | Pending, Settled, Unreconciled, Reconciled, Cancelled |
| `bank_account` | Bank Account | Link | Optional | `-` | Bank Account |
| `company` | Company | Link | Optional | `-` | Company |
| `amended_from` | Amended From | Link | Optional | `-` | Bank Transaction |
| `deposit` | Deposit | Currency | Optional | `-` | currency |
| `withdrawal` | Withdrawal | Currency | Optional | `-` | currency |
| `currency` | Currency | Link | Optional | `-` | Currency |
| `description` | Description | Small Text | Optional | `-` | - |
| `reference_number` | Reference Number | Small Text | Optional | `-` | - |
| `transaction_id` | Transaction ID | Data | Optional | `-` | - |
| `transaction_type` | Transaction Type | Data | Optional | `-` | - |
| `payment_entries` | Payment Entries | Table | Optional | `-` | Bank Transaction Payments |
| `allocated_amount` | Allocated Amount | Currency | Optional | `-` | currency |
| `unallocated_amount` | Unallocated Amount | Currency | Optional | `-` | currency |
| `party_type` | Party Type | Link | Optional | `-` | DocType |
| `party` | Party | Dynamic Link | Optional | `-` | party_type |
| `bank_party_name` | Party Name/Account Holder (Bank Statement) | Data | Optional | `-` | - |
| `bank_party_account_number` | Party Account No. (Bank Statement) | Data | Optional | `-` | - |
| `bank_party_iban` | Party IBAN (Bank Statement) | Data | Optional | `-` | IBAN |
| `included_fee` | Included Fee | Currency | Optional | `-` | currency |
| `excluded_fee` | Excluded Fee | Currency | Optional | `-` | currency |

### DocType: `Budget`
- **Submittable**: Yes
- **Total Data Fields**: 29

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `BUDGET-.########` | BUDGET-.######## |
| `budget_against` | Budget Against | Select | ✓ Mandatory | `Cost Center` | Cost Center, Project |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `account` | Account | Link | ✓ Mandatory | `-` | Account |
| `amended_from` | Amended From | Link | Optional | `-` | Budget |
| `from_fiscal_year` | From Fiscal Year | Link | ✓ Mandatory | `-` | Fiscal Year |
| `to_fiscal_year` | To Fiscal Year | Link | ✓ Mandatory | `-` | Fiscal Year |
| `budget_start_date` | Budget Start Date | Date | Optional | `-` | - |
| `budget_end_date` | Budget End Date | Date | Optional | `-` | - |
| `distribution_frequency` | Distribution Frequency | Select | ✓ Mandatory | `Monthly` | Monthly, Quarterly, Half-Yearly, Yearly |
| `budget_amount` | Budget Amount | Currency | ✓ Mandatory | `-` | - |
| `distribute_equally` | Distribute Equally | Check | Optional | `1` | - |
| `budget_distribution` | Budget Distribution | Table | Optional | `-` | Budget Distribution |
| `budget_distribution_total` | Budget Distribution Total | Currency | Optional | `-` | - |
| `applicable_on_material_request` | Applicable on Material Request | Check | Optional | `0` | - |
| `action_if_annual_budget_exceeded_on_mr` | Action if Annual Budget Exceeded on MR | Select | Optional | `Stop` | Stop, Warn, Ignore |
| `action_if_accumulated_monthly_budget_exceeded_on_mr` | Action if Accumulated Monthly Budget Exceeded on MR | Select | Optional | `Warn` | Stop, Warn, Ignore |
| `applicable_on_purchase_order` | Applicable on Purchase Order | Check | Optional | `0` | - |
| `action_if_annual_budget_exceeded_on_po` | Action if Annual Budget Exceeded on PO | Select | Optional | `Stop` | Stop, Warn, Ignore |
| `action_if_accumulated_monthly_budget_exceeded_on_po` | Action if Accumulated Monthly Budget Exceeded on PO | Select | Optional | `Warn` | Stop, Warn, Ignore |
| `applicable_on_booking_actual_expenses` | Applicable on booking actual expenses | Check | Optional | `0` | - |
| `action_if_annual_budget_exceeded` | Action if Annual Budget Exceeded on Actual | Select | Optional | `Stop` | Stop, Warn, Ignore |
| `action_if_accumulated_monthly_budget_exceeded` | Action if Accumulated Monthly Budget Exceeded on Actual | Select | Optional | `Warn` | Stop, Warn, Ignore |
| `applicable_on_cumulative_expense` | Applicable on Cumulative Expense | Check | Optional | `0` | - |
| `action_if_annual_exceeded_on_cumulative_expense` | Action if Anual Budget Exceeded on Cumulative Expense | Select | Optional | `-` | Stop, Warn, Ignore |
| `action_if_accumulated_monthly_exceeded_on_cumulative_expense` | Action if Accumulative Monthly Budget Exceeded on Cumulative Expense | Select | Optional | `-` | Stop, Warn, Ignore |
| `revision_of` | Revision Of | Data | Optional | `-` | - |

### DocType: `Monthly Distribution`
- **Submittable**: No
- **Total Data Fields**: 3

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `distribution_id` | Distribution Name | Data | ✓ Mandatory | `-` | - |
| `fiscal_year` | Fiscal Year | Link | Optional | `-` | Fiscal Year |
| `percentages` | Monthly Distribution Percentages | Table | Optional | `-` | Monthly Distribution Percentage |

### DocType: `Subscription Plan`
- **Submittable**: No
- **Total Data Fields**: 11

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `plan_name` | Plan Name | Data | ✓ Mandatory | `-` | - |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `item` | Item | Link | ✓ Mandatory | `-` | Item |
| `price_determination` | Subscription Price Based On | Select | ✓ Mandatory | `-` | Fixed Rate, Based On Price List, Monthly Rate |
| `cost` | Cost | Currency | Optional | `-` | currency |
| `price_list` | Price List | Link | Optional | `-` | Price List |
| `billing_interval` | Billing Interval | Select | ✓ Mandatory | `Day` | Day, Week, Month, Year |
| `billing_interval_count` | Billing Interval Count | Int | ✓ Mandatory | `1` | - |
| `product_price_id` | Product Price ID | Data | Optional | `-` | - |
| `payment_gateway` | Payment Gateway | Link | Optional | `-` | Payment Gateway Account |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |

### DocType: `Subscription`
- **Submittable**: No
- **Total Data Fields**: 25

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `party_type` | Party Type | Link | ✓ Mandatory | `-` | DocType |
| `party` | Party | Dynamic Link | ✓ Mandatory | `-` | party_type |
| `company` | Company | Link | Optional | `-` | Company |
| `status` | Status | Select | Optional | `-` | Trialing, Active, Grace Period, Cancelled, Unpaid, Completed |
| `start_date` | Subscription Start Date | Date | Optional | `-` | - |
| `end_date` | Subscription End Date | Date | Optional | `-` | - |
| `cancelation_date` | Cancelation Date | Date | Optional | `-` | - |
| `trial_period_start` | Trial Period Start Date | Date | Optional | `-` | - |
| `trial_period_end` | Trial Period End Date | Date | Optional | `-` | - |
| `follow_calendar_months` | Follow Calendar Months | Check | Optional | `0` | - |
| `generate_new_invoices_past_due_date` | Generate New Invoices Past Due Date | Check | Optional | `0` | - |
| `submit_invoice` | Submit Generated Invoices | Check | Optional | `1` | - |
| `current_invoice_start` | Current Invoice Start Date | Date | Optional | `-` | - |
| `current_invoice_end` | Current Invoice End Date | Date | Optional | `-` | - |
| `days_until_due` | Days Until Due | Int | Optional | `0` | - |
| `generate_invoice_at` | Generate Invoice At | Select | ✓ Mandatory | `End of the current subscription period` | End of the current subscription period, Beginning of the current subscription... |
| `number_of_days` | Number of Days | Int | Optional | `-` | - |
| `cancel_at_period_end` | Cancel At End Of Period | Check | Optional | `0` | - |
| `plans` | Plans | Table | ✓ Mandatory | `-` | Subscription Plan Detail |
| `sales_tax_template` | Sales Taxes and Charges Template | Link | Optional | `-` | Sales Taxes and Charges Template |
| `purchase_tax_template` | Purchase Taxes and Charges Template | Link | Optional | `-` | Purchase Taxes and Charges Template |
| `apply_additional_discount` | Apply Additional Discount On | Select | Optional | `-` | Grand Total, Net Total |
| `additional_discount_percentage` | Additional Discount Percentage | Percent | Optional | `-` | - |
| `additional_discount_amount` | Additional Discount Amount | Currency | Optional | `-` | - |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |

### DocType: `Shareholder`
- **Submittable**: No
- **Total Data Fields**: 9

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `title` | Title | Data | ✓ Mandatory | `-` | - |
| `naming_series` | naming_series | Select | Optional | `-` | ACC-SH-.YYYY.- |
| `folio_no` | Folio no. | Data | Optional | `-` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `is_company` | Is Company | Check | Optional | `0` | - |
| `address_html` | Address HTML | HTML | Optional | `-` | - |
| `contact_html` | Contact HTML | HTML | Optional | `-` | - |
| `share_balance` | Share Balance | Table | Optional | `-` | Share Balance |
| `contact_list` | Contact List | Code | Optional | `-` | - |

### DocType: `Share Transfer`
- **Submittable**: Yes
- **Total Data Fields**: 17

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `transfer_type` | Transfer Type | Select | ✓ Mandatory | `-` | Issue, Purchase, Transfer |
| `date` | Date | Date | ✓ Mandatory | `-` | - |
| `from_shareholder` | From Shareholder | Link | Optional | `-` | Shareholder |
| `from_folio_no` | From Folio No | Data | Optional | `-` | - |
| `to_shareholder` | To Shareholder | Link | Optional | `-` | Shareholder |
| `to_folio_no` | To Folio No | Data | Optional | `-` | - |
| `equity_or_liability_account` | Equity/Liability Account | Link | ✓ Mandatory | `-` | Account |
| `asset_account` | Asset Account | Link | Optional | `-` | Account |
| `share_type` | Share Type | Link | ✓ Mandatory | `-` | Share Type |
| `from_no` | From No | Int | ✓ Mandatory | `-` | - |
| `rate` | Rate | Currency | ✓ Mandatory | `-` | Company:company:default_currency |
| `no_of_shares` | No of Shares | Int | ✓ Mandatory | `-` | - |
| `to_no` | To No | Int | ✓ Mandatory | `-` | - |
| `amount` | Amount | Currency | Optional | `-` | Company:company:default_currency |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `remarks` | Remarks | Long Text | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Share Transfer |

## Module: Stock
*Physical inventory movements via Stock Entry (Material Transfer for Manufacture, Manufacture), Purchase Receipts, Delivery Notes, Bins, and strict non-negative stock governance.*

### Summary of DocTypes in Stock:
- **Stock Entry**: 60 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Purchase Receipt**: 99 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Delivery Note**: 110 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Pick List**: 22 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Stock Reconciliation**: 15 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Landed Cost Voucher**: 13 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Repost Item Valuation**: 25 fields | Submittable: Yes (Draft -> Submitted -> Cancelled)
- **Item**: 82 fields | Submittable: No
- **Warehouse**: 23 fields | Submittable: No
- **Stock Settings**: 53 fields | Submittable: No

### DocType: `Stock Entry`
- **Submittable**: Yes
- **Total Data Fields**: 60

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | MAT-STE-.YYYY.- |
| `stock_entry_type` | Stock Entry Type | Link | ✓ Mandatory | `-` | Stock Entry Type |
| `purpose` | Purpose | Select | Optional | `-` | Material Issue, Material Receipt, Material Transfer, Material Transfer for Ma... |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `posting_date` | Posting Date | Date | Optional | `Today` | - |
| `posting_time` | Posting Time | Time | Optional | `Now` | - |
| `add_to_transit` | Add to Transit | Check | Optional | `0` | - |
| `apply_putaway_rule` | Apply Putaway Rule | Check | Optional | `0` | - |
| `inspection_required` | Inspection Required | Check | Optional | `0` | - |
| `work_order` | Work Order | Link | Optional | `-` | Work Order |
| `subcontracting_order` | Subcontracting Order | Link | Optional | `-` | Subcontracting Order |
| `outgoing_stock_entry` | Stock Entry (Outward GIT) | Link | Optional | `-` | Stock Entry |
| `source_stock_entry` | Source Stock Entry (Manufacture) | Link | Optional | `-` | Stock Entry |
| `from_bom` | From BOM | Check | Optional | `0` | - |
| `use_multi_level_bom` | Use Multi-Level BOM | Check | Optional | `1` | - |
| `bom_no` | BOM No | Link | Optional | `-` | BOM |
| `fg_completed_qty` | Finished Good Quantity  | Float | Optional | `-` | - |
| `get_items` | Get Items | Button | Optional | `-` | - |
| `process_loss_percentage` | % Process Loss | Percent | Optional | `-` | - |
| `process_loss_qty` | Process Loss Qty | Float | Optional | `-` | - |
| `from_warehouse` | Default Source Warehouse | Link | Optional | `-` | Warehouse |
| `source_warehouse_address` | Source Warehouse Address Link | Link | Optional | `-` | Address |
| `source_address_display` | Source Warehouse Address | Text Editor | Optional | `-` | - |
| `to_warehouse` | Default Target Warehouse | Link | Optional | `-` | Warehouse |
| `target_warehouse_address` | Target Warehouse Address Link | Link | Optional | `-` | Address |
| `target_address_display` | Target Warehouse Address | Text Editor | Optional | `-` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `items` | Items | Table | ✓ Mandatory | `-` | Stock Entry Detail |
| `get_stock_and_rate` | Update Rate and Availability | Button | Optional | `-` | get_stock_and_rate |
| `total_outgoing_value` | Total Outgoing Value (Consumption) | Currency | Optional | `-` | Company:company:default_currency |
| `total_incoming_value` | Total Incoming Value (Receipt) | Currency | Optional | `-` | Company:company:default_currency |
| `value_difference` | Total Value Difference (Incoming - Outgoing) | Currency | Optional | `-` | Company:company:default_currency |
| `additional_costs` | Additional Costs | Table | Optional | `-` | Landed Cost Taxes and Charges |
| `total_additional_costs` | Total Additional Costs | Currency | Optional | `-` | Company:company:default_currency |
| `supplier` | Supplier | Link | Optional | `-` | Supplier |
| `supplier_name` | Supplier Name | Data | Optional | `-` | - |
| `supplier_address` | Supplier Address | Link | Optional | `-` | Address |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `project` | Project | Link | Optional | `-` | Project |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `delivery_note_no` | Delivery Note No | Link | Optional | `-` | Delivery Note |
| `sales_invoice_no` | Sales Invoice No | Link | Optional | `-` | Sales Invoice |
| `job_card` | Job Card | Link | Optional | `-` | Job Card |
| `pick_list` | Pick List | Link | Optional | `-` | Pick List |
| `asset_repair` | Asset Repair | Link | Optional | `-` | Asset Repair |
| `purchase_receipt_no` | Purchase Receipt No | Link | Optional | `-` | Purchase Receipt |
| `purchase_order` | Purchase Order | Link | Optional | `-` | Purchase Order |
| `subcontracting_inward_order` | Subcontracting Inward Order | Link | Optional | `-` | Subcontracting Inward Order |
| `is_additional_transfer_entry` | Is Additional Transfer Entry | Check | Optional | `0` | - |
| `is_opening` | Is Opening | Select | Optional | `-` | No, Yes |
| `remarks` | Remarks | Text | Optional | `-` | - |
| `per_transferred` | Per Transferred | Percent | Optional | `-` | - |
| `total_amount` | Total Amount | Currency | Optional | `-` | Company:company:default_currency |
| `amended_from` | Amended From | Link | Optional | `-` | Stock Entry |
| `credit_note` | Credit Note | Link | Optional | `-` | Journal Entry |
| `is_return` | Is Return | Check | Optional | `0` | - |

### DocType: `Purchase Receipt`
- **Submittable**: Yes
- **Total Data Fields**: 99

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | MAT-PRE-.YYYY.-, MAT-PR-RET-.YYYY.- |
| `supplier` | Supplier | Link | ✓ Mandatory | `-` | Supplier |
| `supplier_name` | Supplier Name | Data | Optional | `-` | - |
| `supplier_delivery_note` | Supplier Delivery Note | Data | Optional | `-` | - |
| `subcontracting_receipt` | Subcontracting Receipt | Link | Optional | `-` | Subcontracting Receipt |
| `posting_date` | Date | Date | ✓ Mandatory | `Today` | - |
| `posting_time` | Posting Time | Time | ✓ Mandatory | `Now` | - |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `apply_putaway_rule` | Apply Putaway Rule | Check | Optional | `0` | - |
| `is_return` | Is Return | Check | Optional | `0` | - |
| `return_against` | Return Against Purchase Receipt | Link | Optional | `-` | Purchase Receipt |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `conversion_rate` | Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `buying_price_list` | Price List | Link | Optional | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | Optional | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | Optional | `-` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `set_warehouse` | Accepted Warehouse | Link | Optional | `-` | Warehouse |
| `set_from_warehouse` | Set From Warehouse | Link | Optional | `-` | Warehouse |
| `rejected_warehouse` | Rejected Warehouse | Link | Optional | `-` | Warehouse |
| `is_subcontracted` | Is Subcontracted | Check | Optional | `0` | - |
| `supplier_warehouse` | Supplier Warehouse | Link | Optional | `-` | Warehouse |
| `items` | Items | Table | ✓ Mandatory | `-` | Purchase Receipt Item |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total_net_weight` | Total Net Weight | Float | Optional | `-` | - |
| `base_total` | Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_net_total` | Net Total (Company Currency) | Currency | ✓ Mandatory | `-` | Company:company:default_currency |
| `total` | Total | Currency | Optional | `-` | currency |
| `net_total` | Net Total | Currency | Optional | `-` | currency |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes_and_charges` | Purchase Taxes and Charges Template | Link | Optional | `-` | Purchase Taxes and Charges Template |
| `shipping_rule` | Shipping Rule | Link | Optional | `-` | Shipping Rule |
| `incoterm` | Incoterm | Link | Optional | `-` | Incoterm |
| `named_place` | Named Place | Data | Optional | `-` | - |
| `taxes` | Purchase Taxes and Charges | Table | Optional | `-` | Purchase Taxes and Charges |
| `base_taxes_and_charges_added` | Taxes and Charges Added (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_taxes_and_charges_deducted` | Taxes and Charges Deducted (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `taxes_and_charges_added` | Taxes and Charges Added | Currency | Optional | `-` | currency |
| `taxes_and_charges_deducted` | Taxes and Charges Deducted | Currency | Optional | `-` | currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | currency |
| `grand_total` | Grand Total | Currency | Optional | `-` | currency |
| `in_words` | In Words | Data | Optional | `-` | - |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | currency |
| `rounded_total` | Rounded Total | Currency | Optional | `-` | currency |
| `base_grand_total` | Grand Total | Currency | Optional | `-` | Company:company:default_currency |
| `base_in_words` | In Words | Data | Optional | `-` | - |
| `base_rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounded_total` | Rounded Total | Currency | Optional | `-` | Company:company:default_currency |
| `apply_discount_on` | Apply Additional Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `base_discount_amount` | Additional Discount Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `additional_discount_percentage` | Additional Discount Percentage | Float | Optional | `-` | - |
| `discount_amount` | Additional Discount Amount | Currency | Optional | `-` | currency |
| `other_charges_calculation` | Taxes and Charges Calculation | Text Editor | Optional | `-` | - |
| `item_wise_tax_details` | Item Wise Tax Details | Table | Optional | `-` | Item Wise Tax Detail |
| `pricing_rules` | Pricing Rule Detail | Table | Optional | `-` | Pricing Rule Detail |
| `get_current_stock` | Get Current Stock | Button | Optional | `-` | get_current_stock |
| `supplied_items` | Consumed Items | Table | Optional | `-` | Purchase Receipt Item Supplied |
| `supplier_address` | Supplier Address | Link | Optional | `-` | Address |
| `address_display` | Address | Text Editor | Optional | `-` | - |
| `contact_person` | Contact Person | Link | Optional | `-` | Contact |
| `contact_display` | Contact | Small Text | Optional | `-` | - |
| `contact_mobile` | Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Small Text | Optional | `-` | Email |
| `dispatch_address` | Dispatch Address Template | Link | Optional | `-` | Address |
| `dispatch_address_display` | Dispatch Address | Text Editor | Optional | `-` | - |
| `shipping_address` | Shipping Address Template | Link | Optional | `-` | Address |
| `shipping_address_display` | Shipping Address | Text Editor | Optional | `-` | - |
| `billing_address` | Billing Address | Link | Optional | `-` | Address |
| `billing_address_display` | Billing Address | Text Editor | Optional | `-` | - |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions | Text Editor | Optional | `-` | - |
| `status` | Status | Select | ✓ Mandatory | `Draft` | Draft, Partly Billed, To Bill, Completed, Return, Return Issued, Cancelled, C... |
| `per_billed` | % Amount Billed | Percent | Optional | `-` | - |
| `per_returned` | % Returned | Percent | Optional | `-` | - |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `group_same_items` | Group same items | Check | Optional | `0` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `language` | Print Language | Data | Optional | `-` | - |
| `transporter_name` | Transporter Name | Data | Optional | `-` | - |
| `lr_no` | Vehicle Number | Data | Optional | `-` | - |
| `lr_date` | Vehicle Date | Date | Optional | `-` | - |
| `instructions` | Instructions | Small Text | Optional | `-` | - |
| `is_internal_supplier` | Is Internal Supplier | Check | Optional | `0` | - |
| `represents_company` | Represents Company | Link | Optional | `-` | Company |
| `title` | Title | Data | Optional | `-` | - |
| `inter_company_reference` | Inter Company Reference | Link | Optional | `-` | Delivery Note |
| `remarks` | Remarks | Small Text | Optional | `-` | - |
| `range` | Range | Data | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Purchase Receipt |
| `is_old_subcontracting_flow` | Is Old Subcontracting Flow | Check | Optional | `0` | - |
| `other_details` | Other Details | HTML | Optional | `-` | <div class="columnHeading">Other Details</div> |

### DocType: `Delivery Note`
- **Submittable**: Yes
- **Total Data Fields**: 110

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | MAT-DN-.YYYY.-, MAT-DN-RET-.YYYY.- |
| `customer` | Customer | Link | ✓ Mandatory | `-` | Customer |
| `tax_id` | Tax Id | Data | Optional | `-` | - |
| `customer_name` | Customer Name | Data | Optional | `-` | - |
| `posting_date` | Date | Date | ✓ Mandatory | `Today` | - |
| `posting_time` | Posting Time | Time | ✓ Mandatory | `Now` | - |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `amended_from` | Amended From | Link | Optional | `-` | Delivery Note |
| `is_return` | Is Return | Check | Optional | `0` | - |
| `issue_credit_note` | Issue Credit Note | Check | Optional | `0` | - |
| `return_against` | Return Against Delivery Note | Link | Optional | `-` | Delivery Note |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |
| `project` | Project | Link | Optional | `-` | Project |
| `currency` | Currency | Link | ✓ Mandatory | `-` | Currency |
| `conversion_rate` | Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `selling_price_list` | Price List | Link | ✓ Mandatory | `-` | Price List |
| `price_list_currency` | Price List Currency | Link | ✓ Mandatory | `-` | Currency |
| `plc_conversion_rate` | Price List Exchange Rate | Float | ✓ Mandatory | `-` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `set_warehouse` | Set Source Warehouse | Link | Optional | `-` | Warehouse |
| `set_target_warehouse` | Set Target Warehouse | Link | Optional | `-` | Warehouse |
| `items` | Delivery Note Item | Table | ✓ Mandatory | `-` | Delivery Note Item |
| `total_qty` | Total Quantity | Float | Optional | `-` | - |
| `total_net_weight` | Total Net Weight | Float | Optional | `-` | - |
| `base_total` | Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `base_net_total` | Net Total (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total` | Total | Currency | Optional | `-` | currency |
| `net_total` | Net Total | Currency | Optional | `-` | currency |
| `tax_category` | Tax Category | Link | Optional | `-` | Tax Category |
| `taxes_and_charges` | Sales Taxes and Charges Template | Link | Optional | `-` | Sales Taxes and Charges Template |
| `shipping_rule` | Shipping Rule | Link | Optional | `-` | Shipping Rule |
| `incoterm` | Incoterm | Link | Optional | `-` | Incoterm |
| `named_place` | Named Place | Data | Optional | `-` | - |
| `taxes` | Sales Taxes and Charges | Table | Optional | `-` | Sales Taxes and Charges |
| `base_total_taxes_and_charges` | Total Taxes and Charges (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total_taxes_and_charges` | Total Taxes and Charges | Currency | Optional | `-` | currency |
| `grand_total` | Grand Total | Currency | Optional | `-` | currency |
| `in_words` | In Words | Data | Optional | `-` | - |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | currency |
| `rounded_total` | Rounded Total | Currency | Optional | `-` | currency |
| `base_grand_total` | Grand Total | Currency | Optional | `-` | Company:company:default_currency |
| `base_in_words` | In Words | Data | Optional | `-` | - |
| `base_rounding_adjustment` | Rounding Adjustment | Currency | Optional | `-` | Company:company:default_currency |
| `base_rounded_total` | Rounded Total | Currency | Optional | `-` | Company:company:default_currency |
| `apply_discount_on` | Apply Additional Discount On | Select | Optional | `Grand Total` | Grand Total, Net Total |
| `base_discount_amount` | Additional Discount Amount (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `additional_discount_percentage` | Additional Discount Percentage | Float | Optional | `-` | - |
| `discount_amount` | Additional Discount Amount | Currency | Optional | `-` | currency |
| `other_charges_calculation` | Taxes and Charges Calculation | Text Editor | Optional | `-` | - |
| `item_wise_tax_details` | Item Wise Tax Details | Table | Optional | `-` | Item Wise Tax Detail |
| `packed_items` | Packed Items | Table | Optional | `-` | Packed Item |
| `product_bundle_help` | Product Bundle Help | HTML | Optional | `-` | - |
| `pricing_rules` | Pricing Rule Detail | Table | Optional | `-` | Pricing Rule Detail |
| `customer_address` | Billing Address Name | Link | Optional | `-` | Address |
| `address_display` | Billing Address | Text Editor | Optional | `-` | - |
| `contact_person` | Contact Person | Link | Optional | `-` | Contact |
| `contact_display` | Contact | Small Text | Optional | `-` | - |
| `contact_mobile` | Mobile No | Small Text | Optional | `-` | Phone |
| `contact_email` | Contact Email | Data | Optional | `-` | Email |
| `shipping_address_name` | Shipping Address | Link | Optional | `-` | Address |
| `shipping_address` | Shipping Address | Text Editor | Optional | `-` | - |
| `dispatch_address_name` | Dispatch Address Name | Link | Optional | `-` | Address |
| `dispatch_address` | Dispatch Address | Text Editor | Optional | `-` | - |
| `company_address` | Company Address Name | Link | Optional | `-` | Address |
| `company_address_display` | Company Address | Text Editor | Optional | `-` | - |
| `company_contact_person` | Company Contact Person | Link | Optional | `-` | Contact |
| `tc_name` | Terms | Link | Optional | `-` | Terms and Conditions |
| `terms` | Terms and Conditions Details | Text Editor | Optional | `-` | - |
| `per_billed` | % Amount Billed | Percent | Optional | `-` | - |
| `status` | Status | Select | ✓ Mandatory | `Draft` | Draft, To Bill, Partially Billed, Completed, Return, Return Issued, Cancelled... |
| `per_installed` | % Installed | Percent | Optional | `-` | - |
| `installation_status` | Installation Status | Select | Optional | `-` | - |
| `per_returned` | % Returned | Percent | Optional | `-` | - |
| `transporter` | Transporter | Link | Optional | `-` | Supplier |
| `lr_no` | Transport Receipt No | Data | Optional | `-` | - |
| `delivery_trip` | Delivery Trip | Link | Optional | `-` | Delivery Trip |
| `driver` | Driver | Link | Optional | `-` | Driver |
| `transporter_name` | Transporter Name | Data | Optional | `-` | - |
| `lr_date` | Transport Receipt Date | Date | Optional | `Today` | - |
| `vehicle_no` | Vehicle No | Data | Optional | `-` | - |
| `driver_name` | Driver Name | Data | Optional | `-` | - |
| `po_no` | Customer's Purchase Order No | Small Text | Optional | `-` | - |
| `po_date` | Customer's Purchase Order Date | Date | Optional | `-` | - |
| `sales_partner` | Sales Partner | Link | Optional | `-` | Sales Partner |
| `amount_eligible_for_commission` | Amount Eligible for Commission | Currency | Optional | `-` | Company:company:default_currency |
| `commission_rate` | Commission Rate (%) | Float | Optional | `-` | - |
| `total_commission` | Total Commission | Currency | Optional | `-` | Company:company:default_currency |
| `sales_team` | Sales Team | Table | Optional | `-` | Sales Team |
| `auto_repeat` | Auto Repeat | Link | Optional | `-` | Auto Repeat |
| `letter_head` | Letter Head | Link | Optional | `-` | Letter Head |
| `print_without_amount` | Print Without Amount | Check | Optional | `0` | - |
| `group_same_items` | Group same items | Check | Optional | `0` | - |
| `select_print_heading` | Print Heading | Link | Optional | `-` | Print Heading |
| `language` | Print Language | Link | Optional | `-` | Language |
| `utm_source` | Source | Link | Optional | `-` | UTM Source |
| `utm_medium` | Medium | Link | Optional | `-` | UTM Medium |
| `utm_campaign` | Campaign | Link | Optional | `-` | UTM Campaign |
| `utm_content` | Content | Data | Optional | `-` | - |
| `is_internal_customer` | Is Internal Customer | Check | Optional | `0` | - |
| `represents_company` | Represents Company | Link | Optional | `-` | Company |
| `inter_company_reference` | Inter Company Reference | Link | Optional | `-` | Purchase Receipt |
| `customer_group` | Customer Group | Link | Optional | `-` | Customer Group |
| `territory` | Territory | Link | Optional | `-` | Territory |
| `title` | Title | Data | Optional | `-` | - |
| `excise_page` | Excise Page Number | Data | Optional | `-` | - |
| `instructions` | Instructions | Text | Optional | `-` | - |

### DocType: `Pick List`
- **Submittable**: Yes
- **Total Data Fields**: 22

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `naming_series` | Series | Select | ✓ Mandatory | `-` | STO-PICK-.YYYY.- |
| `purpose` | Purpose | Select | Optional | `Material Transfer for Manufacture` | Material Transfer for Manufacture, Material Transfer, Delivery |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `for_qty` | Qty of Finished Goods Item | Float | Optional | `-` | - |
| `parent_warehouse` | Warehouse | Link | Optional | `-` | Warehouse |
| `consider_rejected_warehouses` | Consider Rejected Warehouses | Check | Optional | `0` | - |
| `get_item_locations` | Get Item Locations | Button | Optional | `-` | - |
| `pick_manually` | Pick Manually | Check | Optional | `0` | - |
| `ignore_pricing_rule` | Ignore Pricing Rule | Check | Optional | `0` | - |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `scan_mode` | Scan Mode | Check | Optional | `0` | - |
| `prompt_qty` | Prompt Qty | Check | Optional | `0` | - |
| `locations` | Item Locations | Table | Optional | `-` | Pick List Item |
| `group_same_items` | Group Same Items | Check | Optional | `0` | - |
| `per_delivered` | % Delivered | Percent | Optional | `-` | - |
| `delivery_status` | Delivery Status | Select | Optional | `-` | Not Delivered, Fully Delivered, Partly Delivered |
| `status` | Status | Select | ✓ Mandatory | `Draft` | Draft, Open, Partly Delivered, Partially Transferred, Completed, Cancelled |
| `work_order` | Work Order | Link | Optional | `-` | Work Order |
| `customer_name` | Customer Name | Data | Optional | `-` | - |
| `material_request` | Material Request | Link | Optional | `-` | Material Request |
| `amended_from` | Amended From | Link | Optional | `-` | Pick List |

### DocType: `Stock Reconciliation`
- **Submittable**: Yes
- **Total Data Fields**: 15

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | MAT-RECO-.YYYY.- |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `purpose` | Purpose | Select | ✓ Mandatory | `-` | Opening Stock, Stock Reconciliation |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `posting_time` | Posting Time | Time | ✓ Mandatory | `Now` | - |
| `set_posting_time` | Edit Posting Date and Time | Check | Optional | `0` | - |
| `set_warehouse` | Default Warehouse | Link | Optional | `-` | Warehouse |
| `scan_barcode` | Scan Barcode | Data | Optional | `-` | Barcode |
| `last_scanned_warehouse` | Last Scanned Warehouse | Data | Optional | `-` | - |
| `scan_mode` | Scan Mode | Check | Optional | `0` | - |
| `items` | Items | Table | ✓ Mandatory | `-` | Stock Reconciliation Item |
| `expense_account` | Difference Account | Link | Optional | `-` | Account |
| `difference_amount` | Difference Amount | Currency | Optional | `-` | Company:company:default_currency |
| `amended_from` | Amended From | Link | Optional | `-` | Stock Reconciliation |
| `cost_center` | Cost Center | Link | Optional | `-` | Cost Center |

### DocType: `Landed Cost Voucher`
- **Submittable**: Yes
- **Total Data Fields**: 13

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | ✓ Mandatory | `-` | MAT-LCV-.YYYY.- |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `Today` | - |
| `purchase_receipts` | Vouchers | Table | ✓ Mandatory | `-` | Landed Cost Purchase Receipt |
| `get_items_from_purchase_receipts` | Get Items | Button | Optional | `-` | - |
| `items` | Receipt Items | Table | ✓ Mandatory | `-` | Landed Cost Item |
| `vendor_invoices` | Vendor Invoices | Table | Optional | `-` | Landed Cost Vendor Invoice |
| `taxes` | Landed Cost | Table | ✓ Mandatory | `-` | Landed Cost Taxes and Charges |
| `total_vendor_invoices_cost` | Total Vendor Invoices Cost (Company Currency) | Currency | Optional | `-` | Company:company:default_currency |
| `total_taxes_and_charges` | Total Landed Cost (Company Currency) | Currency | ✓ Mandatory | `-` | Company:company:default_currency |
| `distribute_charges_based_on` | Distribute Charges Based On | Select | ✓ Mandatory | `-` | Qty, Amount, Distribute Manually |
| `amended_from` | Amended From | Link | Optional | `-` | Landed Cost Voucher |
| `landed_cost_help` | Landed Cost Help | HTML | Optional | `-` | - |

### DocType: `Repost Item Valuation`
- **Submittable**: Yes
- **Total Data Fields**: 25

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `based_on` | Based On | Select | ✓ Mandatory | `Transaction` | Transaction, Item and Warehouse |
| `voucher_type` | Voucher Type | Link | Optional | `-` | DocType |
| `voucher_no` | Voucher No | Dynamic Link | Optional | `-` | voucher_type |
| `item_code` | Item Code | Link | Optional | `-` | Item |
| `warehouse` | Warehouse | Link | Optional | `-` | Warehouse |
| `posting_date` | Posting Date | Date | ✓ Mandatory | `-` | - |
| `posting_time` | Posting Time | Time | Optional | `-` | - |
| `status` | Status | Select | Optional | `Queued` | Queued, In Progress, Completed, Skipped, Failed, Cancelled |
| `company` | Company | Link | Optional | `-` | Company |
| `reposting_reference` | Reposting Reference | Data | Optional | `-` | - |
| `repost_only_accounting_ledgers` | Repost Only Accounting Ledgers | Check | Optional | `0` | - |
| `allow_negative_stock` | Allow Negative Stock | Check | Optional | `1` | - |
| `via_landed_cost_voucher` | Via Landed Cost Voucher | Check | Optional | `0` | - |
| `allow_zero_rate` | Allow Zero Rate | Check | Optional | `0` | - |
| `recreate_stock_ledgers` | Recreate Stock Ledgers | Check | Optional | `0` | - |
| `recalculate_valuation_rate` | Recalculate Valuation Rate | Check | Optional | `0` | - |
| `error_log` | Error Log | Long Text | Optional | `-` | - |
| `items_to_be_repost` | Items to Be Repost | Code | Optional | `-` | - |
| `total_reposting_count` | No of Items to Repost | Int | Optional | `-` | - |
| `current_index` | Current Index | Int | Optional | `-` | - |
| `gl_reposting_index` | GL reposting index | Int | Optional | `0` | - |
| `reposting_data_file` | Reposting Data File | Attach | Optional | `-` | - |
| `amended_from` | Amended From | Link | Optional | `-` | Repost Item Valuation |
| `total_vouchers` | Total Ledgers | Int | Optional | `-` | - |
| `vouchers_posted` | Ledgers Posted | Int | Optional | `-` | - |

### DocType: `Item`
- **Submittable**: No
- **Total Data Fields**: 82

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `naming_series` | Series | Select | Optional | `-` | STO-ITEM-.YYYY.- |
| `item_code` | Item Code | Data | ✓ Mandatory | `-` | - |
| `item_name` | Item Name | Data | Optional | `-` | - |
| `item_group` | Item Group | Link | ✓ Mandatory | `-` | Item Group |
| `stock_uom` | Default Unit of Measure | Link | ✓ Mandatory | `-` | UOM |
| `image` | Image | Attach Image | Optional | `-` | image |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `is_stock_item` | Maintain Stock | Check | Optional | `1` | - |
| `is_fixed_asset` | Is Fixed Asset | Check | Optional | `0` | - |
| `auto_create_assets` | Auto create assets on purchase | Check | Optional | `0` | - |
| `is_grouped_asset` | Create Grouped Asset | Check | Optional | `0` | - |
| `asset_category` | Asset Category | Link | Optional | `-` | Asset Category |
| `asset_naming_series` | Asset Naming Series | Select | Optional | `-` | - |
| `is_sales_item` | Allow Sales | Check | Optional | `1` | - |
| `allow_alternative_item` | Allow Alternative Item | Check | Optional | `0` | - |
| `has_variants` | Has Variants | Check | Optional | `0` | - |
| `is_purchase_item` | Allow Purchase | Check | Optional | `1` | - |
| `is_customer_provided_item` | Is Customer Provided Item | Check | Optional | `0` | - |
| `standard_rate` | Standard Selling Rate | Currency | Optional | `-` | - |
| `opening_stock` | Opening Stock | Float | Optional | `-` | - |
| `over_delivery_receipt_allowance` | Over Delivery/Receipt Allowance (%) | Float | Optional | `-` | - |
| `over_billing_allowance` | Over Billing Allowance (%) | Float | Optional | `-` | - |
| `brand` | Brand | Link | Optional | `-` | Brand |
| `description` | Description | Text Editor | Optional | `-` | - |
| `item_defaults` | Item Defaults | Table | Optional | `-` | Item Default |
| `enable_deferred_expense` | Enable Deferred Expense | Check | Optional | `0` | - |
| `no_of_months_exp` | No of Months (Expense) | Int | Optional | `-` | - |
| `enable_deferred_revenue` | Enable Deferred Revenue | Check | Optional | `0` | - |
| `no_of_months` | No of Months (Revenue) | Int | Optional | `-` | - |
| `uom_help_html` | uom_help_html | HTML | Optional | `-` | <div style="margin-bottom:10px; color: var(--gray-500) !important;">Define al... |
| `uoms` | uoms | Table | Optional | `-` | UOM Conversion Detail |
| `taxes` | Taxes | Table | Optional | `-` | Item Tax |
| `purchase_tax_withholding_category` | Purchase Tax Withholding Category | Link | Optional | `-` | Tax Withholding Category |
| `sales_tax_withholding_category` | Sales Tax Withholding Category | Link | Optional | `-` | Tax Withholding Category |
| `stock_levels_html` | Stock Levels HTML | HTML | Optional | `-` | <div id="stock-levels-placeholder"></div> |
| `valuation_method` | Valuation Method | Select | Optional | `-` | FIFO, Moving Average, LIFO |
| `valuation_rate` | Valuation Rate | Currency | Optional | `-` | - |
| `end_of_life` | End of Life | Date | Optional | `2099-12-31` | - |
| `default_material_request_type` | Default Material Request Type | Select | Optional | `Purchase` | Purchase, Material Transfer, Material Issue, Manufacture, Customer Provided |
| `warranty_period` | Warranty Period (in days) | Data | Optional | `-` | - |
| `weight_per_unit` | Weight Per Unit | Float | Optional | `-` | - |
| `weight_uom` | Weight UOM | Link | Optional | `-` | UOM |
| `allow_negative_stock` | Allow Negative Stock | Check | Optional | `0` | - |
| `barcodes` | Barcodes | Table | Optional | `-` | Item Barcode |
| `reorder_levels` | Reorder level based on Warehouse | Table | Optional | `-` | Item Reorder |
| `has_batch_no` | Has Batch No | Check | Optional | `0` | - |
| `create_new_batch` | Automatically Create New Batch | Check | Optional | `0` | - |
| `batch_number_series` | Batch Number Series | Data | Optional | `-` | - |
| `has_expiry_date` | Has Expiry Date | Check | Optional | `0` | - |
| `shelf_life_in_days` | Shelf Life In Days | Int | Optional | `-` | - |
| `retain_sample` | Retain Sample | Check | Optional | `0` | - |
| `sample_quantity` | Max Sample Quantity | Int | Optional | `-` | - |
| `has_serial_no` | Has Serial No | Check | Optional | `0` | - |
| `serial_no_series` | Serial Number Series | Data | Optional | `-` | - |
| `variant_of` | Variant Of | Link | Optional | `-` | Item |
| `variant_based_on` | Variant Based On | Select | Optional | `Item Attribute` | Item Attribute, Manufacturer |
| `attributes` | Variant Attributes | Table | Optional | `-` | Item Variant Attribute |
| `purchase_uom` | Default Purchase Unit of Measure | Link | Optional | `-` | UOM |
| `min_order_qty` | Minimum Order Qty | Float | Optional | `0.00` | - |
| `safety_stock` | Safety Stock | Float | Optional | `-` | - |
| `lead_time_days` | Lead Time in days | Int | Optional | `-` | - |
| `last_purchase_rate` | Last Purchase Rate | Float | Optional | `-` | - |
| `delivered_by_supplier` | Delivered by Supplier (Drop Ship) | Check | Optional | `0` | - |
| `supplier_items` | Item Supplier | Table | Optional | `-` | Item Supplier |
| `country_of_origin` | Country of Origin | Link | Optional | `-` | Country |
| `customs_tariff_number` | Customs Tariff Number | Link | Optional | `-` | Customs Tariff Number |
| `sales_uom` | Default Sales Unit of Measure | Link | Optional | `-` | UOM |
| `grant_commission` | Grant Commission | Check | Optional | `1` | - |
| `max_discount` | Max Discount (%) | Float | Optional | `-` | - |
| `customer_items` | Customer Items | Table | Optional | `-` | Item Customer Detail |
| `include_item_in_manufacturing` | Include Item In Manufacturing | Check | Optional | `1` | - |
| `is_sub_contracted_item` | Is Subcontracted Item | Check | Optional | `0` | - |
| `default_bom` | Default BOM | Link | Optional | `-` | BOM |
| `production_capacity` | Production Capacity | Int | Optional | `-` | - |
| `total_projected_qty` | Total Projected Qty | Float | Optional | `-` | - |
| `default_manufacturer_part_no` | Default Manufacturer Part No | Data | Optional | `-` | - |
| `default_item_manufacturer` | Default Item Manufacturer | Link | Optional | `-` | Manufacturer |
| `customer_code` | Customer Code | Small Text | Optional | `-` | - |
| `inspection_required_before_purchase` | Inspection Required before Purchase | Check | Optional | `0` | - |
| `inspection_required_before_delivery` | Inspection Required before Delivery | Check | Optional | `0` | - |
| `quality_inspection_template` | Quality Inspection Template | Link | Optional | `-` | Quality Inspection Template |
| `prices_html` | Prices HTML | HTML | Optional | `-` | <div id=\"item-prices-container\"></div> |

### DocType: `Warehouse`
- **Submittable**: No
- **Total Data Fields**: 23

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `disabled` | Disabled | Check | Optional | `0` | - |
| `warehouse_name` | Warehouse Name | Data | ✓ Mandatory | `-` | - |
| `company` | Company | Link | ✓ Mandatory | `-` | Company |
| `is_rejected_warehouse` | Is Rejected Warehouse | Check | Optional | `0` | - |
| `account` | Account | Link | Optional | `-` | Account |
| `parent_warehouse` | Parent Warehouse | Link | Optional | `-` | Warehouse |
| `is_group` | Is Group Warehouse | Check | Optional | `0` | - |
| `customer` | Customer | Link | Optional | `-` | Customer |
| `address_html` | Address HTML | HTML | Optional | `-` | - |
| `contact_html` | Contact HTML | HTML | Optional | `-` | - |
| `email_id` | Email Address | Data | Optional | `-` | - |
| `phone_no` | Phone No | Data | Optional | `-` | Phone |
| `mobile_no` | Mobile No | Data | Optional | `-` | Phone |
| `address_line_1` | Address Line 1 | Data | Optional | `-` | - |
| `address_line_2` | Address Line 2 | Data | Optional | `-` | - |
| `city` | City | Data | Optional | `-` | - |
| `state` | State/Province | Data | Optional | `-` | - |
| `pin` | PIN | Data | Optional | `-` | - |
| `warehouse_type` | Warehouse Type | Link | Optional | `-` | Warehouse Type |
| `default_in_transit_warehouse` | Default In-Transit Warehouse | Link | Optional | `-` | Warehouse |
| `lft` | lft | Int | Optional | `-` | - |
| `rgt` | rgt | Int | Optional | `-` | - |
| `old_parent` | Old Parent | Link | Optional | `-` | Warehouse |

### DocType: `Stock Settings`
- **Submittable**: No
- **Total Data Fields**: 53

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `item_naming_by` | Item Naming By | Select | Optional | `Item Code` | Item Code, Naming Series |
| `naming_series_details` | Naming Series options | Small Text | Optional | `-` | - |
| `configure` | Configure Series | Button | Optional | `-` | - |
| `item_group` | Default Item Group | Link | Optional | `-` | Item Group |
| `valuation_method` | Default Valuation Method | Select | Optional | `-` | FIFO, Moving Average, LIFO |
| `auto_insert_price_list_rate_if_missing` | Auto insert Item Price if missing | Check | Optional | `0` | - |
| `update_existing_price_list_rate` | Update existing Price List Rate | Check | Optional | `0` | - |
| `update_price_list_based_on` | Update Price List based on | Select | Optional | `Rate` | Rate, Price List Rate |
| `stock_uom` | Default Stock UOM | Link | Optional | `-` | UOM |
| `allow_to_edit_stock_uom_qty_for_sales` | Allow to edit stock UOM qty for Sales documents | Check | Optional | `0` | - |
| `allow_to_edit_stock_uom_qty_for_purchase` | Allow to edit stock UOM qty for Purchase documents | Check | Optional | `0` | - |
| `allow_to_edit_stock_uom_qty_for_stock_entry` | Allow to edit stock UOM qty for Stock Entry | Check | Optional | `0` | - |
| `allow_uom_with_conversion_rate_defined_in_item` | Allow UOM with conversion rate defined in Item | Check | Optional | `0` | - |
| `default_warehouse` | Default Warehouse | Link | Optional | `-` | Warehouse |
| `sample_retention_warehouse` | Sample Retention Warehouse | Link | Optional | `-` | Warehouse |
| `allow_negative_stock` | Allow negative stock | Check | Optional | `0` | - |
| `over_delivery_receipt_allowance` | Over Delivery/Receipt Allowance (%) | Float | Optional | `-` | - |
| `mr_qty_allowance` | Over Transfer Allowance (%) | Float | Optional | `-` | - |
| `over_picking_allowance` | Over Picking Allowance (%) | Percent | Optional | `-` | - |
| `role_allowed_to_over_deliver_receive` | Role Allowed to Over Deliver/Receive | Link | Optional | `-` | Role |
| `show_barcode_field` | Show barcode field in stock transactions | Check | Optional | `1` | - |
| `clean_description_html` | Convert Item description to clean HTML in transactions | Check | Optional | `1` | - |
| `allow_internal_transfer_at_arms_length_price` | Allow internal transfers at user-defined rate | Check | Optional | `0` | - |
| `validate_material_transfer_warehouses` | Validate Material Transfer warehouses | Check | Optional | `0` | - |
| `enable_serial_and_batch_no_for_item` | Activate Serial / Batch No for Item | Check | Optional | `0` | - |
| `pick_serial_and_batch_based_on` | Pick Serial / Batch Based On | Select | Optional | `FIFO` | FIFO, LIFO, Expiry |
| `allow_existing_serial_no` | Allow existing Serial No to be Manufactured/Received again | Check | Optional | `1` | - |
| `use_serial_batch_fields` | Use Serial / Batch fields | Check | Optional | `1` | - |
| `disable_serial_no_and_batch_selector` | Disable Serial No and Batch selector | Check | Optional | `0` | - |
| `allow_negative_stock_for_batch` | Allow negative stock for Batch | Check | Optional | `0` | - |
| `do_not_use_batchwise_valuation` | Do not use Batch-wise Valuation | Check | Optional | `0` | - |
| `use_naming_series` | Have default Naming Series for Batch ID? | Check | Optional | `0` | - |
| `naming_series_prefix` | Naming Series Prefix | Data | Optional | `BATCH-` | - |
| `auto_create_serial_and_batch_bundle_for_outward` | Auto create Serial and Batch Bundle for outward | Check | Optional | `1` | - |
| `do_not_update_serial_batch_on_creation_of_auto_bundle` | Do not update Serial / Batch on creation of auto bundle | Check | Optional | `1` | - |
| `set_serial_and_batch_bundle_naming_based_on_naming_series` | Set Serial and Batch Bundle Naming Based on Naming Series | Check | Optional | `0` | - |
| `naming_series_preview` | Naming Series options | Small Text | Optional | `-` | - |
| `configure_series` | Configure Series | Button | Optional | `-` | - |
| `enable_stock_reservation` | Enable stock reservation | Check | Optional | `0` | - |
| `auto_reserve_stock` | Auto reserve stock | Check | Optional | `0` | - |
| `allow_partial_reservation` | Allow partial reservation | Check | Optional | `1` | - |
| `auto_reserve_stock_for_sales_order_on_purchase` | Auto reserve Stock for Sales Order on Purchase | Check | Optional | `0` | - |
| `auto_reserve_serial_and_batch` | Auto reserve Serial and Batch Nos | Check | Optional | `1` | - |
| `allow_to_make_quality_inspection_after_purchase_or_delivery` | Allow to make Quality Inspection after Purchase / Delivery | Check | Optional | `0` | - |
| `action_if_quality_inspection_is_rejected` | Action if Quality Inspection is rejected | Select | Optional | `Stop` | Stop, Warn |
| `action_if_quality_inspection_is_not_submitted` | Action if Quality Inspection is not submitted | Select | Optional | `Stop` | Stop, Warn |
| `auto_indent` | Raise Material Request when stock reaches re-order level | Check | Optional | `0` | - |
| `reorder_email_notify` | Notify by email on creation of automatic Material Request | Check | Optional | `0` | - |
| `stock_frozen_upto_days` | Freeze stocks older than (days) | Int | Optional | `-` | - |
| `stock_frozen_upto` | Stock frozen up to | Date | Optional | `-` | - |
| `stock_auth_role` | Role allowed to edit frozen stock | Link | Optional | `-` | Role |
| `role_allowed_to_create_edit_back_dated_transactions` | Role allowed to create/edit back-dated transactions | Link | Optional | `-` | Role |
| `transaction_naming_html` | transaction_naming_html | HTML | Optional | `-` | - |

## Module: ERPNext Settings
*Global ERP parameter defaults, perpetual inventory toggles, manufacturing backflush rules, and system-wide validation switches.*

### Summary of DocTypes in ERPNext Settings:
- **Global Defaults**: 9 fields | Submittable: No
- **System Settings**: 81 fields | Submittable: No
- **Accounts Settings**: 66 fields | Submittable: No
- **Stock Settings**: 53 fields | Submittable: No
- **Manufacturing Settings**: 19 fields | Submittable: No
- **Buying Settings**: 31 fields | Submittable: No
- **Selling Settings**: 34 fields | Submittable: No
- **Projects Settings**: 4 fields | Submittable: No

### DocType: `Global Defaults`
- **Submittable**: No
- **Total Data Fields**: 9

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `default_company` | Default Company | Link | Optional | `-` | Company |
| `country` | Country | Link | Optional | `-` | Country |
| `default_distance_unit` | Default Distance Unit | Link | Optional | `-` | UOM |
| `default_currency` | Default Currency | Link | ✓ Mandatory | `INR` | Currency |
| `hide_currency_symbol` | Hide Currency Symbol | Select | Optional | `-` | No, Yes |
| `disable_rounded_total` | Disable Rounded Total | Check | Optional | `0` | - |
| `disable_in_words` | Disable In Words | Check | Optional | `0` | - |
| `use_posting_datetime_for_naming_documents` | Use Posting Datetime for Naming Documents | Check | Optional | `0` | - |
| `demo_company` | Demo Company | Link | Optional | `-` | Company |

### DocType: `System Settings`
- **Submittable**: No
- **Total Data Fields**: 81

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `app_name` | Application Name | Data | Optional | `Frappe` | - |
| `country` | Country | Link | Optional | `-` | Country |
| `language` | Language | Link | ✓ Mandatory | `-` | Language |
| `time_zone` | Time Zone | Select | ✓ Mandatory | `-` | - |
| `currency` | Currency | Link | Optional | `-` | Currency |
| `enable_onboarding` | Enable Onboarding | Check | Optional | `0` | - |
| `setup_complete` | Setup Complete | Check | Optional | `0` | - |
| `disable_document_sharing` | Disable Document Sharing | Check | Optional | `0` | - |
| `date_format` | Date Format | Select | ✓ Mandatory | `-` | yyyy-mm-dd, dd-mm-yyyy, dd/mm/yyyy, dd.mm.yyyy, mm/dd/yyyy, mm-dd-yyyy |
| `time_format` | Time Format | Select | ✓ Mandatory | `HH:mm:ss` | HH:mm:ss, HH:mm |
| `number_format` | Number Format | Select | ✓ Mandatory | `-` | #,###.##, #.###,##, # ###.##, # ###,##, #'###.##, #, ###.##, #,##,###.##, #,#... |
| `use_number_format_from_currency` | Use Number Format from Currency | Check | Optional | `0` | - |
| `first_day_of_the_week` | First Day of the Week | Select | Optional | `Sunday` | Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday |
| `float_precision` | Float Precision | Select | Optional | `-` | 2, 3, 4, 5, 6, 7, 8, 9 |
| `currency_precision` | Currency Precision | Select | Optional | `-` | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| `rounding_method` | Rounding Method | Select | Optional | `Banker's Rounding (legacy)` | Banker's Rounding (legacy), Banker's Rounding, Commercial Rounding |
| `show_absolute_datetime_in_timeline` | Show Absolute Datetime in Timeline | Check | Optional | `0` | - |
| `apply_strict_user_permissions` | Apply Strict User Permissions | Check | Optional | `0` | - |
| `show_external_link_warning` | Show External Link Warning | Select | Optional | `Never` | Never, Ask, Always |
| `session_expiry` | Session Expiry (idle timeout) | Data | Optional | `170:00` | - |
| `document_share_key_expiry` | Document Share Key Expiry (in Days) | Int | Optional | `30` | - |
| `deny_multiple_sessions` | Allow only one session per user | Check | Optional | `0` | - |
| `disable_user_pass_login` | Disable Username/Password Login | Check | Optional | `0` | - |
| `max_signups_allowed_per_hour` | Max signups allowed per hour | Int | Optional | `300` | - |
| `allow_login_using_mobile_number` | Allow Login using Mobile Number | Check | Optional | `0` | - |
| `allow_login_using_user_name` | Allow Login using User Name | Check | Optional | `0` | - |
| `login_with_email_link` | Login with email link | Check | Optional | `1` | - |
| `login_with_email_link_expiry` | Login with email link expiry (in minutes) | Int | Optional | `10` | - |
| `rate_limit_email_link_login` | Rate limit for email link login | Int | Optional | `-` | - |
| `allow_consecutive_login_attempts` | Allow Consecutive Login Attempts | Int | Optional | `10` | - |
| `allow_login_after_fail` | Allow Login After Fail | Int | Optional | `60` | - |
| `enable_two_factor_auth` | Enable Two Factor Auth | Check | Optional | `0` | - |
| `bypass_2fa_for_retricted_ip_users` | Bypass Two Factor Auth for users who login from restricted IP Address | Check | Optional | `0` | - |
| `bypass_restrict_ip_check_if_2fa_enabled` | Bypass restricted IP Address check If Two Factor Auth Enabled | Check | Optional | `0` | - |
| `two_factor_method` | Two Factor Authentication method | Select | Optional | `OTP App` | OTP App, SMS, Email |
| `lifespan_qrcode_image` | Expiry time of QR Code Image Page | Int | Optional | `-` | - |
| `otp_issuer_name` | OTP Issuer Name | Data | Optional | `Frappe Framework` | - |
| `otp_sms_template` | OTP SMS Template | Small Text | Optional | `-` | - |
| `logout_on_password_reset` | Logout All Sessions on Password Reset | Check | Optional | `1` | - |
| `force_user_to_reset_password` | Force User to Reset Password | Int | Optional | `-` | - |
| `reset_password_link_expiry_duration` | Reset Password Link Expiry Duration | Duration | Optional | `1200` | - |
| `password_reset_limit` | Password Reset Link Generation Limit | Int | Optional | `3` | - |
| `enable_password_policy` | Enable Password Policy | Check | Optional | `1` | - |
| `minimum_password_score` | Minimum Password Score | Select | Optional | `2` | 1, 2, 3, 4 |
| `email_footer_address` | Email Footer Address | Small Text | Optional | `-` | - |
| `email_retry_limit` | Email Retry Limit | Int | Optional | `3` | - |
| `disable_standard_email_footer` | Disable Standard Email Footer | Check | Optional | `0` | - |
| `hide_footer_in_auto_email_reports` | Hide footer in auto email reports | Check | Optional | `0` | - |
| `attach_view_link` | Include Web View Link in Email | Check | Optional | `1` | - |
| `store_attached_pdf_document` | Store Attached PDF Document | Check | Optional | `1` | - |
| `welcome_email_template` | Welcome Email Template | Link | Optional | `-` | Email Template |
| `reset_password_template` | Reset Password Template | Link | Optional | `-` | Email Template |
| `max_file_size` | Max File Size (MB) | Int | Optional | `-` | - |
| `max_zip_extract_size` | Max Zip Extract Size (MB) | Int | Optional | `-` | - |
| `allow_guests_to_upload_files` | Allow Guests to Upload Files | Check | Optional | `0` | - |
| `force_web_capture_mode_for_uploads` | Force Web Capture Mode for Uploads | Check | Optional | `0` | - |
| `strip_exif_metadata_from_uploaded_images` | Strip EXIF tags from uploaded images | Check | Optional | `1` | - |
| `only_allow_system_managers_to_upload_public_files` | Only allow System Managers to upload public files | Check | Optional | `0` | - |
| `delete_background_exported_reports_after` | Delete Background Exported Reports After (Hours) | Int | Optional | `48` | - |
| `allowed_file_extensions` | Allowed File Extensions | Small Text | Optional | `-` | - |
| `allowed_doctypes_for_guest_uploads` | Allowed Doctypes for Guest Uploads | Small Text | Optional | `-` | - |
| `default_app` | Default App | Select | Optional | `-` | - |
| `disable_system_update_notification` | Disable System Update Notification | Check | Optional | `0` | - |
| `disable_change_log_notification` | Disable Change Log Notification | Check | Optional | `0` | - |
| `hide_empty_read_only_fields` | Hide Empty Read-Only Fields | Check | Optional | `1` | - |
| `disable_product_suggestion` | Disable Product Suggestion | Check | Optional | `0` | - |
| `backup_limit` | Number of Backups | Int | Optional | `3` | - |
| `encrypt_backup` | Encrypt Backups | Check | Optional | `0` | - |
| `max_auto_email_report_per_user` | Max auto email report per user | Int | Optional | `20` | - |
| `max_report_rows` | Max Report Rows | Int | Optional | `100000` | - |
| `enable_snapshot_reports` | Enable Snapshot Reports | Check | Optional | `0` | - |
| `sync_in_batch` | Sync In Batches | Check | Optional | `1` | - |
| `frequency` | Frequency | Select | Optional | `Daily` | Hourly, Daily |
| `sync_timeout` | Sync Timeout (Seconds) | Int | Optional | `-` | - |
| `enable_scheduler` | Enable Scheduled Jobs | Check | Optional | `0` | - |
| `dormant_days` | Run Jobs only Daily if Inactive For (Days) | Int | Optional | `4` | - |
| `allow_error_traceback` | Show Full Error and Allow Reporting of Issues to the Developer | Check | Optional | `1` | - |
| `enable_telemetry` | Allow Sending Usage Data for Improving Applications | Check | Optional | `1` | - |
| `link_field_results_limit` | Link Field Results Limit | Int | Optional | `10` | - |
| `allow_clearing_link_fields` | Allow Clearing Link Fields | Check | Optional | `0` | - |
| `log_api_requests` | Log API Requests | Check | Optional | `0` | - |

### DocType: `Accounts Settings`
- **Submittable**: No
- **Total Data Fields**: 66

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `unlink_payment_on_cancellation_of_invoice` | Unlink Payment on cancellation of invoice | Check | Optional | `1` | - |
| `unlink_advance_payment_on_cancelation_of_order` | Unlink Advance Payment on cancellation of order | Check | Optional | `1` | - |
| `delete_linked_ledger_entries` | Delete Accounting and Stock Ledger entries on deletion of transaction | Check | Optional | `0` | - |
| `enable_immutable_ledger` | Enable Immutable Ledger | Check | Optional | `0` | - |
| `check_supplier_invoice_uniqueness` | Check Supplier invoice number uniqueness | Check | Optional | `0` | - |
| `automatically_fetch_payment_terms` | Automatically fetch Payment Terms from Order/Quotation | Check | Optional | `0` | - |
| `enable_subscription` | Enable Subscription | Check | Optional | `1` | - |
| `enable_common_party_accounting` | Enable Common Party Accounting | Check | Optional | `0` | - |
| `allow_multi_currency_invoices_against_single_party_account` | Allow multi-currency invoices against single party account  | Check | Optional | `0` | - |
| `confirm_before_resetting_posting_date` | Confirm before resetting posting date | Check | Optional | `1` | - |
| `book_stock_expense_gl_entries` | Book Stock Expense GL Entries | Check | Optional | `0` | - |
| `enable_discounts_and_margin` | Enable Discounts and Margin | Check | Optional | `0` | - |
| `enable_accounting_dimensions` | Enable Accounting Dimensions | Check | Optional | `0` | - |
| `merge_similar_account_heads` | Merge similar Account Heads | Check | Optional | `0` | - |
| `book_deferred_entries_based_on` | Book Deferred entries based on | Select | Optional | `Days` | Days, Months |
| `automatically_process_deferred_accounting_entry` | Automatically process deferred Accounting entry | Check | Optional | `1` | - |
| `book_deferred_entries_via_journal_entry` | Book deferred entries via Journal Entry | Check | Optional | `0` | - |
| `submit_journal_entries` | Submit Journal entries | Check | Optional | `0` | - |
| `determine_address_tax_category_from` | Determine Address Tax Category from | Select | Optional | `Billing Address` | Billing Address, Shipping Address |
| `add_taxes_from_item_tax_template` | Automatically add Taxes and Charges from Item Tax Template | Check | Optional | `1` | - |
| `add_taxes_from_taxes_and_charges_template` | Automatically add taxes from Taxes and Charges Template | Check | Optional | `0` | - |
| `book_tax_discount_loss` | Book tax loss on early payment discount | Check | Optional | `0` | - |
| `round_row_wise_tax` | Round tax amount row-wise | Check | Optional | `0` | - |
| `show_inclusive_tax_in_print` | Show inclusive tax in print | Check | Optional | `0` | - |
| `show_taxes_as_table_in_print` | Show taxes as table in print | Check | Optional | `0` | - |
| `show_payment_schedule_in_print` | Show Payment Schedule in print | Check | Optional | `0` | - |
| `maintain_same_internal_transaction_rate` | Maintain same rate throughout internal Transaction | Check | Optional | `0` | - |
| `fetch_valuation_rate_for_internal_transaction` | Fetch valuation rate for internal Transaction | Check | Optional | `0` | - |
| `maintain_same_rate_action` | Action if same rate is not maintained throughout internal transaction | Select | Optional | `Stop` | Stop, Warn |
| `role_to_override_stop_action` | Role allowed to override stop action | Link | Optional | `-` | Role |
| `allow_stale` | Allow Stale Exchange Rates | Check | Optional | `1` | - |
| `allow_pegged_currencies_exchange_rates` | Allow Implicit Pegged Currency Conversion | Check | Optional | `0` | - |
| `stale_days` | Stale Days | Int | Optional | `1` | - |
| `auto_reconcile_payments` | Auto reconcile Payments | Check | Optional | `0` | - |
| `exchange_gain_loss_posting_date` | Posting Date inheritance for exchange gain / loss | Select | Optional | `Payment` | Invoice, Payment, Reconciliation Date |
| `auto_reconciliation_job_trigger` | Auto Reconciliation job trigger | Int | Optional | `15` | - |
| `reconciliation_queue_size` | Reconciliation queue size | Int | Optional | `5` | - |
| `repost_allowed_types` | Allowed DocTypes | Table | Optional | `-` | Repost Allowed Types |
| `fetch_payment_schedule_in_payment_request` | Fetch Payment Schedule in Payment Request | Check | Optional | `1` | - |
| `enable_loyalty_point_program` | Enable Loyalty Point Program | Check | Optional | `0` | - |
| `make_payment_via_journal_entry` | Make Payment via Journal Entry | Check | Optional | `0` | - |
| `over_billing_allowance` | Over Billing Allowance (%) | Currency | Optional | `-` | - |
| `credit_controller` | Role allowed to bypass credit limit | Link | Optional | `-` | Role |
| `role_allowed_to_over_bill` | Role Allowed to over bill  | Link | Optional | `-` | Role |
| `enable_overdue_billing_threshold` | Prevent Sales Invoice when Customer is Overdue | Check | Optional | `0` | - |
| `role_allowed_to_bypass_overdue_billing` | Role Allowed to Bypass Over Billing Restriction | Link | Optional | `-` | Role |
| `book_asset_depreciation_entry_automatically` | Book Asset Depreciation entry automatically | Check | Optional | `1` | - |
| `calculate_depr_using_total_days` | Calculate daily depreciation using total days in depreciation period | Check | Optional | `0` | - |
| `role_to_notify_on_depreciation_failure` | Role to Notify on Depreciation Failure | Link | Optional | `-` | Role |
| `ignore_account_closing_balance` | Ignore Account closing balance | Check | Optional | `0` | - |
| `use_legacy_controller_for_pcv` | Use legacy controller for Period Closing Voucher | Check | Optional | `1` | - |
| `pcv_job_timeout` | PCV Job Timeout (seconds) | Int | Optional | `3600` | - |
| `disable_include_dimensions` | Disable "Consider Accounting Dimension" Filter | Check | Optional | `0` | - |
| `general_ledger_remarks_length` | General Ledger remarks length | Int | Optional | `0` | - |
| `receivable_payable_fetch_method` | Data fetch method | Select | Optional | `Buffered Cursor` | Buffered Cursor, UnBuffered Cursor |
| `default_ageing_range` | Default Ageing Range | Data | Optional | `30, 60, 90, 120` | - |
| `receivable_payable_remarks_length` | Accounts Receivable / Payable remarks length | Int | Optional | `0` | - |
| `ignore_is_opening_check_for_reporting` | Ignore Is Opening check for reporting | Check | Optional | `0` | - |
| `show_balance_in_coa` | Show balances in Chart of Accounts | Check | Optional | `1` | - |
| `enable_party_matching` | Enable Automatic Party Matching | Check | Optional | `0` | - |
| `automatically_run_rules_on_unreconciled_transactions` | Automatically run rules on unreconciled transactions | Check | Optional | `1` | - |
| `enable_fuzzy_matching` | Enable Fuzzy Matching | Check | Optional | `0` | - |
| `transfer_match_days` | Match transfers within 'N' days | Int | Optional | `3` | - |
| `create_pr_in_draft_status` | Create payment requests in Draft status | Check | Optional | `1` | - |
| `use_legacy_budget_controller` | Use legacy Budget Controller | Check | Optional | `0` | - |
| `transaction_naming_html` | transaction_naming_html | HTML | Optional | `-` | - |

### DocType: `Stock Settings`
- **Submittable**: No
- **Total Data Fields**: 53

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `item_naming_by` | Item Naming By | Select | Optional | `Item Code` | Item Code, Naming Series |
| `naming_series_details` | Naming Series options | Small Text | Optional | `-` | - |
| `configure` | Configure Series | Button | Optional | `-` | - |
| `item_group` | Default Item Group | Link | Optional | `-` | Item Group |
| `valuation_method` | Default Valuation Method | Select | Optional | `-` | FIFO, Moving Average, LIFO |
| `auto_insert_price_list_rate_if_missing` | Auto insert Item Price if missing | Check | Optional | `0` | - |
| `update_existing_price_list_rate` | Update existing Price List Rate | Check | Optional | `0` | - |
| `update_price_list_based_on` | Update Price List based on | Select | Optional | `Rate` | Rate, Price List Rate |
| `stock_uom` | Default Stock UOM | Link | Optional | `-` | UOM |
| `allow_to_edit_stock_uom_qty_for_sales` | Allow to edit stock UOM qty for Sales documents | Check | Optional | `0` | - |
| `allow_to_edit_stock_uom_qty_for_purchase` | Allow to edit stock UOM qty for Purchase documents | Check | Optional | `0` | - |
| `allow_to_edit_stock_uom_qty_for_stock_entry` | Allow to edit stock UOM qty for Stock Entry | Check | Optional | `0` | - |
| `allow_uom_with_conversion_rate_defined_in_item` | Allow UOM with conversion rate defined in Item | Check | Optional | `0` | - |
| `default_warehouse` | Default Warehouse | Link | Optional | `-` | Warehouse |
| `sample_retention_warehouse` | Sample Retention Warehouse | Link | Optional | `-` | Warehouse |
| `allow_negative_stock` | Allow negative stock | Check | Optional | `0` | - |
| `over_delivery_receipt_allowance` | Over Delivery/Receipt Allowance (%) | Float | Optional | `-` | - |
| `mr_qty_allowance` | Over Transfer Allowance (%) | Float | Optional | `-` | - |
| `over_picking_allowance` | Over Picking Allowance (%) | Percent | Optional | `-` | - |
| `role_allowed_to_over_deliver_receive` | Role Allowed to Over Deliver/Receive | Link | Optional | `-` | Role |
| `show_barcode_field` | Show barcode field in stock transactions | Check | Optional | `1` | - |
| `clean_description_html` | Convert Item description to clean HTML in transactions | Check | Optional | `1` | - |
| `allow_internal_transfer_at_arms_length_price` | Allow internal transfers at user-defined rate | Check | Optional | `0` | - |
| `validate_material_transfer_warehouses` | Validate Material Transfer warehouses | Check | Optional | `0` | - |
| `enable_serial_and_batch_no_for_item` | Activate Serial / Batch No for Item | Check | Optional | `0` | - |
| `pick_serial_and_batch_based_on` | Pick Serial / Batch Based On | Select | Optional | `FIFO` | FIFO, LIFO, Expiry |
| `allow_existing_serial_no` | Allow existing Serial No to be Manufactured/Received again | Check | Optional | `1` | - |
| `use_serial_batch_fields` | Use Serial / Batch fields | Check | Optional | `1` | - |
| `disable_serial_no_and_batch_selector` | Disable Serial No and Batch selector | Check | Optional | `0` | - |
| `allow_negative_stock_for_batch` | Allow negative stock for Batch | Check | Optional | `0` | - |
| `do_not_use_batchwise_valuation` | Do not use Batch-wise Valuation | Check | Optional | `0` | - |
| `use_naming_series` | Have default Naming Series for Batch ID? | Check | Optional | `0` | - |
| `naming_series_prefix` | Naming Series Prefix | Data | Optional | `BATCH-` | - |
| `auto_create_serial_and_batch_bundle_for_outward` | Auto create Serial and Batch Bundle for outward | Check | Optional | `1` | - |
| `do_not_update_serial_batch_on_creation_of_auto_bundle` | Do not update Serial / Batch on creation of auto bundle | Check | Optional | `1` | - |
| `set_serial_and_batch_bundle_naming_based_on_naming_series` | Set Serial and Batch Bundle Naming Based on Naming Series | Check | Optional | `0` | - |
| `naming_series_preview` | Naming Series options | Small Text | Optional | `-` | - |
| `configure_series` | Configure Series | Button | Optional | `-` | - |
| `enable_stock_reservation` | Enable stock reservation | Check | Optional | `0` | - |
| `auto_reserve_stock` | Auto reserve stock | Check | Optional | `0` | - |
| `allow_partial_reservation` | Allow partial reservation | Check | Optional | `1` | - |
| `auto_reserve_stock_for_sales_order_on_purchase` | Auto reserve Stock for Sales Order on Purchase | Check | Optional | `0` | - |
| `auto_reserve_serial_and_batch` | Auto reserve Serial and Batch Nos | Check | Optional | `1` | - |
| `allow_to_make_quality_inspection_after_purchase_or_delivery` | Allow to make Quality Inspection after Purchase / Delivery | Check | Optional | `0` | - |
| `action_if_quality_inspection_is_rejected` | Action if Quality Inspection is rejected | Select | Optional | `Stop` | Stop, Warn |
| `action_if_quality_inspection_is_not_submitted` | Action if Quality Inspection is not submitted | Select | Optional | `Stop` | Stop, Warn |
| `auto_indent` | Raise Material Request when stock reaches re-order level | Check | Optional | `0` | - |
| `reorder_email_notify` | Notify by email on creation of automatic Material Request | Check | Optional | `0` | - |
| `stock_frozen_upto_days` | Freeze stocks older than (days) | Int | Optional | `-` | - |
| `stock_frozen_upto` | Stock frozen up to | Date | Optional | `-` | - |
| `stock_auth_role` | Role allowed to edit frozen stock | Link | Optional | `-` | Role |
| `role_allowed_to_create_edit_back_dated_transactions` | Role allowed to create/edit back-dated transactions | Link | Optional | `-` | Role |
| `transaction_naming_html` | transaction_naming_html | HTML | Optional | `-` | - |

### DocType: `Manufacturing Settings`
- **Submittable**: No
- **Total Data Fields**: 19

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `material_consumption` | Allow Continuous Material Consumption | Check | Optional | `0` | - |
| `get_rm_cost_from_consumption_entry` | Get Raw Materials Cost from Consumption Entry | Check | Optional | `0` | - |
| `backflush_raw_materials_based_on` | Backflush Raw Materials Based On | Select | Optional | `BOM` | BOM, Material Transferred for Manufacture |
| `validate_components_quantities_per_bom` | Validate Components and Quantities Per BOM | Check | Optional | `0` | - |
| `update_bom_costs_automatically` | Update BOM Cost Automatically | Check | Optional | `0` | - |
| `allow_editing_of_items_and_quantities_in_work_order` | Allow Editing of Items and Quantities in Work Order | Check | Optional | `0` | - |
| `overproduction_percentage_for_sales_order` | Overproduction Percentage For Sales Order | Percent | Optional | `-` | - |
| `overproduction_percentage_for_work_order` | Overproduction Percentage For Work Order | Percent | Optional | `-` | - |
| `transfer_extra_materials_percentage` | Transfer Extra Raw Materials to WIP (%) | Percent | Optional | `-` | - |
| `add_corrective_operation_cost_in_finished_good_valuation` | Add Corrective Operation Cost in Finished Good Valuation | Check | Optional | `0` | - |
| `enforce_time_logs` | Enforce Time Logs | Check | Optional | `0` | - |
| `job_card_excess_transfer` | Allow Excess Material Transfer | Check | Optional | `0` | - |
| `disable_capacity_planning` | Disable Capacity Planning | Check | Optional | `0` | - |
| `allow_overtime` | Allow Overtime | Check | Optional | `0` | - |
| `allow_production_on_holidays` | Allow Production on Holidays | Check | Optional | `0` | - |
| `capacity_planning_for_days` | Capacity Planning For (Days) | Int | Optional | `30` | - |
| `mins_between_operations` | Time Between Operations (Mins) | Int | Optional | `-` | - |
| `set_op_cost_and_secondary_items_from_sub_assemblies` | Set Operating Cost / Secondary Items From Sub-assemblies | Check | Optional | `0` | - |
| `make_serial_no_batch_from_work_order` | Make Serial No / Batch from Work Order | Check | Optional | `0` | - |

### DocType: `Buying Settings`
- **Submittable**: No
- **Total Data Fields**: 31

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `supp_master_name` | Supplier Naming By | Select | Optional | `Supplier Name` | Supplier Name, Naming Series, Auto Name |
| `naming_series_details` | Naming Series options | Small Text | Optional | `-` | - |
| `configure` | Configure Series | Button | Optional | `-` | - |
| `supplier_group` | Default Supplier Group | Link | Optional | `-` | Supplier Group |
| `buying_price_list` | Default Buying Price List | Link | Optional | `-` | Price List |
| `maintain_same_rate` | Maintain same rate throughout the purchase  cycle | Check | Optional | `0` | - |
| `set_landed_cost_based_on_purchase_invoice_rate` | Set Landed Cost Based on Purchase Invoice Rate | Check | Optional | `0` | - |
| `maintain_same_rate_action` | Action if same rate is not maintained | Select | Optional | `Stop` | Stop, Warn |
| `role_to_override_stop_action` | Role allowed to override stop action | Link | Optional | `-` | Role |
| `po_required` | Is Purchase Order required for Purchase Invoice & Receipt creation? | Select | Optional | `-` | No, Yes |
| `pr_required` | Is Purchase Receipt required for Purchase Invoice creation? | Select | Optional | `-` | No, Yes |
| `project_update_frequency` | How often should project be updated of Total Purchase Cost ? | Select | Optional | `Each Transaction` | Each Transaction, Manual |
| `over_order_allowance` | Over Order Allowance (%) | Float | Optional | `-` | - |
| `allow_multiple_items` | Allow Item to be added multiple times in a transaction | Check | Optional | `0` | - |
| `allow_negative_rates_for_items` | Allow negative rates for Items | Check | Optional | `0` | - |
| `set_valuation_rate_for_rejected_materials` | Set valuation rate for rejected Materials | Check | Optional | `0` | - |
| `disable_last_purchase_rate` | Disable last purchase rate | Check | Optional | `0` | - |
| `show_pay_button` | Show pay button in Purchase Order portal | Check | Optional | `1` | - |
| `bill_for_rejected_quantity_in_purchase_invoice` | Bill for rejected quantity in Purchase Invoice | Check | Optional | `1` | - |
| `use_transaction_date_exchange_rate` | Use Transaction Date Exchange Rate | Check | Optional | `0` | - |
| `allow_zero_qty_in_supplier_quotation` | Allow Supplier Quotation with Zero Quantity | Check | Optional | `0` | - |
| `allow_zero_qty_in_request_for_quotation` | Allow Request for Quotation with Zero Quantity | Check | Optional | `0` | - |
| `allow_zero_qty_in_purchase_order` | Allow Purchase Order with Zero Quantity | Check | Optional | `0` | - |
| `blanket_order_allowance` | Blanket Order Allowance (%) | Float | Optional | `0` | - |
| `backflush_raw_materials_of_subcontract_based_on` | Backflush raw materials of subcontract based on | Select | Optional | `BOM` | BOM, Material Transferred for Subcontract |
| `over_transfer_allowance` | Over Transfer Allowance (%) | Float | Optional | `-` | - |
| `validate_consumed_qty` | Validate consumed quantity (as per BOM) | Check | Optional | `0` | - |
| `auto_create_subcontracting_order` | Auto create Subcontracting Order | Check | Optional | `0` | - |
| `auto_create_purchase_receipt` | Auto create Purchase Receipt | Check | Optional | `0` | - |
| `fixed_email` | Fixed Outgoing Email Account | Link | Optional | `-` | Email Account |
| `transaction_naming_html` | transaction_naming_html | HTML | Optional | `-` | - |

### DocType: `Selling Settings`
- **Submittable**: No
- **Total Data Fields**: 34

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `cust_master_name` | Customer Naming By | Select | Optional | `Customer Name` | Customer Name, Naming Series, Auto Name |
| `naming_series_details` | Naming Series options | Small Text | Optional | `-` | - |
| `configure` | Configure Series | Button | Optional | `-` | - |
| `customer_group` | Default Customer Group | Link | Optional | `-` | Customer Group |
| `territory` | Default Territory | Link | Optional | `-` | Territory |
| `selling_price_list` | Default Price List | Link | Optional | `-` | Price List |
| `fallback_to_default_price_list` | Use prices from Default Price List as fallback | Check | Optional | `0` | - |
| `editable_price_list_rate` | Allow editing Price List rate in transactions | Check | Optional | `0` | - |
| `maintain_same_sales_rate` | Maintain same rate throughout sales cycle | Check | Optional | `0` | - |
| `maintain_same_rate_action` | Action if same rate is not maintained throughout sales cycle | Select | Optional | `Stop` | Stop, Warn |
| `role_to_override_stop_action` | Role allowed to override stop action | Link | Optional | `-` | Role |
| `validate_selling_price` | Validate selling price for Item against purchase or valuation rate | Check | Optional | `0` | - |
| `editable_bundle_item_rates` | Calculate Product Bundle price based on child Item's rates | Check | Optional | `0` | - |
| `allow_negative_rates_for_items` | Allow negative rates for Items | Check | Optional | `0` | - |
| `so_required` | Is Sales Order required to create Sales Invoice/Delivery Note? | Select | Optional | `-` | No, Yes |
| `dn_required` | Is Delivery Note required to create Sales Invoice? | Select | Optional | `-` | No, Yes |
| `sales_update_frequency` | How often should sales data be updated in Company/Project? | Select | ✓ Mandatory | `Daily` | Monthly, Each Transaction, Daily |
| `allow_multiple_items` | Allow same Item to be added multiple times in a transaction | Check | Optional | `0` | - |
| `allow_against_multiple_purchase_orders` | Allow multiple Sales Orders against a customer's Purchase Order | Check | Optional | `0` | - |
| `hide_tax_id` | Hide Customer's Tax ID from sales transactions | Check | Optional | `0` | - |
| `allow_sales_order_creation_for_expired_quotation` | Allow Sales Order creation for expired Quotation | Check | Optional | `0` | - |
| `dont_reserve_sales_order_qty_on_sales_return` | Don't reserve Sales Order qty on sales return | Check | Optional | `0` | - |
| `enable_cutoff_date_on_bulk_delivery_note_creation` | Enable cut-off date on creating bulk Delivery Notes | Check | Optional | `0` | - |
| `set_zero_rate_for_expired_batch` | Set incoming rate as zero for expired Batch | Check | Optional | `0` | - |
| `allow_zero_qty_in_quotation` | Allow Quotation with zero quantity | Check | Optional | `0` | - |
| `allow_zero_qty_in_sales_order` | Allow Sales Order with zero quantity | Check | Optional | `0` | - |
| `blanket_order_allowance` | Blanket Order Allowance (%) | Float | Optional | `-` | - |
| `enable_tracking_sales_commissions` | Enable tracking sales commissions | Check | Optional | `0` | - |
| `enable_discount_accounting` | Enable discount accounting for selling | Check | Optional | `0` | - |
| `enable_utm` | Enable UTM | Check | Optional | `0` | - |
| `use_legacy_js_reactivity` | Use Legacy (Client side) Reactivity | Check | Optional | `0` | - |
| `allow_delivery_of_overproduced_qty` | Allow delivery of overproduced quantity | Check | Optional | `0` | - |
| `deliver_secondary_items` | Deliver secondary Items | Check | Optional | `0` | - |
| `transaction_naming_html` | transaction_naming_html | HTML | Optional | `-` | - |

### DocType: `Projects Settings`
- **Submittable**: No
- **Total Data Fields**: 4

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `ignore_workstation_time_overlap` | Ignore Workstation Time Overlap | Check | Optional | `0` | - |
| `ignore_user_time_overlap` | Ignore User Time Overlap | Check | Optional | `0` | - |
| `ignore_employee_time_overlap` | Ignore Employee Time Overlap | Check | Optional | `0` | - |
| `fetch_timesheet_in_sales_invoice` | Fetch Timesheet in Sales Invoice | Check | Optional | `0` | - |

## Module: Framework
*Underlying Frappe metadata engine: DocTypes, Custom Fields, Customize Form, Property Setters, Workflows, Client Scripts, and Server Scripts.*

### Summary of DocTypes in Framework:
- **DocType**: 72 fields | Submittable: No
- **Customize Form**: 45 fields | Submittable: No
- **Custom Field**: 58 fields | Submittable: No
- **Property Setter**: 11 fields | Submittable: No
- **Workflow**: 10 fields | Submittable: No
- **Server Script**: 14 fields | Submittable: No
- **Client Script**: 6 fields | Submittable: No

### DocType: `DocType`
- **Submittable**: No
- **Total Data Fields**: 72

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `form_builder` | Form Builder | HTML | Optional | `-` | - |
| `permissions` | Permissions | Table | Optional | `-` | DocPerm |
| `restrict_to_domain` | Restrict To Domain | Link | Optional | `-` | Domain |
| `read_only` | User Cannot Search | Check | Optional | `0` | - |
| `in_create` | User Cannot Create | Check | Optional | `0` | - |
| `protect_attached_files` | Protect Attached Files | Check | Optional | `0` | - |
| `naming_rule` | Naming Rule | Select | Optional | `-` | Set by user, Autoincrement, By fieldname, By "Naming Series" field, Expressio... |
| `autoname` | Auto Name | Data | Optional | `-` | - |
| `title_field` | Title Field | Data | Optional | `-` | - |
| `allow_rename` | Allow Rename | Check | Optional | `1` | - |
| `module` | Module | Link | ✓ Mandatory | `-` | Module Def |
| `is_submittable` | Is Submittable | Check | Optional | `0` | - |
| `istable` | Is Child Table | Check | Optional | `0` | - |
| `issingle` | Is Single | Check | Optional | `0` | - |
| `is_tree` | Is Tree | Check | Optional | `0` | - |
| `is_calendar_and_gantt` | Is Calendar and Gantt | Check | Optional | `0` | - |
| `editable_grid` | Editable Grid | Check | Optional | `1` | - |
| `quick_entry` | Quick Entry | Check | Optional | `0` | - |
| `grid_page_length` | Grid Page Length | Int | Optional | `50` | - |
| `rows_threshold_for_grid_search` | Rows Threshold for Grid Search | Int | Optional | `20` | - |
| `allow_bulk_edit` | Allow Bulk Edit | Check | Optional | `1` | - |
| `track_changes` | Track Changes | Check | Optional | `0` | - |
| `track_seen` | Track Seen | Check | Optional | `0` | - |
| `track_views` | Track Views | Check | Optional | `0` | - |
| `custom` | Custom? | Check | Optional | `0` | - |
| `beta` | Beta | Check | Optional | `0` | - |
| `is_virtual` | Is Virtual | Check | Optional | `0` | - |
| `queue_in_background` | Queue in Background (BETA) | Check | Optional | `0` | - |
| `description` | Description | Small Text | Optional | `-` | - |
| `image_field` | Image Field | Data | Optional | `-` | - |
| `timeline_field` | Timeline Field | Data | Optional | `-` | - |
| `nsm_parent_field` | Parent Field (Tree) | Data | Optional | `-` | - |
| `max_attachments` | Max Attachments | Int | Optional | `-` | - |
| `documentation` | Documentation Link | Data | Optional | `-` | - |
| `hide_toolbar` | Hide Sidebar, Menu, and Comments | Check | Optional | `0` | - |
| `allow_copy` | Hide Copy | Check | Optional | `0` | - |
| `allow_import` | Allow Import (via Data Import Tool) | Check | Optional | `0` | - |
| `allow_events_in_timeline` | Allow events in timeline | Check | Optional | `0` | - |
| `allow_auto_repeat` | Allow Auto Repeat | Check | Optional | `0` | - |
| `make_attachments_public` | Make Attachments Public by Default | Check | Optional | `0` | - |
| `show_title_field_in_link` | Show Title in Link Fields | Check | Optional | `0` | - |
| `translated_doctype` | Translate Link Fields | Check | Optional | `0` | - |
| `search_fields` | Search Fields | Data | Optional | `-` | - |
| `default_print_format` | Default Print Format | Data | Optional | `-` | - |
| `sort_field` | Default Sort Field | Data | Optional | `creation` | - |
| `sort_order` | Default Sort Order | Select | Optional | `DESC` | ASC, DESC |
| `default_view` | Default View | Select | Optional | `-` | - |
| `force_re_route_to_default_view` | Force Re-route to Default View | Check | Optional | `0` | - |
| `document_type` | Show in Module Section | Select | Optional | `-` | Document, Setup, System, Other |
| `icon` | Icon | Data | Optional | `-` | - |
| `color` | Color | Data | Optional | `-` | - |
| `show_preview_popup` | Show Preview Popup | Check | Optional | `0` | - |
| `show_name_in_global_search` | Make "name" searchable in Global Search | Check | Optional | `0` | - |
| `default_email_template` | Default Email Template | Link | Optional | `-` | Email Template |
| `email_append_to` | Allow document creation via Email | Check | Optional | `0` | - |
| `sender_field` | Sender Email Field | Data | Optional | `-` | - |
| `sender_name_field` | Sender Name Field | Data | Optional | `-` | - |
| `recipient_account_field` | Recipient Account Field | Data | Optional | `-` | - |
| `subject_field` | Subject Field | Data | Optional | `-` | - |
| `fields` | Fields | Table | Optional | `-` | DocField |
| `actions` | Document Actions | Table | Optional | `-` | DocType Action |
| `links` | Document Links | Table | Optional | `-` | DocType Link |
| `states` | Document States | Table | Optional | `-` | DocType State |
| `has_web_view` | Has Web View | Check | Optional | `0` | - |
| `allow_guest_to_view` | Allow Guest to View | Check | Optional | `0` | - |
| `index_web_pages_for_search` | Index Web Pages for Search | Check | Optional | `1` | - |
| `route` | Route | Data | Optional | `-` | - |
| `is_published_field` | Is Published Field | Data | Optional | `-` | - |
| `website_search_field` | Website Search Field | Data | Optional | `-` | - |
| `engine` | Database Engine | Select | Optional | `InnoDB` | InnoDB, MyISAM |
| `migration_hash` | migration_hash | Data | Optional | `-` | - |
| `row_format` | Row Format | Select | Optional | `Dynamic` | Dynamic, Compressed |

### DocType: `Customize Form`
- **Submittable**: No
- **Total Data Fields**: 45

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `doc_type` | Enter Form Type | Link | Optional | `-` | DocType |
| `label` | Change Label (via Custom Translation) | Data | Optional | `-` | - |
| `search_fields` | Search Fields | Data | Optional | `-` | - |
| `grid_page_length` | Grid Page Length | Int | Optional | `-` | - |
| `rows_threshold_for_grid_search` | Rows Threshold for Grid Search | Int | Optional | `-` | - |
| `link_filters` | Link Filters | JSON | Optional | `-` | - |
| `istable` | Is Table | Check | Optional | `0` | - |
| `is_calendar_and_gantt` | Is Calendar and Gantt | Check | Optional | `0` | - |
| `editable_grid` | Editable Grid | Check | Optional | `0` | - |
| `quick_entry` | Quick Entry | Check | Optional | `1` | - |
| `track_changes` | Track Changes | Check | Optional | `0` | - |
| `track_views` | Track Views | Check | Optional | `0` | - |
| `allow_auto_repeat` | Allow Auto Repeat | Check | Optional | `0` | - |
| `allow_import` | Allow Import (via Data Import Tool) | Check | Optional | `0` | - |
| `allow_bulk_edit` | Allow Bulk Edit | Check | Optional | `1` | - |
| `queue_in_background` | Queue in Background (BETA) | Check | Optional | `0` | - |
| `naming_rule` | Naming Rule | Select | Optional | `-` | Set by user, By fieldname, By "Naming Series" field, Expression, Expression (... |
| `autoname` | Auto Name | Data | Optional | `-` | - |
| `image_field` | Image Field | Data | Optional | `-` | - |
| `max_attachments` | Max Attachments | Int | Optional | `-` | - |
| `hide_toolbar` | Hide Sidebar, Menu, and Comments | Check | Optional | `0` | - |
| `allow_copy` | Hide Copy | Check | Optional | `0` | - |
| `make_attachments_public` | Make Attachments Public by Default | Check | Optional | `0` | - |
| `protect_attached_files` | Protect Attached Files | Check | Optional | `0` | - |
| `title_field` | Title Field | Data | Optional | `-` | - |
| `show_title_field_in_link` | Show Title in Link Fields | Check | Optional | `0` | - |
| `translated_doctype` | Translate Link Fields | Check | Optional | `0` | - |
| `default_print_format` | Default Print Format | Link | Optional | `-` | Print Format |
| `default_view` | Default View | Select | Optional | `-` | - |
| `force_re_route_to_default_view` | Force Re-route to Default View | Check | Optional | `0` | - |
| `show_preview_popup` | Show Preview Popup | Check | Optional | `0` | - |
| `show_name_in_global_search` | Make "name" searchable in Global Search | Check | Optional | `0` | - |
| `default_email_template` | Default Email Template | Link | Optional | `-` | Email Template |
| `email_append_to` | Allow document creation via Email | Check | Optional | `0` | - |
| `sender_field` | Sender Email Field | Data | Optional | `-` | - |
| `sender_name_field` | Sender Name Field | Data | Optional | `-` | - |
| `recipient_account_field` | Recipient Account Field | Data | Optional | `-` | - |
| `subject_field` | Subject Field | Data | Optional | `-` | - |
| `sort_field` | Sort Field | Select | Optional | `-` | - |
| `sort_order` | Sort Order | Select | Optional | `-` | ASC, DESC |
| `actions` | Actions | Table | Optional | `-` | DocType Action |
| `links` | Links | Table | Optional | `-` | DocType Link |
| `states` | States | Table | Optional | `-` | DocType State |
| `fields` | Fields | Table | ✓ Mandatory | `-` | Customize Form Field |
| `form_builder` | Form Builder | HTML | Optional | `-` | - |

### DocType: `Custom Field`
- **Submittable**: No
- **Total Data Fields**: 58

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `is_system_generated` | Is System Generated | Check | Optional | `0` | - |
| `dt` | DocType | Link | ✓ Mandatory | `-` | DocType |
| `module` | Module (for export) | Link | Optional | `-` | Module Def |
| `label` | Label | Data | Optional | `-` | - |
| `placeholder` | Placeholder | Data | Optional | `-` | - |
| `label_help` | Label Help | HTML | Optional | `-` | - |
| `fieldname` | Fieldname | Data | Optional | `-` | - |
| `insert_after` | Insert After | Select | Optional | `-` | - |
| `length` | Length | Int | Optional | `-` | - |
| `link_filters` | Link Filters | JSON | Optional | `-` | - |
| `fieldtype` | Field Type | Select | ✓ Mandatory | `Data` | Autocomplete, Attach, Attach Image, Barcode, Button, Check, Code, Color, Colu... |
| `button_color` | Button Color | Select | Optional | `-` | Default, Primary, Info, Success, Warning, Danger |
| `precision` | Precision | Select | Optional | `-` | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| `hide_seconds` | Hide Seconds | Check | Optional | `0` | - |
| `hide_days` | Hide Days | Check | Optional | `0` | - |
| `options` | Options | Small Text | Optional | `-` | - |
| `sort_options` | Sort Options | Check | Optional | `0` | - |
| `fetch_from` | Fetch From | Small Text | Optional | `-` | - |
| `fetch_if_empty` | Fetch on Save if Empty | Check | Optional | `0` | - |
| `options_help` | Options Help | HTML | Optional | `-` | - |
| `collapsible` | Collapsible | Check | Optional | `0` | - |
| `collapsible_depends_on` | Collapsible Depends On | Code | Optional | `-` | - |
| `default` | Default Value | Text | Optional | `-` | - |
| `depends_on` | Depends On | Code | Optional | `-` | - |
| `mandatory_depends_on` | Mandatory Depends On | Code | Optional | `-` | - |
| `read_only_depends_on` | Read Only Depends On | Code | Optional | `-` | - |
| `non_negative` | Non Negative | Check | Optional | `0` | - |
| `reqd` | Is Mandatory Field | Check | Optional | `0` | - |
| `unique` | Unique | Check | Optional | `0` | - |
| `is_virtual` | Is Virtual | Check | Optional | `0` | - |
| `read_only` | Read Only | Check | Optional | `0` | - |
| `mask` | Mask | Check | Optional | `0` | - |
| `ignore_user_permissions` | Ignore User Permissions | Check | Optional | `0` | - |
| `hidden` | Hidden | Check | Optional | `0` | - |
| `print_hide` | Print Hide | Check | Optional | `0` | - |
| `print_hide_if_no_value` | Print Hide If No Value | Check | Optional | `0` | - |
| `print_width` | Print Width | Data | Optional | `-` | - |
| `alignment` | Alignment | Select | Optional | `-` | Left, Center, Right |
| `no_copy` | No Copy | Check | Optional | `0` | - |
| `set_only_once` | Set only once | Check | Optional | `0` | - |
| `allow_on_submit` | Allow on Submit | Check | Optional | `0` | - |
| `in_list_view` | In List View | Check | Optional | `0` | - |
| `in_standard_filter` | In Standard Filter | Check | Optional | `0` | - |
| `in_global_search` | In Global Search | Check | Optional | `0` | - |
| `in_preview` | In Preview | Check | Optional | `0` | - |
| `bold` | Bold | Check | Optional | `0` | - |
| `report_hide` | Report Hide | Check | Optional | `0` | - |
| `search_index` | Index | Check | Optional | `0` | - |
| `allow_in_quick_entry` | Allow in Quick Entry | Check | Optional | `0` | - |
| `allow_bulk_edit` | Allow Bulk Edit | Check | Optional | `0` | - |
| `ignore_xss_filter` | Ignore XSS Filter | Check | Optional | `0` | - |
| `translatable` | Translatable | Check | Optional | `0` | - |
| `hide_border` | Hide Border | Check | Optional | `0` | - |
| `show_dashboard` | Show Dashboard | Check | Optional | `0` | - |
| `description` | Field Description | Text | Optional | `-` | - |
| `permlevel` | Permission Level | Int | Optional | `0` | - |
| `width` | Width | Data | Optional | `-` | - |
| `columns` | Columns | Int | Optional | `-` | - |

### DocType: `Property Setter`
- **Submittable**: No
- **Total Data Fields**: 11

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `is_system_generated` | Is System Generated | Check | Optional | `0` | - |
| `help` | Help | HTML | Optional | `-` | <div class="alert">Please don't update it as it can mess up your form. Use th... |
| `doctype_or_field` | Applied On | Select | ✓ Mandatory | `-` | DocField, DocType, DocType Link, DocType Action, DocType State |
| `doc_type` | DocType | Link | ✓ Mandatory | `-` | DocType |
| `field_name` | Field Name | Data | Optional | `-` | - |
| `row_name` | Row Name | Data | Optional | `-` | - |
| `module` | Module (for export) | Link | Optional | `-` | Module Def |
| `property` | Property | Data | ✓ Mandatory | `-` | - |
| `property_type` | Property Type | Data | Optional | `-` | - |
| `value` | Set Value | Small Text | Optional | `-` | - |
| `default_value` | Default Value | Data | Optional | `-` | - |

### DocType: `Workflow`
- **Submittable**: No
- **Total Data Fields**: 10

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `workflow_name` | Workflow Name | Data | ✓ Mandatory | `-` | - |
| `document_type` | Document Type | Link | ✓ Mandatory | `-` | DocType |
| `is_active` | Is Active | Check | Optional | `0` | - |
| `override_status` | Don't Override Status | Check | Optional | `0` | - |
| `send_email_alert` | Send Email Alert | Check | Optional | `0` | - |
| `enable_action_confirmation` | Enable Action Confirmation | Check | Optional | `0` | - |
| `states` | Document States | Table | Optional | `-` | Workflow Document State |
| `transitions` | Transitions | Table | Optional | `-` | Workflow Transition |
| `workflow_state_field` | Workflow State Field | Data | ✓ Mandatory | `workflow_state` | - |
| `workflow_data` | Workflow Data | JSON | Optional | `-` | - |

### DocType: `Server Script`
- **Submittable**: No
- **Total Data Fields**: 14

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `script_type` | Script Type | Select | ✓ Mandatory | `-` | DocType Event, Scheduler Event, Permission Query, API, Workflow Task |
| `reference_doctype` | Reference Document Type | Link | Optional | `-` | DocType |
| `event_frequency` | Event Frequency | Select | Optional | `-` | All, Hourly, Daily, Weekly, Monthly, Yearly, Hourly Long, Daily Long, Weekly ... |
| `cron_format` | Cron Format | Data | Optional | `-` | - |
| `doctype_event` | DocType Event | Select | Optional | `-` | Before Insert, Before Validate, Before Save, After Insert, After Save, Before... |
| `api_method` | API Method | Data | Optional | `-` | - |
| `allow_guest` | Allow Guest | Check | Optional | `0` | - |
| `module` | Module (for export) | Link | Optional | `-` | Module Def |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `script` | Script | Code | ✓ Mandatory | `-` | Python |
| `enable_rate_limit` | Enable Rate Limit | Check | Optional | `0` | - |
| `rate_limit_count` | Request Limit | Int | Optional | `5` | - |
| `rate_limit_seconds` | Time Window (Seconds) | Int | Optional | `86400` | - |
| `help_html` | help_html | HTML | Optional | `-` | - |

### DocType: `Client Script`
- **Submittable**: No
- **Total Data Fields**: 6

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `dt` | DocType | Link | ✓ Mandatory | `-` | DocType |
| `view` | Apply To | Select | Optional | `Form` | List, Form |
| `module` | Module (for export) | Link | Optional | `-` | Module Def |
| `enabled` | Enabled | Check | Optional | `0` | - |
| `script` | Script | Code | Optional | `-` | JS |
| `sample` | Sample | HTML | Optional | `-` | - |

## Module: Users & System
*Identity management, role-based access control (RBAC), user permissions, activity logs, audit trails, and system security.*

### Summary of DocTypes in Users & System:
- **User**: 78 fields | Submittable: No
- **Role**: 7 fields | Submittable: No
- **User Permission**: 7 fields | Submittable: No
- **Activity Log**: 15 fields | Submittable: No
- **Access Log**: 12 fields | Submittable: No

### DocType: `User`
- **Submittable**: No
- **Total Data Fields**: 78

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `enabled` | Enabled | Check | Optional | `1` | - |
| `email` | Email | Data | ✓ Mandatory | `-` | Email |
| `first_name` | First Name | Data | ✓ Mandatory | `-` | - |
| `middle_name` | Middle Name | Data | Optional | `-` | - |
| `last_name` | Last Name | Data | Optional | `-` | - |
| `full_name` | Full Name | Data | Optional | `-` | - |
| `username` | Username | Data | Optional | `-` | - |
| `language` | Language | Link | Optional | `-` | Language |
| `time_zone` | Time Zone | Autocomplete | Optional | `-` | - |
| `send_welcome_email` | Send Welcome Email | Check | Optional | `1` | - |
| `unsubscribed` | Unsubscribed | Check | Optional | `0` | - |
| `user_image` | User Image | Attach Image | Optional | `-` | - |
| `role_profile_name` | Role Profile | Link | Optional | `-` | Role Profile |
| `role_profiles` | Role Profiles | Table MultiSelect | Optional | `-` | User Role Profile |
| `roles_html` | Roles HTML | HTML | Optional | `-` | - |
| `roles` | Roles Assigned | Table | Optional | `-` | Has Role |
| `module_profile` | Module Profile | Link | Optional | `-` | Module Profile |
| `modules_html` | Modules HTML | HTML | Optional | `-` | - |
| `block_modules` | Block Modules | Table | Optional | `-` | Block Module |
| `home_settings` | Home Settings | Code | Optional | `-` | - |
| `gender` | Gender | Link | Optional | `-` | Gender |
| `birth_date` | Birth Date | Date | Optional | `-` | - |
| `interest` | Interests | Small Text | Optional | `-` | - |
| `phone` | Phone | Data | Optional | `-` | Phone |
| `location` | Location | Data | Optional | `-` | - |
| `bio` | Bio | Small Text | Optional | `-` | - |
| `mobile_no` | Mobile No | Data | Optional | `-` | Phone |
| `mute_sounds` | Mute Sounds | Check | Optional | `0` | - |
| `desk_theme` | Desk Theme | Select | Optional | `-` | Light, Dark, Automatic |
| `code_editor_type` | Code Editor Type | Select | Optional | `vscode` | vscode, vim, emacs |
| `banner_image` | Banner Image | Attach Image | Optional | `-` | - |
| `search_bar` | Search Bar | Check | Optional | `1` | - |
| `notifications` | Notifications | Check | Optional | `1` | - |
| `list_sidebar` | Sidebar | Check | Optional | `1` | - |
| `bulk_actions` | Bulk Actions | Check | Optional | `1` | - |
| `view_switcher` | View Switcher | Check | Optional | `1` | - |
| `form_sidebar` | Sidebar | Check | Optional | `1` | - |
| `form_navigation_buttons` | Navigation Buttons | Check | Optional | `1` | - |
| `timeline` | Timeline | Check | Optional | `1` | - |
| `dashboard` | Dashboard | Check | Optional | `1` | - |
| `show_absolute_datetime_in_timeline` | Show Absolute Datetime in Timeline | Check | Optional | `0` | - |
| `new_password` | Set New Password | Password | Optional | `-` | - |
| `logout_all_sessions` | Logout From All Devices After Changing Password | Check | Optional | `1` | - |
| `reset_password_key` | Reset Password Key | Data | Optional | `-` | - |
| `last_reset_password_key_generated_on` | Last Reset Password Key Generated On | Datetime | Optional | `-` | - |
| `last_password_reset_date` | Last Password Reset Date | Date | Optional | `-` | - |
| `redirect_url` | Redirect URL | Small Text | Optional | `-` | - |
| `document_follow_notify` | Send Notifications For Documents Followed By Me | Check | Optional | `0` | - |
| `document_follow_frequency` | Frequency | Select | Optional | `Daily` | Hourly, Daily, Weekly |
| `follow_created_documents` | Auto follow documents that you create | Check | Optional | `0` | - |
| `follow_commented_documents` | Auto follow documents that you comment on | Check | Optional | `0` | - |
| `follow_liked_documents` | Auto follow documents that you Like | Check | Optional | `0` | - |
| `follow_assigned_documents` | Auto follow documents that are assigned to you | Check | Optional | `0` | - |
| `follow_shared_documents` | Auto follow documents that are shared with you | Check | Optional | `0` | - |
| `email_signature` | Email Signature | Text Editor | Optional | `-` | - |
| `thread_notify` | Send Notifications For Email Threads | Check | Optional | `1` | - |
| `send_me_a_copy` | Send Me A Copy of Outgoing Emails | Check | Optional | `0` | - |
| `allowed_in_mentions` | Allowed In Mentions | Check | Optional | `1` | - |
| `user_emails` | User Emails | Table | Optional | `-` | User Email |
| `default_workspace` | Default Workspace | Link | Optional | `-` | Workspace |
| `default_app` | Default App | Select | Optional | `-` | - |
| `defaults` | User Defaults | Table | Optional | `-` | DefaultValue |
| `simultaneous_sessions` | Simultaneous Sessions | Int | Optional | `2` | - |
| `restrict_ip` | Restrict IP | Small Text | Optional | `-` | - |
| `last_ip` | Last IP | Read Only | Optional | `-` | - |
| `login_after` | Login After | Int | Optional | `-` | - |
| `user_type` | User Type | Link | Optional | `System User` | User Type |
| `last_active` | Last Active | Datetime | Optional | `-` | - |
| `login_before` | Login Before | Int | Optional | `-` | - |
| `bypass_restrict_ip_check_if_2fa_enabled` | Bypass Restricted IP Address Check If Two Factor Auth Enabled | Check | Optional | `0` | - |
| `last_login` | Last Login | Read Only | Optional | `-` | - |
| `last_known_versions` | Last Known Versions | Text | Optional | `-` | - |
| `social_logins` | Social Logins | Table | Optional | `-` | User Social Login |
| `api_key` | API Key | Data | Optional | `-` | - |
| `generate_keys` | Generate Keys | Button | Optional | `-` | - |
| `api_secret` | API Secret | Password | Optional | `-` | - |
| `onboarding_status` | Onboarding Status | Small Text | Optional | `{}` | - |
| `active_sessions` | Active Sessions | Table | Optional | `-` | User Session Display |

### DocType: `Role`
- **Submittable**: No
- **Total Data Fields**: 7

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `role_name` | Role Name | Data | ✓ Mandatory | `-` | - |
| `home_page` | Home Page | Data | Optional | `-` | - |
| `restrict_to_domain` | Restrict To Domain | Link | Optional | `-` | Domain |
| `disabled` | Disabled | Check | Optional | `0` | - |
| `is_custom` | Is Custom | Check | Optional | `0` | - |
| `desk_access` | Desk Access | Check | Optional | `1` | - |
| `two_factor_auth` | Two Factor Authentication | Check | Optional | `0` | - |

### DocType: `User Permission`
- **Submittable**: No
- **Total Data Fields**: 7

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `user` | User | Link | ✓ Mandatory | `-` | User |
| `allow` | Allow | Link | ✓ Mandatory | `-` | DocType |
| `for_value` | For Value | Dynamic Link | ✓ Mandatory | `-` | allow |
| `is_default` | Is Default | Check | Optional | `0` | - |
| `apply_to_all_doctypes` | Apply To All Document Types | Check | Optional | `1` | - |
| `applicable_for` | Applicable For | Link | Optional | `-` | DocType |
| `hide_descendants` | Hide Descendants | Check | Optional | `0` | - |

### DocType: `Activity Log`
- **Submittable**: No
- **Total Data Fields**: 15

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `subject` | Subject | Small Text | ✓ Mandatory | `-` | - |
| `content` | Message | Text Editor | Optional | `-` | - |
| `communication_date` | Date | Datetime | Optional | `Now` | - |
| `ip_address` | IP Address | Data | Optional | `-` | - |
| `operation` | Operation | Select | Optional | `-` | Login, Logout, Impersonate |
| `status` | Status | Select | Optional | `-` | Success, Failed, Linked, Closed |
| `reference_doctype` | Reference Document Type | Link | Optional | `-` | DocType |
| `reference_name` | Reference Name | Dynamic Link | Optional | `-` | reference_doctype |
| `reference_owner` | Reference Owner | Read Only | Optional | `-` | - |
| `timeline_doctype` | Timeline DocType | Link | Optional | `-` | DocType |
| `timeline_name` | Timeline Name | Dynamic Link | Optional | `-` | timeline_doctype |
| `link_doctype` | Link DocType | Link | Optional | `-` | DocType |
| `link_name` | Link Name | Dynamic Link | Optional | `-` | link_doctype |
| `user` | User | Link | Optional | `__user` | User |
| `full_name` | Full Name | Data | Optional | `-` | - |

### DocType: `Access Log`
- **Submittable**: No
- **Total Data Fields**: 12

| Fieldname | Label | Fieldtype | Mandatory | Default | Target Options / Choices |
|---|---|---|---|---|---|
| `export_from` | Export From | Data | Optional | `-` | - |
| `user` | User | Link | Optional | `-` | User |
| `show_document` | Show Document | Button | Optional | `-` | - |
| `reference_document` | Reference Document | Data | Optional | `-` | - |
| `timestamp` | Timestamp | Datetime | Optional | `Now` | - |
| `file_type` | File Type | Data | Optional | `-` | - |
| `method` | Method | Data | Optional | `-` | - |
| `report_name` | Report Name | Data | Optional | `-` | - |
| `filters` | Filters | Code | Optional | `-` | - |
| `show_report` | Show Report | Button | Optional | `-` | - |
| `page` | HTML Page | HTML Editor | Optional | `-` | - |
| `columns` | Columns / Fields | HTML Editor | Optional | `-` | - |
