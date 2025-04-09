// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gymnastics Group', {
	refresh: function(frm) {
		if(!frm.doc.__islocal){
			frm.add_custom_button(__('Add Schedule'), function() {
				frm.events.create_schedule(frm)

			});
		}
	},
	add_days:function(frm) {
		if(!frm.doc.from_date && !frm.doc.to_date) {
			frappe.throw(__("From Date And To Date Mandatory"))
		}
		frm.call({
			doc:frm.doc,
			method:"add_dates_from_day",
			freeze:true,
			freeze_message:"Adding Days ...",
			callback:function(frm) {
				frm.refresh_field("schedules");
			}
		})
	},
	create_schedule:function(frm) {
		frappe.model.open_mapped_doc({
			method: "gymnastics.gymnastics.doctype.gymnastics_group.gymnastics_group.schedule",
			frm: frm
		})
	}
});
