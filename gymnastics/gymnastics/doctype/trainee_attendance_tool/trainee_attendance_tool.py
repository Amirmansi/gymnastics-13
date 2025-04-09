# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.utils import getdate,today
from frappe import _

class TraineeAttendanceTool(Document):
	@frappe.whitelist()
	def get_group_dates(self,group):
		filters  = [
			["Group Schedule","group","=",group],
			["Group Schedule Details","active","=",1],
			["Group Schedule Details","attendance","=",0]]
		group_schedule = frappe.get_all("Group Schedule",filters = filters, fields=["name"])
		dates = []
		schedules = []
		for schedule in group_schedule:
			if not schedule.name in schedules:
				schedule_doc = frappe.get_doc("Group Schedule",schedule.name)
				for row in schedule_doc.schedules:
					if not getdate(row.get("date")) > getdate(today()) and not row.attendance and not row.freeze:
						dates.append({
							"schedule_date": row.get("date")
						})
						schedules.append(schedule.name)

		return dates



@frappe.whitelist()
def get_student_attendance_records(date=None, group=None):
	student_list = []
	student_attendance_list = []

	if not student_list:
		# student_list = frappe.get_all(
		# 	"Group Trainee Details",
		# 	fields=["trainee", "trainee_name"],
		# 	filters={"parent": group}
		# )
		student_list = frappe.db.sql("""select trainee,trainee_name from `tabTrainee Course Schedule Details` where gymnastics_group=%s and date=%s and trainee is not null""",(group,date),as_dict=True)

	TraineeAttendance = frappe.qb.DocType("Trainee Attendance")

	# if course_schedule:
	# 	student_attendance_list = (
	# 		frappe.qb.from_(StudentAttendance)
	# 		.select(StudentAttendance.student, StudentAttendance.status)
	# 		.where((StudentAttendance.course_schedule == course_schedule))
	# 	).run(as_dict=True)
	# else:
	student_attendance_list = (
		frappe.qb.from_(TraineeAttendance)
		.select(TraineeAttendance.trainee, TraineeAttendance.status)
		.where(
			(TraineeAttendance.trainee_group == group)
			& (TraineeAttendance.date == date)
		)
	).run(as_dict=True)

	for attendance in student_attendance_list:
		for student in student_list:
			if student.trainee == attendance.trainee:
				student.status = attendance.status

	return student_list

@frappe.whitelist()
def mark_attendance(
	students_present, students_absent,group=None, date=None
):
	"""Creates Multiple Attendance Records.
	:param students_present: Students Present JSON.
	:param students_absent: Students Absent JSON.
	:param course_schedule: Course Schedule.
	:param student_group: Student Group.
	:param date: Date.
	"""

	# if group:
	# 	academic_year = frappe.db.get_value("Student Group", group, "academic_year")
	# 	if academic_year:
	# 		year_start_date, year_end_date = frappe.db.get_value(
	# 			"Academic Year", academic_year, ["year_start_date", "year_end_date"]
	# 		)
	# 		if getdate(date) < getdate(year_start_date) or getdate(date) > getdate(year_end_date):
	# 			frappe.throw(
	# 				_("Attendance cannot be marked outside of Academic Year {0}").format(academic_year)
	# 			)

	present = json.loads(students_present)
	absent = json.loads(students_absent)
	for d in present:
		make_attendance_records(
			d["trainee"], d["trainee_name"], "Present",group, date
		)

	for d in absent:
		make_attendance_records(
			d["trainee"], d["trainee_name"], "Absent",group, date
		)
	# s_id = frapppe.db.get_value("Group Schedule Details",{""})
	frappe.db.sql("""update `tabGroup Schedule Details`,`tabGroup Schedule` set `tabGroup Schedule Details`.attendance=1  where `tabGroup Schedule Details`.parent=`tabGroup Schedule`.name and `tabGroup Schedule`.group=%s and `tabGroup Schedule Details`.date=%s""",(group,date),debug=1)

	# frappe.db.sql("""update `tabGroup Schedule Details` set attendance=1 where parent=%s and date=%s""",(group,date),debug=1)
	frappe.db.commit()
	frappe.msgprint(_("Attendance has been marked successfully."))


def make_attendance_records(
	trainee, trainee_name, status, group=None, date=None
):
	"""Creates/Update Attendance Record.
	:param student: Student.
	:param student_name: Student Name.
	:param course_schedule: Course Schedule.
	:param status: Status (Present/Absent)
	"""
	student_attendance = frappe.get_doc(
		{
			"doctype": "Trainee Attendance",
			"trainee": trainee,
			"trainee_name": trainee_name,
			"trainee_group": group,
			"date": date,
		}
	)
	if not student_attendance:
		student_attendance = frappe.new_doc("Trainee Attendance")
	student_attendance.trainee = trainee
	student_attendance.trainee_name = trainee_name
	student_attendance.trainee_group = group
	student_attendance.date = date
	student_attendance.status = status
	student_attendance.save()
	student_attendance.submit()