# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from gymnastics.gymnastics.doctype.trainee_enrollment.trainee_enrollment import update_trainee_schedule,update_trainee_schedule_freeze_group
from frappe.utils import getdate
from frappe import _

class GroupFreeze(Document):
	def on_submit(self):
		filters = [
			["group","=",self.group]
		]
		frappe.errprint('call siubmit')
		trainee_schedule = frappe.get_all("Group Schedule",filters=filters,fields=["name"])
		updated_group = []
		for row in trainee_schedule:
			group_doc = frappe.get_doc("Group Schedule",row.name)
			update = False
			for schedule_date in group_doc.schedules:
				for row_f in self.group_freeze_details:
					if getdate(row_f.schedule_date) == getdate(schedule_date.date):
						schedule_date.active = 0
						schedule_date.freeze = 1
						update = True
			if update:
				group_doc.save()
				updated_group.append(group_doc.group)
		filters = [
			["group","in",updated_group]
		]
		freeze_date = [row_f.schedule_date for  row_f in self.group_freeze_details]
		trainee_schedule = frappe.get_all("Trainee Course Schedule",filters=filters,fields=["name"])
		frappe.errprint(trainee_schedule)
		for t_s in trainee_schedule:
			trainee_schedule_doc = frappe.get_doc("Trainee Course Schedule",t_s.name)
			update_trainee_schedule_freeze_group(trainee_schedule_doc,freeze_date)
		frappe.msgprint(_("Group Schedule Updated"))

	def on_cancel(self):
		filters = [
			["group","=",self.group]
		]
		trainee_schedule = frappe.get_all("Group Schedule",filters=filters,fields=["name"])
		updated_group = []
		for row in trainee_schedule:
			group_doc = frappe.get_doc("Group Schedule",row.name)
			update = False
			for schedule_date in group_doc.schedules:
				for row_f in self.group_freeze_details:
					if getdate(row_f.schedule_date) == getdate(schedule_date.date) and schedule_date.freeze:
						schedule_date.active = 1
						schedule_date.freeze = 0
						update = True
			if update:
				group_doc.save()
				updated_group.append(group_doc.group)
		filters = [
			["group","in",updated_group]
		]
		trainee_schedule = frappe.get_all("Trainee Course Schedule",filters=filters,fields=["name"])
		for t_s in trainee_schedule:
			trainee_schedule_doc = frappe.get_doc("Trainee Course Schedule",t_s.name)
			update_trainee_schedule(trainee_schedule_doc)
		frappe.msgprint(_("Group Schedule Updated"))
			

	@frappe.whitelist()
	def get_schedule_between_date(self):
		self.group_freeze_details = []
		schedules = frappe.db.sql("""select c.date as 'schedule_date',c.day as 'day' from `tabGroup Schedule Details` as c inner join `tabGroup Schedule` as p on c.parent=p.name where c.date between %s and %s and p.group=%s""",(self.from_date,self.to_date,self.group),as_dict=1)
		for row in schedules:
			self.append("group_freeze_details",row)

