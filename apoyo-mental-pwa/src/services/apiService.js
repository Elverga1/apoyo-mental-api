// src/services/apiService.js
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async analyzeRisk(text) {
    try {
      const response = await fetch(`${this.baseUrl}/api/analyze-risk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Error en el análisis');
      }

      return await response.json();
    } catch (error) {
      console.error('Error al conectar con la API:', error);
      return this.localAnalysis(text);
    }
  }

  async getLinesOfHelp() {
    return [
      { name: 'Línea de la Vida', number: '800 911 2000', description: 'Atención las 24 horas' },
      { name: 'SAPTEL', number: '55 5259 8121', description: 'Apoyo psicológico por teléfono' },
      { name: 'Línea de Prevención del Suicidio', number: '800 822 3737', description: 'Atención especializada en crisis' }
    ];
  }

  localAnalysis(text) {
    const lowerText = text.toLowerCase();
    const crisisKeywords = ['suicidio', 'matarme', 'morir', 'no quiero vivir', 'quitarme la vida'];
    const hasCrisis = crisisKeywords.some(kw => lowerText.includes(kw));
    
    return {
      risk_analysis: {
        risk_level: hasCrisis ? 'alto' : 'bajo',
        confidence: hasCrisis ? 0.85 : 0.6,
        requires_immediate_action: hasCrisis,
        features: {
          word_count: text.split(/\s+/).length,
          crisis_high: hasCrisis ? 1 : 0,
        }
      },
      response: {
        type: hasCrisis ? 'crisis' : 'support',
        message: hasCrisis 
          ? '⚠️ Noto que estás pasando por un momento difícil. Por favor, contacta a la Línea de la Vida: 800 911 2000'
          : 'Gracias por compartir cómo te sientes. Estoy aquí para apoyarte.',
        show_crisis_button: hasCrisis,
        lines_of_help: hasCrisis ? [{ name: 'Línea de la Vida', number: '800 911 2000' }] : []
      },
      timestamp: new Date().toISOString()
    };
  }
}

export const apiService = new ApiService();
