//this function appends the json data to the table 'gable'
function append_json(data){
	var table = document.getElementById('contas_table');
	data.forEach(function(object) {
		data_vencimento = getDataVencimento(object.dia_vencimento)
		var tr = document.createElement('tr');
		tr.innerHTML = '<td>' + object.conta + '</td>' +
		'<td>' + data_vencimento + '</td>' +
		'<td>' + Number(object.valor_conta).toFixed(2) + '</td>' +
		'<td>' + object.categoria + '</td>'
		table.appendChild(tr);
	});
	$("#contas_table tr").click(function(){
   		$(this).addClass('selected').siblings().removeClass('selected');    
   		var value=$(this).find('td');
   		document.getElementById("conta").value = value[0].innerText
   		var d = value[1].innerText
   		document.getElementById("data_vencimento").value = d.substring(6,10) + '-' + d.substring(3, 5) + '-' + d.substring(0, 2)
   		document.getElementById("valor_pago").value = value[2].innerText
   		document.getElementById("categoria").value = value[3].innerText
	});

	$('.ok').on('click', function(e){
   		var selectedIDs = [];
   		$("#table tr.selected").each(function(index, row) {
      		selectedIDs.push($(row).find("td:first").html());
   		})});
}

function getDataVencimento(dia_vencimento){
	var d = new Date()
	return getTwoDigits(dia_vencimento) + '/' + getTwoDigits(d.getMonth() + 1) + '/' + d.getFullYear()
}

function getTwoDigits(number){
	return ("0" + number).slice(-2)
}