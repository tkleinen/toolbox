function SetTab(mytab,myinhoud)

{

	// juiste tab weergeven, overige verbergen

	

	alletabs = document.getElementById("tabbladen");

	tabs = alletabs.getElementsByTagName("a");

	

	for (var i = 0; i < tabs.length; i++)

	{

		tabs[i].className = "";

	}

	

	mytab.className = "active";

	

	// juiste inhoud weergeven, overige verbergen

	

	if (myinhoud)

	{

		document.getElementById('tab_1').style.visibility = "hidden";
		document.getElementById('tab_1').style.display = "none";

		document.getElementById('tab_2').style.visibility = "hidden";
		document.getElementById('tab_2').style.display = "none";

		document.getElementById('tab_3').style.visibility = "hidden";
		document.getElementById('tab_3').style.display = "none";
		
		document.getElementById('tab_4').style.visibility = "hidden";
		document.getElementById('tab_4').style.display = "none";

		document.getElementById(myinhoud).style.visibility = "visible";
		document.getElementById(myinhoud).style.display = "block";
		
		

	}

	

}