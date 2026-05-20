# V0 运行说明

## 1) 启动 backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

## 2) 启动 frontend (React + Vite + TypeScript)

```bash
cd frontend
npm install
npm run dev
```

默认访问：

- http://127.0.0.1:5173
