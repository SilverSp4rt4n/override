//Send controller widget state
function sendState(widgetID,xValue,yValue){

}

//Joystick Widget
var bigRadius = 0;
var littleRadius = 0;

function addJoyStick(){
	var canvas = document.createElement("CANVAS");
	var jID = 0;
	var canvasName = "joyStick" + jID;
	bigRadius = document.body.clientWidth / 5;
	littleRadius = document.body.clientWidth / 13;
	while(typeof(document.getElementById(canvasName)) != 'undefined' && document.getElementById(canvasName) != null){
		jID+=1;
		canvasName = "joyStick" + jID;
	}
	canvas.setAttribute("id",canvasName);
	canvas.setAttribute("onmousedown","grabJoyStick(this,event);");
	canvas.setAttribute("ontouchstart","grabJoyStick(this,event);");
	canvas.width = 2*(document.body.clientWidth / 5)
	canvas.height = 2*(document.body.clientWidth / 5)
	var ctx = canvas.getContext("2d");
	ctx.beginPath();
	ctx.arc(canvas.width/2, canvas.height/2, bigRadius, 0, 2 * Math.PI);
	ctx.fillStyle = "gray";	
	ctx.fill();
	ctx.beginPath();
	ctx.arc(canvas.width/2, canvas.height/2, littleRadius, 0, 2 * Math.PI);
	ctx.fillStyle = "black";
	ctx.fill();
	
	document.getElementById("controllerSpace").appendChild(canvas);
}

function grabJoyStick(element,event){
	document.body.setAttribute("onmousemove","moveJoyStick("+element.id+",event)");
	element.setAttribute("ontouchmove","moveJoyStick("+element.id+",event)");
	document.body.setAttribute("onmouseup","releaseJoyStick("+element.id+");");
	element.setAttribute("ontouchend","releaseJoyStick("+element.id+");");
	if(event.touches != null && event.touches.length>0){
		event.preventDefault();
		document.body.setAttribute("position","fixed");
		document.body.setAttribute("overflow","hidden");
	}
}

function releaseJoyStick(element){
	var canvas = element;
	document.body.setAttribute("onmousemove","null");
	document.body.setAttribute("onmouseup","null");
	//document.body.setAttribute("ontouchmove","null");
	//document.body.setAttribute("ontouchend","null");
	var ctx = canvas.getContext("2d");
	ctx = canvas.getContext("2d");
	//Clear previous frame
	ctx.clearRect(0,0,canvas.width,canvas.height);
	ctx.beginPath();
	ctx.arc(canvas.width/2, canvas.height/2, bigRadius, 0, 2 * Math.PI);
	ctx.fillStyle = "gray";	
	ctx.fill();
	ctx.beginPath();
	ctx.arc(canvas.width/2, canvas.height/2, littleRadius, 0, 2 * Math.PI);
	ctx.fillStyle = "black";
	ctx.fill();
	sendCData(element.id,0.0,0.0);
}

function moveJoyStick(element,event){
	var canvas = element;
	var mouseX;
	var mouseY;
	var maxDist = bigRadius - littleRadius;
	if(event.touches != null && event.touches.length>0){
		var touchIndex = 0;
		for(var i = 0; i < event.touches.length; i++){
			if(event.touches[i].target == element){
				touchIndex = i;
			}
		}
		mouseX = event.touches[touchIndex].clientX;
		mouseY = event.touches[touchIndex].clientY;
	}else{
		mouseX = event.clientX;
		mouseY = event.clientY;
	}
	var elementX = element.getBoundingClientRect().left;
	var elementY = element.getBoundingClientRect().top
	//Middle of canvas/big circle
	var centerX = canvas.width / 2; //RELATIVE
	var centerY = canvas.height / 2; //RELATIVE
	var ctx = canvas.getContext("2d");
	ctx = canvas.getContext("2d");
	//Coordinates of the inner circle
	var innerX = mouseX - elementX;
	var innerY = mouseY - elementY;
	//Calculate unit vector from center
	var magnitude = Math.sqrt((Math.pow(innerX,2) + Math.pow(innerY,2)));
	var unitX = (innerX-centerX) / magnitude;
	var unitY = (innerY-centerY) / magnitude;
	var calcX = innerX-centerX;
	var calcY = innerY-centerY;
	var distance = Math.sqrt(Math.pow(calcX,2)+Math.pow(calcY,2))
	while(distance > maxDist){
		innerX -= unitX;
		innerY -= unitY;
		distance = Math.sqrt(Math.pow((innerX-centerX),2)+Math.pow((innerY-centerY),2))
	}
	

	//Clear previous frame
	ctx.clearRect(0,0,canvas.width,canvas.height);
	ctx.beginPath();
	ctx.arc(centerX, centerY, bigRadius, 0, 2 * Math.PI);
	ctx.fillStyle = "gray";	
	ctx.fill();
	ctx.beginPath();
	ctx.arc(innerX, innerY, littleRadius, 0, 2 * Math.PI);
	ctx.fillStyle = "black";
	ctx.fill();
	var outputX = (innerX - centerX) / maxDist;
	var outputY = (innerY - centerY) / maxDist;
	console.log(outputX + ", " + outputY)
	sendCData(element.id,outputX,outputY);
}
