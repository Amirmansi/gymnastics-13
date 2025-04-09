# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from gymnastics.gymnastics.doctype.trainee_enrollment.trainee_enrollment import update_trainee_schedule

class GymnasticsLeave(Document):
	def on_submit(self):
		groups = frappe.get_all("Gymnastics Group",filters={"group_coach":self.coach},fields=["name"])
		for row in groups:
			group_doc = frappe.get_doc("Gymnastics Group",row.name)
			for trainee in group_doc.trainees:
				filters = [
					["trainee","=",trainee.trainee]
				]
				trainee_schedule = frappe.get_all("Trainee Course Schedule",filters=filters,fields=["name"])
				for row in trainee_schedule:
					schedule_doc = frappe.get_doc("Trainee Course Schedule",row.name)
					update_trainee_schedule(schedule_doc)

