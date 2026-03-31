"""
Clasificador de Riesgo Suicida para Apoyo Mental
Detecta crisis y activa protocolos de emergencia
"""

import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Palabras clave de crisis en español mexicano
CRISIS_KEYWORDS = {
    'alto': [
        'suicidio', 'suicidarme', 'matarme', 'matar', 'morir', 'muerte',
        'acabar con todo', 'acabar con mi vida', 'no quiero vivir',
        'quitarme la vida', 'desuscribirme', 'adiós', 'despedirme',
        'me voy a matar', 'me quiero morir', 'no puedo más', 'ya no aguanto',
        'me rindo', 'terminar con esto', 'me voy a suicidar',
        'no tiene caso seguir', 'mejor morir', 'dejar de existir'
    ],
    'medio': [
        'desesperado', 'desesperación', 'sin salida', 'no le veo sentido',
        'carga para otros', 'molesto para todos', 'mejor no existir',
        'desaparecer', 'huir', 'escapar', 'no sirvo para nada',
        'inútil', 'fracaso', 'nadie me quiere', 'todo está perdido',
        'no hay esperanza', 'nunca voy a mejorar', 'no puedo seguir'
    ],
    'bajo': [
        'triste', 'tristeza', 'cansado', 'agotado', 'sin energía',
        'sin ganas', 'desánimo', 'abatido', 'deprimido', 'soledad',
        'vacío', 'sin motivación', 'desgana', 'apático'
    ]
}

# Combinar todas las palabras clave para búsqueda rápida
ALL_CRISIS_WORDS = set()
for words in CRISIS_KEYWORDS.values():
    ALL_CRISIS_WORDS.update(words)


class SuicideRiskClassifier:
    """
    Clasificador de riesgo suicida basado en ML clásico + reglas
    """
    
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.is_trained = False
        
    def extract_linguistic_features(self, text):
        """
        Extrae features lingüísticas específicas para detección de crisis
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        # Conteos básicos
        word_count = len(words)
        
        # Conteo de palabras por nivel de crisis
        crisis_high = sum(1 for w in words if w in CRISIS_KEYWORDS['alto'])
        crisis_medium = sum(1 for w in words if w in CRISIS_KEYWORDS['medio'])
        crisis_low = sum(1 for w in words if w in CRISIS_KEYWORDS['bajo'])
        
        # Pronombres en primera persona (autofoco, común en depresión)
        first_person = sum(1 for w in words if w in ['yo', 'me', 'mi', 'mí', 'conmigo', 'mismo'])
        
        # Negaciones (indican pensamiento negativo)
        negations = sum(1 for w in words if w in ['no', 'nunca', 'nada', 'nadie', 'jamás', 'ninguno', 'ni'])
        
        # Palabras desesperanzadoras
        hopelessness = sum(1 for w in words if w in ['nunca', 'siempre', 'imposible', 'nada', 'todo mal'])
        
        # Longitud promedio de palabras
        avg_word_length = np.mean([len(w) for w in words]) if words else 0
        
        # Puntuación
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        # Proporciones
        if word_count > 0:
            crisis_ratio = (crisis_high + crisis_medium) / word_count
        else:
            crisis_ratio = 0
            
        features = {
            'word_count': word_count,
            'crisis_high': crisis_high,
            'crisis_medium': crisis_medium,
            'crisis_low': crisis_low,
            'first_person': first_person,
            'negations': negations,
            'hopelessness': hopelessness,
            'avg_word_length': avg_word_length,
            'exclamation_count': exclamation_count,
            'question_count': question_count,
            'crisis_ratio': crisis_ratio,
            # Feature binaria: contiene palabras de alto riesgo
            'has_high_risk_word': 1 if crisis_high > 0 else 0,
            # Feature: múltiples palabras de alto riesgo
            'multiple_high_risk': 1 if crisis_high >= 2 else 0
        }
        
        return features
    
    def _rule_based_risk(self, text):
        """
        Evaluación basada en reglas (cuando no hay modelo entrenado)
        """
        features = self.extract_linguistic_features(text)
        
        # Reglas de alto riesgo
        if features['crisis_high'] >= 2:
            risk = 'alto'
            confidence = 0.95
            action = True
        elif features['crisis_high'] == 1:
            risk = 'alto'
            confidence = 0.85
            action = True
        elif features['crisis_medium'] >= 3:
            risk = 'alto'
            confidence = 0.80
            action = True
        elif features['crisis_medium'] >= 2:
            risk = 'moderado'
            confidence = 0.75
            action = False
        elif features['crisis_medium'] >= 1 or features['crisis_low'] >= 3:
            risk = 'moderado'
            confidence = 0.65
            action = False
        elif features['crisis_low'] >= 2:
            risk = 'bajo'
            confidence = 0.60
            action = False
        else:
            risk = 'bajo'
            confidence = 0.55
            action = False
            
        return {
            'risk_level': risk,
            'confidence': confidence,
            'requires_immediate_action': action,
            'features': features
        }
    
    def train(self, texts, labels):
        """
        Entrena el clasificador con datos etiquetados
        labels: 0 = sin riesgo, 1 = riesgo bajo, 2 = riesgo moderado, 3 = riesgo alto
        """
        from scipy.sparse import hstack
        
        # Vectorizador TF-IDF para el texto
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.9
        )
        
        # Features TF-IDF del texto
        X_tfidf = self.vectorizer.fit_transform(texts)
        
        # Features lingüísticas adicionales
        linguistic_features = np.array([list(self.extract_linguistic_features(t).values()) 
                                        for t in texts])
        
        # Combinar features
        X = hstack([X_tfidf, linguistic_features])
        
        # Entrenar clasificador
        self.classifier = RandomForestClassifier(
            n_estimators=80,
            max_depth=12,
            random_state=42,
            n_jobs=-1
        )
        
        self.classifier.fit(X, labels)
        self.is_trained = True
        return self
    
    def predict_risk(self, text):
        """
        Predice nivel de riesgo de suicidio
        Retorna dict con nivel, confianza y features detectadas
        """
        if not self.is_trained or self.classifier is None:
            # Usar reglas si no hay modelo entrenado
            return self._rule_based_risk(text)
        
        from scipy.sparse import hstack
        
        # Features TF-IDF
        X_tfidf = self.vectorizer.transform([text])
        
        # Features lingüísticas
        linguistic_features = np.array([list(self.extract_linguistic_features(text).values())])
        
        # Combinar
        X = hstack([X_tfidf, linguistic_features])
        
        # Predecir
        proba = self.classifier.predict_proba(X)[0]
        risk_class = np.argmax(proba)
        confidence = np.max(proba)
        
        risk_labels = {0: 'bajo', 1: 'moderado', 2: 'alto'}
        risk_level = risk_labels.get(risk_class, 'bajo')
        
        # Determinar si requiere acción inmediata
        requires_action = risk_level == 'alto' and confidence > 0.7
        
        return {
            'risk_level': risk_level,
            'confidence': confidence,
            'requires_immediate_action': requires_action,
            'features': self.extract_linguistic_features(text),
            'risk_class': risk_class
        }
    
    def get_crisis_response(self, text):
        """
        Obtiene la respuesta apropiada según el nivel de riesgo
        """
        result = self.predict_risk(text)
        
        if result['risk_level'] == 'alto':
            return {
                'type': 'crisis',
                'message': '⚠️ Noto que estás pasando por un momento muy difícil. '
                          'Es importante que hables con un profesional. '
                          'Por favor, contacta a la Línea de la Vida: 800 911 2000. '
                          'No estás solo/a, hay personas que quieren ayudarte.',
                'show_crisis_button': True,
                'lines_of_help': [
                    {'name': 'Línea de la Vida', 'number': '800 911 2000'},
                    {'name': 'SAPTEL', 'number': '55 5259 8121'}
                ]
            }
        elif result['risk_level'] == 'moderado':
            return {
                'type': 'warning',
                'message': 'Veo que estás pasando por momentos difíciles. '
                          'Quiero que sepas que no estás solo/a. '
                          '¿Te gustaría que te comparta algunos ejercicios que pueden ayudar? '
                          'Recuerda que también puedes hablar con un profesional si lo necesitas.',
                'show_crisis_button': True,
                'suggest_resources': True
            }
        else:
            return {
                'type': 'support',
                'message': 'Gracias por compartir cómo te sientes. '
                          'Estoy aquí para apoyarte. '
                          '¿Te gustaría hacer un ejercicio de respiración o prefieres seguir conversando?',
                'show_crisis_button': False
            }
    
    def analyze_and_respond(self, text):
        """
        Analiza el texto y genera una respuesta completa
        """
        risk_result = self.predict_risk(text)
        crisis_response = self.get_crisis_response(text)
        
        return {
            'risk_analysis': risk_result,
            'response': crisis_response,
            'timestamp': pd.Timestamp.now().isoformat() if 'pd' in dir() else None
        }


# ========== FUNCIÓN PARA CREAR DATASET DE ENTRENAMIENTO ==========
def create_synthetic_crisis_dataset(n_samples=500):
    """
    Crea un dataset sintético para entrenar el clasificador de riesgo
    """
    import pandas as pd
    import random
    
    # Frases de ejemplo por nivel de riesgo
    phrases_by_risk = {
        0: [  # Sin riesgo
            "Hoy me siento bien, gracias por preguntar",
            "Todo va bien en mi vida",
            "Estoy contento con mis logros",
            "Me siento motivado para seguir adelante",
            "Las cosas están mejorando",
            "Disfruto pasar tiempo con mi familia"
        ],
        1: [  # Riesgo bajo
            "Me siento un poco triste hoy",
            "Estoy cansado pero bien",
            "A veces me siento solo",
            "Me preocupa un poco el futuro",
            "No sé qué hacer con mi vida"
        ],
        2: [  # Riesgo moderado
            "Me siento muy triste y desanimado",
            "No encuentro sentido a las cosas",
            "Me siento solo aunque esté con gente",
            "No sé si voy a mejorar algún día",
            "Todo me sale mal, no sé qué hacer"
        ],
        3: [  # Riesgo alto
            "Ya no quiero vivir, estoy pensando en suicidio",
            "Me voy a matar, no puedo más",
            "He estado planeando cómo quitarme la vida",
            "No aguanto más, quiero morir",
            "Estoy desesperado, voy a acabar con todo",
            "Me voy a suicidar, nadie me entiende"
        ]
    }
    
    data = []
    for risk_level, phrases in phrases_by_risk.items():
        n = int(n_samples * (0.1 if risk_level == 3 else 0.2))
        for _ in range(n):
            phrase = random.choice(phrases)
            # Variar ligeramente las frases
            if random.random() > 0.5:
                phrase = phrase + " " + random.choice([
                    "no sé qué hacer", "ayuda por favor", "estoy desesperado"
                ])
            data.append({'text': phrase, 'risk_level': risk_level})
    
    df = pd.DataFrame(data)
    return df


# ========== EJEMPLO DE USO ==========
if __name__ == "__main__":
    import pandas as pd
    
    print("="*60)
    print("🧪 PROBANDO CLASIFICADOR DE RIESGO SUICIDA")
    print("="*60)
    
    # Crear clasificador
    classifier = SuicideRiskClassifier()
    
    # Probar con ejemplos
    test_texts = [
        "Hoy me siento bien, todo está excelente",
        "Me siento un poco triste, pero todo bien",
        "No sé qué hacer, estoy desesperado, siento que no hay salida",
        "He estado pensando en suicidio, no quiero seguir viviendo",
        "Me voy a matar, ya no aguanto más"
    ]
    
    print("\n📝 Pruebas con clasificador basado en reglas:\n")
    for text in test_texts:
        result = classifier.predict_risk(text)
        print(f"📌 Texto: {text}")
        print(f"   Riesgo: {result['risk_level'].upper()} (confianza: {result['confidence']:.2f})")
        print(f"   Acción inmediata: {'SÍ' if result['requires_immediate_action'] else 'NO'}")
        print(f"   Palabras de alto riesgo detectadas: {result['features']['crisis_high']}")
        print("-" * 50)
    
    print("\n" + "="*60)
    print("📊 Creando dataset sintético para entrenamiento...")
    
    # Crear dataset sintético
    df = create_synthetic_crisis_dataset(500)
    print(f"   Dataset creado: {len(df)} muestras")
    print(f"   Distribución:")
    print(df['risk_level'].value_counts())
    
    print("\n   Guardando dataset...")
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_crisis_data.csv', index=False)
    
    print("\n   Entrenando modelo...")
    classifier.train(df['text'].tolist(), df['risk_level'].tolist())
    
    print("\n   Guardando modelo...")
    os.makedirs('models', exist_ok=True)
    joblib.dump(classifier, 'models/suicide_risk_classifier.pkl')
    
    print("\n✅ Clasificador entrenado y guardado correctamente")
    print("   Archivo: models/suicide_risk_classifier.pkl")
    
    print("\n🧪 Probando con el modelo entrenado:")
    for text in test_texts:
        result = classifier.predict_risk(text)
        print(f"\n📌 '{text[:50]}...'")
        print(f"   → Riesgo: {result['risk_level'].upper()} ({result['confidence']:.1%})")
        print(f"   → Respuesta: {classifier.get_crisis_response(text)['message'][:100]}...")