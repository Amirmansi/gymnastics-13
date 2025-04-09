# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.email.doctype.email_group.email_group import add_subscribers
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cstr, flt, getdate
from frappe.model.document import Document


class TraineeApplicant(Document):
	pass

@frappe.whitelist()
def create_trainee(source_name):
	# frappe.publish_realtime('enroll_student_progress', {"progress": [1, 4]}, user=frappe.session.user)
	trainee = get_mapped_doc("Trainee Applicant", source_name,
		{"Trainee Applicant": {
			"doctype": "Trainee",
			"field_map": {
				"name": "trainee_applicant"
			}
		}}, ignore_permissions=True)
	return trainee

	# student_applicant = frappe.db.get_value("Student Applicant", source_name,
	# 	["student_category", "program"], as_dict=True)
	# program_enrollment = frappe.new_doc("Program Enrollment")
	# program_enrollment.student = student.name
	# program_enrollment.student_category = student_applicant.student_category
	# program_enrollment.student_name = student.title
	# program_enrollment.program = student_applicant.program
	# frappe.publish_realtime('enroll_student_progress', {"progress": [2, 4]}, user=frappe.session.user)
	# return program_enrollment