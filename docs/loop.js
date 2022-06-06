

for (let i=0; i<8; i++){
   setTimeout(() => {
      console.log(i)
      document.getElementById("temp").innerHTML = i;
  }, 2000 * i);
}