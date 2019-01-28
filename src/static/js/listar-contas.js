//this function appends the json data to the table 'gable'
function append_json(data){
	var table = document.getElementById('contas_table');
	data.forEach(function(object) {
		var tr = document.createElement('tr');
		tr.innerHTML = '<td>' + object.conta + '</td>' +
		'<td>' + object.data_vencimento + '</td>' +
		'<td>' + Number(object.valor_conta).toFixed(2) + '</td>'
		table.appendChild(tr);
	});
	$("#contas_table tr").click(function(){
   		$(this).addClass('selected').siblings().removeClass('selected');    
   		var value=$(this).find('td');
   		document.getElementById("conta").value = value[0].innerText
   		var d = value[1].innerText
   		document.getElementById("data_vencimento").value = d.substring(6,10) + '-' + d.substring(3, 5) + '-' + d.substring(0, 2)
   		document.getElementById("valor_pago").value = value[2].innerText
	});

	$('.ok').on('click', function(e){
   		var selectedIDs = [];
   		$("#table tr.selected").each(function(index, row) {
      		selectedIDs.push($(row).find("td:first").html());
   		})});
}