from utils import *
from random import random
# def calc_diffuse_color(hitpoint, obj, light, scene, light_ray):
#     return get_material(obj, scene).diffuse_color

epsilon = 0.001


def calculate_color(scene, ray):
    if ray.t == float('inf'):
        color = scene.setting.background_color
        return color
    else:
        color = np.array([0,0,0], dtype = float)
        reflection_color = np.array([0,0,0], dtype = float)
        material = get_material(ray.obj, scene)
        for light in scene.lights:
            # shifted_point = ray.vector() + epsilon*ray.obj.calc_normal(ray.vector()) ##LIGHT RAY ONLY FOR HARD SHADOWS
            light_ray = Ray(light.position, ray.vector()) ##LIGHT RAY ONLY FOR HARD SHADOWS
            color += diffuse_specular_color(light, ray, light_ray, scene, material)
            # color *= soft_shadows(light, ray, scene) #include for soft_shadows
        color = (scene.settings.background_color * material.trans) + color * (1-material.trans)
    # return diffuse_color
    return color

def ray_trace(data, original_ray, scene, reflection, rec_depth):
    if (rec_depth == 0):
        return np.array([0, 0, 0])
    if (original_ray.t == float('inf')):
        return np.array([0, 0, 0])
    hit_light = scene.light_intersection(original_ray, scene)
    if (hit_light != None):
        return hit_light.color
    color = np.array([0, 0, 0])
    hitpoint = original_ray.vector()
    material = get_material(original_ray.obj, scene)
    ray = Ray(hitpoint, hitpoint)
    normal = original_ray.obj.calc_normal(hitpoint)
    if material.trans != 0:
        reflected = original_ray.v-2*(np.dot(original_ray.v, normal))*normal
        ray.v = reflected
        ray.find_intersection(scene)
        color = ray_trace(data, ray, scene, material.reflection_color, rec_depth - 1)
    # if material.is_mirror:
        
        # color += ray_trace(ray_trace(data, ray, scene, material.reflection_color, rec_depth - 1))
    return reflection * color

def diffuse_specular_color(light, ray, light_ray, scene, material):
    # shifted_point = ray.vector() + epsilon*ray.obj.calc_normal(ray.vector())
    # light_ray = Ray(light.position, shifted_point)
    diffuse = calc_diffuse_color(light, ray, light_ray, scene, material)
    specular = calc_specular_color(light, ray, light_ray, scene, material)
    return diffuse + specular

def calc_diffuse_color(light, ray, light_ray, scene, material):
    L = light_ray.p0 - light_ray.p1
    L = L / np.linalg.norm(L)
    normal = ray.obj.calc_normal(ray.vector())
    dot_product = np.dot(normal, L)
    I_diff = material.diffuse_color * light.color * dot_product 
    I_diff *= hard_shadows(light, ray, light_ray, scene) #include for hard shadows result
    return I_diff

def calc_specular_color(light, ray, light_ray, scene, material):
    Ks = material.specular_color
    Ip = light.color
    normal = ray.obj.calc_normal(ray.vector())
    L = light_ray.p0 - light_ray.p1
    R = 2*(np.dot(normal, L))*normal - L
    V = ray.p0 - ray.vector()
    # H = L+V #H*N ~ V*R
    R = R/np.linalg.norm(R)
    V = V/np.linalg.norm(V)
    phong = (np.dot(R, V))
    phong = pow(phong, material.phong)
    specular_color = Ks*Ip*phong
    return specular_color * light.specular_intensity

def hard_shadows(light, ray, light_ray, scene):
    light_ray.object_intersection(ray.obj)  #now t is updated to the current object value
    original_t = light_ray.t
    light_ray.find_intersection(scene)      #new t is updated to the closest object
    new_t = light_ray.t

    if (original_t != new_t):
    # if not collision(ray, light_ray):
        return (1 - light.shadow_intensity)
    return 1

def collision(ray, light_ray):
    if (light_ray.vector() > ray.vector() + epsilon).any():
        return False
    if (light_ray.vector() < ray.vector() - epsilon).any():
        return False
    return True

def soft_shadows(light, ray, scene):
    num_of_rays = scene.settings.sh_rays
    perp_plane = Screen(light.position, ray.vector(), scene.up_vector, 1/num_of_rays, light.radius, light.radius )
    precentage = hit_precentage(light, ray, perp_plane, scene)
    intensity = 1.0-light.shadow_intensity + light.shadow_intensity*precentage
    return intensity

def hit_precentage(light, ray, perp_plane, scene):
    hit_count = 0
    num_of_rays = scene.settings.sh_rays
    for i in range(num_of_rays):
        for j in range(num_of_rays):
            rand_x = random()
            rand_y = random()
            # print (rand_x, rand_y)
            position = perp_plane.start_point
            x_correction = i*perp_plane.x + rand_x
            y_correction = j * perp_plane.y + rand_y
            position = position - x_correction - y_correction
            light_ray = Ray(position, ray.vector())
            light_ray.find_intersection(scene)
            # if (light_ray.vector() != ray.vector()).any():
            if (light_ray.obj == ray.obj):
                hit_count += 1
    # print(hit_count)
    hit_precent = hit_count / (num_of_rays*num_of_rays)
    return hit_precent

    # color = I_E, ambient, SIGMA_l *(diffuse_color + specular_color)*S_L I_L + reflection(K_R I_R) + transperacy K_T I_T
    # I_E = emition (minori)
    # K_A (minori)
    # I_AL (minori)
    # S_L = shadow term - i see light or i dont see light (1, 0 for hard shadows, )
    # I_L = intensity (light color)
    # I_0 = intensity
    # I_R = Radiance for mirror reflection ray
    # K_s
    # Li = Radiance for refraction ray
    # Ki = transperacy coefficent


    #types of light: diffuse, specular, emition, ambient
    # we use point light
    #area light = full shadow + soft shadow
    #light intensity will be multiplied by number of rays that hit the surface, divided by the total number of rays we sent
    # to simulate light we:
    # find plane perpendicular
    # define a rectangle on that plane, center at the light source and as wide as the light radius
    # divide the rectangle into grid (N*N, N = num of shadow rays from scene)
    # select random point in each cell and shoot ray to random point
    # aggregate the values and count how many of them hit the required point on surface
    # light intensity = (1-shadow intensity)*1 +shadow_intensity*(% of rays that hit the points from light source) (only effect diffuse and specular lightting)


#IDEAS FOR FIX:
# 1. shadows not calculated correctly, now its the same result as comparing objects instead of hitpoints
# way to fix collision in hard_shadows & soft_shadows is creating "Hit" class which contains position and shifted_point for easy comparison.
#
#
#IDEAS TO ADD:
# anti aliasing (5 -> 21:26)
