# -*- coding: utf-8 -*-
"""
Created on Mon May  2 15:19:54 2022

@author: Stefan Kaufmann
Abschlussprojekt

1_ Bildbearbeitung
"""

#standard import
import numpy as np
import matplotlib.pyplot as plt
from math import pi

# Open CV
import cv2
from math import atan2, cos, sin, sqrt, pi


class Bilder:  
    # Größe des Skalierten Bildes
    x = 750
    y = 500      
    j = np.array([], dtype=int)       
    count = 0
    obj = []   
    im_dst = 0                               # Bild nach der Skalierung
    plot = False                              # Plotten der Schwereachsen

       
    def __init__(self, img):              
         self.img = img
         
    def maske(self):
        
        if self.count == 0:
            lower = np.array([40,80,80]) 
            upper = np.array([86,230,230]) 
            hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
            self.mask = cv2.inRange(hsv, lower, upper) 
            #cv2.imshow('Maske', self.mask)
            
        else:
            gray = cv2.cvtColor(b.im_dst, cv2.COLOR_BGR2GRAY)
            self.mask = cv2.inRange(gray, 130, 255)
            self.j = []
            #cv2.imshow('Maske2', self.mask)
            
            
       
    def findObjekte(self):
        self.maske()
        self.segmentieren()
      
    
    def ausrichten(self):    
        print('aurichten')
         
        self.maske()             
        
        # Aufrufen der Segmentierung      
        
        self.segmentieren()    
        
        
        # MC sortieren                    
        mc = self.mc
        self.mc = self.mc[self.mc[:,1].argsort()]        
        #print(self.mc)
        if self.mc[0,0] < self.mc[1,0]:            
            temp = np.copy(self.mc[0,:])
            self.mc[0,:] = self.mc[1,:]
            self.mc[1,:] = temp
    
        if self.mc[2,0] > self.mc[3,0]:             
              temp = np.copy(self.mc[2,:])
              self.mc[2,:] = self.mc[3,:]
              self.mc[3,:] = temp
        
        
                
        # Points in destination image        
        points_dst = np.array([ [self.x, 0], [0, 0],[0, self.y],[self.x, self.y] ])
        
        # Homography
        h, status = cv2.findHomography(self.mc, points_dst)          
        self.im_dst = cv2.warpPerspective(self.img, h, (self.x,self.y))
        print('Ende erster Durchlauf')
    
        
    def segmentieren(self):
        self.contours, hierarchy = cv2.findContours(self.mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        
        
        # Counturs Filtern     
        
        
        for i in range(len(self.contours)):       
            area = cv2.contourArea(self.contours[i])
            if area > 150 and self.count == 0:                 
                self.j = np.append(self.j,[i] )
            elif area > 100  and self.count > 0:                   # Fläche Überprüfen
                x,y,w,h = cv2.boundingRect(self.contours[i]) 
                if 0< x < self.x and 0< y < self.y:                # Position Überprüfen
                    obj = np.array([x,y,w,h]) 
                    self.j = np.append(self.j,[i] )  
                    self.obj = np.append(self.obj,obj)

        self.j = self.j[0:len(self.j)]  
        self.j = self.j.astype(int)
        
        if self.count > 0:
            self.obj = np.resize(self.obj,(len(self.j),4))   
            self.obj = self.obj.astype(int)
        
      
           
        
        # Get the moments
        mu = [None]*len(self.j)
        for i in range(len(self.j)):            
            mu[i] = cv2.moments(self.contours[self.j[i]])
       
         

        
        # Get the mass centers
        mc = [None]*len(self.j)
        for i in range(len(self.j)):           
            # add 1e-5 to avoid division by zero
            mc[i] = (mu[i]['m10'] / (mu[i]['m00'] + 1e-5), mu[i]['m01'] / (mu[i]['m00'] + 1e-5))        
        mc = np.asarray(mc)   # Konvertierung in ein Array        
        self.mc = mc.astype(int)
        
        
        if self.count > 0:
                   
            # Get the orientation
            mo = [None]*len(self.j)
            for i in range(len(self.j)):   
                mo[i] = self.getOrientation(mu[i])
            self.mo = np.asarray(mo)
            
            # Get mini Pictures of each obj            
            mp = [None]*len(self.j)
            for i in range(len(self.j)):   
                mp[i] = self.zuschneiden(self.im_dst, self.obj[i])            
            self.mp = mp
            
        
        
       
        
            
            
        
        
        self.count += 1 # Nächster Schritt
    
    def getOrientation(self, mu):
    
        
        x = int(mu["m10"] / mu["m00"])
        y = int(mu["m01"] / mu["m00"])
        center = (x,y)
        
        a = int(mu["m20"] - mu["m10"]*mu["m10"]/mu["m00"])
        b = int(mu["m02"] - mu["m01"]*mu["m01"]/mu["m00"])
        c = int(mu["m11"] - mu["m10"]*mu["m01"]/mu["m00"])
        
        
        J = np.array([[a, c],[c, b]])
        ew,ev = np.linalg.eig(J)
        
        alpha = np.round(atan2(ev[0,1],ev[1,1])*180/pi-90 +360   ,1)           
    
        s = 20  # Skalierung der Pfeile
        
        if self.plot == True:            
            font = cv2.FONT_HERSHEY_SIMPLEX   
            fontScale = 0.6
            color = (0, 0, 0)
            thickness = 1
            cv2.putText(self.im_dst, str(alpha), (x,y) , font, fontScale, color, thickness)
            image = cv2.line(self.im_dst, center, (x+int(ev[0,0]*s),y+int(ev[1,0]*s)), (0,255,0), 2)
            self.image = cv2.line(self.im_dst, center, (x+int(ev[0,1]*s*3),y+int(ev[1,1]*s*3)), (0,0,0), 2)                     
            cv2.imshow('Schwereachsen', self.image)        
         
        return alpha
        
     
    def zuschneiden(self, img, obj):
        d = 2          # Bildüberstand
        x = int(obj[0])
        y = int(obj[1])
        w = int(obj[2])
        h = int(obj[3])
               
        image = img[(y-d):(y+h+d), (x-d):(x+w+d)]
        if self.plot == True:
            cv2.imshow('Bilder_zugeschnitten', image)           
        return image
 
    
              
            
        
# h, status = cv2.findHomography(a, points_dst)        
# im_dst = cv2.warpPerspective(img, h, (x,y))
# cv2.imshow('img', im_dst)

#%%
if __name__=="__main__":
    cv2.destroyAllWindows()


    path = 'Kamerabilder/TX2_SM_kontakt.png'
    
    # reading the image
    img = cv2.imread(path) 
    
    b = Bilder(img)
    b.ausrichten()
    
    for i in range(len(b.j)):
        image = cv2.circle(img, b.mc[i,:], 50, (255, 0, 0), 5)
        cv2.imshow('img', image)
    

    cv2.imshow('im_dst', b.im_dst)
        
    b.findObjekte()
    
    obj = b.obj    
    a = 10
    for i in range(len(b.j)):
        #image = cv2.circle(b.mask, b.mc[i,:], 10, (255, 0, 0), 7)       
           
        cv2.rectangle(b.im_dst,(obj[i,0]-a,obj[i,1]-a),(obj[i,0]+obj[i,2]+a,a+obj[i,1]+obj[i,3]),(0,255,0),1)
        cv2.imshow('im_dst', b.im_dst)

    
   
    
    #wait for a key to be pressed to exit
    print('Press any key')
    cv2.waitKey(0)
 
    # close the window
    cv2.destroyAllWindows()
    