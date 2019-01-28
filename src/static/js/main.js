function handleRadio(elemento){
	var checked = document.getElementById(elemento.name + "_sim").checked
	if(checked){
		document.getElementById("div_" + elemento.name).style.display = "inline"
	}else{
		document.getElementById("div_" + elemento.name).style.display = "none"
	}
}