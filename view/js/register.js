document.getElementById("form-registro").addEventListener("submit", (e) => {
    e.preventDefault();

    const datos = {
        nombre: document.getElementById("nombre").value,
        apellido: document.getElementById("apellido").value,
        correo: document.getElementById("correo").value,
        telefono: document.getElementById("telefono").value,
        direccion: document.getElementById("direccion").value,
        ciudad: document.getElementById("ciudad").value,
        pais: document.getElementById("pais").value
    };

    console.log("Datos enviados (ejemplo):", datos);

    alert("Registro enviado (ejemplo). Luego se conectará al backend");
});
