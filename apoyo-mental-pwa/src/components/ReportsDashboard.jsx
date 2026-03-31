// src/components/ReportsDashboard.jsx
import React, { useState, useEffect } from 'react';
import { Download, TrendingUp, Calendar, Activity, Heart } from 'lucide-react';

const ReportsDashboard = () => {
  const [phq9Results, setPhq9Results] = useState([]);
  const [gad7Results, setGad7Results] = useState([]);
  const [moodData, setMoodData] = useState([]);
  const [activeTab, setActiveTab] = useState('phq9');

  useEffect(() => {
    const loadData = () => {
      const phq9 = JSON.parse(localStorage.getItem('phq9_results') || '[]');
      const gad7 = JSON.parse(localStorage.getItem('gad7_results') || '[]');
      const mood = JSON.parse(localStorage.getItem('mood_entries') || '[]');
      setPhq9Results(phq9.sort((a, b) => new Date(a.date) - new Date(b.date)));
      setGad7Results(gad7.sort((a, b) => new Date(a.date) - new Date(b.date)));
      setMoodData(mood);
    };
    loadData();
  }, []);

  const getSeverityColor = (severity) => {
    const colors = {
      minima: 'text-green-600',
      leve: 'text-yellow-600',
      moderada: 'text-orange-600',
      moderada_grave: 'text-red-600',
      grave: 'text-red-800'
    };
    return colors[severity] || 'text-gray-600';
  };

  const getLatestTrend = (results) => {
    if (results.length < 2) return { direction: 'stable', change: 0 };
    const last = results[results.length - 1].score;
    const previous = results[results.length - 2].score;
    const change = previous - last;
    if (change > 2) return { direction: 'improving', change };
    if (change < -2) return { direction: 'worsening', change: Math.abs(change) };
    return { direction: 'stable', change: 0 };
  };

  const exportToPDF = () => {
    const reportData = {
      generatedAt: new Date().toISOString(),
      phq9: phq9Results,
      gad7: gad7Results,
      mood: moodData,
      summary: {
        totalPHQ9: phq9Results.length,
        totalGAD7: gad7Results.length,
        latestPHQ9: phq9Results[phq9Results.length - 1]?.score || null,
        latestGAD7: gad7Results[gad7Results.length - 1]?.score || null
      }
    };
    
    const dataStr = JSON.stringify(reportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `reporte_mental_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const renderPHQ9Chart = () => {
    if (phq9Results.length === 0) {
      return (
        <div className="text-center py-12 text-gray-500">
          <Calendar className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>Aún no hay evaluaciones PHQ-9</p>
          <p className="text-sm">Completa el cuestionario en la sección de Evaluaciones</p>
        </div>
      );
    }

    const maxScore = Math.max(...phq9Results.map(r => r.score), 27);
    const trend = getLatestTrend(phq9Results);

    return (
      <div>
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h3 className="font-semibold text-gray-800">Evolución de puntajes PHQ-9</h3>
            <p className="text-sm text-gray-500">Depresión (0-27 puntos)</p>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm ${
            trend.direction === 'improving' ? 'bg-green-100 text-green-700' :
            trend.direction === 'worsening' ? 'bg-red-100 text-red-700' :
            'bg-gray-100 text-gray-600'
          }`}>
            {trend.direction === 'improving' && '📉 Mejorando'}
            {trend.direction === 'worsening' && '📈 Empeorando'}
            {trend.direction === 'stable' && '➡️ Estable'}
          </div>
        </div>
        
        <div className="space-y-3">
          {phq9Results.map((result, idx) => {
            const severityColor = getSeverityColor(result.severity);
            const date = new Date(result.date).toLocaleDateString('es-MX');
            return (
              <div key={idx} className="bg-gray-50 rounded-lg p-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-500">{date}</span>
                  <span className={`font-bold ${severityColor}`}>{result.score} pts</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      result.severity === 'minima' ? 'bg-green-500' :
                      result.severity === 'leve' ? 'bg-yellow-500' :
                      result.severity === 'moderada' ? 'bg-orange-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${(result.score / 27) * 100}%` }}
                  />
                </div>
                <p className={`text-xs mt-1 ${severityColor}`}>
                  {result.severity === 'minima' ? 'Depresión mínima' :
                   result.severity === 'leve' ? 'Depresión leve' :
                   result.severity === 'moderada' ? 'Depresión moderada' :
                   result.severity === 'moderada_grave' ? 'Depresión moderadamente grave' :
                   'Depresión grave'}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderGAD7Chart = () => {
    if (gad7Results.length === 0) {
      return (
        <div className="text-center py-12 text-gray-500">
          <Calendar className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>Aún no hay evaluaciones GAD-7</p>
          <p className="text-sm">Completa el cuestionario en la sección de Evaluaciones</p>
        </div>
      );
    }

    const trend = getLatestTrend(gad7Results);

    return (
      <div>
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h3 className="font-semibold text-gray-800">Evolución de puntajes GAD-7</h3>
            <p className="text-sm text-gray-500">Ansiedad (0-21 puntos)</p>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm ${
            trend.direction === 'improving' ? 'bg-green-100 text-green-700' :
            trend.direction === 'worsening' ? 'bg-red-100 text-red-700' :
            'bg-gray-100 text-gray-600'
          }`}>
            {trend.direction === 'improving' && '📉 Mejorando'}
            {trend.direction === 'worsening' && '📈 Empeorando'}
            {trend.direction === 'stable' && '➡️ Estable'}
          </div>
        </div>
        
        <div className="space-y-3">
          {gad7Results.map((result, idx) => {
            const date = new Date(result.date).toLocaleDateString('es-MX');
            return (
              <div key={idx} className="bg-gray-50 rounded-lg p-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-500">{date}</span>
                  <span className={`font-bold ${
                    result.severity === 'minima' ? 'text-green-600' :
                    result.severity === 'leve' ? 'text-yellow-600' :
                    result.severity === 'moderada' ? 'text-orange-600' :
                    'text-red-600'
                  }`}>{result.score} pts</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      result.severity === 'minima' ? 'bg-green-500' :
                      result.severity === 'leve' ? 'bg-yellow-500' :
                      result.severity === 'moderada' ? 'bg-orange-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${(result.score / 21) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {result.severity === 'minima' ? 'Ansiedad mínima' :
                   result.severity === 'leve' ? 'Ansiedad leve' :
                   result.severity === 'moderada' ? 'Ansiedad moderada' :
                   'Ansiedad grave'}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderMoodTrend = () => {
    if (moodData.length === 0) {
      return (
        <div className="text-center py-12 text-gray-500">
          <Heart className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>Aún no hay registros de estado de ánimo</p>
          <p className="text-sm">Usa el chat para comenzar a registrar</p>
        </div>
      );
    }

    const last7Days = moodData.slice(-7);
    const moodEmojis = {
      'muy_bajo': '😔', 'bajo': '😕', 'neutral': '😐', 'bueno': '🙂', 'muy_bueno': '😊'
    };

    return (
      <div>
        <h3 className="font-semibold text-gray-800 mb-4">Estado de ánimo reciente</h3>
        <div className="flex justify-around items-end h-32 gap-2">
          {last7Days.map((entry, idx) => (
            <div key={idx} className="flex flex-col items-center flex-1">
              <div className="text-2xl">{moodEmojis[entry.mood] || '😐'}</div>
              <div className="text-xs text-gray-500 mt-1">
                {new Date(entry.date).toLocaleDateString('es-MX', { weekday: 'short' })}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Reportes y Progreso</h1>
          <p className="text-gray-600">Visualiza tu evolución en salud mental</p>
        </div>
        <button
          onClick={exportToPDF}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Download className="w-4 h-4" />
          Exportar datos
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b">
        {[
          { id: 'phq9', label: 'Depresión (PHQ-9)', icon: Activity },
          { id: 'gad7', label: 'Ansiedad (GAD-7)', icon: TrendingUp },
          { id: 'mood', label: 'Estado de ánimo', icon: Heart }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        {activeTab === 'phq9' && renderPHQ9Chart()}
        {activeTab === 'gad7' && renderGAD7Chart()}
        {activeTab === 'mood' && renderMoodTrend()}
      </div>

      {/* Summary Cards */}
      <div className="grid md:grid-cols-3 gap-4 mt-6">
        <div className="bg-white rounded-lg p-4 shadow">
          <p className="text-sm text-gray-500">Evaluaciones PHQ-9</p>
          <p className="text-2xl font-bold text-gray-800">{phq9Results.length}</p>
        </div>
        <div className="bg-white rounded-lg p-4 shadow">
          <p className="text-sm text-gray-500">Evaluaciones GAD-7</p>
          <p className="text-2xl font-bold text-gray-800">{gad7Results.length}</p>
        </div>
        <div className="bg-white rounded-lg p-4 shadow">
          <p className="text-sm text-gray-500">Registros de ánimo</p>
          <p className="text-2xl font-bold text-gray-800">{moodData.length}</p>
        </div>
      </div>
    </div>
  );
};

export default ReportsDashboard;