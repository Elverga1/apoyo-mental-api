// src/pages/AssessmentsPage.jsx (actualizado)
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, ClipboardList, Activity } from 'lucide-react';
import PHQ9 from '../components/PHQ9';
import GAD7 from '../components/GAD7';

export const AssessmentsPage = () => {
  const [selectedTest, setSelectedTest] = useState(null);
  const [completed, setCompleted] = useState(false);

  const tests = [
    {
      id: 'phq9',
      name: 'PHQ-9',
      description: 'Cuestionario de salud del paciente para depresión',
      icon: ClipboardList,
      color: 'blue'
    },
    {
      id: 'gad7',
      name: 'GAD-7',
      description: 'Evaluación de trastorno de ansiedad generalizada',
      icon: Activity,
      color: 'green',
      disabled: false
    }
  ];

  const handleComplete = () => {
    setCompleted(true);
    setTimeout(() => {
      setSelectedTest(null);
      setCompleted(false);
    }, 2000);
  };

  if (selectedTest === 'phq9') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="bg-blue-600 dark:bg-blue-800 text-white p-4">
          <div className="flex items-center gap-4 max-w-2xl mx-auto">
            <button onClick={() => setSelectedTest(null)} className="p-1 hover:bg-white/20 rounded-full">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="font-semibold">Cuestionario PHQ-9</h1>
          </div>
        </div>
        <PHQ9 onComplete={handleComplete} />
      </div>
    );
  }

  if (selectedTest === 'gad7') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="bg-green-600 dark:bg-green-800 text-white p-4">
          <div className="flex items-center gap-4 max-w-2xl mx-auto">
            <button onClick={() => setSelectedTest(null)} className="p-1 hover:bg-white/20 rounded-full">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="font-semibold">Cuestionario GAD-7</h1>
          </div>
        </div>
        <GAD7 onComplete={handleComplete} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="bg-blue-600 dark:bg-blue-800 text-white p-4">
        <div className="flex items-center gap-4">
          <Link to="/" className="p-1 hover:bg-white/20 rounded-full">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="font-semibold">Evaluaciones</h1>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {completed && (
          <div className="bg-green-100 dark:bg-green-900 border border-green-400 dark:border-green-700 text-green-700 dark:text-green-300 px-4 py-3 rounded mb-4">
            ✅ Evaluación guardada correctamente
          </div>
        )}
        
        <div className="grid md:grid-cols-2 gap-6">
          {tests.map(test => {
            const Icon = test.icon;
            return (
              <button
                key={test.id}
                onClick={() => !test.disabled && setSelectedTest(test.id)}
                className={`bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 text-left transition-all ${
                  test.disabled 
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'hover:shadow-lg hover:scale-[1.02]'
                }`}
                disabled={test.disabled}
              >
                <Icon className={`w-12 h-12 text-${test.color}-600 dark:text-${test.color}-400 mb-4`} />
                <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">{test.name}</h3>
                <p className="text-gray-600 dark:text-gray-400">{test.description}</p>
              </button>
            );
          })}
        </div>
        
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/30 rounded-lg p-4">
          <p className="text-sm text-blue-800 dark:text-blue-300">
            ℹ️ Estas evaluaciones son herramientas de detección basadas en evidencia científica.
            No reemplazan un diagnóstico profesional. Consulta a un especialista si tienes preocupaciones.
          </p>
        </div>
      </div>
    </div>
  );
};