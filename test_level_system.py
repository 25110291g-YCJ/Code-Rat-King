"""快速测试关卡系统的脚本
将房屋生成时间改为5秒,方便测试
"""
import pygame as pg
from ATripHome import Game
import settings

# 临时修改房屋生成时间为5秒
settings.HOUSE_FIXED_SPAWN_MS = 5000

if __name__ == '__main__':
    print("="*50)
    print("测试配置:")
    print(f"- 房屋生成时间: {settings.HOUSE_FIXED_SPAWN_MS}ms (5秒)")
    print(f"- 过渡时间: {settings.LEVEL_TRANSITION_MS}ms (2秒)")
    print(f"- 关卡数量: 3 (sky, mine, volcano)")
    print("="*50)
    print("\n按SPACE开始游戏,等待5秒后房屋会出现")
    print("小猫碰到房屋后会切换到下一关卡\n")
    
    game = Game()
    game.main_loop()
