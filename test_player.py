"""
测试新玩家角色和滑行功能的简单脚本
"""
import pygame as pg
from player import Player
from settings import *

def test_player():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption('Player Test')
    clock = pg.time.Clock()
    
    # 创建玩家
    player_group = pg.sprite.GroupSingle()
    player_group.add(Player())
    player = player_group.sprite
    
    running = True
    frame_count = 0
    
    print("=== 玩家角色测试 ===")
    print(f"角色尺寸: {player.char_width} x {player.char_height}")
    print(f"待机动画帧数: {len(player.idle_frames)}")
    print(f"跑步动画帧数: {len(player.run_frames)}")
    print(f"跳跃动画帧数: {len(player.jump_frames)}")
    print(f"滑行动画帧数: {len(player.slide_frames)}")
    print("\n操作说明:")
    print("- 空格键: 模拟跳跃")
    print("- 向下箭头: 滑行")
    print("- ESC: 退出")
    print("\n开始测试...\n")
    
    while running:
        clock.tick(FPS)
        frame_count += 1
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_SPACE:
                    # 模拟跳跃
                    if player.rect.bottom >= GROUND_HEIGHT:
                        player.start_jump()
                        print(f"[{frame_count}] 跳跃!")
                elif event.key == pg.K_DOWN:
                    # 滑行
                    player.start_slide()
                    if player.is_sliding:
                        print(f"[{frame_count}] 滑行开始! (持续{player.slide_timer}帧)")
        
        # 更新玩家
        player.update()
        
        # 绘制
        screen.fill((135, 206, 235))  # 天空色
        
        # 绘制地面
        ground_rect = pg.Rect(0, GROUND_HEIGHT, WIDTH, GROUND_DEPTH)
        pg.draw.rect(screen, (34, 139, 34), ground_rect)
        
        # 绘制玩家
        player_group.draw(screen)
        
        # 绘制状态信息
        font = pg.font.SysFont(None, 24)
        
        status_texts = [
            f"Frame: {frame_count}",
            f"Position: ({player.rect.x}, {player.rect.y})",
            f"On Ground: {player.rect.bottom >= GROUND_HEIGHT}",
            f"Sliding: {player.is_sliding}",
            f"Slide Cooldown: {player.slide_cooldown / FPS:.1f}s" if player.slide_cooldown > 0 else "Slide Ready",
            f"Animation Index: {player.anim_index:.2f}",
        ]
        
        y_offset = 10
        for text in status_texts:
            surf = font.render(text, True, (255, 255, 255))
            screen.blit(surf, (10, y_offset))
            y_offset += 25
        
        # 滑行提示
        if player.is_sliding:
            slide_text = font.render("SLIDING!", True, (0, 255, 0))
            screen.blit(slide_text, (WIDTH // 2 - 50, HEIGHT // 2))
        
        pg.display.flip()
        
        # 每秒打印一次状态
        if frame_count % FPS == 0:
            print(f"[{frame_count}] 状态: 滑行={player.is_sliding}, 冷却={player.slide_cooldown}帧, 在地面={player.rect.bottom >= GROUND_HEIGHT}")
    
    pg.quit()
    print("\n测试结束")

if __name__ == '__main__':
    test_player()
