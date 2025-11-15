# Solución para Errores de Build del Frontend en Vercel

## 🔍 Problema Identificado

El problema principal es que **Vercel necesita saber dónde está el proyecto Next.js** cuando está en un subdirectorio (`frontend/`). La configuración actual de `vercel.json` puede no estar indicando correctamente a Vercel cómo construir el proyecto.

## ✅ Soluciones Propuestas

### Solución 1: Configurar Root Directory en Dashboard de Vercel (RECOMENDADA)

Esta es la solución más simple y confiable:

1. Ve al dashboard de Vercel
2. Settings → General → **Root Directory**
3. Configura: `frontend`
4. Guarda los cambios
5. Haz un nuevo deploy

**Nota:** Con esta configuración, Vercel tratará `frontend/` como la raíz del proyecto y ejecutará automáticamente `npm install` y `npm run build` desde ahí.

**IMPORTANTE:** Si usas esta solución, necesitas actualizar `vercel.json` para que solo maneje las rutas del API:

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

### Solución 2: Usar package.json en la Raíz

Crear un `package.json` en la raíz que ejecute el build del frontend:

```json
{
  "name": "backyardleadai-root",
  "version": "1.0.0",
  "scripts": {
    "build": "cd frontend && npm install && npm run build",
    "install": "cd frontend && npm install"
  }
}
```

Y actualizar `vercel.json` para usar este package.json.

### Solución 3: Configuración Actual Mejorada

La configuración actual debería funcionar, pero puede necesitar ajustes. El problema puede ser que Vercel no está detectando correctamente el framework.

## 🎯 Recomendación Final

**Usar la Solución 1** porque:
- Es la más simple y confiable
- Vercel maneja automáticamente la detección del framework
- No requiere cambios complejos en la configuración
- Es la práctica recomendada por Vercel para proyectos con estructura de subdirectorios

## 📝 Pasos para Implementar la Solución 1

1. **En el Dashboard de Vercel:**
   - Ve a tu proyecto
   - Settings → General
   - Busca "Root Directory"
   - Configura: `frontend`
   - Guarda

2. **Actualizar vercel.json:**
   - Eliminar el build del frontend (Vercel lo detectará automáticamente)
   - Mantener solo el build del API Python

3. **Hacer un nuevo deploy:**
   - Push a tu repositorio o hacer "Redeploy" en Vercel

## 🔍 Verificaciones Adicionales

Si el problema persiste después de configurar el Root Directory, verifica:

- ✅ `frontend/package.json` tiene el script `build`
- ✅ `frontend/next.config.js` está configurado correctamente
- ✅ No hay errores de TypeScript o ESLint que bloqueen el build
- ✅ Las variables de entorno están configuradas en Vercel
- ✅ `node_modules` no está en el repositorio (debe estar en `.gitignore`)

## 🐛 Errores Comunes

### Error: "Cannot find module"
- **Causa:** Vercel no está ejecutando `npm install` en el directorio correcto
- **Solución:** Configurar Root Directory a `frontend`

### Error: "Build command failed"
- **Causa:** El comando de build no se ejecuta desde el directorio correcto
- **Solución:** Configurar Root Directory a `frontend`

### Error: "Output directory not found"
- **Causa:** Vercel busca `.next` en la raíz en lugar de `frontend/.next`
- **Solución:** Configurar Root Directory a `frontend`

