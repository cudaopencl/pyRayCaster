import OpenGL
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import shaders

import sys
import math
import numpy as np
# import Image
from collections import defaultdict

# Blue Brain Project
# import bbp

from objloader import *

SHADER_NAME = 'raytracing'
WINDOW_NAME = 'PYNeuron'
#JPG_FILE = Image.open("picture.jpg")

default_vertex_shader_code = """
    varying vec3 N;
    varying vec3 v;
    void main(void)
    {
        v = vec3(gl_ModelViewMatrix * gl_Vertex);
        N = normalize(gl_NormalMatrix * gl_Normal);
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    }
    """

default_fragment_shader_code = """
    varying vec3 N;
    varying vec3 v;
    void main(void)
    {
        vec3 L = normalize(gl_LightSource[0].position.xyz - v);
        vec4 Idiff = gl_FrontLightProduct[0].diffuse * max(dot(N,L), 0.0);
        Idiff = clamp(Idiff, 0.0, 1.0);
        gl_FragColor = Idiff;
    }
    """

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
class Application:
    def __init__(self):
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.tex_boxes = []
        self.geometryRotation = [0.0, 0.0, 0.0]
        self.time = 0.0
        self.timer = 0
        self.fov = -2.0
        self.old = [0.0, 0.0, 0.0]
        self.shader = None
        self.origin = [0.0, 0.0, -1.0]
        self.AAValues = [[-0.03, 0.05], [-0.05, 0.03], [0.03, 0.05], [0.05, 0.03]]
        self.nbBoxes = 0
        self.boxes_aabb = dict()

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
        self.geometryRotation[1] -= (self.old[0] - x) / 100.0
        self.geometryRotation[0] -= (self.old[1] - y) / 100.0
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
        loc = glGetUniformLocation(self.shader, 'u_nbVertices')
        glUniform1i(loc, len(self.vertices))
        loc = glGetUniformLocation(self.shader, 'u_nbBoxes')
        glUniform1i(loc, self.nbBoxes)

    def rotate_geometry(self):
        #print 'Rotating geometry and transfering textures'
        cos_angles = [math.cos(self.geometryRotation[0]), math.cos(self.geometryRotation[1]), 0]
        sin_angles = [math.sin(self.geometryRotation[0]), math.sin(self.geometryRotation[1]), 0]

        # Y Axis
        for vertex in self.vertices:
            z = vertex[2] * cos_angles[1] - vertex[0] * sin_angles[1]
            x = vertex[2] * sin_angles[1] + vertex[0] * cos_angles[1]
            vertex[2] = z
            vertex[0] = x
        for vertex in self.normals:
            z = vertex[2] * cos_angles[1] - vertex[0] * sin_angles[1]
            x = vertex[2] * sin_angles[1] + vertex[0] * cos_angles[1]
            vertex[2] = z
            vertex[0] = x

        # X Axis
        for vertex in self.vertices:
            z = vertex[2] * cos_angles[0] - vertex[1] * sin_angles[0]
            y = vertex[2] * sin_angles[0] + vertex[1] * cos_angles[0]
            vertex[2] = z
            vertex[1] = y
        for vertex in self.normals:
            z = vertex[2] * cos_angles[0] - vertex[1] * sin_angles[0]
            y = vertex[2] * sin_angles[0] + vertex[1] * cos_angles[0]
            vertex[2] = z
            vertex[1] = y

        vertices_texture_id = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_1D, vertices_texture_id)
        glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA32F, len(self.faces) * 3 - 1,
                     0, GL_RGBA, GL_FLOAT, self.vertices)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        loc = glGetUniformLocation(self.shader, 'texVertices')
        glUniform1i(loc, 0)

        normal_texture_id = glGenTextures(1)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_1D, normal_texture_id)
        glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA32F, len(self.faces) * 3 - 1,
                     0, GL_RGBA, GL_FLOAT, self.normals)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        loc = glGetUniformLocation(self.shader, 'texNormals')
        glUniform1i(loc, 1)

        boxes_texture_id = glGenTextures(1)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_1D, boxes_texture_id)
        glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA32F, len(self.tex_boxes) * 2 - 1,
                     0, GL_RGBA, GL_FLOAT, self.tex_boxes)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        loc = glGetUniformLocation(self.shader, 'texBoxes')
        glUniform1i(loc, 2)

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
        self.rotate_geometry()

        print "Entering main loop..."
        glutMainLoop()

    def display(self):
        self.timer += 1
        loc = glGetUniformLocation(self.shader, 'u_time')
        glUniform1f(loc, self.geometryRotation[2])

        loc = glGetUniformLocation(self.shader, 'u_fov')
        glUniform1f(loc, self.fov)

        loc = glGetUniformLocation(self.shader, 'u_rotation_x')
        glUniform1f(loc, self.geometryRotation[0])
        loc = glGetUniformLocation(self.shader, 'u_rotation_y')
        glUniform1f(loc, self.geometryRotation[1])
        loc = glGetUniformLocation(self.shader, 'u_rotation_z')
        glUniform1f(loc, self.geometryRotation[2])

        if False:  # Antialiasing
            loc = glGetUniformLocation(self.shader, 'u_origin')
            origin = [
                self.origin[0] + self.AAValues[self.timer % 4][0],
                self.origin[1] + self.AAValues[self.timer % 4][1],
                self.origin[2]]
            glUniform3f(loc, origin[0], origin[1], origin[2])
        else:
            loc = glGetUniformLocation(self.shader, 'u_origin')
            glUniform3f(loc, self.origin[0], self.origin[1], self.origin[2])

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Lightning
        glEnable(GL_LIGHTING)
        light_position = [5.0 * math.cos(2 * self.time), 5.0, 5.0 * math.sin(2 * self.time), 1.0]
        light_color = [1.0, 1.0, 1.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_color)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glEnable(GL_LIGHT0)

        self.time += 0.01
        loc = glGetUniformLocation(self.shader, 'u_time')
        glUniform1f(loc, self.time)

        color = [1.0, 1.0, 1.0, 1.0]
        glMaterialfv(GL_FRONT, GL_DIFFUSE, color)

        if len(self.vertices) > 0:
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_NORMAL_ARRAY)
            if len(self.texcoords) > 0:
                glEnableClientState(GL_TEXTURE_COORD_ARRAY)

            glVertexPointer(3, GL_FLOAT, 0, self.vertices)
            glNormalPointer(GL_FLOAT, 0, self.normals)
            if len(self.texcoords) > 0:
                glTexCoordPointer(3, GL_FLOAT, 0, self.texcoords)

        # Draw scene
        glPushMatrix()
        #glRotatef(self.rotation, 0.2, 1.0, 0.8)
        if False & len(self.vertices) > 0:
            glDrawElements(GL_TRIANGLES,
                           len(self.faces) * 3, GL_UNSIGNED_INT, self.faces.tostring())
        else:
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

        # Set Camera
        glPopMatrix()
        if len(self.vertices) > 0:
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_NORMAL_ARRAY)
            if len(self.texcoords) > 0:
                glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        #glEnable(GL_COLOR_LOGIC_OP)
        glLogicOp(GL_XOR)
        glutSwapBuffers()

    def load_bbp_meshes(self):
        # BBP
        experiment = bbp.Experiment(bbp.test_blueconfig())
        cell_target = experiment.cell_target('Column')
        lf = bbp.Loading_Flags
        microcircuit = experiment.microcircuit()
        microcircuit.load(cell_target, lf.NEURONS | lf.MORPHOLOGIES | lf.MESHES)
        meshes = microcircuit.meshes()
        self.rotation = 0
        # Determine total array sizes
        total_vertices = 0
        total_faces = 0
        neurons = 0
        for mesh in meshes:
            total_vertices += mesh.vertex_count()
            total_faces += mesh.triangle_count()
            neurons += 1
            if neurons == 1: break
        print "Total number of vertices: " + str(total_vertices)

        self.vertices = np.zeros((total_vertices, 3), dtype=np.float32)
        self.normals = np.zeros((total_vertices, 3), dtype=np.float32)
        self.faces = np.zeros((total_faces * 2, 3), dtype=np.uint32)
        neurons = 0
        vertices = 0
        faces = 0
        for mesh in meshes:
            scale = 0.5
            print "Loading " + str(mesh.triangle_count()) + " indices"
            for i in range(0, mesh.vertex_count() - 1):
                self.vertices[vertices + i, 0] = mesh.vertices()[i].x() * scale
                self.vertices[vertices + i, 1] = mesh.vertices()[i].y() * scale
                self.vertices[vertices + i, 2] = mesh.vertices()[i].z() * scale
                self.normals[vertices + i, 0] = mesh.normals()[i].x()
                self.normals[vertices + i, 1] = mesh.normals()[i].y()
                self.normals[vertices + i, 2] = mesh.normals()[i].z()

            for i in range(0, mesh.triangle_count()):
                self.faces[faces + i, 0] = vertices + mesh.triangles()[i * 3]
                self.faces[faces + i, 1] = vertices + mesh.triangles()[i * 3 + 1]
                self.faces[faces + i, 2] = vertices + mesh.triangles()[i * 3 + 2]

            print "Loaded " + str(len(self.faces)) + " faces"

            vertices += mesh.vertex_count()
            faces += mesh.triangle_count()
            neurons += 1
            if neurons == 1:
                break

    def load_obj_file(self, filename):
        print "Loading " + filename + "..."
        obj_loader = ObjLoader(filename, False)
        print "Vertices : " + str(len(obj_loader.vertices))
        print "Normals  : " + str(len(obj_loader.normals))
        print "TexCoords: " + str(len(obj_loader.texcoords))
        print "Faces    : " + str(len(obj_loader.faces))
        self.vertices = np.zeros((len(obj_loader.faces) * 3 + 1, 4), dtype=np.float32)
        self.normals = np.zeros((len(obj_loader.faces) * 3 + 1, 4), dtype=np.float32)
        self.texcoords = np.zeros((len(obj_loader.texcoords) * 3 + 1, 4), dtype=np.float32)
        self.faces = np.zeros((len(obj_loader.faces) + 1, 4), dtype=np.uint32)
        fv = 0
        # Vertices
        scale = 0.2
        center = [0, 0, 0]
        AABB = [[100000, 100000, 100000], [-100000, -100000, -100000]]
        # Faces
        for i in range(0, len(obj_loader.faces)):
            self.faces[i, 0] = obj_loader.faces[i][0][0]
            self.faces[i, 1] = obj_loader.faces[i][0][1]
            self.faces[i, 2] = obj_loader.faces[i][0][2]
            self.faces[i, 3] = 0

            vertex_id = obj_loader.faces[i][0][0] - 1
            for j in range(0, 3):
                self.vertices[fv, j] = obj_loader.vertices[vertex_id][j] * scale
                for k in range(0, 3):
                    AABB[0][k] = min(AABB[0][k], self.vertices[fv, k])
                    AABB[1][k] = max(AABB[1][k], self.vertices[fv, k])
            self.vertices[fv, 3] = 0

            vertex_id = obj_loader.faces[i][0][1] - 1
            for j in range(0, 3):
                self.vertices[fv + 1, j] = obj_loader.vertices[vertex_id][j] * scale
                for k in range(0, 3):
                    AABB[0][k] = min(AABB[0][k], self.vertices[fv, k])
                    AABB[1][k] = max(AABB[1][k], self.vertices[fv, k])
            self.vertices[fv + 1, 3] = 0

            vertex_id = obj_loader.faces[i][0][2] - 1
            for j in range(0, 3):
                self.vertices[fv + 2, j] = obj_loader.vertices[vertex_id][j] * scale
                for k in range(0, 3):
                    AABB[0][k] = min(AABB[0][k], self.vertices[fv, k])
                    AABB[1][k] = max(AABB[1][k], self.vertices[fv, k])
            self.vertices[fv + 2, 3] = 0

            normal_id = obj_loader.faces[i][1][0] - 1
            for j in range(0, 3):
                self.normals[fv, j] = obj_loader.normals[normal_id][j]
            self.normals[fv, 3] = 0
            normal_id = obj_loader.faces[i][1][1] - 1
            for j in range(0, 3):
                self.normals[fv + 1, j] = obj_loader.normals[normal_id][j]
            self.normals[fv + 1, 3] = 0
            normal_id = obj_loader.faces[i][1][2] - 1
            for j in range(0, 3):
                self.normals[fv + 2, j] = obj_loader.normals[normal_id][j]
            self.normals[fv + 2, 3] = 0

            fv += 3

        print 'AABB = ' + str(AABB)
        for i in range(0, 3):
            center[i] = (AABB[1][i] + AABB[0][i]) / 2.0
        print 'Center = ' + str(center)

        print "Loaded " + str(len(obj_loader.faces)) + " faces"
        return AABB

    def compute_bounding_boxes(self, AABB, level, granularity):
        box_size = granularity * granularity * granularity
        print 'Box size = ' + str(box_size)
        self.boxes_aabb[level] = np.zeros((box_size + 1, 2, 4), dtype=np.float32)

        step = [0, 0, 0]
        step[0] = (AABB[1][0] - AABB[0][0]) / granularity
        step[1] = (AABB[1][1] - AABB[0][1]) / granularity
        step[2] = (AABB[1][2] - AABB[0][2]) / granularity
        print 'Steps = ' + str(step)
        print 'Number of vertices:' + str(len(self.vertices))
        for i in range(0, len(self.vertices) / 3):
            # compute triangle AABB and its center
            aabb = [[100000, 100000, 100000, 0], [-100000, -100000, -100000, 0]]
            for j in range(0, 3):
                for k in range(0, 3):
                    aabb[0][k] = min(aabb[0][k], self.vertices[i * 3 + j, k])
                    aabb[1][k] = max(aabb[1][k], self.vertices[i * 3 + j, k])

            center = [0, 0, 0]
            for k in range(0, 3):
                center[k] = (aabb[0][k] + aabb[1][k]) / 2.0

            # Identify box
            index = [0, 0, 0]
            for k in range(0, 3):
                index[k] = int((center[k] - AABB[0][k]) / step[k]) - 1

            box_index = np.int32(
                index[0] * granularity * granularity +
                index[1] * granularity +
                index[2])

            # populate box
            if self.boxes_aabb[level][box_index].any():
                existing_aabb = self.boxes_aabb[level][box_index]
                for k in range(0, 3):
                    existing_aabb[0][k] = min(existing_aabb[0][k], aabb[0][k])
                    existing_aabb[1][k] = max(existing_aabb[1][k], aabb[1][k])
                self.boxes_aabb[level][box_index] = existing_aabb
                self.boxes_aabb[level][box_index][0][3] += 1
            else:
                self.boxes_aabb[level][box_index] = aabb
                self.boxes_aabb[level][box_index][0][3] = 1
                self.boxes_aabb[level][box_index][1][3] = i
        print 'Boxes:'
        nbBoxes = 0
        for i in range(0, len(self.boxes_aabb[level])):
            box = self.boxes_aabb[level][i]
            if box[0][0] + box[0][1] + box[0][2] != 0.0:
                print 'Box ' + str(i) + ': ' + str(self.boxes_aabb[level][i][0]) + ',' + str(self.boxes_aabb[level][i][1])
                nbBoxes += 1

        self.tex_boxes = np.zeros((nbBoxes*2, 4), dtype=np.float32)
        b = 0
        for i in range(0, len(self.boxes_aabb[level])):
            box = self.boxes_aabb[level][i]
            if box[0][0] + box[0][1] + box[0][2] != 0.0:
                for k in range(0, 4):
                    self.tex_boxes[b][k] = self.boxes_aabb[level][i][0][k]
                    self.tex_boxes[b + 1][k] = self.boxes_aabb[level][i][1][k]
                b += 2

        print 'tex boxes: ' + str(self.tex_boxes)
        self.nbBoxes = b / 2
        print str(self.nbBoxes) + ' boxes'


if __name__ == '__main__':
    app = Application()
    # app.loadBBPMeshes()
    AABB = app.load_obj_file('./models/monkey.obj')
    app.compute_bounding_boxes(AABB, 1, 4)
    app.run()
