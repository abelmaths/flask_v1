$('#exercises').dataTable({
   "data": homework_data,
   "bDestroy": true,
   "deferRender": true,
   "paging": false,
   "columns": [
      { "data": "exercise_title_visible" }, 
      // { "data": "exercise_description_visible" }, 
      { "data": "classroom_name" }, 
      { "data": "date_set" },       
      { "data": "date_due" },
      { "data": "status_count" },       
      { 
        "data": "see_pupil_progress",
        "render" : function(data, type, row, meta){return datatable_link(data)},
        "orderable": false,
      },
      {
        "data": "see_exercises",
        "render" : function(data, type, row, meta){return datatable_link(data)},
        "orderable": false,
      },
    ]
});