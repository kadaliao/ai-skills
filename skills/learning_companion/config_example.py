# Example configuration for using learning_companion in different environments

import os
from pathlib import Path

# Example 1: Local file storage
class LocalConfig:
    """Store learning data in local files"""
    DATA_DIR = Path.home() / ".learning_companion"

    KB_FILE = DATA_DIR / "knowledge_base.json"
    RECORDS_FILE = DATA_DIR / "learning_records.json"
    STATE_FILE = DATA_DIR / "coordination_state.json"

    @classmethod
    def initialize(cls):
        """Create data directory if it doesn't exist"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)


# Example 2: Environment-based configuration
class Config:
    """Flexible configuration from environment variables"""

    DATA_DIR = Path(os.getenv("LEARNING_COMPANION_DIR", "/tmp/learning_companion"))

    KB_FILE = Path(os.getenv("KB_FILE", DATA_DIR / "knowledge_base.json"))
    RECORDS_FILE = Path(os.getenv("RECORDS_FILE", DATA_DIR / "learning_records.json"))
    STATE_FILE = Path(os.getenv("STATE_FILE", DATA_DIR / "coordination_state.json"))

    @classmethod
    def initialize(cls):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)


# Example 3: Per-student configuration
class StudentConfig:
    """Configuration for individual students"""

    def __init__(self, student_id: str, base_dir: Path = Path.home() / ".learning"):
        self.student_id = student_id
        self.data_dir = base_dir / student_id
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.kb_file = self.data_dir / "knowledge_base.json"
        self.records_file = self.data_dir / "learning_records.json"
        self.state_file = self.data_dir / "coordination_state.json"


# Example usage:
if __name__ == "__main__":
    from learning_companion import SmartKnowledgeBase, LearningRecords, CoordinationManager

    # Option 1: Use local config
    LocalConfig.initialize()
    kb = SmartKnowledgeBase(kb_file=str(LocalConfig.KB_FILE))

    # Option 2: Use environment-based config
    Config.initialize()
    lr = LearningRecords(
        student_name="Alice",
        records_file=str(Config.RECORDS_FILE)
    )

    # Option 3: Per-student config
    student_config = StudentConfig("student_001")
    cm = CoordinationManager(state_file=str(student_config.state_file))

    print("Learning companion initialized!")
