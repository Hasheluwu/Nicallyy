import sqlite3
import os

def get_con_connection():
    db_path = os.path.abspath("users.db")
    print(f"Ruta absoluta de la base de datos: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con

con = get_con_connection()

# Lista en orden para evitar errores por claves foráneas
tablas = [
    "achievements",
    "categories",
    "questions",
    "correct_responses",
    "responses",
    "images",
    "sqlite_sequence",
    "trivia_images",
    "trivias",
    "user_achievements",
    "user_responses",
    "user_trivias",
    "users"
]

print("\nEliminando tablas existentes...")
for tabla in tablas:
    try:
        con.execute(f"DROP TABLE IF EXISTS {tabla};")
        print(f"Eliminada: {tabla}")
    except Exception as e:
        print(f"Error al eliminar {tabla}: {e}")
con.commit()

sql_crear_tablas = """
CREATE TABLE users (
  id integer,
  gmail text,
  password text,
  username text,
  gender char(1),
  birthday integer,
  PRIMARY KEY (id)
);

CREATE TABLE achievements (
  achievement_id integer,
  title text,
  description text,
  PRIMARY KEY(achievement_id)
);

CREATE TABLE categories (
  category_id integer,
  name text,
  PRIMARY KEY (category_id)
);

CREATE TABLE trivias (
  trivia_id integer,
  user_id integer,
  category_id integer,
  title text,
  points integer,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (category_id) REFERENCES categories(category_id),
  PRIMARY KEY (trivia_id)
);

CREATE TABLE images (
  image text,
  image_id integer,
  horario integer,
  grande integer,
  PRIMARY KEY (image)
);

CREATE TABLE questions (
  question_id integer,
  trivia_id integer,
  question_text text,
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id),
  PRIMARY KEY (question_id)
);

CREATE TABLE responses (
  response_id integer,
  trivia_id integer,
  question_id integer,
  response_text text,
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id),
  FOREIGN KEY (question_id) REFERENCES questions(question_id),
  PRIMARY KEY (response_id)
);

CREATE TABLE correct_responses (
  correct_response_id integer,
  trivia_id integer,
  question_id integer,
  correct_response_text text,
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id),
  FOREIGN KEY (question_id) REFERENCES questions(question_id),
  PRIMARY KEY (correct_response_id)
);

CREATE TABLE trivia_images (
  image_id integer,
  trivia_id integer,
  FOREIGN KEY (image_id) REFERENCES images(image_id),
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id)
);

CREATE TABLE user_achievements (
  user_id integer,
  achievement_id integer,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (achievement_id) REFERENCES achievements(achievement_id)
);

CREATE TABLE user_trivias (
  user_id integer,
  trivia_id integer,
  date_played text,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id)
);

CREATE TABLE user_responses (
  user_id integer,
  trivia_id integer,
  correct_response_id integer,
  response_id integer,
  correct_question_id integer,
  question_id integer, 
  FOREIGN KEY (question_id) REFERENCES questions (question_id),
  FOREIGN KEY (correct_question_id) REFERENCES questions (question_id),  
  FOREIGN KEY (response_id) REFERENCES responses (response_id),
  FOREIGN KEY (correct_response_id) REFERENCES correct_responses (correct_response_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id)
);
"""

print("\nCreando tablas...")
try:
    con.executescript(sql_crear_tablas)
    con.commit()
    print("Tablas creadas correctamente.")
except Exception as e:
    print(f"Error al crear las tablas: {e}")
finally:
    con.close()



'''
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
  points integer,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
  PRIMARY KEY (trivia_id)
)

CREATE TABLE images (
  image text,
  image_id integer,
  PRIMARY KEY (image)
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
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id),
  FOREIGN KEY (question_id) REFERENCES questions(question_id),
  PRIMARY KEY (response_id)
)

CREATE TABLE correct_responses (
  correct_response_id integer,
  trivia_id integer,
  question_id integer,
  correct_response_text text,
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id),
  FOREIGN KEY (question_id) REFERENCES questions(question_id),
  PRIMARY KEY (correct_response_id)
)

CREATE TABLE trivia_images (
  image_id integer,
  trivia_id integer,
  FOREIGN KEY (image_id) REFERENCES images(image_id),
  FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id)
)
CREATE TABLE user_achievements (
  user_id integer,
  achievement_id integer,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (achievement_id) REFERENCES achievements(achievement_id)
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
    correct_response_id integer,
    FOREIGN KEY (correct_response_id) REFERENCES correct_responses (correct_response_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (trivia_id) REFERENCES trivias(trivia_id),
);
'''

'''
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

'''
