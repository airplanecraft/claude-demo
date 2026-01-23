# Getting Started Guide

This guide will help you set up and run the Animation DSL system for generating mathematical video explanations.

## Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- Node.js (for MCP server, if using Claude Desktop)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd claude-demo
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Key dependencies:
- `manimlib` or `manim` - Animation library
- `anthropic` - Claude API client
- `mcp` - Model Context Protocol SDK
- `jsonschema` - DSL validation
- `edge-tts` - Text-to-speech for audio

### 3. Verify Installation

```bash
# Check Manim installation
manim --version

# Check Python packages
python -c "import manim; import anthropic; import jsonschema; print('All packages installed!')"
```

## Usage Options

You have two main ways to use this system:

### Option A: Using MCP Server (Recommended)

This allows Claude to directly create, validate, and render animations through MCP tools.

#### 1. Start the MCP Server

```bash
# From the project root
python server.py
```

The server will start and register these Manim tools:
- `manim_create_scene` - Create and validate DSL scenes
- `manim_validate_scene` - Validate existing scenes
- `manim_render_scene` - Render scenes to video
- `manim_batch_render` - Batch render multiple scenes

#### 2. Configure Claude Desktop (if using)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "manim-animator": {
      "command": "python",
      "args": ["/path/to/claude-demo/server.py"]
    }
  }
}
```

#### 3. Use with Claude

Now you can ask Claude to create animations:

```
User: "Create an animation explaining the Gauss sum problem (1+2+...+100)"

Claude will:
1. Generate Animation DSL (JSON)
2. Use manim_create_scene to save it
3. Use manim_validate_scene to verify it
4. Use manim_render_scene to create the video
```

### Option B: Direct Python Usage

Use the Python API directly without MCP server.

#### 1. Create a DSL Scene

```python
from manim_mcp.tools import create_scene

# Your Animation DSL (JSON)
scene_dsl = {
    "scene_id": "problem_1_solution",
    "metadata": {
        "problem_number": "1",
        "title": "高斯求和问题",
        "description": "计算 1+2+3+...+100 的和"
    },
    "resources": {
        "audio": {
            "voice": "zh-CN-XiaoxiaoNeural",
            "rate": "+0%"
        },
        "images": {
            "logo": "assets/logo.png",
            "problem": "input/problem_1.png"
        }
    },
    "timeline": [
        {
            "phase_id": "cover",
            "duration": 3.0,
            "animations": [
                {
                    "id": "show_logo",
                    "type": "show_image",
                    "params": {
                        "image_key": "logo",
                        "position": [-5.5, 3.0, 0],
                        "scale": 0.3
                    },
                    "start_time": 0.0
                },
                {
                    "id": "show_title",
                    "type": "show_text",
                    "params": {
                        "text": "高斯求和问题",
                        "position": [0, 0.5, 0],
                        "font_size": 48,
                        "audio_text": "今天我们来解决高斯求和问题"
                    },
                    "start_time": 0.5
                }
            ]
        }
    ]
}

# Create and save the scene
result = create_scene(scene_dsl, save_to_file=True)
print(f"Scene created: {result['scene_id']}")
print(f"Saved to: {result['file_path']}")
```

#### 2. Validate the Scene

```python
from manim_mcp.tools import validate_scene

# Validate the saved scene
validation = validate_scene(scene_id="problem_1_solution")

if validation['valid']:
    print("✓ Scene is valid!")
    print(f"Duration: {validation['statistics']['estimated_duration']}s")
    print(f"Animations: {validation['statistics']['total_animations']}")
else:
    print("✗ Validation errors:")
    for error in validation['errors']:
        print(f"  - {error}")
```

#### 3. Render the Scene

```python
from manim_mcp.tools import render_scene

# Render with different quality settings
result = render_scene(
    scene_id="problem_1_solution",
    quality="medium"  # Options: "low" (480p), "medium" (720p), "high" (1080p)
)

if result['success']:
    print(f"✓ Video rendered successfully!")
    print(f"Output: {result['output_file']}")
    print(f"Duration: {result['duration']:.2f}s")
else:
    print(f"✗ Render failed: {result['error']}")
```

#### 4. Batch Render Multiple Scenes

```python
from manim_mcp.tools import batch_render

# Render multiple scenes
result = batch_render(
    scene_ids=["problem_1_solution", "problem_2_solution", "problem_3_solution"],
    quality="medium",
    continue_on_error=True
)

print(f"Completed: {result['summary']['successful']}/{result['summary']['total']}")
for scene_result in result['results']:
    status = "✓" if scene_result['success'] else "✗"
    print(f"{status} {scene_result['scene_id']}")
```

## Project Structure

```
claude-demo/
├── server.py                    # MCP server entry point
├── run.py                       # Original exam solver script
├── requirements.txt             # Python dependencies
│
├── manim_mcp/                   # Animation DSL system
│   ├── dsl/
│   │   ├── schema.json         # DSL JSON Schema
│   │   ├── validator.py        # DSL validator
│   │   ├── parser.py           # DSL parser
│   │   └── examples/
│   │       └── simple_solution.json  # Example DSL
│   │
│   ├── renderer/
│   │   ├── animation_factory.py      # Generates Manim code from DSL
│   │   ├── dsl_to_manim.py          # DSL to Manim converter
│   │   └── render_executor.py       # Executes Manim rendering
│   │
│   └── tools/
│       ├── create_scene.py     # Create scene tool
│       ├── validate_scene.py   # Validate scene tool
│       ├── render_scene.py     # Render scene tool
│       └── batch_render.py     # Batch render tool
│
├── prompts/                     # Prompt templates
│   ├── stage0_master.txt       # Master workflow prompt
│   ├── stage1_visual_strategy.txt
│   ├── stage2_math_solution.txt
│   ├── stage3_dsl_generation.txt    # DSL generation prompt
│   └── stage4_jsxgraph.txt
│
├── scenes/                      # Generated DSL files (created on first run)
├── media/                       # Rendered videos (created by Manim)
└── assets/                      # Images, logos, etc.
```

## Quick Start Example

Here's a complete example from start to finish:

```python
# example_workflow.py
from manim_mcp.tools import create_scene, validate_scene, render_scene

# Step 1: Define your animation in DSL format
scene_dsl = {
    "scene_id": "simple_example",
    "metadata": {
        "title": "Simple Math Animation",
        "description": "A simple example"
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
                        "text": "Hello, Manim!",
                        "position": [0, 0, 0],
                        "font_size": 48,
                        "audio_text": "欢迎来到数学动画世界"
                    },
                    "start_time": 0.0
                },
                {
                    "id": "formula",
                    "type": "show_math",
                    "params": {
                        "latex": "E = mc^2",
                        "position": [0, -1, 0],
                        "font_size": 36,
                        "audio_text": "爱因斯坦的质能方程"
                    },
                    "start_time": 2.0
                }
            ]
        }
    ]
}

# Step 2: Create the scene
print("Creating scene...")
create_result = create_scene(scene_dsl, save_to_file=True)
print(f"✓ Scene saved to: {create_result['file_path']}")

# Step 3: Validate
print("\nValidating scene...")
validation = validate_scene(create_result['scene_id'])
if validation['valid']:
    print(f"✓ Valid! Estimated duration: {validation['statistics']['estimated_duration']}s")
else:
    print(f"✗ Validation failed!")
    exit(1)

# Step 4: Render
print("\nRendering video...")
render_result = render_scene(
    scene_id=create_result['scene_id'],
    quality="medium"
)

if render_result['success']:
    print(f"✓ Success! Video saved to: {render_result['output_file']}")
else:
    print(f"✗ Render failed: {render_result['error']}")
```

Run it:
```bash
python example_workflow.py
```

## Using the Prompt System

If you want Claude to generate DSL for you:

```python
# generate_with_claude.py
import anthropic
import json

# Load the prompts
with open('prompts/stage0_master.txt', 'r') as f:
    master_prompt = f.read()

with open('prompts/stage3_dsl_generation.txt', 'r') as f:
    dsl_prompt = f.read()

# Initialize Claude
client = anthropic.Anthropic(api_key="your-api-key")

# Ask Claude to generate DSL
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4000,
    messages=[
        {
            "role": "user",
            "content": f"{master_prompt}\n\n{dsl_prompt}\n\nProblem: Calculate the sum 1+2+3+...+100 (Gauss sum problem)"
        }
    ]
)

# Extract DSL JSON from response
dsl_json = json.loads(response.content[0].text)

# Now use the tools to render it
from manim_mcp.tools import create_scene, render_scene

create_result = create_scene(dsl_json, save_to_file=True)
render_result = render_scene(create_result['scene_id'], quality="medium")

print(f"Video: {render_result['output_file']}")
```

## Quality Settings

When rendering, you can choose different quality presets:

| Quality | Resolution | FPS | Use Case |
|---------|------------|-----|----------|
| `low` | 480p | 30 | Quick previews, testing |
| `medium` | 720p | 60 | Standard output (default) |
| `high` | 1080p | 60 | Final production, publishing |

Example:
```python
# Quick preview
render_scene("my_scene", quality="low")

# Production quality
render_scene("my_scene", quality="high")
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'manim'"

**Solution**: Install Manim:
```bash
pip install manim
# or for ManimGL
pip install manimgl
```

### Issue: "jsonschema.exceptions.ValidationError"

**Solution**: Your DSL doesn't match the schema. Check:
- Required fields (scene_id, metadata, timeline)
- Animation types are valid (show_text, show_math, etc.)
- Position arrays have 3 elements [x, y, z]

### Issue: "Scene file not found"

**Solution**: Make sure the `scenes/` directory exists:
```bash
mkdir -p scenes
```

### Issue: Render fails with "manim command not found"

**Solution**: Verify Manim is installed and in PATH:
```bash
which manim
manim --version
```

## Next Steps

1. **Explore Examples**: Check out `manim_mcp/dsl/examples/simple_solution.json`
2. **Read the Schema**: Understand DSL structure in `manim_mcp/dsl/schema.json`
3. **Try Different Animations**: Test all 13 animation types
4. **Customize Layouts**: Modify positions to match your needs
5. **Integrate with Claude**: Use MCP server for automated generation

## Documentation

- **Architecture Overview**: `REFACTORING_PLAN.md`
- **Phase Completion Reports**: `PHASE1_COMPLETE.md`, `PHASE2_COMPLETE.md`, etc.
- **Prompt System**: `prompts/README.md`
- **DSL Reference**: `prompts/stage3_dsl_generation.txt`

## Support

For issues or questions:
1. Check the documentation files listed above
2. Review example DSL files in `manim_mcp/dsl/examples/`
3. Validate your DSL with the validator before rendering
4. Check Manim logs in `media/` directory for rendering errors

Happy animating! 🎬
