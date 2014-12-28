from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import shaders

import sys
from objloader import *

SHADER_NAME = 'raycaster'
WINDOW_NAME = 'RayCaster'


class Application:
    def __init__(self):
        self.geometryRotation = [0.0, 0.0, 0.0]
        self.timer = 0
        self.fov = -2.0
        self.old = [0.0, 0.0, 0.0]
        self.shader = None
        self.origin = [0.0, 0.0, -1.0]

    @staticmethod
    def read_shader_from_file(filename):
        file_handle = open(filename, 'r')
        file_content = file_handle.read()
        file_handle.close()
        return file_content

    def mouse(self, button, status, x, y):
        self.old[0] = x
        self.old[1] = y

    def motion(self, x, y):
        #self.fov += (self.old[1] - y) / 500.0
        self.geometryRotation[1] -= (self.old[0] - x) / 1000.0
        self.geometryRotation[0] -= (self.old[1] - y) / 1000.0
        self.old[0] = x
        self.old[1] = y

    def keyboard(self, key, x, y):
        print key + " pressed"
        if key == 'q':
            sys.exit()
        if key == 'r':
            self.compile_shaders()

    def compile_shaders(self):
        print "Initializing shaders"
        vertex_shader = shaders.compileShader(
            self.read_shader_from_file(
                'shaders/' + SHADER_NAME + '.vert'), GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(
            self.read_shader_from_file(
                'shaders/' + SHADER_NAME + '.frag'), GL_FRAGMENT_SHADER)
        self.shader = shaders.compileProgram(vertex_shader, fragment_shader)
        glUseProgram(self.shader)

    def run(self):
        # self.shader = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)
        width = 512
        height = 512
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(width, height)
        glutCreateWindow(WINDOW_NAME)

        glClearColor(0.2, 0.2, 0.2, 1.0)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        glutIdleFunc(self.display)
        glutDisplayFunc(self.display)
        glutMouseFunc(self.mouse)
        glutMotionFunc(self.motion)
        glutKeyboardFunc(self.keyboard)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)
        glPushMatrix()

        self.compile_shaders()

        print "Entering main loop..."
        glutMainLoop()

    def display(self):

        self.timer += 0.01
        loc = glGetUniformLocation(self.shader, 'u_timer')
        glUniform1f(loc, self.timer)
        loc = glGetUniformLocation(self.shader, 'u_rotation_x')
        glUniform1f(loc, self.geometryRotation[0])
        loc = glGetUniformLocation(self.shader, 'u_rotation_y')
        glUniform1f(loc, self.geometryRotation[1])
        loc = glGetUniformLocation(self.shader, 'u_rotation_z')
        glUniform1f(loc, self.geometryRotation[2])

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        color = [1.0, 1.0, 1.0, 1.0]
        glMaterialfv(GL_FRONT, GL_DIFFUSE, color)

        # Draw scene
        glPushMatrix()
        size = 1
        depth = 0.0
        glBegin(GL_QUADS)
        glVertex3f(-size, -size, depth)
        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(size, -size, depth)
        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(size, size, depth)
        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(-size, size, depth)
        glNormal3f(0.0, 0.0, -1.0)
        glEnd()

        glPopMatrix()
        glutSwapBuffers()

if __name__ == '__main__':
    app = Application()
    app.run()
