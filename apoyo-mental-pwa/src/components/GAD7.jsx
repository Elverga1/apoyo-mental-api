// src/components/GAD7.jsx
import React, { useState } from 'react';
import { ArrowLeft, CheckCircle } from 'lucide-react';

const GAD7_QUESTIONS = [
  "Sentirse nervioso/a, ansioso/a o con los nervios de punta",
  "No ser capaz de parar o controlar las preocupaciones",
  "Preocuparse demasiado por diferentes cosas",
  "Dificultad para relajarse",
  "Inquietud que no le deja quedarse quieto/a",
  "Irritabilidad o mal humor fácil",
  "Miedo de que algo terrible vaya a ocurrir"
];

const SEVERITY_LEVELS = {
  minima: { text: "Ansiedad mínima", color: "text-green-600", bg: "bg-green-100", recommendation: "Técnicas de relajación y autocuidado" },
  leve: { text: "Ansiedad leve", color: "text-yellow-600", bg: "bg-yellow-100", recommendation: "Ejercicios de respiración y mindfulness" },
  moderada: { text: "Ansiedad moderada", color: "text-orange-600", bg: "bg-orange-100", recommendation: "Terapia cognitivo-conductual recomendada" },
  grave: { text: "Ansiedad grave", color: "text-red-600", bg: "bg-red-100", recommendation: "Consulta con un profesional de salud mental" }
};

const getSeverity = (score) => {
  if (score <= 4) return "minima";
  if (score <= 9) return "leve";
  if (score <= 14) return "moderada";
  return "grave";
};

const GAD7 = ({ onComplete, onBack }) => {
  const [answers, setAnswers] = useState(Array(7).fill(null));
  const [showResults, setShowResults] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleAnswer = (questionIndex, value) => {
    const newAnswers = [...answers];
    newAnswers[questionIndex] = parseInt(value);
    setAnswers(newAnswers);
  };

  const calculateScore = () => {
    return answers.reduce((sum, val) => sum + (val || 0), 0);
  };

  const handleSubmit = () => {
    if (answers.some(a => a === null)) {
      alert("Por favor responde todas las preguntas");
      return;
    }
    setShowResults(true);
  };

  const handleSave = () => {
    const score = calculateScore();
    const severity = getSeverity(score);
    const result = {
      date: new Date().toISOString(),
      score: score,
      severity: severity,
      answers: answers
    };
    
    const savedResults = JSON.parse(localStorage.getItem('gad7_results') || '[]');
    savedResults.push(result);
    localStorage.setItem('gad7_results', JSON.stringify(savedResults));
    setSaved(true);
    
    if (onComplete) onComplete(result);
  };

  const allAnswered = answers.every(a => a !== null);
  const totalScore = calculateScore();
  const severity = getSeverity(totalScore);
  const severityInfo = SEVERITY_LEVELS[severity];

  if (showResults) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <button onClick={() => setShowResults(false)} className="flex items-center gap-2 text-green-600 mb-6">
          <ArrowLeft className="w-4 h-4" /> Volver al cuestionario
        </button>
        
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Resultados GAD-7</h2>
          
          <div className={`${severityInfo.bg} rounded-lg p-4 mb-6`}>
            <p className={`text-3xl font-bold ${severityInfo.color} mb-2`}>
              {totalScore} puntos
            </p>
            <p className={`font-semibold ${severityInfo.color} mb-2`}>
              {severityInfo.text}
            </p>
            <p className="text-sm text-gray-700 mt-2">
              Recomendación: {severityInfo.recommendation}
            </p>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-green-800">
              ℹ️ Esta es una herramienta de detección, no un diagnóstico clínico.
              Si experimentas síntomas persistentes, consulta a un profesional.
            </p>
          </div>
          
          {!saved ? (
            <button
              onClick={handleSave}
              className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
            >
              Guardar resultado
            </button>
          ) : (
            <div className="text-center text-green-600">
              <CheckCircle className="w-8 h-8 mx-auto mb-2" />
              <p>Resultado guardado correctamente</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Cuestionario GAD-7</h1>
        <p className="text-gray-600">Evaluación de ansiedad generalizada</p>
      </div>
      
      <div className="space-y-4 mb-6">
        {GAD7_QUESTIONS.map((question, idx) => (
          <div key={idx} className="bg-white rounded-lg p-4 shadow">
            <p className="font-medium text-gray-800 mb-3">{idx + 1}. {question}</p>
            <div className="grid grid-cols-4 gap-2">
              {["Ningún día", "Varios días", "Más de la mitad", "Casi todos los días"].map((label, value) => (
                <button
                  key={value}
                  onClick={() => handleAnswer(idx, value)}
                  className={`py-2 px-3 rounded-lg text-sm transition-colors ${
                    answers[idx] === value
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      <button
        onClick={handleSubmit}
        disabled={!allAnswered}
        className={`w-full py-3 rounded-lg font-semibold transition-colors ${
          allAnswered
            ? 'bg-green-600 text-white hover:bg-green-700'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
      >
        Ver resultados
      </button>
    </div>
  );
};

export default GAD7;