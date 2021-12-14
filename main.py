import pygame
from pygame.locals import *
from math import sin, cos, sqrt

class obj_convert():
    def __init__(self, filename):
        self.file = open(filename, "r").read()

    def get_verts(self):
        vert = []

        for line in self.file.split("\n"):
            if line.startswith("v"):
                x = line.lstrip("v "); x = x.split(" ")
                vert.append((float(x[0]), float(x[1]), float(x[2])))
        return vert

    def get_faces(self):
        faces = []

        for line in self.file.split("\n"):
            if line.startswith("f"):
                x = line.lstrip("f "); x = x.split(" ")
                faces.append((int(x[0])-1, int(x[1])-1, int(x[2])-1))
        return faces

class translate():
    def rotateX(coords, angle):
        equation = [[1, 0, 0],
                    [0, cos(angle), -sin(angle)],
                    [0, sin(angle), cos(angle)]]

        result = []

        for i in range(len(equation)):
            result.append((equation[i][0]*coords[0])+(equation[i][1]*coords[1])+(equation[i][2]*coords[2]))

        return result

    def rotateY(coords, angle):
        equation = [[cos(angle), 0, sin(angle)],
                    [0, 1, 0],
                    [-sin(angle), 0, cos(angle)]]

        result = []

        for i in range(len(equation)):
            result.append((equation[i][0]*coords[0])+(equation[i][1]*coords[1])+(equation[i][2]*coords[2]))

        return result

    def rotateZ(coords, angle):
        equation = [[cos(angle), -sin(angle), 0],
                    [sin(angle), cos(angle), 0],
                    [0, 0, 1]]

        result = []

        for i in range(len(equation)):
            result.append((equation[i][0]*coords[0])+(equation[i][1]*coords[1])+(equation[i][2]*coords[2]))

        return result

class render:
    def __init__(self, triangles):
        self.triangles = triangles

    def depth_buffer(self):
        for i in range(len(self.triangles)):
            for j in range(len(self.triangles[i])):
                if j != 3:
                    self.triangles[i][j] = list(self.triangles[i][j])
                    self.triangles[i][j][0], self.triangles[i][j][2] = self.triangles[i][j][2], self.triangles[i][j][0]
        self.triangles = sorted(self.triangles)

        return self.triangles

obj_file = input("Enter the obj filename: ")
obj_file = obj_convert(obj_file)
verts = list(obj_file.get_verts())
faces = list(obj_file.get_faces())
zoom = 100# int(input("Set zoom: "))

camera = (0, 0, 0)
light_direction = [0, 0, -1]

for i in range(len(verts)):
    verts[i] = list(verts[i])

    for j in range(len(verts[i])):
        verts[i][j] *= -zoom

angle = [0, 0, 0]

WIDTH, HEIGHT = 800, 600
HALF_WIDTH, HALF_HEIGHT = WIDTH/2, HEIGHT/2

pygame.init()

window = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("3D Stuff")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 32)

running = True
av = [0, 0, 0]

rndr = render((1, 1, 1, 1, 1))

while running:
        window.fill((0, 0, 0))

        for event in pygame.event.get():
                if event.type == QUIT:
                        running = False

                if event.type == KEYDOWN:
                        if event.key == K_UP:
                                av[0] = 0.1

                        if event.key == K_DOWN:
                                av[0] = -0.1

                        if event.key == K_RIGHT:
                                av[1] = 0.1

                        if event.key == K_LEFT:
                                av[1] = -0.1

                        if event.key == K_q:
                            zoom += 1

                        if event.key == K_e:
                            zoom -= 1

                if event.type == KEYUP:
                        if event.key == K_UP:
                                av[0] = 0

                        if event.key == K_DOWN:
                                av[0] = 0

                        if event.key == K_RIGHT:
                                av[1] = 0

                        if event.key == K_LEFT:
                                av[1] = 0

        for i in range(len(angle)):
                angle[i] += av[i]

        trans_verts = []
        renderable_triangles = []

        for i in range(len(verts)):
                trans_verts.append(translate.rotateX(translate.rotateY(translate.rotateZ(verts[i], angle[2]), angle[1]), angle[0]))

        for face in faces:
                triangle = [trans_verts[face[0]],
                                        trans_verts[face[1]],
                                        trans_verts[face[2]]]

                line1 = [triangle[1][0] - triangle[0][0],
                                 triangle[1][1] - triangle[0][1],
                                 triangle[1][2] - triangle[0][2]]

                line2 = [triangle[2][0] - triangle[0][0],
                                 triangle[2][1] - triangle[0][1],
                                 triangle[2][2] - triangle[0][2]]

                normal = [line1[1] * line2[2] - line1[2] * line2[1],
                                  line1[2] * line2[0] - line1[0] * line2[2],
                                  line1[0] * line2[1] - line1[1] * line2[0]]

                l = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                normal[0] /= 1
                normal[1] /= 1
                normal[2] /= 1

                if (normal[2] < 0): # normal[0] * (triangle[0][0] - camera[0]) + normal[1] * (triangle[0][1] - camera[1]) + normal[2] * (triangle[0][2] - camera[2]) < 0

                        l = sqrt(light_direction[0]*light_direction[0] + light_direction[1]*light_direction[1] + light_direction[2]*light_direction[2])
                        light_direction[0] /= l; light_direction[1] /= l; light_direction[2] /= l

                        dp = (normal[0] * light_direction[0]) + (normal[1] * light_direction[1]) + (normal[2] * light_direction[2])
                        triangle.append(float(dp))

                        renderable_triangles.append(triangle)

        rndr.triangles = renderable_triangles
        renderable_triangles = rndr.depth_buffer()

        for renderable_triangle in renderable_triangles:
                d2_tri = [
                        [renderable_triangle[0][2] + HALF_WIDTH, renderable_triangle[0][1] + HALF_HEIGHT + 60],
                        [renderable_triangle[1][2] + HALF_WIDTH, renderable_triangle[1][1] + HALF_HEIGHT + 60],
                        [renderable_triangle[2][2] + HALF_WIDTH, renderable_triangle[2][1] + HALF_HEIGHT + 60]
                ]

                c = renderable_triangle[3]

                if c > 255:
                        c = 255
                elif c < 0:
                        c = 0

                pygame.draw.polygon(window, (c, c, c), d2_tri)
                # pygame.draw.lines(window, (255, 0, 0), True, d2_tri)

        text = font.render(str(clock.get_fps()), True, (255, 255, 0))
        textRect = text.get_rect()

        window.blit(text, textRect)

        pygame.display.flip()

        clock.tick(30)

pygame.quit()
