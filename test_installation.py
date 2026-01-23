#!/usr/bin/env python3
"""
Test script to verify the Animation DSL system installation.

This script checks all dependencies and components without rendering anything.
Run this first to ensure everything is properly installed.

Usage:
    python test_installation.py
"""

import sys
import os

def test_python_version():
    """Test Python version."""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def test_import(module_name, package_name=None):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        print(f"  ✓ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"  ✗ {package_name or module_name} - {e}")
        return False

def test_manim_command():
    """Test if manim command is available."""
    import subprocess
    try:
        result = subprocess.run(
            ['manim', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip() or result.stderr.strip()
            print(f"  ✓ manim command - {version}")
            return True
        else:
            print(f"  ✗ manim command failed")
            return False
    except FileNotFoundError:
        print(f"  ✗ manim command not found in PATH")
        return False
    except Exception as e:
        print(f"  ✗ manim command error - {e}")
        return False

def test_project_structure():
    """Test if project directories and files exist."""
    print("\nTesting project structure...")

    required_items = [
        ("manim_mcp/", "dir", "Main package directory"),
        ("manim_mcp/dsl/schema.json", "file", "DSL Schema"),
        ("manim_mcp/dsl/validator.py", "file", "DSL Validator"),
        ("manim_mcp/renderer/animation_factory.py", "file", "Animation Factory"),
        ("manim_mcp/tools/create_scene.py", "file", "Create Scene Tool"),
        ("prompts/stage3_dsl_generation.txt", "file", "DSL Generation Prompt"),
    ]

    all_exist = True
    for path, item_type, description in required_items:
        exists = os.path.isdir(path) if item_type == "dir" else os.path.isfile(path)
        if exists:
            print(f"  ✓ {description} ({path})")
        else:
            print(f"  ✗ {description} ({path}) - NOT FOUND")
            all_exist = False

    return all_exist

def test_dsl_components():
    """Test if DSL components can be imported and initialized."""
    print("\nTesting DSL components...")

    try:
        from manim_mcp.dsl.validator import DSLValidator
        validator = DSLValidator()
        print("  ✓ DSL Validator initialized")
    except Exception as e:
        print(f"  ✗ DSL Validator - {e}")
        return False

    try:
        from manim_mcp.dsl.parser import DSLParser
        print("  ✓ DSL Parser imported")
    except Exception as e:
        print(f"  ✗ DSL Parser - {e}")
        return False

    try:
        from manim_mcp.renderer.animation_factory import AnimationFactory
        print("  ✓ Animation Factory imported")
    except Exception as e:
        print(f"  ✗ Animation Factory - {e}")
        return False

    try:
        from manim_mcp.renderer.dsl_to_manim import DSLToManimConverter
        print("  ✓ DSL to Manim Converter imported")
    except Exception as e:
        print(f"  ✗ DSL to Manim Converter - {e}")
        return False

    return True

def test_mcp_tools():
    """Test if MCP tools can be imported."""
    print("\nTesting MCP tools...")

    tools = [
        ("create_scene", "Create Scene"),
        ("validate_scene", "Validate Scene"),
        ("render_scene", "Render Scene"),
        ("batch_render", "Batch Render"),
    ]

    all_work = True
    for tool_name, description in tools:
        try:
            module = __import__('manim_mcp.tools', fromlist=[tool_name])
            getattr(module, tool_name)
            print(f"  ✓ {description}")
        except Exception as e:
            print(f"  ✗ {description} - {e}")
            all_work = False

    return all_work

def test_simple_validation():
    """Test a simple DSL validation."""
    print("\nTesting DSL validation...")

    from manim_mcp.dsl.validator import DSLValidator

    # Minimal valid DSL
    test_dsl = {
        "scene_id": "test_scene",
        "metadata": {
            "title": "Test",
            "description": "Test scene"
        },
        "resources": {
            "audio": {
                "voice": "zh-CN-XiaoxiaoNeural",
                "rate": "+0%"
            }
        },
        "timeline": [
            {
                "phase_id": "test_phase",
                "duration": 1.0,
                "animations": [
                    {
                        "id": "test_anim",
                        "type": "show_text",
                        "params": {
                            "text": "Test",
                            "position": [0, 0, 0],
                            "font_size": 24,
                            "audio_text": "Test"
                        },
                        "start_time": 0.0
                    }
                ]
            }
        ]
    }

    try:
        validator = DSLValidator()
        result = validator.validate(test_dsl)

        if result.valid:
            print("  ✓ Simple DSL validation passed")
            return True
        else:
            print(f"  ✗ Validation failed: {result.errors}")
            return False
    except Exception as e:
        print(f"  ✗ Validation error: {e}")
        return False

def main():
    print("=" * 60)
    print("Animation DSL System - Installation Test")
    print("=" * 60)

    results = []

    # Test Python version
    print("\n1. Checking Python version...")
    results.append(test_python_version())

    # Test required packages
    print("\n2. Checking Python packages...")
    results.append(test_import("manim", "manim"))
    results.append(test_import("jsonschema", "jsonschema"))
    results.append(test_import("anthropic", "anthropic"))
    results.append(test_import("mcp", "mcp"))

    # Test manim command
    print("\n3. Checking manim command...")
    results.append(test_manim_command())

    # Test project structure
    results.append(test_project_structure())

    # Test DSL components
    results.append(test_dsl_components())

    # Test MCP tools
    results.append(test_mcp_tools())

    # Test simple validation
    results.append(test_simple_validation())

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"Tests passed: {passed}/{total} ({success_rate:.0f}%)")

    if all(results):
        print("\n✓ ALL TESTS PASSED!")
        print("\nYou're ready to use the Animation DSL system.")
        print("Try running: python example_workflow.py")
    else:
        print("\n✗ SOME TESTS FAILED")
        print("\nPlease fix the issues above before proceeding.")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
