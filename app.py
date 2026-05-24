from flask import Flask, render_template, send_from_directory, request, jsonify
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
GRADE_COLORS = {'A': '#10b981', 'B': '#3b82f6', 'C': '#f59e0b', 'D': '#ef4444'}
GRADE_LABELS = {'A': '优秀', 'B': '良好', 'C': '中等', 'D': '及格'}


def load_data():
    df = pd.read_csv(DATA_PATH, encoding='gbk')
    df['总分'] = df[SUBJECTS].sum(axis=1)
    df['平均分'] = df[SUBJECTS].mean(axis=1).round(2)
    q25, q50, q75 = df['总分'].quantile([0.25, 0.50, 0.75])
    df['等级'] = df['总分'].apply(lambda s: 'A' if s >= q75 else 'B' if s >= q50 else 'C' if s >= q25 else 'D')
    df['等级标签'] = df['等级'].map(GRADE_LABELS)

    for subj in SUBJECTS:
        df[f'{subj}排名'] = df[subj].rank(ascending=False, method='min').astype(int)

    return df


def generate_student_radar(student_row, compare_avg=False, df=None):
    angles = np.linspace(0, 2 * np.pi, len(SUBJECTS), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    values = [student_row[subj] for subj in SUBJECTS]
    values += values[:1]

    color = GRADE_COLORS[student_row['等级']]
    ax.fill(angles, values, alpha=0.3, color=color)
    ax.plot(angles, values, 'o-', color=color, linewidth=2.5, markersize=8)

    if compare_avg and df is not None:
        avg_values = [df[subj].mean() for subj in SUBJECTS]
        avg_values += avg_values[:1]
        ax.plot(angles, avg_values, 's--', color='#94a3b8', linewidth=2, markersize=6, label='班级平均')
        ax.fill(angles, avg_values, alpha=0.1, color='#94a3b8')
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(SUBJECTS, fontsize=12, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8, color='#94a3b8')
    ax.set_title(f"{student_row['姓名']}的成绩分析", fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)

    filename = f"radar_{student_row['姓名']}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(filepath, dpi=120, bbox_inches='tight', facecolor='white')
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
            '平均分': col.mean().round(1),
            '最高分': col.max(),
            '最低分': col.min(),
            '及格率': f"{(col >= 60).mean() * 100:.1f}",
            '优秀率': f"{(col >= 90).mean() * 100:.1f}"
        }

    grade_counts = df['等级'].value_counts().sort_index()
    grade_stats = {
        g: {
            'count': grade_counts.get(g, 0),
            'pct': grade_counts.get(g, 0) / len(df) * 100,
            'label': GRADE_LABELS[g]
        } for g in ['A', 'B', 'C', 'D']
    }

    students = sorted_df.to_dict('records')
    total_avg = df['平均分'].mean().round(1)
    pass_rate = (df['平均分'] >= 60).mean() * 100

    return render_template('index.html',
                           students=students,
                           subject_stats=subject_stats,
                           grade_stats=grade_stats,
                           subjects=SUBJECTS,
                           total_students=len(df),
                           total_avg=total_avg,
                           pass_rate=pass_rate)


@app.route('/student/<name>')
def student_detail(name):
    df = load_data()
    student = df[df['姓名'] == name]

    if student.empty:
        return render_template('404.html'), 404

    student = student.iloc[0]
    radar_file = generate_student_radar(student, compare_avg=True, df=df)

    sorted_df = df.sort_values('总分', ascending=False).reset_index(drop=True)
    sorted_df.index = sorted_df.index + 1
    student_rank = sorted_df[sorted_df['姓名'] == name].index[0]

    subject_ranks = {}
    for subj in SUBJECTS:
        rank_df = df.sort_values(subj, ascending=False).reset_index(drop=True)
        rank_df.index = rank_df.index + 1
        rank = rank_df[rank_df['姓名'] == name].index[0]
        subject_ranks[subj] = rank

    avg_diff = {}
    for subj in SUBJECTS:
        diff = student[subj] - df[subj].mean()
        avg_diff[subj] = round(diff, 1)

    similar_students = df[
        (df['姓名'] != name) &
        (df['总分'].between(student['总分'] - 30, student['总分'] + 30))
    ].head(3).to_dict('records')

    return render_template('student.html',
                           student=student.to_dict(),
                           radar_file=radar_file,
                           rank=student_rank,
                           total=len(df),
                           subjects=SUBJECTS,
                           subject_ranks=subject_ranks,
                           avg_diff=avg_diff,
                           similar_students=similar_students,
                           grade_colors=GRADE_COLORS)


@app.route('/compare')
def compare():
    df = load_data()
    names = request.args.getlist('name')

    if len(names) < 2:
        students = df.sort_values('总分', ascending=False).to_dict('records')
        return render_template('compare_select.html', students=students, subjects=SUBJECTS)

    students_data = []
    for name in names[:4]:
        student = df[df['姓名'] == name]
        if not student.empty:
            students_data.append(student.iloc[0].to_dict())

    if len(students_data) >= 2:
        angles = np.linspace(0, 2 * np.pi, len(SUBJECTS), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']

        for i, student in enumerate(students_data):
            values = [student[subj] for subj in SUBJECTS]
            values += values[:1]
            ax.plot(angles, values, 'o-', color=colors[i], linewidth=2.5,
                    markersize=8, label=student['姓名'])
            ax.fill(angles, values, alpha=0.1, color=colors[i])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(SUBJECTS, fontsize=12, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.set_title('学生成绩对比', fontsize=16, fontweight='bold', pad=20)

        filename = 'compare_' + '_'.join(names[:4]) + '.png'
        filepath = os.path.join(OUTPUT_DIR, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
    else:
        filename = None

    return render_template('compare_result.html',
                           students=students_data,
                           subjects=SUBJECTS,
                           compare_image=filename,
                           grade_colors=GRADE_COLORS)


@app.route('/analysis')
def analysis():
    df = load_data()

    subject_stats = {}
    for subj in SUBJECTS:
        col = df[subj]
        subject_stats[subj] = {
            'mean': col.mean().round(1),
            'median': col.median().round(1),
            'std': col.std().round(1),
            'max': col.max(),
            'min': col.min()
        }

    corr = df[SUBJECTS].corr().round(2)

    top5 = df.nlargest(5, '总分')[['姓名', '总分', '平均分', '等级']].to_dict('records')
    bottom5 = df.nsmallest(5, '总分')[['姓名', '总分', '平均分', '等级']].to_dict('records')

    grade_students = {}
    for grade in ['A', 'B', 'C', 'D']:
        grade_students[grade] = df[df['等级'] == grade][['姓名', '总分', '平均分']].sort_values('总分', ascending=False).to_dict('records')

    return render_template('analysis.html',
                           subject_stats=subject_stats,
                           corr=corr,
                           subjects=SUBJECTS,
                           top5=top5,
                           bottom5=bottom5,
                           grade_students=grade_students,
                           grade_colors=GRADE_COLORS,
                           grade_labels=GRADE_LABELS)


@app.route('/api/students')
def api_students():
    df = load_data()
    grade = request.args.get('grade')
    sort_by = request.args.get('sort', '总分')
    order = request.args.get('order', 'desc')

    if grade:
        df = df[df['等级'] == grade]

    ascending = order == 'asc'
    df = df.sort_values(sort_by, ascending=ascending)

    return jsonify(df.to_dict('records'))


@app.route('/output/<filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(debug=True, port=5000)
