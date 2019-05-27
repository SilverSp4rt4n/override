var pID = "-1";
var schema = "-1";
var code = "-1";

function joinGame(){
	code = document.getElementById("gamecode").value
	console.log(code)
	var xhr = new XMLHttpRequest();
	xhr.addEventListener("load",joinResults);
	xhr.open("POST","/redbridge/join",true);
	xhr.setRequestHeader("Content-Type","application/json;charset=UTF-8");
	xhr.send(JSON.stringify({"gamecode":code}));
}

function joinResults(){	
	if(this.response.includes("-1:")){
		var userInput = document.getElementById("gamecode");
		userInput.classList.add("is-invalid");
		feedback = document.createElement("DIV");
		feedback.classList.add("invalid-feedback");
		feedback.id = "Negative-Feedback";
		feedback.innerHTML="Invalid Game Code";
		if(userInput.parentNode.lastChild.id!="Negative-Feedback"){
			userInput.parentNode.appendChild(feedback);
		}
	}else{
		getPage("controller.html");
		console.log(this.response);
		data = this.response.split(" ")
		pID = data[1];
		schema = data[2];
		addJoyStick();
		window.setInterval(pingServer,5000);
	}
}

function pingServer(){
	var xhr = new XMLHttpRequest();
	xhr.addEventListener("load",pingResults);
	xhr.open("POST","/redbridge/pingplayer",true);
	xhr.setRequestHeader("Content-Type","application/json;charset=UTF-8");
	xhr.send(JSON.stringify({"gamecode":code,"pid":pID}));
}

function pingResults(){
	if(this.response.includes("-2")){
		alert("Disconnected from game.");
		location.reload();
	}
	return;
}

function sendCData(wID,xVal,yVal){
	var xhr = new XMLHttpRequest();
	xhr.addEventListener("load",pingResults);
	xhr.open("POST","/redbridge/cdata",true);
	xhr.setRequestHeader("Content-Type","application/json;charset=UTF-8");
	xhr.send(JSON.stringify({"gamecode":code,"pid":pID,"xVal":xVal,"yVal":yVal,"wID":wID}));
}
