#!/usr/bin/env python
import hubo_ach as ha
import ach
import sys
import time
import math
import getch
from ctypes import *
import os

# Open Hubo-Ach feed-forward and feed-back (reference and state) channels
s = ach.Channel(ha.HUBO_CHAN_STATE_NAME)
r = ach.Channel(ha.HUBO_CHAN_REF_NAME)

# feed-forward will now be refered to as "state"
state = ha.HUBO_STATE()

# feed-back will now be refered to as "ref"
ref = ha.HUBO_REF()

# Get the current feed-forward (state) 
[statuss, framesizes] = s.get(state, wait=False, last=False)
LHP=0
RHP=0
RKN=0
RAP=0
LKN=0
LAP=0
RHY=0
RHR=0
LHR=0
RAR=0
LAR=0
h=0
k=0
a=0
l1=74.03
l2=74.38
l3=34.97
phi=0;
m=1
#Function to find the IK
def IK(x,y):
    l1=74.03
    l2=74.38
    l3=34.97
    phi=0;
    xw=x-l3*math.cos(0)
    yw=y-l3*math.sin(0)
    if(xw==0 and yw ==0):
      theta1=0
      theta2=0
      theta3=0
    else:
      theta2=math.pi-math.acos((l1**2+l2**2-xw**2-yw**2)/(2*l1*l2))
      theta1=math.atan(yw/xw)-math.acos((l1**2-l2**2+xw**2+yw**2)/(2*l1*math.sqrt(xw**2+yw**2)))
      theta3=phi-theta2-theta1;
    return theta1,theta2,theta3

def init(h,k,a):#the IK values are passed to this function
  h=h/500#The corresponding hip Knee and Ankle values are added in 500 increments
  k=k/500
  a=a/500
  hm=0
  km=0
  am=0
  REB=0
  LEB=0
  for i in range(0,500):
    REB=REB+0.0028
    ref.ref[ha.REB] = -REB
    LEB=LEB+0.0028
    ref.ref[ha.LEB] = -LEB
    r.put(ref)
    ##print 'h : ',hm,'k : ',km,'a : ',am
    hm=hm+h
    km=km+k
    am=am+a 
    ref.ref[ha.RHP] = hm
    ref.ref[ha.RKN] = km 
    ref.ref[ha.RAP] = am
    ref.ref[ha.LHP] = hm 
    ref.ref[ha.LKN] = km
    ref.ref[ha.LAP] = am
    r.put(ref)
    time.sleep(.0001)
    print hm,km,am
  return h,k,a
#Shifting the body weight to the directly to the left
#The value for the shift has been precalculated 
def shiftleft():
  RHR=0
  LHR=0
  RAR=0
  LAR=0
  for i in range (0,500): 
    time.sleep(.0005) 
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =-RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =-LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =LAR 
    r.put(ref) 
def shiftright():
  RHR=0
  LHR=0
  RAR=0
  LAR=0
  for i in range (0,500): 
    time.sleep(.0005) 
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =-RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =-LAR 
    r.put(ref) 
     
#shifting the body weight to the right along with a forward  
def dynshiftright():
  RHR=-0.3
  LHR=-0.3
  RAR=-0.3
  LAR=-0.3
  for i in range (0,500):  
    time.sleep(.0005)
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =-RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =-LAR 
    r.put(ref)
  for i in range (0,500):
    time.sleep(.0005)
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =-RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =-LAR 
    r.put(ref)  
def dynshiftleft():
  RHR=-0.3
  LHR=-0.3
  RAR=-0.3
  LAR=-0.3
  for i in range (0,500):  
    time.sleep(.0005)
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =-RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =-LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =LAR 
    r.put(ref)
  for i in range (0,500):
    time.sleep(.0005)
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =-RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =-LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =LAR 
    r.put(ref) 
def liftright():
  (h,k,a)=IK(80,0)#IK for the required End effector position
  (h1,k1,a1)=IK(160,0)#IK values of the previous end effector position
  #Since we dont have a feedback, we have to assume that the end effector is positioned without any errors.
  d1=h1-h#The difference between the previous IK value and the current IK value is calculated 
  d2=k1-k
  d3=a1-a 
  d1=d1/500#This difference is either added or subtracted in 500 increments
  d2=d2/500
  d3=d3/500
  REB=0
  LEB=0
  t1=d1
  t2=d2
  t3=d3
  for i in range(0,500):
    ref.ref[ha.RHP] = h1-d1
    ref.ref[ha.RKN] = k1-d2
    d1=d1+t1
    d2=d2+t2
    r.put(ref)
    time.sleep(.00005) 
  for i in range(0,500):    
    ref.ref[ha.RAP] = a1-d3
    d3=d3+t3
    r.put(ref)
    time.sleep(.0005)
#a function to lift the left leg
def liftleft():#previous IK value is passed, to find the difference between the two values 
  (h,k,a)=IK(80,0)#IK value for the required leg position
  (h1,k1,a1)=IK(160,0)
  ##print h1,k1,a1 
  d1=h1-h
  d2=k1-k
  d3=a1-a 
  d1=d1/500
  d2=d2/500
  d3=d3/500
  t1=d1
  t2=d2
  t3=d3
  for i in range(0,500):
    ref.ref[ha.LHP] = h1-d1
    ref.ref[ha.LKN] = k1-d2
    d1=d1+t1
    d2=d2+t2
    r.put(ref)
    time.sleep(.00005) 
  for i in range(0,500): 
    ref.ref[ha.LAP] = a1-d3
    d3=d3+t3
    r.put(ref)
    time.sleep(.0005)
#A function to take right foot forward
def rightforward(): 
  (h,k,a)=IK(80,-15)
  (h1,k1,a1)=IK(80,0)
  d1=h1-h
  d2=k1-k
  d3=a1-a 
  d1=d1/800
  d2=d2/800
  d3=d3/800
  t1=d1
  t2=d2
  t3=d3
  for i in range(0,800): 
    ref.ref[ha.RHP] = h1-d1 
    ref.ref[ha.RKN] = k1-d2
    d1=d1+t1
    d2=d2+t2
    r.put(ref)
    time.sleep(.0001)
  for i in range(0,800):
    ref.ref[ha.RAP] = a1-d3
    d3=d3+t3   
    r.put(ref)
    time.sleep(.001)
#left foot forward 
def leftforward(): 
  (h,k,a)=IK(80,-15)
  (h1,k1,a1)=IK(80,0)
  d1=h1-h
  d2=k1-k
  d3=a1-a 
  d1=d1/800
  d2=d2/800
  d3=d3/800
  t1=d1
  t2=d2
  t3=d3
  for i in range(0,800): 
    ref.ref[ha.LHP] = h1-d1 
    ref.ref[ha.LKN] = k1-d2
    d1=d1+t1
    d2=d2+t2
    r.put(ref)
    time.sleep(.0001)
  for i in range(0,800):
    ref.ref[ha.LAP] = a1-d3
    d3=d3+t3   
    r.put(ref)
    time.sleep(.00001)
#right foot down
#the right forward function has been integrated into this function
def rightdown(x): 
  (h,k,a)=IK(x,0)
  (h1,k1,a1)=IK(80,0)
  d1=h1-h
  d2=k1-k
  d3=a1-a 
  d1=d1/800
  d2=d2/800
  d3=d3/800
  t1=d1
  t2=d2
  t3=d3
  RHR=0
  LHR=0
  RAR=0
  LAR=0
  
  for i in range(0,800):
    ref.ref[ha.RHP] = h1-d1 
    ref.ref[ha.RKN] = k1-d2
    d1=d1+t1
    d2=d2+t2
    r.put(ref)
    time.sleep(.001)
  for i in range(0,800):
    ref.ref[ha.RAP] = a1-d3
    d3=d3+t3
    #print 'd1',d1,'d2',d2,'d3',d3
    time.sleep(.00001)
    r.put(ref)
#Left foot down
def leftdown(x):
  (h,k,a)=IK(x,0)
  (h1,k1,a1)=IK(80,0)
  d1=h1-h
  d2=k1-k
  d3=a1-a 
  d1=d1/800
  d2=d2/800
  d3=d3/800
  t1=d1
  t2=d2
  t3=d3
  RHR=0
  LHR=0
  RAR=0
  LAR=0
  for i in range(0,800):
    ref.ref[ha.LHP] = h1-d1 
    ref.ref[ha.LKN] = k1-d2
    d1=d1+t1
    d2=d2+t2
    r.put(ref)
    time.sleep(.001)
  for i in range(0,800):
    ref.ref[ha.LAP] = a1-d3
    d3=d3+t3
    #print 'd1',d1,'d2',d2,'d3',d3
    time.sleep(.000001)
    r.put(ref)
def leftturn1():
  RHY=0
  for i in range(0,800):
    RHY=RHY+.0002
    ref.ref[ha.RHY]=RHY
    print 'RHY',RHY
    r.put(ref)
    time.sleep(.0001) 
def leftturn2():
  LHY=0
  RHY=.2
  for i in range(0,800):
    #LHY=LHY+.00015
    RHY=RHY-.0002
    ref.ref[ha.LHY]=LHY
    ref.ref[ha.RHY]=RHY
    r.put(ref)
    time.sleep(.0001)
def rightturn1():
  LHY=0
  for i in range(0,800):
    LHY=LHY-.0002
    ref.ref[ha.LHY]=LHY
    print 'LHY',LHY
    r.put(ref)
    time.sleep(.0001) 
def rightturn2():
  LHY=-0.2
  RHY=0
  for i in range(0,800):
    #LHY=LHY+.00015
    LHY=LHY+.0002
    ref.ref[ha.LHY]=LHY
    ref.ref[ha.RHY]=RHY
    print 'LHY',LHY
    r.put(ref)
    time.sleep(.0001)
def centershift():
  RHR=-0.3
  LHR=-0.3
  RAR=-0.3
  LAR=-0.3
  for i in range (0,500):  
    time.sleep(.0005)
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =-RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =-LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =LAR 
    r.put(ref)
def centershift1():
  RHR=-0.3
  LHR=-0.3
  RAR=-0.3
  LAR=-0.3
  for i in range (0,500):  
    time.sleep(.0005)
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =-RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =-LAR 
    r.put(ref)










#shifting the body weight to the right along with a forward  
def dynshiftright1(x):
  (h,k,a)=IK(160,0)
  (s,l,p)=(h,k,a)
  (h1,k1,a1)=IK(160,x)
  d1=abs(h-h1)
  d2=abs(k-k1)
  d3=abs(a-a1)
  ##print d1,d2,d3
  if(x>0):
    d1=-d1
    d2=-d2
    d3=-d3
  d1=d1/500
  d2=d2/500
  d3=d3/500
  h=h/500
  k=k/500
  a=a/500
  RHR=-0.3
  LHR=-0.3
  RAR=-0.3
  LAR=-0.3
  hm=0
  km=0
  am=0
  t1=d1
  t2=d2
  t3=d3
  #the upper body is now centered
  for i in range (0,500):  
    time.sleep(.0005)
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =-RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =-LAR 
    r.put(ref)
    #print RHR,LHR,RAR,LAR
  #Now the weight shifts from the central position and is exerted on the right leg 
  #Two types of movements are done at the same loop, 
  #i) Body weight shifts to the right
  #ii) Body weight shifts forward
  for i in range (0,500):
    d1=d1+t1
    d2=d2+t2
    d3=d3+t3
    time.sleep(.0005)
    ref.ref[ha.RHP] = h1+d1
    ref.ref[ha.RKN] = k1+d2 
    ref.ref[ha.RAP] = a1-d3
    ##print h1+d1,k1+d2,a1-d3
    ref.ref[ha.LHP] = s+d1
    ref.ref[ha.LKN] = l+d2
    ref.ref[ha.LAP] = p-d3 
    ##print h1+d1,k1+d2,a1-d3 
    s1=s+d1
    l1=l+d2
    p1=p-d3
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =-RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =-LAR 
    #print RHR,LHR,RAR,LAR
    r.put(ref)
  
#function for lifting the right leg
def dynshiftleft1(x):
  (h,k,a)=IK(160,0)
  (s,l,p)=(h,k,a)
  (h1,k1,a1)=IK(160,x)
  ##print h,k,a
  ##print h1,k1,a1
  d1=abs(h-h1)
  d2=abs(k-k1)
  d3=abs(a-a1)
  if(x>0):
    d1=-d1
    d2=-d2
    d3=-d3
  ##print d1,d2,d3
  d1=d1/500
  d2=d2/500
  d3=d3/500
  h=h/500
  k=k/500
  a=a/500
  RHR=-0.3
  LHR=-0.3
  RAR=-0.3
  LAR=-0.3
  hm=0
  km=0
  am=0
  t1=d1
  t2=d2
  t3=d3
  #the upper body is now centered
  for i in range (0,500):  
    time.sleep(.0005)
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =-RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =-LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =LAR 
    r.put(ref)
  for i in range (0,500):
    time.sleep(.0005)
    d1=d1+t1
    d2=d2+t2
    d3=d3+t3
    ref.ref[ha.LHP] = h1+d1
    ref.ref[ha.LKN] = k1+d2 
    ref.ref[ha.LAP] = a1-d3
    ##print h1+d1,k1+d2,a1-d3
    ref.ref[ha.RHP] = s+d1 
    ref.ref[ha.RKN] = l+d2
    ref.ref[ha.RAP] = p-d3 
    ##print h1+d1,k1+d2,a1-d3 
    s1=s+d1
    l1=l+d2
    p1=p-d3
    RHR=RHR+0.000679603
    ref.ref[ha.RHR] =-RHR 
    LHR=LHR+0.000679603
    ref.ref[ha.LHR] =-LHR
    RAR=RAR+0.000679603
    ref.ref[ha.RAR] =RAR
    LAR=LAR+0.000679603
    ref.ref[ha.LAR] =LAR 
    r.put(ref)
 

def rightstep(sl):
  (h,k,a)=IK(80,sl)
  (h1,k1,a1)=IK(80,0)
  d1=h1-h
  d2=k1-k
  d3=a1-a 
  d1=d1/500
  d2=d2/500
  d3=d3/500
  t1=d1
  t2=d2
  t3=d3
  for i in range(0,500): 
    ref.ref[ha.RHP] = h1-d1 
    ref.ref[ha.RKN] = k1-d2
    d1=d1+t1
    d2=d2+t2
    r.put(ref)
    time.sleep(.001)
  for i in range(0,500):
    ref.ref[ha.RAP] = a1-d3
    d3=d3+t3   
    r.put(ref)
    time.sleep(.0001) 
  (h,k,a)=IK(160,sl)
  (h1,k1,a1)=IK(80,sl)
  d1=h1-h
  d2=k1-k
  d3=a1-a 
  d1=d1/500
  d2=d2/500
  d3=d3/500
  t1=d1
  t2=d2
  t3=d3
  RHR=0
  LHR=0
  RAR=0
  LAR=0
  
  for i in range(0,500):
    ref.ref[ha.RHP] = h1-d1 
    ref.ref[ha.RKN] = k1-d2
    d1=d1+t1
    d2=d2+t2
    r.put(ref)
    time.sleep(.001)
  for i in range(0,500):
    ref.ref[ha.RAP] = a1-d3
    d3=d3+t3
    ##print 'd1',d1,'d2',d2,'d3',d3
    time.sleep(.00001)
    r.put(ref)
#Left foot down
def leftstep(sl):
  (h,k,a)=IK(80,sl)
  (h1,k1,a1)=IK(80,0)
  d1=h1-h
  d2=k1-k
  d3=a1-a 
  d1=d1/500
  d2=d2/500
  d3=d3/500
  t1=d1
  t2=d2
  t3=d3
  for i in range(0,500): 
    ref.ref[ha.LHP] = h1-d1 
    ref.ref[ha.LKN] = k1-d2
    d1=d1+t1
    d2=d2+t2
    r.put(ref)
    time.sleep(.001)
  for i in range(0,500):
    ref.ref[ha.LAP] = a1-d3
    d3=d3+t3   
    r.put(ref)
    time.sleep(.0001) 
  (h,k,a)=IK(160,sl)
  (h1,k1,a1)=IK(80,sl)
  d1=h1-h
  d2=k1-k
  d3=a1-a 
  d1=d1/500
  d2=d2/500
  d3=d3/500
  t1=d1
  t2=d2
  t3=d3
  RHR=0
  LHR=0
  RAR=0
  LAR=0
  for i in range(0,500):
    ref.ref[ha.LHP] = h1-d1 
    ref.ref[ha.LKN] = k1-d2
    d1=d1+t1
    d2=d2+t2
    r.put(ref)
    time.sleep(.001)
  for i in range(0,500):
    ref.ref[ha.LAP] = a1-d3
    d3=d3+t3
    ##print 'd1',d1,'d2',d2,'d3',d3
    time.sleep(.00001)
    r.put(ref)
def squat(x,y,z):
  (h,k,a)=IK(x,0)
  (h1,k1,a1)=IK(y,0)
  d1=h1-h
  d2=k1-k
  d3=a1-a 
  d1=d1/500
  d2=d2/500
  d3=d3/500
  t1=d1
  t2=d2
  t3=d3
  RHR=0
  LHR=0
  RAR=0
  LAR=0
  if z == 1:
    for i in range(0,500):
      ref.ref[ha.RHP] = h1-d1 
      ref.ref[ha.RKN] = k1-d2
      ref.ref[ha.RAP] = a1-d3
      d1=d1+t1
      d2=d2+t2
      d3=d3+t3
      time.sleep(.01)
      r.put(ref)
  elif z== 0:
    for i in range(0,500):
      ref.ref[ha.LHP] = h1-d1 
      ref.ref[ha.LKN] = k1-d2
      ref.ref[ha.LAP] = a1-d3
      d1=d1+t1
      d2=d2+t2
      d3=d3+t3
      time.sleep(.01)
      r.put(ref)
##################################################################################
def origin(x,y):
  (h,k,a)=IK(x,0)
  (h1,k1,a1)=IK(y,0)
  d1=h1-h
  d2=k1-k
  d3=a1-a 
  d1=d1/500
  d2=d2/500
  d3=d3/500
  t1=d1
  t2=d2
  t3=d3
  RHR=0
  LHR=0
  RAR=0
  LAR=0
  
  for i in range(0,500):
      ref.ref[ha.RHP] = h1-d1 
      ref.ref[ha.RKN] = k1-d2
      ref.ref[ha.RAP] = a1-d3
      ref.ref[ha.LHP] = h1-d1 
      ref.ref[ha.LKN] = k1-d2
      ref.ref[ha.LAP] = a1-d3
      d1=d1+t1
      d2=d2+t2
      d3=d3+t3
      time.sleep(.01)
      r.put(ref)  






def leftturn():
  shiftleft()
  #time.sleep(4)
  liftright()
  leftturn1()
  rightdown(160)
  dynshiftright()
  liftleft()
  leftturn2()
  leftdown(160)
  time.sleep(2)
  centershift()        
def rightturn():
  shiftright()
  #time.sleep(4)
  liftleft()
  rightturn1()
  leftdown(160)
  dynshiftleft()
  liftright()
  rightturn2()
  rightdown(160)
  #time.sleep(2)
  centershift1()
def walkforward():
  liftright()
  rightstep(sl)
  dynshiftright1(sl)
  liftleft()
  leftstep(sl)
  dynshiftleft1(sl)
def walkbackward():
  liftright()
  rightstep(15)
  dynshiftright1(15)
  liftleft()
  leftstep(15)
  dynshiftleft1(15)  
while True:
  print 'Press i to initiate walking sequence or q to quit'
  print 'press p to initiate pistol squat'
  key = getch.getch()
  os.system('clear') 
  if key == 'p':
    (h,k,a)=IK(160,0)
    init(h,k,a) 
    print 'press A for left leg squat'
    print 'press D for right leg squat'
    k=getch.getch()
    if k == 'd':    
      RHR=0
      LHR=0
      RAR=0
      LAR=0
      for i in range (0,500): 
        time.sleep(.01) 
        RHR=RHR+0.0003
        ref.ref[ha.RHR] =RHR 
        LHR=LHR+0.0003
        ref.ref[ha.LHR] =LHR
        RAR=RAR+.0003
        ref.ref[ha.RAR] =-RAR
        LAR=LAR+.0003
        ref.ref[ha.LAR] =-LAR 
        r.put(ref)
      liftleft()
      while m==1: 
        os.system('clear')
        print 'Press W for up and S for down or press q to return back to main menu'
        k=getch.getch()
        if k=='s':
          squat(600,650,1)
          print 'press W'
          c=0 
        elif k=='w':
          squat(650,600,1)
          c=1
          print 'press S'
        elif k=='q':
          if c == 0:
            squat(650,600,0)
            rightdown(650)

            RHR=0.15
            LHR=0.15
            RAR=0.15
            LAR=0.15
            for i in range (0,500): 
              time.sleep(.01) 
              RHR=RHR+0.0003
              ref.ref[ha.RHR] =RHR 
              LHR=LHR+0.0003
              ref.ref[ha.LHR] =LHR
              RAR=RAR+.0003
              ref.ref[ha.RAR] =-RAR
              LAR=LAR+.0003
              ref.ref[ha.LAR] =-LAR 
              r.put(ref)
            m=0   
          elif c==1 :
            rightdown(650)
            RHR=0.15
            LHR=0.15
            RAR=0.15
            LAR=0.15
            for i in range (0,500): 
              time.sleep(.01) 
              RHR=RHR+0.0003
              ref.ref[ha.RHR] =RHR 
              LHR=LHR+0.0003
              ref.ref[ha.LHR] =LHR
              RAR=RAR+.0003
              ref.ref[ha.RAR] =-RAR
              LAR=LAR+.0003
              ref.ref[ha.LAR] =-LAR 
              r.put(ref)
            m=0    
    if k=='a':
      RHR=0
      LHR=0
      RAR=0
      LAR=0
      for i in range (0,500): 
        time.sleep(.01) 
        RHR=RHR+0.0003
        ref.ref[ha.RHR] =-RHR 
        LHR=LHR+0.0003
        ref.ref[ha.LHR] =-LHR
        RAR=RAR+.0003
        ref.ref[ha.RAR] =RAR
        LAR=LAR+.0003
        ref.ref[ha.LAR] =LAR 
        r.put(ref)
      liftright()
      while m==1: 
        os.system('clear')
        print 'Press W for up and S for down or press q to return back to main menu'
        k=getch.getch()
        if k=='s':
          os.system('clear')
          squat(600,650,0)
          c=0
          print 'press W' 
        elif k=='w':
          os.system('clear')
          squat(650,600,0)
          c=1
          print 'press S'
        elif k=='q':
          if c == 0:
            squat(650,600,0)
            rightdown(650)
            
            RHR=-0.15
            LHR=-0.15
            RAR=-0.15
            LAR=-0.15
            for i in range (0,500): 
              time.sleep(.01) 
              RHR=RHR+0.0003
              ref.ref[ha.RHR] =RHR 
              LHR=LHR+0.0003
              ref.ref[ha.LHR] =LHR
              RAR=RAR+.0003
              ref.ref[ha.RAR] =-RAR
              LAR=LAR+.0003
              ref.ref[ha.LAR] =-LAR 
              r.put(ref)
            origin(695,650)
            m=0   
          elif c==1 :
            rightdown(650)
            RHR=-0.15
            LHR=-0.15
            RAR=-0.15
            LAR=-0.15
            for i in range (0,500): 
              time.sleep(.01) 
              RHR=RHR+0.0003
              ref.ref[ha.RHR] =RHR 
              LHR=LHR+0.0003
              ref.ref[ha.LHR] =LHR
              RAR=RAR+.0003
              ref.ref[ha.RAR] =-RAR
              LAR=LAR+.0003
              ref.ref[ha.LAR] =-LAR 
              r.put(ref)
            origin(695,650)
            m=0    
  elif key=='i':
    (h,k,a)=IK(160,0)    
    init(h,k,a)  
    time.sleep(4)
    sl=-50
    while True:
      print 'press w to walk forward'
      print 'press a to turn left'
      print 'press d to turn right' 
      print 'press s to turn right'
      key = getch.getch()
      if key=='w':
        while key == 'w':
          for i in range (0,4):  
            shiftleft()     
            walkforward()
          key='q'
        liftright()
        rightstep(0)
        centershift1() 
        key = 'q'
      if key=='a':
        leftturn()
      if key=='d':
        rightturn() 
      if key=='s':
        shiftleft()
        walkbackward()
        liftright()
        rightstep(0)
        centershift1() 
  else:
    if key == 'q':
      print 'exit'
    else:
      print 'INVALID ENTRY : Press I to initialize or Q to quit'


r.close()
s.close()
