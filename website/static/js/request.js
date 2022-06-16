function update_fields() {
	fetch('/request')
		.then(function (response) {
			return response.json();
		}).then(function (msg) {
			document.getElementById("temp1").innerHTML = msg.temp1;
			document.getElementById("amps1").innerHTML = msg.amps1;
			document.getElementById("temp2").innerHTML = msg.temp2;
			document.getElementById("amps2").innerHTML = msg.amps2;
			document.getElementById("pressure").innerHTML = msg.pressure;
			document.getElementById("humidity").innerHTML = msg.humidity;
			document.getElementById("eco2").innerHTML = msg.eco2;
			document.getElementById("tvoc").innerHTML = msg.tvoc;
			document.getElementById("co").innerHTML = msg.co;
			document.getElementById("no2").innerHTML = msg.no2;
			document.getElementById("nh3").innerHTML = msg.nh3;
			document.getElementById("presence1").innerHTML = msg.presence1;
			document.getElementById("presence2").innerHTML = msg.presence2;
			document.getElementById("pm25").innerHTML = msg.pm25;
			document.getElementById("pm10").innerHTML = msg.pm10;
			document.getElementById("door").innerHTML = msg.door;
			document.getElementById("luxes").innerHTML = msg.luxes;
			document.getElementById("instructions").innerHTML = msg.instructions;
		});
}

setInterval(function(){
	update_fields();
}, 3000);
