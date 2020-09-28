import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from math import sqrt

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(800, 900)
        self.pen = QPen(Qt.black, 2, Qt.SolidLine)
        self.penred = QPen(Qt.red, 2, Qt.SolidLine)
        self.penblue = QPen(Qt.blue, 5, Qt.SolidLine)
        self.allmainxy = []
        self.allmainxyjud = []
        self.allsecxy = []
        self.allsecxyjud = []
        self.mainxylen = 0
        self.secxylen = 0
        self.maingraphcnt = 0
        self.secgraphcnt = 0
        self.nowgraph = 1
        self.mainlast = 0
        self.seclast = 0

        # points of inner and outer
        self.mainouterxy = []
        self.maininnerxy = []
        # inner graph cnts
        self.maininnercnts = 0

        self.secouterxy = []
        self.secinnerxy = []
        self.secinnercnts = 0

        self.results = []

        self.mainmodebutton = QPushButton(self)
        self.mainmodebutton.setText("主多边形")
        self.secmodebutton = QPushButton(self)
        self.secmodebutton.setText("次多边形")
        self.printbutton = QPushButton(self)
        self.printbutton.setText("计算结果")

        self.mainmodebutton.clicked.connect(self.switchmainmode)
        self.secmodebutton.clicked.connect(self.switchsecmode)
        self.printbutton.clicked.connect(self.calc)

        self.mainmodebutton.move(30, 830)
        self.secmodebutton.move(330, 830)
        self.printbutton.move(630, 830)

    # 辅助函数

    def isClockWise(self, points):
        lenth = len(points)
        sum = 0
        for i in range(0, lenth-1):
            sum += (points[i+1][0] + points[i][0]) * (points[i+1][1] - points[i][1])
        return sum >= 0

    def cross_point(self, a, b, c, d):
        k1 = (b[1] - a[1]) * 1.0 / (b[0] - a[0])
        b1 = a[1] * 1.0 - a[0] * k1 * 1.0
        if d[0] - c[0] == 0:
            k2 = None
            b2 = 0
        else:
            k2 = (d[1] - c[1]) * 1.0 / (d[0] - c[0])
            b2 = c[1] * 1.0 - c[0] * k2 * 1.0

        if k2 is None:
            x = c[0]
        else:
            x = (b2 - b1) * 1.0 / (k1 - k2)
        y = k1 * x * 1.0 + b1 * 1.0
        return [x,y]

    def dis(self, a, b):
        return sqrt(1.0 * (a[0] - b[0]) * (a[0] - b[0]) + 1.0 * (a[1] - b[1]) * (a[1] - b[1]))

    def onSegment(self, a, b, c):
        if(min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and
           min(a[1], b[1]) <= c[1] <= max(a[1], b[1])):
            return True
        return False


    def addPoint(self, points, pta, ptb, ip):
        st = points.index(pta)
        ed = points.index(ptb)

        it = st
        dist = self.dis(ip, points[it])
        while it != ed and it != len(points):
            if self.dis(points[it], points[st]) >= dist:
                break
            it += 1
        points.insert(it, ip)

    def isEntering(self, pta, ptb, ptc, ptd):
        x1 = ptb[0] - pta[0]
        y1 = ptb[1] - pta[1]
        x2 = ptd[0] - ptc[0]
        y2 = ptd[1] - ptc[1]
        jud = x1 * y2 - x2 * y1
        return jud > 0

    def getOuterPointsAndInerPoints(self):
        # 主多边形外环点集
        for i in range(0, self.allmainxyjud[0] + 1):
            self.mainouterxy.append(self.allmainxy[i])
        # 有内环情况
        if self.maingraphcnt > 1:
            # 添加主多边形所有内环点集
            for i in range(1, self.maingraphcnt):
                la = self.allmainxyjud[i - 1] + 1
                points = []
                for j in range(la, self.allmainxyjud[i] + 1):
                    points.append(self.allmainxy[j])
                self.maininnerxy.append(points)
                self.maininnercnts += 1
        # 次多边形外环点集
        for i in range(0, self.allsecxy[0] + 1):
            self.secouterxy.append(self.allsecxy[i])
        # 有内环情况
        if self.secgraphcnt > 1:
            for i in range(1, self.secgraphcnt):
                la = self.allsecxyjud[i - 1] + 1
                points = []
                for j in range(la, self.allsecxyjud[i] + 1):
                    points.append(self.allsecxy[j])
                self.secinnerxy.append(points)
                self.secinnerxycnts += 1

    def dowalk(self, pointsa, pointsb, enterpoints, exitpoints, results, point, type = 'inner'):
        # inner 遍历主多边形遇到出点结束
        if type == 'inner':
            pointindex = -1
            if point in pointsa:
                pointindex = pointsa.index(point)
            if pointindex == -1:
                return [-1, -1]
            while pointindex < len(pointsa):
                nowpoint = pointsa[pointindex]
                if nowpoint in exitpoints:
                    return nowpoint
                results.append(nowpoint)
                pointindex += 1
                if pointindex == len(pointsa):
                    pointindex = 0
        # outer 遍历副多边形遇到入点结束
        elif type == 'outer':
            pointindex = -1
            if point in pointsb:
                pointindex = pointsb.index(point)
            if pointindex == -1:
                return [-1, -1]
            while pointindex < len(pointsb):
                nowpoint = pointsb[pointindex]
                if nowpoint in enterpoints:
                   return nowpoint
                results.append(nowpoint)
                pointindex += 1
                if pointindex == len(pointsb):
                    pointindex = 0
        return [-1, -1]

    def WA_algorithm(self, pointsa, pointsb, type = 'inner'):
        if self.isClockWise(pointsa) == 0:
            pointsa.reverse()
        if self.isClockWise(pointsb) == 0:
            pointsb.reverse()

        linesa, linesb = [], []
        for i in range(0, len(pointsa) - 1):
            linesa.append([pointsa[i], pointsa[i+1]])
        linesa.append([pointsa[-1], pointsa[0]])
        for i in range(0, len(pointsb) - 1):
            linesb.append([pointsb[i], pointsb[i+1]])
        linesb.append([pointsb[-1], pointsb[0]])

        enterpoints = []
        exitpoints = []
        for linea in linesa:
            for lineb in linesb:
                crosspoint = self.cross_point(linea[0], linea[1], lineb[0], lineb[1])
                if self.onSegment(linea[0], linea[1], crosspoint) and self.onSegment(lineb[0], lineb[1], crosspoint):
                    if self.isEntering(linea[0], linea[1], lineb[0], lineb[1]):
                        exitpoints.append(crosspoint)
                    else:
                        enterpoints.append(crosspoint)
                    self.addPoint(pointsa, linea[0], linea[1], crosspoint)
                    self.addPoint(pointsb, lineb[0], lineb[1], crosspoint)
        results = []
        if type == 'inner':
            for enterpoint in enterpoints:
                if results:
                    jud = 0
                    for points in results:
                        if enterpoint in points:
                            jud = 1
                            break
                    if jud:
                        continue
                jud = 0
                st = enterpoint
                ne = st
                nowresults = []
                while jud == 0 or ne != st:
                    if jud == 0:
                        jud = 1
                    if ne == [-1, -1]:
                        break
                    ne = self.dowalk(pointsa, pointsb, enterpoints, exitpoints, nowresults, ne, 'inner')
                    ne = self.dowalk(pointsa, pointsb, enterpoints, exitpoints, nowresults, ne, 'outer')
                results.append(nowresults)
        elif type == 'outer':
            # TODO
            results = []
        return results








    def paintEvent(self, QPaintEvent):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setPen(self.penblue)
        self.painter.drawLine(0, 0, 0, 800)
        self.painter.drawLine(0, 0, 800, 0)
        self.painter.drawLine(800, 800, 800, 0)
        self.painter.drawLine(800, 800, 0, 800)
        self.painter.setPen(self.pen)
        if len(self.allmainxy):
            for ele in self.allmainxy:
                self.painter.drawPoint(int(ele[0]), int(ele[1]))
        if len(self.allmainxy) >= 2:
            lenth = len(self.allmainxy)
            for i in range(0, lenth):
                if len(self.allmainxyjud) > 0:
                    if i in self.allmainxyjud:
                        index = self.allmainxyjud.index(i)
                        if index == 0:
                            self.painter.drawLine(int(self.allmainxy[i][0]), int(self.allmainxy[i][1]),
                                                  int(self.allmainxy[0][0]), int(self.allmainxy[0][1]))
                        else:
                            self.painter.drawLine(int(self.allmainxy[i][0]), int(self.allmainxy[i][1]),
                                                  int(self.allmainxy[self.allmainxyjud[index-1]+1][0]),
                                                  int(self.allmainxy[self.allmainxyjud[index-1]+1][1]))
                    else:
                        if i == lenth - 1:
                            continue
                        self.painter.drawLine(int(self.allmainxy[i][0]), int(self.allmainxy[i][1]),
                                              int(self.allmainxy[i + 1][0]), int(self.allmainxy[i + 1][1]))
                else:
                    if i == lenth - 1:
                        continue
                    self.painter.drawLine(int(self.allmainxy[i][0]), int(self.allmainxy[i][1]),
                                          int(self.allmainxy[i + 1][0]), int(self.allmainxy[i + 1][1]))
        self.painter.end()

        self.painter.begin(self)
        self.painter.setPen(self.penred)
        if len(self.allsecxy):
            for ele in self.allsecxy:
                self.painter.drawPoint(int(ele[0]), int(ele[1]))
        if len(self.allsecxy) >= 2:
            lenth = len(self.allsecxy)
            for i in range(0, lenth):
                if len(self.allsecxyjud) > 0:
                    if i in self.allsecxyjud:
                        index = self.allsecxyjud.index(i)
                        if index == 0:
                            self.painter.drawLine(int(self.allsecxy[i][0]), int(self.allsecxy[i][1]),
                                                  int(self.allsecxy[0][0]), int(self.allsecxy[0][1]))
                        else:
                            self.painter.drawLine(int(self.allsecxy[i][0]), int(self.allsecxy[i][1]),
                                                  int(self.allsecxy[self.allsecxyjud[index - 1] + 1][0]),
                                                  int(self.allsecxy[self.allsecxyjud[index - 1] + 1][1]))
                    else:
                        if i == lenth - 1:
                            continue
                        self.painter.drawLine(int(self.allsecxy[i][0]), int(self.allsecxy[i][1]),
                                              int(self.allsecxy[i + 1][0]), int(self.allsecxy[i + 1][1]))
                else:
                    if i == lenth - 1:
                        continue
                    self.painter.drawLine(int(self.allsecxy[i][0]), int(self.allsecxy[i][1]),
                                          int(self.allsecxy[i + 1][0]), int(self.allsecxy[i + 1][1]))
        self.painter.end()

        self.painter.begin(self)
        self.painter.setPen(self.penblue)
        if self.results:
            lenth = len(self.results[0])
            for i in range(0, lenth - 1):
                pta = self.results[0][i]
                ptb = self.results[0][i+1]
                self.painter.drawLine(int(pta[0]), int(pta[1]),
                                      int(ptb[0]), int(ptb[1]))
            pta = self.results[0][-1]
            ptb = self.results[0][0]
            self.painter.drawLine(int(pta[0]), int(pta[1]),
                                  int(ptb[0]), int(ptb[1]))
        self.painter.end()

    def mousePressEvent(self, QMouseEvent):
        if self.nowgraph == 1:
            if QMouseEvent.buttons() == QtCore.Qt.LeftButton:
                self.allmainxy.append([QMouseEvent.pos().x(), QMouseEvent.pos().y()])
                self.mainxylen += 1
            elif QMouseEvent.buttons() == QtCore.Qt.RightButton:
                if self.mainxylen < 3:
                    QMessageBox.critical(self, "错误", "请至少输入三个点", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                else:
                    self.allmainxyjud.append(len(self.allmainxy) - 1)
                    self.mainxylen = 0
                    self.maingraphcnt += 1


        elif self.nowgraph == 2:
            if QMouseEvent.buttons() == QtCore.Qt.LeftButton:
                self.allsecxy.append([QMouseEvent.pos().x(), QMouseEvent.pos().y()])
                self.secxylen += 1
            elif QMouseEvent.buttons() == QtCore.Qt.RightButton:
                if self.secxylen < 3:
                    QMessageBox.critical(self, "错误", "请至少输入三个点", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                else:
                    self.allsecxyjud.append(len(self.allsecxy) - 1)
                    self.secxylen = 0
                    self.secgraphcnt += 1

        self.update()

    @pyqtSlot()
    def switchmainmode(self):
        self.nowgraph = 1

    @pyqtSlot()
    def switchsecmode(self):
        self.nowgraph = 2

    @pyqtSlot()
    def calc(self):
        allmainxy = self.allmainxy.copy()
        allsecxy = self.allsecxy.copy()
        self.results = self.WA_algorithm(allmainxy, allsecxy, 'inner')
        self.update()



if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
