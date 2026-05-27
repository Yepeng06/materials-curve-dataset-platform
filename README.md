# 材料曲线图像数据集合成平台（v1.0.1）

快速跳转： 1、[部署方法](#部署方法) 丨2、[功能介绍](#功能介绍)

# 部署方法
**1、拉取项目代码**

找个文件夹用于存放项目，终端执行：
```bash
git clone -b codex/prepare-documentation-for-v0fix-final-2-release https://github.com/Yepeng06/materials-curve-dataset-platform.git
```
---
**2、启动后端**

项目根目录开终端执行：
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
---
**3、启动前端**

项目根目录再开一个终端执行：
```bash
cd .\frontend
npm install
npm run dev
```
---
**4、访问web系统**

浏览器打开：127.0.0.1:5173 

以后再使用只需启动后端、前端，访问web即可。

---
# 功能介绍
## 模板与模式

![](https://jueshipa-pic.oss-cn-beijing.aliyuncs.com/blog/20260527151111084.png)
**系统提供7个预设模板，对应曲线图常见的风格，分别是：**
- Black White Paper（黑白文档风格）
- Grid Interference（网格干扰 / 摩尔纹效果）
- low_quality_screenshot（低质量截图风格）
- Marker Rich（丰富标记风格）
- Multi Curve Comparison（多曲线对比）
- Real Mainstream（真实主流风格）
- Three Stage Creep（三阶段蠕变曲线）

**系统提供两种数据集生成模式：**
- 显式模式：

系统将按照参数设置来生成数据集。
- 概率采样模式：

选一个模板后，系统会根据模板里的概率分布自动随机生成不同风格。
曲线形态、曲线数量、线型、标记点、图例位置、网格等字段可能由模板采样决定，手动输入不一定完全生效。
## 参数设置
![](https://jueshipa-pic.oss-cn-beijing.aliyuncs.com/blog/20260527152658041.png)
可以设置许多参数：

**预览数量：** 按照当前参数和模板设置生成一定数量张预览图。

**随机种子：** 


**曲线数量：** 曲线图中曲线数量

**曲线形态：** 以钢铁蠕变曲线为切入，提供5种曲线形态：近似线性、初期阶段明显、加速阶段明显、三阶段蠕变、不规则波动。

**采样点数：** 从每条曲线上生成点坐标的数量，设置180则记录每条曲线上180个点坐标。

**噪声强度：** 

**线型：** 提供几种常见线型：实现、虚线、点线、点划线。

**线宽：** 曲线的宽度

**标记点：** 提供4种标记点样式（圆点、方块、三角、菱形），也可设置无标记点。

**图例位置：** 可设置图例位置，也可设置无图例。

**显示网格：** 曲线图背景网格。

**坐标轴参数：** 可设置坐标轴的值范围、轴名称、轴单位。

## 数据集生成

![](https://jueshipa-pic.oss-cn-beijing.aliyuncs.com/blog/20260527153750620.png)
此模块可以设置生成数据集的名称、版本、样板数量。可以设置数据集划分：训练集(Train)、验证集(Val)、测试集(Test)，预设比例为训练：验证：测试=7：2：1.
## 曲线图预览与数据集导出

![](https://jueshipa-pic.oss-cn-beijing.aliyuncs.com/blog/20260527154020364.png)
如图所示，用户可导出生成数据集所用的模板与参数设置，还可根据生成的预览图及时调整参数，以获得最理想的数据集。
