// src/components/PHQ9.jsx
import React, { useState } from 'react';
import { ArrowLeft, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

const PHQ9_QUESTIONS = [
  "Poco interés o placer en hacer cosas",
  "Te sientes decaído(a), deprimido(a) o sin esperanzas",
  "Dificultad para dormir o dormir demasiado",
  "Te sientes cansado(a) o con poca energía",
  "Poco apetito o comer en exceso",
  "Te sientes mal contigo mismo(a)",
  "Dificultad para concentrarte",
  "Te mueves o hablas tan lento que otros lo notan",
  "Pensamientos de que estarías mejor muerto(a) o de lastimarte"
];

const SEVERITY_LEVELS = {
  minima: { text: "Depresión mínima", color: "text-green-600", bg: "bg-green-100" },
  leve: { text: "Depresión leve", color: "text-yellow-600", bg: "bg-yellow-100" },
  moderada: { text: "Depresión moderada", color: "text-orange-600", bg: "bg-orange-100" },
  moderada_grave: { text: "Depresión moderadamente grave", color: "text-red-600", bg: "bg-red-100" },
  grave: { text: "Depresión grave", color: "text-red-800", bg: "bg-red-200" }
};

const getSeverity = (score) => {
  if (score <= 4) return "minima";
  if (score <= 9) return "leve";
  if (score <= 14) return "moderada";
  if ( score <= 19) return "moderada_grave";
  return "grave";
};

const PHQ9 = ({ onComplete, onBack }) => {
  const [answers, setAnswers] = useState(Array(9).fill(null));
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
    
    // Guardar en localStorage
    const savedResults = JSON.parse(localStorage.getItem('phq9_results') || '[]');
    savedResults.push(result);
    localStorage.setItem('phq9_results', JSON.stringify(savedResults));
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
        <button onClick={() => setShowResults(false)} className="flex items-center gap-2 text-blue-600 mb-6">
          <ArrowLeft className="w-4 h-4" /> Volver al cuestionario
        </button>
        
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Resultados PHQ-9</h2>
          
          <div className={`${severityInfo.bg} rounded-lg p-4 mb-6`}>
            <p className={`text-3xl font-bold ${severityInfo.color} mb-2`}>
              {totalScore} puntos
            </p>
            <p className={`font-semibold ${severityInfo.color}`}>
              {severityInfo.text}
            </p>
          </div>
          
          <div className="space-y-3 mb-6">
            {PHQ9_QUESTIONS.map((question, idx) => (
              <div key={idx} className="flex justify-between items-center border-b pb-2">
                <span className="text-sm text-gray-600 flex-1">{question}</span>
                <span className="font-semibold text-gray-800">
                  {answers[idx] === 0 ? "Ningún día" :
                   answers[idx] === 1 ? "Varios días" :
                   answers[idx] === 2 ? "Más de la mitad" : "Casi todos los días"}
                </span>
              </div>
            ))}
          </div>
          
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              ℹ️ Esta es una herramienta de detección, no un diagnóstico clínico.
              Si estás preocupado por tu salud mental, consulta a un profesional.
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
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Cuestionario PHQ-9</h1>
        <p className="text-gray-600">Evaluación de depresión</p>
      </div>
      
      <div className="space-y-4 mb-6">
        {PHQ9_QUESTIONS.map((question, idx) => (
          <div key={idx} className="bg-white rounded-lg p-4 shadow">
            <p className="font-medium text-gray-800 mb-3">{idx + 1}. {question}</p>
            <div className="grid grid-cols-4 gap-2">
              {["Ningún día", "Varios días", "Más de la mitad", "Casi todos los días"].map((label, value) => (
                <button
                  key={value}
                  onClick={() => handleAnswer(idx, value)}
                  className={`py-2 px-3 rounded-lg text-sm transition-colors ${
                    answers[idx] === value
                      ? 'bg-blue-600 text-white'
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
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
      >
        Ver resultados
      </button>
    </div>
  );
};

export default PHQ9;