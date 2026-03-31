# backend/classifiers/simple_risk_classifier.py
class SimpleRiskClassifier:
    CRISIS_KEYWORDS = {
        'alto': [
            'suicidio', 'suicidarme', 'matarme', 'matar', 'morir', 'muerte',
            'acabar con todo', 'no quiero vivir', 'quitarme la vida',
            'me voy a matar', 'me quiero morir', 'no puedo más'
        ],
        'medio': [
            'desesperado', 'desesperación', 'sin salida', 'no le veo sentido',
            'carga para otros', 'mejor no existir', 'desaparecer'
        ],
        'bajo': [
            'triste', 'tristeza', 'cansado', 'agotado', 'sin energía',
            'sin ganas', 'desánimo', 'abatido', 'deprimido'
        ]
    }
    
    def predict_risk(self, text):
        text_lower = text.lower()
        words = text_lower.split()
        
        crisis_high = sum(1 for w in words if w in self.CRISIS_KEYWORDS['alto'])
        crisis_medium = sum(1 for w in words if w in self.CRISIS_KEYWORDS['medio'])
        crisis_low = sum(1 for w in words if w in self.CRISIS_KEYWORDS['bajo'])
        
        if crisis_high >= 1:
            risk_level = 'alto'
            confidence = 0.85
            requires_action = True
        elif crisis_medium >= 2:
            risk_level = 'alto'
            confidence = 0.75
            requires_action = True
        elif crisis_medium >= 1:
            risk_level = 'moderado'
            confidence = 0.70
            requires_action = False
        elif crisis_low >= 2:
            risk_level = 'moderado'
            confidence = 0.65
            requires_action = False
        else:
            risk_level = 'bajo'
            confidence = 0.60
            requires_action = False
        
        features = {
            'word_count': len(words),
            'crisis_high': crisis_high,
            'crisis_medium': crisis_medium,
            'crisis_low': crisis_low,
            'first_person': sum(1 for w in words if w in ['yo', 'me', 'mi']),
            'negations': sum(1 for w in words if w in ['no', 'nunca', 'nada']),
            'hopelessness': sum(1 for w in words if w in ['nunca', 'siempre']),
            'crisis_ratio': (crisis_high + crisis_medium) / len(words) if words else 0,
            'has_high_risk_word': 1 if crisis_high > 0 else 0
        }
        
        return {
            'risk_level': risk_level,
            'confidence': confidence,
            'requires_immediate_action': requires_action,
            'features': features
        }
    
    def get_crisis_response(self, text):
        result = self.predict_risk(text)
        
        if result['risk_level'] == 'alto':
            return {
                'type': 'crisis',
                'message': '⚠️ Noto que estás pasando por un momento muy difícil. Es importante que hables con un profesional. Por favor, contacta a la Línea de la Vida: 800 911 2000. No estás solo/a.',
                'show_crisis_button': True,
                'lines_of_help': [
                    {'name': 'Línea de la Vida', 'number': '800 911 2000'},
                    {'name': 'SAPTEL', 'number': '55 5259 8121'}
                ]
            }
        elif result['risk_level'] == 'moderado':
            return {
                'type': 'warning',
                'message': 'Veo que estás pasando por momentos difíciles. Quiero que sepas que no estás solo/a. ¿Te gustaría que te comparta algunos ejercicios que pueden ayudar?',
                'show_crisis_button': True,
                'suggest_resources': True
            }
        else:
            return {
                'type': 'support',
                'message': 'Gracias por compartir cómo te sientes. Estoy aquí para apoyarte.',
                'show_crisis_button': False
            }