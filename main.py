# pip install PySDL3 PyGLM Pillow PyOpenGL numpy

import ctypes
import os

import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import *

os.environ["SDL_MAIN_USE_CALLBACKS"] = "1"
os.environ["SDL_RENDER_DRIVER"] = "opengl"

import sdl3

from font import Font, Language
from text import Text
from texture_loader import loadTexture

glContext = None
window = None

mixedText = None
mixedText2 = None

# Create an orthographic projection matrix and a view matrix
projMatrix = glm.ortho(-50.0, 50.0, -50.0, 50.0, 10.0, -10.0) # not y-flipped
# projMatrix = glm.ortho(-50.0, 50.0, 50.0, -50.0, 10.0, -10.0) # y-flipped
viewMatrix = glm.lookAt(
    glm.vec3(0, 0, 10), # Camera position
    glm.vec3(0, 0, 0), # Target position
    glm.vec3(0, 1, 0)) # Camera up vector
# Combine them to one projView matrix
projViewMatrix = projMatrix * viewMatrix

@sdl3.SDL_AppInit_func
def SDL_AppInit(appState, argc, argv):
    global glContext
    global window
    global fontProgram
    global mixedText
    global mixedText2

    if not sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO):
        sdl3.SDL_Log("Couldn't initialize SDL: %s".encode() % sdl3.SDL_GetError())
        return sdl3.SDL_APP_FAILURE

    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_MULTISAMPLEBUFFERS, 1) # Enable MULTISAMPLE
    sdl3.SDL_GL_SetAttribute(sdl3.SDL_GL_MULTISAMPLESAMPLES, 2) # Can be 2, 4, 8 or 16

    title = "PySDL3 PyGLM Pillow OpenGL Python".encode()
    canvasWidth = 380
    canvasHeight = 380
    window = sdl3.SDL_CreateWindow(title, canvasWidth, canvasHeight, sdl3.SDL_WINDOW_OPENGL)
    if not window:
        sdl3.SDL_Log("Couldn't create a window: %s".encode() % sdl3.SDL_GetError())
        return sdl3.SDL_APP_FAILURE

    # Create an OpenGL context
    glContext = sdl3.SDL_GL_CreateContext(window)
    if not glContext:
        sdl3.SDL_Log("Couldn't create a glContext: %s".encode() % sdl3.SDL_GetError())
        return sdl3.SDL_APP_FAILURE

    sdl3.SDL_GL_SetSwapInterval(1) # Turn on vertical sync

    glViewport(0, 0, canvasWidth, canvasHeight)
    glEnable(GL_DEPTH_TEST)

    glClearColor(0.75, 0.9, 0.7, 1)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vertexShaderSource = None
    fragmentShaderSource = None
    with open("./assets/shaders/font.vert") as file:
        vertexShaderSource = file.read()
    with open("./assets/shaders/font.frag") as file:
        fragmentShaderSource = file.read()

    fontProgram = compileProgram(
       compileShader(vertexShaderSource, GL_VERTEX_SHADER),
       compileShader(fragmentShaderSource, GL_FRAGMENT_SHADER))
    glUseProgram(fontProgram)

    font = Font(fontProgram, "./assets/fonts/microsoft-yahei/microsoft-yahei.fnt",
        "./assets/fonts/microsoft-yahei/microsoft-yahei.png", False)

    position = glm.vec3(-45, 30, 0)
    size = 250
    color = glm.vec3(0.2, 0.7, 0.5)
    mixedText = Text(font, "Hello! Привет!", position, size, color)

    position = glm.vec3(-45, 0, 0)
    size = 250
    color = glm.vec3(0.2, 0.7, 0.5)
    mixedText2 = Text(font, "你好! Nǐ hǎo!", position, size, color)

    return sdl3.SDL_APP_CONTINUE

@sdl3.SDL_AppEvent_func
def SDL_AppEvent(appState, event):
    if sdl3.SDL_DEREFERENCE(event).type == sdl3.SDL_EVENT_QUIT:
        return sdl3.SDL_APP_SUCCESS
    
    return sdl3.SDL_APP_CONTINUE

@sdl3.SDL_AppIterate_func
def SDL_AppIterate(appState):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    mixedText.draw(projViewMatrix)
    mixedText2.draw(projViewMatrix)

    sdl3.SDL_GL_SwapWindow(window)
    return sdl3.SDL_APP_CONTINUE

@sdl3.SDL_AppQuit_func
def SDL_AppQuit(appState, result):
    global glContext
    global fontProgram
    glDeleteProgram(fontProgram)
    sdl3.SDL_GL_DestroyContext(glContext)
    # SDL will clean up the window for us
