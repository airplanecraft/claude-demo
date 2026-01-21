import os
import asyncio
import edge_tts
from manim import *

config.disable_caching = True
config.pixel_height = 1080
config.pixel_width = 1920
config.frame_rate = 60

# LaTeX 中文配置
my_tex_template = TexTemplate()
my_tex_template.tex_compiler = "xelatex"
my_tex_template.output_format = ".xdv"
my_tex_template.add_to_preamble(r"\usepackage[fontset=mac]{ctex}")
config.tex_template = my_tex_template

# 颜色和布局常量
COLOR_BG = "#415049"
COLOR_HIGHLIGHT = "#FFD700"
COLOR_PRIME = "#FF6B6B"
COLOR_CALCULATION = "#4ECDC4"
COLOR_SUCCESS = "#95E1D3"
FONT_NAME = "Heiti SC"
POS_ANIM_CENTER = [3.5, 2.0, 0]  # 动画区域中心（右上）
POS_TEXT_BASE = [3.5, -3.0, 0]   # 文字区域（右下）

def generate_audio_file(text, filename, voice="zh-CN-XiaoxiaoNeural"):
    async def amain():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)
    
    try:
        asyncio.run(amain())
        return True
    except Exception as e:
        print(f"TTS failed: {e}")
        os.system(f'say "{text}"')
        return False

def prepare_all_audio(problem_data, steps_data):
    audio_dir = "audio"
    os.makedirs(audio_dir, exist_ok=True)
    
    # 生成题目音频
    generate_audio_file(problem_data["speech"], f"{audio_dir}/problem.wav")
    
    # 生成步骤音频
    for i, step in enumerate(steps_data):
        generate_audio_file(step["speech"], f"{audio_dir}/step_{i}.wav")

class SolutionVideo1(Scene):
    def construct(self):
        self.problem_image_name = "image_1.png"
        self.text_lines_group = VGroup()

        # 定义数据
        problem_data = {
            "speech": "Tim计算五个不同质数的平均值，答案是整数。求最小可能的整数。"
        }
        
        steps_data = [
            {
                "text": "设五个质数为p1,p2,p3,p4,p5，平均值为k",
                "math": r"p_1 + p_2 + p_3 + p_4 + p_5 = 5k",
                "speech": "设五个质数的平均值为k，则五个质数的和等于5k"
            },
            {
                "text": "分析质数性质：除2外都是奇数",
                "math": r"\text{质数: } 2, 3, 5, 7, 11, 13, ...",
                "speech": "除了2以外，所有质数都是奇数"
            },
            {
                "text": "必须包含质数2才能使5k为整数",
                "math": r"2 + 4\text{个奇质数} = \text{偶数}",
                "speech": "为了让总和能被5整除且为整数，必须包含质数2"
            },
            {
                "text": "寻找最小的4个奇质数: 3,5,7,11",
                "math": r"2 + 3 + 5 + 7 + 11 = 28",
                "speech": "选择最小的4个奇质数，计算总和为28"
            },
            {
                "text": "28除以5不是整数，需要调整",
                "math": r"k = \frac{28}{5} = 5.6",
                "speech": "28除以5等于5点6，不是整数"
            },
            {
                "text": "尝试用13替换11",
                "math": r"2 + 3 + 5 + 7 + 13 = 30",
                "speech": "将11换成13，新的总和为30"
            },
            {
                "text": "验证结果",
                "math": r"k = \frac{30}{5} = 6",
                "speech": "30除以5等于6，这是整数"
            }
        ]
        
        final_answer_text = "答案：6"

        prepare_all_audio(problem_data, steps_data)

        # 执行流程
        cover_objects = self.show_cover_phase()
        video_img_obj = self.transition_to_solution_phase(cover_objects)
        self.safe_read_problem(problem_data, video_img_obj)
        self.play_visual_reasoning(steps_data)
        self.show_final_answer(final_answer_text)

    def play_visual_reasoning(self, steps):
        # 创建动画区域
        anim_group = VGroup()
        
        # 步骤1: 建立数学模型
        self.play_rolling_step_text(steps[0])
        equation = MathTex(steps[0]["math"], color=COLOR_CALCULATION).scale(0.8)
        equation.move_to(POS_ANIM_CENTER)
        self.play(Write(equation))
        self.wait(1)
        anim_group.add(equation)
        
        # 步骤2: 展示质数序列
        self.play_rolling_step_text(steps[1])
        primes = MathTex(steps[1]["math"], color=COLOR_PRIME).scale(0.7)
        primes.move_to([POS_ANIM_CENTER[0], POS_ANIM_CENTER[1] - 0.8, 0])
        self.play(Write(primes))
        self.wait(1)
        anim_group.add(primes)
        
        # 步骤3: 分析包含2的必要性
        self.play_rolling_step_text(steps[2])
        analysis = MathTex(steps[2]["math"], color=COLOR_HIGHLIGHT).scale(0.7)
        analysis.move_to([POS_ANIM_CENTER[0], POS_ANIM_CENTER[1] - 1.6, 0])
        self.play(Write(analysis))
        self.wait(1)
        
        # 清理屏幕
        self.play(FadeOut(anim_group), FadeOut(analysis))
        anim_group = VGroup()
        
        # 步骤4: 第一次尝试
        self.play_rolling_step_text(steps[3])
        first_try = MathTex(steps[3]["math"], color=COLOR_CALCULATION).scale(0.8)
        first_try.move_to(POS_ANIM_CENTER)
        
        # 动态计算过程
        calc_steps = [
            MathTex(r"2 + 3 = 5", color=COLOR_PRIME).scale(0.6),
            MathTex(r"5 + 5 = 10", color=COLOR_PRIME).scale(0.6),
            MathTex(r"10 + 7 = 17", color=COLOR_PRIME).scale(0.6),
            MathTex(r"17 + 11 = 28", color=COLOR_PRIME).scale(0.6)
        ]
        
        for i, step in enumerate(calc_steps):
            step.move_to([POS_ANIM_CENTER[0], POS_ANIM_CENTER[1] - 0.8 - i * 0.4, 0])
        
        self.play(Write(first_try))
        for step in calc_steps:
            self.play(Write(step))
            self.wait(0.3)
        
        anim_group.add(first_try, *calc_steps)
        self.wait(1)
        
        # 步骤5: 检验结果
        self.play_rolling_step_text(steps[4])
        result1 = MathTex(steps[4]["math"], color="#FF4444").scale(0.8)
        result1.move_to([POS_ANIM_CENTER[0], POS_ANIM_CENTER[1] - 2.5, 0])
        self.play(Write(result1))
        self.wait(1)
        
        # 清理并准备第二次尝试
        self.play(FadeOut(anim_group), FadeOut(result1))
        
        # 步骤6: 第二次尝试
        self.play_rolling_step_text(steps[5])
        second_try = MathTex(steps[5]["math"], color=COLOR_CALCULATION).scale(0.8)
        second_try.move_to(POS_ANIM_CENTER)
        self.play(Write(second_try))
        
        # 突出显示变化
        highlight_box = SurroundingRectangle(second_try, color=COLOR_HIGHLIGHT, buff=0.1)
        self.play(Create(highlight_box))
        self.wait(1)
        
        # 步骤7: 最终验证
        self.play_rolling_step_text(steps[6])
        final_result = MathTex(steps[6]["math"], color=COLOR_SUCCESS).scale(1.0)
        final_result.move_to([POS_ANIM_CENTER[0], POS_ANIM_CENTER[1] - 1.0, 0])
        self.play(Write(final_result))
        
        # 成功动画效果
        success_circle = Circle(radius=0.8, color=COLOR_SUCCESS).move_to(final_result.get_center())
        self.play(Create(success_circle))
        self.play(Flash(final_result, color=COLOR_SUCCESS))
        
        self.wait(2)
        self.play(FadeOut(second_try), FadeOut(highlight_box), FadeOut(final_result), FadeOut(success_circle))

    def play_rolling_step_text(self, step):
        step_text = Text(step["text"], font=FONT_NAME, color=WHITE).scale(0.4)
        step_text.move_to(POS_TEXT_BASE)
        
        if len(self.text_lines_group) >= 3:
            self.play(
                self.text_lines_group.animate.shift(UP * 0.6),
                FadeIn(step_text),
                run_time=0.5
            )
            old_line = self.text_lines_group[0]
            self.text_lines_group.remove(old_line)
            self.remove(old_line)
        else:
            step_text.move_to([POS_TEXT_BASE[0], POS_TEXT_BASE[1] - len(self.text_lines_group) * 0.6, 0])
            self.play(FadeIn(step_text), run_time=0.3)
        
        self.text_lines_group.add(step_text)
        
        # 播放语音
        audio_file = f"audio/step_{len(self.text_lines_group)-1}.wav"
        if os.path.exists(audio_file):
            self.add_sound(audio_file)
        
        self.wait(1.5)

    def show_cover_phase(self):
        logo = ImageMobject("assets/logo.png").scale(0.6).to_edge(UP + LEFT)
        cover = ImageMobject("assets/cover.png").scale(0.8)
        title = Text("奥数解题动画", font=FONT_NAME, color=COLOR_HIGHLIGHT).scale(1.2).next_to(cover, DOWN)
        
        self.play(FadeIn(logo), FadeIn(cover), Write(title))
        self.wait(2)
        return VGroup(logo, cover, title)

    def transition_to_solution_phase(self, cover_objects):
        problem_img_path = f"input/images/{self.problem_image_name}"
        video_img = ImageMobject(problem_img_path).scale(0.9)
        video_img.move_to([-3.5, 0, 0])
        
        self.play(
            FadeOut(cover_objects),
            FadeIn(video_img)
        )
        return video_img

    def safe_read_problem(self, problem_data, video_img_obj):
        problem_text = Text("题目分析", font=FONT_NAME, color=COLOR_HIGHLIGHT).scale(0.6)
        problem_text.move_to([POS_TEXT_BASE[0], POS_TEXT_BASE[1] + 1, 0])
        
        self.play(Write(problem_text))
        
        audio_file = "audio/problem.wav"
        if os.path.exists(audio_file):
            self.add_sound(audio_file)
        
        self.wait(2)
        self.play(FadeOut(problem_text))

    def show_final_answer(self, final_answer_text):
        answer = Text(final_answer_text, font=FONT_NAME, color=COLOR_SUCCESS).scale(1.0)
        answer.move_to(POS_ANIM_CENTER)
        
        answer_box = SurroundingRectangle(answer, color=COLOR_SUCCESS, buff=0.3)
        
        self.play(Write(answer), Create(answer_box))
        self.play(Flash(answer, color=COLOR_SUCCESS))
        self.wait(2)
