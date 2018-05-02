from PIL import Image
import numpy as np


# Nombre del archivo a leer
filename = "pera.png"
# Tamaño final imagen
size = [20, 20]

# Convierte la imagen a blanco y negro (no escala grises)
im = Image.open(filename).convert('1', dither=Image.NONE)
# Cambia el tamaño
im = im.resize(size, Image.ANTIALIAS)
# Pasa a array de numpy
figure_array = np.logical_not(np.array(im))

