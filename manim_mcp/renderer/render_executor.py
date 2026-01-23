"""
Render Executor
执行 Manim 渲染命令并处理输出
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional
from ..dsl.parser import SceneSpec
from .dsl_to_manim import convert_dsl_to_manim


class RenderResult:
    """渲染结果"""

    def __init__(self, success: bool):
        self.success = success
        self.video_path: Optional[str] = None
        self.python_code_path: Optional[str] = None
        self.render_time: float = 0.0
        self.video_duration: float = 0.0
        self.file_size_mb: float = 0.0
        self.stdout: str = ""
        self.stderr: str = ""
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "video_path": self.video_path,
            "python_code_path": self.python_code_path,
            "render_time": self.render_time,
            "video_duration": self.video_duration,
            "file_size_mb": self.file_size_mb,
            "error": self.error,
            "stdout": self.stdout if not self.success else "",
            "stderr": self.stderr if not self.success else ""
        }


class RenderExecutor:
    """渲染执行器"""

    # 质量配置
    QUALITY_CONFIGS = {
        "low": {
            "flag": "-ql",
            "fps": 30,
            "description": "480p @ 30fps (快速预览)"
        },
        "medium": {
            "flag": "-qm",
            "fps": 60,
            "description": "720p @ 60fps (标准质量)"
        },
        "high": {
            "flag": "-qh",
            "fps": 60,
            "description": "1080p @ 60fps (高质量)"
        }
    }

    def __init__(
        self,
        scene_spec: SceneSpec,
        quality: str = "medium",
        save_python_code: bool = True
    ):
        """
        初始化渲染执行器

        Args:
            scene_spec: SceneSpec 对象
            quality: 渲染质量 (low/medium/high)
            save_python_code: 是否保存生成的 Python 代码
        """
        self.spec = scene_spec
        self.quality = quality
        self.save_python_code = save_python_code

        # 验证质量参数
        if quality not in self.QUALITY_CONFIGS:
            raise ValueError(
                f"Invalid quality: {quality}. "
                f"Must be one of {list(self.QUALITY_CONFIGS.keys())}"
            )

    def render(self) -> RenderResult:
        """
        执行渲染

        Returns:
            RenderResult 对象
        """
        start_time = time.time()

        try:
            # 1. 生成 Manim 代码
            print(f"[Render] Generating Manim code for {self.spec.scene_id}...")
            python_code = convert_dsl_to_manim(self.spec)

            # 2. 保存 Python 代码
            code_path = self._save_python_code(python_code)
            print(f"[Render] Python code saved to: {code_path}")

            # 3. 执行 Manim 命令
            print(f"[Render] Starting Manim rendering ({self.quality})...")
            result = self._execute_manim(code_path)

            # 4. 处理结果
            if result.success:
                result.render_time = time.time() - start_time
                result.python_code_path = str(code_path) if self.save_python_code else None

                # 获取视频信息
                if result.video_path and os.path.exists(result.video_path):
                    result.file_size_mb = os.path.getsize(result.video_path) / (1024 * 1024)
                    print(f"[Render] ✓ Rendering complete!")
                    print(f"[Render]   Video: {result.video_path}")
                    print(f"[Render]   Size: {result.file_size_mb:.2f} MB")
                    print(f"[Render]   Time: {result.render_time:.1f}s")
                else:
                    result.success = False
                    result.error = "Video file not found after rendering"

            return result

        except Exception as e:
            print(f"[Render] ✗ Rendering failed: {str(e)}")
            result = RenderResult(False)
            result.error = f"Unexpected error: {str(e)}"
            result.render_time = time.time() - start_time
            return result

    def _save_python_code(self, code: str) -> Path:
        """
        保存 Python 代码到文件

        Args:
            code: Python 代码字符串

        Returns:
            保存的文件路径
        """
        # 创建输出目录
        output_dir = Path("output") / self.spec.scene_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存代码
        code_path = output_dir / f"{self.spec.scene_id}.py"
        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(code)

        return code_path

    def _execute_manim(self, code_path: Path) -> RenderResult:
        """
        执行 Manim 命令

        Args:
            code_path: Python 代码文件路径

        Returns:
            RenderResult 对象
        """
        result = RenderResult(True)

        # 获取类名
        class_name = self._get_class_name()

        # 构建命令
        quality_config = self.QUALITY_CONFIGS[self.quality]
        cmd = [
            "manim",
            quality_config["flag"],
            "--fps", str(quality_config["fps"]),
            "-o", f"{self.spec.scene_id}.mp4",
            str(code_path),
            class_name
        ]

        print(f"[Render] Executing: {' '.join(cmd)}")

        try:
            # 执行命令（300秒超时）
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(Path.cwd())
            )

            result.stdout = process.stdout
            result.stderr = process.stderr

            if process.returncode == 0:
                # 查找生成的视频文件
                video_path = self._find_video_file()
                if video_path:
                    result.video_path = str(video_path)
                    result.success = True
                else:
                    result.success = False
                    result.error = "Video file not found after successful render"
            else:
                result.success = False
                result.error = f"Manim command failed with code {process.returncode}"
                print(f"[Render] ✗ Manim error:")
                print(result.stderr)

        except subprocess.TimeoutExpired:
            result.success = False
            result.error = "Rendering timeout (300s)"
            print(f"[Render] ✗ Timeout after 300 seconds")

        except FileNotFoundError:
            result.success = False
            result.error = "manim command not found. Is Manim installed?"
            print(f"[Render] ✗ manim not found. Please install: pip install manim")

        except Exception as e:
            result.success = False
            result.error = f"Execution error: {str(e)}"
            print(f"[Render] ✗ Execution error: {e}")

        return result

    def _find_video_file(self) -> Optional[Path]:
        """
        查找生成的视频文件

        Returns:
            视频文件路径，如果未找到返回 None
        """
        # Manim 默认输出路径
        media_dir = Path("media/videos")

        # 可能的路径
        possible_paths = [
            # 新版 Manim
            media_dir / self.spec.scene_id / self.quality / f"{self.spec.scene_id}.mp4",
            media_dir / self.spec.scene_id / f"{self.quality}/videos" / f"{self.spec.scene_id}.mp4",
            # 旧版 Manim
            media_dir / f"{self.spec.scene_id}/{self.spec.scene_id}.mp4",
            # 输出目录
            Path("output") / self.spec.scene_id / f"{self.spec.scene_id}.mp4"
        ]

        for path in possible_paths:
            if path.exists():
                # 复制到输出目录
                output_path = Path("output") / self.spec.scene_id / f"{self.spec.scene_id}.mp4"
                output_path.parent.mkdir(parents=True, exist_ok=True)

                if path != output_path:
                    import shutil
                    shutil.copy2(path, output_path)

                return output_path

        # 如果都没找到，尝试搜索
        if media_dir.exists():
            for video_file in media_dir.rglob(f"{self.spec.scene_id}.mp4"):
                output_path = Path("output") / self.spec.scene_id / f"{self.spec.scene_id}.mp4"
                output_path.parent.mkdir(parents=True, exist_ok=True)

                import shutil
                shutil.copy2(video_file, output_path)
                return output_path

        return None

    def _get_class_name(self) -> str:
        """获取类名"""
        parts = self.spec.scene_id.split("_")
        return "".join(p.capitalize() for p in parts)


def render_scene(
    scene_spec: SceneSpec,
    quality: str = "medium",
    save_python_code: bool = True
) -> RenderResult:
    """
    便捷函数：渲染场景

    Args:
        scene_spec: SceneSpec 对象
        quality: 渲染质量
        save_python_code: 是否保存 Python 代码

    Returns:
        RenderResult 对象
    """
    executor = RenderExecutor(scene_spec, quality, save_python_code)
    return executor.render()


def render_scene_from_file(
    dsl_file_path: str,
    quality: str = "medium",
    save_python_code: bool = True
) -> RenderResult:
    """
    便捷函数：从 DSL 文件渲染场景

    Args:
        dsl_file_path: DSL JSON 文件路径
        quality: 渲染质量
        save_python_code: 是否保存 Python 代码

    Returns:
        RenderResult 对象
    """
    from ..dsl.parser import DSLParser

    scene_spec = DSLParser.parse_file(dsl_file_path)
    return render_scene(scene_spec, quality, save_python_code)
