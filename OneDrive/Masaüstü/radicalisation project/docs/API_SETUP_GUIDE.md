# API Key Setup Guide

## 🐦 Twitter/X API Setup

### Step 1: Apply for Developer Account
1. Go to https://developer.twitter.com/
2. Click "Apply for a developer account"
3. Choose "Academic research" as your use case
4. Fill out the application explaining your radicalization research
5. Wait for approval (usually 1-7 days)

### Step 2: Create App and Get Keys
1. Once approved, go to Developer Portal
2. Create a new "App" 
3. Go to "Keys and tokens" tab
4. Generate and copy:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret) 
   - Bearer Token
   - Access Token & Secret

### Academic Research Benefits:
- Higher rate limits (10M tweets/month)
- Access to full archive search
- Real-time streaming capabilities

## 🤖 Reddit API Setup

### Step 1: Create Reddit App
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App"
3. Choose "script" type
4. Fill in details:
   - Name: "Digital Radicalization Research"
   - Description: "Academic research on digital radicalization patterns"
   - Redirect URI: http://localhost:8000

### Step 2: Get Credentials
- Client ID: Found under app name
- Client Secret: The "secret" field
- User Agent: Format "AppName/Version by u/YourUsername"

## 📺 YouTube API Setup (Optional)

### Step 1: Google Cloud Console
1. Go to https://console.cloud.google.com/
2. Create new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Restrict key to YouTube Data API

## 📱 Telegram API Setup (Optional)

### Step 1: Create Bot
1. Message @BotFather on Telegram
2. Use /newbot command
3. Follow prompts to name your bot
4. Get bot token

### Step 2: Join Channels (For Monitoring)
- Use bot to join public channels/groups
- Extract channel IDs for monitoring

## 🔒 Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables in production**
3. **Rotate keys regularly**
4. **Monitor API usage and costs**
5. **Implement rate limiting**
6. **Use read-only permissions where possible**

## 📊 Rate Limits to Consider

### Twitter API v2:
- Academic Research: 10M tweets/month
- Standard: 500K tweets/month
- Real-time streams: 1M tweets/month

### Reddit API:
- 60 requests per minute
- 1000 requests per hour
- OAuth required for higher limits

### YouTube API:
- 10,000 units per day (default)
- 1 search = 100 units
- Request quota increase if needed