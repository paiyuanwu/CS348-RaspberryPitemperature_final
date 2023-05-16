

import RPi.GPIO as GPIO
import time
import sys
import cv2

cascPath = "haarcascade_frontalface_default.xml"
if len(sys.argv) > 1:
    cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)

if cv2.__version__.startswith('2'):
    PROP_FRAME_WIDTH = cv2.cv.CV_CAP_PROP_FRAME_WIDTH
    PROP_FRAME_HEIGHT = cv2.cv.CV_CAP_PROP_FRAME_HEIGHT
    HAAR_FLAGS = cv2.cv.CV_HAAR_SCALE_IMAGE
elif cv2.__version__.startswith('3') or cv2.__version__.startswith('4'):
    PROP_FRAME_WIDTH = cv2.CAP_PROP_FRAME_WIDTH
    PROP_FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT
    HAAR_FLAGS = cv2.CV_FEATURE_PARAMS_HAAR

cap = cv2.VideoCapture(0, cv2.CAP_V4L)
cap.set(PROP_FRAME_WIDTH, 320)
cap.set(PROP_FRAME_HEIGHT, 240)

GPIO.setmode(GPIO.BCM)      
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17,0)


def delayMicrosecond(t):  
    start,end=0,0           
    start=time.time()       
    t=(t-3)/1000000     
    while end-start<t:  
        end=time.time()     

tmp=[]      

data = 4  
# https://blog.zeruns.tech  
a,b=0,0


def DHT11():
    GPIO.setup(data, GPIO.OUT)  
    GPIO.output(data,GPIO.HIGH)
    delayMicrosecond(10*1000)  
    GPIO.output(data,GPIO.LOW) 
    delayMicrosecond(25*1000)    
    GPIO.output(data,GPIO.HIGH) 
    GPIO.setup(data, GPIO.IN)   
# https://blog.zeruns.tech    
    a=time.time()          
    while GPIO.input(data):
        b=time.time()       
        if (b-a)>0.1:     
            break           
        
    a=time.time()
    while GPIO.input(data)==0: 
        b=time.time()
        if (b-a)>0.1:
            break
                
    a=time.time()
    while GPIO.input(data):
        b=time.time()
        if (b-a)>=0.1:
            break   
            
    for i in range(40):        
        a=time.time()
        while GPIO.input(data)==0: 
            b=time.time()
            if (b-a)>0.1:
                break
# https://blog.zeruns.tech                        
        delayMicrosecond(28)   
            
        if GPIO.input(data):    
            tmp.append(1)       
                
            a=time.time()
            while GPIO.input(data):
                b=time.time()
                if (b-a)>0.1:
                    break
        else:
            tmp.append(0)       
            
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
#    frame = cv2.flip(frame, -1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=HAAR_FLAGS
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow("preview", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break



#
    del tmp[0:]                 
    time.sleep(1)               
# https://blog.zeruns.tech    
    DHT11()
  
    humidity_bit=tmp[0:8]      
    humidity_point_bit=tmp[8:16]
    temperature_bit=tmp[16:24]  
    temperature_point_bit=tmp[24:32]   
    check_bit=tmp[32:40]       
 
    humidity_int=0
    humidity_point=0
    temperature_int=0
    temperature_point=0
    check=0
# https://blog.zeruns.tech  
    for i in range(8):          # 二进制转换为十进制
        humidity_int+=humidity_bit[i]*2**(7-i)
        humidity_point+=humidity_point_bit[i]*2**(7-i)
        temperature_int+=temperature_bit[i]*2**(7-i)
        temperature_point+=temperature_point_bit[i]*2**(7-i)
        check+=check_bit[i]*2**(7-i)
  
    humidity=humidity_int+humidity_point/10
    temperature=temperature_int+temperature_point/10
  
    check_tmp=humidity_int+humidity_point+temperature_int+temperature_point
    
    #print("Temperature is ", temperature,"C\nHumidity is ",humidity,"%"," check: ", check, " checkTMP: ", check_tmp)
  
    if check==check_tmp and temperature!=0 and temperature!=0:
        print ("Found {0} faces!".format(len(faces)))
        print("Temperature is ", temperature,"C\nHumidity is ",humidity,"%")
        
        if temperature >  10:#| len(faces) > 0:
            print("風扇")
            GPIO.output(17,1)
        elif len(faces) > 0:
            print("風扇")
            GPIO.output(17,1)
        else:
            print("關風扇")
            GPIO.output(17,0)
    else:
        print("error")
        
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
  
    time.sleep(2)
GPIO.cleanup()
