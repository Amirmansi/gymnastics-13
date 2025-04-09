frappe.views.calendar["Group Schedule"] = {
	field_map: {
		"start": "from_datetime",
		"end": "to_datetime",
		"id": "name",
		"title": "group",
		"allDay": "allDay"
	},
	get_events_method: "gymnastics.gymnastics.doctype.group_schedule.group_schedule.get_schedules"
};