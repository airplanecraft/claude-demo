import os
import asyncio
import edge_tts
from manim import *

# ==============================================================================
# 🎛️ 全局配置 (Configuration)
# ==============================================================================
config.disable_caching = True

# [高清设置] 强制 1080p @ 60fps
config.pixel_height = 1080
config.pixel_width = 1920
config.frame_rate = 60

# [核心修复] LaTeX 中文与 Mac 环境支持配置
try:
    my_tex_template = TexTemplate()
    my_tex_template.tex_compiler = "xelatex"
    my_tex_template.output_format = ".xdv"
    my_tex_template.add_to_preamble(r"\usepackage[fontset=mac]{ctex}")
    my_tex_template.add_to_preamble(r"\usepackage{amsmath}")
    my_tex_template.add_to_preamble(r"\usepackage{amssymb}")
    config.tex_template = my_tex_template
except Exception as e:
    print(f"Warning: Failed to configure ctex template: {e}")

# 🎨 颜色配置
COLOR_BG          = "#415049"   # 背景深绿色
COLOR_GRID        = "#253D32"   # 网格线深色
COLOR_TEXT_MAIN   = "#F0F5F2"   # 普通文本白灰色
COLOR_MATH_A      = "#FFFFFF"   # 公式主色
COLOR_MATH_B      = "#A8D8B9"   # 公式辅色
COLOR_HIGHLIGHT   = "#FFD700"   # 高亮色 (金黄) - 核心重点色
COLOR_SUBTITLE    = "#FFFFFF"   # 底部字幕颜色
COLOR_SUB_BG      = "#0A140F"   # 字幕背景半透明黑
COLOR_SEPARATOR   = "#FFFFFF"   # 左右分栏分割线颜色

# 🅰️ 字体配置
FONT_NAME         = "Heiti SC"  # Mac 下推荐黑体，防止乱码
FONT_SIZE_BODY    = 24          # 解题步骤文字大小
FONT_SIZE_MATH    = 32          # 公式文字大小
FONT_SIZE_SUB     = 24          # 字幕文字大小

# 🖼️ 资源路径与常量
# 注意：logo.png 和 cover.png 应放在项目根目录的 assets/ 文件夹下
# 原题图片在 input/images/ 目录下
ASSETS_DIR         = "assets"
LOGO_IMAGE_NAME    = os.path.join(ASSETS_DIR, "logo.png")
COVER_BG_IMAGE     = os.path.join(ASSETS_DIR, "cover.png")
PROBLEM_IMAGE_DIR  = os.path.join("input", "images")
COVER_FOOTER_TEXT  = "2025香港袋鼠数学竞赛中学中年级组"
TTS_CACHE_DIR      = "tts_cache"

# 📐 核心布局常量 (Layout Constants) - 严禁修改数值
# ---------------------------------------------------
# 左侧面板 (题目区)
VIDEO_LEFT_PANEL_X   = -3.5         # 左侧面板的中心 X 坐标
VIDEO_IMG_WIDTH      = 5.5          # 题目图片最大宽度
VIDEO_IMG_MAX_HEIGHT = 6.0          # 题目图片最大高度
SEPARATOR_X          = 0.0
LOGO_SCALE_FACTOR    = 0.15
LOGO_BUFF            = 0.1

# 分割线
SEPARATOR_X          = 0.0          # 左右分栏线的 X 坐标

# 右侧面板 (动画与文字区) - 关键防重叠设置
# [!] 动画必须以此点为中心，不要画得太大导致覆盖下方文字
POS_ANIM_CENTER      = [3.5, 2.0, 0]   # 动画区域中心 (右上)
# [!] 滚动步骤文字出现在此处，动画不要延伸到这里
POS_TEXT_BASE        = [3.5, -3.0, 0]  # 文字区域基准点 (右下)

# 文字行高与数量限制
TEXT_LINE_HEIGHT     = 0.8             # 每一行文字的高度间距
MAX_TEXT_LINES       = 4               # 右下角最多保留几行文字

# 封面布局
COVER_IMG_EXACT_WIDTH    = 4.0
COVER_IMG_EXACT_HEIGHT   = 3.0
COVER_IMG_POS            = DOWN * 0.8
QUESTION_LABEL_FONT_SIZE = 48
QUESTION_LABEL_BUFF      = 0.5
# ---------------------------------------------------

# 🎙️ 语音合成配置
EDGE_VOICE        = "zh-CN-XiaoxiaoNeural"
MAC_VOICE         = "Tingting"
TTS_RATE          = "+10%"
SECONDS_PER_CHAR  = 0.35       # 估算阅读速度

# ==============================================================================
# 🛠️ 音频工具 (Helpers)
# ==============================================================================
async def _run_edge_tts(text, filename):
    communicate = edge_tts.Communicate(text, EDGE_VOICE, rate=TTS_RATE)
    await communicate.save(filename)

def generate_audio_file(text, filename_mp3):
    clean_text = text.replace("\n", " ").strip()
    abs_mp3 = os.path.abspath(filename_mp3)
    abs_m4a = abs_mp3.replace(".mp3", ".m4a")
    try:
        asyncio.run(_run_edge_tts(clean_text, abs_mp3))
        if os.path.exists(abs_mp3) and os.path.getsize(abs_mp3) > 1000: return abs_mp3
    except: pass
    try:
        os.system(f'say -v "{MAC_VOICE}" -o "{abs_m4a}" "{clean_text}"')
        if os.path.exists(abs_m4a) and os.path.getsize(abs_m4a) > 0: return abs_m4a
    except: pass
    return None

def prepare_all_audio(problem_data, steps_data):
    if not os.path.exists(TTS_CACHE_DIR): os.makedirs(TTS_CACHE_DIR)
    q_file = os.path.join(TTS_CACHE_DIR, "question.mp3")
    problem_data["audio_path"] = generate_audio_file(problem_data["speech"], q_file)
    for i, step in enumerate(steps_data):
        s_file = os.path.join(TTS_CACHE_DIR, f"step_{i}.mp3")
        step["audio_path"] = generate_audio_file(step["speech"], s_file)

# ==============================================================================
# 🎬 核心逻辑 (Scene Logic)
# ==============================================================================
class SolutionVideoTEMPLATE(Scene): # AI: 请修改类名，例如 SolutionVideo6
    def construct(self):
        # AI: 请根据用户输入的题号 N，自动生成完整路径
        # 例如：self.problem_image_name = os.path.join(PROBLEM_IMAGE_DIR, "image_6.png")
        self.problem_image_name = os.path.join(PROBLEM_IMAGE_DIR, "image_REPLACE_WITH_NUMBER.png")

        # [固定配置] 题号颜色
        self.question_label_text = "Q"
        self.question_label_color = "#FFD700"

        self.text_lines_group = VGroup()

        # AI: 在此填充 problem_data, steps_data, final_answer_text
        # problem_data = {"speech": "..."}
        # steps_data = [{"text": "...", "math": "...", "speech": "..."}, ...]

        prepare_all_audio(problem_data, steps_data)

        cover_objects = self.show_cover_phase()
        video_img_obj = self.transition_to_solution_phase(cover_objects)
        self.safe_read_problem(problem_data, video_img_obj)
        self.play_visual_reasoning(steps_data)
        self.show_final_answer(final_answer_text)

    # --- 🎨 AI 需编写的动画部分 ---
    def play_visual_reasoning(self, steps):
        # [CRITICAL LAYOUT RULE]
        # 所有动画对象必须位于右上角区域。
        # 请务必使用 obj.move_to(POS_ANIM_CENTER) 来定位主物体。
        # 确保物体底部不要低于 Y = 0，以免遮挡下方的 steps 文字。
        pass

    # --- 🛠️ 滚动文字与字幕 (已支持中文公式) ---
    def play_rolling_step_text(self, step):
        audio_path = step.get("audio_path")
        new_line = VGroup()
        if step["text"]:
            t = Text(step["text"], font=FONT_NAME, font_size=FONT_SIZE_BODY, color=COLOR_HIGHLIGHT)
            new_line.add(t)
        if step["math"]:
            m = MathTex(step["math"], font_size=FONT_SIZE_MATH, color=COLOR_MATH_A)
            new_line.add(m)

        # 将新的一行文字放置在 POS_TEXT_BASE (右下角)
        new_line.arrange(RIGHT, buff=0.2).move_to(POS_TEXT_BASE).set_opacity(0)

        anims = []
        # 旧文字向上滚动
        if len(self.text_lines_group) > 0:
            anims.append(self.text_lines_group.animate.shift(UP * TEXT_LINE_HEIGHT))
        # 最顶部的旧文字消失
        if len(self.text_lines_group) >= MAX_TEXT_LINES:
            anims.append(self.text_lines_group[0].animate.set_opacity(0))
        # 新文字淡入
        anims.append(new_line.animate.set_opacity(1))

        # 底部字幕条
        sub_text = Text(step["speech"], font=FONT_NAME, font_size=FONT_SIZE_SUB, color=COLOR_SUBTITLE)
        if sub_text.width > 12: sub_text.scale(12 / sub_text.width)
        sub_bg = SurroundingRectangle(sub_text, color=COLOR_BG, fill_color=COLOR_SUB_BG, fill_opacity=0.8, buff=0.1)
        sub_group = VGroup(sub_bg, sub_text).to_edge(DOWN, buff=0.2)

        self.text_lines_group.add(new_line)
        self.play(*anims, FadeIn(sub_group), run_time=0.6)
        if len(self.text_lines_group) > MAX_TEXT_LINES:
            self.text_lines_group.remove(self.text_lines_group[0])

        try:
            if audio_path and os.path.exists(audio_path): self.add_sound(audio_path)
        except: pass
        self.wait(max(1.0, len(step["speech"]) * SECONDS_PER_CHAR))
        self.play(FadeOut(sub_group), run_time=0.3)

    # --- 辅助方法 (无需修改) ---
    def show_cover_phase(self):
        if os.path.exists(COVER_BG_IMAGE):
            cover_bg = ImageMobject(COVER_BG_IMAGE).stretch_to_fit_width(config.frame_width).stretch_to_fit_height(config.frame_height)
            cover_bg.z_index = -10
            self.add(cover_bg)
        else: self.add(Rectangle(width=config.frame_width, height=config.frame_height, color=WHITE))

        if os.path.exists(self.problem_image_name):
            prob_img = ImageMobject(self.problem_image_name).stretch_to_fit_width(COVER_IMG_EXACT_WIDTH).stretch_to_fit_height(COVER_IMG_EXACT_HEIGHT).move_to(COVER_IMG_POS)
            border = SurroundingRectangle(prob_img, color="#333333", stroke_width=4, buff=0)
            label = Text(self.question_label_text, font=FONT_NAME, font_size=QUESTION_LABEL_FONT_SIZE, color=self.question_label_color, weight=BOLD).next_to(prob_img, LEFT, buff=QUESTION_LABEL_BUFF)
            self.add(Group(prob_img, border, label))
        else:
            self.add(Text(f"Missing: {self.problem_image_name}", color=RED).move_to(COVER_IMG_POS))

        self.add(Text(COVER_FOOTER_TEXT, font=FONT_NAME, font_size=48, color="#333333", weight=BOLD).to_edge(DOWN, buff=0.5))
        self.wait(3)
        return {"bg": cover_bg if os.path.exists(COVER_BG_IMAGE) else None}

    def transition_to_solution_phase(self, cover_objects):
        self.camera.background_color = COLOR_BG
        grid = NumberPlane(x_range=[-8, 8, 1], y_range=[-5, 5, 1], background_line_style={"stroke_color": COLOR_GRID, "stroke_width": 2, "stroke_opacity": 0.5}, axis_config={"stroke_width": 0})
        separator = Line(start=UP * 4, end=DOWN * 4, color=COLOR_SEPARATOR, stroke_width=2).move_to([SEPARATOR_X, 0, 0])
        logo = ImageMobject(LOGO_IMAGE_NAME).scale(LOGO_SCALE_FACTOR).to_corner(UL, buff=LOGO_BUFF) if os.path.exists(LOGO_IMAGE_NAME) else VGroup()

        if os.path.exists(self.problem_image_name):
            target_img = ImageMobject(self.problem_image_name).scale_to_fit_width(VIDEO_IMG_WIDTH).move_to([VIDEO_LEFT_PANEL_X, 0.5, 0])
            if target_img.height > VIDEO_IMG_MAX_HEIGHT: target_img.scale_to_fit_height(VIDEO_IMG_MAX_HEIGHT)
        else:
            target_img = Text("No Image", color=RED).move_to([VIDEO_LEFT_PANEL_X, 0.5, 0])

        anims = [FadeIn(grid), FadeIn(separator), FadeIn(logo), FadeIn(target_img)]
        if cover_objects.get("bg"): anims.append(FadeOut(cover_objects["bg"]))
        self.clear()
        self.add(grid, separator, logo, target_img)
        self.play(*anims, run_time=1.0)
        return target_img

    def safe_read_problem(self, problem_data, video_img_obj):
        text = problem_data["speech"]
        audio_path = problem_data.get("audio_path")
        sub_text = Text(text, font=FONT_NAME, font_size=FONT_SIZE_SUB, color=COLOR_SUBTITLE)
        if sub_text.width > 12: sub_text.scale(12 / sub_text.width)
        sub_bg = SurroundingRectangle(sub_text, color=COLOR_BG, fill_color=COLOR_SUB_BG, fill_opacity=0.8, buff=0.1)
        sub_group = VGroup(sub_bg, sub_text).to_edge(DOWN, buff=0.2)
        highlight = SurroundingRectangle(video_img_obj, color=COLOR_HIGHLIGHT, buff=0.1, stroke_width=4)
        self.play(FadeIn(sub_group), Create(highlight), run_time=0.5)
        try:
            if audio_path and os.path.exists(audio_path): self.add_sound(audio_path)
        except: pass
        self.wait(len(text) * SECONDS_PER_CHAR + 0.5)
        self.play(FadeOut(sub_group), FadeOut(highlight), run_time=0.5)

    def show_final_answer(self, answer_text):
        ans_text = Text(answer_text, font=FONT_NAME, font_size=40, color=COLOR_HIGHLIGHT)
        ans_text.move_to([VIDEO_LEFT_PANEL_X, -3.2, 0])
        ans_box = SurroundingRectangle(ans_text, color=COLOR_HIGHLIGHT, buff=0.2)
        self.play(Write(ans_text), Create(ans_box))
        self.wait(3)
