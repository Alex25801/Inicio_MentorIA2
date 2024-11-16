from pyexpat import model
import streamlit as st
import os
import google.generativeai as genai
import sqlite3

# Configuración de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Asegúrate de que esta variable de entorno esté configurada
genai.configure(api_key=GEMINI_API_KEY)

def init_db():
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_advising (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            user_input TEXT,
            bot_response TEXT
        )
    ''')
    conn.commit()
    return conn

def save_conversation(student_name, user_input, bot_response):
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student_advising (student_name, user_input, bot_response)
        VALUES (?, ?, ?)
    ''', (student_name, user_input, bot_response))
    conn.commit()
    conn.close()

def generar_recomendacion(intereses, habilidades, rendimiento):
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
    }
    
    modelo = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    
    universidades = {
        "Historia": {
            "Excelente": {
                "América Latina": {
                    "Universidad de Buenos Aires (Argentina)": ["Historia", "Ciencias Sociales"],
                    "Universidad de Chile": ["Historia", "Ciencias Políticas"],
                },
                "Europa": {
                    "Universidad de Oxford (Reino Unido)": ["Historia", "Arqueología"],
                    "Universidad de Cambridge (Reino Unido)": ["Historia", "Antropología"],
                },
                "Asia": {
                    "Universidad de Tokio (Japón)": ["Historia", "Ciencias Sociales"],
                },
            },
            "Bueno": {
                "América Latina": {
                    "Universidad Nacional de La Plata": ["Historia", "Filosofía"],
                },
                "Europa": {
                    "Universidad de Ámsterdam (Países Bajos)": ["Historia", "Ciencias Sociales"],
                },
                "Asia": {
                    "Universidad de Pekín (China)": ["Historia", "Ciencias Políticas"],
                },
            },
            "Promedio": {
                "América Latina": {
                    "Universidad de San Marcos (Perú)": ["Historia", "Ciencias Sociales"],
                },
                "Europa": {
                    "Universidad de Lisboa (Portugal)": ["Historia", "Ciencias Sociales"],
                },
                "Asia": {
                    "Universidad de Seúl (Corea del Sur)": ["Historia", "Ciencias Sociales"],
                },
            },
            "Necesita mejorar": {
                "América Latina": {
                    "Universidad de la Habana (Cuba)": ["Historia", "Ciencias Sociales"],
                },
                "Europa": {
                    "Universidad de Varsovia (Polonia)": ["Historia", "Ciencias Sociales"],
                },
                "Asia": {
                    "Universidad de Manila (Filipinas)": ["Historia", "Ciencias Sociales"],
                },
            },
        },
        "Ciencias Sociales": {
            "Excelente": {
                "América Latina": {
                    "Universidad Nacional Autónoma de México (UNAM)": ["Sociología", "Psicología"],
                },
                "Europa": {
                    "London School of Economics (Reino Unido)": ["Ciencias Sociales", "Economía"],
                },
                "Asia": {
                    "Universidad de Singapur": ["Ciencias Sociales", "Psicología"],
                },
            },
            "Bueno": {
                "América Latina": {
                    "Universidad de los Andes (Colombia)": ["Ciencias Políticas", "Psicología"],
                },
                "Europa": {
                    "Universidad de Ámsterdam (Países Bajos)": ["Ciencias Sociales", "Antropología"],
                },
                "Asia": {
                    "Universidad de Seúl (Corea del Sur)": ["Ciencias Sociales", "Sociología"],
                },
            },
            "Promedio": {
                "América Latina": {
                    "Universidad de Costa Rica": ["Ciencias Sociales", "Psicología"],
                },
                "Europa": {
                    "Universidad de Lisboa (Portugal)": ["Ciencias Sociales", "Antropología"],
                },
                "Asia": {
                    "Universidad de Tailandia": ["Ciencias Sociales", "Psicología"],
                },
            },
            "Necesita mejorar": {
                "América Latina": {
                    "Universidad de la Habana (Cuba)": ["Ciencias Sociales", "Psicología"],
                },
                "Europa": {
                    "Universidad de Varsovia (Polonia)": ["Ciencias Sociales", "Antropología"],
                },
                "Asia": {
                    "Universidad de Manila (Filipinas)": ["Ciencias Sociales", "Psicología"],
                },
            },
        },
        # Agregar más áreas de especialización de manera similar...
    }
    
    prompt = f"""
    Basándote en la siguiente información de un estudiante:
    
    Intereses: {intereses}
    Habilidades: {habilidades}
    Rendimiento académico: {rendimiento}
    
    Sugiere posibles trayectorias educativas y profesionales. Proporciona al menos 3 opciones 
    con una breve explicación de por qué podrían ser adecuadas.
    """
    
    respuesta = modelo.generate_content(prompt)
    recomendaciones = respuesta.text
    area_especializacion = ""
    
    for area in universidades.keys():
        if area in intereses:
            area_especializacion = area
            break
    
    if area_especializacion and area_especializacion in universidades:
        universidades_recomendadas = universidades[area_especializacion][rendimiento]
        recomendaciones += f"\n\n**Universidades y carreras recomendadas para estudiar {area_especializacion} con rendimiento {rendimiento}:**\n"
        
        for continente, lista in universidades_recomendadas.items():
            recomendaciones += f"- **{continente}:**\n"
            for universidad, carreras in lista.items():
                recomendaciones += f"  - {universidad}: " + ", ".join(carreras) + "\n"
    
    return recomendaciones

def test_cultura_general():
    st.subheader("Prueba de Cultura General")
    preguntas = [
        {
            "pregunta": "¿Cuál es la capital de Francia?",
            "opciones": ["Berlín", "Madrid", "París", "Roma"],
            "respuesta_correcta": "París"
        },
        {
            "pregunta": "¿Cuánto es 15 dividido por 3?",
            "opciones": ["3", "4", "5", "6"],
            "respuesta_correcta": "5"
        },
        {
            "pregunta": "¿Qué órgano del cuerpo humano bombea sangre?",
            "opciones": ["Pulmones", "Hígado", "Corazón", "Riñones"],
            "respuesta_correcta": "Corazón"
        },
        {
            "pregunta": "¿Qué es el PIB?",
            "opciones": ["Producto Interno Bruto", "Producto Internacional Bruto", "Producto Interno Bursátil", "Producto Internacional Bursátil"],
            "respuesta_correcta": "Producto Interno Bruto"
        },
        {
            "pregunta": "¿Cuál es la unidad básica de la vida?",
            "opciones": ["Tejido", "Órgano", "Célula", "Sistema"],
            "respuesta_correcta": "Célula"
        },
        {
            "pregunta": "¿En qué año comenzó la Segunda Guerra Mundial?",
            "opciones": ["1939", "1941", "1945", "1936"],
            "respuesta_correcta": "1939"
        },
        {
            "pregunta": "¿Qué tipo de hueso es el fémur?",
            "opciones": ["Hueso largo", "Hueso corto", "Hueso plano", "Hueso irregular"],
            "respuesta_correcta": "Hueso largo"
        },
        {
            "pregunta": "¿Qué es la inflación?",
            "opciones": ["Aumento generalizado de precios", "Disminución de precios", "Estabilidad de precios", "Aumento de la producción"],
            "respuesta_correcta": "Aumento generalizado de precios"
        },
        {
            "pregunta": "¿Cuál es el océano más grande del mundo?",
            "opciones": ["Atlántico", "Índico", "Ártico", "Pacífico"],
            "respuesta_correcta": "Pacífico"
        },
        {
            "pregunta": "¿Quién escribió 'Cien años de soledad'?",
            "opciones": ["Gabriel García Márquez", "Mario Vargas Llosa", "Jorge Luis Borges", "Pablo Neruda"],
            "respuesta_correcta": "Gabriel García Márquez"
        },
        {
            "pregunta": "¿Qué es un número primo?",
            "opciones": ["Un número que solo es divisible por 1 y por sí mismo", "Un número que tiene más de dos divisores", "Un número que termina en 0", "Un número que es par"],
            "respuesta_correcta": "Un número que solo es divisible por 1 y por sí mismo"
        },
        {
            "pregunta": "¿Cuál es la capital de Japón?",
            "opciones": ["Seúl", "Tokio", "Pekín", "Bangkok"],
            "respuesta_correcta": "Tokio"
        },
        {
            "pregunta": "¿Qué es un antiséptico?",
            "opciones": ["Un medicamento para aliviar el dolor", "Una sustancia que previene la infección", "Un tipo de anestesia", "Un tratamiento para enfermedades crónicas"],
            "respuesta_correcta": "Una sustancia que previene la infección"
        },
        {
            "pregunta": "¿Cuál es la raíz cuadrada de 144?",
            "opciones": ["10", "11", "12", "13"],
            "respuesta_correcta": "12"
        },
        {
            "pregunta": "¿Quién fue el primer presidente de los Estados Unidos?",
            "opciones": ["Abraham Lincoln", "George Washington", "Thomas Jefferson", "John Adams"],
            "respuesta_correcta": "George Washington"
        },
        {
            "pregunta": "¿Cuál es el continente más grande del mundo?",
            "opciones": ["África", "Asia", "América", "Europa"],
            "respuesta_correcta": "Asia"
        },
        # ... (mantén el resto de tu lógica de puntuación aquí) ...
    ]
    
    st.write("Responde las siguientes preguntas:")
    respuestas_usuario = {}
    for i, pregunta in enumerate(preguntas):
        respuesta = st.radio(pregunta["pregunta"], pregunta["opciones"], key=f"pregunta_{i}")
        respuestas_usuario[i] = respuesta
    
    if st.button("Verificar respuestas", key="verificar_cultura_general"):
        puntuacion = 0
        for i, pregunta in enumerate(preguntas):
            st.write(f"**{pregunta['pregunta']}**")
            respuesta_usuario = respuestas_usuario[i]
            st.write(f"Tu respuesta: {respuesta_usuario}")
            
            if respuesta_usuario == pregunta["respuesta_correcta"]:
                st.markdown(f"<div style='background-color: #d4edda; padding: 5px;'>¡Correcto! ✅</div>", unsafe_allow_html=True)
                puntuacion += 1.25  # Cada respuesta correcta vale 1.25 puntos
            else:
                st.markdown(f"<div style='background-color: #f8d7da; padding: 5px;'>Respuesta correcta: {pregunta['respuesta_correcta']} ❌</div>", unsafe_allow_html=True)
        
        st.success(f"Has obtenido {puntuacion} de 20 puntos.")

def analizar_habilidades(respuestas):
    habilidades_descubiertas = []
    explicaciones = []
    fortalezas = []
    areas_mejora = []

    # Evaluar respuestas y generar explicaciones
    if respuestas[0] == "Leer libros":
        habilidades_descubiertas.append("Lectura crítica")
        explicaciones.append(
            "Leer libros mejora tu capacidad de análisis y comprensión."
        )
        fortalezas.append("Tienes una inclinación hacia el aprendizaje.")

    if respuestas[1] == "Comunicación":
        habilidades_descubiertas.append("Habilidades de comunicación")
        explicaciones.append(
            "La comunicación efectiva es esencial en casi todas las profesiones."
        )
        fortalezas.append("Tienes la capacidad de conectar con los demás.")

    # Agregar más evaluaciones según las respuestas...

    # Generar un mensaje de retroalimentación
    mensaje = "### Análisis de tus Habilidades\n\n"
    mensaje += "#### Fortalezas:\n"
    if fortalezas:
        mensaje += "- " + "\n- ".join(fortalezas) + "\n\n"
    else:
        mensaje += "No se identificaron fortalezas específicas.\n\n"

    mensaje += "#### Habilidades Descubiertas:\n"
    if habilidades_descubiertas:
        mensaje += "- " + "\n- ".join(habilidades_descubiertas) + "\n\n"
        mensaje += "#### Explicaciones:\n"
        for exp in explicaciones:
            mensaje += f"- {exp}\n"
    else:
        mensaje += "No se identificaron habilidades específicas."

    return mensaje

def preguntas_api():
    st.subheader("Descubre tus Habilidades")
    st.write("¡Hola! Estoy aquí para ayudarte a descubrir tus habilidades y cómo pueden influir en tu trayectoria educativa y profesional. Responde las siguientes preguntas para que podamos conocerte mejor.")
    
    preguntas = [
        {
            "pregunta": "¿Qué actividad disfrutas más en tu tiempo libre?",
            "opciones": ["Leer libros", "Hacer ejercicio", "Jugar videojuegos", "Cocinar"],
            "explicacion": "Esta pregunta nos ayuda a entender tus intereses y pasiones, que son fundamentales para tu desarrollo personal."
        },
        {
            "pregunta": "¿Cuál de las siguientes habilidades consideras más importante para tu carrera?",
            "opciones": ["Comunicación", "Análisis de datos", "Creatividad", "Liderazgo"],
            "explicacion": "Identificar tus habilidades clave puede guiarte hacia una carrera que se alinee con tus fortalezas."
        },
        {
            "pregunta": "Cuando enfrentas un problema, ¿cómo sueles resolverlo?",
            "opciones": ["Analizo la situación", "Pido ayuda a otros", "Confío en mi intuición", "Busco información"],
            "explicacion": "Tu enfoque para resolver problemas puede revelar mucho sobre tu estilo de trabajo y tu capacidad de adaptación."
        },
        {
            "pregunta": "¿Qué tipo de trabajo prefieres?",
            "opciones": ["Trabajo en equipo", "Trabajo individual", "Trabajo en un entorno dinámico", "Trabajo estructurado"],
            "explicacion": "Conocer tu preferencia de trabajo puede ayudarte a encontrar un entorno laboral que te motive."
        },
        {
            "pregunta": "¿Qué te motiva más en tu vida cotidiana?",
            "opciones": ["Aprender cosas nuevas", "Ayudar a los demás", "Lograr mis metas personales", "Disfrutar de mis pasatiempos"],
            "explicacion": "Entender tus motivaciones puede guiarte hacia una carrera que te brinde satisfacción y propósito."
        },
        {
            "pregunta": "¿Cómo te sientes al trabajar bajo presión?",
            "opciones": ["Me gusta el desafío", "Me estresa un poco", "Prefiero un ambiente tranquilo", "No me importa"],
            "explicacion": "Tu respuesta a esta pregunta puede indicar cómo manejas situaciones desafiantes en el trabajo."
        },
        {
            "pregunta": "¿Qué tipo de feedback prefieres recibir?",
            "opciones": ["Crítico y directo", "Positivo y motivador", "Constructivo y equilibrado", "No me gusta recibir feedback"],
            "explicacion": "Saber cómo prefieres recibir feedback puede ayudarte a crecer y mejorar en tu carrera."
        },
        {
            "pregunta": "¿Cuál es tu estilo de aprendizaje preferido?",
            "opciones": ["Visual", "Auditivo", "Kinestésico", "Lectura/escritura"],
            "explicacion": "Conocer tu estilo de aprendizaje puede ayudarte a elegir métodos de estudio que te beneficien."
        },
        {
            "pregunta": "¿Qué habilidades crees que son más importantes para tu futuro?",
            "opciones": ["Habilidades técnicas", "Habilidades interpersonales", "Habilidades de gestión", "Habilidades creativas"],
            "explicacion": "Identificar las habilidades que valoras puede guiarte en tu desarrollo profesional."
        },
        {
            "pregunta": "¿Cómo te sientes al aprender cosas nuevas?",
            "opciones": ["Emocionado", "Nervioso", "Indiferente", "Frustrado"],
            "explicacion": "Tu actitud hacia el aprendizaje puede influir en tu crecimiento personal y profesional."
        },
        {
            "pregunta": "¿Cuál ha sido tu mayor fracaso y qué aprendiste de él?",
            "opciones": ["No he tenido fracasos significativos", "Un proyecto que no salió como esperaba", "Una relación que no funcionó", "Un examen que no aprobé"],
            "explicacion": "Reflexionar sobre los fracasos puede ayudarte a identificar áreas de mejora y crecimiento."
        },
        {
            "pregunta": "¿Qué te impide alcanzar tus metas?",
            "opciones": ["Falta de tiempo", "Miedo al fracaso", "Falta de apoyo", "No estoy seguro de mis metas"],
            "explicacion": "Identificar obstáculos puede ser el primer paso para superarlos y avanzar hacia tus objetivos."
        },
        {
            "pregunta": "¿Cómo manejas la crítica o el rechazo?",
            "opciones": ["Lo tomo de manera constructiva", "Me siento herido", "Lo ignoro", "Me motiva a mejorar"],
            "explicacion": "Entender cómo manejas la crítica puede ayudarte a desarrollar una mentalidad más resiliente."
        },
    ]
    
    respuestas_usuario = {}
    for i, pregunta in enumerate(preguntas):
        st.write(f"**{pregunta['pregunta']}**")
        st.write(f"*{pregunta['explicacion']}*")
        respuesta = st.radio("Selecciona una opción:", pregunta["opciones"], key=f"pregunta_api_{i}")
        respuestas_usuario[i] = respuesta
    
    if st.button("Enviar respuestas", key="enviar_api"):
        habilidades = analizar_habilidades(respuestas_usuario)
        st.subheader("Análisis de Habilidades")
        st.write(habilidades)

# Interfaz de Streamlit
col1, col2 = st.columns([4, 1])

with col1:
    st.title("Recomendador de Trayectorias Educativas y Profesionales")
with col2:
    st.image("descarga.jpg", width=100)

# Crear pestañas
tab1, tab2, tab3 = st.tabs(["Prueba de Cultura General", "Recomendación", "Descubre"])

with tab1:
    test_cultura_general()

with tab2:
    intereses = st.text_area("Ingresa tus intereses (separados por comas):")
    habilidades = st.text_area("Ingresa tus habilidades (separadas por comas):")
    rendimiento = st.selectbox("Selecciona tu rendimiento académico:", 
                               ["Excelente", "Bueno", "Promedio", "Necesita mejorar"])

    if st.button("Generar recomendación", key="generar_recomendacion"):
        if intereses and habilidades:
            with st.spinner("Generando recomendaciones..."):
                recomendacion = generar_recomendacion(intereses, habilidades, rendimiento)
            st.subheader("Recomendaciones:")
            st.write(recomendacion)
        else:
            st.warning("Por favor, ingresa tus intereses y habilidades.")

with tab3:
    preguntas_api()

# Estilo CSS para la aplicación
st.markdown(
    """
    <style>
    /* Estilo para el cuerpo principal de la aplicación */
    .stApp {
        background-color: #0A192F;  /* Azul muy oscuro */
        color: #FFFFFF;  /* Texto blanco */
    }
    
    /* Estilo para la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #D3D3D3;  /* Gris claro */
        padding: 10px;  /* Añadir un poco de espacio */
        height: auto;  /* Cambiado para que la barra lateral ajuste su altura automáticamente */
    }
    [data-testid="stSidebar"] * {
        color: #000000 !important;  /* Texto negro */
    }
    
    /* Asegurarse de que el contenido de la barra lateral sea visible */
    .sidebar-content {
        display: block;  /* Asegurarse de que el contenido se muestre */
    }

    /* Estilo para los inputs de la barra lateral */
    .stTextInput > div > input {
        color: #ffffff !important; /* Texto blanco */
        background-color: #007BFF !important;  /* Color de fondo azul (similar al botón) */
        border: 2px solid #0056b3 !important; /* Bordes azules oscuros */
        border-radius: 5px; /* Bordes redondeados */
        padding: 10px; /* Espaciado interno */
    }
    .stTextInput > div > input:focus {
        border: 2px solid #0056b3 !important; /* Bordes azules oscuros al enfocar */
        outline: none; /* Sin contorno al enfocar */
    }
    .stTextInput > div > input::placeholder {
        color: #ffffff !important; /* Texto blanco para el placeholder */
    }
    .stTextInput > div > input:disabled {
        color: #ffffff !important; /* Texto blanco para inputs deshabilitados */
        background-color: #6c757d !important; /* Color de fondo gris para inputs deshabilitados */
    }
    .stTextInput > div > input:read-only {
        color: #ffffff !important; /* Texto blanco para inputs de solo lectura */
        background-color: #6c757d !important; /* Color de fondo gris para inputs de solo lectura */
    }
    .stTextArea > div > textarea {
        color: #ffffff !important; /* Texto blanco para textarea */
        background-color: #007BFF !important;  /* Color de fondo azul (similar al botón) */
        border: 2px solid #0056b3 !important; /* Bordes azules oscuros */
        border-radius: 5px; /* Bordes redondeados */
        padding: 10px; /* Espaciado interno */
    }
    .stTextArea > div > textarea:focus {
        border: 2px solid #0056b3 !important; /* Bordes azules oscuros al enfocar */
        outline: none; /* Sin contorno al enfocar */
    }
    .stTextArea > div > textarea::placeholder {
        color: #ffffff !important; /* Texto blanco para el placeholder */
    }
    .stTextArea > div > textarea:disabled {
        color: #ffffff !important; /* Texto blanco para textarea deshabilitado */
        background-color: #6c757d !important; /* Color de fondo gris para textarea deshabilitado */
    }
    .stTextArea > div > textarea:read-only {
        color: #ffffff !important; /* Texto blanco para textarea de solo lectura */
        background-color: #6c757d !important; /* Color de fondo gris para textarea de solo lectura */
    }

    </style>
    """,
    unsafe_allow_html=True
)



# Agregar la barra lateral con el chatbot Asimov
st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

st.sidebar.title("Asimov - Asistente Vocacional")

student_name = st.sidebar.text_input("¡Hola soy Asimov 🦊!. Ingresa tu nombre completo para comenzar tu viaje hacia la carrera ideal:")
user_input = st.sidebar.text_input("Cuéntame, ¿qué es lo que realmente te preocupa sobre tu futuro académico?")

if user_input:
    # Usar el modelo de Gemini para generar una respuesta
    prompt = f"Como Asimov, un asistente vocacional, responde a la siguiente preocupación de un estudiante: '{user_input}'. Asegúrate de empatizar y recomendar que la mentoría puede ayudar con su recomendador de carreras."
    respuesta = genai.GenerativeModel(model_name="gemini-1.5-flash").generate_content(prompt).text
    st.sidebar.markdown(f'🦊 Respuesta del asistente: {respuesta}')
    save_conversation(student_name, user_input, respuesta)

if st.sidebar.button('Mostrar alerta'):
    st.sidebar.write("Gracias que tenga un buen día 🦊")

st.sidebar.markdown('</div>', unsafe_allow_html=True)
