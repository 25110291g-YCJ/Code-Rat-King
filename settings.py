import pygame as pg
pg.init()

# 游戏尺寸
WIDTH, HEIGHT = 1600, 900  # 游戏窗口显示尺寸
GROUND_DEPTH = 200  # 地面深度
GROUND_HEIGHT = HEIGHT - GROUND_DEPTH  # 地面高度

# 可配置的猫起始 X 坐标（方便把猫放到屏幕偏左的位置）
# 默认在屏幕中间左移 120 像素
CAT_START_X = WIDTH // 2 - 120
GAMENAME_HEIGHT = HEIGHT // 5  # 游戏名称显示高度
GAMEMESSAGE_HEIGHT = HEIGHT // 1.25  # 游戏提示信息显示高度
TEXTTARGET_HEIGHT = GROUND_HEIGHT // 3  # 文本目标显示高度
SCOREMESSAGE_HEIGHT = HEIGHT//1.25  # 分数信息显示高度
CAT_WIDTH, CAT_HEIGHT = 162, 141  # 猫咪尺寸
DOG_WIDTH, DOG_HEIGHT = 162, 141  # 狗狗尺寸
TREE_WIDTH, TREE_HEIGHT = 264, 333  # 树木尺寸
HOUSE_WIDTH, HOUSE_HEIGHT = 300, 340  # 房屋尺寸
HOUSE_GROUND_OFFSET = 20  # 房屋相对地面的偏移

# 帧率、重力和移动速度
FPS = 60
# GRAVITY 在此项目中也被用作跳跃的初速度（负值向上），将其加大以提高跳跃高度
GRAVITY = -30
MOVING_SPEED = 3
MAX_MOVING_SPEED = 8
SPEED_INCREMENT = 0.4  # 每个难度阶段增加的速度
DIFFICULTY_SCORE_STEP = 20  # 每达到多少得分提升一次难度
CURRENT_MOVING_SPEED = MOVING_SPEED

# 字体
TARGET_FONT = pg.font.Font('assets/font/BubblegumSans.ttf', 150)
SCORE_FONT = pg.font.Font('assets/font/Purrfect.ttf', 100)
TITLE_FONT = pg.font.Font('assets/font/KittenSwash.ttf', 100)
TARGET_TEXT_COLOR = 'mediumslateblue'
TARGET_ALERT_COLOR = 'salmon'
SUPER_JUMP_TEXT_COLOR = 'gold'

# 生成频率与延迟时间
TREE_SPAWN_FREQ = 3000
TREE_SPAWN_MIN = 1500
TREE_SPAWN_STEP = 150
# 房屋默认在约 1 分钟出现（加上 ~4 秒移动距离）
HOUSE_SPAWN_FREQ = 56000
HOUSE_SPAWN_MIN = 35000
HOUSE_SPAWN_STEP = 5000
# 固定一次性房屋生成（毫秒）：用于只在开局后固定时刻生成房屋的模式
HOUSE_FIXED_SPAWN_MS = 60000
# 关卡过渡提示持续时长（毫秒）
LEVEL_TRANSITION_MS = 2000
DOG_SPAWN_FREQ = 30000
DOG_SPAWN_MIN = 12000
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
# 让超级跳跃高度略高于普通跳跃（使用 1.2 倍的初速度），并随 GRAVITY 调整。
SUPER_JUMP_FORCE = int(GRAVITY * 1.2)  # 使用 1.2 倍（例如 GRAVITY=-30 时约为 -36）
SUPER_JUMP_BONUS = 5
SUPER_JUMP_NOTICE_FRAMES = FPS
SUPER_JUMP_EFFECT_FRAMES = FPS // 2

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
    'common_tree': 'assets\\plants\\common_tree.png',
    'cypress_tree1': 'assets\\plants\\cypress_tree1.png',
    'cypress_tree2': 'assets\\plants\\cypress_tree2.png',
    'grass_tree1': 'assets\\plants\\grass_tree1.png',
    'grass_tree2': 'assets\\plants\\grass_tree2.png'
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
TREE_SCALE = 0.65
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
# 已根据请求再次加快一些（由 1.25 -> 1.6）
OBSTACLE_SPEED_MULTIPLIER = 1.6

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
ITEM_TYPES = ['health', 'shield']

# 简单权重（频率），值越大越常见
ITEM_TYPES = ['health', 'shield', 'superjump']
# 超级跳道具贴图
SUPERJUMP_ITEM = 'assets/items/zap.png'
# 血包道具贴图
HEALTH_ITEM = 'assets/items/heart.png'
# 简单权重（频率），值越大越常见。
# 调整为：health 0.50, shield 0.30, superjump 0.20（总计 1.0，便于理解与调试）
ITEM_RARITY = {'health': 0.50, 'shield': 0.30, 'superjump': 0.20}

# 护盾时长（秒）
SHIELD_DURATION = 3

# 可选：道具音效路径（若无对应文件，会被忽略）
HEALTH_SOUND = 'assets/sound effect/hit.wav'
SHIELD_SOUND = 'assets/sound effect/Meow.ogg'

# 音乐路径
PREGAME_MUSIC = 'assets/music/GrayTrip.mp3'
INGAME_MUSIC = ['assets/music/HappyTune.mp3',
                'assets/music/TakeATrip.ogg', 'assets/music/TownTheme.mp3']

# 词库（用于打字目标）
WORDBANK = ["apple", "banana", "cactus", "dolphin", "elephant", "fitness", "guitar", "happiness", "island", "jacket", "kitchen", "lovely", "money", "network", "ocean", "paradise", "question", "romantic", "sunset", "tourist", "universe", "vacation", "wonderful", "xylophone", "yellow", "zebra", "airport", "beautiful", "capital", "dance", "education", "freedom", "government", "hospital", "internet", "journey", "knowledge", "library", "medicine", "natural", "oasis", "peaceful", "quality", "romance", "success", "television", "ultimate", "victory", "wealth", "extraordinary", "friendship", "generous", "hospitality", "imagination", "jubilant", "kindness", "laughter", "miracle", "nature", "optimistic", "passionate", "quest", "romanticism", "satisfied", "triumph", "unbelievable", "vibrant", "wisdom", "xenial", "youthful", "zestful", "adventure", "beauty", "challenge", "dazzling", "excitement", "friendship", "generosity", "honesty", "innovation", "joyful", "kindhearted", "luxury", "music", "optimism", "passion", "quaint", "romance", "satisfaction", "travelling", "understanding", "vitality", "warmth", "xtraordinary", "youthfulness", "zeal", "affection", "blessed", "charming", "delight", "enthusiasm", "fascinating", "generous", "humility", "innovative", "jovial", "kindness", "love", "marvelous", "nourishing", "optimistic", "peace", "quality", "relaxation", "sensual", "thriving", "uplifting", "vibrance",
            "wholesome", "xceptional", "youthful", "zest", "abundance", "blissful", "calmness", "delightful", "exciting", "fantastic", "graceful", "harmony", "inspiration", "jubilation", "kindness", "lovely", "majestic", "nurturing", "oceanic", "pleasure", "quaintness", "rejuvenating", "serenity", "tranquility", "unforgettable", "vibrant", "wondrous", "xeniality", "youthfulness", "zealot", "affectionate", "breathtaking", "charming", "dazzling", "energetic", "flourishing", "glorious", "heavenly", "impressive", "joviality", "knightly", "loveable", "magnificent", "nourished", "oasis", "pleasurable", "quintessential", "refreshing", "spectacular", "thriving", "unforgotten", "vitality", "wondrous", "xpert", "yearning", "zestful", "adoration", "brilliant", "captivating", "delighted", "elegance", "fascinating", "gallant", "heartwarming", "innovative", "jubilant", "knight", "lovely", "mesmerizing", "nourishing", "optimistic", "peaceable", "pleased", "quaint", "relaxing", "satisfied", "tranquil", "unforgettable", "vibrance", "wholesome", "xceptional", "yielding", "zealous", "affectionate", "breathtaking", "charming", "dazzling", "enthusiastic", "flourishing", "glowing", "heavenly", "impressive", "jovial", "kindred", "loving", "mesmerizing", "nourished", "optimism", "peaceful", "pleased", "quaintness", "refreshing", "sensational", "thriving", "unforgotten", "vibrant", "warmhearted", "xpertise", "youthful", "zestful"]
