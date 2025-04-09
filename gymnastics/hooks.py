from . import __version__ as app_version

app_name = "gymnastics"
app_title = "Gymnastics"
app_publisher = "Bhavesh Maheshwari"
app_description = "Manage all gym related features"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "maheshwaribhavesh95863@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/gymnastics/css/gymnastics.css"
# app_include_js = "/assets/gymnastics/js/gymnastics.js"

# include js, css files in header of web template
# web_include_css = "/assets/gymnastics/css/gymnastics.css"
# web_include_js = "/assets/gymnastics/js/gymnastics.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "gymnastics/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"doctype" : "public/js/holiday_list.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "gymnastics.install.before_install"
# after_install = "gymnastics.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "gymnastics.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": {
		"validate": "gymnastics.api.validate_session_items",
		"on_submit": "gymnastics.api.on_submit_invoice"
	},
	"POS Invoice": {
		"on_submit": "gymnastics.api.on_submite_pos_invoice"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"gymnastics.api.update_group_for_expired_schedule"
	]
}

# Testing
# -------

# before_tests = "gymnastics.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "gymnastics.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "gymnastics.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["name", "in", [
				"Sales Invoice-gymnastics_details",
				"Sales Invoice-gymnastics_invoice",
				"Sales Invoice-program",
				"Sales Invoice-trainee",
				"Sales Invoice-gym_cm1",
				"Sales Invoice-course",
				"Sales Invoice-course_from_date",
				"Sales Invoice-gym_col_2",
				"Sales Invoice-group",
				"Sales Invoice-course_to_date",
				"Sales Invoice-course_start_date",
				"Sales Invoice-extend_plan",
				"Sales Invoice-renew_plan",
				"Sales Invoice-applicable_from_date",
				"Sales Invoice-trainee_course_schedule"
            ]]
        ]
    },
    {
        "dt": "Property Setter",
        "filters": [
            ["name", "in", [
                "Sales Invoice-update_stock-hidden"
			]]
        ]
    },
    {
        "dt": "Client Script",
        "filters": [
            ["name", "in", [
                "Sales Invoice-Form",
				"Holiday List-Form"
			]]
        ]
    }
]

# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"gymnastics.auth.validate"
# ]

