// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt
frappe.provide("education");


frappe.ui.form.on('Trainee Attendance Tool', {
	setup: (frm) => {
		console.log(frm.fields_dict);
		frm.students_area = $('<div>')
			.appendTo(frm.fields_dict.traniee_html.wrapper);
	},
	refresh: function(frm) {
		if (frappe.route_options) {
			frm.set_value("based_on", frappe.route_options.based_on);
			frm.set_value("student_group", frappe.route_options.student_group);
			frm.set_value("course_schedule", frappe.route_options.course_schedule);
			frappe.route_options = null;
		}
		frm.disable_save();
	},

	based_on: function(frm) {
		if (frm.doc.based_on == "Student Group") {
			frm.set_value("course_schedule", "");
		} else {
			frm.set_value("student_group", "");
		}
	},

	group: function(frm) {
		if ((frm.doc.group && frm.doc.date)) {
			frm.students_area.find('.student-attendance-checks').html(`<div style='padding: 2rem 0'>Fetching...</div>`);
			// var method = "gymnastics.gymnastics.doctype.trainee_attendance_tool.trainee_attendance_tool.get_trainee_attendance_records";
			var method = "gymnastics.gymnastics.doctype.trainee_attendance_tool.trainee_attendance_tool.get_student_attendance_records";

			frappe.call({
				method: method,
				args: {
					group: frm.doc.group,
					date: frm.doc.date
				},
				callback: function(r) {
					frm.events.get_students(frm, r.message);
				}
			})
		}
	},

	date: function(frm) {
		if (frm.doc.date > frappe.datetime.get_today())
			frappe.throw(__("Cannot mark attendance for future dates."));
		frm.trigger("group");
	},

	get_students: function(frm, students) {
		students = students || [];
		frm.students_editor = new education.StudentsEditor(frm, frm.students_area, students);
	},
	select_date(frm) {
	    frm.call({
			method:'get_group_dates',
			doc: frm.doc,
			args: {
				group: frm.doc.group
			},
			freeze:true,
			freeze_message:"Fetching Date",
			callback: (r) => {
				// console.log(r);
				var data = r.message;
				if(data.length > 0) {
					show_availability(data);
				} else {
					show_empty_state();
				}
			}
		});

		function show_empty_state() {
			frappe.msgprint({
				title: __('Not Available'),
				message: __("No Schedule Available For Group {0}", [frm.doc.group.bold()]),
				indicator: 'red'
			});
		}

		function show_availability(data) {
			var d = new frappe.ui.Dialog({
				title: __("Available Dates"),
				fields: [{ fieldtype: 'HTML', fieldname: 'available_slots'}],
				primary_action_label: __("Mark Attendance"),
				primary_action: function() {
					// book slot
					frm.set_value('date', selected_slot);
					d.hide();
					// frm.save();
				}
			});
			var $wrapper = d.fields_dict.available_slots.$wrapper;
			var selected_slot = null;

			// disable dialog action initially

			// make buttons for each slot
			var slot_html = data.map(slot => {
				return `<button class="btn btn-default"
					data-name=${slot.schedule_date}
					style="margin: 0 10px 10px 0; width: 130px" title="Available">
					${slot.schedule_date}
				</button>`;
			}).join("");

			$wrapper
				.css('margin-bottom', 0)
				.addClass('text-center')
				.html(slot_html);


			// blue button when clicked
			$wrapper.on('click', 'button', function() {
				var $btn = $(this);
				$wrapper.find('button').removeClass('btn-primary');
				$btn.addClass('btn-primary');
				selected_slot = $btn.attr('data-name');

				// enable dialog action
				d.get_primary_btn().attr('disabled', null);
			});

			d.show();
		}
	},

});
// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Trainee Attendance', {
// 	// refresh: function(frm) {

// 	// }
// });




education.StudentsEditor = class StudentsEditor {
	constructor(frm, wrapper, students) {
		this.wrapper = wrapper;
		this.frm = frm;
		if(students.length > 0) {
			this.make(frm, students);
		} else {
			this.show_empty_state();
		}
	}
	make(frm, students) {
		var me = this;

		$(this.wrapper).empty();
		var student_toolbar = $('<p>\
			<button class="btn btn-default btn-add btn-xs" style="margin-right: 5px;"></button>\
			<button class="btn btn-xs btn-default btn-remove" style="margin-right: 5px;"></button>\
			<button class="btn btn-default btn-primary btn-mark-att btn-xs"></button></p>').appendTo($(this.wrapper));


		console.log(students)

		student_toolbar.find(".btn-add")
			.html(__('Check all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if (!$(check).prop("disabled")) {
						check.checked = true;
					}
				});
			});

		student_toolbar.find(".btn-remove")
			.html(__('Uncheck all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if (!$(check).prop("disabled")) {
						check.checked = false;
					}
				});
			});

		student_toolbar.find(".btn-mark-att")
			.html(__('Mark Attendance'))
			.on("click", function() {
				$(me.wrapper.find(".btn-mark-att")).attr("disabled", true);
				var studs = [];
				$(me.wrapper.find('input[type="checkbox"]')).each(function(i, check) {
					var $check = $(check);
					studs.push({
						trainee: $check.data().trainee,
						trainee_name: $check.data().trainee_name,
						disabled: $check.prop("disabled"),
						checked: $check.is(":checked")
					});
				});

				var students_present = studs.filter(function(stud) {
					return !stud.disabled && stud.checked;
				});

				var students_absent = studs.filter(function(stud) {
					return !stud.disabled && !stud.checked;
				});

				frappe.confirm(__("Do you want to update attendance? <br> Present: {0} <br> Absent: {1}",
					[students_present.length, students_absent.length]),
					function() {	//ifyes
						if(!frappe.request.ajax_count) {
							frappe.call({
								method: "gymnastics.gymnastics.doctype.trainee_attendance_tool.trainee_attendance_tool.mark_attendance",
								freeze: true,
								freeze_message: __("Marking attendance"),
								args: {
									"students_present": students_present,
									"students_absent": students_absent,
									"group": frm.doc.group,
									"date": frm.doc.date
								},
								callback: function(r) {
									$(me.wrapper.find(".btn-mark-att")).attr("disabled", false);
									frm.trigger("student_group");
								}
							});
						}
					},
					function() {	//ifno
						$(me.wrapper.find(".btn-mark-att")).attr("disabled", false);
					}
				);
			});

		// make html grid of students
		let student_html = '';
		for (let student of students) {
			student_html += `<div class="col-sm-3">
					<div class="checkbox">
						<label>
							<input
								type="checkbox"
								data-trainee="${student.trainee}"
								data-trainee_name="${student.trainee_name}"
								class="trainee-check"
								${student.status==='Present' ? 'checked' : ''}>
							${student.trainee_name}
						</label>
					</div>
				</div>`;
		}
		console.log(me.wrapper)

		$(`<div class='student-attendance-checks'>${student_html}</div>`).appendTo(me.wrapper);
	}

	show_empty_state() {
		$(this.wrapper).html(
			`<div class="text-center text-muted" style="line-height: 100px;">
				${__("No Students in")} ${this.frm.doc.student_group}
			</div>`
		);
	}
};