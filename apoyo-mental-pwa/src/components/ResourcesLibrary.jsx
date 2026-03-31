// src/components/ResourcesLibrary.jsx
import React, { useState } from 'react';
import { Wind, Brain, BookOpen, Smile, Activity, Moon, Heart, ChevronRight } from 'lucide-react';

const resources = {
  breathing: [
    {
      title: "Respiración 4-7-8",
      description: "Técnica para calmar la ansiedad",
      steps: [
        "Inhala por la nariz durante 4 segundos",
        "Mantén la respiración durante 7 segundos",
        "Exhala lentamente por la boca durante 8 segundos",
        "Repite 4-5 veces"
      ],
      icon: Wind
    },
    {
      title: "Respiración abdominal",
      description: "Para reducir el estrés",
      steps: [
        "Siéntate cómodamente con la espalda recta",
        "Coloca una mano en el pecho y otra en el abdomen",
        "Inhala profundamente sintiendo cómo se eleva el abdomen",
        "Exhala lentamente sintiendo cómo desciende",
        "Repite durante 3-5 minutos"
      ],
      icon: Wind
    }
  ],
  mindfulness: [
    {
      title: "Escaneo corporal",
      description: "Conectar con las sensaciones físicas",
      steps: [
        "Acuéstate cómodamente",
        "Dirige tu atención a los pies, nota cualquier sensación",
        "Sube lentamente por piernas, abdomen, pecho, brazos",
        "Llega a la cabeza y la cara",
        "Observa sin juzgar, solo nota lo que sientes"
      ],
      icon: Brain
    },
    {
      title: "Atención plena de 5 minutos",
      description: "Anclarte en el presente",
      steps: [
        "Siéntate en un lugar tranquilo",
        "Enfócate en tu respiración",
        "Cuando tu mente divague, tráela de vuelta suavemente",
        "Observa los sonidos a tu alrededor sin etiquetarlos"
      ],
      icon: Brain
    }
  ],
  cognitive: [
    {
      title: "Reestructuración cognitiva",
      description: "Cambiar pensamientos negativos",
      steps: [
        "Identifica el pensamiento automático negativo",
        "¿Qué evidencia apoya este pensamiento?",
        "¿Qué evidencia lo contradice?",
        "¿Hay una forma alternativa de verlo?",
        "Crea un pensamiento más equilibrado"
      ],
      icon: BookOpen
    },
    {
      title: "Registro de pensamientos",
      description: "Identificar patrones de pensamiento",
      steps: [
        "Anota la situación que causó malestar",
        "Escribe el pensamiento automático",
        "Identifica la emoción y su intensidad",
        "Encuentra evidencia en contra",
        "Reformula con un pensamiento alternativo"
      ],
      icon: BookOpen
    }
  ],
  wellbeing: [
    {
      title: "Actividades placenteras",
      description: "Aumentar el bienestar diario",
      steps: [
        "Haz una lista de actividades que disfrutas",
        "Programa al menos una actividad placentera por día",
        "Registra cómo te sentiste después",
        "Celebra tus pequeños logros"
      ],
      icon: Smile
    },
    {
      title: "Ejercicio físico",
      description: "Beneficios para la salud mental",
      steps: [
        "Camina 15-20 minutos al día",
        "Busca una actividad que disfrutes",
        "Empieza con metas pequeñas",
        "Acompaña con música motivadora"
      ],
      icon: Activity
    }
  ],
  sleep: [
    {
      title: "Higiene del sueño",
      description: "Mejorar la calidad del descanso",
      steps: [
        "Mantén horarios regulares para dormir",
        "Evita pantallas 1 hora antes de acostarte",
        "Crea un ambiente oscuro y tranquilo",
        "Evita cafeína después de las 4pm",
        "Establece una rutina relajante pre-sueño"
      ],
      icon: Moon
    }
  ]
};

const categories = [
  { id: 'breathing', name: 'Respiración', icon: Wind, color: 'blue' },
  { id: 'mindfulness', name: 'Mindfulness', icon: Brain, color: 'green' },
  { id: 'cognitive', name: 'Terapia Cognitiva', icon: BookOpen, color: 'purple' },
  { id: 'wellbeing', name: 'Bienestar', icon: Smile, color: 'orange' },
  { id: 'sleep', name: 'Sueño', icon: Moon, color: 'indigo' }
];

const ResourceCard = ({ resource, category }) => {
  const [expanded, setExpanded] = useState(false);
  const Icon = resource.icon;

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <div className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg bg-${category.color}-100`}>
              <Icon className={`w-5 h-5 text-${category.color}-600`} />
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">{resource.title}</h3>
              <p className="text-sm text-gray-500">{resource.description}</p>
            </div>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-gray-400 hover:text-gray-600"
          >
            <ChevronRight className={`w-5 h-5 transition-transform ${expanded ? 'rotate-90' : ''}`} />
          </button>
        </div>
        
        {expanded && (
          <div className="mt-4 pt-4 border-t">
            <ol className="space-y-2">
              {resource.steps.map((step, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex gap-2">
                  <span className="font-bold text-gray-400">{idx + 1}.</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
            <button
              onClick={() => {
                const saved = JSON.parse(localStorage.getItem('favorite_resources') || '[]');
                if (!saved.includes(resource.title)) {
                  saved.push(resource.title);
                  localStorage.setItem('favorite_resources', JSON.stringify(saved));
                  alert('✅ Recurso guardado en favoritos');
                }
              }}
              className="mt-4 text-sm text-blue-600 hover:text-blue-700"
            >
              Guardar en favoritos
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const ResourcesLibrary = () => {
  const [selectedCategory, setSelectedCategory] = useState('breathing');

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Recursos de Apoyo</h1>
        <p className="text-gray-600">
          Ejercicios basados en Terapia Cognitivo-Conductual y mindfulness
        </p>
      </div>

      {/* Categories */}
      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map(cat => {
          const Icon = cat.icon;
          return (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full transition-colors ${
                selectedCategory === cat.id
                  ? `bg-${cat.color}-600 text-white`
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm">{cat.name}</span>
            </button>
          );
        })}
      </div>

      {/* Resources */}
      <div className="space-y-4">
        {resources[selectedCategory]?.map((resource, idx) => (
          <ResourceCard
            key={idx}
            resource={resource}
            category={categories.find(c => c.id === selectedCategory)}
          />
        ))}
      </div>

      <div className="mt-8 bg-blue-50 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          💡 Consejo: Practica estos ejercicios regularmente. La constancia ayuda a desarrollar habilidades de regulación emocional.
        </p>
      </div>
    </div>
  );
};

export default ResourcesLibrary;