frappe.ui.form.on('Holiday List', {
	refresh(frm) {
		// your code here
		 frm.add_custom_button(__("Update Holiday"), function() {
            frappe.call({
                method:"gymnastics.api.update_holidays",
                args:{"holiday_list_id":frm.doc.name},
                freeze:true,
                freeze_message:"Updating...",
                callback:function(r){
                    
                }
            })
         });
	}
})