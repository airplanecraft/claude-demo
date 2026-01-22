#!/usr/bin/env python3
"""
诊断 API 连接问题
检查：代理设置、图片大小、网络配置
"""

import os
import sys
from pathlib import Path
from run import encode_image, get_image_list

print("=" * 60)
print("API 连接问题诊断")
print("=" * 60)

# 1. 检查代理设置
print("\n1. 检查代理设置：")
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY']
proxy_found = False
for var in proxy_vars:
    value = os.getenv(var)
    if value:
        print(f"   ⚠️  发现代理: {var}={value}")
        proxy_found = True

if not proxy_found:
    print("   ✓ 未发现环境变量中的代理设置")
else:
    print("\n   建议：代理服务器可能有60秒超时限制")
    print("   解决方案：临时禁用代理或联系代理管理员延长超时")

# 2. 检查图片大小
print("\n2. 检查图片文件大小：")
images = get_image_list()
if not images:
    print("   ❌ 未找到图片文件")
    sys.exit(1)

for img in images[:3]:  # 只检查前3张
    img_path = Path(__file__).parent / 'input' / 'images' / img
    if not img_path.exists():
        print(f"   ⚠️  {img}: 文件不存在")
        continue

    size_kb = img_path.stat().st_size / 1024
    print(f"\n   图片: {img}")
    print(f"   原始大小: {size_kb:.2f} KB")

    # 测试压缩
    try:
        base64_data, media_type = encode_image(str(img_path), compress=True, max_size_kb=800)
        encoded_size_kb = len(base64_data) * 3 / 4 / 1024  # Base64 解码后的实际大小
        print(f"   压缩后大小: {encoded_size_kb:.2f} KB")
        print(f"   媒体类型: {media_type}")
        print(f"   Base64 长度: {len(base64_data):,} 字符")

        # 警告如果太大
        if encoded_size_kb > 1000:
            print(f"   ⚠️  警告: 图片仍然很大 ({encoded_size_kb:.2f} KB > 1 MB)")
            print(f"   建议: 进一步压缩图片或降低分辨率")
        elif encoded_size_kb > 500:
            print(f"   ⚠️  注意: 图片较大 ({encoded_size_kb:.2f} KB)")
        else:
            print(f"   ✓ 图片大小合适")

    except Exception as e:
        print(f"   ❌ 压缩失败: {str(e)}")

# 3. 检查 Anthropic API 配置
print("\n3. 检查 Anthropic API 配置：")
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    print(f"   ✓ API Key 已设置 ({api_key[:10]}...)")
else:
    print("   ❌ 未找到 ANTHROPIC_API_KEY")

# 4. 建议
print("\n" + "=" * 60)
print("诊断建议：")
print("=" * 60)

if proxy_found:
    print("\n⚠️  发现代理配置 - 这很可能是问题根源！")
    print("\n解决方案 1：临时禁用代理")
    print("   在运行前执行：")
    print("   unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY")
    print("   python run.py")
    print("\n解决方案 2：配置代理超时")
    print("   联系代理管理员将超时延长至 120 秒以上")
    print("\n解决方案 3：使用更小的图片")
    print("   进一步压缩图片，减少处理时间")
else:
    print("\n未发现明显的代理问题")
    print("\n可能原因：")
    print("1. Anthropic API 服务器端处理超时（图片太大或太复杂）")
    print("2. 网络连接不稳定")
    print("3. prompt 太长导致处理时间过长")
    print("\n建议：")
    print("- 进一步压缩图片（降低质量或分辨率）")
    print("- 简化 system prompt")
    print("- 检查网络连接稳定性")

print("\n" + "=" * 60)
