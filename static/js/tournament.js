function renderTournaments(tournamentData){
	console.log(tournamentData);
	for (idx in tournamentData) {
		renderTournament(tournamentData[idx]);
	}
}

function renderTournament(tournament){
	var targetDiv = $("#tournament_view");
	var fights = tournament.fights;
	var markup = "<h1>"+tournament.tournament_name+"</h1><table class='table table-bordered table-striped tournament-table'>";
	var rowCount = calcRowCount(tournament.tournament_level);
	var tournamentLevel = Math.pow(2, rowCount);
	for (i=0; i<rowCount; i++){
		var colCount = Math.pow(2, i);
		var tournament_level = Math.pow(2, i+1);
		var colspan = Math.pow(2, rowCount - (i+1));
		markup += "<tr>";
		for (j=0; j<colCount; j++){
			markup +="<td colspan='"+colspan+"'>"+tournament_level+"강</td>"
		}
		markup += "</tr>";
		markup += "<tr>";
		for (j=0; j<colCount; j++){
			var fight_info = "";
			var fight = "";
			fight = fights[tournament_level+":"+(j+1)];
			if (fight != null) {
				if('winner' in fight && fight.winner != null){
					fight_info += "<span class='label label-warning'>승자: " + fight.winner.name+ "</span><br/> ";
				}
				fight_info += fight.player1.name + "<br/>vs<br/>" + fight.player2.name;
			}
			markup +="<td colspan='"+colspan+"'>"+fight_info+"</td>"
		}
		markup += "</tr>";
	}
	markup += "</table>";
	targetDiv.append($(markup));
}

function calcRowCount(tournament_level){
		var rowCount = 0;
		for (i=1; i<tournament_level; i*=2){
			rowCount++;
		}
		return rowCount;
}
