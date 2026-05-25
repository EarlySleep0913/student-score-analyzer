# 学生成绩分析系统

基于 Python + Flask 的学生成绩分析工具，支持命令行分析和 Web 界面展示，提供多维度统计、可视化图表和交互式分析。

## 功能特性

- **多考试批次管理** — 支持期中、期末、月考等多次考试数据切换
- **成绩统计分析** — 各科平均分、最高/最低分、及格率、优秀率、标准差
- **等级评定** — 按总分四分位自动划分 A/B/C/D 四个等级
- **可视化图表** — 成绩分布直方图、柱状图、雷达图、箱线图、相关性热力图
- **学生详情页** — 个人雷达图、班级排名、各科排名、与平均分对比
- **学生对比** — 选择 2-4 名学生进行雷达图对比
- **成绩趋势** — 查看学生多次考试的成绩变化
- **数据导入导出** — 支持 CSV 和 JSON 格式
- **搜索筛选** — 按姓名搜索、按等级筛选

## 环境要求

- Python 3.10+
- 依赖：matplotlib, pandas, flask

## 快速开始

### 安装依赖

```bash
pip install matplotlib pandas flask
```

### 运行命令行分析

```bash
python main.py
```

生成报告和图表，保存在 `output/` 目录。

### 启动 Web 界面

```bash
python app.py
```

访问 http://127.0.0.1:5000

### 生成模拟考试数据

```bash
python create_exam_data.py
```

生成 4 次模拟考试数据（期中、期末、月考一、月考二），保存在 `data/exams/`。

## 项目结构

```
student-score-analyzer/
├── main.py                 # 命令行分析脚本
├── app.py                  # Flask Web 应用
├── create_exam_data.py     # 模拟数据生成脚本
├── data/
│   ├── students.csv        # 学生成绩数据（GBK 编码）
│   └── exams/              # 多次考试数据
│       ├── exam_list.csv   # 考试元数据
│       ├── 期中考试.csv
│       ├── 期末考试.csv
│       ├── 月考一.csv
│       └── 月考二.csv
├── templates/              # HTML 模板
│   ├── base.html           # 基础布局（深色主题）
│   ├── index.html          # 首页总览
│   ├── student.html        # 学生详情
│   ├── analysis.html       # 深度分析
│   ├── compare_select.html # 对比选择
│   ├── compare_result.html # 对比结果
│   ├── trend.html          # 成绩趋势
│   ├── import_data.html    # 导入导出
│   ├── no_data.html        # 无数据提示
│   └── 404.html            # 错误页面
└── output/                 # 生成的报告和图表
```

## 数据格式

CSV 文件，GBK 编码，字段：

| 姓名 | 数学 | 英语 | 物理 | 化学 | 生物 |
|------|------|------|------|------|------|
| 张伟 | 95   | 92   | 97   | 93   | 90   |

## Web 界面

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | `/` | 概览卡片、各科统计、图表、学生列表 |
| 深度分析 | `/analysis` | 统计指标、相关性矩阵、TOP5/BOTTOM5 |
| 学生对比 | `/compare` | 多学生雷达图对比 |
| 成绩趋势 | `/trend` | 多次考试成绩变化 |
| 导入导出 | `/import` | CSV/JSON 数据管理 |
| 学生详情 | `/student/<姓名>` | 个人雷达图、排名、与平均分对比 |

## 截图

**首页总览**

![首页](https://github.com/EarlySleep0913/student-score-analyzer/blob/master/output/score_distribution.png)

**学生排名**

![排名](https://github.com/EarlySleep0913/student-score-analyzer/blob/master/output/total_ranking.png)

**相关性分析**

![相关性](https://github.com/EarlySleep0913/student-score-analyzer/blob/master/output/correlation_heatmap.png)

## 技术栈

- **后端**: Python, Flask
- **数据处理**: Pandas, NumPy
- **可视化**: Matplotlib
- **前端**: HTML, CSS, JavaScript (原生)

## License

MIT
