# ⚡ Quick Setup Reference

**For detailed instructions, see [SETUP.md](SETUP.md)**

---

## 🚀 Minimal Setup (5 minutes)

```bash
# 1. Clone
git clone https://github.com/hermee/chem-agent.git
cd chem-agent

# 2. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Setup Python
uv sync

# 4. Setup Frontend
cd src/frontend/reactome-ui && npm install && cd ../../..

# 5. Configure AWS
cp .env.example .env
# Edit .env with your AWS credentials

# 6. Run
./run.sh
```

**Access:** http://localhost:4200

---

## 📦 Required Software

| Software | Version | Install |
|----------|---------|---------|
| Python | 3.12+ | `apt install python3.12` |
| Node.js | 18+ | `curl -fsSL https://deb.nodesource.com/setup_18.x \| bash -` |
| UV | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Rust | 1.83+ | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |

---

## 🔑 AWS Setup

```bash
# Configure credentials
aws configure
# Region: us-west-2

# Verify
aws sts get-caller-identity
```

---

## 🐛 Common Issues

**Port in use:**
```bash
sudo lsof -i :8000  # or :4200
sudo kill -9 <PID>
```

**RDKit import error:**
```bash
uv sync --reinstall-package rdkit
```

**Node modules error:**
```bash
cd src/frontend/reactome-ui
rm -rf node_modules && npm install
```

---

## 📍 Ports

- **8000** - Backend API
- **4200** - Frontend UI
- **8001** - Standalone WASM (optional)

---

## 🔗 Links

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health
- Full Setup Guide: [SETUP.md](SETUP.md)
