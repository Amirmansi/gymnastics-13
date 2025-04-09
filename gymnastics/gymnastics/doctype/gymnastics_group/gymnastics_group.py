# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate,today,add_days
from frappe import _
from frappe.model.mapper import get_mapped_doc


class GymnasticsGroup(Document):
	def validate(self):
		self.validate_trainee()

	def validate_trainee(self):
		for row in self.trainees:
			trainee_res = frappe.db.sql("""select name from `tabGroup Trainee Details` where name<>%s and trainee=%s and parent=%s""",(row.name,row.trainee,row.parent),as_dict=1)
			if len(trainee_res) >= 1:
				frappe.throw(_("Duplicate Trainee {0} In Group").format(row.trainee))

	def add_dates_from_day(self):
		self.schedules = []
		from_date = self.from_date
		to_date = self.to_date
		selected_days = self.selected_days()
		while from_date <= to_date:
			day_name = getdate(from_date).strftime('%A')
			if day_name in selected_days:
				self.append("schedules",dict(
					date = from_date,
					day = day_name,
					active = 1
				))
			from_date = add_days(from_date,1)

	def selected_days(self):
		days = []
		if self.sunday:
			days.append("Sunday")
		if self.monday:
			days.append("Monday")
		if self.tuesday:
			days.append("Tuesday")
		if self.wednesday:
			days.append("Wednesday")
		if self.thursday:
			days.append("Thursday")
		if self.friday:
			days.append("Friday")
		if self.saturday:
			days.append("Saturday")
		return days


@frappe.whitelist()
def schedule(source_name):
	# frappe.publish_realtime('enroll_student_progress', {"progress": [1, 4]}, user=frappe.session.user)
	trainee = get_mapped_doc("Gymnastics Group", source_name,
		{"Gymnastics Group": {
			"doctype": "Group Schedule",
			"field_map": {
				"name": "group"
			}
		}}, ignore_permissions=True)
	return trainee