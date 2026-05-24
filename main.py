import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

DATA_PATH = 'data/students.csv'
OUTPUT_DIR = 'output'
SUBJECTS = ['数学', '英语', '物理', '化学', '生物']
GRADE_COLORS = {'A': '#4CAF50', 'B': '#2196F3', 'C': '#FF9800', 'D': '#F44336'}


def load_data(path):
    df = pd.read_csv(path, encoding='gbk')
    df['总分'] = df[SUBJECTS].sum(axis=1)
    df['平均分'] = df[SUBJECTS].mean(axis=1).round(2)
    df['等级'] = assign_grades(df['总分'])
    return df


def assign_grades(scores):
    q25, q50, q75 = scores.quantile([0.25, 0.50, 0.75])
    grades = []
    for s in scores:
        if s >= q75:
            grades.append('A')
        elif s >= q50:
            grades.append('B')
        elif s >= q25:
            grades.append('C')
        else:
            grades.append('D')
    return grades


def calc_subject_stats(df):
    stats = {}
    for subj in SUBJECTS:
        col = df[subj]
        stats[subj] = {
            '平均分': col.mean().round(2),
            '最高分': col.max(),
            '最低分': col.min(),
            '及格率': f"{(col >= 60).mean() * 100:.1f}%"
        }
    return stats


def get_top_bottom(df, n=3):
    sorted_df = df.sort_values('总分', ascending=False)
    top = sorted_df.head(n)[['姓名', '总分', '平均分']]
    bottom = sorted_df.tail(n)[['姓名', '总分', '平均分']]
    return top, bottom


def generate_report(df, subject_stats, top, bottom):
    lines = ['=' * 50]
    lines.append('学生成绩分析报告')
    lines.append('=' * 50)
    lines.append('')

    lines.append('一、各科统计')
    lines.append('-' * 40)
    for subj, s in subject_stats.items():
        lines.append(f"  {subj}：平均分 {s['平均分']}，最高分 {s['最高分']}，最低分 {s['最低分']}，及格率 {s['及格率']}")
    lines.append('')

    lines.append('二、总分前3名')
    lines.append('-' * 40)
    for i, (_, row) in enumerate(top.iterrows(), 1):
        lines.append(f"  第{i}名：{row['姓名']}，总分 {row['总分']}，平均分 {row['平均分']}")
    lines.append('')

    lines.append('三、总分后3名')
    lines.append('-' * 40)
    for i, (_, row) in enumerate(bottom.iterrows(), 1):
        lines.append(f"  第{i}名：{row['姓名']}，总分 {row['总分']}，平均分 {row['平均分']}")
    lines.append('')

    lines.append('四、等级分布统计')
    lines.append('-' * 40)
    grade_counts = df['等级'].value_counts().sort_index()
    total = len(df)
    for grade in ['A', 'B', 'C', 'D']:
        count = grade_counts.get(grade, 0)
        pct = count / total * 100
        lines.append(f"  {grade}等：{count}人（{pct:.1f}%）")
    lines.append('')

    lines.append('五、全部学生成绩')
    lines.append('-' * 40)
    for _, row in df.sort_values('总分', ascending=False).iterrows():
        scores = '，'.join(f"{subj} {row[subj]}" for subj in SUBJECTS)
        lines.append(f"  {row['姓名']}：{scores}，总分 {row['总分']}，平均分 {row['平均分']}，等级 {row['等级']}")

    return '\n'.join(lines)


def plot_score_distribution(df):
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('各科成绩分布', fontsize=16)
    for i, subj in enumerate(SUBJECTS):
        ax = axes[i // 3][i % 3]
        ax.hist(df[subj], bins=10, range=(50, 100), edgecolor='black', alpha=0.7)
        ax.set_title(subj)
        ax.set_xlabel('分数')
        ax.set_ylabel('人数')
    axes[1][2].axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'score_distribution.png'), dpi=150)
    plt.close()


def plot_subject_avg(df):
    avgs = [df[subj].mean() for subj in SUBJECTS]
    plt.figure(figsize=(10, 6))
    bars = plt.bar(SUBJECTS, avgs, color=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336'])
    plt.title('各科平均分', fontsize=14)
    plt.xlabel('科目')
    plt.ylabel('平均分')
    plt.ylim(0, 100)
    for bar, avg in zip(bars, avgs):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 f'{avg:.1f}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'subject_avg.png'), dpi=150)
    plt.close()


def plot_total_ranking(df):
    sorted_df = df.sort_values('总分', ascending=True)
    colors = [GRADE_COLORS[g] for g in sorted_df['等级']]
    plt.figure(figsize=(10, 8))
    bars = plt.barh(sorted_df['姓名'], sorted_df['总分'], color=colors)
    plt.title('学生总分排名', fontsize=14)
    plt.xlabel('总分')
    plt.ylabel('姓名')
    for i, (_, row) in enumerate(sorted_df.iterrows()):
        plt.text(row['总分'] + 1, i, f"{row['总分']}({row['等级']})", va='center')
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=GRADE_COLORS[g], label=f'{g}等') for g in ['A', 'B', 'C', 'D']]
    plt.legend(handles=legend_elements, loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'total_ranking.png'), dpi=150)
    plt.close()


def plot_student_radar(df):
    num_vars = len(SUBJECTS)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, axes = plt.subplots(4, 5, figsize=(20, 16), subplot_kw=dict(polar=True))
    fig.suptitle('学生各科成绩雷达图', fontsize=16, y=1.02)

    for idx, (_, row) in enumerate(df.iterrows()):
        ax = axes[idx // 5][idx % 5]
        values = [row[subj] for subj in SUBJECTS]
        values += values[:1]

        color = GRADE_COLORS[row['等级']]
        ax.fill(angles, values, alpha=0.25, color=color)
        ax.plot(angles, values, 'o-', color=color, linewidth=2)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(SUBJECTS, fontsize=8)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=6)
        ax.set_title(f"{row['姓名']}({row['等级']})", fontsize=10, pad=10)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'student_radar.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_boxplot(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    data = [df[subj] for subj in SUBJECTS]
    bp = ax.boxplot(data, tick_labels=SUBJECTS, patch_artist=True)

    colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_title('各科成绩箱线图', fontsize=14)
    ax.set_xlabel('科目')
    ax.set_ylabel('分数')
    ax.set_ylim(40, 105)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'score_boxplot.png'), dpi=150)
    plt.close()


def plot_correlation_heatmap(df):
    corr = df[SUBJECTS].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr, cmap='RdYlGn', vmin=0, vmax=1)

    ax.set_xticks(range(len(SUBJECTS)))
    ax.set_yticks(range(len(SUBJECTS)))
    ax.set_xticklabels(SUBJECTS)
    ax.set_yticklabels(SUBJECTS)

    for i in range(len(SUBJECTS)):
        for j in range(len(SUBJECTS)):
            ax.text(j, i, f'{corr.iloc[i, j]:.2f}', ha='center', va='center',
                    color='white' if corr.iloc[i, j] > 0.5 else 'black', fontsize=12)

    ax.set_title('各科成绩相关性热力图', fontsize=14)
    plt.colorbar(im, ax=ax, label='相关系数')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_heatmap.png'), dpi=150)
    plt.close()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = load_data(DATA_PATH)
    subject_stats = calc_subject_stats(df)
    top, bottom = get_top_bottom(df)

    report = generate_report(df, subject_stats, top, bottom)
    report_path = os.path.join(OUTPUT_DIR, 'report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"报告已保存至 {report_path}")

    plot_score_distribution(df)
    plot_subject_avg(df)
    plot_total_ranking(df)
    plot_student_radar(df)
    plot_boxplot(df)
    plot_correlation_heatmap(df)
    print(f"图表已保存至 {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
