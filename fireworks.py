#fireworks.py

# events-example0.py
# Barebones timer, mouse, and keyboard events

from tkinter import *
import random, math

def distance(x0,y0,x1,y1):
    return ((x1-x0)**2 + (y1-y0)**2)**.5

def rgbString(value):
    return "#%02x%02x%02x" % (value, value, value)

#http://stackoverflow.com/questions/19175037/determine-a-b-c-of-quadratic-equation-using-data-points
def coefficient(x,y): # [x1,x2,x3], [y1,y2,y3]
    x_1 = x[0] 
    x_2 = x[1] 
    x_3 = x[2] 
    y_1 = y[0] 
    y_2 = y[1] 
    y_3 = y[2] 

    a = y_1/((x_1-x_2)*(x_1-x_3)) + y_2/((x_2-x_1)*(x_2-x_3)) + y_3/((x_3-x_1)*(x_3-x_2))

    b = (-y_1*(x_2+x_3)/((x_1-x_2)*(x_1-x_3))
         -y_2*(x_1+x_3)/((x_2-x_1)*(x_2-x_3))
         -y_3*(x_1+x_2)/((x_3-x_1)*(x_3-x_2)))

    c = (y_1*x_2*x_3/((x_1-x_2)*(x_1-x_3))
        +y_2*x_1*x_3/((x_2-x_1)*(x_2-x_3))
        +y_3*x_1*x_2/((x_3-x_1)*(x_3-x_2)))

    return a,b,c

class parabola(object): #used for the moon's path across the sky
    def __init__(self, p1,p2,p3): #three tuples of points
        self.xPoints = [p1[0],p2[0],p3[0]]
        self.yPoints = [p1[1],p2[1],p3[1]]
        self.solution = coefficient(self.xPoints,self.yPoints)
        self.a, self.b, self.c = self.solution[0], self.solution[1], self.solution[2]

    def YPosAtX(self,x): #where y is at at an X coord
        return ((x**2)*self.a) + (x*self.b) + self.c   

class moon(object): #moon object
    def __init__(self,data):
        self.cx = data.width//4
        self.cy = data.height//5
        self.r = 70
        self.path = parabola((self.cx,self.cy),((data.width//2)-100,50),(data.width-150,350))
        self.speed = .75
        self.color = "#edece3"
        self.craters = set()
        self.phases = [[0,0],[0,10],[0,20],[0,30],[0,40],[0,50],[0,60],[0,65],[0,0],[10,0],
                        [20,0],[30,0],[40,0],[50,0],[60,0],[65,0]]
        self.phaseIndex = random.randint(0,len(self.phases)-1)
        self.phase = self.phases[self.phaseIndex]
        
        for i in range(25): #add random crater objects to the moon surface
            self.craters.add(crater())

    def update(self,data):
        self.cx += self.speed
        self.cy = self.path.YPosAtX(self.cx)
        if self.cx > data.width+100: 
            self.cx = -100  
            self.phaseIndex = (self.phaseIndex+1)%(len(self.phases)-1)
            self.phase = self.phases[self.phaseIndex]

    def draw(self,canvas):
        x0,x1 = self.cx - self.r, self.cx + self.r
        y0,y1 = self.cy - self.r, self.cy + self.r  
        canvas.create_oval(x0,y0,x1,y1,fill=self.color)
        for thisCrater in self.craters: #draw discolored craters
            x0,x1 = self.cx + thisCrater.x - thisCrater.r, self.cx + thisCrater.x + thisCrater.r
            y0,y1 = self.cy + thisCrater.y - thisCrater.r, self.cy + thisCrater.y + thisCrater.r
            canvas.create_oval(x0,y0,x1,y1,fill=thisCrater.color,outline=thisCrater.color)
        x0,x1 = self.cx - self.r, self.cx + self.r
        y0,y1 = self.cy - self.r, self.cy + self.r

        
        P1,P2 = self.phase[0],self.phase[1]
        canvas.create_arc(x0+P1,y0,x1-P1,y1,fill="black",style=CHORD,extent=180,start=90,outline="black")
        canvas.create_arc(x0+P2,y0,x1-P2,y1,fill="black",style=CHORD,extent=180,start=270,outline="black")

class crater(object): #craters that appear on the moon surface
    def __init__(self):
        self.x = random.randint(0,45)
        self.y = random.randint(0,45)
        self.r = random.randint(5,10)
        self.color = "#d5d5d0"
        if random.randint(0,1) == 0: self.x *= -1
        if random.randint(0,1) == 0: self.y *= -1

class shootingStar(object): #shooting star random event
    def __init__(self,data):
        self.x, self.y = random.randint(0,data.width), random.randint(0,data.height)
        self.speedX, self.speedY = random.randint(25,40), random.randint(25,40)
        self.duration = 1500
        self.origin = (self.x,self.y)
        self.r = 3
        self.color = "white"
        self.trail = set()
        if random.randint(0,1) == 0: self.speedX *= -1
        if random.randint(0,1) == 0: self.speedY *= -1

    def update(self):
        self.x += self.speedX
        self.y += self.speedY
        self.trail.add(trailParticle(self))

    def isDone(self):
        return distance(self.x,self.y,self.origin[0],self.origin[1]) > self.duration

    def draw(self,canvas):
        x0,x1 = self.x - self.r, self.x + self.r
        y0,y1 = self.y - self.r, self.y + self.r
        canvas.create_oval(x0,y0,x1,y1,fill=self.color)
        for thisParticle in self.trail:
            thisParticle.draw(canvas)

class trailParticle(object): # shooting star trail particles that follow the star's path
    def __init__(self,shooting):
        self.x = shooting.x
        self.y = shooting.y
        self.color = 255
        self.r = 1

    def isDone(self):
        return self.color < 120

    def update(self):
        self.color -= 15
        if self.color < 0: self.color = 0

    def draw(self,canvas):
        x0,x1 = self.x - self.r, self.x + self.r
        y0,y1 = self.y - self.r, self.y + self.r
        canvas.create_oval(x0,y0,x1,y1,fill=rgbString(self.color))

class star(object): # background star objects
    #have random sizes and fade in and out at different rates
    def __init__(self, data):
        self.x = random.randint(0,data.width)
        self.y = random.randint(0,data.height)
        self.color = random.randint(120,250)
        self.r = random.randint(1,2)
        self.Cdirection = - random.randint(1,5)

    def draw(self,canvas):
        x0,x1 = self.x - self.r, self.x + self.r
        y0,y1 = self.y - self.r, self.y + self.r
        canvas.create_rectangle(x0,y0,x1,y1,fill=rgbString(self.color))

    def update(self): 
        self.color += self.Cdirection
        if self.color < 120: 
            self.Cdirection = - self.Cdirection
        elif self.color > 255:
            self.color = 255
            self.Cdirection = - self.Cdirection

class firework(object): #firework missile object
    def __init__(self,data,x,y=0,instant=False):
        self.instant = instant
        self.acceleration = 1
        self.x = x
        self.y = data.height
        self.speed = - random.randint(20,45)
        self.r = 4
        self.color = random.choice(["blue","red","yellow","green","pink","orange","cyan","magenta",
                                    "dodger blue","chocolate","firebrick","violet","green2", "yellow2",
                                    "white","sea green","yellow2","DeepPink2","red2","magenta2","VioletRed1"])
        self.sparkle = True if random.randint(0,10) == 0 else False
        self.stream = True if random.randint(0,8) == 0 else False

    def update(self,data):
        self.speed += self.acceleration #accoutnt fot acceleration
        self.y += self.speed
        if self.stream:
            speedX = random.random()
            if random.randint(0,1) == 0: speedX *= -1
            streamParticle = particle(data,self.x,self.y,speedX,-2,self.color,False)
            data.particles.add(streamParticle)


    def shouldExplode(self): #when it about to start falling it should explode
        return self.speed > -5 or self.instant == True

    def explode(self,data):
        explosionFactor = random.random() * 15
        layers = random.randint(2,8)
        #create a random number of layers that explode at a different speed
        for i in range(layers):
            for angle in range(0,360,10):
                radian = angle * (math.pi / 180)
                speed = i * explosionFactor * (random.randint(75,100)/200)
                speedX = math.cos(radian) * speed
                speedY = math.sin(radian) * speed
                data.particles.add(particle(data,self.x,self.y,speedX,speedY,self.color,self.sparkle))

    def draw(self,canvas):
        x0,x1 = self.x - self.r, self.x + self.r
        y0,y1 = self.y - self.r, self.y + self.r
        canvas.create_rectangle(x0,y0,x1,y1,fill=self.color)

class particle(object): #firework explosion particle objects
    def __init__(self,data,x,y,speedX,speedY,color,sparkle):
        self.origin = (x,y)
        self.x = x
        self.y = y
        self.speedX = speedX
        self.speedY = speedY
        self.acceleration = .1
        self.r = 2
        self.color = color
        self.sparkle = sparkle
        self.show = True
        if self.sparkle == True: self.show = random.choice([True,False])

    def update(self):
        self.speedY += self.acceleration #accoutnt for acceleration
        self.y += self.speedY
        self.x += self.speedX
        if self.sparkle == True: self.show = not self.show

    def draw(self,canvas):
        x0,x1 = self.x - self.r, self.x + self.r
        y0,y1 = self.y - self.r, self.y + self.r
        if self.show == True:
            canvas.create_rectangle(x0,y0,x1,y1,fill=self.color)

    def shouldFade(self): #if certain distance from the origin with some randomness
        return distance(self.origin[0],self.origin[1],self.x,self.y) > (500 * random.random())

def createFirework(data): #returns a random firework object
    xPos = random.randint(0,data.width)
    return firework(data,xPos)

####################################
# customize these functions
####################################

def init(data):
    data.timer = 0 #how long time has been running
    data.fireworks = set()
    data.particles = set()
    data.fireworks.add(createFirework(data))
    data.stars = set()
    data.shootingStars = []
    data.moon = moon(data)
    data.fireworkRate = 40 #how many ms for a chance of firework spawning

    for i in range(200): #create the star background
        data.stars.add(star(data))

def mousePressed(event, data):
    # use event.x and event.y
    data.fireworks.add(createFirework(data))
    #toggle between firework timing speeds
    if data.fireworkRate > 30: data.fireworkRate = 30
    else: data.fireworkRate = 40

def keyPressed(event, data):
    # use event.char and event.keysym
    key = event.keysym
    #granular control of friework spawn rate
    if key == "Up": 
        data.fireworkRate = max(30,data.fireworkRate-2)
    elif key == "Down": 
        data.fireworkRate = min(70,data.fireworkRate+2)
    elif key == "c":
        data.moon.phase = random.choice(data.moon.phases)

def timerFired(data):

    data.timer += data.timerDelay

    data.moon.update(data)
    
    #chance for a shooting star to spawn
    if random.randint(0,70) == 0:
        data.shootingStars.append(shootingStar(data))

    #update and clean up shooting stars
    for thisShooting in data.shootingStars:
        thisShooting.update()
        for thisParticle in thisShooting.trail:
            thisParticle.update()
        if thisShooting.isDone(): 
            data.shootingStars.remove(thisShooting)

    #chance at spawning firework 
    if data.timer % data.fireworkRate == 0:
        if random.randint(0,1) == 0:
            data.fireworks.add(createFirework(data))

    #firework cleanup
    fireworkRemove = set()
    for thisFirework in data.fireworks:
        thisFirework.update(data)
        if thisFirework.shouldExplode():
             thisFirework.explode(data)
             fireworkRemove.add(thisFirework)
    for thisFirework in fireworkRemove:     
        data.fireworks.remove(thisFirework)

    #particle cleanup
    particleRemove = set()
    for thisParticle in data.particles:
        thisParticle.update()
        if thisParticle.shouldFade():
             particleRemove.add(thisParticle)
    for thisParticle in particleRemove:
        data.particles.remove(thisParticle)

    #update the stars
    for thisStar in data.stars:
        thisStar.update()

def redrawAll(canvas, data):
    # draw in canvas
    canvas.create_rectangle(0,0,data.width,data.height, fill="black")
    #draw stars
    for thisStar in data.stars:
        thisStar.draw(canvas)
    #draw shooing stars
    for thisShooting in data.shootingStars:
        thisShooting.draw(canvas)\
    #draw the moon
    data.moon.draw(canvas)
    #draw fireworks
    for thisFirework in data.fireworks: 
        thisFirework.draw(canvas)
    #draw particles
    for thisParticle in data.particles:
        thisParticle.draw(canvas)

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 60 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1920, 1080)