"""
Animation Factory
根据 DSL 动画类型创建对应的 Manim 代码
"""

from typing import Dict, Any, Optional
from ..dsl.parser import AnimationSpec


class AnimationFactory:
    """动画工厂：将 DSL 动画规格转换为 Manim 代码"""

    # 布局常量（与模板一致）
    POS_ANIM_CENTER = [3.5, 2.0, 0]
    POS_TEXT_BASE = [3.5, -3.0, 0]
    VIDEO_LEFT_PANEL_X = -3.5

    def __init__(self):
        self.object_registry = {}  # 追踪已创建的对象

    def generate_animation_code(self, anim: AnimationSpec) -> str:
        """
        生成单个动画的 Manim 代码

        Args:
            anim: AnimationSpec 对象

        Returns:
            Manim 代码字符串
        """
        anim_type = anim.type
        target = anim.target
        params = anim.params
        duration = anim.duration

        # 根据动画类型生成代码
        if anim_type == "show_text":
            return self._generate_show_text(target, params, duration)
        elif anim_type == "show_math":
            return self._generate_show_math(target, params, duration)
        elif anim_type == "show_image":
            return self._generate_show_image(target, params, duration)
        elif anim_type == "fade_in":
            return self._generate_fade_in(target, params, duration)
        elif anim_type == "fade_out":
            return self._generate_fade_out(target, params, duration)
        elif anim_type == "move_to":
            return self._generate_move_to(target, params, duration)
        elif anim_type == "scale":
            return self._generate_scale(target, params, duration)
        elif anim_type == "rotate":
            return self._generate_rotate(target, params, duration)
        elif anim_type == "highlight":
            return self._generate_highlight(target, params, duration)
        elif anim_type == "indicate":
            return self._generate_indicate(target, params, duration)
        elif anim_type == "create":
            return self._generate_create(target, params, duration)
        elif anim_type == "write":
            return self._generate_write(target, params, duration)
        elif anim_type == "transform":
            return self._generate_transform(target, params, duration)
        else:
            return f"        # Unknown animation type: {anim_type}"

    def _generate_show_text(self, target: str, params: Dict, duration: float) -> str:
        """生成显示文字的代码"""
        text = params.get("text", "")
        position = params.get("position", self.POS_TEXT_BASE)
        font_size = params.get("font_size", 24)
        color = params.get("color", "#FFD700")
        has_box = params.get("box", False)

        code_lines = []
        code_lines.append(f"        # Create text: {target}")
        code_lines.append(f"        {target} = Text(")
        code_lines.append(f"            '{text}',")
        code_lines.append(f"            font='Heiti SC',")
        code_lines.append(f"            font_size={font_size},")
        code_lines.append(f"            color='{color}'")
        code_lines.append(f"        ).move_to({position})")

        if has_box:
            box_var = f"{target}_box"
            code_lines.append(f"        {box_var} = SurroundingRectangle(")
            code_lines.append(f"            {target},")
            code_lines.append(f"            color='{color}',")
            code_lines.append(f"            buff=0.2")
            code_lines.append(f"        )")
            code_lines.append(f"        self.play(Write({target}), Create({box_var}), run_time={duration})")
            self.object_registry[f"{target}_box"] = True
        else:
            code_lines.append(f"        self.play(Write({target}), run_time={duration})")

        self.object_registry[target] = True
        return "\n".join(code_lines)

    def _generate_show_math(self, target: str, params: Dict, duration: float) -> str:
        """生成显示数学公式的代码"""
        latex = params.get("latex", "")
        position = params.get("position", self.POS_ANIM_CENTER)
        font_size = params.get("font_size", 32)
        color = params.get("color", "#FFFFFF")

        code_lines = []
        code_lines.append(f"        # Create math formula: {target}")
        code_lines.append(f"        {target} = MathTex(")
        code_lines.append(f"            r'{latex}',")
        code_lines.append(f"            font_size={font_size},")
        code_lines.append(f"            color='{color}'")
        code_lines.append(f"        ).move_to({position})")
        code_lines.append(f"        self.play(Write({target}), run_time={duration})")

        self.object_registry[target] = True
        return "\n".join(code_lines)

    def _generate_show_image(self, target: str, params: Dict, duration: float) -> str:
        """生成显示图片的代码"""
        image = params.get("image", "")
        position = params.get("position", [0, 0, 0])
        width = params.get("width")
        height = params.get("height")
        scale_factor = params.get("scale_factor")

        code_lines = []
        code_lines.append(f"        # Create image: {target}")
        code_lines.append(f"        if os.path.exists('{image}'):")
        code_lines.append(f"            {target} = ImageMobject('{image}')")

        # 处理缩放
        if scale_factor:
            code_lines.append(f"            {target}.scale({scale_factor})")
        elif width and height:
            code_lines.append(f"            {target}.stretch_to_fit_width({width})")
            code_lines.append(f"            {target}.stretch_to_fit_height({height})")
        elif width:
            code_lines.append(f"            {target}.scale_to_fit_width({width})")
        elif height:
            code_lines.append(f"            {target}.scale_to_fit_height({height})")

        code_lines.append(f"            {target}.move_to({position})")
        code_lines.append(f"            self.play(FadeIn({target}), run_time={duration})")
        code_lines.append(f"        else:")
        code_lines.append(f"            {target} = Text('Image not found: {image}', color=RED).move_to({position})")
        code_lines.append(f"            self.play(FadeIn({target}), run_time={duration})")

        self.object_registry[target] = True
        return "\n".join(code_lines)

    def _generate_fade_in(self, target: str, params: Dict, duration: float) -> str:
        """生成淡入动画"""
        # 如果目标是图片，需要先创建
        image = params.get("image")
        if image:
            return self._generate_show_image(target, params, duration)

        # 否则假设对象已存在
        return f"        self.play(FadeIn({target}), run_time={duration})"

    def _generate_fade_out(self, target: str, params: Dict, duration: float) -> str:
        """生成淡出动画"""
        if target in self.object_registry:
            return f"        self.play(FadeOut({target}), run_time={duration})"
        else:
            return f"        # Warning: {target} not found in registry"

    def _generate_move_to(self, target: str, params: Dict, duration: float) -> str:
        """生成移动动画"""
        position = params.get("position", [0, 0, 0])
        width = params.get("width")

        code_lines = []
        if width:
            code_lines.append(f"        self.play(")
            code_lines.append(f"            {target}.animate.scale_to_fit_width({width}).move_to({position}),")
            code_lines.append(f"            run_time={duration}")
            code_lines.append(f"        )")
        else:
            code_lines.append(f"        self.play({target}.animate.move_to({position}), run_time={duration})")

        return "\n".join(code_lines)

    def _generate_scale(self, target: str, params: Dict, duration: float) -> str:
        """生成缩放动画"""
        scale_factor = params.get("scale_factor", 1.0)
        return f"        self.play({target}.animate.scale({scale_factor}), run_time={duration})"

    def _generate_rotate(self, target: str, params: Dict, duration: float) -> str:
        """生成旋转动画"""
        angle = params.get("angle", 0)
        return f"        self.play({target}.animate.rotate({angle}), run_time={duration})"

    def _generate_highlight(self, target: str, params: Dict, duration: float) -> str:
        """生成高亮动画"""
        color = params.get("color", "#FFD700")
        stroke_width = params.get("stroke_width", 4)

        code_lines = []
        highlight_var = f"{target}_highlight"
        code_lines.append(f"        # Highlight: {target}")
        code_lines.append(f"        {highlight_var} = SurroundingRectangle(")
        code_lines.append(f"            {target},")
        code_lines.append(f"            color='{color}',")
        code_lines.append(f"            stroke_width={stroke_width},")
        code_lines.append(f"            buff=0.1")
        code_lines.append(f"        )")
        code_lines.append(f"        self.play(Create({highlight_var}), run_time={duration})")

        self.object_registry[highlight_var] = True
        return "\n".join(code_lines)

    def _generate_indicate(self, target: str, params: Dict, duration: float) -> str:
        """生成指示动画"""
        color = params.get("color", "#FFD700")
        return f"        self.play(Indicate({target}, color='{color}'), run_time={duration})"

    def _generate_create(self, target: str, params: Dict, duration: float) -> str:
        """生成创建动画"""
        return f"        self.play(Create({target}), run_time={duration})"

    def _generate_write(self, target: str, params: Dict, duration: float) -> str:
        """生成书写动画"""
        # 检查是否需要创建对象
        if "text" in params:
            return self._generate_show_text(target, params, duration)
        elif "latex" in params:
            return self._generate_show_math(target, params, duration)
        else:
            return f"        self.play(Write({target}), run_time={duration})"

    def _generate_transform(self, target: str, params: Dict, duration: float) -> str:
        """生成变换动画"""
        from_obj = params.get("from")
        to_obj = params.get("to")

        if from_obj and to_obj:
            return f"        self.play(Transform({from_obj}, {to_obj}), run_time={duration})"
        else:
            return f"        # Transform requires 'from' and 'to' parameters"
