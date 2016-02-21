$('#submissions').dataTable({
   "data": submission_data,
   "bDestroy": true,
   "deferRender": true,
   "paging": false,
   "columns": [
      { "data": "pupil_name" }, 
      { "data": "exercise_title_visible" },     
      { "data": "progress" },     
      { "data": "status" },     
      { "data": "total_score" },     
      { "data": "percentage_attempted" },          
      { 
        "data": "see_attempt",
        "render" : function(data, type, row, meta){return datatable_link(data)},
        "orderable": false,
      }
    ]
});
