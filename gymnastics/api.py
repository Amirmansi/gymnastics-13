import frappe
from frappe import _
from frappe.utils import getdate, today
from frappe.utils import cstr, cint


@frappe.whitelist()
def get_items_from_session(doctype, txt, searchfield, start, page_len, filters):
    if not filters.get("course"):
        return []
    session_items = frappe.db.sql(
        """select item from `tabGymnastics Course Amount` where parent=%s""",
        filters.get("course"),
        as_dict=1,
    )
    session_items_list = [row.item for row in session_items]
    item_filters = [["name", "in", session_items_list]]
    items = frappe.get_all(
        "Item",
        fields=["name as 'name'"],
        filters=item_filters,
        limit_start=start,
        limit_page_length=page_len,
        as_list=1,
    )
    return items


@frappe.whitelist()
def validate_session_items(self, method):
    if self.gymnastics_invoice:
        session_items = frappe.db.sql(
            """select item from `tabGymnastics Course Amount` where parent=%s""",
            self.get("course"),
            as_dict=1,
        )
        session_items_list = [row.item for row in session_items]
        for item in self.items:
            if not item.item_code in session_items_list:
                frappe.throw(
                    _("Selected Item Must Be Define In Course {0}".format(self.course))
                )


@frappe.whitelist()
def check_enroll(invoice_no):
    invoice_no = frappe.db.get_value(
        "Trainee Enrollment", {"invoice_no": invoice_no, "docstatus": 1}, "name"
    )
    if invoice_no:
        return invoice_no
    else:
        return False


@frappe.whitelist()
def update_holidays(holiday_list_id):
    from gymnastics.gymnastics.doctype.trainee_enrollment.trainee_enrollment import (
        update_trainee_schedule,
    )

    holiday_doc = frappe.get_doc("Holiday List", holiday_list_id)
    holiday_dates = [cstr(row.holiday_date) for row in holiday_doc.holidays]
    groups = frappe.get_all("Group Schedule", filters={}, fields=["name"])
    updated_group = []
    for group in groups:
        group_doc = frappe.get_doc("Group Schedule", group.name)
        update = False
        for schedule_date in group_doc.schedules:
            if cstr(schedule_date.date) in holiday_dates:
                frappe.errprint(schedule_date.date)
                frappe.db.set_value(
                    schedule_date.doctype, schedule_date.name, "active", 0
                )
                frappe.db.set_value(
                    schedule_date.doctype, schedule_date.name, "holiday", 1
                )
                # schedule_date.active = 0
                # schedule_date.holiday = 1
                update = True
            else:
                if schedule_date.holiday:
                    frappe.db.set_value(
                        schedule_date.doctype, schedule_date.name, "active", 1
                    )
                    frappe.db.set_value(
                        schedule_date.doctype, schedule_date.name, "holiday", 0
                    )
                    update = True
        if update:
            updated_group.append(group_doc.group)
    filters = [["group", "in", updated_group]]
    trainee_schedule = frappe.get_all(
        "Trainee Course Schedule", filters=filters, fields=["name"]
    )
    for t_s in trainee_schedule:
        trainee_schedule_doc = frappe.get_doc("Trainee Course Schedule", t_s.name)
        update_trainee_schedule(trainee_schedule_doc)
    frappe.msgprint(_("Group Schedule Updated With Holidays"))


@frappe.whitelist()
def get_schedule_details(schedule_id):
    schedule_doc = frappe.get_doc("Trainee Course Schedule", schedule_id)
    program = frappe.db.get_value(
        "Trainee Enrollment", schedule_doc.enrollment, "program"
    )
    return dict(
        program=program,
        course=schedule_doc.course,
        trainee=schedule_doc.trainee,
        customer=frappe.db.get_value("Trainee", schedule_doc.trainee, "customer"),
    )


@frappe.whitelist()
def on_submit_invoice(self, method):
    if self.extend_plan or self.renew_plan:
        session = frappe.db.get_value(
            "Gymnastics Course Amount", {"item": self.items[0].item_code}, "frequency"
        )
        applicable_date = ""
        schedule_doc = frappe.get_doc(
            "Trainee Course Schedule", self.trainee_course_schedule
        )
        schedule_doc.session = cint(schedule_doc.session) + cint(session)
        if not self.applicable_from_date:
            applicable_date = today()
            for row in schedule_doc.trainee_course_schedule_details:
                if getdate(row.date) >= getdate(applicable_date):
                    applicable_date = row.date
        else:
            validate_date(self, schedule_doc)
            applicable_date = self.applicable_from_date
        update_schedule(applicable_date, schedule_doc, invoice_no=self.name)


def validate_date(self, schedule_doc):
    for row in schedule_doc.trainee_course_schedule_details:
        if getdate(row.date) >= getdate(self.applicable_from_date):
            frappe.throw(_("Applicable From Date Must Be Greater Than Schedule Dates"))


@frappe.whitelist()
def extend_plan_manually():
    invoice_no = ["SINV-22-00106"]
    invoice_schedule_map = {"SINV-22-00106": "TRAINEESCHEDULE00028"}
    # invoice_no = ["SINV-22-00099","SINV-22-00098","SINV-22-00096","SINV-22-00086","SINV-22-00082","SINV-22-00081","SINV-22-00080"]

    # invoice_schedule_map = {
    # 	"SINV-22-00099":"TRAINEESCHEDULE00031",
    # 	"SINV-22-00098":"TRAINEESCHEDULE00031",
    # 	"SINV-22-00096":"TRAINEESCHEDULE00037",
    # 	"SINV-22-00086":"TRAINEESCHEDULE00015",
    # 	"SINV-22-00082":"TRAINEESCHEDULE00011",
    # 	"SINV-22-00081":"TRAINEESCHEDULE00010",
    # 	"SINV-22-00080":"TRAINEESCHEDULE00006"
    # }
    for invoice in invoice_no:
        self = frappe.get_doc("Sales Invoice", invoice)
        self.applicable_from_date = "2022-05-14"
        session = frappe.db.get_value(
            "Gymnastics Course Amount", {"item": self.items[0].item_code}, "frequency"
        )
        applicable_date = ""
        schedule_doc = frappe.get_doc(
            "Trainee Course Schedule", invoice_schedule_map.get(invoice)
        )
        schedule_doc.session = cint(schedule_doc.session) + cint(session)
        if not self.applicable_from_date:
            frappe.throw("wrong")
            # for row in schedule_doc.trainee_course_schedule_details:
            # 	if applicable_date == "":
            # 		applicable_date = row.date
            # 	elif getdate(row.date) >= getdate(applicable_date):
            # 		applicable_date = row.date
        else:
            validate_date(self, schedule_doc)
            applicable_date = self.applicable_from_date
        update_schedule(applicable_date, schedule_doc)


def update_schedule(applicable_date, doc, invoice_no=None):
    from gymnastics.gymnastics.doctype.trainee_enrollment.trainee_enrollment import (
        validate_session,
        trainee_freeze_date,
        coach_leave_days,
    )

    session = len(doc.trainee_course_schedule_details)
    if validate_session(session, doc):
        return
    freeze_dates = trainee_freeze_date(doc.trainee)
    coach = frappe.db.get_value("Gymnastics Group", doc.group, "group_coach")
    leave_days = coach_leave_days(coach)
    schedules = frappe.get_all(
        "Group Schedule",
        filters=[["from_date", "<=", applicable_date], ["group", "=", doc.group]],
        fields=["name"],
    )
    training_start_date = frappe.db.get_value(
        "Trainee Enrollment", doc.enrollment, "from_date"
    )
    # if getdate(training_start_date) < getdate(applicable_date):
    training_start_date = applicable_date
    training_end_date = ""
    for row in schedules:
        if validate_session(session, doc):
            break
        schedule_doc = frappe.get_doc("Group Schedule", row.name)
        for schedule in schedule_doc.schedules:
            if schedule.active and getdate(schedule.date) > getdate(
                training_start_date
            ):
                if (
                    not cstr(schedule.date) in freeze_dates
                    and not cstr(schedule.date) in leave_days
                ):
                    from_time = to_time = ""
                    if len(schedule_doc.group_schedule_time) >= 1:
                        from_time = schedule_doc.group_schedule_time[0].from_time
                        to_time = schedule_doc.group_schedule_time[0].to_time

                    doc.append(
                        "trainee_course_schedule_details",
                        dict(
                            date=schedule.date,
                            day=schedule.day,
                            from_time=from_time,
                            to_time=to_time,
                            gymnastics_group=schedule_doc.group,
                            sales_invoice=invoice_no,
                        ),
                    )
                    session += 1
                    if validate_session(session, doc):
                        break
                    training_end_date = schedule.date
    if not validate_session(session, doc):
        frappe.throw(
            _("Schedule Not Available To Fullfill All Session {0}".format(doc.name))
        )
    doc.to_date = training_end_date
    group_doc = frappe.get_doc("Gymnastics Group", doc.group)
    trainee_exists = False
    for trainee_row in group_doc.trainees:
        if trainee_row.get("trainee") == doc.trainee:
            trainee_exists = True
    if not trainee_exists:
        group_doc.append(
            "trainees",
            dict(
                trainee=doc.trainee,
                trainee_name=frappe.db.get_value(
                    "Trainee", doc.trainee, "trainee_name"
                ),
            ),
        )
        group_doc.save(ignore_permissions=True)
    doc.save(ignore_permissions=True)


def update_group_for_expired_schedule():
    groups = frappe.get_all("Gymnastics Group", filters={"disable": 0}, fields=["name"])
    for g in groups:
        update = False
        print(g.name)
        group_doc = frappe.get_doc("Gymnastics Group", g.name)
        for trainee in group_doc.trainees:
            trainee_schedule = frappe.get_all(
                "Trainee Course Schedule",
                filters={"group": g.name, "trainee": trainee.trainee},
                fields=["name"],
            )
            expired = True
            for schedule in trainee_schedule:
                print(schedule.name)
                trainee_schedule_max_date = frappe.db.sql(
                    """select max(date) as 'date' from `tabTrainee Course Schedule Details` where parent=%s""",
                    schedule.name,
                    as_dict=1,
                )
                if len(trainee_schedule_max_date) >= 1:
                    print(trainee_schedule_max_date)
                    if getdate(trainee_schedule_max_date[0].date) >= getdate(today()):
                        expired = False
                        break
            if expired:
                print(trainee)
                frappe.db.sql(
                    """delete from `tabGroup Trainee Details` where name=%s""",
                    trainee.name,
                )
                update = True
        if update:
            group_doc.reload()


def on_submite_pos_invoice(doc, method):
    items = []
    for item in doc.items:
        # item.parenttype = "Sales Invoice"
        # item.doctype = "Sales Invoice Item"
        items.append(
            {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": item.rate,
                "discount_percentage": item.discount_percentage,
                "discount_amount": item.discount_amount,
                "income_account": item.income_account,
                "expense_account": item.expense_account,
                "warehouse": item.warehouse,
            }
        )
    for tax in doc.taxes:
        tax.parenttype = "Sales Invoice"
        tax.doctype = ""
    for payment in doc.payments:
        payment.parenttype = "Sales Invoice"
        payment.doctype = ""
    invoice_doc = frappe.get_doc(
        dict(
            doctype="Sales Invoice",
            customer=doc.customer,
            custom_invoice_type="POS",
            pos_invoice=doc.name,
            posting_date=doc.posting_date,
            due_date=doc.due_date,
            trainee=doc.trainee,
            set_warehouse=doc.set_warehouse,
            update_stock=doc.update_stock,
            items=items,
            taxes=doc.taxes,
            payments=doc.payments,
            is_pos=1,
            pos_profile=doc.pos_profile,
            apply_discount_on=doc.apply_discount_on,
            additional_discount_percentage=doc.additional_discount_percentage,
            taxes_and_charges=doc.taxes_and_charges,
            discount_amount=doc.discount_amount,
        )
    ).insert(ignore_permissions=True)
    invoice_doc.submit()
    frappe.db.set_value("POS Invoice", doc.name, "sales_invoice", invoice_doc.name)


@frappe.whitelist()
def update_trainee_schedule():
    # schedules = frappe.get_all("Trainee Course Schedule",filters={},fields=["name"])
    # for row in schedules:
    # 	schedule_doc = frappe.get_doc("Trainee Course Schedule",row.name)
    # 	for row_sc in schedule_doc.trainee_course_schedule_details:
    # 		print(schedule_doc.trainee)
    frappe.db.sql(
        """update `tabTrainee Course Schedule Details` as c inner join `tabTrainee Course Schedule` as p on c.parent=p.name set c.trainee=p.trainee"""
    )
    frappe.db.commit()
