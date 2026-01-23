#!/usr/bin/env python3
"""
测试 Phase 3: MCP Tools

测试流程:
1. create_scene - 创建场景
2. validate_scene - 验证场景
3. render_scene - 渲染场景（可选）
4. batch_render - 批量渲染（可选）
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from manim_mcp.tools.create_scene import create_scene, format_result as format_create
from manim_mcp.tools.validate_scene import validate_scene, format_result as format_validate
from manim_mcp.tools.render_scene import render_scene, format_result as format_render
from manim_mcp.tools.batch_render import batch_render, format_result as format_batch


def test_create_scene():
    """测试创建场景"""
    print("=" * 60)
    print("Test 1: create_scene")
    print("=" * 60)

    # 加载示例 DSL
    dsl_file = "manim_mcp/dsl/examples/simple_solution.json"
    with open(dsl_file, 'r', encoding='utf-8') as f:
        dsl = json.load(f)

    print(f"\n[1] Creating scene from DSL: {dsl['scene_id']}")

    # 调用 create_scene
    result = create_scene(
        scene_dsl=dsl,
        save_to_file=True,
        output_dir="scenes"
    )

    # 格式化输出
    print(f"\n{format_create(result)}")

    if not result["success"]:
        return False

    print(f"\n✓ create_scene test passed!")
    return True


def test_validate_scene():
    """测试验证场景"""
    print("\n" + "=" * 60)
    print("Test 2: validate_scene")
    print("=" * 60)

    scene_id = "problem_1_solution"
    print(f"\n[1] Validating scene: {scene_id}")

    # 调用 validate_scene
    result = validate_scene(
        scene_id=scene_id,
        scenes_dir="scenes"
    )

    # 格式化输出
    print(f"\n{format_validate(result)}")

    if not result["success"]:
        return False

    if not result["validation"]["valid"]:
        print(f"\n✗ Scene validation failed!")
        return False

    print(f"\n✓ validate_scene test passed!")
    return True


def test_render_scene(skip_render=True):
    """测试渲染场景"""
    print("\n" + "=" * 60)
    print("Test 3: render_scene (Optional)")
    print("=" * 60)

    if skip_render:
        print(f"\n[Skipped]")
        print(f"  Rendering test is skipped by default.")
        print(f"  To enable rendering, set skip_render=False")
        print(f"  Note: Rendering requires Manim to be installed.")
        return True

    scene_id = "problem_1_solution"
    print(f"\n[1] Rendering scene: {scene_id}")
    print(f"    Quality: low (for testing)")
    print(f"    This may take 1-3 minutes...")

    # 调用 render_scene
    result = render_scene(
        scene_id=scene_id,
        quality="low",
        save_python_code=True,
        scenes_dir="scenes"
    )

    # 格式化输出
    print(f"\n{format_render(result)}")

    if not result["success"]:
        print(f"\n✗ render_scene test failed!")
        return False

    print(f"\n✓ render_scene test passed!")
    return True


def test_batch_render(skip_render=True):
    """测试批量渲染"""
    print("\n" + "=" * 60)
    print("Test 4: batch_render (Optional)")
    print("=" * 60)

    if skip_render:
        print(f"\n[Skipped]")
        print(f"  Batch rendering test is skipped by default.")
        print(f"  To enable, set skip_render=False")
        return True

    scene_ids = ["problem_1_solution"]
    print(f"\n[1] Batch rendering {len(scene_ids)} scenes")
    print(f"    Quality: low (for testing)")

    # 调用 batch_render
    result = batch_render(
        scene_ids=scene_ids,
        quality="low",
        save_python_code=False,
        scenes_dir="scenes",
        stop_on_error=False
    )

    # 格式化输出
    print(f"\n{format_batch(result)}")

    if not result["success"]:
        print(f"\n✗ batch_render test failed!")
        return False

    print(f"\n✓ batch_render test passed!")
    return True


def test_mcp_tools_registration():
    """测试 MCP Tools 注册"""
    print("\n" + "=" * 60)
    print("Test 5: MCP Tools Registration")
    print("=" * 60)

    from manim_mcp.tools import MANIM_TOOLS, MANIM_TOOL_HANDLERS, MANIM_TOOL_FORMATTERS

    print(f"\n[1] Checking tool registration")

    print(f"\n[Tool Schemas]")
    for tool in MANIM_TOOLS:
        print(f"  ✓ {tool['name']}: {tool['description'][:50]}...")

    print(f"\n[Tool Handlers]")
    for name, handler in MANIM_TOOL_HANDLERS.items():
        print(f"  ✓ {name}: {handler.__name__}()")

    print(f"\n[Tool Formatters]")
    for name, formatter in MANIM_TOOL_FORMATTERS.items():
        print(f"  ✓ {name}: {formatter.__name__}()")

    # 验证数量匹配
    if len(MANIM_TOOLS) == len(MANIM_TOOL_HANDLERS) == len(MANIM_TOOL_FORMATTERS) == 4:
        print(f"\n✓ All 4 tools registered correctly!")
        return True
    else:
        print(f"\n✗ Tool count mismatch!")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Phase 3 MCP Tools Test Suite")
    print("=" * 60)

    results = []

    # Test 1: create_scene
    try:
        passed = test_create_scene()
        results.append(("create_scene", passed))
    except Exception as e:
        print(f"\n✗ create_scene failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("create_scene", False))

    # Test 2: validate_scene
    try:
        passed = test_validate_scene()
        results.append(("validate_scene", passed))
    except Exception as e:
        print(f"\n✗ validate_scene failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("validate_scene", False))

    # Test 3: render_scene (Optional)
    try:
        passed = test_render_scene(skip_render=True)
        results.append(("render_scene (Optional)", passed))
    except Exception as e:
        print(f"\n✗ render_scene failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("render_scene (Optional)", False))

    # Test 4: batch_render (Optional)
    try:
        passed = test_batch_render(skip_render=True)
        results.append(("batch_render (Optional)", passed))
    except Exception as e:
        print(f"\n✗ batch_render failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("batch_render (Optional)", False))

    # Test 5: MCP Tools Registration
    try:
        passed = test_mcp_tools_registration()
        results.append(("MCP Tools Registration", passed))
    except Exception as e:
        print(f"\n✗ MCP Tools Registration failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("MCP Tools Registration", False))

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
        print("\nPhase 3 MCP Tools implementation is working correctly.")
        print("\nNext steps:")
        print("  1. Test with actual MCP server integration")
        print("  2. (Optional) Enable rendering tests")
        print("  3. Proceed to Phase 4: Prompt updates")
    else:
        print("✗ Some tests failed!")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
