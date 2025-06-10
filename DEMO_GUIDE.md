# Forever Boutique Chat Demo - Quick Start Guide

This guide will help you get the Forever Boutique chatbot demo up and running quickly, without needing to deal with Facebook integration.

## Local Development

### Step 1: Setup
1. Make sure you have Python 3.11+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Run Locally
1. Start the demo server:
   ```bash
   python demo_app.py
   ```
2. Open your browser to: `http://localhost:8000`

## Deploy to Render

### Step 1: Prepare Repository
1. Ensure these files are in your repository:
   - `demo_app.py`
   - `demo_render.yaml`
   - `requirements.txt`
   - `templates/index.html`

### Step 2: Deploy
1. Log in to Render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select "Python" as the environment
5. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn demo_app:app --host 0.0.0.0 --port $PORT`
6. Click "Create Web Service"

### Step 3: Test
1. Wait for deployment to complete
2. Visit your Render URL
3. Test the chat interface

## Features

The demo version includes:
- Modern, responsive chat interface
- Real-time message handling
- Product recommendations
- FAQ responses
- Store information
- Special offers

## Testing the Chatbot

Try these example queries:
1. "What are your store hours?"
2. "Can you recommend some products?"
3. "What's your return policy?"
4. "Do you have any special offers?"
5. "Where is your store located?"

## Troubleshooting

If you encounter issues:
1. Check the browser console for errors
2. Verify the server is running (`/health` endpoint)
3. Check Render logs for deployment issues

## Next Steps

Once you're ready to integrate with Facebook:
1. Follow the full deployment guide in `DEPLOYMENT.md`
2. Set up your Facebook Developer account
3. Configure the webhook

## Support

For immediate assistance:
1. Check the Render logs
2. Review the error messages in the browser console
3. Contact support if issues persist 