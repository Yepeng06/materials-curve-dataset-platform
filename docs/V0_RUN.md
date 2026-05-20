# V0 运行说明（第四步：模板系统与概率采样）

## 1) 启动 backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
uvicorn backend.main:app --reload --port 8000
```

## 2) 启动 frontend

```bash
cd frontend
npm install
npm run dev
```

## 3) 模板选择与模式说明

- 模板文件目录：`templates/`
- 前端会在页面加载时调用 `GET /templates` 并填充模板下拉框。
- 生成模式：
  - `explicit`：使用前端手动参数（兼容旧模式）。
  - `probabilistic`：根据模板 `probability_distributions` 采样；部分手动参数会被模板采样覆盖。

## 4) GET /templates

返回格式：

```json
{
  "status": "ok",
  "count": 7,
  "items": [
    {
      "template_id": "real_mainstream",
      "template_name": "Real Mainstream",
      "description": "Mainstream paper-like creep chart style.",
      "file_name": "real_mainstream.yaml"
    }
  ]
}
```

## 5) POST /preview 新字段

新增请求字段：

- `mode`: `explicit` | `probabilistic`（默认 `explicit`）
- `template_id`: 模板 ID（默认 `real_mainstream`）

### explicit 示例

```bash
curl -X POST http://127.0.0.1:8000/preview \
  -H 'Content-Type: application/json' \
  -d '{
    "mode":"explicit",
    "template_id":"real_mainstream",
    "preview_count":3,
    "num_curves":3,
    "curve_shape":"near_linear",
    "seed":20260520
  }'
```

### probabilistic 示例

```bash
curl -X POST http://127.0.0.1:8000/preview \
  -H 'Content-Type: application/json' \
  -d '{
    "mode":"probabilistic",
    "template_id":"real_mainstream",
    "preview_count":6,
    "seed":20260520
  }'
```

## 6) MCG-JSON 追踪字段

每张预览图的 MCG-JSON 中会记录：

- `mode`
- `template_id`
- `template_name`
- `seed`
- `sampled_parameters`
- `actual_parameters`

用于追踪每张图实际生成参数与复现。
