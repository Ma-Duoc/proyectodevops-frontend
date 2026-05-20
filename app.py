# Importar librerías necesarias
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear instancia de la aplicación Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave_secreta_por_defecto')

# Habilitar CORS para permitir peticiones desde otros orígenes
CORS(app)

# Configuración de la URL del backend API
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:3000')

# Ruta principal - muestra la página de inicio
@app.route('/')
def index():
    try:
        response = requests.get(f'{BACKEND_URL.rstrip("/")}/api/usuarios')

        if response.status_code == 200:
            usuarios = response.json()
            return render_template('index.html', usuarios=usuarios)
        else:
            flash('Error al obtener los usuarios del servidor', 'error')
            return render_template('index.html', usuarios=[])

    except requests.exceptions.RequestException as e:
        print(f'Error de conexión con el backend: {e}')
        flash('No se pudo conectar con el servidor backend', 'error')
        return render_template('index.html', usuarios=[])


@app.route('/crear')
def crear_usuario_form():
    return render_template('crear_usuario.html')


@app.route('/crear', methods=['POST'])
def crear_usuario():
    try:
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        edad = request.form.get('edad')

        if not nombre or not email:
            flash('El nombre y el email son obligatorios', 'error')
            return redirect(url_for('crear_usuario_form'))

        datos_usuario = {
            'nombre': nombre,
            'email': email,
            'edad': int(edad) if edad else None
        }

        response = requests.post(
            f'{BACKEND_URL.rstrip("/")}/api/usuarios',
            json=datos_usuario,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 201:
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('index'))
        else:
            error_data = response.json()
            flash(f'Error al crear usuario: {error_data.get("error", "Error desconocido")}', 'error')
            return redirect(url_for('crear_usuario_form'))

    except Exception as e:
        print(f'Error: {e}')
        flash('No se pudo conectar con el servidor backend', 'error')
        return redirect(url_for('crear_usuario_form'))


@app.route('/editar/<int:usuario_id>')
def editar_usuario_form(usuario_id):
    try:
        response = requests.get(f'{BACKEND_URL.rstrip("/")}/api/usuarios')

        if response.status_code == 200:
            usuarios = response.json()
            usuario = next((u for u in usuarios if u['id'] == usuario_id), None)

            if usuario:
                return render_template('editar_usuario.html', usuario=usuario)

        flash('Error al obtener los datos del usuario', 'error')
        return redirect(url_for('index'))

    except Exception as e:
        print(f'Error: {e}')
        flash('No se pudo conectar con el servidor backend', 'error')
        return redirect(url_for('index'))


@app.route('/editar/<int:usuario_id>', methods=['POST'])
def editar_usuario(usuario_id):
    try:
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        edad = request.form.get('edad')

        datos_usuario = {
            'nombre': nombre,
            'email': email,
            'edad': int(edad) if edad else None
        }

        response = requests.put(
            f'{BACKEND_URL.rstrip("/")}/api/usuarios/{usuario_id}',
            json=datos_usuario,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            flash('Usuario actualizado exitosamente', 'success')
        else:
            flash('Error al actualizar usuario', 'error')

        return redirect(url_for('index'))

    except Exception as e:
        print(f'Error: {e}')
        flash('Error de conexión con backend', 'error')
        return redirect(url_for('index'))


@app.route('/eliminar/<int:usuario_id>', methods=['POST'])
def eliminar_usuario(usuario_id):
    try:
        response = requests.delete(
            f'{BACKEND_URL.rstrip("/")}/api/usuarios/{usuario_id}'
        )

        if response.status_code == 200:
            flash('Usuario eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar usuario', 'error')

    except Exception as e:
        print(f'Error: {e}')
        flash('No se pudo conectar con el servidor backend', 'error')

    return redirect(url_for('index'))


@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_servidor(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'

    print(f'Iniciando servidor Flask en el puerto {port}')
    print(f'URL del backend: {BACKEND_URL}')

    app.run(host='0.0.0.0', port=port, debug=debug_mode)   