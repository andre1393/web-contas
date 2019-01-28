function handleRadio(elemento){
	var checked = document.getElementById(elemento.name + "_sim").checked
	if(checked){
		document.getElementById("div_" + elemento.name).style.display = "inline"
	}else{
		document.getElementById("div_" + elemento.name).style.display = "none"
	}
}

//this function appends the json data to the table 'gable'
function append_json(data, table_name, columns){
	var table = document.getElementById(table_name);
	data.forEach(function(object) {
		var tr = document.createElement('tr');
		columns.forEach(function (column) {
			tr.innerHTML += '<td>' + object[column] + '</td>'
		});
		table.appendChild(tr);
	});
}