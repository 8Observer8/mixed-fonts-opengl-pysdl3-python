
import glm
from numpy import equal
from OpenGL.GL import *

from font import CharData, Font


class Text:

    def __init__(self, font, text, position = glm.vec3(0, 0, 0), size=200,
        color = glm.vec3(0.57, 0.83, 0.72), outlineColor = glm.vec3(0.1, 0.1, 0.1)):

        self.font = font
        self.text = text
        self.position = position

        self.setSize(size)
        self.setColor(color)
        self.setOutlineColor(outlineColor)

        self.x = 0
        self.y: float
        self.w: float
        self.h: float
        self.cd: CharData = None

    def getWidth(self):
        w = 0.0
        for i in range(len(self.text)):
            self.cd: CharData = self.font.charMap[self.text[i]]
            w = w + (self.cd.xAdvance * self.size) * 0.85
        return w

    def draw(self, projViewMatrix):
        self.font.bind()
        self.setColor(self.color)
        self.setOutlineColor(self.outlineColor)

        self.x = 0
        self.y = 0
        for i in range(len(self.text)):
            self.cd: CharData = self.font.charMap[self.text[i]]
            self.x = self.x + self.cd.xOffset * self.size
            self.y = self.cd.yOffset * self.size
            self.w = self.cd.width * self.size
            self.h = self.cd.height * self.size

            y = 0
            if self.font.yFlipped:
                y = self.position.y + self.y
            else:
                y = self.position.y - self.y
            modelMatrix = glm.translate(glm.mat4(1), glm.vec3(self.position.x + self.x,
                y, self.position.z))
            modelMatrix = glm.scale(modelMatrix, glm.vec3(self.w, self.h, 1))
            mvpMatrix = projViewMatrix * modelMatrix
            self.font.setMvpMatrix(mvpMatrix)

            glDrawArrays(GL_TRIANGLE_STRIP, self.font.charIndices[self.text[i]], 4)
            self.x = self.x + (self.cd.xAdvance * self.size) * 0.85

    def text(self):
        return self.text

    def setText(self, text):
        self.text = text

    def position(self):
        return self.position

    def setPosition(self, position):
        self.position = position

    def setSize(self, size):
        self.size = size / 1000

    def color(self):
        return self.color

    def setColor(self, color):
        self.color = color
        self.font.setColor(color)

    def outlineColor(self):
        return self.outlineColor

    def setOutlineColor(self, outlineColor):
        self.outlineColor = outlineColor
        self.font.setOutlineColor(outlineColor)
