# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Python 学生成绩分析项目，支持命令行分析和 Web 界面展示。

### 功能特性
- 命令行分析脚本：生成统计报告和可视化图表
- Flask Web 界面：现代化 UI，支持交互式分析
- 学生详情页：个人雷达图、成绩排名、与平均分对比
- 学生对比：支持多学生雷达图对比
- 深度分析：统计指标、相关性矩阵、等级分布
- 搜索筛选：按姓名搜索、按等级筛选

## 环境要求

- Python 3.10+
- 依赖：matplotlib, pandas, flask

## 数据格式

- 数据文件：`data/students.csv`，GBK 编码
- 字段：姓名, 数学, 英语, 物理, 化学, 生物

## 常用命令

```bash
# 安装依赖
pip install matplotlib pandas flask

# 运行分析脚本（生成报告和图表）
python main.py

# 启动 Web 界面（访问 http://127.0.0.1:5000）
python app.py
```

## 项目结构

```
student-score-analyzer/
├── main.py              # 分析脚本（命令行）
├── app.py               # Flask Web 应用
├── data/
│   └── students.csv     # 学生成绩数据（GBK 编码）
├── templates/           # HTML 模板
│   ├── base.html        # 基础布局模板
│   ├── index.html       # 首页（总览、图表、学生列表）
│   ├── student.html     # 学生详情页
│   ├── analysis.html    # 深度分析页
│   ├── compare_select.html  # 对比选择页
│   ├── compare_result.html  # 对比结果页
│   └── 404.html         # 错误页面
└── output/              # 生成的报告和图表
```

## 语言偏好

始终使用中文回复。
