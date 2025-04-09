# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from pydoc import doc
from tokenize import Triple
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import today, cint, getdate, add_days, cstr, formatdate


class TraineeEnrollment(Document):
    def validate(self):
        self.validate_overlap()

    def on_submit(self):
        create_entry_in_group(self.group, self.trainee)
        create_schedule_for_trainee(self)
        if self.invoice_no:
            frappe.db.set_value("Sales Invoice", self.invoice_no, "enroll", 1)

    def on_cancel(self):
        remove_entry_in_group(self.group, self.trainee)
        delete_schedule_for_trainee(self)
        if self.invoice_no:
            frappe.db.set_value("Sales Invoice", self.invoice_no, "enroll", 0)

    def validate_overlap(self):
        query = """
			select name
			from `tab{0}`
			where name != %(name)s
			and trainee = %(trainee)s and (from_date between %(from_date)s and %(to_date)s \
				or to_date between %(from_date)s and %(to_date)s \
				or (from_date < %(from_date)s and to_date > %(to_date)s))
			"""
        if not self.name:
            # hack! if name is null, it could cause problems with !=
            self.name = "New " + self.doctype

        overlap_doc = frappe.db.sql(
            query.format(self.doctype),
            {
                "from_date": self.from_date,
                "to_date": self.to_date,
                "name": self.name,
                "trainee": self.trainee,
            },
            as_dict=1,
        )

        if overlap_doc:
            msg = (
                _("A {0} exists between {1} and {2} (").format(
                    self.doctype, formatdate(self.from_date), formatdate(self.to_date)
                )
                + """ <b><a href="/app/Form/{0}/{1}">{1}</a></b>""".format(
                    self.doctype, overlap_doc[0].name
                )
                + _(") for {0}").format(self.trainee)
            )
            frappe.throw(msg)


@frappe.whitelist()
def get_frequency(course):
    frequency = frappe.get_all(
        "Gymnastics Course Amount",
        filters=[["parent", "=", course]],
        fields=["frequency"],
    )
    return [row.frequency for row in frequency]


@frappe.whitelist()
def get_amount_for_course(frequency, course):
    frequency = frappe.get_all(
        "Gymnastics Course Amount",
        filters=[["parent", "=", course], ["frequency", "=", frequency]],
        fields=["amount"],
    )
    if len(frequency) >= 1:
        return frequency[0].amount or 0
    else:
        return 0


@frappe.whitelist()
def create_invoice(
    trainee, date, item, amount, account, enroll, mode_of_payment, paid_amount
):
    customer = frappe.db.get_value("Trainee", trainee, "customer")
    if not customer:
        frappe.throw(_("Trainee Not Linked With Any Customer."))
    enroll_doc = frappe.get_doc("Trainee Enrollment", enroll)
    items = [
        {
            "item_code": item,
            "qty": 1,
            "rate": amount,
            "enable_deferred_revenue": 1,
            "deferred_revenue_account": account,
            "service_start_date": enroll_doc.from_date,
            "service_end_date": enroll_doc.to_date,
        }
    ]
    invoice_doc = frappe.get_doc(
        dict(
            doctype="Sales Invoice",
            posting_date=date,
            customer=customer,
            items=items,
            gymnastics_invoice=1,
            trainee=enroll_doc.trainee,
            course=enroll_doc.course,
            group=enroll_doc.group,
            from_date=enroll_doc.from_date,
            to_date=enroll_doc.to_date,
            is_pos=1,
        )
    )
    invoice_doc.append(
        "payments", dict(mode_of_payment=mode_of_payment, amount=paid_amount)
    )
    res = invoice_doc.insert(ignore_permissions=True)
    res.submit()
    frappe.db.set_value("Trainee Enrollment", enroll, "invoice_no", res.name)
    create_entry_in_group(enroll_doc.group, enroll_doc.trainee)
    create_schedule_for_trainee(enroll_doc)


def create_entry_in_group(group, trainee):
    doc = frappe.get_doc("Gymnastics Group", group)
    trainee_exists = False
    for trainee_row in doc.trainees:
        if trainee_row == trainee:
            trainee_exists = True
    if not trainee_exists:
        doc.append(
            "trainees",
            dict(
                trainee=trainee,
                trainee_name=frappe.db.get_value("Trainee", trainee, "trainee_name"),
            ),
        )
        doc.save(ignore_permissions=True)


def remove_entry_in_group(group, trainee):
    frappe.db.sql(
        """delete from `tabGroup Trainee Details` where parent=%s and trainee=%s""",
        (group, trainee),
    )
    group_doc = frappe.get_doc("Gymnastics Group", group)
    group_doc.reload()
    group_doc.save(ignore_permissions=True)


def delete_schedule_for_trainee(enroll_doc):
    schedules = frappe.get_all(
        "Trainee Course Schedule", {"enrollment": enroll_doc.name}, pluck="name"
    )
    for schedule in schedules:
        frappe.delete_doc(
            "Trainee Course Schedule", schedule, ignore_missing=True, force=True
        )


def create_schedule_for_trainee(enroll_doc):
    doc = frappe.new_doc("Trainee Course Schedule")
    doc.enrollment = enroll_doc.name
    doc.date = today()
    doc.trainee = enroll_doc.trainee
    doc.coach = frappe.db.get_value("Gymnastics Group", enroll_doc.group, "group_coach")
    doc.course = enroll_doc.course
    doc.group = enroll_doc.group
    doc.session = enroll_doc.frequency
    schedules = frappe.get_all(
        "Group Schedule",
        filters=[["from_date", "<=", enroll_doc.from_date], ["group", "=", doc.group]],
        fields=["name"],
    )
    session = 0
    for row in schedules:
        if validate_session(session, doc):
            break
        schedule_doc = frappe.get_doc("Group Schedule", row.name)
        for schedule in schedule_doc.schedules:
            if schedule.active and getdate(schedule.date) >= getdate(
                enroll_doc.from_date
            ):
                doc.append(
                    "trainee_course_schedule_details",
                    dict(
                        date=schedule.date,
                        day=schedule.day,
                        from_time=schedule.get("from_time"),
                        to_time=schedule.get("to_time"),
                        gymnastics_group=enroll_doc.group,
                        sales_invoice=enroll_doc.invoice_no,
                    ),
                )
                session += 1
                if validate_session(session, doc):
                    break
    if not validate_session(session, doc):
        frappe.throw(_("Schedule Not Available To Fullfill All Session"))
    doc.insert(ignore_permissions=True)


def validate_session(session, doc):
    if cint(session) == cint(doc.session):
        return True
    else:
        return False


def update_trainee_schedule(doc, freeze_date_current=[], from_date=None):
    old_schedules = []
    # old_date_invoice_map = {}
    if not from_date:
        from_date = today()
    for t_schedule in doc.trainee_course_schedule_details:
        if getdate(t_schedule.date) < getdate(from_date):
            old_schedules.append(t_schedule)
    session = len(old_schedules) or 0
    doc.trainee_course_schedule_details = []
    if validate_session(session, doc):
        return
    for old_schedule in old_schedules:
        doc.append("trainee_course_schedule_details", old_schedule)
    freeze_dates = trainee_freeze_date(doc.trainee)

    freeze_dates.extend(freeze_date_current)
    coach = frappe.db.get_value("Gymnastics Group", doc.group, "group_coach")
    leave_days = coach_leave_days(coach)
    schedules = frappe.get_all(
        "Group Schedule",
        filters=[["from_date", "<=", from_date], ["group", "=", doc.group]],
        fields=["name"],
    )
    training_start_date = frappe.db.get_value(
        "Trainee Enrollment", doc.enrollment, "from_date"
    )
    if not training_start_date:
        training_start_date = from_date
    if getdate(training_start_date) < getdate(from_date):
        training_start_date = from_date
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

                    doc.append(
                        "trainee_course_schedule_details",
                        dict(
                            date=schedule.date,
                            day=schedule.day,
                            from_time=schedule.from_time,
                            to_time=schedule.to_time,
                            gymnastics_group=schedule_doc.group,
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
    doc.save(ignore_permissions=True)


def update_trainee_schedule_for_transfer(doc, date):
    old_schedules = []
    for t_schedule in doc.trainee_course_schedule_details:
        if getdate(t_schedule.date) < getdate(date):
            old_schedules.append(t_schedule)
    session = len(old_schedules) or 0
    doc.trainee_course_schedule_details = []
    if validate_session(session, doc):
        return
    for old_schedule in old_schedules:
        doc.append("trainee_course_schedule_details", old_schedule)
    freeze_dates = trainee_freeze_date(doc.trainee)
    coach = frappe.db.get_value("Gymnastics Group", doc.group, "group_coach")
    leave_days = coach_leave_days(coach)
    schedules = frappe.get_all(
        "Group Schedule",
        filters=[["from_date", "<=", date], ["group", "=", doc.group]],
        fields=["name"],
    )
    # training_start_date = frappe.db.get_value("Trainee Enrollment",doc.enrollment,"from_date")
    # if getdate(training_start_date) < getdate(today()):
    training_start_date = date
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
                    doc.append(
                        "trainee_course_schedule_details",
                        dict(
                            date=schedule.date,
                            day=schedule.day,
                            from_time=schedule.from_time,
                            to_time=schedule.to_time,
                            gymnastics_group=schedule_doc.group,
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
    doc.save(ignore_permissions=True)


def update_trainee_schedule_freeze_group(doc, dates=[]):
    old_schedules = []
    for t_schedule in doc.trainee_course_schedule_details:
        if not cstr(t_schedule.date) in dates:
            old_schedules.append(t_schedule)
    session = len(old_schedules) or 0
    doc.trainee_course_schedule_details = []
    if validate_session(session, doc):
        return
    except_date = []
    idx = 1
    for old_schedule in old_schedules:
        except_date.append(cstr(old_schedule.date))
        old_schedule.idx = idx
        doc.append("trainee_course_schedule_details", old_schedule)
        idx += 1
    freeze_dates = trainee_freeze_date(doc.trainee)
    coach = frappe.db.get_value("Gymnastics Group", doc.group, "group_coach")
    leave_days = coach_leave_days(coach)
    training_start_date = frappe.db.get_value(
        "Trainee Enrollment", doc.enrollment, "from_date"
    )
    if getdate(training_start_date) < getdate(today()):
        training_start_date = today()
    schedules = frappe.get_all(
        "Group Schedule",
        filters=[["from_date", "<=", training_start_date], ["group", "=", doc.group]],
        fields=["name"],
    )
    training_end_date = ""
    except_date.extend(leave_days)
    except_date.extend(freeze_dates)
    except_date.extend(dates)
    for row in schedules:
        if validate_session(session, doc):
            break
        schedule_doc = frappe.get_doc("Group Schedule", row.name)
        for schedule in schedule_doc.schedules:
            if schedule.active and getdate(schedule.date) >= getdate(
                training_start_date
            ):
                if not cstr(schedule.date) in except_date:
                    doc.append(
                        "trainee_course_schedule_details",
                        dict(
                            date=schedule.date,
                            day=schedule.day,
                            from_time=schedule.from_time,
                            to_time=schedule.to_time,
                            gymnastics_group=schedule_doc.group,
                            idx=idx,
                        ),
                    )
                    session += 1
                    idx += 1
                    if validate_session(session, doc):
                        break
                    training_end_date = schedule.date
    if not validate_session(session, doc):
        frappe.throw(
            _("Schedule Not Available To Fullfill All Session {0}".format(doc.name))
        )
    doc.to_date = training_end_date
    doc.save(ignore_permissions=True)


def trainee_freeze_date(trainee):
    filters = [
        ["trainee", "=", trainee],
        ["docstatus", "=", 1],
        ["from_date", ">=", today()],
    ]
    freeze_doc = frappe.get_all(
        "Trainee Freeze Request", filters=filters, fields=["from_date", "to_date"]
    )
    freeze_date = []
    for row in freeze_doc:
        from_date = row.from_date
        while from_date <= row.to_date:
            freeze_date.append(cstr(from_date))
            from_date = add_days(from_date, 1)
    return freeze_date


def coach_leave_days(coach):
    filters = [
        ["coach", "=", coach],
        ["docstatus", "=", 1],
        ["from_date", ">=", today()],
        ["alternate_coach_arrangement", "=", 0],
    ]
    leave_doc = frappe.get_all(
        "Gymnastics Leave", filters=filters, fields=["name", "from_date", "to_date"]
    )
    leave_date = []
    for row in leave_doc:
        from_date = row.from_date
        while from_date <= row.to_date:
            leave_date.append(cstr(from_date))
            from_date = add_days(from_date, 1)
    return leave_date
