# V0 运行与验收说明

## 1. 安装依赖

### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Frontend
```bash
cd frontend
npm install
cd ..
```

## 2. 启动服务

### 启动 backend
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 启动 frontend
```bash
cd frontend
npm run dev
```
默认前端访问：`http://127.0.0.1:5173`

## 3. 核心接口验收

### GET /health
```bash
curl http://127.0.0.1:8000/health
```

### GET /templates
```bash
curl http://127.0.0.1:8000/templates
```

### POST /preview（explicit）
```bash
curl -X POST http://127.0.0.1:8000/preview \
  -H 'Content-Type: application/json' \
  -d '{"mode":"explicit","template_id":"real_mainstream","preview_count":3,"seed":20260520}'
```

### POST /preview（probabilistic）
```bash
curl -X POST http://127.0.0.1:8000/preview \
  -H 'Content-Type: application/json' \
  -d '{"mode":"probabilistic","template_id":"real_mainstream","preview_count":6,"seed":20260520}'
```

### POST /generate（total_count=6）
```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "dataset_name":"creep_synth",
    "version":"v0.1",
    "total_count":6,
    "mode":"probabilistic",
    "template_id":"real_mainstream",
    "seed":20260520,
    "split":{"train":0.7,"val":0.2,"test":0.1}
  }'
```

## 4. 输出路径

### 预览输出
- `examples/previews/images/`
- `examples/previews/csv/`
- `examples/previews/annotations/`

### 批量数据集输出
- `datasets/{dataset_id}/images/train|val|test`
- `datasets/{dataset_id}/annotations/train|val|test`
- `datasets/{dataset_id}/csv/train|val|test`
- `datasets/{dataset_id}/config.yaml`
- `datasets/{dataset_id}/distribution.yaml`
- `datasets/{dataset_id}/seed.json`
- `datasets/{dataset_id}/summary.json`
- `datasets/{dataset_id}/quality_report.json`
- `datasets/{dataset_id}/README.md`

## 5. 前端验收要点

- 模板列表可加载（`GET /templates`）。
- 可切换 `explicit/probabilistic`。
- 可触发 `/preview` 并显示 `image_path/annotation_path/csv_paths`。
- 可触发 `/generate` 并显示数据集结果。
- loading 与错误信息可见。

## 6. 一键烟雾测试脚本

```bash
python scripts/v0_smoke_test.py
```

脚本检查：
- preview explicit/probabilistic 可用；
- generate total_count=6 可用；
- 关键目录和文件存在；
- 同 seed 采样一致、不同 seed 有变化。

## 7. 常见问题

1. **backend 启动时报目录不存在**
   - 当前实现会自动创建 `examples/previews/*` 与 `datasets/`，无需手动建目录。
2. **前端请求失败**
   - 检查 backend 是否运行在 `127.0.0.1:8000`。
3. **split 报错**
   - `train+val+test` 必须等于 `1.0`。
4. **模板不存在**
   - 使用 `GET /templates` 查看可用 `template_id`。
