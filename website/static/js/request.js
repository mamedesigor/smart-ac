function update_fields() {
	fetch('/request')
		.then(function (response) {
			return response.json();
		}).then(function (msg) {
			document.getElementById("temp").innerHTML = msg.temp1;
		});
}

update_fields();
