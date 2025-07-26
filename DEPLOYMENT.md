# Quick Deployment Guide

## ⚡ Fast Railway Deployment

### Step 1: Get Hugging Face Token
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: `Railway-RAG-API`
4. Type: `Read`
5. Copy the token

### Step 2: Deploy to Railway
1. Go to https://railway.app
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your `Rag_Chainlet_API` repository
5. Wait for deployment to start

### Step 3: Add Environment Variable
1. In Railway dashboard, click on your project
2. Go to "Variables" tab
3. Add new variable:
   - **Name**: `HUGGINGFACE_API_TOKEN`
   - **Value**: Your token from Step 1
4. Click "Add"

### Step 4: Redeploy
1. Click "Deploy" to restart with the new token
2. Wait for deployment to complete
3. Your API will be available at the Railway URL

## ✅ Verification

### Test your deployed API:
```bash
curl -X POST "https://your-railway-url.railway.app/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI governance?"}'
```

### Expected response:
```json
{
  "answer": "AI governance refers to..."
}
```

## 🔧 Troubleshooting

### Common Issues:

1. **Build fails**: Check that `HUGGINGFACE_API_TOKEN` is set
2. **API errors**: Verify your token has "Read" permissions
3. **Timeout**: First request may be slow (model loading)

### Support:
- Check Railway logs for detailed error messages
- Ensure ChromaDB files are included in your repository

---

**Total deployment time: ~5-10 minutes** ⏱️
