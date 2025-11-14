# BackyardLeadAI

BackendLeadAI is a platform that generates landscaping leads by detecting homes with undeveloped or underused backyards using satellite imagery and AI analysis.

## Architecture

- **Backend**: FastAPI (Python) - Analyzes properties via Zillow API, satellite imagery, and OpenAI Vision
- **Frontend**: Next.js (TypeScript) - B2B storefront for landscaping companies to purchase leads

## Features

- Property discovery via Zillow API
- Satellite imagery analysis (Google Maps Static API)
- AI-powered backyard classification (OpenAI Vision)
- Lead scoring based on landscaping potential
- CSV/JSON export for leads
- Stripe integration ready (frontend prepared)

## Setup

### Backend

1. Install dependencies:
```bash
pip install -r requirements.txt
# or
poetry install
```

2. Set environment variables:
```bash
ZILLOW_API_KEY=your_key
GOOGLE_MAPS_API_KEY=your_key
OPENAI_API_KEY=your_key
```

3. Run backend:
```bash
uvicorn backend.src.solar_ai_backend.main:app --reload
```

### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
npm install
```

2. Set environment variables:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_key
```

3. Run frontend:
```bash
npm run dev
```

## Deployment

### Vercel (Recommended - Full Stack)

The entire application (backend + frontend) can be deployed to Vercel:

1. **Connect Repository to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel will auto-detect the configuration from `vercel.json`

2. **Set Environment Variables in Vercel Dashboard:**
   ```
   ZILLOW_API_KEY=your_zillow_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_key
   GEMINI_API_KEY=your_gemini_api_key
   VISION_MODEL=gemini-2.5-flash
   ```

3. **Deploy:**
   - Vercel will automatically build and deploy both frontend and backend
   - Backend API will be available at `/api/v1/*`
   - Frontend will be served from the root

4. **Cost:** Free tier includes:
   - 100GB-hours of serverless function execution per month
   - Unlimited bandwidth for frontend
   - Automatic HTTPS

### Alternative: Backend on Railway + Frontend on Vercel

If you need longer execution times or always-on backend:

1. **Backend (Railway):**
   - Connect repository to Railway
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn backend.src.solar_ai_backend.main:app --host 0.0.0.0 --port $PORT`
   - Set environment variables
   - Cost: $5/month minimum

2. **Frontend (Vercel):**
   - Set `NEXT_PUBLIC_API_URL` to your Railway backend URL
   - Deploy normally
   - Cost: Free

## API Endpoints

- `POST /api/v1/leads` - Generate landscaping leads for a location
- `POST /api/v1/validate-location` - Validate and geocode a location
- `GET /health` - Health check

See `docs/leeds_endpoint.md` for detailed API documentation.

