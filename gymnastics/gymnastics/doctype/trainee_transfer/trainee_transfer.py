# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from gymnastics.gymnastics.doctype.trainee_enrollment.trainee_enrollment import update_trainee_schedule, update_trainee_schedule_freeze_group, update_trainee_schedule_for_transfer,create_entry_in_group,remove_entry_in_group
from frappe.utils import getdate, cstr
from frappe import _


class TraineeTransfer(Document):
    def on_submit(self):
        schedule_id = frappe.db.get_value("Trainee Course Schedule", {
                                          "trainee": self.trainee, "group": self.from_group}, "name")
        if not schedule_id:
            frappe.throw(_("No Any Trainee Schedule Available"))
        # sessions = 0
        schedule_doc = frappe.get_doc("Trainee Course Schedule", schedule_id)
        schedule_doc.group = self.to_group
        schedule_doc.coach = frappe.db.get_value("Gymnastics Group",self.to_group,"group_coach")
        schedule_doc.coach_name = frappe.db.get_value("Gymnastics Group",self.to_group,"coach_name")
        update_trainee_schedule_for_transfer(schedule_doc, self.effective_date)
        schedule_doc.save()
        remove_entry_in_group(self.from_group,self.trainee)
        create_entry_in_group(self.to_group,self.trainee)

    def on_cancel(self):
        frappe.throw(_("Not Allow To Cancel Group Transfer"))


