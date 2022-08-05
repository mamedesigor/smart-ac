function update_fields() {
	fetch('/request')
		.then(function (response) {
			return response.json();
		}).then(function (msg) {
			document.getElementById("temp1").innerHTML = msg.temp1;
			document.getElementById("amps").innerHTML = msg.amps;
			document.getElementById("temp2").innerHTML = msg.temp2;
			document.getElementById("pressure").innerHTML = msg.pressure;
			document.getElementById("humidity").innerHTML = msg.humidity;
			document.getElementById("eco2").innerHTML = msg.eco2;
			document.getElementById("tvoc").innerHTML = msg.tvoc;
			document.getElementById("motion1").innerHTML = msg.motion1;
			document.getElementById("motion2").innerHTML = msg.motion2;
			document.getElementById("pm25").innerHTML = msg.pm25;
			document.getElementById("pm10").innerHTML = msg.pm10;
			document.getElementById("door1").innerHTML = msg.door1;
			document.getElementById("door2").innerHTML = msg.door2;
			document.getElementById("luxes").innerHTML = msg.luxes;
			document.getElementById("instructions").innerHTML = msg.instructions;
		});
}

setInterval(function(){
	update_fields();
}, 3000);
