$(document).ready(function(){
  var startDate=$('input[name="startDate"]'); //our date input has the name "date"
  var container=$('.bootstrap-iso form').length>0 ? $('.bootstrap-iso form').parent() : "body";
  var options={
	format: 'yyyy-mm-dd',
	container: container,
	todayHighlight: true,
	autoclose: true,
  };
  startDate.datepicker(options);

  var endDate=$('input[name="endDate"]'); //our date input has the name "date"
  var container=$('.bootstrap-iso form').length>0 ? $('.bootstrap-iso form').parent() : "body";
  var options={
	format: 'yyyy-mm-dd',
	container: container,
	todayHighlight: true,
	autoclose: true,
  };
  endDate.datepicker(options);
})