function update_fields() {
	fetch('/request')
		.then(function (response) {
			return response.json();
		}).then(function (msg) {
			document.getElementById("temp1").innerHTML = msg.temp1;
			document.getElementById("temp2").innerHTML = msg.temp2;
		});
}

update_fields();
