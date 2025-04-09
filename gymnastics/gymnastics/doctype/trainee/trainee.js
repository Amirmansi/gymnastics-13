// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trainee', {
	// refresh: function(frm) {

	// }
});


frappe.ui.form.on("Trainee", {
	refresh: function(frm) {
		console.log('console.log')
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__("Create Invoice"), function() {
				frm.events.create_invoice(frm)
				// frappe.route_options = {
				// 	customer: frm.doc.customer,
				// 	trainee: frm.doc.name
				// };
				// frappe.set_route("Form", "Sales Invoice","new-sales-invoice-1");
			}).addClass("btn-primary");

		}

	},
	create_invoice: function(frm) {
		frappe.model.open_mapped_doc({
			method: "gymnastics.gymnastics.doctype.trainee.trainee.create_invoice",
			frm: frm
		})
	}
});