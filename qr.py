import sqlite3
import os

database = "users.db"
def get_con_connection(database):
    db_path = os.path.abspath(database)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con

con = get_con_connection(database)

print(database)
# Conectar a la base de datos
print("Conexion a la base de datos")

# Limpiar tablas existentes
tables = ["user_responses", "user_trivias", "responses", "correct_responses",
          "questions", "trivias", "categories", "trivia_images", "images"]
for table in tables:
    con.execute(f"DELETE FROM {table};")
con.commit()
print("Tablas limpiadas.")


con.execute("""
INSERT INTO images (image, image_id, horario) VALUES
('/static/dia1.jpg',1,1),
('/static/dia2.jpg',2,1),    
('/static/dia3.jpg',3,1),     
('/static/dia4.jpg',4,1),     
('/static/dia5.jpg',5,1),     
('/static/dia6.jpg',6,1),    
('/static/noche1.jpg',1,0),
('/static/noche2.jpg',2,0),
('/static/noche3.jpg',3,0),
('/static/noche4.jpg',4,0),
('/static/noche5.jpg',5,0)
            """)

con.execute("""
INSERT INTO achievements (achievement_id, title, description) VALUES
(1, 'Principiante', 'Completaste 1 trivia!'),
(2, 'Experimentado', 'Completaste 3 trivias!'),
(3, 'Pinolero!', 'Uwu')
            
""") 

con.commit()

# Insertar categorías
con.execute("""
    INSERT INTO categories (category_id, name) VALUES
    (1, 'Cultura General'),
    (2, 'Historia'),
    (3, 'Gastronomía'),
    (4, 'Arte'),
    (5, 'Tradiciones');
""")
con.commit()
print("Categorias insertadas.")

# Insertar trivias
con.execute("""
    INSERT INTO trivias (trivia_id, user_id, category_id, title, points) VALUES
    (1, NULL, 1, 'Símbolos Nacionales de Nicaragua', 10),
    (2, NULL, 2, 'Historia de Nicaragua', 15),
    (3, NULL, 3, 'Gastronomía Nicaragüense', 20),
    (4, NULL, 4, 'Literatura Nicaragüense', 25),
    (5, NULL, 5, 'Leyendas de Nicaragua', 30),
    (6, NULL, 4, 'Flora y fauna', 10),
    (7, NULL, 2, 'Geografia', 15),
    (8, NULL, 1, 'Festividades', 20),
    (9, NULL, 5, 'Economia', 25),
    (10, NULL, 3, 'Turismo', 30);
""")
con.commit()
print("Trivias insertadas.")

# Insertar preguntas para Trivia 1
con.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (1, 1, '¿Cuál es el símbolo nacional de Nicaragua que aparece en el centro de la bandera?'),
    (2, 1, '¿Qué representan los cinco volcanes en el escudo de armas de Nicaragua?'),
    (3, 1, '¿Cuál es la flor nacional de Nicaragua?'),
    (4, 1, '¿Qué significa el sol en el escudo de armas de Nicaragua?');
""")
con.commit()
print("Preguntas de la Trivia 1 insertadas.")

# Insertar respuestas correctas para Trivia 1 (corregido)
con.execute("""
    INSERT INTO correct_responses (correct_response_id, question_id, trivia_id, correct_response_text) VALUES 
    (1, 1, 1, 'Un triángulo equilátero'),
    (4, 2, 1, 'Los cinco países de Centroamérica'),
    (7, 3, 1, 'Sacuanjoche'),
    (10, 4, 1, 'La libertad');
""")
con.commit()
print("Respuestas correctas de la Trivia 1 insertadas.")

# Insertar respuestas incorrectas para Trivia 1
con.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text) VALUES
    (2, 1, 1, 'Un rectángulo azul'),
    (3, 1, 1, 'Un círculo dorado'),
    (5, 2, 1, 'Las cinco montañas más altas'),
    (6, 2, 1, 'Las cinco luchas por la independencia'),
    (8, 3, 1, 'Flor de Mayo'),
    (9, 3, 1, 'Jazmín'),
    (11, 4, 1, 'La unidad'),
    (12, 4, 1, 'La justicia');
""")
con.commit()
print("Respuestas incorrectas de la Trivia 1 insertadas.")

# Insertar preguntas y respuestas para Trivia 2: Historia de Nicaragua
con.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (5, 2, '¿En qué año se independizó Nicaragua de España?'),
    (6, 2, '¿Qué conflicto armado ocurrió en Nicaragua entre 1981 y 1990?'),
    (7, 2, '¿Quién fue el líder del Frente Sandinista de Liberación Nacional (FSLN) que llegó al poder en 1979?'),
    (8, 2, '¿Qué evento marcó el fin de la dictadura somocista?');
""")

con.commit()
print("Trivia 2 preguntas y respuestas")

con.execute("""
    INSERT INTO correct_responses (correct_response_id, question_id, trivia_id, correct_response_text) VALUES
    (13, 5, 2, '1821'),
    (16, 6, 2, 'La Guerra de los Contras'),
    (19, 7, 2, 'Daniel Ortega'),
    (22, 8, 2, 'La Revolución Sandinista');
""")
con.commit()
print("Trivia 2 preguntas y respuestas")

con.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text) VALUES
    (14, 5, 2, '1905'),
    (15, 5, 2, '1838'),
    (17, 6, 2, 'La Revolución Liberal'),
    (18, 6, 2, 'La Guerra Fría'),
    (20, 7, 2, 'Anastasio Somoza'),
    (21, 7, 2, 'Violeta Barrios'),
    (23, 8, 2, 'La Guerra de los Contras'),
    (24, 8, 2, 'La Revolución Liberal');
""")
con.commit()
print("Trivia 2 preguntas y respuestas")

# Insertar preguntas y respuestas para Trivia 3: Gastronomía Nicaragüense
con.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (9, 3, '¿Cuál es el plato nacional de Nicaragua?'),
    (10, 3, '¿Qué bebida tradicional se elabora con maíz fermentado?'),
    (11, 3, '¿Qué dulce típico es originario de León?'),
    (12, 3, '¿Cuál es la bebida típica que se toma en las fiestas de Nicaragua?');
""")
con.commit()
print("Trivia 3 preguntas y respuestas")

con.execute("""
    INSERT INTO correct_responses (correct_response_id, question_id, trivia_id, correct_response_text) VALUES
    (25, 9, 3, 'Gallo Pinto'),
   
    (28, 10, 3, 'Chicha'),
    
    (31, 11, 3, 'Cajeta de leche'),
  
    (34, 12, 3, 'Ron');
   
""")
con.commit()
print("Trivia 3 preguntas y respuestas")

con.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text) VALUES
    (26, 9, 3, 'Baho'),
    (27, 9, 3, 'Vigorón'),
    (29, 10, 3, 'Pinolillo'),
    (30, 10, 3, 'Cacao'),
    (32, 11, 3, 'Rosquillas'),
    (33, 11, 3, 'Turrón'),
    (35, 12, 3, 'Cerveza'),
    (36, 12, 3, 'Café');
""")
con.commit()
print("Trivia 3 preguntas y respuestas")

# Insertar preguntas y respuestas para Trivia 4: Literatura Nicaragüense
con.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (13, 4, '¿Quién es considerado el poeta más importante de Nicaragua?'),
    (14, 4, '¿En qué año Rubén Darío publicó *Azul*?'),
    (15, 4, '¿Qué corriente literaria es asociada con Rubén Darío?'),
    (16, 4, '¿Qué poeta nicaragüense ganó el Premio Cervantes en 2005?');
""")
con.commit()
print("Trivia 4 preguntas y respuestas")

con.execute("""
    INSERT INTO correct_responses (correct_response_id, question_id, trivia_id, correct_response_text) VALUES
    (37, 13, 4, 'Rubén Darío'),
   
    (40, 14, 4, '1888'),
   
    (43, 15, 4, 'Modernismo'),
    
    (46, 16, 4, 'Carlos Martínez Rivas');
    
""")
con.commit()
print("Trivia 4 preguntas y respuestas")
con.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text) VALUES
    (38, 13, 4, 'Ernesto Cardenal'),
    (39, 13, 4, 'Salomón de la Selva'),
    (41, 14, 4, '1890'),
    (42, 14, 4, '1875'),
    (44, 15, 4, 'Romanticismo'),
    (45, 15, 4, 'Realismo'),
    (47, 16, 4, 'Gioconda Belli'),
    (48, 16, 4, 'Darío Jaramillo');
""")
con.commit()
print("Trivia 4 preguntas y respuestas")
# Insertar preguntas y respuestas para Trivia 5: Leyendas de Nicaragua
con.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (17, 5, '¿Qué leyenda nicaragüense habla de una mujer que perdió su hijo en un naufragio?'),
    (18, 5, '¿Cómo se llama el fantasma que persigue a las personas en las montañas nicaragüenses?'),
    (19, 5, '¿Cuál es la leyenda que habla de un hombre que transformó su alma en un perro?'),
    (20, 5, '¿Qué leyenda se asocia con un demonio que castiga a los habitantes de una ciudad?');
""")
con.commit()
print("Trivia 5 preguntas y respuestas")
con.execute("""
    INSERT INTO correct_responses (correct_response_id, question_id, trivia_id, correct_response_text) VALUES
    (49, 17, 5, 'La Llorona'),
  
    (52, 18, 5, 'El Cadejo'),
   
    (55, 19, 5, 'El Chacal'),
   
    (58, 20, 5, 'La Sombra del Diablo');
    
""")
con.commit()
print("Trivia 5 preguntas y respuestas")
con.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text) VALUES
    (50, 17, 5, 'El Cipitío'),
    (51, 17, 5, 'El Sombrerón'),
    (53, 18, 5, 'El Duende'),
    (54, 18, 5, 'La Mocuana'),
    (56, 19, 5, 'El Sapo'),
    (57, 19, 5, 'El Brujo'),
    (59, 20, 5, 'La Luz Mala'),
    (60, 20, 5, 'La Sombra del Viento');
""")
con.commit()
print("Trivia 5 preguntas y respuestas")

# Insertar preguntas y respuestas para Trivia 6: Flora y Fauna de Nicaragua
con.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (21, 6, '¿Cuál es el ave nacional de Nicaragua?'),
    (22, 6, '¿Qué animal es considerado símbolo de la fauna de Nicaragua?'),
    (23, 6, '¿Cuál es el árbol nacional de Nicaragua?'),
    (24, 6, '¿Qué especie de tortuga se encuentra en las costas de Nicaragua?');
""")
con.commit()
print("Trivia 6 preguntas y respuestas")

con.execute("""
    INSERT INTO correct_responses (correct_response_id, question_id, trivia_id, correct_response_text) VALUES
    (61, 21, 6, 'La Guacamaya'),
   
    (64, 22, 6, 'El Jaguar'),
    
    (67, 23, 6, 'El Ceibo'),
    
    (70, 24, 6, 'La Tortuga Carey');
   
""")
con.commit()
print("Trivia 6 preguntas y respuestas")

con.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text) VALUES
    (62, 21, 6, 'El Quetzal'),
    (63, 21, 6, 'El Tucán'),
    (65, 22, 6, 'El Mono Araña'),
    (66, 22, 6, 'El León'),   
    (68, 23, 6, 'El Pinus'),
    (69, 23, 6, 'El Roble'),
    (71, 24, 6, 'La Tortuga Baula'),
    (72, 24, 6, 'La Tortuga Verde');
""")
con.commit()
print("Trivia 6 preguntas y respuestas")

# Insertar preguntas y respuestas para Trivia 7: Geografía de Nicaragua
con.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (25, 7, '¿Cuál es el lago más grande de Nicaragua?'),
    (26, 7, '¿En qué departamento se encuentra la ciudad de León?'),
    (27, 7, '¿Qué océano baña las costas del país al oeste?'),
    (28, 7, '¿Cuál es el río más largo de Nicaragua?');
""")
con.commit()
print("Trivia 7 preguntas y respuestas")

con.execute("""
    INSERT INTO correct_responses (correct_response_id, question_id, trivia_id, correct_response_text) VALUES
    (73, 25, 7, 'Lago Cocibolca'),
    
    (76, 26, 7, 'León'),
 
    (79, 27, 7, 'Océano Pacífico'),
    
    (82, 28, 7, 'Río San Juan');
    
""")
con.commit()
print("Trivia 7 preguntas y respuestas")

con.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text) VALUES
    
    (74, 25, 7, 'Lago Xolotlan'),
    (75, 25, 7, 'Lago de Cocibolca'),
    (77, 26, 7, 'Chinandega'),
    (78, 26, 7, 'Managua'),
    (80, 27, 7, 'Océano Atlántico'),
    (81, 27, 7, 'Mar Caribe'),
    (83, 28, 7, 'Río Coco'),
    (84, 28, 7, 'Río Escondido');
""")
con.commit()
print("Trivia 7 preguntas y respuestas")
# Insertar preguntas y respuestas para Trivia 8: Cultura Nicaragüense
con.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (29, 8, '¿En qué ciudad de Nicaragua se celebra la fiesta de la Gritería?'),
    (30, 8, '¿Qué tipo de música es muy popular en las fiestas nicaragüenses?'),
    (31, 8, '¿Qué baile tradicional es famoso en Nicaragua?'),
    (32, 8, '¿Qué bebida alcohólica es típica de las festividades en Nicaragua?');
""")
con.commit()
print("Trivia 8 preguntas y respuestas")

con.execute("""
    INSERT INTO correct_responses (correct_response_id, question_id, trivia_id, correct_response_text) VALUES
    (85, 29, 8, 'Managua'),
   
    (88, 30, 8, 'Marimba'),
   
    (91, 31, 8, 'La Danza del Coyolito'),
    
    (94, 32, 8, 'El Ron');
    
""")
con.commit()
print("Trivia 8 preguntas y respuestas")

con.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text) VALUES
    (86, 29, 8, 'Granada'),
    (87, 29, 8, 'Masaya'),
    (89, 30, 8, 'Salsa'),
    (90, 30, 8, 'Cumbia'),
    (92, 31, 8, 'La Cumbia'),
    (93, 31, 8, 'El Merengue'),
    (95, 32, 8, 'La Cerveza'),
    (96, 32, 8, 'El Vino');
""")
con.commit()
print("Trivia 8 preguntas y respuestas")
# Insertar preguntas y respuestas para Trivia 9: Economía de Nicaragua
con.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (33, 9, '¿Cuál es la principal fuente de ingresos de Nicaragua?'),
    (34, 9, '¿En qué rubro se destaca principalmente la economía de Nicaragua?'),
    (35, 9, '¿Qué producto agrícola se cultiva más en Nicaragua?'),
    (36, 9, '¿En qué año Nicaragua firmó un tratado de libre comercio con los Estados Unidos?');
""")
con.commit()
print("Trivia 9 preguntas y respuestas")

con.execute("""
    INSERT INTO correct_responses (correct_response_id, question_id, trivia_id, correct_response_text) VALUES
    (97, 33, 9, 'Exportaciones de café'),
 
    (100, 34, 9, 'Agricultura'),
   
    (103, 35, 9, 'Café'),
   
    (106, 36, 9, '2005');
    
""")
con.commit()
print("Trivia 9 preguntas y respuestas")

con.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text) VALUES
    (98, 33, 9, 'Turismo'),
    (99, 33, 9, 'Pesca'),
    (101, 34, 9, 'Manufacturas'),
    (102, 34, 9, 'Servicios'),
    (104, 35, 9, 'Banano'),
    (105, 35, 9, 'Arroz'),
    (107, 36, 9, '2002'),
    (108, 36, 9, '2010');
""")
con.commit()
print("Trivia 9 preguntas y respuestas")
# Insertar preguntas y respuestas para Trivia 10: Turismo en Nicaragua
con.execute("""
    INSERT INTO questions (question_id, trivia_id, question_text) VALUES
    (37, 10, '¿Cuál es el destino turístico más visitado de Nicaragua?'),
    (38, 10, '¿Qué ciudad colonial es conocida como la “ciudad de los poetas”?'),
    (39, 10, '¿En qué región de Nicaragua se encuentra la Isla de Ometepe?'),
    (40, 10, '¿Qué parque nacional de Nicaragua es famoso por su volcán activo?');
""")
con.commit()
print("Trivia 10 preguntas y respuestas")

con.execute("""
    INSERT INTO correct_responses (correct_response_id, question_id, trivia_id, correct_response_text) VALUES
    (109, 37, 10, 'Granada'),
    (112, 38, 10, 'León'),
    (115, 39, 10, 'En el Lago Cocibolca'),
    (118, 40, 10, 'Parque Nacional Masaya');
""")

con.commit()
print("Trivia 10 preguntas y respuestas")

con.execute("""
    INSERT INTO responses (response_id, question_id, trivia_id, response_text) VALUES
    (110, 37, 10, 'León'),
    (111, 37, 10, 'Managua'),
    (113, 38, 10, 'Granada'),
    (114, 38, 10, 'Masaya'),
    (116, 39, 10, 'En el Lago Xolotlan'),
    (117, 39, 10, 'En el Caribe'),
    (119, 40, 10, 'Parque Nacional Volcán Cerro Negro'),
    (120, 40, 10, 'Parque Nacional Volcán San Cristóbal');
""")

con.commit()
print("Trivia 10 preguntas y respuestas")


print("Datos insertados correctamente.")
con.close()
