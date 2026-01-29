// Obtener elementos HTML
var modal = document.getElementById('myModal');
var btn = document.getElementById("openModalBtn");
var span = document.getElementsByClassName("close")[0];

// Cuando se hace clic en el botón, abrir la ventana modal
btn.onclick = function() {
  modal.style.display = "block";
}

// Cuando se hace clic en la "x", cerrar la ventana modal
span.onclick = function() {
  modal.style.display = "none";
}

// Cuando el usuario hace clic fuera de la ventana modal, cerrarla
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}
