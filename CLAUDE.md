# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Python 学生成绩分析项目。

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
│   ├── base.html        # 基础模板
│   ├── index.html       # 首页
│   └── student.html     # 学生详情页
└── output/              # 生成的报告和图表
```

## 语言偏好

始终使用中文回复。
