# V0 运行说明（第三步）

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

## 2) 启动 frontend (React + Vite + TypeScript)

```bash
cd frontend
npm install
npm run dev
```

默认访问：

- http://127.0.0.1:5173

## 3) 前端参数面板使用

首页新增 5 组参数面板：

- A. 图像与预览设置：`preview_count`、`seed`、`grid`
- B. 坐标轴设置：`x_label`、`x_unit`、`y_label`、`y_unit`（下拉+可自定义）
- C. 曲线设置：`num_curves`、`curve_shape`、`points_per_curve`、`noise_level`
- D. 曲线视觉风格：`line_style`、`line_width`、`marker`
- E. 图例设置：`legend_position`

调参后点击“生成预览图”按钮，前端会将参数通过 `POST /preview` 发送到后端，页面会显示 3–6 张预览图、路径信息和可展开的 MCG-JSON。

## 4) /preview 请求字段

`POST /preview` 当前支持字段：

- `preview_count` (3-6)
- `seed`
- `grid`
- `x_label`, `x_unit`, `y_label`, `y_unit`
- `num_curves` (1-4)
- `curve_shape` (`near_linear` / `primary_obvious` / `accelerated_obvious`)
- `points_per_curve` (50-500)
- `noise_level` (0-0.1)
- `line_style` (`solid` / `dashed` / `dotted` / `dashdot`)
- `line_width` (0.5-4)
- `marker` (`none` / `triangle` / `circle` / `square`)
- `legend_position` (`none` / `inside_upper_right` / `inside_upper_left` / `inside_lower_right` / `outside_right`)

示例：

```bash
curl -X POST http://127.0.0.1:8000/preview \
  -H 'Content-Type: application/json' \
  -d '{
    "preview_count":4,
    "seed":20260520,
    "grid":true,
    "x_label":"Time",
    "x_unit":"hr",
    "y_label":"Strain",
    "y_unit":"%",
    "num_curves":2,
    "curve_shape":"accelerated_obvious",
    "points_per_curve":220,
    "noise_level":0.01,
    "line_style":"dashdot",
    "line_width":2.2,
    "marker":"circle",
    "legend_position":"outside_right"
  }'
```

## 5) 预览输出位置

- PNG: `examples/previews/images/`
- CSV: `examples/previews/csv/`
- MCG-JSON: `examples/previews/annotations/`
