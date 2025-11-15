# Análisis de Errores en Build de Vercel

## 🔍 Problemas Identificados

### 1. **Frontend en Subdirectorio - Problema Principal** ⚠️
   - **Problema**: El proyecto Next.js está en `frontend/` pero Vercel necesita saber dónde ejecutar los comandos de build.
   - **Impacto**: Vercel puede ejecutar `npm install` y `npm run build` desde la raíz en lugar de `frontend/`, causando errores de "module not found" o "package.json not found".
   - **Ubicación**: Estructura del proyecto

### 2. **Configuración de `vercel.json`**
   - **Problema**: La configuración con `builds` puede no estar indicando correctamente a Vercel cómo construir el proyecto Next.js desde un subdirectorio.
   - **Impacto**: Vercel puede no detectar correctamente el framework o ejecutar los comandos desde el directorio incorrecto.
   - **Ubicación**: `vercel.json`

### 3. **Falta Configuración del Root Directory**
   - **Problema**: No hay configuración explícita del directorio raíz para el proyecto Next.js.
   - **Impacto**: Vercel puede no saber dónde ejecutar `npm install` y `npm run build` para el frontend.
   - **Solución**: Configurar el root directory en el dashboard de Vercel (RECOMENDADO) o ajustar `vercel.json`.

### 4. **Rutas Potencialmente Problemáticas**
   - **Problema**: Las rutas pueden no funcionar correctamente si el build no se ejecuta desde el directorio correcto.
   - **Impacto**: El frontend puede no servir correctamente las páginas.

## ✅ Soluciones Propuestas

### Solución 1: Configurar Root Directory en Dashboard de Vercel (⭐ RECOMENDADA)

Esta es la solución más simple y confiable:

1. Ve al dashboard de Vercel → Tu Proyecto → Settings → General
2. Busca "Root Directory" 
3. Configura: `frontend`
4. Guarda los cambios
5. Haz un nuevo deploy

**Ventajas:**
- Vercel automáticamente detecta Next.js y ejecuta los comandos desde `frontend/`
- No requiere cambios complejos en `vercel.json`
- Es la práctica recomendada por Vercel para proyectos con estructura de subdirectorios

**IMPORTANTE:** Con esta solución, actualiza `vercel.json` para que solo maneje las rutas del API:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/v1/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHONPATH": "backend/src"
  }
}
```

### Solución 2: Mantener Configuración Actual (Ya Corregida)

La configuración actual de `vercel.json` debería funcionar, pero puede necesitar el Root Directory configurado:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    },
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/v1/(.*)",
      "dest": "api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ],
  "env": {
    "PYTHONPATH": "backend/src"
  }
}
```

**Nota**: Esta configuración funciona mejor cuando el Root Directory está configurado a `frontend` en el dashboard.

## 🎯 Recomendación Final

**Usar la Solución 1** porque:
- Es la más simple y confiable
- Vercel maneja automáticamente la detección del framework
- No requiere cambios complejos en la configuración
- Es la práctica recomendada por Vercel

## 📝 Pasos para Corregir

1. Actualizar `vercel.json` eliminando `config.outputDirectory`
2. Verificar que `api/requirements.txt` tenga todas las dependencias necesarias
3. Asegurarse de que las variables de entorno estén configuradas en Vercel
4. Hacer un nuevo deploy

## 🔍 Verificaciones Adicionales

- ✅ `api/index.py` exporta `handler` correctamente
- ✅ `api/requirements.txt` incluye `mangum`
- ✅ `frontend/package.json` tiene el script `build`
- ✅ Variables de entorno configuradas en Vercel dashboard
- ⚠️ `vercel.json` tiene configuración obsoleta que necesita corrección

