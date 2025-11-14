# Guía de Despliegue en Vercel

Esta guía te ayudará a desplegar BackyardLeadAI completo (backend + frontend) en Vercel.

## 📋 Requisitos Previos

1. Cuenta en [Vercel](https://vercel.com) (gratis)
2. Repositorio en GitHub con el código
3. API Keys necesarias:
   - Zillow API Key (RapidAPI)
   - Google Maps API Key
   - Gemini API Key

## 🚀 Pasos para Desplegar

### 1. Preparar el Repositorio

Asegúrate de que tu repositorio tenga estos archivos:
- ✅ `vercel.json` (configuración de Vercel)
- ✅ `api/index.py` (wrapper para funciones serverless)
- ✅ `api/requirements.txt` (dependencias Python para Vercel)
- ✅ `requirements.txt` (con `mangum` incluido)
- ✅ `frontend/` (aplicación Next.js)

### 2. Conectar Repositorio a Vercel

1. Ve a [vercel.com](https://vercel.com) e inicia sesión
2. Click en "Add New Project"
3. Importa tu repositorio de GitHub
4. Vercel detectará automáticamente la configuración desde `vercel.json`

### 3. Configurar Variables de Entorno

En el dashboard de Vercel, ve a **Settings → Environment Variables** y agrega:

```
ZILLOW_API_KEY=tu_clave_zillow
GOOGLE_MAPS_API_KEY=tu_clave_google_maps
GEMINI_API_KEY=tu_clave_gemini
VISION_MODEL=gemini-2.5-flash
```

**Importante:** Marca estas variables para todos los entornos (Production, Preview, Development).

### 4. Configurar Build Settings (si es necesario)

Vercel debería detectar automáticamente:
- **Framework Preset:** Next.js (para frontend)
- **Build Command:** Automático
- **Output Directory:** Automático
- **Python Version:** 3.10+ (automático)

Si necesitas ajustar algo:
- **Root Directory:** Dejar vacío (raíz del proyecto)
- **Install Command:** Automático

### 5. Desplegar

1. Click en **Deploy**
2. Espera a que termine el build (puede tardar 3-5 minutos la primera vez)
3. Una vez completado, tendrás URLs:
   - **Production:** `https://tu-proyecto.vercel.app`
   - **Preview:** URLs únicas para cada push

### 6. Verificar el Despliegue

1. **Frontend:** Visita `https://tu-proyecto.vercel.app`
2. **Backend Health:** `https://tu-proyecto.vercel.app/api/v1/health`
3. **API Docs:** `https://tu-proyecto.vercel.app/docs` (si FastAPI docs están habilitados)

## 🔧 Estructura de URLs en Producción

- **Frontend:** `https://tu-proyecto.vercel.app/`
- **API Backend:** `https://tu-proyecto.vercel.app/api/v1/*`
- **Ejemplo:** `https://tu-proyecto.vercel.app/api/v1/leads`

## 💰 Costos

### Plan Gratuito (Hobby)
- ✅ 100GB-hours de ejecución de funciones serverless/mes
- ✅ Ancho de banda ilimitado para frontend
- ✅ HTTPS automático
- ✅ Deployments ilimitados
- ✅ Dominios personalizados

**Suficiente para:** Desarrollo y proyectos pequeños/medianos

### Plan Pro ($20/mes)
- ✅ Todo lo del plan gratuito
- ✅ Sin cold starts
- ✅ 60 segundos de timeout (vs 10s en free)
- ✅ Más ancho de banda
- ✅ Analytics avanzado

**Recomendado si:** Necesitas más tiempo de ejecución o eliminar cold starts

## 🐛 Troubleshooting

### Error: "Module not found"
- Verifica que `api/requirements.txt` tenga todas las dependencias necesarias
- Revisa los logs de build en Vercel

### Error: "Handler not found"
- Asegúrate de que `api/index.py` exporte `handler`
- Verifica que `mangum` esté en `requirements.txt`

### Error: "CORS"
- El backend ya está configurado para aceptar requests de Vercel
- Verifica que `allow_origin_regex` incluya `https://.*\.vercel\.app`

### Cold Starts Lentos
- Normal en el plan gratuito
- Considera upgrade a Pro para eliminar cold starts
- O usa Railway para backend siempre activo

### Timeout en Requests Largos
- Plan gratuito: máximo 10 segundos
- Plan Pro: máximo 60 segundos
- Si necesitas más tiempo, considera Railway para el backend

## 📝 Notas Importantes

1. **Variables de Entorno:** Nunca subas `.env` al repositorio (ya está en `.vercelignore`)

2. **Python Path:** Vercel usa `PYTHONPATH=backend/src` automáticamente gracias a `vercel.json`

3. **Frontend API URL:** En producción, el frontend usa URLs relativas automáticamente (mismo dominio)

4. **Logs:** Puedes ver logs en tiempo real en el dashboard de Vercel → Deployments → Logs

5. **Re-deploy:** Cada push a `main` despliega automáticamente a producción

## 🔄 Actualizar el Despliegue

Cualquier push a tu repositorio activará un nuevo deployment automáticamente.

Para forzar un re-deploy:
1. Ve a Deployments en Vercel
2. Click en "Redeploy" en el deployment más reciente

## 📚 Recursos

- [Documentación de Vercel](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [Mangum Documentation](https://mangum.io/)

