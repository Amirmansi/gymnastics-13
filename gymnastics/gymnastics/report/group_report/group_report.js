// Copyright (c) 2016, Bhavesh Maheshwari and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Group Report"] = {
	"filters": [
		{
			"label":"Remove Disable Group",
			"fieldname":"remove_disable_group",
			"fieldtype":"Check",
			"default":"1"
		}
	]
};
