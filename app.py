import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, is_valid_email, is_secure_password,require_profile_completion,get_con_connection

from datetime import timedelta, datetime
import re

# Configure application
app = Flask(__name__)

# Configure session
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "/static"
app.permanent_session_lifetime = timedelta(minutes=60)
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Toggle dark mode
@app.route("/toggle-dark-mode", methods=["POST"])
def toggle_dark_mode():
    if session.get("dark-mode") == "enabled":
        session["dark-mode"] = "disabled"
    else:
        session["dark-mode"] = "enabled"
    return ("", 204)
 
@app.route("/")
@require_profile_completion
def index():
    
    
    if "user_id" in session:
        user_id = session["user_id"]
        print(user_id)
        con = get_con_connection()
        
        
        # ✅ Arreglo: falta fetchone y parámetro como tupla
        username = con.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
        username = username["username"]
        
        print(username)

        # ✅ Arreglo: usar diccionario y fetchone()
        completed_trivias = con.execute(
            "SELECT COUNT(DISTINCT trivia_id) AS total_completed FROM user_trivias WHERE user_id = :user_id",
            {"user_id": user_id}
        ).fetchone()["total_completed"]
        
        print(completed_trivias)

        achievements_to_check = [
            {"id": 1, "condition": completed_trivias >= 1},
            {"id": 2, "condition": completed_trivias >= 3},
            {"id": 3, "condition": completed_trivias >= 5},
        ]

        for achievement in achievements_to_check:
            # ✅ Arreglo: diccionario con ambos parámetros y fetchone()
            exists = con.execute(
                """
                SELECT 1 FROM user_achievements
                WHERE user_id = :user_id AND achievement_id = :achievement_id
                """,
                {"user_id": user_id, "achievement_id": achievement["id"]}
            ).fetchone()

            if not exists and achievement["condition"]:
                con.execute(
                    """
                    INSERT INTO user_achievements (user_id, achievement_id)
                    VALUES (:user_id, :achievement_id)
                    """,
                    {"user_id": user_id, "achievement_id": achievement["id"]}
                )

        # ✅ Arreglo: agregar fetchall()
        categories = con.execute("SELECT * FROM categories").fetchall()
        
        categories_dicts = [dict(row) for row in categories]
        
        print(categories_dicts)
        trivias = con.execute(
            """
            SELECT t.trivia_id, t.title, c.name as category_name
            FROM trivias t
            JOIN categories c ON t.category_id = c.category_id
            """
        ).fetchall()
        
        trivias_dict = [dict(row) for row in trivias]
        print(trivias_dict)

        con.close()
        return render_template("index.html", categories=categories, trivias=trivias, user_id=user_id, username=username)

    return redirect("/register")

# Main route
'''@app.route("/")
def index():
    if "user_id" in session:
        user_id = session["user_id"]
        con = get_con_connection()
        username = con.execute("SELECT username FROM users WHERE id = ?", user_id)
        username = username[0]["username"]
        
        # Validar logros existentes
        completed_trivias = con.execute(
            "SELECT COUNT(DISTINCT trivia_id) AS total_completed FROM user_trivias WHERE user_id = :user_id",
            user_id=user_id
        )[0]["total_completed"]

        # Verificar y asignar logros según el progreso
        achievements_to_check = [
            {"id": 1, "condition": completed_trivias >= 1},  # Principiante: Completó 1 trivia
            {"id": 2, "condition": completed_trivias >= 3},  # Uwu: Completó 3 trivias
            {"id": 3, "condition": completed_trivias >= 5},  # Pinolero: Completó todas las trivias
        ]

        for achievement in achievements_to_check:
            # Verificar si ya tiene el logro asignado
            exists = con.execute(
                """
                SELECT 1 FROM user_achievements
                WHERE user_id = :user_id AND achievement_id = :achievement_id
                """,
                user_id=user_id,
                achievement_id=achievement["id"]
            )
            # Si no lo tiene y cumple la condición, agregar el logro
            if not exists and achievement["condition"]:
                con.execute(
                    """
                    INSERT INTO user_achievements (user_id, achievement_id)
                    VALUES (:user_id, :achievement_id)
                    """,
                    user_id=user_id,
                    achievement_id=achievement["id"]
                )

        # Obtener categorías y trivias para mostrar en el index
        categories = con.execute("SELECT * FROM categories")
        trivias = con.execute(
            """
            SELECT t.trivia_id, t.title, t.image, c.name as category_name
            FROM trivias t
            JOIN categories c ON t.category_id = c.category_id
            """
        )
        con.close()
        return render_template("index.html", categories=categories, trivias=trivias, user_id = user_id, username = username)

    # Redirigir al registro si no hay sesión activa
    return redirect("/register")
'''

# User registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        con = get_con_connection()
        gmail = request.form.get("gmail")
        print("gmail recibido:", repr(gmail))
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not gmail or not is_valid_email(gmail):
            print("Correo inválido.")
            return render_template("register.html", error_message="Por favor, introduce un correo electrónico válido.")
        
        existing_user = con.execute("SELECT * FROM users WHERE gmail = ?", (gmail,)).fetchone()
        if existing_user:
            print("Correo ya registrado.")
            con.close()
            return render_template("register.html", error_message="El correo ya está registrado.")

        if not is_secure_password(password):
            print("Contraseña insegura.")
            con.close()
            return render_template("register.html", error_message="La contraseña no es segura.")
        
        if password != confirmation:
            print("Contraseñas no coinciden.")
            con.close()
            return render_template("register.html", error_message="Las contraseñas no coinciden.")
        
        password_hash = generate_password_hash(password)
        print("Insertando en la base de datos...")
        con.execute("INSERT INTO users (gmail, password) VALUES (?, ?)", (gmail, password_hash,))
        con.commit()
        con.close()
        
        print("Registro completado, redirigiendo a /login")
        
        
        return redirect("/login")
    else:
        print("Método GET, renderizando formulario.")
        return render_template("register.html")


# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        
        gmail = request.form.get("gmail")
        password = request.form.get("password")

        if not gmail or not password:
            return render_template("login.html", error_message="Debes completar ambos campos.")
           
        
        con = get_con_connection()
        
        user = con.execute("SELECT * FROM users WHERE gmail = ?", (gmail,)).fetchone()
        if not user or not check_password_hash(user["password"], password):
            print("Correo o contrasenia incorrectos")
            con.close()
           
            return render_template("login.html", error_message="Correo o contraseña incorrectos.")

        session["user_id"] = user["id"]
        user_id = session["user_id"]
        session.permanent = True
        user_profile_data = con.execute("SELECT username, gender, birthday FROM users WHERE id = ?",
                                        (user_id,)).fetchone()
        
        username = user_profile_data["username"]
        gender = user_profile_data["gender"]
        birthday = user_profile_data["birthday"]
    
        con.close()
        if(username and gender and birthday):
            return redirect("/")
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
            return render_template("profile.html", error_message="Datos inválidos.",
                                   current_date=current_date)
            
        con = get_con_connection()
        
        con.execute(
            "UPDATE users SET username = ?, gender = ?, birthday = ? WHERE id = ?",
            (username, gender, birthday, session["user_id"])
        )
        con.commit()

        
        
        con.close()
        return redirect("/")
    return render_template("profile.html", current_date=current_date)


@app.route("/user_profile", methods=["GET"])
@require_profile_completion
def user_profile():
    user_id = session["user_id"]
    print(user_id)

    # Consultar los datos del usuario
    con = get_con_connection()
    user_data = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    
    username = user_data["username"]
    gender = user_data["gender"]
    birthday = user_data["birthday"]
    
    
    if user_data is None:
    # No existe usuario con ese ID, manejar ese caso
        return "Usuario no encontrado", 404

    # Consultar los logros del usuario
    achievements = con.execute("""
        SELECT achievements.title
        FROM user_achievements
        JOIN achievements ON user_achievements.achievement_id = achievements.achievement_id
        WHERE user_achievements.user_id = ?
    """, (user_id,)).fetchall()

    con.close()
    return render_template(
        "user_profile.html",
        username=username,
        genre=gender,
        birthday=birthday,
        achievements=achievements
    )
    
# Trivia gameplay

import random

@app.route("/trivia/<int:trivia_id>")
@login_required
def trivia(trivia_id):
	#1. Desde index obtenemos el dato de trivia_id.
	  
    con = get_con_connection()
    user_id = session["user_id"]

    # 2. Inicializar vidas en la sesión si no existen
    if "lives" not in session:
        print("Obtenemos las vidas")
        session["lives"] = 3

    print(session["lives"])
    
    # 3. Obtener la trivia y verificar si existe
    trivia = con.execute("SELECT * FROM trivias WHERE trivia_id = ?", (trivia_id,)).fetchone()    
    con.close()
    if not trivia:
        con.close()
        return redirect("/")
    
    

    print(f"Obtenemos los datos de la trivia. {dict(trivia)} \n")
    #4. aqui lo que hacemos es obtener la trivia_id.
    datos_trivia = trivia
    trivia = trivia[0]

    print(f"Obtenemos el id de la trivia {trivia_id} \n")
    # 5. Obtener preguntas no respondidas correctamente.
    """Primero seleccionamos todas los datos de la tabla questions (q), en donde su 
    valor de q.trivia_id sea el de la trivia actual y QUE NO EXISTA EN, la tabla de
    user_responses (ur) en donde el valor de ur.correct_response_id sea igual al id de
    q.question_id, esto funciona ya que el id de la respuestas correctas es el mismo
    al de su pregunta correspondiente.
     
    Aqui obtenemos todas las preguntas  en la base de datos, cuya respuesta correcta
    (que solo puede ser una) no este en la tabla de user_responses, asi asegurando
    que solo obtenga preguntas que aun no ha respondido el usuario por cada trivia."""
     
    con = get_con_connection()
    
    unanswered_questions = con.execute("""
    SELECT q.*
    FROM questions q
    WHERE q.trivia_id = ?
    AND NOT EXISTS (
        SELECT 1
        FROM user_responses ur
        WHERE ur.user_id = ? AND ur.correct_response_id = q.question_id
    )
    ORDER BY q.question_id 
    """,(trivia_id, user_id,)).fetchall()
    
    unanswered_questions_dicts = [dict(row) for row in unanswered_questions]
    print(f"Obtenemos las preguntas sin obtener {unanswered_questions_dicts} \n")
    con.close()
    #Si entramos a la trivia y no detecta preguntas cuyas respuesta correcta no este
    #en la tabla de user_responses solamente nos dira que ya completamos esta trivia
    #y nos devolvera al lobby principal.
    
    if not unanswered_questions:
        flash("Ya completaste esta trivia.", "success")
        con.close()
        return redirect("/")

    # Barajar las preguntas para que sean random en cada jugada.
    random.shuffle(unanswered_questions)
    
    unanswered_questions_dicts = [dict(row) for row in unanswered_questions]
    print(f"randomizamos las preguntas {unanswered_questions_dicts} \n")
    
    #Obtenemos la primera pregunta de la lista de preguntas no respondidas.
    question = unanswered_questions[0]
    
    print(f"Obtenemos la primera pregunta de la lista de preguntas no respondidas {dict(question)}\n")
		
    # Obtener las respuestas de la pregunta actual.
    con = get_con_connection()
    
    responses = con.execute(
        "SELECT * FROM responses WHERE question_id = ?", (question["question_id"],)
    ).fetchall()
    
    responses_dicts = [dict(row) for row in responses]
    print(f"Obtenemos todas las respuestas erroneas de responses {responses_dicts} \n")
    
    #obtenemos las respuestas correctas de la pregunta actual.
    correct_responses = con.execute(
        "SELECT * FROM correct_responses WHERE question_id = ?", (question["question_id"],),
    ).fetchall()
    
    correct_responses_dicts = [dict(row) for row in correct_responses]
    print(f"Obtenemos las respuestas correctas de correct_responses {correct_responses_dicts} \n")
    con.close()
		
    total_responses = responses + correct_responses
	
    total_responses_dicts = [dict(row) for row in total_responses]
    
    print(f"Creamos total_responses {total_responses_dicts} \n")
    # Barajar las respuestas incorrectas y correctas.
    random.shuffle(total_responses)
    
    total_responses_dicts = [dict(row) for row in total_responses]
    
    print(f"Randomizamos total_responses{total_responses_dicts} \n")

    # Contar preguntas y progreso
    """Algo raro pero aqui contamos todas las preguntas en total que tiene ligada esta
     trivia"""
    
    con = get_con_connection()
    
    total_questions = con.execute(
    "SELECT COUNT(*) as total FROM questions WHERE trivia_id = ?", (trivia_id,)
        ).fetchone()

    
    
    print(f"Obtenemos en numero todas las preguntas de la trivia {dict(total_questions)} \n")

    """Aqui contamos el progreso, contea todos los elementos que encuentre con esta query, 
    de la tabla user_responses, pues al parecer dentro de esta tabla busco encontrar todas las
    preguntas y respuestas que tengo incluidas dentro de mi tabla de user_responses, esto 
    antes tenia sentido porque yo incluia todas las responses dentro de la tabla de user_responses
    pero ahora solo incluyo las que vengan de correct_user_responses"""
    
    """me podrias explicar que es lo que realmente hace aqui?, cuenta cuantas preguntas
    ya han sido respondidas en la tabla de user_responses?"""
    
    answered_count = con.execute(
        """
        SELECT COUNT(*) as count
        FROM user_responses ur
        WHERE ur.user_id = ? AND ur.trivia_id = ?
        """,(
        user_id, trivia_id,)
    ).fetchone()
    
    print(f"Obtenemos las preguntas que ya han sido respondidas y entramos a el render_template {dict(answered_count)} /n")
    
    con.close()
    
    '''for response in total_responses_dicts:
        print(f"{response} /n")'''
        
    print("THIS IS ALL THE DATA BY ORDER. 1.datos_trivia, 2.question, 3.responses, 4.correct_responses, 5.total_responses, 6.answered_count ,7.lives, 8.unanswered_questions \n")    
    print(f"{dict(datos_trivia)} \n {dict(question)} \n {responses_dicts} \n {correct_responses_dicts} \n")
    print(f"{total_responses_dicts} \n {dict(answered_count)} \n {unanswered_questions_dicts}")    
    print(session["lives"])
    
    template_total_questions = dict(total_questions)
    print(f"\n {answered_count[0] +1 } \n {template_total_questions}")
    
    total_responses = [dict(response) for response in total_responses]
    
    return render_template(
        "trivia.html",
        trivia = datos_trivia,
        question = question,
        responses = responses,
        correct_responses = correct_responses,
        total_responses = total_responses,
        question_num = answered_count[0] + 1,
        total_questions = template_total_questions["total"],
        lives = session["lives"],
        unanswered_questions = unanswered_questions # Enviar las vidas a la plantilla
    )

'''If response["correct_response_id] AND response["correct_response_text]
        logic
    else
        logic'''
        
@app.route("/register_response/<int:trivia_id>", methods=["POST"])
@require_profile_completion
def register_response(trivia_id):
    session["lives"] -= 1  # Restar una vida
    if session["lives"] <= 0:  # Si las vidas llegan a 0, redirigir al inicio
        flash("Te has quedado sin vidas. ¡Mejor suerte la próxima vez!", "error")
        session.pop("lives", None)  # Reiniciar las vidas al salir
        return redirect("/")
    flash(f"Respuesta incorrecta. Te quedan {session['lives']} vidas.", "error")
    return redirect(f'/trivia/{trivia_id}')
    

@app.route("/register_correct_response/<int:trivia_id>/<int:correct_response_id>/<int:total_questions>", methods=["POST"])
@require_profile_completion
def register_correct_response(trivia_id, correct_response_id, total_questions):
    user_id = session["user_id"]
    con = get_con_connection()
    
    unanswered_questions = con.execute("""
    SELECT q.*
    FROM questions q
    WHERE q.trivia_id = ?
    AND NOT EXISTS (
        SELECT 1
        FROM user_responses ur
        WHERE ur.user_id = ? AND ur.correct_response_id = q.question_id
    )
    ORDER BY q.question_id 
    """,(trivia_id, user_id,)).fetchall()
    
    unanswered_questions_dicts = [dict(row) for row in unanswered_questions]

    # Verificar si la trivia ya fue completada
    if not unanswered_questions:
        flash("¡Ya completaste esta trivia anteriormente!", "info")
        return redirect("/")

    # Registrar respuesta solo si aún no existe un registro para esta respuesta
    con.execute(
        """
        INSERT INTO user_responses (user_id, trivia_id, correct_response_id)
        VALUES (?, ?, ?)
        ON CONFLICT DO NOTHING;
        """,
        (user_id, trivia_id, correct_response_id,)
    )
    
    con.commit()

    # Manejo de vidas si la respuesta es incorrecta
    flash("¡Respuesta correcta! Sigue con la próxima pregunta.", "success")

    # Si todas las preguntas fueron respondidas correctamente, registrar como completada
    '''Encuentra todas las ocasiones en donde se encuentre este trivia_id con este usuario_id en la tabla de user_responses
    esto funciona porque todas los registros de preguntas son positivos.'''
    correct_responses_count = con.execute(
        """
        SELECT COUNT(*) as count
        FROM user_responses ur
        WHERE user_id = ? AND trivia_id = ?
        
        """, (user_id,trivia_id,)
    ).fetchone()
    
    correct_responses_count_dict = dict(correct_responses_count)
    
    print(f"\n CORRECT RESPONSES COUNT AHHH! {correct_responses_count_dict['count'] }")
    
    if correct_responses_count_dict['count'] >= total_questions:
        con.execute(
            """
            INSERT OR IGNORE INTO user_trivias (user_id, trivia_id, date_played)
            VALUES (?, ?, DATE('now'))
            """,
            (user_id, trivia_id,)
        )
        con.commit()
        
        flash("¡Felicidades, completaste la trivia con todas las respuestas correctas!", "success")
        session.pop("lives", None)  # Reiniciar vidas tras completar la trivia
        return redirect("/")
    
    return redirect(f'/trivia/{trivia_id}')


@app.route("/logout")
@login_required
def logout():
    """Log user out"""
    # Forget any user_id
    session.pop("user_id", None)

    # Redirect user to login form
    return redirect("/login")


# Additional routes (Wiki, Trophy, Settings)
@app.route("/enciclopedia")
def wiki():
    if "user_id" in session:
        return render_template("enciclopedia.html")
    return redirect("/login")


@app.route("/achievements")
@require_profile_completion
def trophy():
     if "user_id" in session:
        # Obtener los logros desbloqueados por el usuario
        con = get_con_connection()
        user_achievements = con.execute("""
            SELECT achievements.title, achievements.description
            FROM achievements
            JOIN user_achievements ON achievements.achievement_id = user_achievements.achievement_id
            WHERE user_achievements.user_id = ?
        """, (session["user_id"],)).fetchall()
        
        print(user_achievements)

        
        con.close()
        return render_template("achievements.html", achievements=user_achievements)
     return redirect("/")



@app.route("/settings")
@require_profile_completion
def settings():
    if "user_id" in session:

        return render_template("settings.html")
    return redirect("/login")



@app.route("/reset_progress", methods=["GET"])
@require_profile_completion
def reset_progress():
    user_id = session["user_id"]

    # Eliminar datos de progreso
    con = get_con_connection()
    con.execute("DELETE  FROM user_responses WHERE user_id = ?", (user_id,))
    con.execute("DELETE  FROM user_trivias WHERE user_id = ?", (user_id,))
    con.execute("DELETE  FROM user_achievements WHERE user_id = ?", (user_id,))

    con.commit()
    flash("Progreso de trivias eliminado", "success")
    con.close()
    return redirect("/settings")


@app.route("/settings/history", methods=["GET"])
@require_profile_completion
def trivia_history():
    user_id = session["user_id"]

    # Consultar el historial de trivias con preguntas y respuestas
    con = get_con_connection()
    history = con.execute("""
        SELECT t.title, q.question_text, cr.correct_response_text
        FROM user_responses ur
        JOIN correct_responses cr ON ur.correct_response_id = cr.correct_response_id
        JOIN questions q ON cr.question_id = q.question_id
        JOIN trivias t ON q.trivia_id = t.trivia_id
        WHERE ur.user_id = ?
    """, (user_id,)).fetchall()
    
    history_dicts = [dict(row) for row in history]
    print(f"Obtenemos las preguntas sin obtener {history_dicts} \n")
    
    con.close()
    return render_template("trivia_history.html", history=history)



@app.route("/settings/delete_account", methods=["GET"])
@require_profile_completion
def delete_account():
    user_id = session["user_id"]

    # Eliminar datos relacionados con el usuario
    con = get_con_connection()
    con.execute("DELETE FROM user_responses WHERE user_id = ?", (user_id,))
    con.execute("DELETE FROM user_trivias WHERE user_id = ?", (user_id,))
    con.execute("DELETE FROM user_achievements WHERE user_id = ?", (user_id,))
    con.execute("DELETE FROM users WHERE id = ?", (user_id,))

    # Cerrar sesión
    session.clear()
    con.close()
    flash("Cuenta eliminada con éxito", "info")
    return redirect("/")


@app.route("/new_profile", methods=["GET", "POST"])

@require_profile_completion

def newprofile():
    current_date = datetime.now().strftime('%Y-%m-%d')
    if request.method == "POST":
        username = request.form.get("username")
        gender = request.form.get("gender")
        birthday = request.form.get("birthday")

        if not username or not gender or not birthday or birthday > current_date:
            return render_template("profile.html", error_message="Datos inválidos.", current_date=current_date)
        con = get_con_connection()
        con.execute("UPDATE users SET username = ?, gender = ?, birthday = ? WHERE id = ?",
                    (username, gender, birthday, session)["user_id"])
        con.close()
        return render_template("settings.html")
    return render_template("profile.html", current_date=current_date)
