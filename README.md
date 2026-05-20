# Materials Curve Dataset Platform

本项目用于开发一个面向材料科学曲线图的合成数据集 Web 平台，重点服务于钢铁材料蠕变曲线图像识别与智能解析任务。

平台目标不是单纯绘制曲线图，而是构建一个能够批量生成、预览、检查、标注和导出训练数据的数据集生产工具。

## 1. Project Background

本项目面向“材料科学图像曲线识别与智能解析”方向，以钢铁蠕变曲线作为切入点。

前期已经完成真实论文中钢铁蠕变曲线图的风格统计分析，统计内容包括：

- 曲线数量
- 坐标轴含义与单位
- 坐标轴类型
- 曲线形态
- marker 类型
- 曲线线型
- 图例位置
- 网格背景
- 坐标轴边框
- 子图形式
- 图像质量
- 是否适合标注
- 是否适合合成参考

本平台需要将这些统计结果转化为可配置、可采样、可批量生成的数据集生产流程。

## 2. Core Goals

平台需要实现以下核心目标：

1. 参数化生成钢铁蠕变曲线图。
2. 支持预设模板快速生成常见论文风格曲线图。
3. 支持显式指定模式，即用户手动指定曲线数量、坐标轴、图例、线型等参数。
4. 支持概率采样模式，即按照真实曲线风格统计分布自动采样生成。
5. 支持实时预览 3–6 张样图。
6. 支持预览每张图对应的标注数据。
7. 使用统一的 MCG-JSON 中间标注格式。
8. 支持通过导出适配器导出多种训练格式。
9. 支持数据集版本控制和随机种子复现。
10. 支持后续扩展到 YOLO、COCO、mask、OCR、polyline 等训练任务。

## 3. Main Features

### 3.1 Template System

平台应内置若干预设模板：

- 真实主流风格
- 多曲线对比风格
- 纯黑白论文风格
- 带 marker 风格
- 带网格干扰风格
- 低质量截图风格
- 完整三阶段蠕变风格

模板应以配置文件形式保存，例如：

```text
templates/
  real_mainstream.yaml
  multi_curve_comparison.yaml
  black_white_paper.yaml
  marker_rich.yaml
  grid_interference.yaml
  low_quality_screenshot.yaml
  three_stage_creep.yaml
```

### 3.2 Parameter Panel

参数面板不需要分基础模式和高级模式，但需要按照类别清晰排布。

建议分为以下类别：

#### A. 图像基础信息

- 图像尺寸
- DPI
- 图名
- 是否显示图名
- 图像质量
- 背景类型

#### B. 坐标轴设置

- x 轴含义
- x 轴单位
- y 轴含义
- y 轴单位
- 坐标轴类型：linear / log
- 坐标范围
- 坐标轴边框：左下坐标轴 / 完整四边框

#### C. 曲线设置

- 曲线条数
- 曲线形态
- 曲线点数
- 噪声强度
- 曲线间距
- 是否允许曲线交叉
- 是否允许曲线重叠

曲线形态包括：

- near_linear
- primary_obvious
- accelerated_obvious
- three_stage
- irregular

#### D. 曲线视觉风格

- 曲线颜色
- 曲线线型：solid / dashed / dotted / dashdot
- 曲线线宽
- marker 类型
- marker 大小
- marker 间隔

#### E. 图例设置

- 是否显示图例
- 图例位置
- 图例文字模板
- 图例是否带边框
- 图例字号

#### F. 背景与网格

- 是否显示网格
- 网格样式
- 网格透明度
- 网格线宽
- 是否模拟截图压缩
- 是否模拟轻微模糊
- 是否模拟低分辨率

#### G. 子图与论文风格

- 是否生成子图
- 子图编号
- 子图编号位置
- 是否裁剪成论文截图风格
- 是否加入留白变化

### 3.3 Generation Modes

平台需要支持两种生成模式。

#### Explicit Mode

显式指定模式。

用户手动指定参数，例如：

- 曲线条数：3
- x 轴：Creep time / h
- y 轴：Creep strain / %
- 图例：inside_upper_right
- 线型：solid
- marker：none
- 网格：false
- 曲线形态：near_linear

适合调试单一风格、生成展示图、小规模测试样本。

#### Probabilistic Mode

概率采样模式。

用户通过配置概率分布来控制批量生成，例如：

```yaml
axis_type:
  linear: 0.88
  log: 0.12

num_curves:
  1: 0.04
  2: 0.22
  3: 0.25
  4: 0.27
  5: 0.12
  6: 0.09
  8: 0.01

line_style:
  solid: 0.88
  dashed: 0.10
  other: 0.02
```

适合正式批量生成训练集。

### 3.4 Preview Generation

预览生成用于快速查看当前参数效果。

要求：

- 一次生成 3–6 张样图。
- 速度优先。
- 可使用较低分辨率。
- 每张预览图都要能查看对应的 MCG-JSON 标注。
- 支持切换显示标注叠加效果。

预览阶段不需要生成所有正式导出文件。

### 3.5 Formal Dataset Export

正式导出用于生成可训练的数据集。

要求：

- 支持批量生成。
- 支持设置生成数量。
- 支持设置 train / val / test 划分比例。
- 支持设置随机种子。
- 支持保存完整配置。
- 支持生成数据集版本目录。
- 支持输出统计报告。
- 支持打包下载。

### 3.6 Annotation Preview

每张图应支持查看以下内容：

- 原图
- bbox overlay
- mask overlay
- polyline overlay
- data points
- plot area
- axis information
- legend information
- text boxes
- MCG-JSON 原文

### 3.7 Export Adapters

平台内部使用统一的 MCG-JSON 中间格式，然后通过导出适配器转换为不同训练格式。

需要逐步支持：

- CSV + MCG-JSON
- YOLO Detection
- COCO Detection
- COCO Segmentation
- Mask PNG
- OCR JSON
- Polyline / Keypoint JSON
- Data Recovery Format

## 4. MCG-JSON Internal Annotation Format

MCG-JSON 是平台内部统一标注格式，全称为：

Materials Curve Graph JSON

每张生成图像都必须对应一个 MCG-JSON 文件。

示例结构：

```json
{
  "dataset_info": {
    "dataset_id": "creep_synth_v0.1",
    "sample_id": "creep_000001",
    "generator_version": "0.1.0",
    "seed": 20260520,
    "created_at": "2026-05-20T12:00:00"
  },
  "image": {
    "file_name": "creep_000001.png",
    "width": 1024,
    "height": 768,
    "dpi": 150,
    "quality_level": "high"
  },
  "plot_area": {
    "bbox_xyxy": [120, 80, 900, 650],
    "bbox_xywh": [120, 80, 780, 570]
  },
  "axis": {
    "x": {
      "label": "Creep time",
      "unit": "h",
      "scale": "linear",
      "range": [0, 1000],
      "tick_values": [0, 200, 400, 600, 800, 1000],
      "tick_bboxes": []
    },
    "y": {
      "label": "Creep strain",
      "unit": "%",
      "scale": "linear",
      "range": [0, 3.5],
      "tick_values": [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
      "tick_bboxes": []
    }
  },
  "style": {
    "template": "real_mainstream",
    "num_curves": 3,
    "legend_position": "inside_upper_right",
    "grid": false,
    "axis_frame": "left_bottom"
  },
  "legend": {
    "visible": true,
    "bbox_xyxy": [650, 110, 880, 210],
    "items": [
      {
        "curve_id": "curve_1",
        "text": "650°C / 120 MPa",
        "text_bbox": [700, 120, 860, 145],
        "symbol_bbox": [660, 125, 690, 135]
      }
    ]
  },
  "curves": [
    {
      "curve_id": "curve_1",
      "label": "650°C / 120 MPa",
      "shape_type": "near_linear",
      "line_color": "#1f77b4",
      "line_style": "solid",
      "line_width": 1.5,
      "marker": "none",
      "data_points": [[0, 0.12], [10, 0.14]],
      "pixel_points": [[126, 543], [134, 539]],
      "bbox_xyxy": [126, 240, 850, 543],
      "mask_path": "masks/creep_000001_curve_1.png",
      "csv_path": "csv/creep_000001_curve_1.csv"
    }
  ],
  "quality_check": {
    "passed": true,
    "warnings": []
  }
}
```

## 5. Dataset Versioning

每次正式导出数据集时，必须生成独立版本目录。

推荐结构：

```text
datasets/
  creep_synth_v0.1_20260520_001/
    images/
    annotations/
    csv/
    masks/
    exports/
      yolo/
      coco_detection/
      coco_segmentation/
      ocr/
      polyline/
    config.yaml
    distribution.yaml
    seed.json
    summary.json
    quality_report.json
    README.md
```

必须保存：

- 数据集名称
- 数据集版本号
- 生成时间
- 生成数量
- 使用模板
- 全部参数配置
- 概率分布配置
- 随机种子
- 生成器版本号
- 导出格式
- 样本统计摘要
- 质量检查结果

## 6. Quality Check

批量生成时必须进行质量检查。

检查项包括：

- 曲线是否超出 plot area
- 曲线 bbox 是否为空
- 曲线是否过度重叠
- 图例是否遮挡主要曲线
- 坐标轴标签是否超出画布
- tick label 是否重叠严重
- mask 是否为空
- pixel_points 是否和 data_points 数量一致
- 是否存在 NaN / inf
- 图像是否成功保存

不合格样本应被标记或自动重新生成。

## 7. Suggested Tech Stack

- Frontend: React + Vite + TypeScript
- Backend: FastAPI
- Generator: Python + NumPy + Matplotlib + Pillow
- Image processing: OpenCV, Pillow
- Config: YAML / JSON
- Storage: local filesystem first, SQLite optional
- Dataset export: ZIP package

## 8. Suggested Directory Structure

```text
materials-curve-dataset-platform/
├─ README.md
├─ AGENTS.md
├─ frontend/
├─ backend/
├─ generator/
├─ templates/
├─ docs/
├─ examples/
├─ datasets/
└─ tests/
```

## 9. Development Roadmap

### V0: Minimum Usable Platform

V0 should implement:

- Basic project structure
- FastAPI backend
- React frontend
- Template selection
- Parameter panel
- Explicit mode
- Preview generation of 3–6 images
- Basic MCG-JSON annotation
- Export PNG + CSV + MCG-JSON
- Save seed and config

V0 does not need:

- YOLO exporter
- COCO exporter
- mask generation
- OCR exporter
- complex degradation
- history management

### V1: Training Dataset Version

V1 should implement:

- Probabilistic mode
- Batch generation
- Dataset version directory
- train / val / test split
- YOLO exporter
- COCO detection exporter
- Mask PNG exporter
- Quality check

### V2: Research Enhanced Version

V2 should implement:

- COCO segmentation
- OCR exporter
- Polyline exporter
- subplot generation
- image degradation
- dataset history page
- distribution comparison report

## 10. Local Development

This section should be updated as the project is implemented.

Expected commands:

```bash
# backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# frontend
cd frontend
npm install
npm run dev
```

## 11. License

This project is for academic research and SRTP project development.

## 12. V0 Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173` in your browser.
