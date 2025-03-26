import os
from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or os.urandom(24).hex()

# Usuarios predefinidos (sin base de datos)
USUARIOS = {
    "admin": {
        "password": generate_password_hash("admin123"),
        "rol": "admin"
    },
    "viewer": {
        "password": generate_password_hash("viewer123"),
        "rol": "viewer"
    }
}

# Lista global de equipos disponibles
EQUIPOS_DISPONIBLES = [
    "Barcelona", "Real Madrid", "Manchester United",
    "Bayern Múnich", "Juventus", "PSG"
]

# Datos de jugadores en memoria (sin base de datos)
jugadores = [
    {
        "Dorsal": "10",
        "Nombre": "Lionel",
        "Ap_paterno": "Messi",
        "Ap_materno": "Cuccitini",
        "Edad_en_años": 36,
        "Equipo": "Inter Miami"
    }
]

# Decorador para verificar roles
def requiere_rol(rol):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session or USUARIOS.get(session['username'], {}).get('rol') != rol:
                flash('Acceso denegado: No tienes permisos suficientes', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = USUARIOS.get(username)
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['user_rol'] = user['rol']
            flash('¡Bienvenido!', 'success')
            return redirect(url_for('index'))
        
        flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

# Rutas principales
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html', 
                         jugadores=jugadores,
                         es_admin=session.get('user_rol') == 'admin')

# Rutas CRUD (solo admin)
@app.route('/jugadores/new', methods=['GET', 'POST'])
@requiere_rol('admin')
def create_jugador():
    if request.method == 'POST':
        nuevo_jugador = {
            "Dorsal": request.form.get('Dorsal'),
            "Nombre": request.form.get('Nombre'),
            "Ap_paterno": request.form.get('Ap_paterno'),
            "Ap_materno": request.form.get('Ap_materno'),
            "Edad_en_años": int(request.form.get('Edad_en_años')),
            "Equipo": request.form.get('Equipo')
        }
        jugadores.append(nuevo_jugador)
        flash('Jugador creado exitosamente', 'success')
        return redirect(url_for('index'))
    
    return render_template('create_jugador.html', equipos=EQUIPOS_DISPONIBLES)

@app.route('/jugadores/delete/<string:Dorsal>')
@requiere_rol('admin')
def delete_jugador(Dorsal):
    global jugadores
    jugadores = [j for j in jugadores if j['Dorsal'] != Dorsal]
    flash('Jugador eliminado exitosamente', 'success')
    return redirect(url_for('index'))

@app.route('/jugadores/update/<string:Dorsal>', methods=['GET', 'POST'])
@requiere_rol('admin')
def update_jugador(Dorsal):
    jugador = next((j for j in jugadores if j['Dorsal'] == Dorsal), None)
    
    if not jugador:
        flash('Jugador no encontrado', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        jugador.update({
            "Nombre": request.form.get('Nombre'),
            "Ap_paterno": request.form.get('Ap_paterno'),
            "Ap_materno": request.form.get('Ap_materno'),
            "Edad_en_años": int(request.form.get('Edad_en_años')),
            "Equipo": request.form.get('Equipo')
        })
        flash('Jugador actualizado exitosamente', 'success')
        return redirect(url_for('index'))
    
    return render_template('update_jugador.html', 
                         jugador=jugador,
                         equipos=EQUIPOS_DISPONIBLES)

if __name__ == '__main__':
    app.run(debug=True)