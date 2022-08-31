function mpld3_load_lib(url, callback){
	var s = document.createElement('script');
	s.src = url;
	s.async = true;
	s.onreadystatechange = s.onload = callback;
	s.onerror = function(){console.warn("failed to load library " + url);};
	document.getElementsByTagName("head")[0].appendChild(s);
}

function plot(plot_query) {
	fetch('/plot?begin=' + plot_query.begin + '&end=' + plot_query.end + '&pq=' + plot_query.pq)
		.then(function (response) {
			return response.json();
		}).then(function (data) {

			if(typeof(mpld3) !== "undefined" && mpld3._mpld3IsLoaded){
				// already loaded: just create the figure
				!function(mpld3){

					mpld3.draw_figure("plot", data);
				}(mpld3);
			}else if(typeof define === "function" && define.amd){
				// require.js is available: use it to load d3/mpld3
				require.config({paths: {d3: "https://d3js.org/d3.v5"}});
				require(["d3"], function(d3){
					window.d3 = d3;
					mpld3_load_lib("https://mpld3.github.io/js/mpld3.v0.5.7.js", function(){

						mpld3.draw_figure("plot", data);
					});
				});
			}else{
				// require.js not available: dynamically load d3 & mpld3
				mpld3_load_lib("https://d3js.org/d3.v5.js", function(){
					mpld3_load_lib("https://mpld3.github.io/js/mpld3.v0.5.7.js", function(){

						mpld3.draw_figure("plot", data);
					})
				});
			}
		});
}

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

plot_query = {"begin": "25-6-0", "end": "25-18-0", "pq": "amps"}
plot(plot_query);

setInterval(function(){
	update_fields();
}, 3000);
