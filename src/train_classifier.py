import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import nltk
from nltk.corpus import stopwords
import joblib
import re
import os
import warnings
warnings.filterwarnings('ignore')

# Configuración
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*60)
print("🚀 INICIANDO ENTRENAMIENTO DEL CLASIFICADOR DE DEPRESIÓN")
print("="*60)

# ========== 1. CARGAR DATOS ==========
print("\n📂 1. Cargando datos...")

# Verificar que el archivo existe
if not os.path.exists('data/synthetic_depression_data.csv'):
    print("   ❌ ERROR: No se encuentra el archivo data/synthetic_depression_data.csv")
    print("   💡 Ejecuta primero: python src/utils/create_synthetic_data.py")
    exit(1)

df = pd.read_csv('data/synthetic_depression_data.csv')
print(f"   ✅ Dataset cargado: {len(df)} muestras")

# Verificar que la columna 'text' existe
if 'text' not in df.columns:
    print("   ❌ ERROR: La columna 'text' no existe en el dataset")
    print(f"   📋 Columnas disponibles: {list(df.columns)}")
    exit(1)

# ========== 2. LIMPIAR DATOS ==========
print("\n🧹 2. Limpiando datos...")

# Convertir la columna 'text' a string y manejar valores nulos
df['text'] = df['text'].fillna('').astype(str)

# Eliminar filas donde 'text' está vacío después de limpiar
initial_count = len(df)
df = df[df['text'].str.strip() != '']
print(f"   ✅ Eliminadas {initial_count - len(df)} filas con texto vacío")
print(f"   ✅ Total de muestras válidas: {len(df)}")

# ========== 3. ANÁLISIS EXPLORATORIO ==========
print("\n📊 3. Análisis exploratorio...")
print(f"   Distribución de severidad:")
for severity, count in df['severity'].value_counts().items():
    print(f"      - {severity}: {count} muestras")
print(f"   Puntaje PHQ-9 - Media: {df['phq9_total'].mean():.2f}, Max: {df['phq9_total'].max()}, Min: {df['phq9_total'].min()}")

# ========== 4. PREPROCESAMIENTO ==========
print("\n🧹 4. Preprocesando texto...")

# Descargar stopwords en español
try:
    nltk.data.find('corpora/stopwords.zip')
except:
    nltk.download('stopwords')

# Obtener stopwords en español como lista
spanish_stopwords = set(stopwords.words('spanish'))

# Añadir palabras comunes que no aportan significado
custom_stopwords = spanish_stopwords.union({
    'me', 'te', 'se', 'lo', 'la', 'le', 'mi', 'tu', 'su', 'de', 'en', 'y', 'a', 'que',
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'eso', 'esa', 'esos', 'esas',
    'este', 'esta', 'estos', 'estas', 'aquello', 'aquel', 'aquella', 'eso', 'esa',
    'muy', 'más', 'menos', 'tan', 'como', 'cuando', 'donde', 'cual', 'cuales',
    'porque', 'por', 'para', 'con', 'sin', 'sobre', 'entre', 'hasta', 'desde'
})

# Convertir a lista para TfidfVectorizer
stop_words_list = list(custom_stopwords)

print(f"   ✅ Stopwords cargadas: {len(stop_words_list)} palabras")

def preprocess_text(text):
    """Limpia y normaliza texto - MANEJA ERRORES"""
    try:
        # Asegurar que es string
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        
        # Si está vacío, retornar vacío
        if len(text.strip()) == 0:
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Eliminar signos de puntuación (mantener solo letras, números y espacios)
        text = re.sub(r'[^a-záéíóúñü\s]', '', text)
        
        # Dividir en palabras
        words = text.split()
        
        # Filtrar stopwords y palabras muy cortas
        words = [w for w in words if w not in stop_words_list and len(w) > 2]
        
        # Unir de nuevo
        return ' '.join(words)
    except Exception as e:
        print(f"   ⚠️ Error al procesar texto: {text[:50]}... Error: {e}")
        return ""

# Aplicar preprocesamiento con manejo de errores
print("   Procesando textos...")
df['text_clean'] = df['text'].apply(preprocess_text)

# Eliminar filas donde text_clean quedó vacío
initial_count = len(df)
df = df[df['text_clean'].str.strip() != '']
print(f"   ✅ Eliminadas {initial_count - len(df)} filas con texto limpio vacío")
print(f"   ✅ Total de muestras después de limpieza: {len(df)}")

# Mostrar ejemplo
if len(df) > 0:
    print(f"\n   📝 Ejemplo de texto original vs preprocesado:")
    print(f"   Original: {df['text'].iloc[0][:100]}...")
    print(f"   Limpio:   {df['text_clean'].iloc[0][:100]}...")

# ========== 5. VERIFICAR QUE HAY DATOS SUFICIENTES ==========
if len(df) < 100:
    print("\n   ❌ ERROR: No hay suficientes datos después de la limpieza")
    print(f"   💡 Se necesitan al menos 100 muestras, solo hay {len(df)}")
    print("   💡 Revisa el dataset o ejecuta nuevamente create_synthetic_data.py")
    exit(1)

# ========== 6. CREAR FEATURES TF-IDF ==========
print("\n🔢 5. Creando features TF-IDF...")

# Crear vectorizer con stopwords en español como lista
vectorizer = TfidfVectorizer(
    max_features=2000,
    ngram_range=(1, 3),
    min_df=2,
    max_df=0.8,
    stop_words=stop_words_list  # Usar la lista de stopwords en español
)

X = vectorizer.fit_transform(df['text_clean'])
y = df['severity']
print(f"   ✅ Matriz de features: {X.shape[0]} muestras x {X.shape[1]} features")

# Verificar que hay features suficientes
if X.shape[1] == 0:
    print("\n   ❌ ERROR: No se generaron features. Revisa el preprocesamiento.")
    exit(1)

# ========== 7. DIVIDIR DATOS ==========
print("\n✂️ 6. Dividiendo datos en entrenamiento y prueba...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   ✅ Entrenamiento: {X_train.shape[0]} muestras")
print(f"   ✅ Prueba: {X_test.shape[0]} muestras")

# ========== 8. ENTRENAR MODELO ==========
print("\n🤖 7. Entrenando modelo Random Forest...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)
print("   ✅ Modelo entrenado")

# ========== 9. EVALUAR MODELO ==========
print("\n📈 8. Evaluando modelo...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"   🎯 Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

print("\n   📋 Reporte de clasificación:")
print(classification_report(y_test, y_pred))

# ========== 10. MATRIZ DE CONFUSIÓN ==========
print("\n📊 9. Generando matriz de confusión...")
os.makedirs('models', exist_ok=True)

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=model.classes_,
            yticklabels=model.classes_)
plt.title('Matriz de Confusión')
plt.ylabel('Valor Real')
plt.xlabel('Valor Predicho')
plt.tight_layout()
plt.savefig('models/confusion_matrix.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Guardada en: models/confusion_matrix.png")

# ========== 11. FEATURES IMPORTANTES ==========
print("\n🔝 10. Analizando palabras más importantes...")
feature_names = vectorizer.get_feature_names_out()
feature_importance = pd.DataFrame({
    'palabra': feature_names,
    'importancia': model.feature_importances_
}).sort_values('importancia', ascending=False).head(20)

plt.figure(figsize=(10, 8))
sns.barplot(data=feature_importance, x='importancia', y='palabra')
plt.title('Top 20 Palabras Más Importantes')
plt.xlabel('Importancia')
plt.ylabel('Palabra')
plt.tight_layout()
plt.savefig('models/feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Top 10 palabras:")
for i, row in feature_importance.head(10).iterrows():
    print(f"      - {row['palabra']}: {row['importancia']:.4f}")

# ========== 12. VALIDACIÓN CRUZADA ==========
print("\n🔄 11. Validación cruzada...")
try:
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    print(f"   Scores: {cv_scores}")
    print(f"   Media: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    cv_mean = cv_scores.mean()
except Exception as e:
    print(f"   ⚠️ Error en validación cruzada: {e}")
    cv_mean = accuracy

# ========== 13. PRUEBAS CON EJEMPLOS ==========
print("\n🧪 12. Probando con frases de ejemplo...")
test_phrases = [
    "Hoy me siento muy bien, todo va excelente",
    "Me siento un poco cansado pero bien",
    "No sé qué hacer, me siento muy triste y sin ganas de nada",
    "No puedo dormir, estoy muy preocupado por todo",
    "Ya no quiero seguir así, siento que no hay salida",
    "Me siento inútil, todo me sale mal",
    "He pensado en suicidio, no quiero vivir más"
]

for phrase in test_phrases:
    clean_phrase = preprocess_text(phrase)
    if clean_phrase:
        vectorized = vectorizer.transform([clean_phrase])
        pred = model.predict(vectorized)[0]
        proba = model.predict_proba(vectorized)[0]
        confidence = max(proba) * 100
        print(f"   '{phrase[:50]}...' → {pred.upper()} ({confidence:.1f}%)")
    else:
        print(f"   '{phrase[:50]}...' → ⚠️ No se pudo procesar")

# ========== 14. GUARDAR MODELO ==========
print("\n💾 13. Guardando modelo...")
os.makedirs('models', exist_ok=True)

joblib.dump(model, 'models/depression_classifier.pkl')
joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
print("   ✅ Modelo guardado en: models/depression_classifier.pkl")
print("   ✅ Vectorizador guardado en: models/tfidf_vectorizer.pkl")

# ========== 15. GUARDAR MÉTRICAS EN TXT ==========
print("\n📝 14. Guardando reporte de métricas...")
with open('models/training_report.txt', 'w', encoding='utf-8') as f:
    f.write("="*60 + "\n")
    f.write("REPORTE DE ENTRENAMIENTO - CLASIFICADOR DE DEPRESIÓN\n")
    f.write("="*60 + "\n\n")
    f.write(f"Muestras totales: {len(df)}\n")
    f.write(f"Features: {X.shape[1]}\n")
    f.write(f"Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)\n")
    f.write(f"Validación cruzada: {cv_mean:.4f} ({cv_mean*100:.2f}%)\n\n")
    f.write("Top 10 palabras más importantes:\n")
    for i, row in feature_importance.head(10).iterrows():
        f.write(f"  - {row['palabra']}: {row['importancia']:.4f}\n")
print("   ✅ Reporte guardado en: models/training_report.txt")

# ========== RESUMEN FINAL ==========
print("\n" + "="*60)
print("✅ ENTRENAMIENTO COMPLETADO CON ÉXITO")
print("="*60)
print(f"\n📊 Resumen:")
print(f"   - Muestras: {len(df)}")
print(f"   - Accuracy: {accuracy*100:.2f}%")
print(f"   - Validación cruzada: {cv_mean*100:.2f}%")
print(f"   - Features: {X.shape[1]} palabras únicas")
print(f"\n📁 Archivos generados en carpeta 'models/':")
print(f"   - depression_classifier.pkl")
print(f"   - tfidf_vectorizer.pkl")
print(f"   - confusion_matrix.png")
print(f"   - feature_importance.png")
print(f"   - training_report.txt")
print("\n🚀 Siguiente paso: Ejecutar el backend con FastAPI")