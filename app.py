import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
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

 

@app.route('/toggle-dark-mode', methods=['POST'])
def toggle_dark_mode():
    current = session.get('dark_mode', False)
    session['dark_mode'] = not current
    return ('', 204)  # No content, pero confirma éxito


@app.route("/prueba")
def prueba():
    return render_template("prueba.html")

@app.route("/")
@require_profile_completion
def index():
    
    if "user_id" in session:      
        
        print(f"EL USER ID ACTUAL: {session['user_id']}\n")
        con = get_con_connection()

        # ✅ Arreglo: falta fetchone y parámetro como tupla
        username = session["username"]
        
        print(f"USERNAME: {username}\n")

        # Consulta: contar trivias completadas
        completed_trivias = con.execute(
            "SELECT COUNT(DISTINCT trivia_id) AS total_completed FROM user_trivias WHERE user_id = ?",
            (session['user_id'],)
        ).fetchone()["total_completed"]

        print(f"LAS TRIVIAS COMPLETADAS: {completed_trivias} \n")

        # Logros que se deben verificar
        achievements_to_check = [
            {"id": 1, "condition": completed_trivias >= 1},
            {"id": 2, "condition": completed_trivias >= 3},
            {"id": 3, "condition": completed_trivias >= 5},
        ]

        # Revisión e inserción de logros
        for achievement in achievements_to_check:
            exists = con.execute(
                """
                SELECT 1 FROM user_achievements
                WHERE user_id = ? AND achievement_id = ?
                """,
                (session['user_id'], achievement["id"])
            ).fetchone()

            if not exists and achievement["condition"]:
                con.execute(
                    """
                    INSERT INTO user_achievements (user_id, achievement_id)
                    VALUES (?, ?)
                    """,
                    (session['user_id'], achievement["id"])
                )
                
                con.commit()
                print(f"Agrego un logro, el logro: {achievement['id']} \n")

        # ✅ Arreglo: agregar fetchall()
        
        achievements = con.execute("""
        SELECT DISTINCT achievement_id FROM user_achievements WHERE user_id = ?
                                   
                                   
                                   """, (session['user_id'],)).fetchall()
        achievements = [dict(row) for row in achievements]
        print(f"LISTA DE ACHIEVEMENTS OBTENIDOS: {achievements} \n")
        
        session['achievements'] = achievements
        
        categories = con.execute("SELECT * FROM categories").fetchall()
        
        categories_dicts = [dict(row) for row in categories]
        
        print(f"TODAS LAS CATEGORIAS: {categories_dicts} \n")
        trivias = con.execute(
            """
            SELECT t.trivia_id, t.title, c.name as category_name
            FROM trivias t
            JOIN categories c ON t.category_id = c.category_id
            """
        ).fetchall()
        
        trivias_dict = [dict(row) for row in trivias]
        print(f"TODAS LAS TRIVIAS: {trivias_dict} \n")

        imagen_dia = get_random_image(1)
        imagen_noche = get_random_image(0)
        
        print(f"\n {imagen_dia}")
        print(f"\n {imagen_noche}")
        
        con.close()
        return render_template("index.html",  categories=categories, trivias=trivias, user_id=session['user_id'], username=username, achievements = session['achievements'])

    return redirect("/register")


# User registration
@app.route("/register", methods=["GET", "POST"])
def register():
    imagen_dia = get_random_image(1)
    imagen_noche = get_random_image(0)
        
    print(f"\n {imagen_dia}")
    print(f"\n {imagen_noche}")
    
    if request.method == "POST":
        con = get_con_connection()
        gmail = request.form.get("gmail")
        print("gmail recibido:\n", repr(gmail) )
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not gmail or not is_valid_email(gmail):
            print("Correo inválido.\n")
            return render_template("register.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche, error_message="Por favor, introduce un correo electrónico válido.")
        
        existing_user = con.execute("SELECT * FROM users WHERE gmail = ?", (gmail,)).fetchone()
        if existing_user:
            print("Correo ya registrado.\n")
            con.close()
            return render_template("register.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche, error_message="El correo ya está registrado.")

        if not is_secure_password(password):
            print("Contraseña insegura.\n")
            con.close()
            return render_template("register.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche , error_message="La contraseña no es segura.")
        
        if password != confirmation:
            print("Contraseñas no coinciden.\n")
            con.close()
            return render_template("register.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche ,  error_message="Las contraseñas no coinciden.")
        
        password_hash = generate_password_hash(password)
        print("Insertando en la base de datos...\n")
        con.execute("INSERT INTO users (gmail, password) VALUES (?, ?)", (gmail, password_hash,))
        con.commit()
        con.close()
        
        print("Registro completado, redirigiendo a /login\n")
        
        
        return redirect("/login")
    else:
        print("Método GET, renderizando formulario.\n")
        return render_template("register.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche)


# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    imagen_dia = get_random_image(1)
    imagen_noche = get_random_image(0)
        
    print(f"\n {imagen_dia}")
    print(f"\n {imagen_noche}")
    
    if request.method == "POST":    
        gmail = request.form.get("gmail")
        password = request.form.get("password")

        if not gmail or not password:
            return render_template("login.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche ,  error_message="Debes completar ambos campos.")
           
        con = get_con_connection()
        
        user = con.execute("SELECT * FROM users WHERE gmail = ?", (gmail,)).fetchone()
        if not user or not check_password_hash(user["password"], password):
            print("Correo o contrasenia incorrectos\n")
            con.close()
           
            return render_template("login.html", error_message="Correo o contraseña incorrectos." ,imagen_dia = imagen_dia, imagen_noche = imagen_noche)

        session["user_id"] = user["id"]
        
        user_id = session["user_id"]
        session.permanent = True
        user_profile_data = con.execute("SELECT username, gender, birthday FROM users WHERE id = ?",
                                        (user_id,)).fetchone()
        
        username = user_profile_data["username"]
        gender = user_profile_data["gender"]
        birthday = user_profile_data["birthday"]
        
        session["username"] = username
        session["gender"] = gender
        session["birthday"] = birthday
    
        con.close()
        if(username and gender and birthday):
            return redirect("/")
        return redirect("/profile")
    return render_template("login.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche )

# User profile
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    imagen_dia = get_random_image(1)
    imagen_noche = get_random_image(0)
        
    print(f"\n {imagen_dia}")
    print(f"\n {imagen_noche}")
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    if request.method == "POST":
        username = request.form.get("username")
        gender = request.form.get("gender")
        birthday = request.form.get("birthday")

        if not username or not gender or not birthday or birthday > current_date:
            return render_template("profile.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche , error_message="Datos inválidos.",
                                   current_date=current_date)
            
        con = get_con_connection()
        
        con.execute(
            "UPDATE users SET username = ?, gender = ?, birthday = ? WHERE id = ?",
            (username, gender, birthday, session["user_id"])
        )
        con.commit()

        session["username"] = username
        
        print(f"Este sera el username de la session {username}")
        
        
        
        con.close()
        return redirect("/")
    return render_template("profile.html", current_date=current_date, imagen_dia = imagen_dia, imagen_noche = imagen_noche)


@app.route("/user_profile", methods=["GET"])
@require_profile_completion
def user_profile():
    imagen_dia = get_random_image(1)
    imagen_noche = get_random_image(0)
        
    print(f"\n {imagen_dia}")
    print(f"\n {imagen_noche}")
    
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
        achievements=achievements,
        imagen_dia = imagen_dia, imagen_noche = imagen_noche
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
    
    con = get_con_connection()
    
    unanswered_questions = con.execute("""
    SELECT q.*
    FROM questions q
    WHERE q.trivia_id = ?
    AND NOT EXISTS (
        SELECT 1
        FROM user_responses ur
        WHERE ur.user_id = ? AND ur.correct_question_id = q.question_id
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
        SELECT COUNT(correct_response_id) as count
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
    print(f"datos trivia: {dict(datos_trivia)} \n question:  {dict(question)} \n responses:{responses_dicts} \n correct_responses{correct_responses_dicts} \n")
    print(f"total responses: {total_responses_dicts} \n answered count: {dict(answered_count)} \n unanswered questions: {unanswered_questions_dicts} \n")    
    print(f" LIVES {session['lives']}")
    
    template_total_questions = dict(total_questions)
    
    print(f"\n answered_count: {answered_count[0] +1 } \n total_questions: {template_total_questions}")
    
    total_responses = [dict(response) for response in total_responses]
    
    return render_template(
        "trivia.html",
        trivia = datos_trivia,
        question = question,
        responses = responses,
        correct_responses = correct_responses,
        total_responses = total_responses,
        question_num = answered_count[0],
        total_questions = template_total_questions["total"],
        lives = session["lives"],
        unanswered_questions = unanswered_questions # Enviar las vidas a la plantilla
    )
 
@app.route("/register_response/<int:trivia_id>/<int:response_id>/<int:question_id>", methods=["POST"])
@require_profile_completion
def register_response(trivia_id,response_id,question_id):
    user_id = session["user_id"]
        
    con = get_con_connection()
    
    con.execute(
        """
        INSERT INTO user_responses (user_id, trivia_id, response_id,question_id)
        VALUES (?, ?, ?, ?)
        ON CONFLICT DO NOTHING;
        """,
        (user_id, trivia_id, response_id, question_id)
    )
    
    con.commit()
    
    con.close()
    
    session["lives"] -= 1  # Restar una vida
    if session["lives"] <= 0:  # Si las vidas llegan a 0, redirigir al inicio
        flash("Te has quedado sin vidas. ¡Mejor suerte la próxima vez!", "error")
        session.pop("lives", None)  # Reiniciar las vidas al salir
        return redirect("/")
    flash(f"Respuesta incorrecta. Te quedan {session['lives']} vidas.", "error")
    
    return redirect(f'/trivia/{trivia_id}')
    

@app.route("/register_correct_response/<int:trivia_id>/<int:correct_response_id>/<int:total_questions>/<int:correct_question_id>", methods=["POST"])
@require_profile_completion
def register_correct_response(trivia_id, correct_response_id, total_questions, correct_question_id):
    user_id = session["user_id"]
    con = get_con_connection()
    
    unanswered_questions = con.execute("""
    SELECT q.*
    FROM questions q
    WHERE q.trivia_id = ?
    AND NOT EXISTS (
        SELECT 1
        FROM user_responses ur
        WHERE ur.user_id = ? AND ur.correct_question_id = q.question_id
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
        INSERT INTO user_responses (user_id, trivia_id, correct_response_id, correct_question_id)
        VALUES (?, ?, ?, ?)
        ON CONFLICT DO NOTHING;
        """,
        (user_id, trivia_id, correct_response_id, correct_question_id)
    )
    
    con.commit()

    # flash de ganador

    trivia_actual = con.execute("SELECT COUNT(trivia_id) AS FLASH FROM user_trivias WHERE trivia_id = ?", (trivia_id,)).fetchone()
    trivia_actual = dict(trivia_actual)
    print(f"CONTEO DE SI YA COMPLETAMOS ESTA TRIVIA VALIDACION FLASH{trivia_actual}")
    
    

    # Si todas las preguntas fueron respondidas correctamente, registrar como completada
    '''Encuentra todas las ocasiones en donde se encuentre este trivia_id con este usuario_id en la tabla de user_responses
    esto funciona porque todas los registros de preguntas son positivos.'''
    correct_responses_count = con.execute(
        """
        SELECT COUNT(correct_response_id) as count
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
        
        con.close()
        flash("¡Felicidades, completaste la trivia con todas las respuestas correctas!", "success")
        session.pop("lives", None)  # Reiniciar vidas tras completar la trivia
        return redirect("/")

    if trivia_actual['FLASH'] == 0:
        flash("¡Respuesta correcta! Sigue con la próxima pregunta.", "success")
    
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
    imagen_dia = get_random_image(1)
    imagen_noche = get_random_image(0)
        
    print(f"\n {imagen_dia}")
    print(f"\n {imagen_noche}")
    
    
    if "user_id" in session:
        return render_template("enciclopedia.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche, username = session['username'])
    return redirect("/login")


@app.route("/achievements")
@require_profile_completion
def trophy():
    
     imagen_dia = get_random_image(1)
     imagen_noche = get_random_image(0)
        
     print(f"\n {imagen_dia}")
     print(f"\n {imagen_noche}")
     
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
        return render_template("achievements.html",imagen_dia = imagen_dia, imagen_noche = imagen_noche, achievements=user_achievements, username = session['username'])
     return redirect("/")



@app.route("/settings")
@require_profile_completion
def settings():
    imagen_dia = get_random_image(1)
    imagen_noche = get_random_image(0)
        
    print(f"\n {imagen_dia}")
    print(f"\n {imagen_noche}")
     
    
    if "user_id" in session:

        return render_template("settings.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche, username = session['username'])
    return redirect("/login")



@app.route("/reset_progress", methods=["GET"])
@require_profile_completion
def reset_progress():
    user_id = session["user_id"]

    # Eliminar datos de progreso
    con = get_con_connection()
    
    history = con.execute("SELECT * FROM user_responses, user_trivias, user_achievements WHERE user_responses.user_id = ?", (user_id,)).fetchall()
    
    history_check = [dict(row) for row in history]
    
    con.execute("DELETE  FROM user_responses WHERE user_id = ?", (user_id,))
    con.execute("DELETE  FROM user_trivias WHERE user_id = ?", (user_id,))
    con.execute("DELETE  FROM user_achievements WHERE user_id = ?", (user_id,))

    con.commit()
    
    print(f"AHHH MIRA WEON: {history_check}")
    if history_check == []:
        flash("No tienes ningun progreso aun.", "error")
        
    elif history_check != []:
        flash("Progreso de trivias eliminado", "success")
        
    con.close()
    return redirect("/settings")


@app.route("/settings/history", methods=["GET"])
@require_profile_completion
def trivia_history():
    imagen_dia = get_random_image(1)
    imagen_noche = get_random_image(0)
        
    print(f"\n {imagen_dia}")
    print(f"\n {imagen_noche}")
     
    user_id = session["user_id"]

    # Consultar el historial de trivias con preguntas y respuestas
    con = get_con_connection()
    correct_history = con.execute("""
        SELECT t.title, q.question_text, cr.correct_response_text
        FROM user_responses ur
        JOIN correct_responses cr ON ur.correct_response_id = cr.correct_response_id
        JOIN questions q ON cr.question_id = q.question_id
        JOIN trivias t ON q.trivia_id = t.trivia_id
        WHERE ur.user_id = ?
    """, (user_id,)).fetchall()
    
    incorrect_history = con.execute("""
        SELECT t.title, q.question_text, r.response_text
        FROM user_responses ur
        JOIN responses r ON ur.response_id = r.response_id
        JOIN questions q ON r.question_id = q.question_id
        JOIN trivias t ON q.trivia_id = t.trivia_id
        WHERE ur.user_id = ?
    """, (user_id,)).fetchall()
    
    correct_history_dicts = [dict(row) for row in correct_history]
    incorrect_history_dicts =[dict(row) for row in incorrect_history]
    
    print(f"historial correcto {correct_history_dicts} \n")
    print(f"historial incorrecto {incorrect_history_dicts} \n")
    
    histories = correct_history + incorrect_history
    histories =  [dict(history) for history in histories]
    con.close()
    return render_template("trivia_history.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche,histories = histories, username = session['username'])



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
    imagen_dia = get_random_image(1)
    imagen_noche = get_random_image(0)
        
    print(f"\n {imagen_dia}")
    print(f"\n {imagen_noche}")
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    if request.method == "POST":
        username = request.form.get("username")
        gender = request.form.get("gender")
        birthday = request.form.get("birthday")

        if not username or not gender or not birthday or birthday > current_date:
            return render_template("profile.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche, error_message="Datos inválidos.", current_date=current_date)
        con = get_con_connection()
        con.execute("UPDATE users SET username = ?, gender = ?, birthday = ? WHERE id = ?",
                    (username, gender, birthday, session)["user_id"])
        con.close()
        return render_template("settings.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche, username = session['username'])
    return render_template("profile.html", imagen_dia = imagen_dia, imagen_noche = imagen_noche,  current_date=current_date)

@app.context_processor
def inject_dark_mode():
    return dict(dark_mode=session.get('dark_mode', False))

def get_random_image(horario):
    con = get_con_connection()

    # Traer todas las imágenes según si es día (1) o noche (0)
    rows = con.execute("SELECT image FROM images WHERE horario = ?", (horario,)).fetchall()
    

    # Convertir a lista de diccionarios
    imagenes = [dict(row) for row in rows]

    # Escoger una imagen aleatoria si hay disponibles
    if imagenes:
        return random.choice(imagenes)['image']
    return None
