# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from gymnastics.gymnastics.doctype.trainee_enrollment.trainee_enrollment import (
    update_trainee_schedule,
)
from frappe.utils import today, cstr, add_days, getdate


class TraineeFreezeRequest(Document):
    def on_submit(self):
        filters = [["trainee", "=", self.trainee]]
        trainee_schedule = frappe.get_all(
            "Trainee Course Schedule", filters=filters, fields=["name"]
        )
        freeze_date = []
        from_date = self.from_date
        while from_date <= self.to_date:
            freeze_date.append(cstr(from_date))
            from_date = add_days(from_date, 1)
        for row in trainee_schedule:
            schedule_doc = frappe.get_doc("Trainee Course Schedule", row.name)
            update_trainee_schedule(schedule_doc, freeze_date, from_date=self.from_date)

    def on_cancel(self):
        filters = [["trainee", "=", self.trainee]]
        trainee_schedule = frappe.get_all(
            "Trainee Course Schedule", filters=filters, fields=["name"]
        )
        for row in trainee_schedule:
            schedule_doc = frappe.get_doc("Trainee Course Schedule", row.name)
            update_trainee_schedule(schedule_doc)

    @frappe.whitelist()
    def get_schedule_between_date(self):
        self.schedules = []
        schedules = frappe.db.sql(
            """SELECT c.date AS 'schedule_date',
       c.day AS 'day',
       p.course AS 'course',
       p.group AS 'group'
FROM `tabTrainee Course Schedule Details` AS c
INNER JOIN `tabTrainee Course Schedule` AS p ON c.parent=p.name
WHERE c.date BETWEEN %s AND %s
  AND p.trainee=%s AND p.group=%s""",
            (self.from_date, self.to_date, self.trainee, self.trainee_group),
            as_dict=1,
        )
        for row in schedules:
            # if not getdate(today()) == getdate(row.get("schedule_date")):
            # continue
            self.append("schedules", row)
