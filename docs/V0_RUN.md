# V0 运行说明（第二步：预览生成）

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

预览接口测试：

```bash
curl -X POST http://127.0.0.1:8000/preview \
  -H "Content-Type: application/json" \
  -d '{
    "preview_count": 3,
    "num_curves": 3,
    "curve_shape": "near_linear",
    "x_label": "Creep time",
    "x_unit": "h",
    "y_label": "Creep strain",
    "y_unit": "%",
    "legend_position": "inside_upper_right",
    "grid": false,
    "seed": 20260520
  }'
```

## 2) 启动 frontend (React + Vite + TypeScript)

```bash
cd frontend
npm install
npm run dev
```

默认访问：

- http://127.0.0.1:5173

## 3) 预览输出文件位置

- PNG 图像：`examples/previews/images/`
- CSV 文件：`examples/previews/csv/`
- MCG-JSON 标注：`examples/previews/annotations/`
