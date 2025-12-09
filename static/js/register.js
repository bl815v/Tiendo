// register.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('form-registro');
    const contrasenaInput = document.getElementById('contrasena');
    const confirmarContrasenaInput = document.getElementById('confirmar_contrasena');
    
    if (!form) {
        console.error('Formulario de registro no encontrado');
        return;
    }

    // Validar que las contraseñas coincidan
    function validarContrasenas() {
        const contrasena = contrasenaInput.value;
        const confirmarContrasena = confirmarContrasenaInput.value;
        
        // Remover mensajes anteriores
        const mensajeAnterior = document.getElementById('mensaje-contrasena');
        if (mensajeAnterior) {
            mensajeAnterior.remove();
        }
        
        if (contrasena && confirmarContrasena) {
            const mensaje = document.createElement('div');
            mensaje.id = 'mensaje-contrasena';
            
            if (contrasena === confirmarContrasena) {
                mensaje.textContent = '✓ Las contraseñas coinciden';
                mensaje.className = 'password-match';
            } else {
                mensaje.textContent = '✗ Las contraseñas no coinciden';
                mensaje.className = 'password-mismatch';
            }
            
            confirmarContrasenaInput.parentNode.appendChild(mensaje);
        }
    }
    
    // Escuchar cambios en los campos de contraseña
    if (contrasenaInput && confirmarContrasenaInput) {
        contrasenaInput.addEventListener('input', validarContrasenas);
        confirmarContrasenaInput.addEventListener('input', validarContrasenas);
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validar contraseñas
        if (contrasenaInput.value !== confirmarContrasenaInput.value) {
            alert('Las contraseñas no coinciden');
            return;
        }
        
        if (contrasenaInput.value.length < 6) {
            alert('La contraseña debe tener al menos 6 caracteres');
            return;
        }
        
        // Recolectar datos del formulario
        const datos = {
            nombre: document.getElementById('nombre').value.trim(),
            apellido: document.getElementById('apellido').value.trim(),
            correo: document.getElementById('correo').value.trim(),
            contrasena: contrasenaInput.value,
            telefono: document.getElementById('telefono').value.trim() || null,
            direccion: document.getElementById('direccion').value.trim() || null,
            ciudad: document.getElementById('ciudad').value.trim() || null,
            pais: document.getElementById('pais').value.trim() || null
        };
        
        // Validación básica
        if (!datos.nombre || !datos.apellido || !datos.correo || !datos.contrasena) {
            alert('Por favor, completa los campos obligatorios');
            return;
        }
        
        // Validar email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(datos.correo)) {
            alert('Por favor, ingresa un correo electrónico válido');
            return;
        }
        
        console.log('Intentando registrar usuario:', { ...datos, contrasena: '***' });
        
        try {
            // Mostrar indicador de carga
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Registrando...';
            submitBtn.disabled = true;
            
            // Enviar solicitud a la API
            const response = await fetch('/api/v1/clientes/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(datos)
            });
            
            const responseData = await response.json();
            
            if (!response.ok) {
                // Manejar errores de la API
                let mensajeError = 'Error en el registro';
                if (responseData.detail) {
                    if (typeof responseData.detail === 'string') {
                        mensajeError = responseData.detail;
                    } else if (Array.isArray(responseData.detail)) {
                        mensajeError = responseData.detail.map(err => err.msg).join(', ');
                    }
                }
                throw new Error(mensajeError);
            }
            
            // Éxito en el registro
            console.log('Usuario registrado exitosamente:', responseData);
            
            // Mostrar mensaje de éxito
            alert(`¡Registro exitoso! Bienvenido/a ${datos.nombre}. Tu ID de cliente es: ${responseData.id_cliente}`);
            
            // Cerrar modal después de registro exitoso
            const modal = document.getElementById('modal');
            if (modal) {
                modal.classList.add('hidden');
            }
            
            // Opcional: Redirigir automáticamente o mostrar login
            // window.location.href = '/user';
            
        } catch (error) {
            console.error('Error en el registro:', error);
            alert(`Error al registrar: ${error.message}`);
        } finally {
            // Restaurar botón
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Crear cuenta';
                submitBtn.disabled = false;
            }
        }
    });
    
    // Manejar clic en "Iniciar sesión"
    const goLoginBtn = document.getElementById('go-login');
    if (goLoginBtn) {
        goLoginBtn.addEventListener('click', function() {
            // Cargar formulario de login
            const modalContent = document.getElementById('modal-content');
            if (modalContent) {
                fetch('/login-template')
                    .then(response => response.text())
                    .then(content => {
                        modalContent.innerHTML = content;
                    })
                    .catch(error => {
                        console.error('Error cargando login:', error);
                        modalContent.innerHTML = '<p style="color:#c00">Error cargando formulario.</p>';
                    });
            }
        });
    }
});