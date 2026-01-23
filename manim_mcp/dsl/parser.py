"""
DSL 解析器
解析 Animation DSL 并提供便捷的访问接口
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class AnimationSpec:
    """单个动画规格"""

    def __init__(self, data: Dict):
        self.anim_id = data["anim_id"]
        self.type = data["type"]
        self.target = data["target"]
        self.params = data.get("params", {})
        self.duration = data.get("duration", 1.0)
        self.parallel = data.get("parallel", [])

    def __repr__(self) -> str:
        return f"Animation({self.anim_id}, type={self.type}, duration={self.duration}s)"


class PhaseSpec:
    """单个阶段规格"""

    def __init__(self, data: Dict):
        self.phase_id = data["phase_id"]
        self.type = data["type"]
        self.audio = data.get("audio")
        self.animations = [AnimationSpec(anim) for anim in data.get("animations", [])]

    def __repr__(self) -> str:
        return f"Phase({self.phase_id}, type={self.type}, {len(self.animations)} animations)"


class SceneSpec:
    """完整场景规格"""

    def __init__(self, data: Dict):
        self.scene_id = data["scene_id"]
        self.metadata = data["metadata"]
        self.timeline = [PhaseSpec(phase) for phase in data.get("timeline", [])]

    @property
    def title(self) -> str:
        return self.metadata.get("title", "")

    @property
    def problem_image(self) -> str:
        return self.metadata.get("problem_image", "")

    @property
    def resolution(self) -> str:
        return self.metadata.get("resolution", "1080p")

    @property
    def frame_rate(self) -> int:
        return self.metadata.get("frame_rate", 60)

    @property
    def theme(self) -> str:
        return self.metadata.get("theme", "dark")

    def get_phase(self, phase_id: str) -> Optional[PhaseSpec]:
        """根据ID获取阶段"""
        for phase in self.timeline:
            if phase.phase_id == phase_id:
                return phase
        return None

    def get_animation(self, anim_id: str) -> Optional[AnimationSpec]:
        """根据ID获取动画"""
        for phase in self.timeline:
            for anim in phase.animations:
                if anim.anim_id == anim_id:
                    return anim
        return None

    def __repr__(self) -> str:
        return f"Scene({self.scene_id}, {len(self.timeline)} phases)"


class DSLParser:
    """DSL 解析器"""

    @staticmethod
    def parse(dsl: Dict) -> SceneSpec:
        """
        解析 DSL 字典

        Args:
            dsl: Animation DSL 字典

        Returns:
            SceneSpec 对象
        """
        return SceneSpec(dsl)

    @staticmethod
    def parse_file(file_path: str) -> SceneSpec:
        """
        解析 DSL 文件

        Args:
            file_path: DSL JSON 文件路径

        Returns:
            SceneSpec 对象
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            dsl = json.load(f)
        return DSLParser.parse(dsl)

    @staticmethod
    def load_template() -> Dict:
        """
        加载 DSL 模板

        Returns:
            模板字典
        """
        template_path = Path(__file__).parent.parent.parent / "templates" / "scene_template.json"
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
