function validateForm(){
	var response = ""
	myForm = document.forms['form']
	console.log(myForm["pago"].value)
	if (myForm["conta"].value == ""){ response = response + "o campo conta deve ser preenchido\n"}
	if (myForm["valor"].value == ""){ response = response + "o campo valor_conta deve ser preenchido\n"}
	
	if (myForm["data_pagamento"].value == ""){ response = response + "o campo data_pagamento deve ser preenchido\n"}
	if (myForm["pagador"].value == ""){ response = response + "o campo pagador deve ser preenchido\n"}
	
	if (response != ""){
		alert(response)
		return false
	}
}