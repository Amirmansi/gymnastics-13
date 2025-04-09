# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.email.doctype.email_group.email_group import add_subscribers
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cstr, flt, getdate, today
from frappe.model.document import Document

class Trainee(Document):
	def validate(self):
		self.validate_fields()
	
	def validate_fields(self):
		if self.mobile and not len(self.mobile) == 10:
			frappe.throw("Mobile must be in 10 digit")
		if self.national_id and not len(self.national_id) == 10:
			frappe.throw("National Id Must be in 10 digit")

	def before_insert(self):
		self.create_customer()
	
	def create_customer(self):
		cust_doc = frappe.new_doc("Customer")
		cust_doc.customer_name = self.trainee_name
		cust_doc.customer_type = "Individual"
		cust_doc.customer_group = "Trainee"
		cust_doc.territory = "Saudi Arabia"
		res = cust_doc.insert(ignore_permissions = True)
		self.customer = res.name


@frappe.whitelist()
def enrollment(source_name):
	# frappe.publish_realtime('enroll_student_progress', {"progress": [1, 4]}, user=frappe.session.user)
	trainee = get_mapped_doc("Trainee", source_name,
		{"Trainee": {
			"doctype": "Trainee Enrollment",
			"field_map": {
				"name": "trainee"
			}
		}}, ignore_permissions=True)
	return trainee


@frappe.whitelist()
def create_invoice(source_name):
	# frappe.publish_realtime('enroll_student_progress', {"progress": [1, 4]}, user=frappe.session.user)
	trainee = get_mapped_doc("Trainee", source_name,
		{"Trainee": {
			"doctype": "Sales Invoice",
			"field_map": {
				"name": "trainee",
				"customer":"customer"
			}
		}}, ignore_permissions=True)
	trainee.customer_name_in_arabic = frappe.db.get_value("Trainee",source_name,"trainee_name_ar")
	trainee.apply_discount_on = "Net Total"
	return trainee

@frappe.whitelist()
def enrollment_from_invoice(source_name):
	# frappe.publish_realtime('enroll_student_progress', {"progress": [1, 4]}, user=frappe.session.user)
	doc = frappe.get_doc("Sales Invoice",source_name)
	invoice = get_mapped_doc("Sales Invoice", source_name,
		{"Sales Invoice": {
			"doctype": "Trainee Enrollment",
			"field_map": {
				"trainee": "trainee",
				"name": "invoice_no"
			}
		}}, ignore_permissions=True)
	invoice.enrollment_date = today()
	invoice.frequency = get_items_session(doc.items[0].item_code,doc.course)
	invoice.course_amount = doc.items[0].amount
	return invoice

def get_items_session(item,course):
	return frappe.db.get_value("Gymnastics Course Amount",{"item":item,"parent":course},"frequency")
