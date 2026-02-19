"""
三个角色协调管理器
Coordination Manager for Three Roles

角色:
1. Anki 复习助手 - 复习已学知识
2. 面试准备学习伙伴 - 推送新知识
3. mini (主对话) - 响应主动学习

协调策略:
- 主对话优先，定时任务让路
- 用户主动学习时，定时任务暂停
- 用户休息时，定时任务恢复
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List


class CoordinationManager:
    """协调管理器 / Coordination Manager"""

    STATE_FILE = "/workspace/group/learning_companion/coordination_state.json"

    # 状态定义
    STATE_IDLE = "idle"                    # 空闲，可以推送
    STATE_ACTIVE_LEARNING = "active_learning"  # 主动学习中
    STATE_REVIEWING = "reviewing"          # 复习中
    STATE_AUTO_TEACHING = "auto_teaching"  # 自动教学中

    def __init__(self):
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """加载状态 / Load state"""
        try:
            with open(self.STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._default_state()

    def _default_state(self) -> dict:
        """默认状态 / Default state"""
        return {
            "current_state": self.STATE_IDLE,
            "learning_in_progress": False,
            "active_topics": [],
            "last_activity": None,
            "suppress_until": None,
            "user_preference": {
                "pause_auto_learning": False,
                "pause_auto_review": False
            },
            "metadata": {
                "last_main_conversation": None,
                "last_anki_review": None,
                "last_auto_teaching": None
            }
        }

    def _save_state(self):
        """保存状态 / Save state"""
        with open(self.STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    # ========================================================================
    # 主对话 (mini) 使用的方法
    # ========================================================================

    def start_active_learning(self, topics: List[str]):
        """
        开始主动学习 / Start active learning

        Args:
            topics: 学习主题列表 / List of learning topics
        """
        self.state["current_state"] = self.STATE_ACTIVE_LEARNING
        self.state["learning_in_progress"] = True
        self.state["active_topics"] = topics
        self.state["last_activity"] = datetime.now().isoformat()
        self.state["metadata"]["last_main_conversation"] = datetime.now().isoformat()
        self._save_state()
        print(f"✅ 主动学习开始: {', '.join(topics)}")

    def end_active_learning(self):
        """
        结束主动学习 / End active learning
        """
        self.state["current_state"] = self.STATE_IDLE
        self.state["learning_in_progress"] = False
        self.state["active_topics"] = []
        self.state["last_activity"] = datetime.now().isoformat()
        self._save_state()
        print("✅ 主动学习结束")

    def update_activity(self):
        """
        更新最后活动时间 / Update last activity time
        用于检测用户是否还在活跃
        """
        self.state["last_activity"] = datetime.now().isoformat()
        self._save_state()

    def check_auto_timeout(self, timeout_minutes: int = 30) -> bool:
        """
        检查是否自动超时 / Check if auto timeout

        Args:
            timeout_minutes: 超时分钟数 / Timeout in minutes

        Returns:
            是否超时 / Whether timed out
        """
        if not self.state["last_activity"]:
            return True

        last_activity = datetime.fromisoformat(self.state["last_activity"])
        now = datetime.now()

        if (now - last_activity).total_seconds() > timeout_minutes * 60:
            # 自动结束学习状态
            if self.state["learning_in_progress"]:
                self.end_active_learning()
            return True

        return False

    # ========================================================================
    # Anki 复习助手使用的方法
    # ========================================================================

    def can_anki_review(self) -> tuple[bool, str]:
        """
        检查是否可以进行 Anki 复习 / Check if Anki review is allowed

        Returns:
            (是否允许, 原因) / (allowed, reason)
        """
        # 检查用户偏好
        if self.state["user_preference"].get("pause_auto_review", False):
            return False, "用户暂停了自动复习"

        # 检查抑制时间
        if self.state.get("suppress_until"):
            suppress_until = datetime.fromisoformat(self.state["suppress_until"])
            if datetime.now() < suppress_until:
                return False, f"抑制到 {suppress_until.strftime('%H:%M')}"

        # 检查当前状态
        state = self.state["current_state"]
        if state == self.STATE_ACTIVE_LEARNING:
            return False, "用户正在主动学习"
        elif state == self.STATE_AUTO_TEACHING:
            return False, "学习伙伴正在教学"

        # 检查超时（30分钟无活动自动恢复）
        self.check_auto_timeout(30)

        return True, "允许复习"

    def start_anki_review(self):
        """开始 Anki 复习 / Start Anki review"""
        self.state["current_state"] = self.STATE_REVIEWING
        self.state["metadata"]["last_anki_review"] = datetime.now().isoformat()
        self._save_state()

    def end_anki_review(self):
        """结束 Anki 复习 / End Anki review"""
        self.state["current_state"] = self.STATE_IDLE
        self._save_state()

    # ========================================================================
    # 面试准备学习伙伴使用的方法
    # ========================================================================

    def can_auto_teach(self) -> tuple[bool, str]:
        """
        检查是否可以自动教学 / Check if auto teaching is allowed

        Returns:
            (是否允许, 原因) / (allowed, reason)
        """
        # 检查用户偏好
        if self.state["user_preference"].get("pause_auto_learning", False):
            return False, "用户暂停了自动学习"

        # 检查抑制时间
        if self.state.get("suppress_until"):
            suppress_until = datetime.fromisoformat(self.state["suppress_until"])
            if datetime.now() < suppress_until:
                return False, f"抑制到 {suppress_until.strftime('%H:%M')}"

        # 检查当前状态
        state = self.state["current_state"]
        if state == self.STATE_ACTIVE_LEARNING:
            return False, "用户正在主动学习"
        elif state == self.STATE_REVIEWING:
            return False, "用户正在复习"

        # 检查超时
        self.check_auto_timeout(30)

        return True, "允许教学"

    def start_auto_teaching(self, topic: str):
        """开始自动教学 / Start auto teaching"""
        self.state["current_state"] = self.STATE_AUTO_TEACHING
        self.state["active_topics"] = [topic]
        self.state["metadata"]["last_auto_teaching"] = datetime.now().isoformat()
        self._save_state()

    def end_auto_teaching(self):
        """结束自动教学 / End auto teaching"""
        self.state["current_state"] = self.STATE_IDLE
        self.state["active_topics"] = []
        self._save_state()

    # ========================================================================
    # 用户控制方法
    # ========================================================================

    def pause_auto_learning(self, duration_hours: Optional[int] = None):
        """
        暂停自动学习 / Pause auto learning

        Args:
            duration_hours: 暂停时长(小时)，None表示永久 / Duration in hours, None for permanent
        """
        self.state["user_preference"]["pause_auto_learning"] = True

        if duration_hours:
            suppress_until = datetime.now() + timedelta(hours=duration_hours)
            self.state["suppress_until"] = suppress_until.isoformat()
            print(f"✅ 自动学习已暂停 {duration_hours} 小时")
        else:
            print("✅ 自动学习已永久暂停")

        self._save_state()

    def resume_auto_learning(self):
        """恢复自动学习 / Resume auto learning"""
        self.state["user_preference"]["pause_auto_learning"] = False
        self.state["suppress_until"] = None
        self._save_state()
        print("✅ 自动学习已恢复")

    def pause_auto_review(self, duration_hours: Optional[int] = None):
        """
        暂停自动复习 / Pause auto review

        Args:
            duration_hours: 暂停时长(小时)，None表示永久 / Duration in hours, None for permanent
        """
        self.state["user_preference"]["pause_auto_review"] = True

        if duration_hours:
            suppress_until = datetime.now() + timedelta(hours=duration_hours)
            self.state["suppress_until"] = suppress_until.isoformat()
            print(f"✅ 自动复习已暂停 {duration_hours} 小时")
        else:
            print("✅ 自动复习已永久暂停")

        self._save_state()

    def resume_auto_review(self):
        """恢复自动复习 / Resume auto review"""
        self.state["user_preference"]["pause_auto_review"] = False
        self.state["suppress_until"] = None
        self._save_state()
        print("✅ 自动复习已恢复")

    def get_status(self) -> dict:
        """
        获取当前状态 / Get current status

        Returns:
            状态信息 / Status info
        """
        return {
            "当前状态": self.state["current_state"],
            "正在学习": self.state["learning_in_progress"],
            "活跃主题": self.state["active_topics"],
            "最后活动": self.state["last_activity"],
            "暂停自动学习": self.state["user_preference"]["pause_auto_learning"],
            "暂停自动复习": self.state["user_preference"]["pause_auto_review"],
            "抑制到": self.state.get("suppress_until")
        }


# ============================================================================
# 命令行测试 / Command-line test
# ============================================================================

if __name__ == "__main__":
    cm = CoordinationManager()

    print("=" * 80)
    print("协调管理器测试 / Coordination Manager Test")
    print("=" * 80)

    # 显示初始状态
    print("\n📊 初始状态:")
    for k, v in cm.get_status().items():
        print(f"  {k}: {v}")

    # 测试主动学习
    print("\n" + "━" * 80)
    print("🎓 模拟：用户开始主动学习 SQL")
    cm.start_active_learning(["SQL 连接类型"])

    # 检查 Anki 是否可以运行
    can_review, reason = cm.can_anki_review()
    print(f"\n❓ Anki 复习助手可以运行吗? {'✅ 是' if can_review else '❌ 否'}")
    print(f"   原因: {reason}")

    # 检查学习伙伴是否可以运行
    can_teach, reason = cm.can_auto_teach()
    print(f"\n❓ 学习伙伴可以运行吗? {'✅ 是' if can_teach else '❌ 否'}")
    print(f"   原因: {reason}")

    # 结束主动学习
    print("\n" + "━" * 80)
    print("🛑 模拟：用户结束主动学习")
    cm.end_active_learning()

    # 再次检查
    can_review, reason = cm.can_anki_review()
    print(f"\n❓ Anki 复习助手可以运行吗? {'✅ 是' if can_review else '❌ 否'}")
    print(f"   原因: {reason}")

    can_teach, reason = cm.can_auto_teach()
    print(f"\n❓ 学习伙伴可以运行吗? {'✅ 是' if can_teach else '❌ 否'}")
    print(f"   原因: {reason}")

    # 测试暂停功能
    print("\n" + "━" * 80)
    print("⏸️  模拟：暂停自动学习 2 小时")
    cm.pause_auto_learning(duration_hours=2)

    can_teach, reason = cm.can_auto_teach()
    print(f"\n❓ 学习伙伴可以运行吗? {'✅ 是' if can_teach else '❌ 否'}")
    print(f"   原因: {reason}")

    # 恢复
    print("\n" + "━" * 80)
    print("▶️  模拟：恢复自动学习")
    cm.resume_auto_learning()

    can_teach, reason = cm.can_auto_teach()
    print(f"\n❓ 学习伙伴可以运行吗? {'✅ 是' if can_teach else '❌ 否'}")
    print(f"   原因: {reason}")

    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)
