function renderPlayground(data){
	console.log(data);
	var playgrounds = data;
	var playgroundDiv = $('#playgrounds');
	for (var idx in playgrounds){
		playgroundDiv.append("<button class='btn'>경기장"+playgrounds[idx].playground_num+"</button>");
	}
}
	
