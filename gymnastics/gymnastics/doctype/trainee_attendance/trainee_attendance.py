# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate

class TraineeAttendance(Document):
	def validate(self):
		filters  = [["Group Schedule","group","=",self.trainee_group],["Group Schedule Details","date","=",self.date],["Group Schedule Details","active","=",1]]
		group_schedule = frappe.get_all("Group Schedule",filters = filters, fields=["name"])
		# group_schedule = frappe.db.sql("""select p.name from `tabGroup Schedule Details` as c inner join `tabGroup Schedule` as p on c.parent=p.name where parent=%s and c.date=%s and c.active=1""",(self.trainee_group,self.date),as_dict=1)
		if not len(group_schedule) >= 1:
			frappe.throw(_(f"Attendance Date Must Be As Per Group Schedule Date.{self.date} Is Not Available In Group Schedule"))
		attendance = frappe.db.sql("""select name from `tabTrainee Attendance` where trainee_group=%s and trainee=%s and date=%s and name<>%s""",(self.trainee_group,self.trainee,self.date,self.name),as_dict=1)
		if len(attendance) >= 1:
			frappe.throw(_(f"Already Marked Attendance For Trainee {self.trainee_name} On {self.date}"))
		
	def on_submit(self):
		trainee_schedule_id = frappe.db.get_value("Trainee Course Schedule Details",{"trainee":self.trainee,"date":self.date, "gymnastics_group":self.trainee_group},"name")
		if trainee_schedule_id:
			frappe.db.set_value("Trainee Course Schedule Details",trainee_schedule_id,"attendance",self.name)

