#!/usr/bin/env python3
"""
Simple example workflow demonstrating the Animation DSL system.

This script creates a simple math animation, validates it, and renders it to video.
Run this after setting up the environment to verify everything works.

Usage:
    python example_workflow.py
"""

from manim_mcp.tools import create_scene, validate_scene, render_scene
import json

def main():
    print("=" * 60)
    print("Animation DSL Workflow Example")
    print("=" * 60)

    # Step 1: Define your animation in DSL format
    print("\n[Step 1] Creating Animation DSL...")

    scene_dsl = {
        "scene_id": "simple_example",
        "metadata": {
            "problem_number": "demo",
            "title": "Simple Math Animation",
            "description": "A demonstration of the Animation DSL system"
        },
        "resources": {
            "audio": {
                "voice": "zh-CN-XiaoxiaoNeural",
                "rate": "+0%"
            }
        },
        "timeline": [
            {
                "phase_id": "intro",
                "duration": 5.0,
                "animations": [
                    {
                        "id": "title",
                        "type": "show_text",
                        "params": {
                            "text": "Welcome to Animation DSL!",
                            "position": [0, 1, 0],
                            "font_size": 48,
                            "audio_text": "欢迎来到动画DSL系统"
                        },
                        "start_time": 0.0
                    },
                    {
                        "id": "formula",
                        "type": "show_math",
                        "params": {
                            "latex": "E = mc^2",
                            "position": [0, -0.5, 0],
                            "font_size": 36,
                            "audio_text": "这是爱因斯坦的质能方程"
                        },
                        "start_time": 2.0
                    }
                ]
            },
            {
                "phase_id": "highlight",
                "duration": 3.0,
                "animations": [
                    {
                        "id": "highlight_formula",
                        "type": "highlight",
                        "params": {
                            "target": "formula",
                            "color": "#FFFF00",
                            "audio_text": "让我们强调一下这个重要的公式"
                        },
                        "start_time": 5.0
                    }
                ]
            }
        ]
    }

    print(f"✓ DSL created with {len(scene_dsl['timeline'])} phases")

    # Step 2: Create and save the scene
    print("\n[Step 2] Saving scene to file...")

    try:
        create_result = create_scene(scene_dsl, save_to_file=True)
        print(f"✓ Scene saved to: {create_result['file_path']}")
        print(f"  Scene ID: {create_result['scene_id']}")
    except Exception as e:
        print(f"✗ Failed to create scene: {e}")
        return

    # Step 3: Validate the scene
    print("\n[Step 3] Validating scene...")

    try:
        validation = validate_scene(create_result['scene_id'])

        if validation['valid']:
            print("✓ Scene is valid!")
            stats = validation['statistics']
            print(f"  Phases: {stats['total_phases']}")
            print(f"  Animations: {stats['total_animations']}")
            print(f"  Estimated duration: {stats['estimated_duration']}s")

            if validation['warnings']:
                print("\n  Warnings:")
                for warning in validation['warnings']:
                    print(f"    ⚠ {warning}")
        else:
            print("✗ Validation failed!")
            print("\n  Errors:")
            for error in validation['errors']:
                print(f"    ✗ {error}")
            return
    except Exception as e:
        print(f"✗ Validation error: {e}")
        return

    # Step 4: Render the video
    print("\n[Step 4] Rendering video...")
    print("  Quality: medium (720p @ 60fps)")
    print("  This may take a minute...")

    try:
        render_result = render_scene(
            scene_id=create_result['scene_id'],
            quality="medium"
        )

        if render_result['success']:
            print("\n✓ Video rendered successfully!")
            print(f"  Output file: {render_result['output_file']}")
            print(f"  Duration: {render_result['duration']:.2f}s")
            print(f"  Quality: {render_result['quality']}")

            print("\n" + "=" * 60)
            print("SUCCESS! Your animation is ready.")
            print(f"Watch it here: {render_result['output_file']}")
            print("=" * 60)
        else:
            print(f"\n✗ Render failed: {render_result['error']}")
            if 'stderr' in render_result:
                print(f"\nError details:\n{render_result['stderr']}")
    except Exception as e:
        print(f"✗ Render error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
