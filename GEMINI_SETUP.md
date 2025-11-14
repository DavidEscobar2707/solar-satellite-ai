# Configuración de Google Gemini

El proyecto ahora usa **Google Gemini Pro Vision** para el análisis de imágenes de patios traseros.

## Obtener API Key de Gemini

1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en "Get API Key" o "Create API Key"
4. Copia la API key generada

## Configurar en el proyecto

Agrega la API key a tu archivo `.env` en la raíz del proyecto:

```env
GEMINI_API_KEY=tu_api_key_aqui
```

## Instalar dependencias

```bash
pip install google-generativeai>=0.3.0 Pillow>=10.0.0
```

O reinstala todas las dependencias:

```bash
pip install -r requirements.txt
```

## Modelo usado

- **Modelo por defecto**: `gemini-pro-vision` (modelo estándar para visión)
- **Precio**: Muy bajo comparado con OpenAI
- **Capacidades**: Soporta análisis de imágenes (vision)
- **Modelos alternativos disponibles**: `gemini-pro`, `gemini-1.5-pro`

## Verificar que funciona

Después de configurar la API key, reinicia el servidor y prueba:

```bash
curl -X POST http://localhost:8000/api/v1/leads \
  -H "Content-Type: application/json" \
  -d '{"location": "San Diego, CA", "max_properties": 1}'
```

Deberías ver `backyard_status` con valores como "undeveloped", "partially_developed", etc., en lugar de `null`.

