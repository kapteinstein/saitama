import sys
import cv2
import datetime
import os
import numpy as np

default_dir = "captures/"

class CameraService():
    def __init__(self,dir_folder):
        self.cam = cv2.VideoCapture(0)
        self.dir_folder = dir_folder
        if(not os.path.isdir(dir_folder)):
            os.makedirs(dir_folder)

    def get_snapshot(self,name = "snapshot",p=100):
        img_path = self.dir_folder + name + ".jpg"
        print(img_path)
        ret,img = self.cam.read()
        img = np.pad(img, [(p,p),(p,p),(0,0)],mode='constant',)
        cv2.imwrite(img_path,img)
        return img_path

def main():
    if(len(sys.argv)>2):
        dir_folder = sys.argv[1]
        name = sys.argv[2]
    elif(len(sys.argv)>1):
        dir_folder = default_dir
        name = sys.argv[1]
    else:
        dir_folder = default_dir
        name = "Capture_"+str(datetime.date.today())
    
    if(dir_folder[-1] != "/"):
        dir_folder += "/"    
    cam = CameraService(dir_folder)
    cam.get_snapshot(name)
    return name

if __name__ == "__main__":
    main()
    
        
