# Guía: Configurar Root Directory en Vercel

## 🎯 Objetivo
Configurar Vercel para que construya el proyecto Next.js desde el directorio `frontend/`.

## 📋 Pasos en el Dashboard de Vercel

### Paso 1: Acceder a Settings
1. Ve a [vercel.com](https://vercel.com) e inicia sesión
2. Selecciona tu proyecto **BackyardLeadAI**
3. Ve a la pestaña **Settings** (Configuración)

### Paso 2: Configurar Root Directory
1. En el menú lateral izquierdo, haz clic en **General**
2. Desplázate hasta la sección **Root Directory**
3. Haz clic en **Edit** (Editar)
4. Ingresa: `frontend`
5. Haz clic en **Save** (Guardar)

### Paso 3: Verificar la Configuración
Después de guardar, deberías ver:
- **Root Directory:** `frontend`
- **Framework Preset:** Next.js (detectado automáticamente)
- **Build Command:** `npm run build` (automático)
- **Output Directory:** `.next` (automático)

### Paso 4: Hacer Deploy
1. Ve a la pestaña **Deployments**
2. Haz clic en **Redeploy** en el último deployment
3. O simplemente haz push a tu repositorio para activar un nuevo deploy automático

## ✅ Verificación

Después del deploy, verifica que:
- ✅ El build se completa sin errores
- ✅ El frontend se sirve correctamente en la URL principal
- ✅ El API funciona en `/api/v1/*`

## 🔍 Si el Build Sigue Fallando

Si después de configurar el Root Directory el build aún falla:

1. **Revisa los logs de build:**
   - Ve a Deployments → Click en el deployment fallido → Ver logs

2. **Verifica las variables de entorno:**
   - Settings → Environment Variables
   - Asegúrate de que todas las variables necesarias estén configuradas

3. **Verifica que `vercel.json` esté actualizado:**
   - El archivo `vercel.json` ya está configurado correctamente
   - Solo necesita manejar las rutas del API Python

## 📝 Notas Importantes

- **Root Directory** le dice a Vercel dónde está el proyecto principal
- Con `frontend` configurado, Vercel ejecutará todos los comandos desde `frontend/`
- El `vercel.json` seguirá funcionando para las rutas del API Python
- No necesitas cambiar nada más en la configuración

