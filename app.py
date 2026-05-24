from flask import Flask, render_template, send_from_directory
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

app = Flask(__name__)

DATA_PATH = 'data/students.csv'
OUTPUT_DIR = 'output'
SUBJECTS = ['数学', '英语', '物理', '化学', '生物']
GRADE_COLORS = {'A': '#4CAF50', 'B': '#2196F3', 'C': '#FF9800', 'D': '#F44336'}


def load_data():
    df = pd.read_csv(DATA_PATH, encoding='gbk')
    df['总分'] = df[SUBJECTS].sum(axis=1)
    df['平均分'] = df[SUBJECTS].mean(axis=1).round(2)
    q25, q50, q75 = df['总分'].quantile([0.25, 0.50, 0.75])
    df['等级'] = df['总分'].apply(lambda s: 'A' if s >= q75 else 'B' if s >= q50 else 'C' if s >= q25 else 'D')
    return df


def generate_student_radar(student_row):
    angles = np.linspace(0, 2 * np.pi, len(SUBJECTS), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    values = [student_row[subj] for subj in SUBJECTS]
    values += values[:1]

    color = GRADE_COLORS[student_row['等级']]
    ax.fill(angles, values, alpha=0.25, color=color)
    ax.plot(angles, values, 'o-', color=color, linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(SUBJECTS, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_title(f"{student_row['姓名']}的成绩雷达图", fontsize=12, pad=15)

    filename = f"radar_{student_row['姓名']}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()
    return filename


@app.route('/')
def index():
    df = load_data()
    sorted_df = df.sort_values('总分', ascending=False)

    subject_stats = {}
    for subj in SUBJECTS:
        col = df[subj]
        subject_stats[subj] = {
            '平均分': col.mean().round(2),
            '最高分': col.max(),
            '最低分': col.min(),
            '及格率': f"{(col >= 60).mean() * 100:.1f}%"
        }

    grade_counts = df['等级'].value_counts().sort_index()
    grade_stats = {g: {'count': grade_counts.get(g, 0), 'pct': grade_counts.get(g, 0) / len(df) * 100} for g in ['A', 'B', 'C', 'D']}

    students = sorted_df.to_dict('records')

    return render_template('index.html',
                           students=students,
                           subject_stats=subject_stats,
                           grade_stats=grade_stats,
                           subjects=SUBJECTS)


@app.route('/student/<name>')
def student_detail(name):
    df = load_data()
    student = df[df['姓名'] == name].iloc[0]

    radar_file = generate_student_radar(student)

    rank = df.sort_values('总分', ascending=False).reset_index(drop=True)
    rank.index = rank.index + 1
    student_rank = rank[rank['姓名'] == name].index[0]

    return render_template('student.html',
                           student=student.to_dict(),
                           radar_file=radar_file,
                           rank=student_rank,
                           total=len(df),
                           subjects=SUBJECTS)


@app.route('/output/<filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(debug=True, port=5000)
