# 🚀 Railway Deployment Guide

## Quick Railway Deployment (2 minutes!)

### Step 1: Push to GitHub
```bash
# Make sure your code is pushed to GitHub
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Deploy to Railway

1. **Go to** [railway.app](https://railway.app)
2. **Sign up/Login** with your GitHub account
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose** `BRoliix/Driver_Drowsy_Master`
6. **Click "Deploy Now"**

### Step 3: Add Environment Variables

In Railway dashboard:
1. **Go to Variables tab**
2. **Add these variables**:
```
POCKETBASE_URL=https://steady-park.pockethost.io/
POCKETBASE_ADMIN_EMAIL=rohilsagar2003@gmail.com
POCKETBASE_ADMIN_PASSWORD=OmerAli787
```

### Step 4: That's it! 🎉

Railway will automatically:
- ✅ Detect Python app
- ✅ Install dependencies from `requirements.txt`
- ✅ Run the app using `Procfile`
- ✅ Provide HTTPS URL
- ✅ Enable WebSocket support

Your app will be available at: `https://your-app-name.railway.app`

---

## 🔧 Manual Railway CLI Deployment (Alternative)

### Install Railway CLI
```bash
npm install -g @railway/cli
# or
brew install railway/railway/railway
```

### Deploy via CLI
```bash
# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up

# Add environment variables
railway variables:set POCKETBASE_URL=https://steady-park.pockethost.io/
railway variables:set POCKETBASE_ADMIN_EMAIL=rohilsagar2003@gmail.com
railway variables:set POCKETBASE_ADMIN_PASSWORD=OmerAli787
```

---

## 📋 What's Configured

### Files Created for Railway:
- ✅ `Procfile` - Tells Railway how to start the app
- ✅ `requirements.txt` - Python dependencies
- ✅ `railway.toml` - Railway configuration
- ✅ `runtime.txt` - Python version

### App Features on Railway:
- ✅ **Full camera access** (HTTPS enabled)
- ✅ **WebSocket support** for real-time video
- ✅ **SOS system** connected to PocketBase
- ✅ **Auto-scaling** and **auto-deployment**
- ✅ **Custom domain** support (if needed)

### Fallback Detection:
- ✅ **Advanced mode**: Uses dlib + facial landmarks (if available)
- ✅ **Basic mode**: Uses OpenCV cascades (Railway fallback)
- ✅ **Automatic switching** based on available libraries

---

## ⚡ Expected Results

After deployment:
1. **App URL**: `https://your-project.railway.app`
2. **Camera Access**: Works perfectly (HTTPS)
3. **Real-time Detection**: WebSocket streaming
4. **SOS Alerts**: Saved to PocketBase database
5. **Performance**: Fast with Railway's infrastructure

---

## 🐛 Troubleshooting

### Check Deployment Logs:
```bash
railway logs
```

### Common Issues:

1. **Build Failed**: Check `requirements.txt` syntax
2. **App Won't Start**: Check `Procfile` command
3. **Environment Variables**: Verify in Railway dashboard
4. **Camera Not Working**: Should work automatically with HTTPS

### Support:
- Railway docs: [docs.railway.app](https://docs.railway.app)
- Railway Discord: Join their community

---

## 💰 Railway Pricing

- **Free Tier**: $5 worth of usage monthly
- **Usage-based**: Only pay for what you use
- **Generous limits**: Perfect for this application
- **No sleep mode**: Unlike other free tiers

---

## 🎯 Quick Deploy Command

```bash
# One-command deployment (after setting up Railway CLI)
railway login && railway init && railway up
```

**Your Driver Drowsiness Detection system will be live in under 2 minutes!** 🚀