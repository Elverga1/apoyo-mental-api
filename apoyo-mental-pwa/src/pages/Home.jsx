// src/pages/Home.jsx
import { BarChart3, BookOpen, ClipboardList, Heart, MessageCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import authService from '../services/authService';

export const Home = () => {
  const { isDark, toggleDark } = useTheme();

  const features = [
    {
      icon: MessageCircle,
      title: 'Chat de Apoyo',
      description: 'Habla con nuestra IA que te escuchará y apoyará',
      path: '/chat',
      color: 'blue'
    },
    {
      icon: ClipboardList,
      title: 'Evaluaciones',
      description: 'Cuestionarios PHQ-9 y GAD-7 basados en evidencia',
      path: '/assessments',
      color: 'green'
    },
    {
      icon: BookOpen,
      title: 'Recursos',
      description: 'Ejercicios y técnicas basadas en TCC',
      path: '/resources',
      color: 'teal'
    },
    {
      icon: BarChart3,
      title: 'Reportes',
      description: 'Visualiza tu progreso y comparte con tu terapeuta',
      path: '/reports',
      color: 'purple'
    }
  ];

  return (
    <div className={`min-h-screen ${isDark ? 'dark' : ''}`}>
      <div className={`min-h-screen ${isDark ? 'bg-gray-900' : 'bg-gradient-to-br from-blue-50 to-gray-100'}`}>
        {/* Botón de modo oscuro */}
        <div className="absolute top-4 right-4">
          <button
            onClick={toggleDark}
            className={`p-2 rounded-full transition-colors ${
              isDark 
                ? 'bg-gray-700 text-yellow-400 hover:bg-gray-600' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {isDark ? '☀️' : '🌙'}
          </button>
          <button
            onClick={() => {
              authService.logout();
              window.location.href = '/login';
            }}
            className="p-2 rounded-full bg-red-500/20 text-red-600 hover:bg-red-500/30 transition-colors ml-2"
          >
            Cerrar sesión
          </button>
        </div>

        {/* Hero Section */}
        <div className={`${isDark ? 'bg-blue-900' : 'bg-gradient-to-r from-blue-600 to-blue-700'} text-white py-16`}>
          <div className="container mx-auto px-4 text-center">
            <Heart className="w-20 h-20 mx-auto mb-6 text-white" />
            <h1 className="text-5xl font-bold mb-4">Apoyo Mental</h1>
            <p className="text-xl mb-8 max-w-2xl mx-auto">
              Herramienta de apoyo psicológico basada en evidencia científica
            </p>
            <Link
              to="/chat"
              className="inline-flex items-center gap-2 bg-white text-blue-600 px-8 py-4 rounded-full text-lg font-semibold hover:bg-gray-100 transition-colors shadow-lg"
            >
              <MessageCircle className="w-5 h-5" />
              Comenzar a hablar
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="container mx-auto px-4 py-12">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              const colorClasses = {
                blue: 'text-blue-600 dark:text-blue-400',
                green: 'text-green-600 dark:text-green-400',
                teal: 'text-teal-600 dark:text-teal-400',
                purple: 'text-purple-600 dark:text-purple-400'
              };
              const bgClasses = {
                blue: 'bg-blue-100 dark:bg-blue-900/30',
                green: 'bg-green-100 dark:bg-green-900/30',
                teal: 'bg-teal-100 dark:bg-teal-900/30',
                purple: 'bg-purple-100 dark:bg-purple-900/30'
              };
              
              return (
                <Link
                  key={idx}
                  to={feature.path}
                  className={`${isDark ? 'bg-gray-800 hover:bg-gray-700' : 'bg-white hover:shadow-lg'} rounded-xl shadow-md p-6 transition-all hover:scale-[1.02]`}
                >
                  <div className={`${bgClasses[feature.color]} p-3 rounded-lg inline-block mb-4`}>
                    <Icon className={`w-6 h-6 ${colorClasses[feature.color]}`} />
                  </div>
                  <h3 className={`text-xl font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-800'}`}>
                    {feature.title}
                  </h3>
                  <p className={`${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    {feature.description}
                  </p>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Disclaimer */}
        <div className="container mx-auto px-4 pb-12">
          <div className={`${isDark ? 'bg-yellow-900/30 border-yellow-800 text-yellow-200' : 'bg-yellow-100 border-yellow-300 text-yellow-800'} border rounded-lg p-4 text-sm`}>
            <p className="font-semibold mb-1">⚠️ Aviso importante</p>
            <p>
              Esta herramienta es un complemento, no un sustituto de la atención profesional.
              Si estás en crisis o tienes pensamientos de autolesión, contacta inmediatamente:
            </p>
            <p className="font-medium mt-2">
              Línea de la Vida: 800 911 2000
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};