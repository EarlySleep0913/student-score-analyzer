import pandas as pd
import numpy as np
import os

np.random.seed(42)

STUDENTS = [
    '张伟', '王芳', '李明', '赵静', '刘洋',
    '陈思', '杨磊', '周婷', '吴强', '郑雪',
    '孙浩', '朱丽', '马超', '胡梅', '林峰',
    '何欣', '罗杰', '谢芳', '唐明', '韩雪'
]

SUBJECTS = ['数学', '英语', '物理', '化学', '生物']

EXAMS = {
    '期中考试': {
        'date': '2026-04-15',
        'desc': '高一下学期期中考试',
        'base_means': [75, 76, 74, 73, 75],
        'base_stds': [12, 11, 13, 12, 11]
    },
    '期末考试': {
        'date': '2026-06-20',
        'desc': '高一下学期期末考试',
        'base_means': [78, 77, 76, 75, 77],
        'base_stds': [13, 12, 14, 13, 12]
    },
    '月考一': {
        'date': '2026-03-10',
        'desc': '高一下学期第一次月考',
        'base_means': [72, 73, 71, 70, 72],
        'base_stds': [11, 10, 12, 11, 10]
    },
    '月考二': {
        'date': '2026-05-08',
        'desc': '高一下学期第二次月考',
        'base_means': [76, 75, 74, 73, 75],
        'base_stds': [12, 11, 13, 12, 11]
    }
}

# 学生能力等级（影响各次考试的相对表现）
STUDENT_LEVELS = {
    '张伟': 1.15, '王芳': 1.08, '李明': 0.95, '赵静': 1.12, '刘洋': 0.82,
    '陈思': 1.05, '杨磊': 0.72, '周婷': 1.20, '吴强': 0.88, '郑雪': 1.10,
    '孙浩': 0.75, '朱丽': 1.00, '马超': 0.70, '胡梅': 1.06, '林峰': 0.93,
    '何欣': 1.14, '罗杰': 0.80, '谢芳': 0.87, '唐明': 0.98, '韩雪': 0.68
}

os.makedirs('data/exams', exist_ok=True)

for exam_name, exam_info in EXAMS.items():
    data = {'姓名': STUDENTS}
    for i, subj in enumerate(SUBJECTS):
        scores = []
        for student in STUDENTS:
            level = STUDENT_LEVELS[student]
            base = exam_info['base_means'][i]
            std = exam_info['base_stds'][i]
            score = int(np.clip(base * level + np.random.normal(0, std * 0.5), 50, 100))
            scores.append(score)
        data[subj] = scores

    df = pd.DataFrame(data)
    filename = f"data/exams/{exam_name}.csv"
    df.to_csv(filename, index=False, encoding='gbk')
    print(f"已创建: {filename}")

# 创建考试元数据
meta = []
for exam_name, exam_info in EXAMS.items():
    meta.append({
        '考试名称': exam_name,
        '考试日期': exam_info['date'],
        '考试说明': exam_info['desc'],
        '文件名': f"{exam_name}.csv"
    })

meta_df = pd.DataFrame(meta)
meta_df.to_csv('data/exams/exam_list.csv', index=False, encoding='gbk')
print("\n已创建考试列表: data/exams/exam_list.csv")
print("\n所有考试数据创建完成！")
