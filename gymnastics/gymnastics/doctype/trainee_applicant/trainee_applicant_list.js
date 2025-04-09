frappe.listview_settings['Trainee Applicant'] = {
	add_fields: [ "status", 'paid'],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		if (doc.paid) {
			return [__("Paid"), "green", "paid,=,Yes"];
		}
		else if (doc.status=="Applied") {
			return [__("Applied"), "orange", "status,=,Applied"];
		}
		else if (doc.status=="Approved") {
			return [__("Approved"), "green", "status,=,Approved"];
		}
		else if (doc.status=="Rejected") {
			return [__("Rejected"), "red", "status,=,Rejected"];
		}
		else if (doc.status=="Admitted") {
			return [__("Admitted"), "blue", "status,=,Admitted"];
		}
	}
};