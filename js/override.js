var homeContent = "";

function saveHome(){
	var container = document.getElementById("content");
	homeContent = container.innerHTML;
}

function getHome(){
	var container = document.getElementById("content");
	container.innerHTML = homeContent;
}

function submitForm(formType){
	if(event.key === 'Enter' && formType === 'login'){
		login();
	}
}

function login(){
	var userInput = document.getElementById("username");
	var passInput = document.getElementById("pwd");
	var username = userInput.value;
	var password = passInput.value;
	userInput.value = "";
	passInput.value = "";
	var xhr = new XMLHttpRequest();
	xhr.addEventListener("load",loginResults);
	xhr.open("POST","/login",true);
	xhr.setRequestHeader("Content-Type","application/json;charset=UTF-8")
	xhr.send(JSON.stringify({"username":username,"password":password}));
}

function signup(){
	if(checkInput()==true){
		var userInput = document.getElementById("username");
		var emailInput = document.getElementById("email");
		var passInput = document.getElementById("pwd");

		var username = userInput.value;
		var email = emailInput.value;
		var password1 = passInput.value;

		var xhr = new XMLHttpRequest();
		xhr.addEventListener("load",signupResults);
		xhr.open("POST","/signup",true);
		xhr.setRequestHeader("Content-Type","application/json;charset=UTF-8");
		xhr.send(JSON.stringify({"username":username,"password":password1,"email":email}));
	}else{
		return -1;
	}
}
function signupResults(){
	console.log(this.response);
	if(this.response.includes("-5:")){
		var userInput = document.getElementById("username");
		userInput.classList.add("is-invalid");
		feedback = document.createElement("DIV");
		feedback.classList.add("invalid-feedback");
		feedback.id = "Negative-Feedback";
		feedback.innerHTML="Username taken.";
		if(userInput.parentNode.lastChild.id!="Negative-Feedback"){
			userInput.parentNode.appendChild(feedback);
		}
	}
	else if(this.response.includes("-6:")){
		var userInput = document.getElementById("username");
		userInput.classList.remove("is-invalid");
		userInput.classList.add("is-valid");
		var emailInput = document.getElementById("email");
		email.classList.add("is-invalid");
		badFeedback = document.getElementById("Negative-Feedback");
		if(badFeedback!=null){
			badFeedback.parentNode.removeChild(badFeedback);
		}
		feedback = document.createElement("DIV");
		feedback.classList.add("invalid-feedback");
		feedback.id = "Negative-Feedback";
		feedback.innerHTML = "Email is already in use.";
		if(emailInput.parentNode.lastChild.id!="Negative-Feedback"){
			emailInput.parentNode.appendChild(feedback);
		}		
	}else if(this.response.includes("0:")){
		getLoginForm();
		var container = document.getElementById("content");
		var alertBox = document.createElement("DIV");
		alertBox.className = "alert alert-success";
		alertBox.id = "alertBox";
		container.innerHTML+="<br><br>"
		alertBox.innerHTML = "<strong>Account Created!</strong>"
		container.appendChild(alertBox);
		
	}
}

function checkInput(){
	var userInput = document.getElementById("username");
	var emailInput = document.getElementById("email");
	var passInput = document.getElementById("pwd");
	var confirmPass = document.getElementById("confirm-pwd");
	var container = document.getElementById("content");

	var username = userInput.value;
	var email = emailInput.value;
	var password1 = passInput.value;
	var password2 = confirmPass.value;

	var feedback;
	var passwordRegex = /^(?=.*[A-Z]+)(?=.*[a-z]+)(?=.*[0-9]+)/
	var emailRegex = /[^@]+@[^@]+\.[^a]+/

	//Check email regex
	if(email.length > 0 && emailRegex.exec(email)==null){
		emailInput.classList.add("is-invalid");
		feedback = document.createElement("DIV");
		feedback.classList.add("invalid-feedback");
		feedback.id = "Negative-Feedback";
		feedback.innerHTML="Invalid email";
		if(emailInput.parentNode.lastChild.id!="Negative-Feedback"){
			emailInput.parentNode.appendChild(feedback);
		}
		return false;
	}else{
		emailInput.classList.remove("is-invalid");
		badFeedback = document.getElementById("Negative-Feedback");
		if(badFeedback!=null){
			badFeedback.parentNode.removeChild(badFeedback);
		}
		if(email.length > 0){
			emailInput.classList.add("is-valid");
		}
	}
	//Check password length
	if(password1.length < 8 && password1.length > 0){
		passInput.classList.add("is-invalid");
		feedback = document.createElement("DIV");
		feedback.classList.add("invalid-feedback");
		feedback.id = "Negative-Feedback";
		feedback.innerHTML="Password must be 8 characters or longer";
		if(passInput.parentNode.lastChild.id!="Negative-Feedback"){
			passInput.parentNode.appendChild(feedback);
		}
		return false;
	}else{
		passInput.classList.remove("is-invalid");
		badFeedback = document.getElementById("Negative-Feedback");
		if(badFeedback!=null){
			badFeedback.parentNode.removeChild(badFeedback);
		}
	}	
	//Check that password meets regex requirement
	if(passwordRegex.exec(password1)==null && password1.length > 0){
		passInput.classList.add("is-invalid");
		feedback = document.createElement("DIV");
		feedback.classList.add("invalid-feedback");
		feedback.id = "Negative-Feedback";
		feedback.innerHTML="Password must container numbers, uppercase and lowercase letters";
		if(passInput.parentNode.lastChild.id!="Negative-Feedback"){
			passInput.parentNode.appendChild(feedback);
		}
		return false;
	}else{
		passInput.classList.remove("is-invalid");
		badFeedback = document.getElementById("Negative-Feedback");
		if(badFeedback!=null){
			badFeedback.parentNode.removeChild(badFeedback);	
		}
	}
	//Check that passwords match
	if(password1 != password2 && password1.length > 0){
		passInput.classList.add("is-invalid");
		confirmPass.classList.add("is-invalid");
		feedback = document.createElement("DIV");
		feedback.classList.add("invalid-feedback");
		feedback.id = "Negative-Feedback";
		feedback.innerHTML="passwords do not match.";
		if(confirmPass.parentNode.lastChild.id!="Negative-Feedback"){
			confirmPass.parentNode.appendChild(feedback);
		}
		return false;
	}else if(password1.length > 0){
		passInput.classList.remove("is-invalid");
		confirmPass.classList.remove("is-invalid");
		passInput.classList.add("is-valid");
		confirmPass.classList.add("is-valid");
		badFeedback = document.getElementById("Negative-Feedback");
		if(badFeedback!=null){
			badFeedback.parentNode.removeChild(badFeedback);
		}
	}
	return true;

}

function logout(){
	var xhr = new XMLHttpRequest();
	xhr.addEventListener("load",function(){location.reload();});
	xhr.open("GET","/logout",true);
	xhr.send();
}

function loginResults(){
	console.log(this.response);
	if(this.response.includes("Authenticated")){
		console.log("Logged in");
		location.reload();
	}else{
		var container = document.getElementById("content");
		var oldAlert = document.getElementById("alertBox");
		if(oldAlert){
			oldAlert.parentNode.removeChild(oldAlert);
		}
		var alertBox = document.createElement("DIV");
		alertBox.className = "alert alert-danger";
		alertBox.id = "alertBox";
		if(container.lastChild.tagName!="BR"){
			container.innerHTML+="<br><br>"
		}
		alertBox.innerHTML = "<strong>Incorrect Username/Password Combination</strong>"
		container.appendChild(alertBox);
	}
}

function loadPage(){
	var container = document.getElementById("content");
	container.innerHTML = this.response;
}

function getPage(pagename){
	var xhr = new XMLHttpRequest();
	xhr.addEventListener("load",loadPage);
	xhr.responseType="text/html";
	var url = "client/"+pagename
	xhr.open("GET",url,false)
	xhr.send();
}

function getLoginForm(){
	getPage("login.html");
}
function getSignup(){
	getPage("signup.html");
}
function getRedBridge(){
	getPage("redbridge.html");
}
