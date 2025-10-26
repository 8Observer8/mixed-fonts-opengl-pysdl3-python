import re
from enum import Enum

import glm
import numpy as np
from OpenGL.GL import *

from texture_loader import loadTexture


class CharData:
    def __init__(self):
        self.charId: int
        self.xAdvance: int
        self.xOffset: int
        self.yOffset: int
        self.height: int
        self.width: int
        self.x: int
        self.y: int

class Language(Enum):
    English = 0,
    Russian = 1

class Font:
    def __init__(self, program, fontContentPath, fontTexturePath, yFlipped):

        self.program = program
        self.yFlipped = yFlipped

        glUseProgram(self.program)
        self.aPositionLocation = glGetAttribLocation(self.program, "aPosition")
        self.aTexCoordLocation = glGetAttribLocation(self.program, "aTexCoord")
        self.uMvpMatrixLocation = glGetUniformLocation(self.program, "uMvpMatrix")
        self.uColorLocation = glGetUniformLocation(self.program, "uColor")
        self.uOutlineColorLocation = glGetUniformLocation(self.program, "uOutlineColor")
        uSamplerLocation = glGetUniformLocation(self.program, "uSampler")
        glUniform1i(uSamplerLocation, 0)

        self.charMap = self.parse(fontContentPath)

        vertPositions = []
        if self.yFlipped:
            for i in range(len(self.charMap)):
                vertPositions.extend([0.0, 0.0, 0.0])
                vertPositions.extend([0.0, 1.0, 0.0])
                vertPositions.extend([1.0, 0.0, 0.0])
                vertPositions.extend([1.0, 1.0, 0.0])
        else:
            for i in range(len(self.charMap)):
                vertPositions.extend([0.0, 0.0, 0.0])
                vertPositions.extend([0.0, -1.0, 0.0])
                vertPositions.extend([1.0, 0.0, 0.0])
                vertPositions.extend([1.0, -1.0, 0.0])
        vertPositions = np.array(vertPositions, dtype=np.float32)
        self.vertPosBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertPosBuffer)
        glBufferData(GL_ARRAY_BUFFER, len(vertPositions) * 4,
            vertPositions, GL_STATIC_DRAW)

        self.charIndices = {}
        drawIndex = 0
        texCoords = []
        for ch in self.charMap:
            self.charIndices[ch] = drawIndex
            drawIndex += 4
            cd = self.charMap[ch]
            x = cd.x / 512.0
            y = cd.y / 512.0
            w = cd.width / 512
            h = cd.height / 512
            texCoords.extend([x, y])
            texCoords.extend([x, y + h])
            texCoords.extend([x + w, y])
            texCoords.extend([x + w, y + h])
        texCoords = np.array(texCoords, dtype=np.float32)
        self.texCoordBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.texCoordBuffer)
        glBufferData(GL_ARRAY_BUFFER, len(texCoords) * 4,
            texCoords, GL_STATIC_DRAW)

        self.texture = loadTexture(fontTexturePath)

    def bind(self):
        glUseProgram(self.program)

        glBindBuffer(GL_ARRAY_BUFFER, self.vertPosBuffer)
        glVertexAttribPointer(self.aPositionLocation, 3, GL_FLOAT,
            GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(self.aPositionLocation)

        glBindBuffer(GL_ARRAY_BUFFER, self.texCoordBuffer)
        glVertexAttribPointer(self.aTexCoordLocation, 2, GL_FLOAT,
            GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(self.aTexCoordLocation)

        glBindTexture(GL_TEXTURE_2D, self.texture)

    def setColor(self, color):
        glUseProgram(self.program)
        glUniform3fv(self.uColorLocation, 1, glm.value_ptr(color))

    def setOutlineColor(self, outlineColor):
        glUseProgram(self.program)
        glUniform3fv(self.uOutlineColorLocation, 1, glm.value_ptr(outlineColor))

    def setMvpMatrix(self, mvpMatrix):
        glUseProgram(self.program)
        glUniformMatrix4fv(self.uMvpMatrixLocation, 1, GL_FALSE,
            glm.value_ptr(mvpMatrix))

    def yFlipped(self):
        return self.yFlipped

    def getValue(self, s):
        i = s.index("=")
        value = int(s[i+1:])
        return value

    def parse(self, path):
        charMap = {}
        with open(path, "r", encoding="utf-8") as file:
            lines = file.read().splitlines()

        for line in lines:
            if line.startswith("char "):
                charData = CharData()
                # Use regex to extract key=value
                kv_pairs = re.findall(r"(\w+)=(\"?.+?\"?)\s", line + " ")
                kv_dict = {k: v.strip('"') for k, v in kv_pairs}

                charData.charId = int(kv_dict.get("id", 0))
                charData.x = int(kv_dict.get("x", 0))
                charData.y = int(kv_dict.get("y", 0))
                charData.width = int(kv_dict.get("width", 0))
                charData.height = int(kv_dict.get("height", 0))
                charData.xOffset = int(kv_dict.get("xoffset", 0))
                charData.yOffset = int(kv_dict.get("yoffset", 0))
                charData.xAdvance = int(kv_dict.get("xadvance", 0))

                # skip control characters
                if charData.charId in (0, 10, 127):
                    continue

                try:
                    charMap[chr(charData.charId)] = charData
                except ValueError:
                    continue

        return charMap