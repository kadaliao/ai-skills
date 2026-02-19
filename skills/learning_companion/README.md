# Learning Companion

An intelligent learning system library for managing knowledge and tracking learning progress with semantic deduplication and spaced repetition.

## Features

- **Smart Knowledge Base** - Store and manage learning materials with automatic duplicate detection
- **Learning Records** - Track learning progress with Ebbinghaus forgetting curve spaced repetition
- **Coordination Manager** - Manage multiple learning modes (active learning, review, auto-teaching)

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Smart Knowledge Base

```python
from learning_companion import SmartKnowledgeBase

# Initialize knowledge base
kb = SmartKnowledgeBase(kb_file="/path/to/knowledge_base.json")

# Add a question with automatic duplicate detection
status, similar = kb.add_question(
    topic="Python Concurrency",
    question_zh="什么是 GIL？",
    question_en="What is the GIL?",
    answer_zh="全局解释器锁...",
    answer_en="Global Interpreter Lock...",
    difficulty="medium",
    tags=["python", "concurrency"]
)

if status == "SIMILAR_FOUND":
    print("Similar questions found:")
    for item in similar:
        print(f"  - {item['question']} ({item['similarity']:.1%})")

# Search knowledge
results = kb.search_questions("GIL")

# List topics
topics = kb.list_topics()
```

### 2. Learning Records

```python
from learning_companion import LearningRecords

# Initialize learning records for a student
lr = LearningRecords(
    student_name="John",
    records_file="/path/to/learning_records.json"
)

# Record a learning session
lr.add_qa_record(
    topic="Python Concurrency",
    question_zh="什么是 GIL？",
    question_en="What is the GIL?",
    user_answer="全局解释器锁",
    correct_answer_zh="全局解释器锁（Global Interpreter Lock）是...",
    correct_answer_en="The Global Interpreter Lock (GIL) is...",
    score=9,  # 0-10
    notes="Good understanding of the concept"
)

# Get pending reviews using Ebbinghaus forgetting curve
pending = lr.get_pending_reviews()
print(f"Items to review: {len(pending)}")

# Get learning statistics
stats = lr.get_statistics()
print(f"Accuracy: {stats['correct_answers']}/{stats['total_questions']}")
print(f"Average score: {stats['average_score']}/10")
```

### 3. Coordination Manager

```python
from learning_companion import CoordinationManager

# Initialize coordination manager
cm = CoordinationManager(state_file="/path/to/coordination_state.json")

# Mark active learning in progress
cm.start_active_learning(["Python Concurrency"])

# Check if system should suppress auto-teaching
if not cm.should_suppress_auto_teaching():
    # Proceed with auto-teaching
    pass

# Mark user is done learning
cm.end_active_learning()
```

## Configuration

All classes accept a file path parameter for persistent storage:

```python
# Use custom paths for different data stores
kb = SmartKnowledgeBase(kb_file="/my/custom/path/knowledge_base.json")
lr = LearningRecords(student_name="Alice", records_file="/my/path/records.json")
cm = CoordinationManager(state_file="/my/path/state.json")
```

## Data Structure

### Knowledge Base

```json
{
  "topics": {
    "Topic Name": {
      "questions": [
        {
          "id": "unique-id",
          "question_zh": "中文问题",
          "question_en": "English question",
          "answer_zh": "中文答案",
          "answer_en": "English answer",
          "difficulty": "easy|medium|hard",
          "tags": ["tag1", "tag2"],
          "created_at": "2025-02-19T..."
        }
      ]
    }
  },
  "metadata": {
    "created_at": "2025-02-19T..."
  }
}
```

### Learning Records

```json
{
  "student_name": "John",
  "created_at": "2025-02-19T...",
  "learning_sessions": [
    {
      "topic": "Topic Name",
      "question_zh": "问题",
      "question_en": "Question",
      "user_answer": "用户答案",
      "score": 9,
      "mastery_level": "good",
      "timestamp": "2025-02-19T..."
    }
  ],
  "review_schedule": [
    {
      "question_id": "id",
      "next_review": "2025-02-20T...",
      "review_count": 1
    }
  ],
  "statistics": {
    "total_questions": 10,
    "correct_answers": 9,
    "average_score": 9.2
  }
}
```

## API Reference

### SmartKnowledgeBase

- `add_question(topic, question_zh, question_en, answer_zh, answer_en, difficulty, tags, force=False)` - Add a question with duplicate detection
- `search_questions(keyword)` - Search questions by keyword
- `get_topic_questions(topic)` - Get all questions in a topic
- `list_topics()` - List all topics
- `remove_question(topic, question_id)` - Remove a question
- `get_question(topic, question_id)` - Get specific question

### LearningRecords

- `add_qa_record(topic, question_zh, question_en, user_answer, correct_answer_zh, correct_answer_en, score, notes)` - Record a learning session
- `get_pending_reviews(days_ahead=7)` - Get items needing review
- `get_statistics()` - Get learning statistics
- `get_weak_topics()` - Get topics with low accuracy
- `calculate_next_review(mastery_level)` - Get next review dates for a mastery level

### CoordinationManager

- `start_active_learning(topics)` - Mark active learning session started
- `end_active_learning()` - Mark active learning session ended
- `should_suppress_auto_teaching()` - Check if auto-teaching should be suppressed
- `set_state(state)` - Manually set system state
- `get_state()` - Get current system state

## Use Cases

This library is designed for:

- **Learning Management Systems** - Track student progress and schedule reviews
- **AI Tutors** - Manage knowledge base and prevent duplicate content
- **Study Apps** - Implement spaced repetition with multiple learning modes
- **Educational Chatbots** - Coordinate different conversation modes
- **Personalized Learning** - Track and analyze learning patterns

## License

MIT
