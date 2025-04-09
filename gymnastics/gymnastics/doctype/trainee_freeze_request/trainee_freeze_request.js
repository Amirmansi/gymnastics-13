// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trainee Freeze Request', {
	from_date: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn];
		if(doc.trainee && doc.from_date && doc.to_date && doc.trainee_group) {
			frm.events.get_schedules(frm)
		}
	},
	to_date: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn]
		if(doc.trainee && doc.from_date && doc.to_date && doc.trainee_group) {
			frm.events.get_schedules(frm)
			
		}
	},
	trainee_group: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn]
		if(doc.trainee && doc.from_date && doc.to_date && doc.trainee_group) {
			frm.events.get_schedules(frm)
			
		}
	},
	get_schedules: function(frm) {
		frm.call({
			method:"get_schedule_between_date",
			doc: frm.doc,
			callback:function(r){
				frm.reload_doc()
			}
		})
	}
});
