# 🚀 Remote Server Setup Guide

Complete setup instructions for deploying the Reactome LNP Agent on a fresh remote server.

---

## 📋 Prerequisites

- Ubuntu 20.04+ / Amazon Linux 2023+ / macOS
- Sudo access
- AWS credentials with Bedrock access (us-west-2)

---

## 1️⃣ System Dependencies

### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Rust (for Dioxus apps)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# Install build tools
sudo apt install -y build-essential pkg-config libssl-dev
```

### Amazon Linux 2023
```bash
# Install Python 3.12
sudo dnf install -y python3.12 python3.12-pip python3.12-devel

# Install Node.js
sudo dnf install -y nodejs npm

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# Install build tools
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y openssl-devel
```

### macOS
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.12 node rust
```

---

## 2️⃣ Install UV (Python Package Manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env  # or restart shell
```

---

## 3️⃣ Clone Repository

```bash
git clone https://github.com/hermee/chem-agent.git
cd chem-agent
```

---

## 4️⃣ Backend Setup

### Install Python Dependencies
```bash
# Create virtual environment and install packages
uv sync
```

### Configure AWS Credentials
```bash
# Option 1: AWS CLI (recommended)
aws configure
# Enter your AWS Access Key ID, Secret Key, and set region to us-west-2

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_here
export AWS_REGION=us-west-2
```

### Create Environment File
```bash
cat > .env << 'EOF'
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_FAST_MODEL_ID=us.anthropic.claude-3-5-haiku-20241022-v1:0
DEBUG=true
PORT=8000
EOF
```

### Verify Backend
```bash
# Activate virtual environment
source .venv/bin/activate

# Test import
python -c "import rdkit; print('RDKit OK')"

# Start backend (test)
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000
# Press Ctrl+C to stop
```

---

## 5️⃣ Frontend Setup

### Install Angular Dependencies
```bash
cd src/frontend/reactome-ui
npm install
cd ../../..
```

### Verify Frontend
```bash
cd src/frontend/reactome-ui
ng serve --host 0.0.0.0 --port 4200
# Press Ctrl+C to stop
cd ../../..
```

---

## 6️⃣ Standalone Apps (Optional)

### WASM Standalone (Molecular Analysis)

#### Install Trunk
```bash
cargo install trunk wasm-bindgen-cli
rustup target add wasm32-unknown-unknown
```

#### Build
```bash
cd src/standalone
trunk build --release
cd ../..
```

#### Serve
```bash
cd src/standalone
python serve.py  # http://localhost:8001
cd ../..
```

### Desktop App (Full Application)

#### Build
```bash
cd src/standalone-desktop
cargo build --release
cd ../..
```

#### Run
```bash
# Requires backend on port 8000 and frontend on port 4200
./src/standalone-desktop/target/release/lnp-desktop
```

---

## 7️⃣ Running the Application

### Quick Start (Both Services)
```bash
./run.sh
```

### Manual Start

#### Terminal 1 - Backend
```bash
source .venv/bin/activate
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2 - Frontend
```bash
cd src/frontend/reactome-ui
ng serve --host 0.0.0.0 --port 4200
```

### Access
- **Web UI:** http://localhost:4200
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

---

## 8️⃣ Firewall Configuration

### AWS Security Group
```bash
# Allow inbound traffic
# Port 8000 (Backend API)
# Port 4200 (Frontend)
# Port 8001 (Standalone WASM - optional)
```

### UFW (Ubuntu)
```bash
sudo ufw allow 8000/tcp
sudo ufw allow 4200/tcp
sudo ufw allow 8001/tcp  # optional
```

---

## 9️⃣ Production Deployment

### Using systemd (Backend)

Create `/etc/systemd/system/lnp-backend.service`:
```ini
[Unit]
Description=LNP Agent Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/chem-agent
Environment="PATH=/home/ubuntu/chem-agent/.venv/bin:/usr/bin"
ExecStart=/home/ubuntu/chem-agent/.venv/bin/uvicorn src.backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable lnp-backend
sudo systemctl start lnp-backend
sudo systemctl status lnp-backend
```

### Using systemd (Frontend)

Create `/etc/systemd/system/lnp-frontend.service`:
```ini
[Unit]
Description=LNP Agent Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/chem-agent/src/frontend/reactome-ui
ExecStart=/usr/bin/ng serve --host 0.0.0.0 --port 4200
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable lnp-frontend
sudo systemctl start lnp-frontend
sudo systemctl status lnp-frontend
```

### Using Nginx (Reverse Proxy)

Install Nginx:
```bash
sudo apt install -y nginx
```

Create `/etc/nginx/sites-available/lnp-agent`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:4200;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/lnp-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔍 Troubleshooting

### Backend Issues

**Import Error: RDKit**
```bash
# Reinstall with uv
uv sync --reinstall-package rdkit
```

**AWS Credentials Not Found**
```bash
# Check credentials
aws sts get-caller-identity

# Verify region
echo $AWS_REGION
```

**Port Already in Use**
```bash
# Find process using port 8000
sudo lsof -i :8000
# Kill process
sudo kill -9 <PID>
```

### Frontend Issues

**Node Modules Error**
```bash
cd src/frontend/reactome-ui
rm -rf node_modules package-lock.json
npm install
```

**Angular CLI Not Found**
```bash
npm install -g @angular/cli
```

### Rust/Dioxus Issues

**Trunk Not Found**
```bash
cargo install trunk wasm-bindgen-cli
```

**WASM Target Missing**
```bash
rustup target add wasm32-unknown-unknown
```

---

## 📊 Verify Installation

Run all checks:
```bash
# Python
python3.12 --version

# UV
uv --version

# Node.js
node --version
npm --version

# Rust
rustc --version
cargo --version

# Angular CLI
ng version

# AWS CLI
aws --version
aws sts get-caller-identity
```

---

## 🔐 Security Notes

- Never commit `.env` file (already in `.gitignore`)
- Use IAM roles on EC2 instead of access keys when possible
- Restrict security group rules to specific IPs in production
- Use HTTPS with SSL certificates (Let's Encrypt) for production

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **Technical Summary:** `docs/technical_summary_v1.pdf`
- **Desktop App README:** `src/standalone-desktop/README.md`
- **Main README:** `README.md`

---

## 🆘 Support

For issues, check:
1. Backend logs: `tail -f app.log`
2. Frontend logs: `tail -f frontend.log`
3. System logs: `journalctl -u lnp-backend -f`

---

**Last Updated:** 2026-02-13
