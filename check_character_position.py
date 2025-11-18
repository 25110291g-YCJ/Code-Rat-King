"""检查角色图像和位置的脚本"""
import pygame as pg
import glob
import os

pg.init()
screen = pg.display.set_mode((100, 100))  # 创建一个小窗口以初始化视频模式

# 加载一个角色图像
idle_frames = sorted(glob.glob('assets/character/Idle/*.png'))
if idle_frames:
    # 加载原始图像
    original_img = pg.image.load(idle_frames[0]).convert_alpha()
    print(f"原始图像尺寸: {original_img.get_size()}")
    
    # 缩放到游戏中的尺寸
    scaled_img = pg.transform.scale(original_img, (162, 200))
    print(f"缩放后尺寸: {scaled_img.get_size()}")
    
    # 检查图像中非透明像素的分布
    # 找到最底部的非透明像素
    rect = original_img.get_rect()
    bottom_y = 0
    for y in range(rect.height - 1, -1, -1):
        for x in range(rect.width):
            if original_img.get_at((x, y)).a > 0:  # 非透明
                bottom_y = y
                break
        if bottom_y > 0:
            break
    
    print(f"原始图像中最底部的非透明像素在: Y={bottom_y} (图像高度={rect.height})")
    print(f"脚部到图像底部的距离: {rect.height - bottom_y} 像素")
    
    # 计算缩放后的偏移
    scale_factor = 200 / rect.height
    foot_offset_scaled = int((rect.height - bottom_y) * scale_factor)
    print(f"\n缩放到200高度后，脚部到图像底部的距离约: {foot_offset_scaled} 像素")
    
    # 游戏设置
    GROUND_HEIGHT = 700
    print(f"\n游戏中的GROUND_HEIGHT: {GROUND_HEIGHT}")
    print(f"如果使用 midbottom=(x, {GROUND_HEIGHT}):")
    print(f"  - rect.bottom = {GROUND_HEIGHT}")
    print(f"  - 角色脚部实际位置 ≈ {GROUND_HEIGHT - foot_offset_scaled}")
    print(f"  - 脚部悬空/下沉了约 {foot_offset_scaled} 像素")
    
    # 建议
    if foot_offset_scaled > 10:
        print(f"\n⚠️ 建议调整：角色应该放置在 Y={GROUND_HEIGHT + foot_offset_scaled} 的位置")
        print(f"或者添加一个 PLAYER_GROUND_OFFSET = {foot_offset_scaled}")
else:
    print("未找到角色图像文件")

pg.quit()
