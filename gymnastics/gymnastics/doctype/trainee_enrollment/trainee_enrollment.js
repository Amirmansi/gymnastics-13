// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trainee Enrollment', {
	setup:function(frm,cdt,cdn) {
		frm.set_query("group", function() {
			return { filters: { course: frm.doc.course } };
		});
	},
	refresh:function(frm,cdt,cdn){
		var doc = locals[cdt][cdn];
		if(frm.doc.docstatus == 1){
			if (!frm.doc.invoice_no){
				frm.add_custom_button(__('Create Invoice'), function() {			
					let d = new frappe.ui.Dialog({
						title: 'Invoice Details',
						fields: [
							{
								label: 'Date',
								fieldname: 'date',
								fieldtype: 'Date',
								reqd:1
							},
							{
								label: 'Item',
								fieldname: 'item',
								fieldtype: 'Link',
								options:'Item',
								reqd:1
							},
							{
								label: 'Deferred Revenue',
								fieldname: 'deferred_revenue',
								fieldtype: 'Link',
								options:'Account',
								get_query:function(){
									return {
										filters:{
											"company":frm.doc.company,
											"root_type":"Liability",
											"is_group":0
										}
									}
								},
								reqd:1
							},
							{
								label: 'Amount',
								fieldname: 'amount',
								fieldtype: 'Currency',
								reqd:1
							},
							{
								label: 'Mode Of Payment',
								fieldname: 'mode_of_payment',
								fieldtype: 'Link',
								reqd:1,
								options:"Mode of Payment"
							},
							{
								label: 'Paid Amount',
								fieldname: 'paid_amount',
								fieldtype: 'Currency',
								reqd:1
							}
						],
						primary_action_label: 'Submit',
						primary_action(values) {
							console.log(values);
							frappe.call({
								method:"gymnastics.gymnastics.doctype.trainee_enrollment.trainee_enrollment.create_invoice",
								args:{"trainee":frm.doc.trainee,"date":values.date,"item":values.item,"amount":values.amount,"account":values.deferred_revenue,"enroll":frm.doc.name,"mode_of_payment":values.mode_of_payment,"paid_amount":values.paid_amount},
								freeze:true,
								freeze_message:"Creating Invoice ...",
								async:false,
								callback:function(r){
									d.hide();
									frm.reload_doc()
								}	
							})
							// d.hide();
						}
					});
					
					d.show();
					d.set_value("date",doc.enrollment_date)
					d.set_value("amount",doc.course_amount)
					d.set_value("paid_amount",doc.course_amount)

				})
			} else{
				frm.add_custom_button(__("View Invoice"),function(){
					frappe.set_route("Form","Sales Invoice",frm.doc.invoice_no)
				})
			}
		}
	},
	course: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn];
		if(doc.course){
			frappe.model.set_value(cdt,cdn,"frequency","")
			frappe.call({
				method:"gymnastics.gymnastics.doctype.trainee_enrollment.trainee_enrollment.get_frequency",
				args:{"course":doc.course},
				callback:function(r){
					if(r.message){
						frm.set_df_property('frequency', 'options', r.message);
					}
				}
			})
		}
	},
	frequency: function(frm,cdt,cdn){
			var doc = locals[cdt][cdn];
			if(doc.frequency && doc.course){
				frappe.call({
					method:"gymnastics.gymnastics.doctype.trainee_enrollment.trainee_enrollment.get_amount_for_course",
					args:{"course":doc.course,"frequency":doc.frequency},
					callback:function(r){
						if(r.message){
							frappe.model.set_value(cdt,cdn,"course_amount",r.message)
						}
					}
				})
			}
	}
});
