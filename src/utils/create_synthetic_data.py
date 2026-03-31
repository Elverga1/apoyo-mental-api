import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Síntomas del PHQ-9
SYMPTOMS = [
    "animo_deprimido",
    "anhedonia",
    "problemas_sueno",
    "fatiga",
    "apetito",
    "culpa",
    "concentracion",
    "psicomotor",
    "suicidio"
]

# Frases base por nivel de severidad (0-3)
PHRASES_BY_SEVERITY = {
    0: [
        "Me siento bien hoy",
        "Todo va normal",
        "Disfruto mis actividades",
        "Duermo bien por las noches",
        "Tengo energía para hacer mis cosas",
        "Estoy contento con mi día",
        "Me siento motivado",
        "Las cosas van bien"
    ],
    1: [
        "Me siento un poco decaído",
        "A veces pierdo el interés",
        "Me cuesta un poco dormir",
        "Me siento un poco cansado",
        "A veces me siento culpable",
        "No estoy al 100% pero voy bien",
        "Me siento un poco triste hoy",
        "Me cuesta concentrarme a veces"
    ],
    2: [
        "Me siento triste la mayoría del día",
        "No disfruto casi nada",
        "Duermo muy mal",
        "Estoy cansado todo el tiempo",
        "Me siento inútil frecuentemente",
        "No le encuentro sentido a las cosas",
        "Me cuesta mucho levantarme",
        "Siento que todo me sale mal"
    ],
    3: [
        "No puedo dejar de sentirme triste",
        "Nada me interesa, nada me importa",
        "No duermo nada o duermo todo el día",
        "No tengo energía para nada",
        "Siento que soy una carga para los demás",
        "He pensado en que sería mejor no estar aquí",
        "No puedo más con esto",
        "Ya no quiero seguir así",
        "Siento que no hay salida"
    ]
}

def generate_user_text(symptom_vector):
    """Genera un texto de usuario basado en sus síntomas"""
    texts = []
    
    # Selecciona frases según los síntomas más severos
    for i, score in enumerate(symptom_vector[:9]):
        if score > 0:
            phrases = PHRASES_BY_SEVERITY.get(score, PHRASES_BY_SEVERITY[0])
            # A veces no incluir todas las frases para variar
            if random.random() > 0.3:
                texts.append(random.choice(phrases))
    
    # Añadir frases introductorias para variar
    if random.random() > 0.6:
        intro = random.choice([
            "Hoy me siento...", 
            "Quiero compartir cómo me siento: ",
            "Mi estado de ánimo hoy es: ",
            "Siento que ",
            "La verdad es que "
        ])
        texts.insert(0, intro)
    
    # Añadir preguntas o desahogos
    if random.random() > 0.7:
        texts.append(random.choice([
            "¿Crees que esto va a mejorar?",
            "No sé qué hacer con mi vida",
            "¿Alguna vez te has sentido así?",
            "Necesito ayuda pero no sé cómo pedirla"
        ]))
    
    # Añadir despedida
    if random.random() > 0.8:
        texts.append(random.choice([
            "Gracias por escuchar",
            "Eso es todo por hoy",
            "Solo quería desahogarme"
        ]))
    
    return " ".join(texts)

def generate_dataset(n_samples=2000):
    """Genera dataset sintético con vectores de síntomas"""
    data = []
    
    for i in range(n_samples):
        # Generar vector de síntomas con correlaciones realistas
        # Primero definir la severidad base
        # Distribución más realista: más casos leves/moderados
        base_severity = np.random.choice([0, 1, 2, 3], p=[0.25, 0.35, 0.30, 0.10])
        
        symptom_vector = []
        for symptom_idx in range(9):
            # Los síntomas tienden a correlacionarse con la severidad base
            # Pero con variación individual
            if symptom_idx == 8:  # Suicidio es menos común incluso en depresión severa
                if base_severity == 0:
                    probs = [0.92, 0.06, 0.02, 0.00]
                elif base_severity == 1:
                    probs = [0.85, 0.10, 0.04, 0.01]
                elif base_severity == 2:
                    probs = [0.70, 0.18, 0.10, 0.02]
                else:  # severidad 3
                    probs = [0.50, 0.25, 0.15, 0.10]
            else:
                # Para otros síntomas, más correlación con severidad base
                if base_severity == 0:
                    probs = [0.70, 0.20, 0.08, 0.02]
                elif base_severity == 1:
                    probs = [0.30, 0.40, 0.25, 0.05]
                elif base_severity == 2:
                    probs = [0.10, 0.30, 0.40, 0.20]
                else:  # severidad 3
                    probs = [0.05, 0.15, 0.35, 0.45]
            
            score = np.random.choice([0, 1, 2, 3], p=probs)
            symptom_vector.append(score)
        
        # Calcular puntuación total PHQ-9
        total_score = sum(symptom_vector)
        
        # Clasificar severidad según PHQ-9
        if total_score <= 4:
            severity = "minima"
        elif total_score <= 9:
            severity = "leve"
        elif total_score <= 14:
            severity = "moderada"
        elif total_score <= 19:
            severity = "moderada_grave"
        else:
            severity = "grave"
        
        # Generar texto del usuario basado en sus síntomas
        user_text = generate_user_text(symptom_vector)
        
        # Crear registro
        record = {
            'id': i,
            'text': user_text,
            'phq9_total': total_score,
            'severity': severity,
        }
        
        # Añadir cada síntoma individualmente
        for idx, symptom_name in enumerate(SYMPTOMS):
            record[f'symptom_{idx+1}_{symptom_name}'] = symptom_vector[idx]
        
        data.append(record)
    
    df = pd.DataFrame(data)
    return df

# Generar y guardar
if __name__ == "__main__":
    print("Generando dataset sintético...")
    df = generate_dataset(2000)
    
    # Guardar a CSV
    df.to_csv('data/synthetic_depression_data.csv', index=False)
    
    print(f"\n✅ Dataset generado: {len(df)} muestras")
    print("\n📊 Distribución de severidad:")
    print(df['severity'].value_counts())
    
    print("\n📝 Ejemplo de texto generado:")
    print("-" * 50)
    for i in range(3):
        print(f"Ejemplo {i+1}: {df['text'].iloc[i][:200]}...")
        print(f"Severidad: {df['severity'].iloc[i]}")
        print(f"Puntaje PHQ-9: {df['phq9_total'].iloc[i]}")
        print("-" * 50)
    
    print("\n✅ Archivo guardado en: data/synthetic_depression_data.csv")