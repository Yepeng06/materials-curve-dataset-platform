# V0 运行说明（第二步）

## 1) 启动 backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
uvicorn backend.main:app --reload --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

预览接口：

```bash
curl -X POST http://127.0.0.1:8000/preview \
  -H 'Content-Type: application/json' \
  -d '{"preview_count":3,"num_curves":3,"curve_shape":"near_linear","seed":20260520}'
```

## 2) 启动 frontend (React + Vite + TypeScript)

```bash
cd frontend
npm install
npm run dev
```

默认访问：

- http://127.0.0.1:5173

点击首页按钮“生成 3 张预览图”会调用后端 `/preview` 并展示图片与 MCG-JSON。

## 3) 预览输出位置

- PNG: `examples/previews/images/`
- CSV: `examples/previews/csv/`
- MCG-JSON: `examples/previews/annotations/`
