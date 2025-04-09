// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on("Trainee Applicant", {
	refresh: function(frm) {
		if (frm.doc.status==="Applied" && frm.doc.docstatus===1 ) {
			frm.add_custom_button(__("Approve"), function() {
				frm.set_value("status", "Approved");
				frm.save_or_update();

			}, 'Actions');

			frm.add_custom_button(__("Reject"), function() {
				frm.set_value("status", "Rejected");
				frm.save_or_update();
			}, 'Actions');
		}

		if (frm.doc.status === "Approved" && frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Create Trainee"), function() {
				frm.events.profile(frm)
			}).addClass("btn-primary");

			frm.add_custom_button(__("Reject"), function() {
				frm.set_value("status", "Rejected");
				frm.save_or_update();
			}, 'Actions');
		}
	},

	profile: function(frm) {
		frappe.model.open_mapped_doc({
			method: "gymnastics.gymnastics.doctype.trainee_applicant.trainee_applicant.create_trainee",
			frm: frm
		})
	}
});
