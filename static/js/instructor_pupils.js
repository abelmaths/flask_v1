$('#pupils').dataTable({
   "data": pupil_data,
   "bDestroy": true,
   "deferRender": true,
   "paging": false,
   "columns": [
      { "data": "name" }, 
      { "data": "classrooms" },     
      { 
        "data": "see_progress",
        "render" : function(data, type, row, meta){return datatable_link(data)},
        "orderable": false,
      }
    ]
});