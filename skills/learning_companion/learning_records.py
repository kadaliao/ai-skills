"""
学习记录系统 - 基于艾宾浩斯遗忘曲线
Learning Records System - Based on Ebbinghaus Forgetting Curve
"""

import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class LearningRecords:
    """学习记录管理 / Learning Records Manager"""

    def __init__(self, student_name: str, records_file: str = "/workspace/group/learning_companion/sixi_learning_records.json"):
        """
        初始化学习记录 / Initialize learning records

        Args:
            student_name: 学生姓名 / Student name
            records_file: 记录文件路径 / Records file path
        """
        self.student_name = student_name
        self.records_file = records_file
        self.records = self._load_records()

    def _load_records(self) -> Dict:
        """加载记录 / Load records"""
        try:
            with open(self.records_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "student_name": self.student_name,
                "created_at": datetime.now().isoformat(),
                "learning_sessions": [],
                "review_schedule": [],
                "statistics": {
                    "total_questions": 0,
                    "correct_answers": 0,
                    "average_score": 0.0,
                    "weak_topics": []
                }
            }

    def _save_records(self):
        """保存记录 / Save records"""
        with open(self.records_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)

    def add_qa_record(
        self,
        topic: str,
        question_zh: str,
        question_en: str,
        user_answer: str,
        correct_answer_zh: str,
        correct_answer_en: str,
        score: int,
        notes: str = ""
    ):
        """
        添加问答记录 / Add Q&A record

        Args:
            topic: 主题 / Topic
            question_zh: 中文问题 / Chinese question
            question_en: 英文问题 / English question
            user_answer: 用户答案 / User answer
            correct_answer_zh: 中文标准答案 / Chinese correct answer
            correct_answer_en: 英文标准答案 / English correct answer
            score: 得分 (0-10) / Score (0-10)
            notes: 备注 / Notes
        """
        qa_record = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "question_zh": question_zh,
            "question_en": question_en,
            "user_answer": user_answer,
            "correct_answer_zh": correct_answer_zh,
            "correct_answer_en": correct_answer_en,
            "score": score,
            "notes": notes,
            "mastery_level": self._calculate_mastery(score)
        }

        self.records["learning_sessions"].append(qa_record)
        self._update_statistics()
        self._schedule_reviews(qa_record)
        self._save_records()

    def _calculate_mastery(self, score: int) -> str:
        """
        计算掌握程度 / Calculate mastery level

        Args:
            score: 得分 / Score

        Returns:
            掌握程度 / Mastery level
        """
        if score >= 9:
            return "excellent"  # 优秀 / Excellent
        elif score >= 7:
            return "good"  # 良好 / Good
        elif score >= 5:
            return "fair"  # 一般 / Fair
        else:
            return "poor"  # 较差 / Poor

    def _schedule_reviews(self, qa_record: Dict):
        """
        安排复习计划 / Schedule reviews
        基于艾宾浩斯遗忘曲线 / Based on Ebbinghaus forgetting curve

        Args:
            qa_record: 问答记录 / Q&A record
        """
        mastery = qa_record["mastery_level"]
        timestamp = datetime.fromisoformat(qa_record["timestamp"])

        # 根据掌握程度调整复习间隔 / Adjust review intervals based on mastery
        if mastery == "excellent":
            intervals = [1, 3, 7, 15, 30]  # 天 / days
        elif mastery == "good":
            intervals = [1, 2, 5, 10, 20]
        elif mastery == "fair":
            intervals = [1, 2, 4, 7, 14]
        else:  # poor
            intervals = [1, 1, 3, 5, 10]

        for interval in intervals:
            review_date = timestamp + timedelta(days=interval)

            self.records["review_schedule"].append({
                "review_date": review_date.isoformat(),
                "topic": qa_record["topic"],
                "question_zh": qa_record["question_zh"],
                "question_en": qa_record["question_en"],
                "mastery_level": mastery,
                "interval_days": interval,
                "completed": False
            })

    def _update_statistics(self):
        """更新统计信息 / Update statistics"""
        sessions = self.records["learning_sessions"]

        if not sessions:
            return

        total = len(sessions)
        correct = sum(1 for s in sessions if s["score"] >= 7)
        avg_score = sum(s["score"] for s in sessions) / total

        # 找出薄弱主题 / Find weak topics
        topic_scores = {}
        for s in sessions:
            topic = s["topic"]
            if topic not in topic_scores:
                topic_scores[topic] = []
            topic_scores[topic].append(s["score"])

        weak_topics = []
        for topic, scores in topic_scores.items():
            avg = sum(scores) / len(scores)
            if avg < 7:
                weak_topics.append({
                    "topic": topic,
                    "average_score": round(avg, 1),
                    "attempts": len(scores)
                })

        weak_topics.sort(key=lambda x: x["average_score"])

        self.records["statistics"] = {
            "total_questions": total,
            "correct_answers": correct,
            "average_score": round(avg_score, 1),
            "weak_topics": weak_topics
        }

    def get_pending_reviews(self, date: Optional[datetime] = None) -> List[Dict]:
        """
        获取待复习内容 / Get pending reviews

        Args:
            date: 日期 (默认今天) / Date (default today)

        Returns:
            待复习列表 / List of pending reviews
        """
        if date is None:
            date = datetime.now()

        pending = []
        for review in self.records["review_schedule"]:
            if not review["completed"]:
                review_date = datetime.fromisoformat(review["review_date"])
                if review_date.date() <= date.date():
                    pending.append(review)

        return pending

    def mark_review_completed(self, question_zh: str, review_date: str):
        """
        标记复习完成 / Mark review as completed

        Args:
            question_zh: 中文问题 / Chinese question
            review_date: 复习日期 / Review date
        """
        for review in self.records["review_schedule"]:
            if (review["question_zh"] == question_zh and
                review["review_date"] == review_date):
                review["completed"] = True
                break

        self._save_records()

    def get_statistics(self) -> Dict:
        """
        获取学习统计 / Get learning statistics

        Returns:
            统计信息 / Statistics
        """
        return self.records["statistics"]

    def get_all_records(self) -> List[Dict]:
        """
        获取所有学习记录 / Get all learning records

        Returns:
            记录列表 / List of records
        """
        return self.records["learning_sessions"]


# 命令行交互示例 / Command-line interaction example
if __name__ == "__main__":
    lr = LearningRecords("Sixi")

    print("=" * 80)
    print(f"📊 {lr.student_name} 的学习记录 / Learning Records")
    print("=" * 80)

    # 显示统计 / Show statistics
    stats = lr.get_statistics()
    print(f"\n总问题数 / Total Questions: {stats['total_questions']}")
    print(f"正确率 / Accuracy: {stats['correct_answers']}/{stats['total_questions']}")
    print(f"平均分 / Average Score: {stats['average_score']}/10")

    if stats['weak_topics']:
        print(f"\n薄弱主题 / Weak Topics:")
        for wt in stats['weak_topics']:
            print(f"  - {wt['topic']}: {wt['average_score']}/10 ({wt['attempts']} 次)")

    # 显示待复习 / Show pending reviews
    pending = lr.get_pending_reviews()
    print(f"\n待复习 / Pending Reviews: {len(pending)} 个")
    for p in pending[:5]:  # 只显示前5个 / Show first 5 only
        print(f"  - {p['topic']}: {p['question_zh']}")
