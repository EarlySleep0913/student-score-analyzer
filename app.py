from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from datetime import datetime
import json
import csv
import io

matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

OUTPUT_DIR = 'output'
EXAMS_DIR = 'data/exams'
SUBJECTS = ['数学', '英语', '物理', '化学', '生物']
GRADE_COLORS = {'A': '#10b981', 'B': '#3b82f6', 'C': '#f59e0b', 'D': '#ef4444'}
GRADE_LABELS = {'A': '优秀', 'B': '良好', 'C': '中等', 'D': '及格'}


def get_exam_list():
    meta_file = os.path.join(EXAMS_DIR, 'exam_list.csv')
    if os.path.exists(meta_file):
        return pd.read_csv(meta_file, encoding='gbk').to_dict('records')
    return []


def load_exam_data(exam_name=None):
    exams = get_exam_list()
    if not exams:
        return None, None

    if exam_name is None:
        exam_name = exams[0]['考试名称']

    exam_info = next((e for e in exams if e['考试名称'] == exam_name), None)
    if exam_info is None:
        return None, None

    filepath = os.path.join(EXAMS_DIR, exam_info['文件名'])
    if not os.path.exists(filepath):
        return None, None

    df = pd.read_csv(filepath, encoding='gbk')
    df['总分'] = df[SUBJECTS].sum(axis=1)
    df['平均分'] = df[SUBJECTS].mean(axis=1).round(2)
    q25, q50, q75 = df['总分'].quantile([0.25, 0.50, 0.75])
    df['等级'] = df['总分'].apply(lambda s: 'A' if s >= q75 else 'B' if s >= q50 else 'C' if s >= q25 else 'D')
    df['等级标签'] = df['等级'].map(GRADE_LABELS)
    df['考试'] = exam_name

    for subj in SUBJECTS:
        df[f'{subj}排名'] = df[subj].rank(ascending=False, method='min').astype(int)

    return df, exam_info


def generate_student_radar(student_row, compare_avg=False, df=None):
    angles = np.linspace(0, 2 * np.pi, len(SUBJECTS), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    values = [student_row[subj] for subj in SUBJECTS]
    values += values[:1]

    color = GRADE_COLORS.get(student_row.get('等级', 'B'), '#3b82f6')
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

    filename = f"radar_{student_row['姓名']}_{datetime.now().strftime('%H%M%S')}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(filepath, dpi=120, bbox_inches='tight', facecolor='white')
    plt.close()
    return filename


def generate_compare_radar(students_data):
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

    filename = 'compare_' + '_'.join([s['姓名'] for s in students_data[:4]]) + '.png'
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(filepath, dpi=120, bbox_inches='tight', facecolor='white')
    plt.close()
    return filename


@app.route('/')
def index():
    exam_name = request.args.get('exam')
    df, exam_info = load_exam_data(exam_name)

    if df is None:
        return render_template('no_data.html')

    exams = get_exam_list()
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
                           pass_rate=pass_rate,
                           exams=exams,
                           current_exam=exam_info)


@app.route('/student/<name>')
def student_detail(name):
    exam_name = request.args.get('exam')
    df, exam_info = load_exam_data(exam_name)

    if df is None:
        return render_template('404.html'), 404

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

    exams = get_exam_list()

    return render_template('student.html',
                           student=student.to_dict(),
                           radar_file=radar_file,
                           rank=student_rank,
                           total=len(df),
                           subjects=SUBJECTS,
                           subject_ranks=subject_ranks,
                           avg_diff=avg_diff,
                           similar_students=similar_students,
                           grade_colors=GRADE_COLORS,
                           exams=exams,
                           current_exam=exam_info)


@app.route('/compare')
def compare():
    exam_name = request.args.get('exam')
    df, exam_info = load_exam_data(exam_name)

    if df is None:
        return render_template('no_data.html')

    names = request.args.getlist('name')
    exams = get_exam_list()

    if len(names) < 2:
        students = df.sort_values('总分', ascending=False).to_dict('records')
        return render_template('compare_select.html',
                               students=students,
                               subjects=SUBJECTS,
                               exams=exams,
                               current_exam=exam_info)

    students_data = []
    for name in names[:4]:
        student = df[df['姓名'] == name]
        if not student.empty:
            students_data.append(student.iloc[0].to_dict())

    compare_image = None
    if len(students_data) >= 2:
        compare_image = generate_compare_radar(students_data)

    return render_template('compare_result.html',
                           students=students_data,
                           subjects=SUBJECTS,
                           compare_image=compare_image,
                           grade_colors=GRADE_COLORS,
                           exams=exams,
                           current_exam=exam_info)


@app.route('/analysis')
def analysis():
    exam_name = request.args.get('exam')
    df, exam_info = load_exam_data(exam_name)

    if df is None:
        return render_template('no_data.html')

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

    exams = get_exam_list()

    return render_template('analysis.html',
                           subject_stats=subject_stats,
                           corr=corr,
                           subjects=SUBJECTS,
                           top5=top5,
                           bottom5=bottom5,
                           grade_students=grade_students,
                           grade_colors=GRADE_COLORS,
                           grade_labels=GRADE_LABELS,
                           exams=exams,
                           current_exam=exam_info)


@app.route('/trend')
def trend():
    student_name = request.args.get('student')
    exams = get_exam_list()

    all_data = []
    for exam in exams:
        df, _ = load_exam_data(exam['考试名称'])
        if df is not None:
            if student_name:
                student = df[df['姓名'] == student_name]
                if not student.empty:
                    all_data.append(student.iloc[0].to_dict())
            else:
                avg_row = {'姓名': '班级平均', '考试': exam['考试名称']}
                for subj in SUBJECTS:
                    avg_row[subj] = df[subj].mean().round(1)
                avg_row['总分'] = df['总分'].mean().round(1)
                avg_row['平均分'] = df['平均分'].mean().round(1)
                all_data.append(avg_row)

    students = []
    if exams:
        df, _ = load_exam_data(exams[0]['考试名称'])
        if df is not None:
            students = df['姓名'].tolist()

    return render_template('trend.html',
                           trend_data=all_data,
                           subjects=SUBJECTS,
                           students=students,
                           current_student=student_name,
                           exams=exams)


@app.route('/import', methods=['GET', 'POST'])
def import_data():
    exams = get_exam_list()

    if request.method == 'POST':
        exam_name = request.form.get('exam_name')
        exam_date = request.form.get('exam_date')
        exam_desc = request.form.get('exam_desc', '')
        file = request.files.get('file')

        if not exam_name or not file:
            return render_template('import_data.html', error='请填写考试信息并选择文件', exams=exams)

        if not file.filename.endswith('.csv'):
            return render_template('import_data.html', error='请上传CSV文件', exams=exams)

        try:
            content = file.read().decode('gbk')
            df = pd.read_csv(io.StringIO(content))

            required_cols = ['姓名'] + SUBJECTS
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return render_template('import_data.html',
                                       error=f'缺少必要列: {", ".join(missing_cols)}',
                                       exams=exams)

            filename = f"{exam_name}.csv"
            filepath = os.path.join(EXAMS_DIR, filename)
            df.to_csv(filepath, index=False, encoding='gbk')

            meta_file = os.path.join(EXAMS_DIR, 'exam_list.csv')
            if os.path.exists(meta_file):
                meta_df = pd.read_csv(meta_file, encoding='gbk')
            else:
                meta_df = pd.DataFrame(columns=['考试名称', '考试日期', '考试说明', '文件名'])

            new_row = pd.DataFrame([{
                '考试名称': exam_name,
                '考试日期': exam_date or datetime.now().strftime('%Y-%m-%d'),
                '考试说明': exam_desc,
                '文件名': filename
            }])
            meta_df = pd.concat([meta_df, new_row], ignore_index=True)
            meta_df.to_csv(meta_file, index=False, encoding='gbk')

            return render_template('import_data.html', success=f'考试"{exam_name}"导入成功！', exams=exams)

        except Exception as e:
            return render_template('import_data.html', error=f'导入失败: {str(e)}', exams=exams)

    return render_template('import_data.html', exams=exams)


@app.route('/export')
def export():
    exam_name = request.args.get('exam')
    format_type = request.args.get('format', 'csv')

    df, exam_info = load_exam_data(exam_name)
    if df is None:
        return jsonify({'error': '没有数据'}), 404

    if format_type == 'csv':
        output = io.StringIO()
        df[['姓名'] + SUBJECTS + ['总分', '平均分', '等级']].to_csv(output, index=False, encoding='utf-8-sig')
        response = app.response_class(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={exam_name}_成绩.csv'}
        )
        return response

    elif format_type == 'json':
        data = df[['姓名'] + SUBJECTS + ['总分', '平均分', '等级']].to_dict('records')
        response = app.response_class(
            json.dumps(data, ensure_ascii=False, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename={exam_name}_成绩.json'}
        )
        return response

    return jsonify({'error': '不支持的格式'}), 400


@app.route('/api/students')
def api_students():
    exam_name = request.args.get('exam')
    df, _ = load_exam_data(exam_name)

    if df is None:
        return jsonify({'error': '没有数据'}), 404

    grade = request.args.get('grade')
    sort_by = request.args.get('sort', '总分')
    order = request.args.get('order', 'desc')

    if grade:
        df = df[df['等级'] == grade]

    ascending = order == 'asc'
    df = df.sort_values(sort_by, ascending=ascending)

    return jsonify(df[['姓名'] + SUBJECTS + ['总分', '平均分', '等级']].to_dict('records'))


@app.route('/api/exams')
def api_exams():
    return jsonify(get_exam_list())


@app.route('/output/<filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(EXAMS_DIR, exist_ok=True)
    app.run(debug=True, port=5000)
