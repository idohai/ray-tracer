# ray-tracer

A simple Ray-Tracer implemented in python.

the Ray-Tracer recieve Scene information and renders the described scene to an image.

information:
* Camera (Position, Look-at point, Up vector, Distance of camera screen from the camera, Screen width)
* Scene settings (Background color, Number of shadow rays used to compute soft shadows, Maximum recursion level for reflective surfaces, Fish-eye (bool))
* Surfaces in scene (Spheres, Infinite planes, Boxes)
* Surface materials (Diffuse color,Specular color, "Phong speculariy coefficient", Reflection color, Transparency)
* Light sources (Position, color, Shadow intensity, Specular intensity)

To use: 
Run RayTracer.py with the following arguments:
* [1]: Scene information file
* [2]: Output image file name
* [3]: Output image width
* [4]: Output image height

TODO:
* Improve Fisheye functionality for more accurate results
* Implement the reflective color calculations
