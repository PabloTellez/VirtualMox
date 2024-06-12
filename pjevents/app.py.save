from flask import Flask, request, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
import re
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'Usuario1+'  # Necesario para usar mensajes flash

# Configuración de la base de datos
app.config['MYSQL_HOST'] = '192.168.5.26'
app.config['MYSQL_USER'] = 'jmam-pts'
app.config['MYSQL_PASSWORD'] = 'Usuario1+'
app.config['MYSQL_DB'] = 'eventos'

mysql = MySQL(app)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pjevents_1@hotmail.com'
app.config['MAIL_PASSWORD'] = 'Usuario1+'

mail = Mail(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuario_login WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[3])
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido1 = request.form['apellido1']
        apellido2 = request.form.get('apellido2')
        edad = request.form['edad']
        email = request.form['email']

        if not nombre or not apellido1 or not edad or not email:
            flash('Por favor complete todos los campos obligatorios.')
            return redirect(url_for('registrar'))

        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Correo electrónico no válido.')
            return redirect(url_for('registrar'))

        cursor = mysql.connection.cursor()
        # Verificar si ya existe un usuario con el mismo nombre, apellido y correo electrónico
        cursor.execute(
            "SELECT * FROM Usuario WHERE nombre = %s AND apellido1 = %s AND email = %s",
            (nombre, apellido1, email)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Ya existe un usuario con los mismos datos.')
            cursor.close()
            return redirect(url_for('registrar'))

        cursor.execute(
            "INSERT INTO Usuario (nombre, apellido1, apellido2, edad, email) VALUES (%s, %s, %s, %s, %s)",
            (nombre, apellido1, apellido2, edad, email)
        )
        mysql.connection.commit()

        user_id = cursor.lastrowid
        cursor.close()

        return redirect(url_for('confirmacion', user_id=user_id))
    return render_template('registrar.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuario_login WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        if user_data and user_data[2] == password:
            user = User(user_data[0], user_data[1], user_data[3])
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/confirmacion/<int:user_id>')
def confirmacion(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Usuario WHERE id_usuario = %s", (user_id,))
    usuario = cursor.fetchone()
    cursor.close()
    return render_template('confirmacion.html', usuario=usuario)

@app.route('/eventos')
def eventos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Evento")
    eventos = cursor.fetchall()
    cursor.close()
    evento_id = request.args.get('evento_id')  # Obtener el evento_id de los parámetros de la URL
    return render_template('eventos.html', eventos=eventos, evento_id=evento_id)

@app.route('/evento/<int:evento_id>')
def evento(evento_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Evento WHERE id_evento = %s", (evento_id,))
    evento = cursor.fetchone()
    cursor.execute("SELECT Usuario.nombre, Usuario.apellido1, Usuario.apellido2, Reserva.fecha_reserva FROM Usuario JOIN Reserva ON Usuario.id_usuario = Reserva.id_usuario WHERE Reserva.id_evento = %s", (evento_id,))
    asistentes = cursor.fetchall()
    cursor.close()
    return render_template('evento.html', evento=evento, asistentes=asistentes)

@app.route('/crear_evento', methods=['GET', 'POST'])
@login_required
def crear_evento():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']
        ubicacion = request.form['ubicacion']
        max_personas = request.form['max_personas']

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Evento (titulo, descripcion, fecha, ubicacion, max_personas) VALUES (%s, %s, %s, %s, %s)",
            (titulo, descripcion, fecha, ubicacion, max_personas)
        )
        mysql.connection.commit()
        cursor.close()

        # Enviar notificación por correo electrónico
        enviar_notificacion_nuevo_evento(titulo, descripcion, fecha, ubicacion)

        # Flash message
        flash('Evento creado y notificaciones enviadas.', 'success')

	#Redirigir a la misma página para mostrar el mensaje
        return redirect(url_for('crear_evento'))
    return render_template('crear_evento.html')

@app.route('/apuntarse/<int:evento_id>', methods=['GET', 'POST'])
def apuntarse(evento_id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido1 = request.form['apellido1']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id_usuario FROM Usuario WHERE nombre = %s AND apellido1 = %s", (nombre, apellido1))
        usuario_id = cursor.fetchone()
        cursor.close()

        if usuario_id:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM Reserva WHERE id_evento = %s", (evento_id,))
            num_asistentes = cursor.fetchone()[0]

            cursor.execute("SELECT max_personas FROM Evento WHERE id_evento = %s", (evento_id,))
            max_personas = cursor.fetchone()[0]

            if num_asistentes < max_personas:
                cursor.execute(
                    "INSERT INTO Reserva (id_evento, id_usuario, fecha_reserva) VALUES (%s, %s, NOW())",
                    (evento_id, usuario_id)
                )
                mysql.connection.commit()
                flash('Te has apuntado al evento con éxito.')
            else:
                flash('El evento ha alcanzado el máximo de asistentes.')

            cursor.close()
            return redirect(url_for('evento', evento_id=evento_id))
        else:
            flash('Nombre y apellido no encontrados en la base de datos.')
            return redirect(url_for('evento', evento_id=evento_id))
    return render_template('apuntarse.html', evento_id=evento_id)

@app.route('/nosotros')
def nosotros():
    # Código para la página "Nosotros"
    return render_template('nosotros.html')

def enviar_notificacion_nuevo_evento(titulo, descripcion, fecha, ubicacion):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT email FROM Usuario")
    usuarios = cursor.fetchall()
    cursor.close()

    with mail.connect() as conn:
        for usuario in usuarios:
            msg = Message(
                'Nuevo Evento Creado',
                sender='pjevents_1@hotmail.com',
                recipients=[usuario[0]]
            )
            msg.html = render_template(
                'email/nuevo_evento.html',
                titulo=titulo,
                descripcion=descripcion,
                fecha=fecha,
                ubicacion=ubicacion
            )
            conn.send(msg)

if __name__ == '__main__':
    app.run(debug=True)
