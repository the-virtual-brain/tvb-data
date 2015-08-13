import os

def flip_winding(triangles):
    """
    :param triangles: an array of indices
    """
    for i in xrange(0, len(triangles), 3):
        triangles[i], triangles[i+1] = triangles[i+1], triangles[i]

def flip_normals(normals):
    """
    :param triangles: an array of normals
    """
    for i in xrange(len(normals)):
        normals[i] = -normals[i]

def to_obj():    
    unimplemented

def main_flip_standard_surface(folder):
    """
    flips triangle winding and normals of a surface stored as 
    normals.txt , triangles.txt 
    """
    def read(pth):
        with open(pth) as f:
            return [float(x) for x in f.read().split()]
    
    def write(pth, data):
        with open(pth, 'w') as f:
            for i in xrange(0, len(data), 3):
                f.write(' '.join(str(t) for t in data[i:i+3]))
                f.write('\n')

    normals_pth = os.path.join(folder, 'normals.txt')
    triangles_pth = os.path.join(folder, 'triangles.txt')
    normals = read(normals_pth)
    triangles = read(triangles_pth)
    flip_normals(normals)
    flip_winding(triangles)
    write(normals_pth, normals)
    write(triangles_pth, triangles)

