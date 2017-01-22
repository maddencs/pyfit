/**
 * Created by cory on 1/21/17.
 */
var csrftoken;
function submitAddExerciseForm(data){
	$.ajax({
		url: '/add-exercise/',
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

function submitEditExerciseForm(data){
	$.ajax({
		url: '/edit-exercise/',
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

function deleteExercise(e){
	var exerciseId = $(e.target).data('exercise-id');
	$.ajax({
		url: '/delete-exercise/',
		method: 'POST',
		data: {
			'exercise_id': exerciseId,
			'csrfmiddlewaretoken': csrftoken
		},
		success: function(data){
			if(data.success){
				window.location.reload();
			} else{
				var reason = 'There was a problem deleting the exercise.';
				switch(data.reason){
					case 'EXERCISE_DNE':
						reason = 'The exercise you\'re trying to delete may already have been deleted. Try refreshing the page.';
						break;
					default:
						break;
				}
				alert(reason);
			}
		},
		error: function(){
			alert("Server error. Bummer.");
		}
	})
}


$(document).ready(function(){
	csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
	
	$('.common-info').click(function(e){
		var exerciseId = $(e.target).closest('tr').data('exercise-id');
		window.location = '/exercise/' + exerciseId + '/';
	})
	
	
	$('.delete-exercise-btn').click(deleteExercise)
	
	$('.edit-exercise-btn').click(function(e){
		$('#edit-exercise-id').val($(e.target).data('exercise-id'));
		$('#edit-exercise-popup').show();
	})
	
	$('#add-exercise').click(function(){
		$('#add-exercise-popup').show();
	})
	
	
	$('#add-exercise-form').submit(function(e){
		e.preventDefault();
		var data = $(this).serialize();
		submitAddExerciseForm(data);
	})
	
	$('#edit-exercise-form').submit(function(e){
		e.preventDefault();
		var data = $(this).serialize();
		submitEditExerciseForm(data);
	})
	
});

