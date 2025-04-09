// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Group Schedule', {
	add_custom_days:function(frm) {
		console.log('add')
		// if(!frm.doc.from_date && !frm.doc.to_date) {
		// 	frappe.throw(__("From Date And To Date Mandatory"))
		// }
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
	update:function(frm) {
		console.log('add')
		// if(!frm.doc.from_date && !frm.doc.to_date) {
		// 	frappe.throw(__("From Date And To Date Mandatory"))
		// }
		frm.call({
			doc:frm.doc,
			method:"add_dates_from_day",
			freeze:true,
			freeze_message:"Adding Days ...",
			callback:function(frm) {
				frm.refresh_field("schedules");
				frm.reload_doc()
			}
		})
	}
});
