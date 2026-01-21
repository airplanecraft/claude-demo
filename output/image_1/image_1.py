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

# 颜色和常量定义
COLOR_BG = "#415049"
COLOR_HIGHLIGHT = "#FFD700"
COLOR_PRIME = "#00CED1"
COLOR_CALCULATION = "#FF6B6B"
COLOR_SUCCESS = "#98FB98"
COLOR_FAIL = "#FFA07A"
FONT_NAME = "Heiti SC"
POS_ANIM_CENTER = [3.5, 2.0, 0]
POS_TEXT_BASE = [3.5, -3.0, 0]

async def generate_audio_file(text, filename, voice="zh-CN-XiaoxiaoNeural", rate="+0%", pitch="+0Hz"):
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)
        return True
    except Exception as e:
        print(f"TTS生成失败: {e}")
        return False

def prepare_all_audio(problem_data, steps_data):
    async def main():
        tasks = []
        tasks.append(generate_audio_file(problem_data["speech"], "problem_audio.mp3"))
        
        for i, step in enumerate(steps_data):
            tasks.append(generate_audio_file(step["speech"], f"step_{i}_audio.mp3"))
        
        await asyncio.gather(*tasks)
    
    asyncio.run(main())

class SolutionVideo1(Scene):
    def construct(self):
        self.problem_image_name = "image_1.png"
        self.text_lines_group = VGroup()

        # 定义数据
        problem_data = {
            "speech": "Tim计算五个不同质数的平均值，他的答案是一个整数。那么他可能得到的最小整数是多少？"
        }
        
        steps_data = [
            {
                "text": "步骤1：列出最小的质数序列",
                "math": "2, 3, 5, 7, 11, 13, 17, 19, ...",
                "speech": "首先列出最小的几个质数：2, 3, 5, 7, 11, 13, 17, 19等"
            },
            {
                "text": "步骤2：理解平均值为整数的条件",
                "math": "平均值 = \\frac{\\sum p_i}{5} \\in \\mathbb{Z}",
                "speech": "平均值为整数意味着五个质数的和必须是5的倍数"
            },
            {
                "text": "步骤3：尝试最小的五个质数",
                "math": "2 + 3 + 5 + 7 + 11 = 28",
                "speech": "尝试最小的五个质数：2加3加5加7加11等于28"
            },
            {
                "text": "步骤4：检验能否整除5",
                "math": "28 \\div 5 = 5.6 \\text{（不是整数）}",
                "speech": "28除以5等于5.6，不是整数，所以不符合条件"
            },
            {
                "text": "步骤5：寻找下一个可能的组合",
                "math": "2 + 3 + 5 + 7 + 13 = 30",
                "speech": "将11替换为13，得到：2加3加5加7加13等于30"
            },
            {
                "text": "步骤6：验证新组合",
                "math": "30 \\div 5 = 6 \\text{（整数）}",
                "speech": "30除以5等于6，是整数，符合条件"
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
        # 创建动画区域标题
        title = Text("解题过程", font_size=36, color=COLOR_HIGHLIGHT).move_to(POS_ANIM_CENTER + UP * 2.5)
        self.play(Write(title))
        
        for i, step in enumerate(steps):
            self.play_rolling_step_text(step)
            
            if i == 0:  # 显示质数序列
                primes = [2, 3, 5, 7, 11, 13, 17, 19]
                prime_group = VGroup()
                for j, p in enumerate(primes):
                    prime_text = Text(str(p), font_size=24, color=COLOR_PRIME)
                    prime_text.move_to(POS_ANIM_CENTER + LEFT * 3 + RIGHT * j * 0.8)
                    prime_group.add(prime_text)
                
                self.play(LaggedStart(*[Write(p) for p in prime_group], lag_ratio=0.3))
                self.wait(1)
                
            elif i == 2:  # 第一次尝试计算
                # 高亮前五个质数
                first_five = VGroup()
                calc_parts = []
                for j in range(5):
                    num_text = Text(str([2,3,5,7,11][j]), font_size=28, color=COLOR_HIGHLIGHT)
                    num_text.move_to(POS_ANIM_CENTER + LEFT * 2 + RIGHT * j * 0.8)
                    first_five.add(num_text)
                    calc_parts.append(str([2,3,5,7,11][j]))
                
                self.play(Write(first_five))
                
                # 显示加法过程
                plus_signs = VGroup()
                for j in range(4):
                    plus_text = Text("+", font_size=24, color=WHITE)
                    plus_text.move_to(POS_ANIM_CENTER + LEFT * 1.6 + RIGHT * j * 0.8)
                    plus_signs.add(plus_text)
                
                self.play(Write(plus_signs))
                
                # 显示结果
                equals_text = Text("= 28", font_size=28, color=COLOR_CALCULATION)
                equals_text.move_to(POS_ANIM_CENTER + RIGHT * 2.5)
                self.play(Write(equals_text))
                self.wait(1)
                
            elif i == 3:  # 检验除法
                division = MathTex("28 \\div 5 = 5.6", font_size=32, color=COLOR_FAIL)
                division.move_to(POS_ANIM_CENTER)
                self.play(Write(division))
                
                cross = Line(LEFT, RIGHT, color=RED, stroke_width=8).scale(0.5)
                cross.move_to(division)
                self.play(Create(cross))
                self.wait(1)
                
            elif i == 4:  # 新的组合
                # 清除之前的动画
                self.play(FadeOut(*self.mobjects[-10:]))
                
                # 显示新组合
                new_combo = VGroup()
                numbers = [2, 3, 5, 7, 13]
                for j, num in enumerate(numbers):
                    num_text = Text(str(num), font_size=28, color=COLOR_PRIME)
                    if num == 13:
                        num_text.set_color(COLOR_HIGHLIGHT)
                    num_text.move_to(POS_ANIM_CENTER + LEFT * 2 + RIGHT * j * 0.8)
                    new_combo.add(num_text)
                
                self.play(Write(new_combo))
                
                # 显示新的加法
                new_plus = VGroup()
                for j in range(4):
                    plus_text = Text("+", font_size=24, color=WHITE)
                    plus_text.move_to(POS_ANIM_CENTER + LEFT * 1.6 + RIGHT * j * 0.8)
                    new_plus.add(plus_text)
                
                self.play(Write(new_plus))
                
                new_result = Text("= 30", font_size=28, color=COLOR_SUCCESS)
                new_result.move_to(POS_ANIM_CENTER + RIGHT * 2.5)
                self.play(Write(new_result))
                self.wait(1)
                
            elif i == 5:  # 最终验证
                final_division = MathTex("30 \\div 5 = 6", font_size=32, color=COLOR_SUCCESS)
                final_division.move_to(POS_ANIM_CENTER + DOWN * 0.8)
                self.play(Write(final_division))
                
                checkmark = Text("✓", font_size=40, color=COLOR_SUCCESS)
                checkmark.move_to(final_division.get_right() + RIGHT * 0.5)
                self.play(Write(checkmark))
                self.wait(2)
            
            self.wait(0.5)

    def play_rolling_step_text(self, step):
        text_content = step["text"]
        math_content = step.get("math", "")
        
        # 文本行
        text_obj = Text(text_content, font_size=20, color=WHITE, font=FONT_NAME)
        text_obj.move_to(POS_TEXT_BASE + DOWN * len(self.text_lines_group) * 0.6)
        
        # 数学公式行（如果有）
        if math_content:
            math_obj = MathTex(math_content, font_size=18, color=COLOR_HIGHLIGHT)
            math_obj.next_to(text_obj, DOWN, buff=0.3)
        
        # 播放音频
        if os.path.exists(f"step_{len(self.text_lines_group)}_audio.mp3"):
            self.add_sound(f"step_{len(self.text_lines_group)}_audio.mp3")
        else:
            os.system(f'say "{step["speech"]}"')
        
        # 动画显示
        self.play(Write(text_obj))
        if math_content:
            self.play(Write(math_obj))
            self.text_lines_group.add(VGroup(text_obj, math_obj))
        else:
            self.text_lines_group.add(text_obj)

    def show_cover_phase(self):
        # 背景
        background = Rectangle(width=config.frame_width, height=config.frame_height, 
                             fill_color=COLOR_BG, fill_opacity=1, stroke_width=0)
        
        # 标题
        title = Text("奥数题解析", font_size=48, color=COLOR_HIGHLIGHT, font=FONT_NAME)
        subtitle = Text("Prime Numbers Average", font_size=24, color=WHITE, font=FONT_NAME)
        subtitle.next_to(title, DOWN, buff=0.5)
        
        cover_group = VGroup(background, title, subtitle)
        self.play(FadeIn(cover_group))
        self.wait(1)
        
        return cover_group

    def transition_to_solution_phase(self, cover_objects):
        # 淡出封面
        self.play(FadeOut(cover_objects))
        
        # 显示题目图片
        try:
            if os.path.exists(self.problem_image_name):
                video_img = ImageMobject(self.problem_image_name)
                video_img.scale_to_fit_width(6)
                video_img.move_to(LEFT * 3 + UP * 0.5)
                self.play(FadeIn(video_img))
                return video_img
        except:
            pass
        
        return None

    def safe_read_problem(self, problem_data, video_img_obj):
        # 播放问题音频
        if os.path.exists("problem_audio.mp3"):
            self.add_sound("problem_audio.mp3")
        else:
            os.system(f'say "{problem_data["speech"]}"')
        
        self.wait(3)

    def show_final_answer(self, final_answer_text):
        # 最终答案
        answer_bg = RoundedRectangle(width=4, height=1.2, corner_radius=0.3,
                                   fill_color=COLOR_HIGHLIGHT, fill_opacity=0.3,
                                   stroke_color=COLOR_HIGHLIGHT, stroke_width=3)
        answer_bg.move_to(POS_ANIM_CENTER + DOWN * 2)
        
        answer_text = Text(final_answer_text, font_size=32, color=COLOR_HIGHLIGHT, 
                          font=FONT_NAME, weight=BOLD)
        answer_text.move_to(answer_bg.get_center())
        
        self.play(DrawBorderThenFill(answer_bg))
        self.play(Write(answer_text))
        
        # 添加闪烁效果
        self.play(answer_text.animate.set_color(WHITE), run_time=0.5)
        self.play(answer_text.animate.set_color(COLOR_HIGHLIGHT), run_time=0.5)
        
        self.wait(2)
