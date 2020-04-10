import sys
import numpy as np
import time
import threading

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import json

import sys, random
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt
import copy
from functools import partial

ROOT_DIR = 'F:/AICLS/Pose_imgs'
ANNO_DIR = 'F:/AICLS/Pose_anns'
if not os.path.exists(ANNO_DIR):
    os.makedirs(ANNO_DIR)

PartNames = ["边框","头", "左耳", "右耳", "左眼", "右眼", "鼻尖", "左嘴角", "右嘴角", "下巴", "左肩", "右肩"]

class Annos():
    def __init__(self):
        self.init()

    def init(self):
        self.imagepath = None
        self.scaleratio = 1.0
        self.keypoints = []
        self.cur_keypoint = np.zeros((11,3), dtype = np.float32)
        self.cur_bbox = [0.0,0.0,0.0,0.0]
        self.cur_partID = 0
        self.cur_vis = True

    def newItem(self):
        keypoint = {}
        keypoint['keypoint'] = copy.deepcopy(self.cur_keypoint.reshape(-1).tolist())
        keypoint['box'] = copy.deepcopy(self.cur_bbox)
        self.keypoints.append(keypoint)
        self.cur_keypoint = np.zeros((11,3), dtype = np.float32)
        self.cur_bbox = [0.0,0.0,0.0,0.0]
        self.cur_partID = 0
        self.cur_vis = True

    def savejson(self):
        if self.imagepath:
            if np.sum(self.cur_keypoint) > 0:
                self.newItem()
            if len(self.keypoints) > 0:
                res = {'imagepath': self.imagepath, 'scaleratio': self.scaleratio, 'keypoints':self.keypoints}
                imgfile = self.imagepath.split("/")[-1]
                imgname = os.path.splitext(imgfile)[0]
               # savepath = self.imagepath.replace(ROOT_DIR, ANNO_DIR)+'_annos.json'
                savepath = os.path.join(ANNO_DIR,imgname + '.json')
                with open(savepath, 'w') as f:
                    json.dump(res, f)

    def print(self, log):
        print ('-------------- < %s > ------------'%log)
        print ('imagepath:', self.imagepath)
        print ('scaleratio:', self.scaleratio)
        print ('keypoints:', self.keypoints)
        print ('cur_keypoint:', self.cur_keypoint)
        print ('cur_bbox:', self.cur_bbox)
        print ('cur_partID:', self.cur_partID)
        print ('cur_vis:', self.cur_vis)

CurrentAnnos = Annos()

class MyQLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.label_maxw = 1280.0
        self.label_maxh = 800.0
        self.setGeometry(100, 50, self.label_maxw, self.label_maxh) 

        self.pen = QPen()
        self.pen.setWidth(5)
        self.pen.setBrush(Qt.red)

        self.pos = None
        self.png = None
        self.rect_f = False
        
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        
    def paintEvent(self, e):
        global CurrentAnnos
        qp = QPainter()
        qp.begin(self)
        if self.png:
            qp.drawPixmap(0,0, self.png)
        if self.pos:
            qp.setPen(self.pen)
            qp.drawPoint(self.pos.x(), self.pos.y()) 
        
        if(CurrentAnnos.cur_partID == 0):
            if(self.x0 !=0 and self.x1 != 0):
                rect =QRect(self.x0,self.y0,self.x1-self.x0,self.y1-self.y0)
                qp.setPen(self.pen)
                qp.drawRect(rect) 
        
        for ann in CurrentAnnos.keypoints:
            keypoints = np.array(ann['keypoint']).reshape((11,3))
            self.pen.setWidth(5)
            self.pen.setBrush(Qt.green)
            for point in keypoints:
                if(point[2]>0):
                    qp.setPen(self.pen)
                    qp.drawPoint(point[0], point[1]) 
            
            box = ann['box']
            rect =QRect(box[0],box[1],box[2]-box[0],box[3]-box[1])
            
            self.pen.setWidth(3)
            self.pen.setBrush(Qt.blue)
            qp.setPen(self.pen)
            qp.drawRect(rect)
            self.pen.setBrush(Qt.red) 

        qp.end()
        
    def mouseMoveEvent(self,e):
        if(CurrentAnnos.cur_partID == 0):
            self.pos = e.pos()
            if self.rect_f:
                self.x1 = self.pos.x()
                self.y1 = self.pos.y()
                self.update()
            
    def mouseReleaseEvent(self,e):
        self.pos = e.pos()
        # print ('PRESS: %d,%d'%(self.pos.x(), self.pos.y()))
        # self.update() 
        
        if(CurrentAnnos.cur_partID == 0):
            self.rect_f = False
            self.x1 = self.pos.x()
            self.y1 = self.pos.y()
            CurrentAnnos.cur_bbox = [self.x0,self.y0,self.x1,self.y1]
            self.x0 = 0
            self.y0 = 0
            self.x1 = 0
            self.y1 = 0
        
    def mousePressEvent(self, e):
        self.pos = e.pos()
        print ('PRESS: %d,%d'%(self.pos.x(), self.pos.y()))
        self.update() 

        global CurrentAnnos
        if CurrentAnnos.imagepath:
            if(CurrentAnnos.cur_partID == 0):
                self.rect_f = True
                self.x0 = self.pos.x()
                self.y0 = self.pos.y()
            else:
                self.update() 
                CurrentAnnos.cur_keypoint[CurrentAnnos.cur_partID-1, 0] = self.pos.x()
                CurrentAnnos.cur_keypoint[CurrentAnnos.cur_partID-1, 1] = self.pos.y()
                if CurrentAnnos.cur_vis == True:
                    CurrentAnnos.cur_keypoint[CurrentAnnos.cur_partID-1, 2] = 1
                elif CurrentAnnos.cur_vis == False:
                    CurrentAnnos.cur_keypoint[CurrentAnnos.cur_partID-1, 2] = 2
                CurrentAnnos.print('mousePressEvent')

    def loadimg(self, filename):
        self.pos = None
        png = QPixmap(filename)
        ratio = min( self.label_maxw / png.width(), self.label_maxh / png.height())
        self.png = png.scaled(png.width()*ratio, png.height()*ratio)
        self.update() 

        global CurrentAnnos
        CurrentAnnos.init()
        CurrentAnnos.imagepath = filename
        CurrentAnnos.scaleratio = ratio
        CurrentAnnos.print('loadimg')

class ControlWindow(QMainWindow):
    def __init__(self):
        super(ControlWindow, self).__init__()
        self.setGeometry(50, 50, 1400, 860)
        self.setWindowTitle("AnnoSystem")

        self.nextImageAction = QAction("&NextImage", self)
        self.nextImageAction.setShortcut("Q")
        self.nextImageAction.triggered.connect(partial(self.nextImage, +1))
        
        self.preImageAction = QAction("&PreImage", self)
        self.preImageAction.setShortcut("A")
        self.preImageAction.triggered.connect(partial(self.nextImage, -1))

        self.nextItemAction = QAction("&NextPerson", self)
        self.nextItemAction.setShortcut("R")
        self.nextItemAction.triggered.connect(self.nextItem)
        
        self.nextPartAction = QAction("&NextPart", self)
        self.nextPartAction.setShortcut("W")
        self.nextPartAction.triggered.connect(self.nextPart)
        
        self.changeVisAction = QAction("&ChangeVisState", self)
        self.changeVisAction.setShortcut("E")
        self.changeVisAction.triggered.connect(self.changeVisState)

        self.saveAction = QAction("&SaveAnn", self)
        self.saveAction.setShortcut("S")
        self.saveAction.triggered.connect(self.saveAnn)

        self.mainMenu = self.menuBar()
        self.mainMenu.addAction(self.nextImageAction)
        self.mainMenu.addAction(self.preImageAction)
        self.mainMenu.addAction(self.nextItemAction)
        self.mainMenu.addAction(self.changeVisAction)
        self.mainMenu.addAction(self.nextPartAction)
        self.mainMenu.addAction(self.saveAction)
        
        self.currentID  = -1
        self.imagelistmp= os.listdir(ROOT_DIR)
        self.annlistmp  = os.listdir(ANNO_DIR)
        self.annlists   = [os.path.splitext(file)[0] for file in self.annlistmp]
        
        self.imagelist = []
        for file in self.imagelistmp:
            if(os.path.splitext(file)[0] in self.annlists):
                continue
            else:
                self.imagelist.append(file)
                
        print("Image num: ", len(self.imagelist))
      #  self.imagelist = [item for item in self.imagelist if item[-4:]=='.jpg' or item[-5:]=='.jpeg']
        self.imagelist.sort(key=lambda x:int(x[:-4]))

        self.qlabel = MyQLabel(self)

        BodyPartBox = QWidget(self)
        BodyPartBoxlayout = QVBoxLayout()
        self.buttonlist = []
        for i in range(12):
            button = QRadioButton(PartNames[i])
            button.clicked.connect(partial(self.changePart, i))
            self.buttonlist.append(button)
            BodyPartBoxlayout.addWidget(button)
              
        self.buttonlist[0].setChecked(True)
        self.buttonlist[0].setStyleSheet("background-color: red")
        BodyPartBox.setLayout(BodyPartBoxlayout)
        BodyPartBox.setGeometry(10, 30, 90, 600) 

		# self.hintbox.setText('下一张／上一张图： Q／A     本图下一个人：R      下一个部位：W   
        
    def saveAnn(self):
        global CurrentAnnos
        CurrentAnnos.savejson() 

    def nextImage(self, direction):
        global CurrentAnnos
       # CurrentAnnos.savejson()
        self.currentID += direction
        self.currentID = min(max(self.currentID, 0), len(self.imagelist)-1)
        self.currentPath = '%s/%s'%(ROOT_DIR, self.imagelist[self.currentID])
        self.qlabel.loadimg(self.currentPath)
		
        self.buttonlist[CurrentAnnos.cur_partID].setChecked(True)
        for bt in self.buttonlist:
            bt.setStyleSheet("background-color: None")
        self.buttonlist[CurrentAnnos.cur_partID].setStyleSheet("background-color: red")
        CurrentAnnos.print('nextImage')

    def nextItem(self):
        global CurrentAnnos
        CurrentAnnos.newItem()
        self.buttonlist[CurrentAnnos.cur_partID].setChecked(True)
        for bt in self.buttonlist:
            bt.setStyleSheet("background-color: None")
        self.buttonlist[CurrentAnnos.cur_partID].setStyleSheet("background-color: red")
        CurrentAnnos.print('nextItem')

    def nextPart(self):
        global CurrentAnnos
        CurrentAnnos.cur_partID += 1
        CurrentAnnos.cur_partID = CurrentAnnos.cur_partID % 12
        CurrentAnnos.cur_vis = True
        self.buttonlist[CurrentAnnos.cur_partID].setChecked(True)
        for bt in self.buttonlist:
            bt.setStyleSheet("background-color: None")
        self.buttonlist[CurrentAnnos.cur_partID].setStyleSheet("background-color: red")
        CurrentAnnos.print('nextPart')

    def changePart(self, id):
        global CurrentAnnos
        CurrentAnnos.cur_partID = id
        CurrentAnnos.cur_vis = True
        self.buttonlist[CurrentAnnos.cur_partID].setChecked(True)
        for bt in self.buttonlist:
            bt.setStyleSheet("background-color: None")
        self.buttonlist[CurrentAnnos.cur_partID].setStyleSheet("background-color: red")
        CurrentAnnos.print('changePart')

    def changeVisState(self):
        global CurrentAnnos
        CurrentAnnos.cur_vis = bool((CurrentAnnos.cur_vis + 1) % 2)
        CurrentAnnos.print('changeVisState')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ControlWindow()
	#window.showMaximized()
    window.show()
    sys.exit(app.exec_())
