document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form-registro');
    const contrasenaInput = document.getElementById('contrasena');
    const confirmarContrasenaInput = document.getElementById('confirmar_contrasena');

    if (!form) {
        console.error('Formulario de registro no encontrado');
        return;
    }

    /**
     * Valida si los valores de los campos de contraseña y confirmación de contraseña coinciden.
     * Muestra un mensaje visual debajo del campo de confirmación indicando si las contraseñas coinciden o no.
     * Elimina cualquier mensaje anterior antes de mostrar uno nuevo.
     *
     * Dependencias:
     * - Deben existir los elementos `contrasenaInput` y `confirmarContrasenaInput` en el ámbito global.
     * - El mensaje se inserta como un elemento `<div>` con id 'mensaje-contrasena' como hijo del padre de `confirmarContrasenaInput`.
     */
    function validarContrasenas() {
        const contrasena = contrasenaInput.value;
        const confirmarContrasena = confirmarContrasenaInput.value;

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

    if (contrasenaInput && confirmarContrasenaInput) {
        contrasenaInput.addEventListener('input', validarContrasenas);
        confirmarContrasenaInput.addEventListener('input', validarContrasenas);
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        if (contrasenaInput.value !== confirmarContrasenaInput.value) {
            alert('Las contraseñas no coinciden');
            return;
        }

        if (contrasenaInput.value.length < 6) {
            alert('La contraseña debe tener al menos 6 caracteres');
            return;
        }

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

        if (!datos.nombre || !datos.apellido || !datos.correo || !datos.contrasena) {
            alert('Por favor, completa los campos obligatorios');
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(datos.correo)) {
            alert('Por favor, ingresa un correo electrónico válido');
            return;
        }

        console.log('Intentando registrar usuario:', { ...datos, contrasena: '***' });

        try {
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Registrando...';
            submitBtn.disabled = true;

            const response = await fetch('/api/v1/clientes/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(datos)
            });

            const responseData = await response.json();

            if (!response.ok) {
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

            console.log('Usuario registrado exitosamente:', responseData);

            alert(`¡Registro exitoso! Bienvenido/a ${datos.nombre}. Tu ID de cliente es: ${responseData.id_cliente}`);

            const modal = document.getElementById('modal');
            if (modal) {
                modal.classList.add('hidden');
            }

        } catch (error) {
            console.error('Error en el registro:', error);
            alert(`Error al registrar: ${error.message}`);
        } finally {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Crear cuenta';
                submitBtn.disabled = false;
            }
        }
    });

    const goLoginBtn = document.getElementById('go-login');
    if (goLoginBtn) {
        goLoginBtn.addEventListener('click', function () {
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