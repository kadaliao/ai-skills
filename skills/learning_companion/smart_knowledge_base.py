"""
智能知识库系统 - 带语义去重
Smart Knowledge Base System - With Semantic Deduplication
"""

import json
import hashlib
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
import re


class SmartKnowledgeBase:
    """智能知识库 / Smart Knowledge Base"""

    def __init__(self, kb_file: str = "/workspace/group/learning_companion/knowledge_base.json"):
        """
        初始化知识库 / Initialize knowledge base

        Args:
            kb_file: 知识库文件路径 / Knowledge base file path
        """
        self.kb_file = kb_file
        self.knowledge_base = self._load_kb()

    def _load_kb(self) -> Dict:
        """加载知识库 / Load knowledge base"""
        try:
            with open(self.kb_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"topics": {}, "metadata": {"created_at": datetime.now().isoformat()}}

    def _save_kb(self):
        """保存知识库 / Save knowledge base"""
        with open(self.kb_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)

    def extract_keywords(self, text: str) -> Set[str]:
        """
        提取中文关键词 / Extract Chinese keywords
        使用 n-gram 方法提取 1-3 个字的词组
        Uses n-gram method to extract 1-3 character phrases

        Args:
            text: 输入文本 / Input text

        Returns:
            关键词集合 / Set of keywords
        """
        # 转小写 / Convert to lowercase
        text_lower = text.lower()

        # 停用词 / Stopwords
        stopwords = {
            '的', '是', '在', '有', '和', '了', '与', '个', '对', '为',
            '这', '那', '什么', '如何', '怎么', '哪些', '哪个', '吗', '呢', '地方'
        }

        keywords = set()

        # 提取所有汉字 / Extract all Chinese characters
        chars = [c for c in text_lower if '\u4e00' <= c <= '\u9fff']

        # 1-gram: 单字 / Single characters
        for c in chars:
            if c not in stopwords and len(c) == 1:
                keywords.add(c)

        # 2-gram: 双字词 / Two-character words
        for i in range(len(chars) - 1):
            word = chars[i] + chars[i+1]
            keywords.add(word)

        # 3-gram: 三字词 / Three-character words
        for i in range(len(chars) - 2):
            word = chars[i] + chars[i+1] + chars[i+2]
            keywords.add(word)

        return keywords

    def calculate_similarity(self, keywords1: Set[str], keywords2: Set[str]) -> float:
        """
        计算 Jaccard 相似度 / Calculate Jaccard similarity

        Args:
            keywords1: 关键词集合1 / Keyword set 1
            keywords2: 关键词集合2 / Keyword set 2

        Returns:
            相似度 [0, 1] / Similarity score [0, 1]
        """
        if not keywords1 or not keywords2:
            return 0.0

        intersection = keywords1 & keywords2
        union = keywords1 | keywords2

        return len(intersection) / len(union) if union else 0.0

    def find_similar_questions(self, topic: str, new_question: str, threshold: float = 0.6) -> List[Dict]:
        """
        查找相似问题 / Find similar questions

        Args:
            topic: 主题 / Topic
            new_question: 新问题 / New question
            threshold: 相似度阈值 / Similarity threshold

        Returns:
            相似问题列表 / List of similar questions
        """
        topic_id = hashlib.md5(topic.encode()).hexdigest()[:8]

        if topic_id not in self.knowledge_base["topics"]:
            return []

        new_keywords = self.extract_keywords(new_question)
        similar_questions = []

        for qa in self.knowledge_base["topics"][topic_id]["questions"]:
            existing_question = qa["question_zh"]
            existing_keywords = self.extract_keywords(existing_question)

            similarity = self.calculate_similarity(new_keywords, existing_keywords)

            if similarity >= threshold:
                similar_questions.append({
                    "question": existing_question,
                    "similarity": similarity,
                    "hash": qa["question_hash"]
                })

        # 按相似度排序 / Sort by similarity
        similar_questions.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_questions

    def add_question(
        self,
        topic: str,
        question_zh: str,
        question_en: str,
        answer_zh: str,
        answer_en: str,
        difficulty: str = "medium",
        tags: List[str] = None,
        force: bool = False
    ) -> Tuple[str, Optional[List[Dict]]]:
        """
        添加问题到知识库 / Add question to knowledge base

        Args:
            topic: 主题 / Topic
            question_zh: 中文问题 / Chinese question
            question_en: 英文问题 / English question
            answer_zh: 中文答案 / Chinese answer
            answer_en: 英文答案 / English answer
            difficulty: 难度 / Difficulty (easy/medium/hard)
            tags: 标签 / Tags
            force: 强制添加(跳过去重) / Force add (skip deduplication)

        Returns:
            (状态, 相似问题列表) / (status, similar_questions_list)
            状态可能是 / Status can be:
            - "ADDED": 成功添加 / Successfully added
            - "EXACT_DUPLICATE": 完全重复 / Exact duplicate
            - "SIMILAR_FOUND": 发现相似问题 / Similar questions found
        """
        topic_id = hashlib.md5(topic.encode()).hexdigest()[:8]
        question_hash = hashlib.md5(question_zh.encode()).hexdigest()[:16]

        # 初始化主题 / Initialize topic
        if topic_id not in self.knowledge_base["topics"]:
            self.knowledge_base["topics"][topic_id] = {
                "topic_name": topic,
                "created_at": datetime.now().isoformat(),
                "questions": []
            }

        # 检查完全重复 / Check exact duplicate
        for qa in self.knowledge_base["topics"][topic_id]["questions"]:
            if qa["question_hash"] == question_hash:
                return ("EXACT_DUPLICATE", None)

        # 如果不强制添加,检查相似问题 / If not forcing, check similar questions
        if not force:
            similar = self.find_similar_questions(topic, question_zh, threshold=0.6)
            if similar:
                return ("SIMILAR_FOUND", similar)

        # 添加问题 / Add question
        qa_entry = {
            "question_hash": question_hash,
            "question_zh": question_zh,
            "question_en": question_en,
            "answer_zh": answer_zh,
            "answer_en": answer_en,
            "difficulty": difficulty,
            "tags": tags or [],
            "added_at": datetime.now().isoformat(),
            "review_count": 0,
            "last_reviewed": None
        }

        self.knowledge_base["topics"][topic_id]["questions"].append(qa_entry)
        self._save_kb()

        return ("ADDED", None)

    def get_topic_questions(self, topic: str) -> List[Dict]:
        """
        获取主题下的所有问题 / Get all questions under a topic

        Args:
            topic: 主题 / Topic

        Returns:
            问题列表 / List of questions
        """
        topic_id = hashlib.md5(topic.encode()).hexdigest()[:8]

        if topic_id in self.knowledge_base["topics"]:
            return self.knowledge_base["topics"][topic_id]["questions"]
        return []

    def list_topics(self) -> List[Dict]:
        """
        列出所有主题 / List all topics

        Returns:
            主题列表 / List of topics
        """
        topics = []
        for topic_id, topic_data in self.knowledge_base["topics"].items():
            topics.append({
                "topic_id": topic_id,
                "topic_name": topic_data["topic_name"],
                "question_count": len(topic_data["questions"]),
                "created_at": topic_data["created_at"]
            })
        return topics

    def search_questions(self, keyword: str) -> List[Dict]:
        """
        搜索包含关键词的问题 / Search questions containing keyword

        Args:
            keyword: 搜索关键词 / Search keyword

        Returns:
            匹配的问题列表 / List of matching questions
        """
        results = []
        for topic_id, topic_data in self.knowledge_base["topics"].items():
            for qa in topic_data["questions"]:
                if (keyword.lower() in qa["question_zh"].lower() or
                    keyword.lower() in qa["question_en"].lower() or
                    keyword.lower() in qa["answer_zh"].lower() or
                    keyword.lower() in qa["answer_en"].lower()):

                    results.append({
                        "topic": topic_data["topic_name"],
                        "question_zh": qa["question_zh"],
                        "question_en": qa["question_en"],
                        "difficulty": qa["difficulty"],
                        "tags": qa["tags"]
                    })
        return results


# 命令行交互示例 / Command-line interaction example
if __name__ == "__main__":
    kb = SmartKnowledgeBase()

    print("=" * 80)
    print("📚 智能知识库系统 / Smart Knowledge Base System")
    print("=" * 80)

    # 示例:添加问题 / Example: Add question
    status, similar = kb.add_question(
        topic="Python GIL",
        question_zh="GIL 是什么?",
        question_en="What is GIL?",
        answer_zh="GIL(Global Interpreter Lock)是Python的全局解释器锁...",
        answer_en="GIL (Global Interpreter Lock) is Python's global interpreter lock...",
        difficulty="medium",
        tags=["python", "concurrency", "threading"]
    )

    print(f"\n状态 / Status: {status}")
    if similar:
        print("\n发现相似问题 / Similar questions found:")
        for s in similar:
            print(f"  - {s['question']} (相似度 {s['similarity']:.1%})")

    # 列出所有主题 / List all topics
    print("\n" + "=" * 80)
    print("📋 所有主题 / All Topics")
    print("=" * 80)
    for t in kb.list_topics():
        print(f"{t['topic_name']}: {t['question_count']} 个问题")
