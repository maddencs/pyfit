/**
 * Created by cory on 1/21/17.
 */
var csrftoken;
function submitAddRoutineForm(data){
	$.ajax({
		url: '/add-routine/',
		data: data,
		method: 'POST',
		success: function(data){
			location.reload();
		},
		error: function(){
			alert("Server error. Bummer.");
		}
	})
}

function editRoutineSubmitForm(data){
	$.ajax({
		url: '/edit-routine/',
		method: 'POST',
		data: data,
		success: function(data){
			location.reload();
		},
		error: function(){
			alert("Server failure.");
		}
	})
}

function deleteRoutine(e){
	var routineId = $(e.target).data('routine-id');
	$.ajax({
		url: '/delete-routine/',
		method: 'POST',
		data: {
			'routine_id': routineId,
			'csrfmiddlewaretoken': csrftoken
		},
		success: function(data){
			location.reload();
		},
		error: function(){
			alert("Server error. Bummer.");
		}
	})
}


$(document).ready(function(){
	csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
	
	$('.common-info').click(function(e){
		var routineId = $(e.target).closest('tr').data('routine-id');
		window.location = '/routine/' + routineId + '/';
	})
	
	
	$('.delete-routine-btn').click(deleteRoutine)
	
	$('.edit-routine-btn').click(function(e){
		$('#edit-routine-id').val($(e.target).data('routine-id'));
		$('#edit-routine-popup').show();
	})
		
	$('#add-routine').click(function(){
		$('#add-routine-popup').show();
	})
	
	
	$('#add-routine-form').submit(function(e){
		e.preventDefault();
		var data = $(this).serialize();
		submitAddRoutineForm(data);
	})
	
	$('#edit-routine-form').submit(function(e){
		e.preventDefault();
		var data = $(this).serialize();
		editRoutineSubmitForm(data);
	})
	
});
