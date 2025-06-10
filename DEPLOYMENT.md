# Forever Boutique Deployment Guide

This guide will walk you through deploying the Forever Boutique chatbot to Render and setting up the Facebook Messenger webhook.

## Prerequisites

- A Render.com account
- A Facebook Developer account
- A Facebook Page for your business
- Python 3.11 or higher

## Part 1: Deploy to Render

### Step 1: Prepare Your Repository
1. Ensure all files are committed to your repository
2. Verify these files exist in your repository:
   - `render.yaml`
   - `start.sh`
   - `requirements.txt`
   - `Procfile`
   - `main.py`
   - `integrations/facebook_messenger.py`

### Step 2: Deploy on Render
1. Log in to your Render dashboard
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - Name: `forever-boutique`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `./start.sh`
5. Add Environment Variables:
   - `FB_VERIFY_TOKEN`: Your Facebook webhook verify token
   - `FB_PAGE_ACCESS_TOKEN`: Your Facebook Page access token
   - `FB_APP_SECRET`: Your Facebook App secret
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ENVIRONMENT`: Set to `production`
6. Click "Create Web Service"

### Step 3: Verify Deployment
1. Wait for the build to complete
2. Visit your Render URL (e.g., `https://forever-boutique.onrender.com`)
3. Test the health endpoint: `https://forever-boutique.onrender.com/health`
4. You should see a JSON response indicating the service is healthy

## Part 2: Facebook Messenger Setup

### Step 1: Create Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com)
2. Click "Create App"
3. Select "Business" as the app type
4. Fill in your app details
5. Add "Messenger" product to your app

### Step 2: Configure Messenger
1. In your app dashboard, go to "Messenger" → "Settings"
2. Generate a Page Access Token
3. Save this token as `FB_PAGE_ACCESS_TOKEN` in Render
4. Get your App Secret from "Settings" → "Basic"
5. Save this as `FB_APP_SECRET` in Render

### Step 3: Configure Webhook
1. In Messenger settings, click "Add Callback URL"
2. Enter your Render URL + `/webhook` (e.g., `https://forever-boutique.onrender.com/webhook`)
3. Enter your verify token (same as `FB_VERIFY_TOKEN` in Render)
4. Select these subscription fields:
   - `messages`
   - `messaging_postbacks`
   - `messaging_optins`
5. Click "Verify and Save"

### Step 4: Test the Integration
1. Go to your Facebook Page
2. Click "Message" to start a conversation
3. Send a test message
4. Verify you receive a response from the chatbot

## Troubleshooting

### Common Issues
1. Webhook verification fails:
   - Check if `FB_VERIFY_TOKEN` matches in both Facebook and Render
   - Ensure the webhook URL is correct

2. Messages not being received:
   - Verify `FB_PAGE_ACCESS_TOKEN` is correct
   - Check Render logs for any errors
   - Ensure the Facebook Page is connected to your app

3. Deployment fails:
   - Check Render build logs
   - Verify all required files are present
   - Ensure `start.sh` has execute permissions

### Checking Logs
1. In Render dashboard, click on your service
2. Go to "Logs" tab
3. Look for any error messages or warnings

## Support

If you encounter any issues:
1. Check the Render logs
2. Verify all environment variables are set correctly
3. Ensure your Facebook App settings are properly configured
4. Contact support if issues persist 