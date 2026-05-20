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

## 7) POST /generate（批量生成）

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "dataset_name": "creep_synth",
    "version": "v0.1",
    "total_count": 6,
    "mode": "probabilistic",
    "template_id": "real_mainstream",
    "seed": 20260520,
    "split": {"train": 0.7, "val": 0.2, "test": 0.1}
  }'
```

返回示例：

```json
{
  "status": "ok",
  "dataset_id": "creep_synth_v0.1_20260520_001",
  "dataset_path": "datasets/creep_synth_v0.1_20260520_001",
  "total_count": 6,
  "split_counts": {"train": 4, "val": 1, "test": 1},
  "summary_path": "datasets/creep_synth_v0.1_20260520_001/summary.json",
  "quality_report_path": "datasets/creep_synth_v0.1_20260520_001/quality_report.json"
}
```

## 8) 数据集版本目录结构

```text
datasets/{dataset_name}_{version}_{YYYYMMDD}_{seq}/
  images/train|val|test/
  annotations/train|val|test/
  csv/train|val|test/
  config.yaml
  distribution.yaml
  seed.json
  summary.json
  quality_report.json
  README.md
```

文件作用：

- `config.yaml`：保存本次请求参数。
- `distribution.yaml`：保存模板概率分布和模式。
- `seed.json`：保存全局种子和每个 sample_id 的 sample_seed。
- `summary.json`：保存总量、split 数量、模式与分布统计。
- `quality_report.json`：保存通过/警告/失败统计与样本 warning。

## 9) 前端批量生成区域

- 页面新增“批量生成数据集”区域。
- 参数：`dataset_name`、`version`、`total_count`、`mode`、`template_id`、`seed`、`train/val/test ratio`。
- 点击按钮后调用 `POST /generate`，返回数据集 ID、路径、split 统计与摘要文件路径。
