"""
DSL to Manim Converter
将 Animation DSL 转换为完整的 Manim Python 代码
"""

import os
from typing import Dict, List, Optional
from pathlib import Path
from ..dsl.parser import SceneSpec, PhaseSpec, AnimationSpec
from .animation_factory import AnimationFactory


class DSLToManimConverter:
    """DSL → Manim 转换器"""

    def __init__(self, scene_spec: SceneSpec):
        """
        初始化转换器

        Args:
            scene_spec: SceneSpec 对象
        """
        self.spec = scene_spec
        self.factory = AnimationFactory()

    def generate_scene_code(self) -> str:
        """
        生成完整的 Manim Scene 代码

        Returns:
            完整的 Python 代码字符串
        """
        code_parts = []

        # 1. Imports and header
        code_parts.append(self._generate_header())

        # 2. Global configuration
        code_parts.append(self._generate_config())

        # 3. Audio helper functions
        code_parts.append(self._generate_audio_helpers())

        # 4. Scene class
        code_parts.append(self._generate_scene_class())

        return "\n\n".join(code_parts)

    def _generate_header(self) -> str:
        """生成头部 imports"""
        return """import os
import asyncio
import edge_tts
from manim import *"""

    def _generate_config(self) -> str:
        """生成全局配置"""
        resolution = self.spec.resolution
        frame_rate = self.spec.frame_rate

        # 解析分辨率
        if resolution == "1080p":
            height, width = 1080, 1920
        elif resolution == "720p":
            height, width = 720, 1280
        elif resolution == "4k":
            height, width = 2160, 3840
        else:
            height, width = 1080, 1920

        config_code = f"""# Global Configuration
config.disable_caching = True
config.pixel_height = {height}
config.pixel_width = {width}
config.frame_rate = {frame_rate}

# Layout Constants
POS_ANIM_CENTER = [3.5, 2.0, 0]      # Animation center (right upper)
POS_TEXT_BASE = [3.5, -3.0, 0]       # Text base (right lower)
VIDEO_LEFT_PANEL_X = -3.5            # Problem image (left)
SEPARATOR_X = 0.0                    # Separator line

# Color scheme
COLOR_BG = "#415049"
COLOR_GRID = "#253D32"
COLOR_TEXT_MAIN = "#F0F5F2"
COLOR_MATH_A = "#FFFFFF"
COLOR_MATH_B = "#A8D8B9"
COLOR_HIGHLIGHT = "#FFD700"
COLOR_SUBTITLE = "#FFFFFF"
COLOR_SUB_BG = "#0A140F"
COLOR_SEPARATOR = "#FFFFFF"

# Font configuration
FONT_NAME = "Heiti SC"
FONT_SIZE_BODY = 24
FONT_SIZE_MATH = 32
FONT_SIZE_SUB = 24

# Audio configuration
TTS_CACHE_DIR = "tts_cache"
EDGE_VOICE = "zh-CN-XiaoxiaoNeural"
MAC_VOICE = "Tingting"
TTS_RATE = "+10%"
SECONDS_PER_CHAR = 0.15
AUDIO_BUFFER = 0.3"""

        return config_code

    def _generate_audio_helpers(self) -> str:
        """生成音频辅助函数"""
        return '''# Audio Helper Functions
async def _run_edge_tts(text, filename):
    """使用 edge_tts 生成语音"""
    communicate = edge_tts.Communicate(text, EDGE_VOICE, rate=TTS_RATE)
    await communicate.save(filename)

def generate_audio_file(text, filename_mp3):
    """
    生成音频文件（优先使用 edge_tts，失败则使用 Mac say 命令）
    """
    clean_text = text.replace("\\n", " ").strip()
    abs_mp3 = os.path.abspath(filename_mp3)
    abs_m4a = abs_mp3.replace(".mp3", ".m4a")

    # 尝试使用 edge_tts
    try:
        asyncio.run(_run_edge_tts(clean_text, abs_mp3))
        if os.path.exists(abs_mp3) and os.path.getsize(abs_mp3) > 1000:
            return abs_mp3
    except Exception as e:
        print(f"  [TTS] edge_tts failed: {str(e)}")

    # 回退到 Mac say 命令
    try:
        os.system(f'say -v "{MAC_VOICE}" -o "{abs_m4a}" "{clean_text}"')
        if os.path.exists(abs_m4a) and os.path.getsize(abs_m4a) > 0:
            return abs_m4a
    except Exception as e:
        print(f"  [TTS] Mac say failed: {str(e)}")

    return None

def prepare_audio(phase_id, audio_text):
    """预生成音频文件"""
    if not os.path.exists(TTS_CACHE_DIR):
        os.makedirs(TTS_CACHE_DIR)

    audio_file = os.path.join(TTS_CACHE_DIR, f"{phase_id}.mp3")
    return generate_audio_file(audio_text, audio_file)'''

    def _generate_scene_class(self) -> str:
        """生成 Scene 类"""
        class_name = self._get_class_name()

        code_lines = []
        code_lines.append(f"class {class_name}(Scene):")
        code_lines.append(f'    """')
        code_lines.append(f'    {self.spec.title}')
        code_lines.append(f'    Auto-generated from Animation DSL')
        code_lines.append(f'    """')
        code_lines.append("")
        code_lines.append("    def construct(self):")
        code_lines.append(f'        print("\\n" + "=" * 60)')
        code_lines.append(f'        print("Rendering: {self.spec.title}")')
        code_lines.append(f'        print("=" * 60)')
        code_lines.append("")

        # 设置背景
        code_lines.append("        # Setup background")
        code_lines.append("        self.camera.background_color = COLOR_BG")
        code_lines.append("        grid = NumberPlane(")
        code_lines.append("            x_range=[-8, 8, 1],")
        code_lines.append("            y_range=[-5, 5, 1],")
        code_lines.append("            background_line_style={")
        code_lines.append('                "stroke_color": COLOR_GRID,')
        code_lines.append('                "stroke_width": 2,')
        code_lines.append('                "stroke_opacity": 0.5')
        code_lines.append("            },")
        code_lines.append('            axis_config={"stroke_width": 0}')
        code_lines.append("        )")
        code_lines.append("        self.add(grid)")
        code_lines.append("")

        # 生成时间轴代码
        code_lines.append("        # Timeline execution")
        for i, phase in enumerate(self.spec.timeline, 1):
            code_lines.append(f"        print(f'  Phase {i}/{len(self.spec.timeline)}: {phase.phase_id}')")
            code_lines.extend(self._generate_phase_code(phase))
            code_lines.append("")

        code_lines.append(f'        print("=" * 60)')
        code_lines.append(f'        print("Rendering complete")')
        code_lines.append(f'        print("=" * 60)')

        return "\n".join(code_lines)

    def _generate_phase_code(self, phase: PhaseSpec) -> List[str]:
        """生成单个阶段的代码"""
        code_lines = []
        code_lines.append("")
        code_lines.append(f"        # Phase: {phase.phase_id} (type: {phase.type})")

        # 处理音频
        if phase.audio:
            audio_text = phase.audio.get("text", "")
            code_lines.append(f"        # Prepare audio")
            code_lines.append(f"        audio_path = prepare_audio('{phase.phase_id}', '{audio_text}')")
            code_lines.append("")

        # 处理动画
        if phase.animations:
            for anim in phase.animations:
                anim_code = self.factory.generate_animation_code(anim)
                code_lines.append(anim_code)
                code_lines.append("")

        # 播放音频
        if phase.audio:
            audio_text = phase.audio.get("text", "")
            audio_duration = len(audio_text) * 0.15 + 0.3
            code_lines.append(f"        # Play audio")
            code_lines.append(f"        if audio_path and os.path.exists(audio_path):")
            code_lines.append(f"            self.add_sound(audio_path)")
            code_lines.append(f"            self.wait(max(2.0, {audio_duration}))")
            code_lines.append(f"        else:")
            code_lines.append(f"            self.wait(max(1.5, {audio_duration * 0.6}))")

        return code_lines

    def _get_class_name(self) -> str:
        """生成类名"""
        # 从 scene_id 生成类名
        # 例如: problem_1_solution -> SolutionVideoProblem1
        parts = self.spec.scene_id.split("_")
        class_name = "".join(p.capitalize() for p in parts)
        return class_name


def convert_dsl_to_manim(scene_spec: SceneSpec) -> str:
    """
    便捷函数：将 SceneSpec 转换为 Manim 代码

    Args:
        scene_spec: SceneSpec 对象

    Returns:
        Manim Python 代码字符串
    """
    converter = DSLToManimConverter(scene_spec)
    return converter.generate_scene_code()


def convert_dsl_file_to_manim(dsl_file_path: str) -> str:
    """
    便捷函数：从 DSL 文件生成 Manim 代码

    Args:
        dsl_file_path: DSL JSON 文件路径

    Returns:
        Manim Python 代码字符串
    """
    from ..dsl.parser import DSLParser

    scene_spec = DSLParser.parse_file(dsl_file_path)
    return convert_dsl_to_manim(scene_spec)
