# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class TraineeCourseSchedule(Document):
	def validate(self):
		for row in self.trainee_course_schedule_details:
			row.trainee = self.trainee
			row.trainee_name = self.trainee_name



@frappe.whitelist()
def create_extend_invoice(source_name):
	try:
		trainee_schedule = frappe.get_doc("Trainee Course Schedule",source_name)

		invoice = get_mapped_doc("Trainee Course Schedule", source_name,
			{"Trainee Course Schedule": {
				"doctype": "Sales Invoice",
				"field_map": {
					"trainee": "trainee"
				}
			}}, ignore_permissions=True)
		invoice.customer = frappe.db.get_value("Trainee",trainee_schedule.trainee,"customer")
		invoice.extend = 1
		return invoice
	except Exception as e:
		frappe.log_error(frappe.get_traceback())


@frappe.whitelist()
def create_renew_invoice(source_name):
	try:
		trainee_schedule = frappe.get_doc("Trainee Course Schedule",source_name)

		invoice = get_mapped_doc("Trainee Course Schedule", source_name,
			{"Trainee Course Schedule": {
				"doctype": "Sales Invoice",
				"field_map": {
					"trainee": "trainee"
				}
			}}, ignore_permissions=True)
		# invoice.customer = frappe.db.get_value("Trainee",trainee_schedule.trainee,"customer")
		invoice.extend = 1
		return invoice
	except Exception as e:
		frappe.log_error(frappe.get_traceback())

