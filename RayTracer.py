import sys
import time
from PIL import Image
import numpy as np
from utils import *
from color import *

def parse_scene(argv):
    input_file = open(argv[1], 'r')
    next(input_file)
    line = input_file.readline().rstrip().split()
    camera = Camera(line,int(argv[3]), int(argv[4]))
    next(input_file)
    line = input_file.readline().rstrip().split()
    settings = Settings(line)
    next(input_file)

    is_mirror = False
    line_counter = 3

    mtl_lst = []
    sph_lst = []
    pln_lst = []
    lgt_lst = []


    #reading the input file and creating variables
    for line in input_file:
        line_counter += 1
        if line != '\n':            
            line = line.rstrip().split()
            s = line[0].strip('#')
            if line[1] == 'Mirror':
                is_mirror = True
            elif 'mtl' in s:
                mtl_lst.append(Material(line, is_mirror))
            elif 'sph' in s:
                sph_lst.append(Sphere(line))
            elif 'pln' in s:
                pln_lst.append(Plane(line))
            elif 'lgt' in s:
                lgt_lst.append(Light(line))
            elif line[0] == '#':
                continue
            else:
                sys.exit('Error: did not recognized object: ' + line[0] + '(line '+ str(line_counter) + ')')
    scene = Scene([settings, mtl_lst, sph_lst, lgt_lst, pln_lst], camera)
    print("Finished parsing scene file " + argv[1])
    return camera, scene

def ray_cast(camera, scene, height, width):
    data = np.zeros((width, height, 3), dtype=np.float)
    # rays = np.empty(shape = (width, height), dtype = Ray)
    for i in range(width):
        for j in range(height):
            ray = Ray(camera.position, i * camera.screen.x + j * camera.screen.y + camera.screen.start_point)
            ray.find_intersection(scene)
            # rays[i][j] = ray
            color = calculate_color(scene, ray)
            data[i][j] = color
    # for i in range(width):
    #     for j in range(height):
    #         material = get_material(rays[i][j].obj, scene)
    #         reflective_color = ray_trace(data, rays[i][j], scene, material.reflection_color, scene.settings.rec_max)
    #         data[i][j] += reflective_color
    data = np.clip(data, 0, 1)
    return data

#NOTES:
# PIXEL SIZE: camera.width / picture width

def main():
    args = sys.argv
    if len(args) < 3:
        sys.exit("missing arguments")
    camera, scene = parse_scene(args)
    width = int(args[3])
    height = int(args[4])
    start_time = time.time()

    final_data = ray_cast(camera, scene, height, width)
    final_data = (final_data*255).astype(np.uint8)
    # data[0:256, 0:256] = [255, 0, 0] # red patch in upper left
    # print (final_data)
    img = Image.fromarray(final_data, 'RGB')
    img.save(args[2])
    end_time = time.time()

main()
