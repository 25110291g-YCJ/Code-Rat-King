import pygame as pg
pg.init()

# 游戏尺寸
WIDTH, HEIGHT = 1600, 900  # 游戏窗口显示尺寸
GROUND_DEPTH = 200  # 地面深度
GROUND_HEIGHT = HEIGHT - GROUND_DEPTH  # 地面高    'obstacle_5': 'assets/barrier/new/0_Archer_Running_007-5(1).png',

# 可配置的猫起始 X 坐标（方便把猫放到屏幕偏左的位置）
# 默认在屏幕中间左移 120 像素
CAT_START_X = WIDTH // 2 - 120
GAMENAME_HEIGHT = HEIGHT // 5  # 游戏名称显示高度
GAMEMESSAGE_HEIGHT = HEIGHT // 1.25  # 游戏提示信息显示高度
TEXTTARGET_HEIGHT = GROUND_HEIGHT // 3  # 文本目标显示高度
SCOREMESSAGE_HEIGHT = HEIGHT//1.25  # 分数信息显示高度
CAT_WIDTH, CAT_HEIGHT = 162, 141  # 猫咪尺寸（保留兼容性）
PLAYER_WIDTH, PLAYER_HEIGHT = 162, 200  # 玩家角色尺寸
PLAYER_GROUND_OFFSET = 50  # 玩家角色脚部到图像底部的偏移（修正悬空问题）
DOG_WIDTH, DOG_HEIGHT = 162, 141  # 狗狗尺寸
TREE_WIDTH, TREE_HEIGHT = 250, 250  # 树木尺寸
HOUSE_WIDTH, HOUSE_HEIGHT = 300, 340  # 房屋尺寸
HOUSE_GROUND_OFFSET = 50  # 房屋相对地面的偏移 (Align with player)

# 帧率、重力和移动速度
FPS = 60
# GRAVITY 在此项目中也被用作跳跃的初速度（负值向上），将其加大以提高跳跃高度
GRAVITY = -29
MOVING_SPEED = 3
MAX_MOVING_SPEED = 8
SPEED_INCREMENT = 0.4  # 每个难度阶段增加的速度
DIFFICULTY_SCORE_STEP = 20  # 每达到多少得分提升一次难度
CURRENT_MOVING_SPEED = MOVING_SPEED

# 字体
TARGET_FONT = pg.font.Font('assets/font/BubblegumSans.ttf', 150)
SCORE_FONT = pg.font.Font('assets/font/Purrfect.ttf', 100)
# TITLE_FONT = pg.font.Font('assets/font/KittenSwash.ttf', 100) # 原字体带有水印
TITLE_FONT = pg.font.Font('assets/font/Purrfect.ttf', 100) # 替换为无水印字体
TARGET_TEXT_COLOR = 'white'
TARGET_ALERT_COLOR = 'salmon'
SUPER_JUMP_TEXT_COLOR = 'gold'

# 生成频率与延迟时间
TREE_SPAWN_FREQ = 4500
TREE_SPAWN_MIN = 2000
TREE_SPAWN_STEP = 150
# 房屋默认在约 1 分钟出现（加上 ~4 秒移动距离）
HOUSE_SPAWN_FREQ = 60000
HOUSE_SPAWN_MIN = 40000
HOUSE_SPAWN_STEP = 5000
# 固定一次性房屋生成（毫秒）：用于只在开局后固定时刻生成房屋的模式
HOUSE_FIXED_SPAWN_MS = 15000
# 关卡过渡提示持续时长（毫秒）
LEVEL_TRANSITION_MS = 2000
DOG_SPAWN_FREQ = 40000
DOG_SPAWN_MIN = 15000
DOG_SPAWN_STEP = 1000
DELAY_TIME = 3000
EASTEREGG_PROB = 0.06

# 游戏事件
CORRECT_TYPING = pg.USEREVENT + 1
TREE_SPAWN = pg.USEREVENT + 2
HOUSE_SPAWN = pg.USEREVENT + 3
DOG_SPAWN = pg.USEREVENT + 4
NEXT_MUSIC = pg.USEREVENT + 5
WRONG_TYPING = pg.USEREVENT + 6
SUPER_JUMP_READY = pg.USEREVENT + 7
LAND_EVENT = pg.USEREVENT + 8
ITEM_SPAWN = pg.USEREVENT + 9

# 惩罚与奖励设置
MISS_FEEDBACK_FRAMES = FPS // 4
PENALTY_LOCK_FRAMES = FPS // 2
PENALTY_FLASH_FRAMES = FPS // 6
COMBO_THRESHOLD = 20

# 连击评分设定：每 COMBO_STEP 个连续命中增加 COMBO_BONUS 的倍率，上限为 COMBO_MAX_MULTIPLIER
COMBO_STEP = 5
COMBO_BONUS = 0.1
COMBO_MAX_MULTIPLIER = 2.0

# 超级跳跃力：比普通跳更强
# 让超级跳跃高度略高于普通跳跃（使用 1.25 倍的初速度），并随 GRAVITY 调整。
SUPER_JUMP_FORCE = int(GRAVITY * 1.25)  # 使用 1.25 倍
SUPER_JUMP_BONUS = 5
SUPER_JUMP_NOTICE_FRAMES = FPS
SUPER_JUMP_EFFECT_FRAMES = FPS // 2

# 滑行技能设置
SLIDE_DURATION = 50  # 滑行持续时间（帧）
SLIDE_COOLDOWN = 5 * FPS  # 滑行冷却时间（帧），5秒
SLIDE_KEY = pg.K_LCTRL  # 滑行按键（左Ctrl）

# Boss 设置
BOSS_WIDTH = 200  # Boss 宽度
BOSS_HEIGHT = 200  # Boss 高度
BOSS_X_POSITION = WIDTH - 150  # Boss X坐标（屏幕右侧）
BOSS_MOVE_SPEED = 2  # Boss 上下移动速度
BOSS_MOVE_TOP = 150  # Boss 移动范围上限

# Boss 射击间隔配置（帧数，60帧=1秒）
# 降低频率：Simon(3s), David(2.5s), Gio(2s)
BOSS_SHOOT_INTERVALS = {
    'simon': 180,
    'david': 150,
    'gio': 120
}
BOSS_SHOOT_INTERVAL_DEFAULT = 180
BOSS_MOVE_BOTTOM = HEIGHT - 250  # Boss 移动范围下限
BOSS_SHOOT_INTERVAL = 120  # Boss 射击间隔（帧）= 2秒

# 子弹设置
BULLET_SIZE = 40  # 子弹尺寸
BULLET_SPEED = 8  # 子弹速度

# 评级系统设置
# 评级等级和对应的分数阈值（更鲜艳醒目的颜色）
RANK_THRESHOLDS = [
    (150, 'S', (255, 223, 0)),    # 金色（更亮）
    (120, 'A', (255, 50, 50)),    # 鲜红色（更鲜艳）
    (90, 'B', (50, 150, 255)),    # 亮蓝色（更饱和）
    (60, 'C', (50, 255, 50)),     # 鲜绿色（更明亮）
    (40, 'D', (255, 150, 50)),    # 橙色（更醒目）
    (20, 'E', (180, 180, 180)),   # 浅灰色（更明显）
    (0, 'F', (120, 120, 120))     # 中灰色（提高对比度）
]

# 单词长度范围
WORD_BASE_MIN_LENGTH = 4
WORD_BASE_MAX_LENGTH = 7
WORD_LENGTH_CAP = 12

# 血量设置
MAX_HEALTH = 20  # 玩家最多能承受多少次错误（已调整为20次）
HEALTH_BAR_WIDTH = 300
HEALTH_BAR_HEIGHT = 28
HEALTH_BAR_POS = (40, 40)
HEALTH_BAR_BG = 'gray'
HEALTH_BAR_COLOR = 'salmon'

# 图片路径
SKY_BACKGROUND = 'assets/background/sky.png'
GROUND_BACKGROUND = 'assets/background/ground.png'
HOUSE = 'assets/house/home.png'
CAT_STAND = 'assets/cat/Stand.png'
CAT_WALK = ['assets/cat/Walk1.png', 'assets/cat/Walk2.png', 'assets/cat/Walk3.png', 'assets/cat/Walk4.png', 'assets/cat/Walk5.png',
            'assets/cat/Walk6.png', 'assets/cat/Walk7.png', 'assets/cat/Walk8.png', 'assets/cat/Walk9.png', 'assets/cat/Walk10.png']

CAT_JUMP = ['assets/cat/Jump1.png', 'assets/cat/Jump2.png', 'assets/cat/Jump3.png', 'assets/cat/Jump4.png',
            'assets/cat/Jump5.png', 'assets/cat/Jump6.png', 'assets/cat/Jump7.png', 'assets/cat/Jump8.png']

DOG_RUN = ['assets/dog/Run1.png', 'assets/dog/Run2.png', 'assets/dog/Run3.png', 'assets/dog/Run4.png',
           'assets/dog/Run5.png', 'assets/dog/Run6.png', 'assets/dog/Run7.png', 'assets/dog/Run8.png']

TREE_TYPE = {
    'obstacle_1': 'assets/barrier/new/0_Archer_Running_007-1.png',
    'obstacle_2': 'assets/barrier/new/0_Archer_Running_007-2.png',
    'obstacle_3': 'assets/barrier/new/0_Archer_Running_007-3(1).png',
    'obstacle_4': 'assets/barrier/new/0_Archer_Running_007-4(1).png',
    'obstacle_5': 'assets/barrier/new/0_Archer_Running_007-5(1).png',
    'common_tree': 'assets/barrier/new/0_Archer_Running_007-1.png'
}

# 音效路径
JUMP_SOUND = 'assets/sound effect/Meow.ogg'
HIT_SOUND = 'assets/sound effect/hit.wav'
WIN_SOUND = 'assets/sound effect/win.ogg'
BARK_SOUND = 'assets/sound effect/dog_barking.wav'

# 失败（Game Over）配置
GAME_OVER_DURATION = 2000  # 毫秒，Game Over 屏保持时长
LOSE_SOUND = 'assets/sound effect/hit.wav'  # 可替换为更合适的失败音效

# 碰撞伤害相关：命中后短时间无敌，防止多帧连续受伤（以帧为单位）
# 推荐值为 FPS（1 秒无敌），可按需缩短
DAMAGE_INVULN_FRAMES = FPS
# 受伤浮动文字持续帧数（上移并消失）
DAMAGE_POPUP_FRAMES = FPS // 2
# 树破碎效果与粒子配置
TREE_BREAK_SOUND = 'assets/sound effect/hit.wav'
PARTICLE_COUNT = 8
PARTICLE_LIFETIME = FPS // 2
PARTICLE_COLORS = [(160, 82, 45), (139, 69, 19), (205, 133, 63)]  # 棕色系碎片颜色
# 树缩放因子（<1 表示更矮更窄），可调整以确保猫能跳过
TREE_SCALE = 0.9
# 树最小间距（像素），用于防止两棵树或更多障碍物生成得太靠近
TREE_MIN_GAP = 320
# 在尝试寻找合适生成位置时的最大重试次数
TREE_SPAWN_MAX_TRIES = 8
# 多层视差配置：天空层与地面层的速度因子（从远到近）
# 小于1 表示比基础速度慢（更远），大于1 表示更快（更近/前景）
PARALLAX_SKY_SPEEDS = [0.2, 0.45]
PARALLAX_GROUND_SPEEDS = [1.0, 1.4]
# 前景地面图层不透明度（0-255）——较低值让后方内容隐约可见
PARALLAX_GROUND_ALPHAS = [255, 200]
# 障碍物总体速度倍数（>1 增加障碍物移动速度）
# 已根据请求再次加快一些（由 1.6 -> 2.2）
OBSTACLE_SPEED_MULTIPLIER = 2.2

# 着陆/地面粒子（跳跃落地尘土）配置
DUST_PARTICLE_COUNT = 12
DUST_PARTICLE_LIFETIME = FPS // 6  # 较短寿命
DUST_PARTICLE_COLORS = [(210, 190, 150), (180, 160, 120)]
DUST_PARTICLE_SIZE_MIN = 4
DUST_PARTICLE_SIZE_MAX = 10

# 地面道具（Items）配置：生命包与护盾
ITEM_SPAWN_FREQ = 5000  # 毫秒，默认每 5 秒尝试生成一次道具
ITEM_MAX_ACTIVE = 2      # 场上同时存在的道具数量上限
ITEM_LIFETIME = 8 * FPS  # 帧数计数的生存时间

# 道具类型：血包、护盾、超级跳、金币
ITEM_TYPES = ['health', 'shield', 'superjump', 'coin']

# 各道具贴图（使用 barrier 里的图片）
SUPERJUMP_ITEM = 'assets/barrier/0_Archer_Running_007-3.png'   # 超级大跳
SHIELD_ITEM = 'assets/barrier/0_Archer_Running_007-4.png'      # 护盾
COIN_ITEM = 'assets/barrier/0_Archer_Running_007-5.png'        # 金币
HEALTH_ITEM = 'assets/barrier/0_Archer_Running_007-6.png'      # 血包

# 道具出现权重（频率），值越大越常见
ITEM_RARITY = {'health': 0.40, 'shield': 0.25, 'superjump': 0.15, 'coin': 0.20}

# 护盾时长（秒）
SHIELD_DURATION = 3

# 可选：道具音效路径（若无对应文件，会被忽略）
HEALTH_SOUND = 'assets/sound effect/hit.wav'
SHIELD_SOUND = 'assets/sound effect/Meow.ogg'

# 音乐路径
PREGAME_MUSIC = 'assets/music/bgm/begin.mp3'
# 场景背景音乐
SCENE_MUSIC_DEBUG = 'assets/music/bgm/level.mp3'      # 场景1和场景2
SCENE_MUSIC_BOSS = 'assets/music/bgm/boss.mp3'        # 场景3

INGAME_MUSIC = ['assets/music/HappyTune.mp3',
                'assets/music/TakeATrip.ogg', 'assets/music/TownTheme.mp3']

# 词库（用于打字目标）
WORDBANK = [
    {'en': 'python', 'zh': 'Python语言'}, {'en': 'import', 'zh': '导入'}, {'en': 'return', 'zh': '返回'},
    {'en': 'class', 'zh': '类'}, {'en': 'def', 'zh': '定义函数'}, {'en': 'yield', 'zh': '产出'},
    {'en': 'print', 'zh': '打印'}, {'en': 'range', 'zh': '范围'}, {'en': 'input', 'zh': '输入'},
    {'en': 'open', 'zh': '打开'}, {'en': 'string', 'zh': '字符串'}, {'en': 'integer', 'zh': '整数'},
    {'en': 'float', 'zh': '浮点数'}, {'en': 'boolean', 'zh': '布尔值'}, {'en': 'list', 'zh': '列表'},
    {'en': 'tuple', 'zh': '元组'}, {'en': 'set', 'zh': '集合'}, {'en': 'module', 'zh': '模块'},
    {'en': 'package', 'zh': '包'}, {'en': 'library', 'zh': '库'}, {'en': 'django', 'zh': 'Django框架'},
    {'en': 'flask', 'zh': 'Flask框架'}, {'en': 'pandas', 'zh': 'Pandas库'}, {'en': 'numpy', 'zh': 'NumPy库'},
    {'en': 'variable', 'zh': '变量'}, {'en': 'function', 'zh': '函数'}, {'en': 'method', 'zh': '方法'},
    {'en': 'object', 'zh': '对象'}, {'en': 'argument', 'zh': '实参'}, {'en': 'syntax', 'zh': '语法'},
    {'en': 'error', 'zh': '错误'}, {'en': 'debug', 'zh': '调试'}, {'en': 'compile', 'zh': '编译'},
    {'en': 'loop', 'zh': '循环'}, {'en': 'operator', 'zh': '运算符'}, {'en': 'instance', 'zh': '实例'},
    {'en': 'database', 'zh': '数据库'}, {'en': 'server', 'zh': '服务器'}, {'en': 'client', 'zh': '客户端'},
    {'en': 'request', 'zh': '请求'}, {'en': 'response', 'zh': '响应'}, {'en': 'api', 'zh': '接口'},
    {'en': 'json', 'zh': 'JSON格式'}, {'en': 'script', 'zh': '脚本'}, {'en': 'testing', 'zh': '测试'},
    # New words (<= 8 letters)
    {'en': 'code', 'zh': '代码'}, {'en': 'data', 'zh': '数据'}, {'en': 'file', 'zh': '文件'},
    {'en': 'path', 'zh': '路径'}, {'en': 'type', 'zh': '类型'}, {'en': 'name', 'zh': '名称'},
    {'en': 'self', 'zh': '自身'}, {'en': 'init', 'zh': '初始化'}, {'en': 'main', 'zh': '主函数'},
    {'en': 'true', 'zh': '真'}, {'en': 'false', 'zh': '假'}, {'en': 'none', 'zh': '空'},
    {'en': 'break', 'zh': '中断'}, {'en': 'pass', 'zh': '跳过'}, {'en': 'else', 'zh': '否则'},
    {'en': 'while', 'zh': '当...时'}, {'en': 'for', 'zh': '对于'}, {'en': 'try', 'zh': '尝试'},
    {'en': 'except', 'zh': '除了'}, {'en': 'raise', 'zh': '引发'}, {'en': 'with', 'zh': '使用'},
    {'en': 'from', 'zh': '从'}, {'en': 'global', 'zh': '全局'}, {'en': 'lambda', 'zh': '匿名函数'},
    {'en': 'async', 'zh': '异步'}, {'en': 'await', 'zh': '等待'}, {'en': 'map', 'zh': '映射'},
    {'en': 'filter', 'zh': '过滤'}, {'en': 'slice', 'zh': '切片'}, {'en': 'sort', 'zh': '排序'},
    {'en': 'len', 'zh': '长度'}, {'en': 'max', 'zh': '最大值'}, {'en': 'min', 'zh': '最小值'},
    {'en': 'sum', 'zh': '求和'}, {'en': 'zip', 'zh': '打包'}, {'en': 'dict', 'zh': '字典'},
    {'en': 'int', 'zh': '整型'}, {'en': 'str', 'zh': '字符串'}, {'en': 'bool', 'zh': '布尔'},
    {'en': 'byte', 'zh': '字节'}, {'en': 'char', 'zh': '字符'}, {'en': 'stack', 'zh': '栈'},
    {'en': 'queue', 'zh': '队列'}, {'en': 'heap', 'zh': '堆'}, {'en': 'tree', 'zh': '树'},
    {'en': 'graph', 'zh': '图'}, {'en': 'node', 'zh': '节点'}, {'en': 'root', 'zh': '根'},
    {'en': 'leaf', 'zh': '叶子'}, {'en': 'hash', 'zh': '哈希'}, {'en': 'index', 'zh': '索引'},
    {'en': 'key', 'zh': '键'}, {'en': 'value', 'zh': '值'}, {'en': 'item', 'zh': '项'},
    {'en': 'query', 'zh': '查询'}, {'en': 'logic', 'zh': '逻辑'}, {'en': 'math', 'zh': '数学'},
    {'en': 'random', 'zh': '随机'}, {'en': 'time', 'zh': '时间'}, {'en': 'date', 'zh': '日期'},
    {'en': 'sys', 'zh': '系统'}, {'en': 'os', 'zh': '操作系统'}, {'en': 'pip', 'zh': '包管理'},
    {'en': 'git', 'zh': '版本控制'}, {'en': 'push', 'zh': '推送'}, {'en': 'pull', 'zh': '拉取'},
    {'en': 'commit', 'zh': '提交'}, {'en': 'merge', 'zh': '合并'}, {'en': 'branch', 'zh': '分支'},
    {'en': 'clone', 'zh': '克隆'}, {'en': 'status', 'zh': '状态'}, {'en': 'diff', 'zh': '差异'},
    {'en': 'log', 'zh': '日志'}, {'en': 'tag', 'zh': '标签'}, {'en': 'head', 'zh': '头部'},
    {'en': 'origin', 'zh': '远程源'}, {'en': 'remote', 'zh': '远程'}, {'en': 'local', 'zh': '本地'},
    {'en': 'user', 'zh': '用户'}, {'en': 'host', 'zh': '主机'}, {'en': 'port', 'zh': '端口'},
    {'en': 'url', 'zh': '链接'}, {'en': 'http', 'zh': '超文本'}, {'en': 'html', 'zh': '网页'},
    {'en': 'css', 'zh': '样式'}, {'en': 'web', 'zh': '网络'}, {'en': 'net', 'zh': '网'},
    {'en': 'ip', 'zh': 'IP地址'}, {'en': 'bug', 'zh': '漏洞'}, {'en': 'fix', 'zh': '修复'},
    {'en': 'run', 'zh': '运行'}, {'en': 'build', 'zh': '构建'}, {'en': 'test', 'zh': '测试'},
    {'en': 'demo', 'zh': '演示'}, {'en': 'view', 'zh': '视图'}, {'en': 'model', 'zh': '模型'},
    {'en': 'form', 'zh': '表单'}, {'en': 'app', 'zh': '应用'}, {'en': 'bot', 'zh': '机器人'},
    {'en': 'ai', 'zh': '人工智能'}
]
