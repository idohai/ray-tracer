import sys
import numpy as np
import math

class Camera():
    def __init__(self, args, width, height):
        if not(12 <= len(args) <= 14):
            print (args)
            sys.exit('missing arguments')
        #PARSING:
        self.position = np.array([float(args[1]), float(args[2]), float(args[3])])
        self.look_at_point = np.array([float(args[4]), float(args[5]), float(args[6])])
        self.up_vector = np.array([float(args[7]), float(args[8]), float(args[9])])
        self.sc_dist = float(args[10])
        self.sc_width = float(args[11])
        self.ratio = height/width
        self.sc_height = self.ratio * self.sc_width
        self.screen = Screen(self.position, self.look_at_point, self.up_vector, self.sc_width, height, width, self.sc_dist)
        #Parsing FishEye:
        if len(args) > 12:
            if (args[12] == "false"):
                self.fisheye_flag = False
            else:
                self.fisheye_flag = True
            self.fisheye_value = args[13]
        else:
            self.fisheye_flag = False
            self.fisheye_value = 0.5

    #changing scale for x and y of he screen

#width = light radius
# N = number of shadow rays from scene parameter
class Screen():
    def __init__(self, position, look_at_point, up_vector, sc_width , height = 1, width = 1, distance = 0): #light_position, 
        self.z = look_at_point - position
        self.y = np.cross(up_vector, self.z)
        self.x = np.cross(self.y, self.z)
        self.z = self.z / np.linalg.norm(self.z)
        self.y = self.y / np.linalg.norm(self.y)
        self.x = self.x / np.linalg.norm(self.x)
        self.center = position + distance * self.z
        ratio = height/width
        sc_height = sc_width*ratio
        up_to_start = self.y*(sc_height/2)
        right_to_start = self.x*(sc_width/2)
        self.start_point = self.center - up_to_start - right_to_start

        self.set_vectors(sc_width, sc_height, width, height, distance)


    def set_vectors(self, sc_width, sc_height, width, height, distance):
        self.x = sc_width/width * self.x
        self.y = sc_height/height * self.y

class Material():
    def __init__(self, args, is_mirror):
        if len(args) != 12:
            print (args)
            sys.exit('missing arguments')
        self.diffuse_color = np.array([float(args[1]), float(args[2]), float(args[3])])
        self.specular_color = np.array([float(args[4]),float(args[5]),float(args[6])])
        self.reflection_color = np.array([float(args[7]),float(args[8]),float(args[9])])
        self.phong = float(args[10])
        self.trans = float(args[11])
        self.is_mirror = is_mirror

class Settings():
    def __init__(self, args):
        if len(args) != 6:
            print (args)
            sys.exit('missing arguments')
        self.background_color =  np.array([float(args[1]),float(args[2]),float(args[3])])
        self.sh_rays = int(args[4])
        self.rec_max = int(args[5])

class Plane():
    def __init__(self, args):
        if len(args) != 6:
            print (args)
            sys.exit('missing arguments')
        self.normal =  np.array([float(args[1]),float(args[2]),float(args[3])])
        self.offset = -float(args[4])
        self.mat_idx = int(args[5])

    def calc_intersection(self, ray):
        t = -(np.dot(ray.p0, self.normal) + self.offset)/(np.dot(ray.v, self.normal))
        if t < ray.t and t != 0:
            ray.t = t
            ray.obj = self

    def calc_normal(self, p):
        return self.normal

class Sphere():
    def __init__(self, args):
        if len(args) != 6:
            print (args)
            sys.exit('missing arguments')
        self.center =  np.array([float(args[1]),float(args[2]),float(args[3])])
        self.radius = float(args[4])
        self.mat_idx = int(args[5])

    def calc_intersection(self, ray):
        L = self.center - ray.p0
        t_ca = np.dot(L, ray.v)
        if t_ca < 0:
        #     print ("t_ca < 0")
            return 0
        d2 = np.dot(L,L) - t_ca**2
        r2 = self.radius**2
        if d2 > r2:
            return 0
        t_hc = math.sqrt(r2 - d2)
        t = min(t_ca - t_hc, t_ca + t_hc)
        if t < ray.t and t != 0:
            ray.t = t
            ray.obj = self

    def calc_normal(self, p):
        return (p - self.center) / (np.linalg.norm(p - self.center))

class Box():
    pass

class Light():
    def __init__(self, args):
        if len(args) != 10:
            print (args)
            sys.exit('missing arguments')
        self.position =  np.array([float(args[1]),float(args[2]),float(args[3])])
        self.color =  np.array([float(args[4]),float(args[5]),float(args[6])])
        self.specular_intensity = float(args[7])
        self.shadow_intensity = float(args[8])
        self.radius = float(args[9])

class Scene():
    def __init__(self, lst, camera):
        self.settings = lst[0]
        self.material = lst[1]
        self.lights = lst[3]
        self.objects = lst[2] + lst[4]
        self.up_vector = camera.up_vector

    def light_intersection(self, ray, scene):
        distance = float('inf')
        hit_light = None
        for light in scene.lights:
            light_ray = Ray(ray.p0, light.position)
            if (light_ray.v == ray.v).all():
                current_distance = np.linalg.norm(ray.p0 - light.position)
                if current_distance < distance:
                    hit_light = light

class Ray():
    def __init__(self, p0, p1):
        v = p1 - p0
        self.v = v/np.linalg.norm(v)
        self.p0 = p0
        self.p1 = p1
        self.t = float('inf')
        self.obj = None

    def vector(self):
        return self.p0 + self.t*self.v

    def find_intersection(self, scene):
        for obj in scene.objects:
            obj.calc_intersection(self)
        return self.vector()

    def object_intersection(self, obj):
        obj.calc_intersection(self)


def get_material(obj, scene):
    return scene.material[obj.mat_idx-1]

