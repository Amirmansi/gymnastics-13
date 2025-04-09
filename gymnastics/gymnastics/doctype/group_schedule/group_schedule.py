# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from email.utils import format_datetime
import json
from socket import fromfd
import frappe
from frappe.model.document import Document
from frappe.utils import getdate,today,add_days,get_time,get_datetime,cstr
from frappe import _
from gymnastics.gymnastics.doctype.trainee_enrollment.trainee_enrollment import update_trainee_schedule_for_transfer

class GroupSchedule(Document):
	def validate(self):
		self.validate_days()
		self.duplicate_schedule()

	def duplicate_schedule(self):
		schedules = frappe.db.sql("""select name from `tabGroup Schedule` where `tabGroup Schedule`.group=%s and name<>%s""",(self.group,self.name),as_dict=1)
		if len(schedules) >= 1:
			frappe.throw(_("Group Schedule Already Exists For Selected Group"))

	
	def validate_days(self):
		selected_days = self.selected_days()
		for row in self.schedules:
			if not row.day == getdate(row.date).strftime('%A'):
				frappe.throw(_("Row{0}: Day Must Match With Date of Day"))
			if not row.day in selected_days:
				if getdate(row.date) > getdate(today()):
					days = ",".join(selected_days)
					frappe.throw(_("Row{1}:Only {0} Allowed".format(days,row.idx)))
			row.group = self.group
			row.from_datetime = get_datetime(cstr(row.date)+ ' ' + cstr(row.from_time))
			row.to_datetime = get_datetime(cstr(row.date)+ ' ' + cstr(row.to_time))

	def on_update(self):
		# self.update_schedule_time_in_trainee()
		self.update_trainee_schedule()

	# def update_schedule_time_in_trainee(self):
	# 	if self.from_time and self.to_time:
	# 		filters = [
	# 			["Trainee Course Schedule Details","date",">=",today()],
	# 			["Trainee Course Schedule Details","gymnastics_group","=",self.group],
	# 		]
	# 		schedules = frappe.get_all("Trainee Course Schedule",filters=filters,fields=["name"],group_by="name")
	# 		for schedule in schedules:
	# 			schedule_doc = frappe.get_doc("Trainee Course Schedule",schedule.name)
	# 			for row in schedule_doc.trainee_course_schedule_details:
	# 				if row.gymnastics_group == self.group:
	# 					row.from_time = get_time(row.from_time)
	# 					row.to_time = get_time(row.to_time)
	# 			schedule_doc.save()

	def update_trainee_schedule(self):
		# if self.from_time and self.to_time:
		filters = [
			["Trainee Course Schedule Details","date",">=",today()],
			["Trainee Course Schedule Details","gymnastics_group","=",self.group],
		]
		schedules = frappe.get_all("Trainee Course Schedule",filters=filters,fields=["name"],group_by="name")
		for schedule in schedules:
			schedule_doc = frappe.get_doc("Trainee Course Schedule",schedule.name)
			update_trainee_schedule_for_transfer(schedule_doc,today())

	@frappe.whitelist()
	def add_dates_from_day(self):
		old_schedules = self.schedules
		self.schedules = []
		last_date = ''
		for sc_row in old_schedules:
			if getdate(sc_row.date) <= getdate(today()):
				if not last_date == '':
					if getdate(last_date) < getdate(sc_row.date):
						last_date = sc_row.date
				else:
					last_date = sc_row.date
				self.append("schedules",sc_row)
		selected_days = self.selected_days()
		for row in self.group_schedule_time:
			from_date = row.from_date
			to_date = row.to_date
			while from_date <= to_date:
				day_name = getdate(from_date).strftime('%A')
				if not last_date == '':
					if getdate(from_date) > getdate(last_date):
						if day_name in selected_days:
							self.append("schedules",dict(
								date = from_date,
								day = day_name,
								active = 1,
								from_time = row.from_time,
								to_time = row.to_time
							))
				else:
					if day_name in selected_days:
						self.append("schedules",dict(
							date = from_date,
							day = day_name,
							active = 1,
							from_time = row.from_time,
							to_time = row.to_time
						))				
				from_date = add_days(from_date,1)
		self.save()
		# self.update_trainee_schedule()

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
def get_schedules(start, end, filters=None):
	events = []
	filters = json.loads(filters)
	conditions = ""
	conditions += " from_datetime between '{0}' and '{1}'".format(start,end)
	conditions += " and to_datetime between '{0}' and '{1}'".format(start,end)
	schedules = frappe.db.sql("""SELECT parent as 'name',`tabGroup Schedule Details`.group as 'group',from_datetime,to_datetime 
		FROM `tabGroup Schedule Details` where {0}""".format(conditions),as_dict=1,debug=1)
	frappe.errprint(schedules)
	return schedules
	# for d in job_cards:
	# 		subject_data = []
	# 		for field in ["name", "work_order", "remarks", "employee_name"]:
	# 			if not d.get(field): continue

	# 			subject_data.append(d.get(field))

	# 		color = event_color.get(d.status)
	# 		job_card_data = {
	# 			'from_time': d.from_time,
	# 			'to_time': d.to_time,
	# 			'name': d.name,
	# 			'subject': '\n'.join(subject_data),
	# 			'color': color if color else "#89bcde"
	# 		}

	# 		events.append(job_card_data)

	return events