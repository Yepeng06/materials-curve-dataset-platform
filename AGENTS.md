# AGENTS.md

This file provides instructions for AI coding agents working on this repository.

## 1. Project Goal

Build a web platform for generating synthetic materials science curve chart datasets, especially steel creep curve charts.

The platform should support:

- Parameterized curve chart generation
- Template-based generation
- Explicit parameter mode
- Probabilistic sampling mode
- Preview generation
- Annotation preview
- Dataset export
- Reproducible dataset versioning
- Export adapters for model training formats

The platform is part of an SRTP project related to materials science image curve recognition and intelligent analysis.

## 2. Core Principle

This project is not just a plotting tool.

It is a dataset generation and annotation management platform.

Every generated image must have corresponding structured annotation data.

The internal annotation format is MCG-JSON.

All exporters should convert from MCG-JSON rather than directly from the plotting code.

## 3. Tech Stack

Use the following stack unless the user explicitly changes it:

- Frontend: React + Vite + TypeScript
- Backend: FastAPI
- Generator: Python, NumPy, Matplotlib, Pillow
- Image processing: Pillow and OpenCV
- Config files: YAML and JSON
- Storage: local filesystem first
- Optional database: SQLite

Avoid introducing heavy dependencies unless necessary.

## 4. Repository Structure

Expected structure:

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

Directory purposes:

- `frontend/`: React web interface.
- `backend/`: FastAPI server and API routes.
- `generator/`: curve generation, rendering, annotation, quality check, and export logic.
- `templates/`: YAML templates for generation styles.
- `docs/`: requirement documents and design notes.
- `examples/`: sample generated outputs.
- `datasets/`: generated dataset versions. Do not commit large datasets unless explicitly requested.
- `tests/`: unit and integration tests.

## 5. Required Modules

The generator should eventually include these modules:

```text
generator/
├─ curve_models.py
├─ style_models.py
├─ sampler.py
├─ renderer.py
├─ annotation_schema.py
├─ annotation_exporter.py
├─ quality_check.py
├─ degradation.py
└─ utils.py
```

Module responsibilities:

### curve_models.py

Generate numerical curve data.

Required curve types:

- near_linear
- primary_obvious
- accelerated_obvious
- three_stage
- irregular

### style_models.py

Define chart visual style options.

Examples:

- line style
- marker
- legend position
- grid
- axis frame
- image quality
- subplot option

### sampler.py

Handle parameter sampling.

Must support:

- explicit mode
- probabilistic mode
- random seed

### renderer.py

Render charts using Matplotlib.

Must return:

- image file
- plot area bbox
- pixel coordinates of curves
- text bbox if available
- curve bbox if available

### annotation_schema.py

Define MCG-JSON schema.

This should be the single source of truth for internal annotation.

### annotation_exporter.py

Export MCG-JSON to external formats.

Planned exporters:

- CSV + MCG-JSON
- YOLO Detection
- COCO Detection
- COCO Segmentation
- Mask PNG
- OCR JSON
- Polyline / Keypoint JSON
- Data Recovery Format

### quality_check.py

Check whether generated samples are valid.

Required checks:

- curve inside plot area
- non-empty bbox
- non-empty mask if mask is generated
- no NaN or inf
- pixel_points and data_points length match
- labels not outside canvas
- serious tick overlap warning
- legend overlap warning

### degradation.py

Add optional visual degradation.

Examples:

- JPEG compression
- blur
- low resolution
- gray background
- grayscale conversion
- screenshot-like degradation

## 6. Frontend Requirements

The frontend should provide at least these pages:

### Home Page

Show project overview and recent datasets.

### Parameter and Preview Page

Main page.

Should include:

- template selector
- generation mode selector
- parameter panel
- preview generation button
- 3–6 preview images
- MCG-JSON preview for each image

Parameters should be grouped clearly:

1. 图像基础信息
2. 坐标轴设置
3. 曲线设置
4. 曲线视觉风格
5. 图例设置
6. 背景与网格
7. 子图与论文风格

Do not implement a separate basic/advanced/expert mode unless explicitly requested.

### Annotation Preview Page

Should show:

- original image
- bbox overlay
- polyline overlay
- mask overlay if available
- plot area overlay
- legend overlay
- axis/text overlay
- raw MCG-JSON

### Batch Generation and Export Page

Should support:

- generation quantity
- generation mode
- train/val/test split
- export format selection
- dataset name
- version
- seed
- formal generation

### Dataset History Page

Should show previous dataset versions.

Each dataset should include:

- dataset name
- version
- created time
- sample count
- template
- config
- summary
- download link if available

## 7. Generation Modes

The platform must support two generation modes.

### Explicit Mode

All parameters are directly specified by the user.

Use this for preview, debugging, and controlled generation.

### Probabilistic Mode

Parameters are sampled from distributions.

Use this for formal dataset generation.

The distribution config should be editable and savable.

Example:

```yaml
axis_type:
  linear: 0.88
  log: 0.12

line_style:
  solid: 0.88
  dashed: 0.10
  other: 0.02
```

## 8. Templates

Templates should be stored as YAML files under `templates/`.

Required default templates:

```text
real_mainstream.yaml
multi_curve_comparison.yaml
black_white_paper.yaml
marker_rich.yaml
grid_interference.yaml
low_quality_screenshot.yaml
three_stage_creep.yaml
```

Templates should be readable and editable by humans.

## 9. MCG-JSON Requirements

Every generated image must have one MCG-JSON annotation.

Minimum required fields:

- dataset_info
- image
- plot_area
- axis
- style
- legend
- curves
- quality_check

Each curve must include:

- curve_id
- label
- shape_type
- line_color
- line_style
- line_width
- marker
- data_points
- pixel_points
- bbox
- mask_path if available
- csv_path if available

The schema should remain stable.

If schema changes are needed, update documentation and version number.

## 10. Dataset Versioning

Every formal export must create a dataset version directory.

Required structure:

```text
datasets/
  dataset_name_version_timestamp/
    images/
    annotations/
    csv/
    masks/
    exports/
    config.yaml
    distribution.yaml
    seed.json
    summary.json
    quality_report.json
    README.md
```

Each formal export must preserve:

- dataset name
- dataset version
- created time
- generator version
- config
- distribution
- random seed
- sample count
- export formats
- quality report

Generation must be reproducible when the same config and seed are used.

## 11. Development Rules

Follow these rules:

1. Keep code modular.
2. Do not hard-code absolute paths.
3. Do not store secrets or API keys.
4. Do not introduce unrelated features.
5. Do not modify unrelated files.
6. Use type hints in Python when practical.
7. Use clear names for functions and files.
8. Keep functions reasonably small.
9. Add short comments for non-obvious logic.
10. Preserve reproducibility with random seeds.
11. Avoid over-engineering.
12. Prefer readable implementation over clever implementation.

## 12. API Requirements

Backend should eventually expose these API endpoints:

```text
GET  /health
GET  /templates
POST /preview
POST /generate
GET  /datasets
GET  /datasets/{dataset_id}
GET  /datasets/{dataset_id}/download
POST /export
```

### /preview

Input:

- template
- mode
- parameters
- distribution if probabilistic
- preview_count
- seed

Output:

- preview image paths or base64 images
- MCG-JSON annotations
- summary

### /generate

Input:

- dataset name
- version
- generation quantity
- template
- mode
- parameters
- distribution
- train/val/test split
- export formats
- seed

Output:

- dataset_id
- dataset path
- summary
- quality report

## 13. Testing Expectations

Add tests where practical.

Important tests:

- curve generation returns valid numerical points
- renderer creates image file
- renderer returns pixel points
- MCG-JSON contains required fields
- same seed gives reproducible output
- exporter creates expected files
- quality check catches invalid samples

Do not skip basic validation.

## 14. Done Criteria

A task is done only when:

1. Code runs without obvious errors.
2. The implemented feature matches the request.
3. A simple usage note is added when needed.
4. Existing functionality is not broken.
5. Generated outputs can be inspected.
6. No unrelated files are modified.
7. Tests or basic verification steps are provided when practical.

## 15. First Development Target

The first development target is V0.

V0 should implement:

- basic repository structure
- FastAPI backend with `/health`
- React frontend with a simple home page
- generator module skeleton
- at least one basic curve generator
- at least one template
- preview generation for 3 images
- MCG-JSON output
- PNG + CSV + JSON export for preview samples

V0 should not yet implement:

- full YOLO exporter
- full COCO exporter
- OCR exporter
- complex dataset history
- complex degradation
- large-scale batch generation

## 16. Communication Style

When explaining changes, be concise and specific.

Mention:

- what was changed
- how to run it
- how to verify it
- any limitations or next steps
