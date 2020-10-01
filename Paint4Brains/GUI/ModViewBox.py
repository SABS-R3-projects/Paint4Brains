"""Viewing Box Module

This file contains a class required for creating a viewing box enabling the user to view the data.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.GUI.ModViewBox import ModViewBox

        view = ModViewBox()

"""

import numpy as np
from pyqtgraph.Qt import QtCore
from pyqtgraph.Point import Point
from pyqtgraph import ViewBox
from pyqtgraph import functions as fn


class ModViewBox(ViewBox):
    """ModViewBox class for Paint4Brains.

    This class is required for creating a viewing box enabling the user to view the data.

    Args:
        parent (class): Base or parent class
    """

    def __init__(self, parent=None):
        super(ModViewBox, self).__init__(parent=parent)
        # By default not in drawing mode
        self.drawing = False
        self.state['mouseMode'] = 3
        self.setAspectLocked(True)

    def mouseDragEvent(self, ev, axis=None):
        """Mouse drag tracker

        This function keep track of the mouse position and overwrites it to take the draw mode into account.

        Args:
            ev: signal emitted when user releases a mouse button.
        """
        # Overwritting mouseDragEvent to take drawmode into account.
        ev.accept()

        pos = ev.pos()
        lastPos = ev.lastPos()
        dif = pos - lastPos
        dif = dif * -1

        # Ignore axes if mouse is disabled
        mouseEnabled = np.array(self.state['mouseEnabled'], dtype=np.float)
        mask = mouseEnabled.copy()
        if axis is not None:
            mask[1 - axis] = 0.0

        # If in drawing mode (editted part):
        if self.drawing:
            self.state['mouseMode'] = self.RectMode
            # If right button is selected draw zoom in boxes:
            if ev.button() & QtCore.Qt.RightButton:
                if ev.isFinish():
                    self.rbScaleBox.hide()
                    ax = QtCore.QRectF(
                        Point(ev.buttonDownPos(ev.button())), Point(pos))
                    ax = self.childGroup.mapRectFromParent(ax)
                    self.showAxRect(ax)
                    self.axHistoryPointer += 1
                    self.axHistory = self.axHistory[:self.axHistoryPointer] + [ax]
                else:
                    self.updateScaleBox(ev.buttonDownPos(), ev.pos())
            # If Left Button is selected drag image (This will be overwritten in the image by the drawing kernel)
            elif ev.button() & QtCore.Qt.LeftButton:
                tr = dif * mask
                tr = self.mapToView(tr) - self.mapToView(Point(0, 0))
                x = tr.x() if mask[0] == 1 else None
                y = tr.y() if mask[1] == 1 else None

                self._resetTarget()
                if x is not None or y is not None:
                    self.translateBy(x=x, y=y)
                self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
            # If Middle Button (wheel) zoom in or out.
            elif ev.button() & QtCore.Qt.MidButton:
                if self.state['aspectLocked'] is not False:
                    mask[0] = 0

                dif = ev.screenPos() - ev.lastScreenPos()
                dif = np.array([dif.x(), dif.y()])
                dif[0] *= -1
                s = ((mask * 0.02) + 1) ** dif

                tr = self.childGroup.transform()
                tr = fn.invertQTransform(tr)

                x = s[0] if mouseEnabled[0] == 1 else None
                y = s[1] if mouseEnabled[1] == 1 else None

                center = Point(tr.map(ev.buttonDownPos(QtCore.Qt.LeftButton)))
                self._resetTarget()
                self.scaleBy(x=x, y=y, center=center)
                self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
        # If not in drawing mode: (original functionality)
        else:
            # Scale or translate based on mouse button
            if ev.button() & (QtCore.Qt.LeftButton | QtCore.Qt.MidButton):
                if self.state['mouseMode'] == ViewBox.RectMode:
                    if ev.isFinish():  # This is the final move in the drag; change the view scale now
                        # print "finish"
                        self.rbScaleBox.hide()
                        ax = QtCore.QRectF(
                            Point(ev.buttonDownPos(ev.button())), Point(pos))
                        ax = self.childGroup.mapRectFromParent(ax)
                        self.showAxRect(ax)
                        self.axHistoryPointer += 1
                        self.axHistory = self.axHistory[:self.axHistoryPointer] + [
                            ax]
                    else:
                        # update shape of scale box
                        self.updateScaleBox(ev.buttonDownPos(), ev.pos())
                else:
                    tr = dif * mask
                    tr = self.mapToView(tr) - self.mapToView(Point(0, 0))
                    x = tr.x() if mask[0] == 1 else None
                    y = tr.y() if mask[1] == 1 else None

                    self._resetTarget()
                    if x is not None or y is not None:
                        self.translateBy(x=x, y=y)
                    self.sigRangeChangedManually.emit(
                        self.state['mouseEnabled'])
            elif ev.button() & QtCore.Qt.RightButton:
                # print "vb.rightDrag"
                if self.state['aspectLocked'] is not False:
                    mask[0] = 0

                dif = ev.screenPos() - ev.lastScreenPos()
                dif = np.array([dif.x(), dif.y()])
                dif[0] *= -1
                s = ((mask * 0.02) + 1) ** dif

                tr = self.childGroup.transform()
                tr = fn.invertQTransform(tr)

                x = s[0] if mouseEnabled[0] == 1 else None
                y = s[1] if mouseEnabled[1] == 1 else None

                center = Point(tr.map(ev.buttonDownPos(QtCore.Qt.RightButton)))
                self._resetTarget()
                self.scaleBy(x=x, y=y, center=center)
                self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
