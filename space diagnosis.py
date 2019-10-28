
# coding: utf-8

# In[1]:


#coding=utf-8  
#import numpy as np 
import cv2
import dlib
from scipy.spatial import distance
import os
from imutils import face_utils
import time
from tkinter import *
import tkinter.messagebox
import tkinter as tk
from PIL import Image,ImageTk
import winsound


# In[2]:


detector = dlib.get_frontal_face_detector()# 人脸检测器
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')# 人脸特征点检测器


# In[3]:


EYE_AR_THRESH = 0.22# EAR阈值
EYE_AR_CONSEC_FRAMES = 20# 当EAR小于阈值时，接连多少帧算作进行了闭眼。本机帧率约为729fps

# 对应特征点的序号
RIGHT_EYE_START = 37 - 1
RIGHT_EYE_END = 42 - 1
LEFT_EYE_START = 43 - 1
LEFT_EYE_END = 48 - 1

#播放的声音的频率和时间
duration = 600  # millisecond
freq_yes = 500  # 测试通过
freq_no=220;#测试不通过


# In[4]:


def eye_aspect_ratio(eye):
    # print(eye)
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear1 = (A + B) / (2.0 * C)
    return ear1


# In[5]:


frame_counter = 0# 连续帧计数 
close_eye = 0# 眨眼计数
on_hit = False
def video_loop():
    global frame_counter
    global close_eye
    global time_ori
    global on_hit
    #global ear
    success, img = camera.read()  # 从摄像头读取照片
    if success:
        if on_hit:
            cv2.waitKey(1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)# 转成灰度图像
            rects = detector(gray, 0)# 人脸检测
            for rect in rects:# 遍历每一个人脸（实际应该只有一个）
                shape = predictor(gray, rect)# 检测特征点
                points = face_utils.shape_to_np(shape)# convert the facial landmark (x, y)-coordinates to a NumPy array
                leftEye = points[LEFT_EYE_START:LEFT_EYE_END + 1]# 取出左眼对应的特征点
                rightEye = points[RIGHT_EYE_START:RIGHT_EYE_END + 1]# 取出右眼对应的特征点
                leftEAR = eye_aspect_ratio(leftEye)# 计算左眼EAR
                rightEAR = eye_aspect_ratio(rightEye)# 计算右眼EAR
                ear = (leftEAR + rightEAR) / 2.0# 求左右眼EAR的均值
                leftEyeHull = cv2.convexHull(leftEye)# 寻找左眼轮廓
                rightEyeHull = cv2.convexHull(rightEye)# 寻找右眼轮廓
                cv2.drawContours(img, [leftEyeHull], -1, (0, 255, 0), 1)# 绘制左眼轮廓
                cv2.drawContours(img, [rightEyeHull], -1, (0, 255, 0), 1)# 绘制右眼轮始计算连续帧，只有连续帧计数超过EYE_AR_CONSEC_FRAMES时，才会计做一次眨眼
                if ear < EYE_AR_THRESH:
                    frame_counter +=1 
            if frame_counter >= EYE_AR_CONSEC_FRAMES:
#                 close_eye += 1
#                 frame_counter = 0
                winsound.Beep(freq_yes, duration)#提示音，医生可以及时关闭程序
                r=tkinter.messagebox.showinfo(title='闭眼检测', message='指令完成，测试通过！')  
                print(r)
                frame_counter=0;
                var.set('')
                var1.set('开始检测')
                del rects
                on_hit=False;
            time_now=time.time()#当前的时间戳
            if time_now-time_ori>=30 and on_hit:#时间超过30秒，认为测试不通过
                winsound.Beep(freq_no, duration)
                r=tk.messagebox.showerror(title='闭眼检测', message='时间已到，测试不通过！')  
                print(r)
                del rects
                var.set('')
                var1.set('开始检测')
                on_hit=False;
            cv2.putText(img, "Close_num:{0}".format(close_eye), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
        #cv2.putText(img, "EAR:{:.2f}".format(ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)   
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)#转换颜色从BGR到RGBA
        current_image = Image.fromarray(cv2image)#将图像转换成Image对象
        imgtk = ImageTk.PhotoImage(image=current_image)
        panel.imgtk = imgtk
        panel.config(image=imgtk)
        root.after(1, video_loop)
        
camera = cv2.VideoCapture(0)    #摄像头
root = Tk()
root.title("闭眼检测")
#root.protocol('WM_DELETE_WINDOW', detector)
panel = Label(root)  # initialize image panel
panel.pack(padx=4, pady=6)
var = tk.StringVar()    # 将label标签的内容设置为字符类型，用var来接收hit_me函数的传出内容用以显示在标签上
var1 = tk.StringVar()
l = tk.Label(root, textvariable=var, bg='white', font=('Arial',40), width=18, height=4)
l.pack()
var1.set('开始检测')
#l = tk.Label(window, textvariable=var, bg='green', fg='white', font=('Arial', 12), width=30, height=2)
def hit_me():
    global on_hit
    global time_ori;
    if on_hit == False:
        on_hit = True
        time_ori=time.time()#开始运行时的时间戳
        var.set('您好，请闭上您的眼睛')
        var1.set('检测中')
#b = tk.Button(root, text='开始检测', font=('Arial', 12), width=10, height=1, command=hit_me)
b = tk.Button(root, textvariable=var1, font=('Arial', 12), width=10, height=2, command=hit_me)
b.pack()
root.config(cursor="arrow")

video_loop()

root.mainloop()

camera.release()
cv2.destroyAllWindows()
 


# In[ ]:




