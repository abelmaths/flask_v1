$('#submissions').dataTable({
   "data": submission_data,
   "bDestroy": true,
   "deferRender": true,
   "paging": false,
   "columns": [
      { 
        "data": "exercise_name",
        "render" : function(data, type, row, meta){return datatable_link(data)},
        "orderable": false,
      }, 
      { "data": "exercise_description_visible" },     
      { "data": "status" },     
      { "data": "total_score" },     
      { "data": "percentage_attempted" },          
      { "data": "date_set" },          
      { "data": "date_due" }
    ]
});
