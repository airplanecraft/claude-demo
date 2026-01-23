"""
DSL 验证器
验证 Animation DSL 的合法性（schema + 业务逻辑）
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ValidationResult:
    """验证结果"""

    def __init__(self, valid: bool, errors: List[str], warnings: List[str]):
        self.valid = valid
        self.errors = errors
        self.warnings = warnings
        self.estimated_duration = 0.0
        self.animation_count = 0
        self.phase_count = 0

    def to_dict(self) -> Dict:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "estimated_duration": self.estimated_duration,
            "animation_count": self.animation_count,
            "phase_count": self.phase_count
        }


class DSLValidator:
    """DSL 验证器"""

    def __init__(self, schema_path: Optional[str] = None):
        """
        初始化验证器

        Args:
            schema_path: JSON Schema 文件路径，如果为 None 则使用默认路径
        """
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.json"
        else:
            schema_path = Path(schema_path)

        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)

    def validate(self, dsl: Dict) -> ValidationResult:
        """
        验证 DSL

        Args:
            dsl: Animation DSL 字典

        Returns:
            ValidationResult 对象
        """
        errors = []
        warnings = []

        # 1. JSON Schema 验证
        try:
            jsonschema.validate(dsl, self.schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
            errors.append(f"  Path: {' -> '.join(str(p) for p in e.path)}")
            return ValidationResult(False, errors, warnings)
        except jsonschema.SchemaError as e:
            errors.append(f"Invalid schema: {e.message}")
            return ValidationResult(False, errors, warnings)

        # 2. 业务逻辑验证
        business_errors, business_warnings = self._validate_business_logic(dsl)
        errors.extend(business_errors)
        warnings.extend(business_warnings)

        # 3. 计算统计信息
        result = ValidationResult(len(errors) == 0, errors, warnings)
        result.estimated_duration = self._estimate_duration(dsl)
        result.animation_count = self._count_animations(dsl)
        result.phase_count = len(dsl.get("timeline", []))

        return result

    def _validate_business_logic(self, dsl: Dict) -> Tuple[List[str], List[str]]:
        """
        验证业务逻辑

        Returns:
            (errors, warnings)
        """
        errors = []
        warnings = []

        # 检查资源文件是否存在
        problem_image = dsl.get("metadata", {}).get("problem_image", "")
        if problem_image:
            image_path = Path("input/images") / problem_image
            if not image_path.exists():
                errors.append(f"Problem image not found: {problem_image}")
                errors.append(f"  Expected path: {image_path}")

        # 检查所有动画ID的唯一性
        all_anim_ids = []
        for phase in dsl.get("timeline", []):
            for anim in phase.get("animations", []):
                anim_id = anim.get("anim_id", "")
                if anim_id in all_anim_ids:
                    errors.append(f"Duplicate animation ID: {anim_id}")
                all_anim_ids.append(anim_id)

        # 检查并行动画引用
        for phase in dsl.get("timeline", []):
            for anim in phase.get("animations", []):
                if "parallel" in anim:
                    for parallel_id in anim["parallel"]:
                        if parallel_id not in all_anim_ids:
                            errors.append(
                                f"Invalid parallel animation reference: {parallel_id} "
                                f"in animation {anim.get('anim_id', 'unknown')}"
                            )

        # 检查动画时长
        for phase in dsl.get("timeline", []):
            phase_id = phase.get("phase_id", "unknown")
            for anim in phase.get("animations", []):
                anim_id = anim.get("anim_id", "unknown")
                duration = anim.get("duration", 1.0)

                if duration < 0.1:
                    warnings.append(
                        f"Very short animation duration ({duration}s): "
                        f"{phase_id} -> {anim_id}"
                    )

                if duration > 10.0:
                    warnings.append(
                        f"Very long animation duration ({duration}s): "
                        f"{phase_id} -> {anim_id}"
                    )

        # 检查位置参数
        for phase in dsl.get("timeline", []):
            for anim in phase.get("animations", []):
                params = anim.get("params", {})
                if "position" in params:
                    pos = params["position"]
                    if not isinstance(pos, list) or len(pos) != 3:
                        errors.append(
                            f"Invalid position format in {anim.get('anim_id', 'unknown')}: "
                            f"expected [x, y, z], got {pos}"
                        )

        # 检查必需的资源文件
        for phase in dsl.get("timeline", []):
            for anim in phase.get("animations", []):
                params = anim.get("params", {})

                # 检查图片资源
                if "image" in params:
                    image_path = Path(params["image"])
                    if not image_path.exists():
                        warnings.append(
                            f"Image not found: {params['image']} "
                            f"(animation: {anim.get('anim_id', 'unknown')})"
                        )

        # 检查phase类型和audio的一致性
        for phase in dsl.get("timeline", []):
            phase_type = phase.get("type", "")
            has_audio = "audio" in phase

            if phase_type == "problem_reading" and not has_audio:
                warnings.append(
                    f"Phase '{phase.get('phase_id', 'unknown')}' is of type "
                    f"'problem_reading' but has no audio"
                )

        return errors, warnings

    def _estimate_duration(self, dsl: Dict) -> float:
        """
        估算视频总时长

        Args:
            dsl: Animation DSL 字典

        Returns:
            估算的总时长（秒）
        """
        total_duration = 0.0

        for phase in dsl.get("timeline", []):
            phase_duration = 0.0

            # 计算动画时长（考虑并行）
            # 简化版本：取所有动画时长的最大值
            max_duration = 0.0
            for anim in phase.get("animations", []):
                duration = anim.get("duration", 1.0)
                max_duration = max(max_duration, duration)

            phase_duration += max_duration

            # 添加音频时长
            if "audio" in phase:
                audio_text = phase["audio"].get("text", "")
                # 估算：中文约 0.15 秒/字
                audio_duration = len(audio_text) * 0.15
                phase_duration = max(phase_duration, audio_duration)

            total_duration += phase_duration

        return round(total_duration, 2)

    def _count_animations(self, dsl: Dict) -> int:
        """
        统计动画数量

        Args:
            dsl: Animation DSL 字典

        Returns:
            动画总数
        """
        count = 0
        for phase in dsl.get("timeline", []):
            count += len(phase.get("animations", []))
        return count


def validate_dsl_file(file_path: str) -> ValidationResult:
    """
    验证 DSL 文件

    Args:
        file_path: DSL JSON 文件路径

    Returns:
        ValidationResult 对象
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            dsl = json.load(f)

        validator = DSLValidator()
        return validator.validate(dsl)

    except FileNotFoundError:
        return ValidationResult(
            False,
            [f"File not found: {file_path}"],
            []
        )
    except json.JSONDecodeError as e:
        return ValidationResult(
            False,
            [f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}"],
            []
        )
    except Exception as e:
        return ValidationResult(
            False,
            [f"Unexpected error: {str(e)}"],
            []
        )
