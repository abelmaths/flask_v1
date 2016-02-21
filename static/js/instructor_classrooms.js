$('#classrooms').dataTable({
   "data": classroom_data,
   "bDestroy": true,
   "deferRender": true,
   "paging": false,
   "columns": [
      { "data": "name" }, 
      { "data": "pupil_count" }, 
      { "data": "latest_set" }, 
      { "data": "next_due" },    
      { "data": "entry_code" },       
      { 
        "data": "see_pupils",
        "render" : function(data, type, row, meta){return datatable_link(data)},
        "orderable": false,
      },
      {
        "data": "see_exercises",
        "render" : function(data, type, row, meta){return datatable_link(data)},
        "orderable": false,
      },
      {
        "data": "set_exercise",
        "render" : function(data, type, row, meta){return datatable_link(data)},
        "orderable": false,
      }
    ]
});