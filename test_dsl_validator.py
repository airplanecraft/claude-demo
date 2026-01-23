#!/usr/bin/env python3
"""
测试 DSL Validator 和 Parser
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from manim_mcp.dsl.validator import DSLValidator, validate_dsl_file
from manim_mcp.dsl.parser import DSLParser


def test_validator():
    """测试验证器"""
    print("=" * 60)
    print("Testing DSL Validator")
    print("=" * 60)

    # 测试示例文件
    example_file = "manim_mcp/dsl/examples/simple_solution.json"

    print(f"\n[1] Validating: {example_file}")
    result = validate_dsl_file(example_file)

    print(f"\n[Result]")
    print(f"  Valid: {result.valid}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")
    print(f"  Estimated Duration: {result.estimated_duration}s")
    print(f"  Animation Count: {result.animation_count}")
    print(f"  Phase Count: {result.phase_count}")

    if result.errors:
        print(f"\n[Errors]")
        for i, error in enumerate(result.errors, 1):
            print(f"  {i}. {error}")

    if result.warnings:
        print(f"\n[Warnings]")
        for i, warning in enumerate(result.warnings, 1):
            print(f"  {i}. {warning}")

    if result.valid:
        print(f"\n✓ Validation passed!")
    else:
        print(f"\n✗ Validation failed!")

    return result.valid


def test_parser():
    """测试解析器"""
    print("\n" + "=" * 60)
    print("Testing DSL Parser")
    print("=" * 60)

    example_file = "manim_mcp/dsl/examples/simple_solution.json"

    print(f"\n[1] Parsing: {example_file}")
    scene = DSLParser.parse_file(example_file)

    print(f"\n[Scene Info]")
    print(f"  Scene ID: {scene.scene_id}")
    print(f"  Title: {scene.title}")
    print(f"  Problem Image: {scene.problem_image}")
    print(f"  Resolution: {scene.resolution}")
    print(f"  Frame Rate: {scene.frame_rate} fps")
    print(f"  Theme: {scene.theme}")
    print(f"  Phases: {len(scene.timeline)}")

    print(f"\n[Timeline]")
    for i, phase in enumerate(scene.timeline, 1):
        print(f"  {i}. {phase}")
        has_audio = "✓" if phase.audio else "✗"
        print(f"     Audio: {has_audio}")
        for j, anim in enumerate(phase.animations, 1):
            print(f"       {i}.{j} {anim}")

    print(f"\n✓ Parser test passed!")
    return True


def test_invalid_dsl():
    """测试无效的 DSL"""
    print("\n" + "=" * 60)
    print("Testing Invalid DSL")
    print("=" * 60)

    invalid_dsl = {
        "scene_id": "test_invalid",
        # 缺少必需的 metadata
        "timeline": []
    }

    print(f"\n[1] Validating invalid DSL (missing metadata)")
    validator = DSLValidator()
    result = validator.validate(invalid_dsl)

    print(f"\n[Result]")
    print(f"  Valid: {result.valid}")
    print(f"  Errors: {len(result.errors)}")

    if result.errors:
        print(f"\n[Errors]")
        for i, error in enumerate(result.errors, 1):
            print(f"  {i}. {error}")

    if not result.valid:
        print(f"\n✓ Correctly detected invalid DSL!")
    else:
        print(f"\n✗ Failed to detect invalid DSL!")

    return not result.valid


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("DSL Validator & Parser Test Suite")
    print("=" * 60)

    results = []

    try:
        results.append(("Validator", test_validator()))
    except Exception as e:
        print(f"\n✗ Validator test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Validator", False))

    try:
        results.append(("Parser", test_parser()))
    except Exception as e:
        print(f"\n✗ Parser test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Parser", False))

    try:
        results.append(("Invalid DSL", test_invalid_dsl()))
    except Exception as e:
        print(f"\n✗ Invalid DSL test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Invalid DSL", False))

    # 总结
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name}: {status}")
        all_passed = all_passed and passed

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
