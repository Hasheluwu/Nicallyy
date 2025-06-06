# NICALLY
                        #### Video Demo:https://youtu.be/XYmbKW6W1Tc?si=_WwIrYMj2gn8kTbL
                        #### Description:Nically es una pagina educativa de trivias, su enfoque es dar a conocer sobre la cultura Nicaraguense de una forma interactiva y
                        
divertida, ya sea para niños o adultos extranjeros. La pagina cuenta con diferentes categorias de trivias, cada una con sus
preguntas y respuestas, los usuarios tienen 3 intentos por trivia para contestar las preguntas, si pierde todas sus vidas seran
devueltos a la pagina principal con su progreso actual en la trivia guardado, asi hasta que la completen y sucesivamente
completen todas las trivias, ganando trofeos mediante complete mas trivias.

Tambien hay un apartado de enciclopedia que brinda toda la informacion necesaria para poder resolver las trivias [esta algo
incompleta], aparte de eso que seria lo principal, la pagina ofrece un sistema de registro y login, el usuario se registra y
se guarda en la base de datos, usando sessions podemos guardar el progreso de cada usuario individualmente haciendo posible que
[con unas cuantas actualizaciones mas] sea una pagina online y con aptitudes sociales.

en el apartado de ajustes y perfil tenemos las opciones de borrar la cuenta actual, editar los datos del usuario, reiniciar el
progreso de las trivias para poder empezar denuevo y disfrutar de la pagina otra vez, y poder ver tu historial de respuestas en
el cual ves las respuestas incorrectas y correctas que brindastastes en las trivias.

Toda la pagina es responsive para poder ser vista en cualquier dispositivo moderno, ya sea celular, tablet o computadora.

Habiendo concluido todo esto voy a explicar las partes que componen la pagina y como se conectan entre si.


Herramientas que se utilizaron: FLASK- PYTHON, HTML, CSS-TAILWIND, JS, SQL, GITHUB.


Primeramente comenzamos creando el sistema de ingreso de usuario y manejo de sesiones, para eso creamos un archivo llamado
app.py donde creamos las primeras rutas, register y login, estas usando el session_id de la librerias.

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from helpers import login_required, is_valid_email, is_secure_password
from datetime import timedelta, datetime

Las otras librerias sirven para hacer las validaciones necesarias para obtener los metadatos del usuario de manera exitosa
ya sea el email o la contraseña, tambien para poder manejar las sesiones de manera correcta.

Despues de haber creado el sistema de sesiones con el register y login, ademas del logout que fue facil, solo usamos el session.
pop(user_id), empezamos a indagar en que podiamos hacer para que la pagina fuera mas interactiva y divertida, asi que decidimos
usar tailwind.

Esto al principio fue un problema enorme, ya que nunca habiamos usado tailwind, y ninguno de los tutores lo manejaba bien tampoco
tuvimos que indagar mucho por cada nueva feature y cambio que haciamos, todas las ideas poco a poco cobraban vida a prueba y error
pero al final valio la pena porque tailwind es muy util para hacer paginas responsive y con un diseño muy atractivo, ya hay muchas
plantillas disponibles solo para implementar y modificar a tu antojo, todas las clases que incluyen aunque dificiles de recordar
al principio facilitan mucho la tarea de tener diseños atractivos y responsivos.

Despues de eso mas de lo mismo.

# User registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        gmail = request.form.get("gmail")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not gmail or not is_valid_email(gmail):
            return render_template("register.html", error_message="Por favor, introduce un correo electrónico válido.")

        existing_user = db.execute("SELECT * FROM users WHERE gmail = ?", gmail)
        if existing_user:
            return render_template("register.html", error_message="El correo ya está registrado.")

        if not is_secure_password(password):
            return render_template("register.html", error_message="La contraseña no es segura, añade al menos un número, mayúscula y símbolo especial.")
        if password != confirmation:
            return render_template("register.html", error_message="Las contraseñas no coinciden.")

        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (gmail, password) VALUES (?, ?)", gmail, password_hash)
        return redirect("/login")
    else:
        return render_template("register.html")

# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        gmail = request.form.get("gmail")
        password = request.form.get("password")

        if not gmail or not password:
            return render_template("login.html", error_message="Debes completar ambos campos.")

        user = db.execute("SELECT * FROM users WHERE gmail = ?", gmail)
        if not user or not check_password_hash(user[0]["password"], password):
            return render_template("login.html", error_message="Correo o contraseña incorrectos.")

        session["user_id"] = user[0]["id"]
        session.permanent = True
        return redirect("/profile")
    return render_template("login.html")

# User profile
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    current_date = datetime.now().strftime('%Y-%m-%d')
    if request.method == "POST":
        username = request.form.get("username")
        gender = request.form.get("gender")
        birthday = request.form.get("birthday")

        if not username or not gender or not birthday or birthday > current_date:
            return render_template("profile.html", error_message="Datos inválidos.", current_date=current_date)

        db.execute("UPDATE users SET username = ?, gender = ?, birthday = ? WHERE id = ?", username, gender, birthday, session["user_id"])
        return redirect("/")
    return render_template("profile.html", current_date=current_date)


@app.route("/user_profile", methods=["GET"])
@login_required
def user_profile():
    user_id = session["user_id"]

    # Consultar los datos del usuario
    user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    username = user_data[0]["username"]
    gender = user_data[0]["gender"]
    birthday = user_data[0]["birthday"]

    # Consultar los logros del usuario
    achievements = db.execute("""
        SELECT achievements.title
        FROM user_achievements
        JOIN achievements ON user_achievements.achievement_id = achievements.achievement_id
        WHERE user_achievements.user_id = ?
    """, user_id)

    return render_template(
        "user_profile.html",
        username=username,
        genre=gender,
        birthday=birthday,
        achievements=achievements
    )


Creamos las rutas para el ingreso de los metadatos de el usuario como el nombre, la contraseña y el genero por ejemplo.
luego creamos otra ruta para mostrar esos datos en una pagina de perfil del usuario.

Cabe aclarar que para todas estas paginas usamos un layout.html el cual contiene una navbar conectado a todas las rutas de
el app.py.

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Website{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.0.0/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" rel="stylesheet">
    <link href="../static/styles.css">
</head>

<body class="bg-gray-100">
    <!-- Navbar -->
    <nav style="background-color: #333c87;" class="bg-blue-500 p-4">
        <div class="container mx-auto flex justify-between items-center">
            <a href="/" class="text-white text-lg font-bold"> <i class="fa-solid fa-house"></i> Nically</a>

            <!-- Botón para menú en dispositivos pequeños -->
            <button id="menu-toggle" class="block md:hidden text-white">
                <i class="fa-solid fa-bars"></i>
            </button>

            <!-- Menú de navegación -->
            <div id="menu" class="hidden md:flex space-x-4">
                <a href="/enciclopedia" class="text-white hover:bg-blue-700 px-3 py-2 rounded">
                    <i class="fa-solid fa-landmark"></i> Enciclopedia
                </a>
                <a href="/achievements" class="text-white hover:bg-blue-700 px-3 py-2 rounded">
                    <i class="fa-solid fa-crown"></i> Trofeos
                </a>
                <a href="/settings" class="text-white hover:bg-blue-700 px-3 py-2 rounded">
                    <i class="fa-solid fa-gear"></i> Ajustes
                </a>
                <a href="/user_profile" class="text-white hover:bg-blue-700 px-3 py-2 rounded">
                    <i class="fa-solid fa-user"></i> Perfil
                </a>

                {% if not session.get('user_id') %}
                <a href="/login" class="text-white hover:bg-blue-700 px-3 py-2 rounded">
                    <i class="fa-solid fa-pen-to-square"></i> Login
                </a>
                <a href="/register" class="text-white hover:bg-blue-700 px-3 py-2 rounded">
                    <i class="fa-solid fa-file"></i> Register
                </a>
                {% else %}
                <a href="/logout" class="text-white hover:bg-blue-700 px-3 py-2 rounded">
                    <i class="fa-solid fa-user-minus"></i> Logout
                </a>
                <h class="text-white hover:bg-blue-700 px-3 py-2 rounded">
                    <i class="fa-solid fa-cube"></i> Bienvenido {{ username }}
                </h>
                {% endif %}

                <button id="dark-mode-toggle" class="text-white hover:bg-blue-700 px-3 py-2 rounded">
                    <i class="fa-solid fa-moon"></i>
                </button>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container mx-auto p-4">
        {% block main %}{% endblock %}
    </div>

    <script>
        // Navbar toggle para dispositivos móviles
        const toggle = document.getElementById('menu-toggle');
        const menu = document.getElementById('menu');
        toggle.addEventListener('click', () => {
            menu.classList.toggle('hidden');
        });

        // Dark mode toggle
        document.addEventListener('DOMContentLoaded', function () {
            if ("{{ session.get('dark-mode') }}" === "enabled") {
                document.documentElement.classList.add('dark-mode');
            }
            document.querySelector('#dark-mode-toggle').addEventListener('click', () => {
                document.documentElement.classList.toggle('dark-mode');
                fetch('/toggle-dark-mode', { method: 'POST' });
            });
        });
    </script>
</body>
</html>


Despues de haber creado todo esto empezamos con la parte mas dificil, el crear la plantilla para el contenido principal la base
de datos y la logica de las trivias, para esto primero creamos la ruta de index, ya estaba desde antes pero te redirigia al
register si no habias iniciado sesion.


En esta ruta index necesitabamos una base de datos con la informacion de las trivias, [categorias, preguntas, opciones,
respuestas, puntajes], para esto creamos un modelo de base de datos que sufrio muchos cambios. aqui dejo el finalizado.


CREATE TABLE users (
  id integer,
  gmail text,
  password text,
  username text,
  gender char(1),
  birthday integer,
  PRIMARY KEY (id)
)

CREATE TABLE achievements (
  achievement_id integer,
  title text,
  description text,
  PRIMARY KEY(achievement_id)
)

CREATE TABLE user_achievements (
  user_id integer,
  achievement_id integer,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (achievement_id) REFERENCES achievements(achievement_id)
)


CREATE TABLE categories (
  category_id integer,
  name text,
  PRIMARY KEY (category_id)
)


CREATE TABLE trivias (
  trivia_id integer,
  user_id integer,
  category_id integer,
  title text,
  image text,
  points integer,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
  PRIMARY KEY (trivia_id)
)

CREATE TABLE questions (
  question_id integer,
  trivia_id integer,
  question_text text,
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id),
  PRIMARY KEY (question_id)
)

CREATE TABLE responses (
  response_id integer,
  trivia_id integer,
  question_id integer,
  response_text text,
  correct boolean,
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id),
  FOREIGN KEY (question_id) REFERENCES questions(question_id),
  PRIMARY KEY (response_id)
)

CREATE TABLE user_trivias (
  user_id integer,
  trivia_id integer,
  date_played text,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id)
)

CREATE TABLE user_responses (
    user_id integer,
    trivia_id integer,
    response_id integer,
    correct boolean,
    attempted boolean,
    PRIMARY KEY (user_id, trivia_id, response_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id),
    FOREIGN KEY (response_id) REFERENCES responses(response_id)
);


Todas las tablas estan interconectadas mediante FOREIGN KEYS, y PRIMARY KEYS, las tablas que contienen un user_, son tablas de rel
acion, que contienen la informacion de los usuarios que han jugado a la trivia, solo manejan los id's de los datos que es necesar
ario acceder mas adelante.

despues de esto rellenamos la trivia con este archivo de aqui.



from cs50 import SQL

# Conectar a la base de datos
db = SQL("sqlite:///users.db")

# Limpiar tablas existentes
tables = ["user_responses", "user_trivias", "responses", "questions", "trivias", "categories"]
for table in tables:
    db.execute(f"DELETE FROM {table};")



# Insertar categorías
db.execute("""
    INSERT INTO categories (category_id, name) VALUES
    (1, 'Cultura General'),
    (2, 'Historia'),
    (3, 'Gastronomía'),
    (4, 'Arte'),
    (5, 'Tradiciones');
""")

# Insertar trivias
db.execute("""
    INSERT INTO trivias (trivia_id, user_id, category_id, title, image, points) VALUES
    (1, NULL, 1, 'Símbolos Nacionales de Nicaragua', '/static/Simbolos_nacionales.jpg', 10),
    (2, NULL, 2, 'Historia de Nicaragua', '/static/historia.jpg', 15),
    (3, NULL, 3, 'Gastronomía Nicaragüense', '/static/gastronomia.jpg', 20),
    (4, NULL, 4, 'Literatura Nicaragüense', '/static/literatura.jpg', 25),
    (5, NULL, 5, 'Leyendas de Nicaragua', '/static/leyendas.jpg', 30),
    (6, NULL, 4, 'Flora y fauna', '/static/fauna.jpg', 10),
    (7, NULL, 2, 'Geografia', '/static/geografia.jpg', 15),
    (8, NULL, 1, 'Festividades', '/static/festividades.jpg', 20),
    (9, NULL, 5, 'Economia', '/static/economia.jpg', 25),
    (10, NULL, 3, 'Turismo', '/static/turismo.jpg', 30);
""")

# Insertar preguntas y respuestas para Trivia 1: Símbolos Nacionales de Nicaragua
db.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (1, 1, '¿Cuál es el símbolo nacional de Nicaragua que aparece en el centro de la bandera?'),
    (2, 1, '¿Qué representan los cinco volcanes en el escudo de armas de Nicaragua?'),
    (3, 1, '¿Cuál es la flor nacional de Nicaragua?'),
    (4, 1, '¿Qué significa el sol en el escudo de armas de Nicaragua?');
""")

db.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text, correct) VALUES
    (1, 1, 1, 'Un triángulo equilátero', 1),
    (2, 1, 1, 'Un rectángulo azul', 0),
    (3, 1, 1, 'Un círculo dorado', 0),
    (4, 2, 1, 'Los cinco países de Centroamérica', 1),
    (5, 2, 1, 'Las cinco montañas más altas', 0),
    (6, 2, 1, 'Las cinco luchas por la independencia', 0),
    (7, 3, 1, 'Sacuanjoche', 1),
    (8, 3, 1, 'Flor de Mayo', 0),
    (9, 3, 1, 'Jazmín', 0),
    (10, 4, 1, 'La libertad', 1),
    (11, 4, 1, 'La unidad', 0),
    (12, 4, 1, 'La justicia', 0);
""")

# Insertar preguntas y respuestas para Trivia 2: Historia de Nicaragua
db.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (5, 2, '¿En qué año se independizó Nicaragua de España?'),
    (6, 2, '¿Qué conflicto armado ocurrió en Nicaragua entre 1981 y 1990?'),
    (7, 2, '¿Quién fue el líder del Frente Sandinista de Liberación Nacional (FSLN) que llegó al poder en 1979?'),
    (8, 2, '¿Qué evento marcó el fin de la dictadura somocista?');
""")

db.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text, correct) VALUES
    (13, 5, 2, '1821', 1),
    (14, 5, 2, '1905', 0),
    (15, 5, 2, '1838', 0),
    (16, 6, 2, 'La Guerra de los Contras', 1),
    (17, 6, 2, 'La Revolución Liberal', 0),
    (18, 6, 2, 'La Guerra Fría', 0),
    (19, 7, 2, 'Daniel Ortega', 1),
    (20, 7, 2, 'Anastasio Somoza', 0),
    (21, 7, 2, 'Violeta Barrios', 0),
    (22, 8, 2, 'La Revolución Sandinista', 1),
    (23, 8, 2, 'La Guerra de los Contras', 0),
    (24, 8, 2, 'La Revolución Liberal', 0);
""")

# Insertar preguntas y respuestas para Trivia 3: Gastronomía Nicaragüense
db.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (9, 3, '¿Cuál es el plato nacional de Nicaragua?'),
    (10, 3, '¿Qué bebida tradicional se elabora con maíz fermentado?'),
    (11, 3, '¿Qué dulce típico es originario de León?'),
    (12, 3, '¿Cuál es la bebida típica que se toma en las fiestas de Nicaragua?');
""")

db.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text, correct) VALUES
    (25, 9, 3, 'Gallo Pinto', 1),
    (26, 9, 3, 'Baho', 0),
    (27, 9, 3, 'Vigorón', 0),
    (28, 10, 3, 'Chicha', 1),
    (29, 10, 3, 'Pinolillo', 0),
    (30, 10, 3, 'Cacao', 0),
    (31, 11, 3, 'Cajeta de leche', 1),
    (32, 11, 3, 'Rosquillas', 0),
    (33, 11, 3, 'Turrón', 0),
    (34, 12, 3, 'Ron', 1),
    (35, 12, 3, 'Cerveza', 0),
    (36, 12, 3, 'Café', 0);
""")

# Insertar preguntas y respuestas para Trivia 4: Literatura Nicaragüense
db.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (13, 4, '¿Quién es considerado el poeta más importante de Nicaragua?'),
    (14, 4, '¿En qué año Rubén Darío publicó *Azul*?'),
    (15, 4, '¿Qué corriente literaria es asociada con Rubén Darío?'),
    (16, 4, '¿Qué poeta nicaragüense ganó el Premio Cervantes en 2005?');
""")

db.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text, correct) VALUES
    (37, 13, 4, 'Rubén Darío', 1),
    (38, 13, 4, 'Ernesto Cardenal', 0),
    (39, 13, 4, 'Salomón de la Selva', 0),
    (40, 14, 4, '1888', 1),
    (41, 14, 4, '1890', 0),
    (42, 14, 4, '1875', 0),
    (43, 15, 4, 'Modernismo', 1),
    (44, 15, 4, 'Romanticismo', 0),
    (45, 15, 4, 'Realismo', 0),
    (46, 16, 4, 'Carlos Martínez Rivas', 1),
    (47, 16, 4, 'Gioconda Belli', 0),
    (48, 16, 4, 'Darío Jaramillo', 0);
""")

# Insertar preguntas y respuestas para Trivia 5: Leyendas de Nicaragua
db.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (17, 5, '¿Qué leyenda nicaragüense habla de una mujer que perdió su hijo en un naufragio?'),
    (18, 5, '¿Cómo se llama el fantasma que persigue a las personas en las montañas nicaragüenses?'),
    (19, 5, '¿Cuál es la leyenda que habla de un hombre que transformó su alma en un perro?'),
    (20, 5, '¿Qué leyenda se asocia con un demonio que castiga a los habitantes de una ciudad?');
""")

db.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text, correct) VALUES
    (49, 17, 5, 'La Llorona', 1),
    (50, 17, 5, 'El Cipitío', 0),
    (51, 17, 5, 'El Sombrerón', 0),
    (52, 18, 5, 'El Cadejo', 1),
    (53, 18, 5, 'El Duende', 0),
    (54, 18, 5, 'La Mocuana', 0),
    (55, 19, 5, 'El Chacal', 1),
    (56, 19, 5, 'El Sapo', 0),
    (57, 19, 5, 'El Brujo', 0),
    (58, 20, 5, 'La Sombra del Diablo', 1),
    (59, 20, 5, 'La Luz Mala', 0),
    (60, 20, 5, 'La Sombra del Viento', 0);
""")

# Insertar preguntas y respuestas para Trivia 6: Flora y Fauna de Nicaragua
db.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (21, 6, '¿Cuál es el ave nacional de Nicaragua?'),
    (22, 6, '¿Qué animal es considerado símbolo de la fauna de Nicaragua?'),
    (23, 6, '¿Cuál es el árbol nacional de Nicaragua?'),
    (24, 6, '¿Qué especie de tortuga se encuentra en las costas de Nicaragua?');
""")

db.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text, correct) VALUES
    (61, 21, 6, 'La Guacamaya', 1),
    (62, 21, 6, 'El Quetzal', 0),
    (63, 21, 6, 'El Tucán', 0),
    (64, 22, 6, 'El Jaguar', 1),
    (65, 22, 6, 'El Mono Araña', 0),
    (66, 22, 6, 'El León', 0),
    (67, 23, 6, 'El Ceibo', 1),
    (68, 23, 6, 'El Pinus', 0),
    (69, 23, 6, 'El Roble', 0),
    (70, 24, 6, 'La Tortuga Carey', 1),
    (71, 24, 6, 'La Tortuga Baula', 0),
    (72, 24, 6, 'La Tortuga Verde', 0);
""")

# Insertar preguntas y respuestas para Trivia 7: Geografía de Nicaragua
db.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (25, 7, '¿Cuál es el lago más grande de Nicaragua?'),
    (26, 7, '¿En qué departamento se encuentra la ciudad de León?'),
    (27, 7, '¿Qué océano baña las costas del país al oeste?'),
    (28, 7, '¿Cuál es el río más largo de Nicaragua?');
""")

db.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text, correct) VALUES
    (73, 25, 7, 'Lago Cocibolca', 1),
    (74, 25, 7, 'Lago Xolotlan', 0),
    (75, 25, 7, 'Lago de Cocibolca', 0),
    (76, 26, 7, 'León', 1),
    (77, 26, 7, 'Chinandega', 0),
    (78, 26, 7, 'Managua', 0),
    (79, 27, 7, 'Océano Pacífico', 1),
    (80, 27, 7, 'Océano Atlántico', 0),
    (81, 27, 7, 'Mar Caribe', 0),
    (82, 28, 7, 'Río San Juan', 1),
    (83, 28, 7, 'Río Coco', 0),
    (84, 28, 7, 'Río Escondido', 0);
""")

# Insertar preguntas y respuestas para Trivia 8: Cultura Nicaragüense
db.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (29, 8, '¿En qué ciudad de Nicaragua se celebra la fiesta de la Gritería?'),
    (30, 8, '¿Qué tipo de música es muy popular en las fiestas nicaragüenses?'),
    (31, 8, '¿Qué baile tradicional es famoso en Nicaragua?'),
    (32, 8, '¿Qué bebida alcohólica es típica de las festividades en Nicaragua?');
""")

db.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text, correct) VALUES
    (85, 29, 8, 'Managua', 1),
    (86, 29, 8, 'Granada', 0),
    (87, 29, 8, 'Masaya', 0),
    (88, 30, 8, 'Marimba', 1),
    (89, 30, 8, 'Salsa', 0),
    (90, 30, 8, 'Cumbia', 0),
    (91, 31, 8, 'La Danza del Coyolito', 1),
    (92, 31, 8, 'La Cumbia', 0),
    (93, 31, 8, 'El Merengue', 0),
    (94, 32, 8, 'El Ron', 1),
    (95, 32, 8, 'La Cerveza', 0),
    (96, 32, 8, 'El Vino', 0);
""")

# Insertar preguntas y respuestas para Trivia 9: Economía de Nicaragua
db.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (33, 9, '¿Cuál es la principal fuente de ingresos de Nicaragua?'),
    (34, 9, '¿En qué rubro se destaca principalmente la economía de Nicaragua?'),
    (35, 9, '¿Qué producto agrícola se cultiva más en Nicaragua?'),
    (36, 9, '¿En qué año Nicaragua firmó un tratado de libre comercio con los Estados Unidos?');
""")

db.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text, correct) VALUES
    (97, 33, 9, 'Exportaciones de café', 1),
    (98, 33, 9, 'Turismo', 0),
    (99, 33, 9, 'Pesca', 0),
    (100, 34, 9, 'Agricultura', 1),
    (101, 34, 9, 'Manufacturas', 0),
    (102, 34, 9, 'Servicios', 0),
    (103, 35, 9, 'Café', 1),
    (104, 35, 9, 'Banano', 0),
    (105, 35, 9, 'Arroz', 0),
    (106, 36, 9, '2005', 1),
    (107, 36, 9, '2002', 0),
    (108, 36, 9, '2010', 0);
""")

# Insertar preguntas y respuestas para Trivia 10: Turismo en Nicaragua
db.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (37, 10, '¿Cuál es el destino turístico más visitado de Nicaragua?'),
    (38, 10, '¿Qué ciudad colonial es conocida como la “ciudad de los poetas”?'),
    (39, 10, '¿En qué región de Nicaragua se encuentra la Isla de Ometepe?'),
    (40, 10, '¿Qué parque nacional de Nicaragua es famoso por su volcán activo?');
""")

db.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text, correct) VALUES
    (109, 37, 10, 'Granada', 1),
    (110, 37, 10, 'León', 0),
    (111, 37, 10, 'Managua', 0),
    (112, 38, 10, 'León', 1),
    (113, 38, 10, 'Granada', 0),
    (114, 38, 10, 'Masaya', 0),
    (115, 39, 10, 'En el Lago Cocibolca', 1),
    (116, 39, 10, 'En el Lago Xolotlan', 0),
    (117, 39, 10, 'En el Caribe', 0),
    (118, 40, 10, 'Parque Nacional Masaya', 1),
    (119, 40, 10, 'Parque Nacional Volcán Cerro Negro', 0),
    (120, 40, 10, 'Parque Nacional Volcán San Cristóbal', 0);
""")



print("Datos insertados correctamente.")


Aqui rellenamos la base de datos con todos los datos necesarios para iniciar a jugar la trivia, informacion de las trivias
categorias, preguntas, respuestas etc.

La investigacion de esta informacion tambien tomo un tiempo, ya que en la estructura actual de la base de datos no podiamos
tener algunas caracteristicas entre las preguntas porque causarian problemas, por ejemplo no podia haber una preguna que
compartiera una respuesta correcta con otra pregunta, seria un problema de integridad referencial, por lo que se decidió en
hacer que todas las preguntas tengan respuestas diferentes.

Tambien creamos otro archivo para eliminar las tablas en caso de tener que modificarlas llamado drop.py


Finalizando solo nos quedaba crear la plantilla de las trivias y la logica de las trivias.


Primeramente creamos la plantilla de las trivias, para esto creamos un archivo llamado trivia.html, que extiende un archivo
llamado trivia_layout.html, aqui se crean los containers para contener el titulo, pregunta y respuesta de la trivia actual que el
usuario clickeo en la pagina principal index.



{% extends "trivia_layout.html" %}

{% block content %}
<div class="container mx-auto px-4 py-16" id="trivia-container">
    <!-- Encabezado con título y vidas -->
    <div class="flex items-center justify-between mb-6 relative">
        <div class="absolute left-1/2 transform -translate-x-1/2">
            <h2 class="text-3xl font-semibold text-center">{{ trivia.title }}</h2>
        </div>
        <div class="ml-auto bg-red-100 text-red-800 text-sm font-bold px-4 py-2 rounded shadow-lg">
            Lives: {{ lives }}
        </div>
    </div>

    <!-- Contenedor para la trivia -->
    <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-4xl mx-auto mb-8">
        <p class="text-sm text-gray-500 text-center mb-4">
            Pregunta {{ question_num }} de {{ total_questions }}
        </p>
        <p id="question-text" class="text-lg font-medium text-center">
            {{ question['question_text'] }}
        </p>
    </div>

    <!-- Contenedor para las respuestas -->
    <div class="bg-gray-100 rounded-lg shadow-md p-6 w-full max-w-4xl mx-auto">
        {% for response in responses %}
        <form
            method="POST"
            action="{{ url_for('register_response', trivia_id=trivia['trivia_id'], response_id=response['response_id']) }}"
        >
            <button
                type="submit"
                id="button"
                onclick= "button.play();"
                class="bg-blue-500 hover:bg-blue-400 text-white font-bold py-2 px-4 border-b-4 border-blue-700 hover:border-blue-500 rounded w-full trivia-button"
            >
                {{ response['response_text'] }}
            </button>
        </form>
        {% endfor %}
    </div>
</div>

<!-- Audio para el sonido -->
<script type="text/javascript">
    const button = new Audio();
    button.src = "./static/yay.mp3";
</script>

{% endblock %}



<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Trivia - {{ trivia.title if trivia else "Juego" }}{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen flex flex-col">
    <!-- Encabezado de Trivia -->
    <header class="bg-blue-500 text-white py-4 px-6">
        <div class="container mx-auto flex items-center justify-between">
            <h1 class="text-xl font-semibold">{{ trivia.title if trivia else "Trivias" }}</h1>
            <a href="/" class="text-sm underline hover:text-gray-300">Regresar al Inicio</a>
        </div>
    </header>

    <!-- Contenido Principal -->
    <main class="flex-1 flex justify-center items-center py-8">
        {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
        <div class="fixed inset-0 bg-gray-800 bg-opacity-50 flex justify-center items-center">
            <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-lg">
                {% for category, message in messages %}
                <p class="text-center text-lg font-semibold text-{{ 'green-500' if category == 'success' else 'red-500' }}">
                    {{ message }}
                </p>
                {% endfor %}
                <button
                    onclick="this.parentElement.parentElement.classList.add('hidden')"
                    class="mt-4 bg-blue-500 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded w-full"
                >
                    Cerrar
                </button>
            </div>
        </div>
        {% endif %}
        {% endwith %}

        {% block content %}
        {% endblock %}
    </main>

    <footer class="bg-gray-100 text-center py-4 text-sm text-gray-500">
        &copy; {{ current_year }} Trivias Nicaragüenses
    </footer>
</body>


</html>



Ahora solo nos faltaba la logica necesaria para mostrar la trivias y procesar las preguntas que pone el usuario.


primero mostrare los archivos y luego la explicacion general.



import random

@app.route("/trivia/<int:trivia_id>")
@login_required
def trivia(trivia_id):
    user_id = session["user_id"]

    # Inicializar vidas en la sesión si no existen
    if "lives" not in session:
        session["lives"] = 3

    # Obtener la trivia y verificar si existe
    trivia = db.execute("SELECT * FROM trivias WHERE trivia_id = ?", trivia_id)
    if not trivia:
        return redirect("/")

    trivia = trivia[0]

    # Obtener preguntas no respondidas correctamente
    unanswered_questions = db.execute(
        """
        SELECT q.*
        FROM questions q
        WHERE q.trivia_id = ?
        AND NOT EXISTS (
            SELECT 1
            FROM user_responses ur
            JOIN responses r ON ur.response_id = r.response_id
            WHERE ur.user_id = ? AND ur.correct = 1 AND r.question_id = q.question_id
        )
        ORDER BY q.question_id
        """,
        trivia_id, user_id,
    )

    if not unanswered_questions:
        flash("Ya completaste esta trivia.", "success")
        return redirect("/")

    # Barajar las preguntas
    random.shuffle(unanswered_questions)
    question = unanswered_questions[0]

    # Obtener las respuestas de la pregunta actual
    responses = db.execute(
        "SELECT * FROM responses WHERE question_id = ?", question["question_id"]
    )

    # Barajar las respuestas
    random.shuffle(responses)

    # Contar preguntas y progreso
    total_questions = db.execute(
        "SELECT COUNT(*) as total FROM questions WHERE trivia_id = ?", trivia_id
    )[0]["total"]

    answered_count = db.execute(
        """
        SELECT COUNT(*) as count
        FROM user_responses ur
        JOIN responses r ON ur.response_id = r.response_id
        JOIN questions q ON r.question_id = q.question_id
        WHERE ur.user_id = ? AND q.trivia_id = ?
        """,
        user_id, trivia_id,
    )[0]["count"]

    return render_template(
        "trivia.html",
        trivia=trivia,
        question=question,
        responses=responses,
        question_num=answered_count + 1,
        total_questions=total_questions,
        lives=session["lives"],  # Enviar las vidas a la plantilla
    )


@app.route("/register_response/<int:trivia_id>/<int:response_id>", methods=["POST"])
@login_required
def register_response(trivia_id, response_id):
    user_id = session["user_id"]

    # Verificar si la trivia ya fue completada
    correct_answers = db.execute(
        """
        SELECT COUNT(DISTINCT q.question_id) as correct_count
        FROM questions q
        JOIN responses r ON q.question_id = r.question_id
        JOIN user_responses ur ON ur.response_id = r.response_id
        WHERE ur.user_id = ? AND q.trivia_id = ? AND ur.correct = 1
        """,
        user_id, trivia_id
    )[0]["correct_count"]

    total_questions = db.execute(
        "SELECT COUNT(*) as total FROM questions WHERE trivia_id = ?", trivia_id
    )[0]["total"]

    if correct_answers >= total_questions:
        flash("¡Ya completaste esta trivia anteriormente!", "info")
        return redirect("/")

    # Verificar información de la respuesta seleccionada
    response = db.execute(
        """
        SELECT r.correct, q.question_id
        FROM responses r
        JOIN questions q ON r.question_id = q.question_id
        WHERE r.response_id = ? AND q.trivia_id = ?
        """,
        response_id, trivia_id,
    )

    if not response:
        flash("Pregunta no encontrada. Inténtalo nuevamente.", "error")
        return redirect("/")

    correct = response[0]["correct"]

    # Registrar respuesta solo si aún no existe un registro para esta respuesta
    db.execute(
        """
        INSERT INTO user_responses (user_id, trivia_id, response_id, correct)
        VALUES (?, ?, ?, ?)
        ON CONFLICT DO NOTHING;
        """,
        user_id, trivia_id, response_id, correct,
    )

    # Manejo de vidas si la respuesta es incorrecta
    if not correct:
        session["lives"] -= 1  # Restar una vida
        if session["lives"] <= 0:  # Si las vidas llegan a 0, redirigir al inicio
            flash("Te has quedado sin vidas. ¡Mejor suerte la próxima vez!", "error")
            session.pop("lives", None)  # Reiniciar las vidas al salir
            return redirect("/")
        flash(f"Respuesta incorrecta. Te quedan {session['lives']} vidas.", "error")
    else:
        flash("¡Respuesta correcta! Sigue con la próxima pregunta.", "success")

    # Verificar progreso del usuario
    correct_count = db.execute(
        """
        SELECT COUNT(DISTINCT q.question_id) as count
        FROM questions q
        JOIN responses r ON q.question_id = r.question_id
        JOIN user_responses ur ON ur.response_id = r.response_id
        WHERE ur.user_id = ? AND q.trivia_id = ? AND ur.correct = 1
        """,
        user_id, trivia_id,
    )[0]["count"]

    total_questions = db.execute(
        "SELECT COUNT(*) as total FROM questions WHERE trivia_id = ?", trivia_id
    )[0]["total"]

    # Si todas las preguntas fueron respondidas correctamente, registrar como completada
    if correct_count >= total_questions:
        db.execute(
            """
            INSERT OR IGNORE INTO user_trivias (user_id, trivia_id, date_played)
            VALUES (?, ?, DATE('now'))
            """,
            user_id, trivia_id,
        )
        flash("¡Felicidades, completaste la trivia con todas las respuestas correctas!", "success")
        session.pop("lives", None)  # Reiniciar vidas tras completar la trivia
        return redirect("/")

    # Obtener la siguiente pregunta no respondida o respondida incorrectamente
    next_question = db.execute(
        """
        SELECT q.*
        FROM questions q
        WHERE q.trivia_id = ?
        AND NOT EXISTS (
            SELECT 1
            FROM user_responses ur
            JOIN responses r ON ur.response_id = r.response_id
            WHERE ur.user_id = ? AND r.question_id = q.question_id AND ur.correct = 1
        )
        ORDER BY q.question_id
        LIMIT 1
        """,
        trivia_id, user_id
    )

    if not next_question:
        flash("No hay más preguntas disponibles.", "error")
        return redirect("/")

    # Obtener las respuestas para la siguiente pregunta
    responses = db.execute(
        "SELECT * FROM responses WHERE question_id = ?", next_question[0]["question_id"]
    )

    return render_template(
        "trivia.html",
        trivia=db.execute("SELECT * FROM trivias WHERE trivia_id = ?", trivia_id)[0],
        question=next_question[0],
        responses=responses,
        question_num=correct_count + 1,
        total_questions=total_questions,
        lives=session["lives"],  # Enviar las vidas a la plantilla
    )


Primeramente, obtenemos todos los datos enviados al index.html, que son los datos de las trivias, mas especificamente
el trivia_id con eso podemos usar querys y JOINS para encontrar todos los datos necesarios de esa misma trivia,
la pregunta, respuesta y titulo.

Despues la parte de registrar las preguntas, agarramos la respuestaque clickeo el usuario mediante un form en el trivia_id, proce
samos si es correcta mediante un apartado BOOL  correct en la tabla de responses, y conforme a eso podemos marcar esa pregunta
como correcta o incorrecta, si es incorrecta se le resta una vida al usuario, la vida es una variable guardada en la session.

No tengo mucho tiempo, tengo que entregar esto a las 12 pm, asi que, si necesitan una explicacion mas a detalle , no se preocupen, la actualizare si me notifican.

La parte mas dificil fue el registrar las respuestas del usuario, ya que los JOINS en los querys hacian conflictos, y
tuve que modificar las tablas de la base de datos para que los JOINS no fueran tan complicados, y que todas las condiciones
se cumplan en esa interaccion.

solo se usa redirecciones de flash asi que la pagina tiene que recargar cada vez que se realiza un chequeo de la respuesta
actual.
