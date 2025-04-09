// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trainee Transfer', {
	setup: function(frm) {
		frm.set_query("from_group", function() {
			return {
				filters:[["Group Trainee Details","trainee","=",frm.doc.trainee]]
			};
		});
	}
});
