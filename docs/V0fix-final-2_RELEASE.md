# V0fix-final-2 版本说明

## 版本定位
V0fix-final-2 是当前项目的 **V0 阶段稳定演示版**，用于生成材料科学曲线合成数据集，并输出配套 `PNG / CSV / MCG-JSON` 标注文件。该版本重点满足 SRTP 中期检查展示、流程演示、结果复现与后续交接开发需求。

## 当前已实现功能
- 中文化网页 UI（参数分组、按钮文案、提示信息）
- 模板选择与模板默认参数应用
- `explicit` 显式模式
- `probabilistic` 概率采样模式
- 曲线参数设置（曲线数量、形态、点数、噪声等）
- 样式参数设置（线型、线宽、marker、图例位置等）
- 坐标轴参数设置（标签、单位、范围、网格等）
- 预览图生成（`/preview`）
- 批量数据集生成（`/generate`）
- `PNG / CSV / MCG-JSON` 输出
- 多曲线追踪字段：`curve_index / total_curves`
- 版本追踪字段：`generator_version / dataset_version`
- `pytest` + smoke test 基础验证

## 当前不包含的功能（V1 及以后）
以下功能 **未包含在 V0fix-final-2**，属于后续 V1+ 规划：
- YOLO 标注导出
- COCO 标注导出
- mask 生成
- OCR
- 自动识别真实论文图像
- 深度学习模型训练

## 使用方法

### 1) 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2) 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 3) 如何生成预览
- 打开前端页面后，选择模板与生成模式。
- 设置参数后点击“生成预览”。
- 系统调用 `/preview`，返回 3–6 张样图及对应 MCG-JSON。

### 4) 如何生成数据集
- 在批量生成区域填写 `dataset_name / version / total_count / split / seed`。
- 点击生成后调用 `/generate`。
- 后端按设置写出数据集目录与摘要信息。

### 5) 输出目录位置
- 预览输出：`examples/previews/`
- 正式数据集输出：`datasets/<dataset_name>_<version>_<timestamp>/`

### 6) 如何查看 annotation / CSV
- `annotations/` 下为每张图对应的 MCG-JSON。
- `csv/` 下为每条曲线数据点（每曲线一个 CSV）。

## 参数说明（中文）
- `mode`：生成模式，`explicit`（手动）或 `probabilistic`（按分布采样）。
- `template`：模板标识（如 `real_mainstream`），用于提供默认参数与概率分布。
- `preview_count`：预览张数，当前约束在 3–6。
- `seed`：随机种子；相同配置+种子可复现。
- `num_curves`：单图曲线条数。
- `curve_shape`：曲线形态（near_linear / primary_obvious / accelerated_obvious / three_stage / irregular）。
- `points_per_curve`：每条曲线采样点数量。
- `noise_level`：曲线噪声幅度。
- `line_style`：线型（如 solid / dashed）。
- `line_width`：线宽。
- `marker`：点标记类型。
- `legend_position`：图例位置。
- `grid`：是否显示网格。
- `x_label / y_label`：坐标轴名称。
- `x_range`：x 轴数据范围。
- `dataset_name`：数据集名称。
- `total_count`：正式生成样本总数。
- `split`：训练/验证/测试划分比例（如 train/val/test）。

## 输出文件说明
正式数据集目录中重点包含：
- `images/`：生成图像（PNG）
- `csv/`：曲线原始数据点
- `annotations/`：MCG-JSON 标注

MCG-JSON 顶层字段包括：
- `dataset_info`
- `image`
- `plot_area`
- `axis`
- `style`
- `legend`
- `curves`
- `quality_check`

`curves` 内字段说明（节选）：
- `curve_index`：该曲线在当前图内的序号（从 0 开始）。
- `total_curves`：该图总曲线数，用于多曲线还原与对齐。

## 测试方法
在仓库根目录执行：
```bash
pytest
python scripts/v0_smoke_test.py
cd frontend && npm run build
```

## 已知限制
- 当前 UI 已中文化，但模板 `description` 文本可能仍来自英文模板内容。
- 当前只生成合成曲线数据，不做真实论文图像自动识别。
- 当前版本主要服务 V0 生成与演示，不是完整训练平台。
