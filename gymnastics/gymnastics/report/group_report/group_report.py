# Copyright (c) 2013, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from dataclasses import field
from time import time
import frappe
from frappe import _
from frappe.utils import cstr, get_time, getdate, today
import copy


def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    max_columns = 1
    for row in data:
        group_doc = frappe.get_doc("Gymnastics Group", row.group_name_id)
        if len(group_doc.trainees) > max_columns:
            for x in range(max_columns, len(group_doc.trainees)):
                columns.append(_("Trainee") + " " + _(cstr(x)) + ":Data:300")
            max_columns = len(group_doc.trainees)
        count = 1
        for t_row in group_doc.trainees:
            expire_date, remain_session = get_expire_details(
                row.group_name_id, t_row.trainee
            )
            trainee_arabic_name = frappe.db.get_value(
                "Trainee", t_row.trainee, "trainee_name_ar"
            )
            color = "black"
            frappe.errprint(remain_session)
            frappe.errprint(expire_date)
            if remain_session <= 2:
                color = "red"
            elif remain_session <= 5:
                color = "green"
            else:
                color = "black"
            row[
                "trainee_" + cstr(count)
            ] = '<span style="color:{2}">{0}</span> / {1}'.format(
                trainee_arabic_name, expire_date, color
            )
            count += 1
        row["number_of_trainee"] = len(group_doc.trainees)
    frappe.errprint(data)
    return columns, data


def get_expire_details(group, trainee):
    data = frappe.db.sql(
        """select date from `tabTrainee Course Schedule Details` where gymnastics_group=%s and trainee=%s order by date asc""",
        (group, trainee),
        as_dict=1,
    )
    frappe.errprint("data")
    frappe.errprint(data)
    max_date = ""
    remain_session = 0
    for row in data:
        if getdate(row.date) > getdate(today()):
            remain_session += 1
        if max_date == "":
            max_date = row.date
            continue
        if getdate(max_date) < getdate(row.date):
            max_date = row.date
    return max_date, remain_session


def get_columns(filters):
    return [
        _("Program Name") + ":Link/Gymnastics Program:120",
        _("Course Name") + ":Link/Gymnastics Course:200",
        _("Group Name") + ":Data:100",
        _("Age Group") + ":Data:120",
        _("Skills Type") + ":Data:120",
        _("Color") + ":Data:120",
        _("Days") + ":Data:120",
        _("From Time") + "::60",
        _("To Time") + "::60",
        _("Coach Name") + ":Data:120",
        _("Number of trainee") + ":Int:120",
    ]


def get_data(filters):
    data = []
    course_details = frappe.db.sql(
        """select name,course_name,program as program_name from `tabGymnastics Course`""",
        as_dict=1,
    )
    for row in course_details:
        group_details = frappe.db.sql(
            """select name,group_name,age_group,skills_type,group_color,coach_name,disable from `tabGymnastics Group` where course=%s""",
            row.name,
            as_dict=1,
        )
        frappe.errprint(group_details)
        for group_row in group_details:
            if int(filters.get("remove_disable_group")) == 1:
                if int(group_row.get("disable")) == 1:
                    frappe.errprint("skip group {0}".format(group_row.group_name))
                    continue
            frappe.errprint(group_row.name)
            d_row = copy.deepcopy(row)
            d_row["group_name"] = group_row.group_name
            d_row["group_name_id"] = group_row.name
            d_row["skills_type"] = group_row.skills_type
            d_row["color"] = group_row.group_color
            d_row["age_group"] = group_row.age_group
            d_row["coach_name"] = group_row.coach_name
            frappe.errprint(d_row)
            get_group_schedule(group_row.name, row=d_row)
            data.append(d_row)
    frappe.errprint(data)
    return data


def get_group_schedule(group, row):
    from datetime import datetime

    group_details = frappe.get_all(
        "Group Schedule",
        filters={"group": group},
        fields=["name"],
        order_by="creation desc",
        limit=1,
    )
    if len(group_details) >= 1:
        group_doc = frappe.get_doc("Group Schedule", group_details[0].name)
        if len(group_doc.group_schedule_time) >= 1:
            row["from_time"] = group_doc.group_schedule_time[
                len(group_doc.group_schedule_time) - 1
            ].get("from_time")
            row["to_time"] = group_doc.group_schedule_time[
                len(group_doc.group_schedule_time) - 1
            ].get("to_time")
            if row["from_time"]:
                if get_time("11:59:59") < get_time(row["from_time"]):
                    time = datetime.strptime(cstr(row["from_time"]), "%H:%M:%S")
                    row["from_time"] = time.strftime("%I:%M %p")
                else:
                    time = datetime.strptime(cstr(row["from_time"]), "%H:%M:%S")
                    row["from_time"] = time.strftime("%I:%M %p")
            if row["to_time"]:
                if get_time("11:59:59") < get_time(row["to_time"]):
                    time = datetime.strptime(cstr(row["to_time"]), "%H:%M:%S")
                    row["to_time"] = time.strftime("%I:%M %p")
                else:
                    time = datetime.strptime(cstr(row["to_time"]), "%H:%M:%S")
                    row["to_time"] = time.strftime("%I:%M %p")
        else:
            row["from_time"] = ""
            row["to_time"] = ""
        days_str = ""
        if group_doc.sunday:
            days_str += "Sunday"
        if group_doc.monday:
            if not days_str == "":
                days_str += ","
            days_str += "Monday"
        if group_doc.tuesday:
            if not days_str == "":
                days_str += ","
            days_str += "Tuesday"
        if group_doc.wednesday:
            if not days_str == "":
                days_str += ","
            days_str += "Wednesday"
        if group_doc.thursday:
            if not days_str == "":
                days_str += ","
            days_str += "Thursday"
        if group_doc.friday:
            if not days_str == "":
                days_str += ","
            days_str += "Friday"
        if group_doc.saturday:
            if not days_str == "":
                days_str += ","
            days_str += "Saturday"
        row["days"] = days_str
    else:
        row["from_time"] = ""
        row["to_time"] = ""
        row["days"] = "-"
