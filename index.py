#coding:utf-8
import pygame, sys, random, time, easygui
from pygame.locals import *

pygame.init()

#创建窗口
canvas = pygame.display.set_mode((1200,715))
canvas.fill((255,255,255))
#导入图片
bg = pygame.image.load("images/background/bg235.jpg")
startGame =  pygame.image.load("images/logo/startGame.png")
logo =  pygame.image.load("images/logo/LOGO.png")

enemy1 = pygame.image.load("images/enemy/enemy1.png")
enemy2 = pygame.image.load("images/enemy/enemy2.png")
enemy3 = pygame.image.load("images/enemy/enemy3.png")
hero = pygame.image.load("images/hero/hero.png")
bullet = pygame.image.load("images/background/bullet1.png")
score = pygame.image.load("images/logo/score.png")

pause = pygame.image.load("images/logo/game_pause_nor.png")
over = pygame.image.load("images/logo/over.png")
#创建背景类
class Sky:
    def __init__(self):
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = -680
        self.width = 480
        self.height = 680
        self.img = bg
    def paint(self):
        draw(self.img, self.x1, self.y1)
        draw(self.img, self.x2, self.y2)
    def step(self):
        self.y1 += 1
        self.y2 += 1
        if self.y1 > self.height:
            self.y1 = -self.height
        if self.y2 > self.height:
            self.y2 = -self.height
#创建飞行父类
class Fly():
    def __init__(self,x,y,width,height,img,life):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.img = img
        self.canDel = False
        self.life = life
        self.moveLastTime = 0
        self.moveIntervalTime = 0.01 # 敌飞机移动的时间间隔
    #绘制图片
    def paint(self):
        draw(self.img, self.x, self.y)
        
    #移动
    def step(self):
        if not ifTimeDown(self.moveLastTime, self.moveIntervalTime):
            return
        AllVar.moveLastTime = time.time() 
        self.y += 3
    #是否碰撞
    def isHit(self, other):
        return self.x + self.width >= other.x and self.x < other.x + other.width\
            and self.y + self.height >= other.y and self.y < other.y + other.height
    #碰撞后逻辑处理
    def bang(self):
        self.life -= 1
        if self.life <= 0:
            self.canDel = True
            if hasattr(self, "score"):
                AllVar.score += self.score

#创建英雄机类
class Hero(Fly):
    def __init__(self,x,y,width,height,img,life):
        Fly.__init__(self, x, y, width, height, img, life)
        self.shootLastTime = 0
        self.shootInterval = 0.2# 单位为秒
        
    def shoot(self):
        if not ifTimeDown(self.shootLastTime, self.shootInterval):
            return
        self.shootLastTime = time.time()
        AllVar.bullets.append(Bullet(self.x+10, self.y, 10, 10, bullet, 1))
    def bang(self):
        self.life -= 1
        if self.life <= 0:
            self.canDel = True
            AllVar.state = 3
        AllVar.hero.x = 240
        AllVar.hero.y = 500
              
#创建敌飞机类
class Enemy(Fly):
    def __init__(self,x,y,width,height,img,life,score):
        Fly.__init__(self, x, y, width, height, img, life)
        self.score = score
    def isOut(self):
        return self.y > 650+self.height
        
#创建子弹类
class Bullet(Fly):
    def __init__(self,x,y,width,height,img,life):
        Fly.__init__(self, x, y, width, height, img, life)
        self.retime = 0.1
    def step(self):
        self.y -= 5
    def isOut(self):
        return self.y < -self.height
        
#随机产生敌飞机
def makeEnemys():
    if not ifTimeDown(AllVar.makeLastTime, AllVar.makeIntervalTime):
        return
    AllVar.makeLastTime = time.time()
      
    x1 = random.randint(0, 1300 - 57)
    x2 = random.randint(0, 1300 - 50)
    x3 = random.randint(0, 1300 - 169)
    n = random.randint(0,10)
    if n <=6:
        AllVar.enemys.append(Enemy(x1, 0, 57, 45, enemy1, 1, 1))
    elif n <= 9:
        AllVar.enemys.append(Enemy(x2, 0, 50, 68, enemy2, 3, 5))
    else:
        AllVar.enemys.append(Enemy(x3, 0, 169, 258, enemy3, 3, 10))
 
        
#绘制全部组件
def paintAll():
    if not ifTimeDown(AllVar.paintLastTime, AllVar.paintIntervalTime):
        return
    AllVar.paintLastTime = time.time()
    
    AllVar.sky.paint()
    AllVar.hero.paint()
    for enemy in AllVar.enemys:
        enemy.paint()
    for bullet in AllVar.bullets:
        bullet.paint()
    draw(score, 720 + 210, 10) #写分数
    renderText(str(AllVar.score), (780 + 305, 25))
    renderText(str(AllVar.hero.life), (780 + 305, 62))


#移动全部组件
def stepAll():
    AllVar.sky.step()
    for enemy in AllVar.enemys:
        enemy.step()
    for bullet in AllVar.bullets:
        bullet.step()


#检查全部组件碰撞
def cheackAll():
    for enemy in AllVar.enemys:
        if AllVar.hero.isHit(enemy):
            enemy.bang()
            AllVar.hero.bang()
        for bullet in AllVar.bullets:
            if enemy.isHit(bullet):
                enemy.bang()
                bullet.bang()
 
#删除
def delAll():
    for enemy in AllVar.enemys:
        if enemy.isOut() or enemy.life <= 0:
            AllVar.enemys.remove(enemy)
    for bullet in AllVar.bullets:
        if bullet.isOut() or bullet.life <= 0:
            AllVar.bullets.remove(bullet)


#创建全局变量
class AllVar():
    sky = None
    hero = None
    bullets = []
    enemys = []
    state = ""
    score = 0
    makeIntervalTime = 0.5 #产生敌飞机的时间间隔
    makeLastTime = 0#产生敌飞机的最后时间
    paintIntervalTime = 0.01# 重绘飞行物的时间间隔
    paintLastTime = 0# 重绘飞行物的时间间隔
    
    
#初始化变量
AllVar.state = 0
AllVar.sky = Sky()
AllVar.hero = Hero(600,600,60,75,hero,3)
AllVar.enemys.append(Enemy(200, 0, 57, 45, enemy1, 1, 1))

#处理互动事件
def handleEvent():
    for event in pygame.event.get():
        #退出监听
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            sys.exit() 
        #鼠标左键点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if AllVar.state == 0:
                AllVar.state = 1
        #监听键盘按键
        if event.type == KEYDOWN and event.key == K_r:
            if AllVar.state == 3:
                AllVar.score = 0
                AllVar.hero.life = 3
                AllVar.state = 0
        #监听鼠标移动事件
        if event.type == pygame.MOUSEMOTION:
            if AllVar.state == 1:
                AllVar.hero.x = event.pos[0]
                AllVar.hero.y = event.pos[1]
            # 鼠标移入移出事件切换状态
            if ifMouseOut():
                if AllVar.state == 1:
                    AllVar.state = 2
            if ifMouseIn():
                if AllVar.state == 2:
                    AllVar.state = 1
#对应状态写对应组件逻辑
def controlStates():
    if AllVar.state == 0:
        AllVar.sky.paint()
        AllVar.sky.step()
        draw(logo, 300, 200)
        draw(startGame, 500, 500)
    elif AllVar.state == 1:
        makeEnemys()
        paintAll()
        stepAll()
        AllVar.hero.shoot()
        cheackAll()
        delAll()
        
    elif AllVar.state == 2:
        paintAll()
        AllVar.sky.step()
        draw(pause, 500, 250)    
    elif AllVar.state == 3:
        paintAll()
        AllVar.sky.step()
        draw(over, 230, 250)
       

#工具方法
#判断是否已到时间间隔
def ifTimeDown(lastTime, intervalTime):
    if lastTime == 0:
        return True
    now = time.time()
    return now - lastTime >= intervalTime

#判断鼠标是否移出屏幕
def ifMouseOut():
    return AllVar.hero.x < 0 or AllVar.hero.x > 480 or\
        AllVar.hero.y < 0 or AllVar.hero.y > 650
#判断鼠标是否移入屏幕
def ifMouseIn():
    return AllVar.hero.x > 0 or AllVar.hero.x < 480 or\
        AllVar.hero.y > 0 or AllVar.hero.y < 650

#绘制图片
def draw(img, x, y):
    canvas.blit(img,(x,y))
# 写文字方法
def renderText(text, position):
    # 设置字体样式和大小
    my_font = pygame.font.Font("my_font/font1.ttf", 30)
    # 渲染文字
    text = my_font.render(text, True, (255, 255, 255))
    canvas.blit(text, position)    
    
#业务逻辑
while True:
    #将游戏流程切分成四种状态
    controlStates()
    #监听互动事件
    handleEvent()
    # 更新屏幕内容
    pygame.display.update()
    # 等待0.01秒后再进行下一次循环
    pygame.time.delay(5)
    