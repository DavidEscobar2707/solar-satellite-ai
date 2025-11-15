# ✅ Pasos para Configurar Root Directory en Vercel

## 🚀 Instrucciones Paso a Paso

### 1️⃣ Acceder al Dashboard de Vercel
- Ve a: https://vercel.com
- Inicia sesión con tu cuenta
- Selecciona tu proyecto **BackyardLeadAI**

### 2️⃣ Ir a Settings
- En la parte superior del proyecto, haz clic en **Settings**
- O usa el menú lateral izquierdo → **Settings**

### 3️⃣ Configurar Root Directory
1. En el menú lateral de Settings, haz clic en **General**
2. Busca la sección **Root Directory**
3. Haz clic en el botón **Edit** (o el ícono de editar)
4. En el campo de texto, escribe: `frontend`
5. Haz clic en **Save** (Guardar)

### 4️⃣ Verificar la Configuración
Después de guardar, deberías ver:
```
Root Directory: frontend
Framework Preset: Next.js
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

### 5️⃣ Hacer Deploy
Tienes dos opciones:

**Opción A: Redeploy Manual**
- Ve a la pestaña **Deployments**
- Encuentra el último deployment
- Haz clic en los tres puntos (⋯) → **Redeploy**
- Confirma el redeploy

**Opción B: Push al Repositorio**
- Haz commit y push de los cambios
- Vercel automáticamente creará un nuevo deployment

## 📸 Ubicación Visual

```
Vercel Dashboard
├── Tu Proyecto
│   ├── Overview
│   ├── Deployments
│   ├── Settings ⬅️ AQUÍ
│   │   ├── General ⬅️ AQUÍ
│   │   │   └── Root Directory ⬅️ CONFIGURAR: "frontend"
│   │   ├── Environment Variables
│   │   └── ...
```

## ✅ Verificación Post-Configuración

Después del deploy, verifica:

1. **Build Exitoso:**
   - Ve a Deployments
   - El último deployment debe mostrar estado ✅ "Ready"

2. **Frontend Funcionando:**
   - Visita: `https://tu-proyecto.vercel.app`
   - Debe cargar la página principal sin errores

3. **API Funcionando:**
   - Visita: `https://tu-proyecto.vercel.app/api/v1/health`
   - Debe responder: `{"status": "ok"}`

## 🐛 Troubleshooting

### Si el Root Directory no aparece:
- Asegúrate de estar en **Settings → General**
- Si no ves la opción, puede que necesites permisos de administrador del proyecto

### Si el build sigue fallando:
1. Verifica que escribiste exactamente: `frontend` (sin espacios, sin barra al inicio)
2. Revisa los logs del deployment para ver el error específico
3. Verifica que `frontend/package.json` existe en el repositorio

### Si las rutas del API no funcionan:
- El `vercel.json` ya está configurado correctamente
- Las rutas del API deberían funcionar automáticamente
- Verifica que `api/index.py` existe en el repositorio

## 📝 Notas

- ✅ El `vercel.json` ya está actualizado y listo para funcionar con Root Directory
- ✅ No necesitas cambiar nada más en el código
- ✅ Vercel detectará automáticamente Next.js cuando Root Directory esté en `frontend`
- ✅ El build del frontend se ejecutará automáticamente desde `frontend/`

