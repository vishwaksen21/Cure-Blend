# 🚀 Cure-Blend Deployment Guide

Complete guide for deploying your Streamlit health diagnosis application to production.

---

## 📋 Pre-Deployment Checklist

- [x] Application tested locally ✅
- [x] All dependencies listed in requirements.txt ✅
- [x] Data files available (9.7MB total) ✅
- [x] No console warnings ✅
- [ ] Choose deployment platform
- [ ] Configure environment variables (if using Azure AI)
- [ ] Set up domain name (optional)

---

## 🌟 Recommended: Streamlit Community Cloud (FREE & EASIEST)

### Advantages:
- ✅ **Free hosting** for public apps
- ✅ **Zero configuration** needed
- ✅ **Auto-deployment** from GitHub
- ✅ **HTTPS** included
- ✅ **Custom domain** support
- ✅ Built-in **secrets management**

### Steps:

#### 1. Push to GitHub
```bash
cd /workspaces/Cure-Blend

# Initialize git (if not already done)
git init
git add .
git commit -m "Production-ready Cure-Blend application"

# Push to GitHub
git remote add origin https://github.com/vishwaksen21/Cure-Blend.git
git branch -M main
git push -u origin main
```

#### 2. Deploy to Streamlit Cloud

1. Go to **https://share.streamlit.io/**
2. Click **"New app"**
3. Connect your GitHub account
4. Select:
   - **Repository:** `vishwaksen21/Cure-Blend`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
5. Click **"Deploy"**

#### 3. Configure Secrets (Optional - for Azure AI)

If using Azure AI features:
1. In Streamlit Cloud dashboard, go to **Settings → Secrets**
2. Add:
   ```toml
   [azure]
   api_key = "your-azure-api-key"
   endpoint = "your-azure-endpoint"
   ```

#### 4. Done! 🎉

Your app will be live at: `https://cure-blend-yourappname.streamlit.app`

---

## 🐳 Option 2: Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create .dockerignore

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.log
.git/
.gitignore
.vscode/
.idea/
*.md
!README.md
test_*.py
```

### Build and Run

```bash
# Build image
docker build -t cure-blend .

# Run container
docker run -p 8501:8501 cure-blend

# Or with environment variables
docker run -p 8501:8501 \
  -e AZURE_API_KEY="your-key" \
  -e AZURE_ENDPOINT="your-endpoint" \
  cure-blend
```

### Deploy to Docker Hub

```bash
# Login
docker login

# Tag image
docker tag cure-blend vishwaksen21/cure-blend:latest

# Push
docker push vishwaksen21/cure-blend:latest
```

---

## ☁️ Option 3: Cloud Platforms

### 3.1 Heroku

#### Create Files:

**Procfile:**
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

**runtime.txt:**
```
python-3.10.13
```

**setup.sh:**
```bash
#!/bin/bash
mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

#### Deploy:
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create cure-blend-app

# Push
git push heroku main

# Open
heroku open
```

---

### 3.2 AWS EC2

1. **Launch EC2 Instance:**
   - Ubuntu 22.04 LTS
   - t2.small (2GB RAM minimum)
   - Open port 8501 in security group

2. **Connect and Setup:**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3-pip git

# Clone repository
git clone https://github.com/vishwaksen21/Cure-Blend.git
cd Cure-Blend

# Install requirements
pip3 install -r requirements.txt

# Run with nohup
nohup streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 &
```

3. **Setup Systemd Service (Recommended):**

Create `/etc/systemd/system/cure-blend.service`:
```ini
[Unit]
Description=Cure-Blend Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Cure-Blend
ExecStart=/usr/local/bin/streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable cure-blend
sudo systemctl start cure-blend
sudo systemctl status cure-blend
```

4. **Setup Nginx Reverse Proxy:**
```bash
sudo apt install -y nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/cure-blend
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/cure-blend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### 3.3 Google Cloud Run

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Login
gcloud auth login

# Set project
gcloud config set project your-project-id

# Build and deploy
gcloud run deploy cure-blend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

### 3.4 Azure App Service

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name cure-blend-rg --location eastus

# Create app service plan
az appservice plan create \
  --name cure-blend-plan \
  --resource-group cure-blend-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group cure-blend-rg \
  --plan cure-blend-plan \
  --name cure-blend-app \
  --runtime "PYTHON:3.10"

# Deploy
az webapp up \
  --name cure-blend-app \
  --resource-group cure-blend-rg
```

---

## 🔒 Security Considerations

### 1. Environment Variables

Create `.streamlit/secrets.toml` (local only, don't commit):
```toml
[azure]
api_key = "your-api-key"
endpoint = "your-endpoint"

[database]
connection_string = "your-db-connection"
```

Access in code:
```python
import streamlit as st
azure_key = st.secrets["azure"]["api_key"]
```

### 2. Update .gitignore

```
.streamlit/secrets.toml
.env
*.env
__pycache__/
*.pyc
.vscode/
.idea/
```

### 3. Rate Limiting

Add to streamlit_app.py:
```python
import streamlit as st
from datetime import datetime, timedelta

# Simple rate limiting
if 'last_request' not in st.session_state:
    st.session_state.last_request = datetime.now()

time_since_last = datetime.now() - st.session_state.last_request
if time_since_last < timedelta(seconds=1):
    st.warning("Please wait a moment before submitting again.")
    st.stop()

st.session_state.last_request = datetime.now()
```

---

## 📊 Monitoring & Maintenance

### 1. Application Monitoring

Add analytics to track usage:
```python
import streamlit as st

# Google Analytics (add to app)
GA_TRACKING_ID = "UA-XXXXXXXXX-X"
st.markdown(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_TRACKING_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_TRACKING_ID}');
    </script>
""", unsafe_allow_html=True)
```

### 2. Error Tracking

Use Sentry:
```bash
pip install sentry-sdk
```

```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### 3. Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("User submitted diagnosis request")
```

---

## 🔄 Continuous Deployment

### GitHub Actions (Auto-deploy on push)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          python test_core_functions.py
      
      - name: Deploy to Streamlit Cloud
        run: |
          echo "Streamlit Cloud will auto-deploy from this push"
```

---

## 🌐 Custom Domain Setup

### For Streamlit Cloud:

1. Go to app settings
2. Click "Custom domain"
3. Add your domain (e.g., cure-blend.yourdomain.com)
4. Update DNS records:
   ```
   Type: CNAME
   Name: cure-blend
   Value: your-app.streamlit.app
   ```

### For AWS/Other:

1. Get a domain from:
   - Namecheap
   - GoDaddy
   - Google Domains
   - AWS Route 53

2. Point DNS to your server IP

3. Setup SSL with Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 📈 Performance Optimization

### 1. Caching

Already implemented in your app! Verify these are present:

```python
@st.cache_data
def load_model():
    # Load ML model
    pass

@st.cache_resource
def load_data():
    # Load data
    pass
```

### 2. Compression

Add to `.streamlit/config.toml`:
```toml
[server]
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200

[browser]
gatherUsageStats = false
```

### 3. CDN (Optional)

For static assets, use Cloudflare:
1. Sign up at cloudflare.com
2. Add your domain
3. Enable caching rules

---

## 💰 Cost Estimation

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| **Streamlit Cloud** | ✅ Unlimited public apps | - | Small projects, portfolios |
| **Heroku** | ✅ 550 dyno hours/month | $7/month | Quick deployments |
| **AWS EC2** | ✅ 750 hours t2.micro (1 year) | ~$10-30/month | Full control |
| **Google Cloud Run** | ✅ 2M requests/month | Pay per use | Scalable apps |
| **Azure** | ✅ $200 credit (30 days) | ~$13-50/month | Enterprise |
| **Railway** | ✅ $5 credit/month | $5-20/month | Easy Docker deploy |

---

## 🎯 Quick Start (Recommended Path)

### For Immediate Public Deployment:

```bash
# 1. Ensure code is committed
git add .
git commit -m "Production ready"
git push origin main

# 2. Go to https://share.streamlit.io/
# 3. Click "New app"
# 4. Select your repo
# 5. Wait 2-3 minutes
# 6. Done! Your app is live
```

**Your app will be at:** `https://cure-blend.streamlit.app`

### For Private/Enterprise Deployment:

Use **AWS EC2** or **Azure App Service** with the systemd service setup above.

---

## 🆘 Troubleshooting

### Issue: App crashes on startup

**Solution:** Check if all data files are present:
```bash
ls -lh data/*.pkl data/*.csv
```

### Issue: Out of memory

**Solution:** Increase server resources or optimize caching:
```python
@st.cache_resource(ttl=3600)  # Cache for 1 hour
def load_large_model():
    # Your code
    pass
```

### Issue: Slow loading

**Solution:** 
1. Enable caching
2. Reduce data size
3. Use lazy loading

### Issue: Port already in use

**Solution:**
```bash
# Find process
lsof -ti:8501

# Kill it
kill -9 <PID>

# Or use different port
streamlit run streamlit_app.py --server.port=8502
```

---

## 📞 Support & Resources

- **Streamlit Docs:** https://docs.streamlit.io/
- **Streamlit Forum:** https://discuss.streamlit.io/
- **Streamlit Community Cloud:** https://share.streamlit.io/
- **Docker Hub:** https://hub.docker.com/
- **GitHub Actions:** https://github.com/features/actions

---

## ✅ Deployment Checklist

Before going live:

- [ ] All tests passing
- [ ] No console warnings
- [ ] Environment variables configured
- [ ] Data files included in deployment
- [ ] Error handling in place
- [ ] Rate limiting configured
- [ ] Monitoring setup
- [ ] Backup strategy
- [ ] Custom domain (optional)
- [ ] SSL certificate (if custom domain)
- [ ] Privacy policy (if collecting data)
- [ ] Terms of service

---

## 🚀 Next Steps

1. **Choose your deployment platform** (Streamlit Cloud recommended for quickest start)
2. **Follow the platform-specific steps** above
3. **Test thoroughly** in production
4. **Monitor usage** and performance
5. **Iterate** based on user feedback

---

**Your app is production-ready and tested!** Pick a deployment method and go live! 🎉

For most users, **Streamlit Community Cloud is the fastest way to deploy** - just push to GitHub and click deploy.
