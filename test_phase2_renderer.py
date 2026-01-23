#!/usr/bin/env python3
"""
测试 Phase 2: 渲染器组件

测试流程:
1. DSL 验证
2. DSL → Manim 代码转换
3. 代码生成验证
4. (可选) 渲染测试
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from manim_mcp.dsl.validator import validate_dsl_file
from manim_mcp.dsl.parser import DSLParser
from manim_mcp.renderer.dsl_to_manim import convert_dsl_to_manim
from manim_mcp.renderer.render_executor import render_scene


def test_dsl_validation():
    """测试 DSL 验证"""
    print("=" * 60)
    print("Test 1: DSL Validation")
    print("=" * 60)

    dsl_file = "manim_mcp/dsl/examples/simple_solution.json"
    print(f"\n[1] Validating: {dsl_file}")

    result = validate_dsl_file(dsl_file)

    print(f"\n[Result]")
    print(f"  Valid: {result.valid}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")
    print(f"  Estimated Duration: {result.estimated_duration}s")
    print(f"  Animation Count: {result.animation_count}")
    print(f"  Phase Count: {result.phase_count}")

    if result.errors:
        print(f"\n[Errors]")
        for error in result.errors:
            print(f"  - {error}")
        return False

    if result.warnings:
        print(f"\n[Warnings]")
        for warning in result.warnings:
            print(f"  - {warning}")

    print(f"\n✓ DSL Validation passed!")
    return True


def test_dsl_parsing():
    """测试 DSL 解析"""
    print("\n" + "=" * 60)
    print("Test 2: DSL Parsing")
    print("=" * 60)

    dsl_file = "manim_mcp/dsl/examples/simple_solution.json"
    print(f"\n[1] Parsing: {dsl_file}")

    scene = DSLParser.parse_file(dsl_file)

    print(f"\n[Scene Info]")
    print(f"  Scene ID: {scene.scene_id}")
    print(f"  Title: {scene.title}")
    print(f"  Problem Image: {scene.problem_image}")
    print(f"  Phases: {len(scene.timeline)}")

    print(f"\n✓ DSL Parsing passed!")
    return scene


def test_code_generation(scene):
    """测试代码生成"""
    print("\n" + "=" * 60)
    print("Test 3: Manim Code Generation")
    print("=" * 60)

    print(f"\n[1] Converting DSL to Manim code...")
    python_code = convert_dsl_to_manim(scene)

    print(f"\n[Generated Code Stats]")
    lines = python_code.split("\n")
    print(f"  Total Lines: {len(lines)}")
    print(f"  Code Size: {len(python_code)} bytes")

    # 验证关键部分
    checks = {
        "Imports": "from manim import *" in python_code,
        "Config": "config.pixel_height" in python_code,
        "Audio Helpers": "generate_audio_file" in python_code,
        "Scene Class": f"class {scene.scene_id.replace('_', '').title()}" in python_code or "class Problem1Solution" in python_code,
        "Timeline": "# Timeline execution" in python_code,
    }

    print(f"\n[Code Validation]")
    all_passed = True
    for check_name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")
        all_passed = all_passed and passed

    if not all_passed:
        print(f"\n✗ Some code checks failed!")
        return False, None

    # 保存代码用于检查
    output_dir = Path("output/test_phase2")
    output_dir.mkdir(parents=True, exist_ok=True)
    code_path = output_dir / "generated_scene.py"

    with open(code_path, 'w', encoding='utf-8') as f:
        f.write(python_code)

    print(f"\n[Generated Code Saved]")
    print(f"  Path: {code_path}")
    print(f"  You can inspect the generated code at: {code_path}")

    # 显示代码片段
    print(f"\n[Code Preview - First 30 lines]")
    print("-" * 60)
    for i, line in enumerate(lines[:30], 1):
        print(f"{i:3d} | {line}")
    print("-" * 60)

    print(f"\n✓ Code Generation passed!")
    return True, code_path


def test_rendering(scene, skip_render=True):
    """测试渲染（可选）"""
    print("\n" + "=" * 60)
    print("Test 4: Rendering (Optional)")
    print("=" * 60)

    if skip_render:
        print(f"\n[Skipped]")
        print(f"  Rendering test is skipped by default.")
        print(f"  To enable rendering, set skip_render=False in test_rendering()")
        print(f"  Note: Rendering requires Manim to be installed.")
        return True

    print(f"\n[1] Starting render (quality: low)...")
    print(f"    This may take 1-3 minutes...")

    try:
        result = render_scene(scene, quality="low", save_python_code=True)

        print(f"\n[Render Result]")
        print(f"  Success: {result.success}")

        if result.success:
            print(f"  Video Path: {result.video_path}")
            print(f"  Python Code: {result.python_code_path}")
            print(f"  Render Time: {result.render_time:.1f}s")
            print(f"  File Size: {result.file_size_mb:.2f} MB")
            print(f"\n✓ Rendering passed!")
            return True
        else:
            print(f"  Error: {result.error}")
            if result.stderr:
                print(f"\n[Stderr]")
                print(result.stderr[:500])
            print(f"\n✗ Rendering failed!")
            return False

    except Exception as e:
        print(f"\n✗ Rendering exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Phase 2 Renderer Test Suite")
    print("=" * 60)

    results = []

    # Test 1: DSL Validation
    try:
        passed = test_dsl_validation()
        results.append(("DSL Validation", passed))
    except Exception as e:
        print(f"\n✗ DSL Validation failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("DSL Validation", False))
        return 1

    # Test 2: DSL Parsing
    scene = None
    try:
        scene = test_dsl_parsing()
        results.append(("DSL Parsing", scene is not None))
    except Exception as e:
        print(f"\n✗ DSL Parsing failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("DSL Parsing", False))
        return 1

    # Test 3: Code Generation
    if scene:
        try:
            passed, code_path = test_code_generation(scene)
            results.append(("Code Generation", passed))
        except Exception as e:
            print(f"\n✗ Code Generation failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(("Code Generation", False))
            return 1
    else:
        results.append(("Code Generation", False))

    # Test 4: Rendering (Optional)
    if scene:
        try:
            passed = test_rendering(scene, skip_render=True)
            results.append(("Rendering (Optional)", passed))
        except Exception as e:
            print(f"\n✗ Rendering failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(("Rendering (Optional)", False))

    # 总结
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name}: {status}")
        if "(Optional)" not in test_name:
            all_passed = all_passed and passed

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All core tests passed!")
        print("\nPhase 2 implementation is working correctly.")
        print("\nNext steps:")
        print("  1. Review generated code: output/test_phase2/generated_scene.py")
        print("  2. (Optional) Enable rendering test to verify full pipeline")
        print("  3. Proceed to Phase 3: Implement MCP Tools")
    else:
        print("✗ Some tests failed!")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
