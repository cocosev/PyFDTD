from PIL import Image
import numpy as np
import matplotlib.pyplot as plt 

# Nombre del archivo a leer
filename = "perita.png"
# Tamanho final imagen
size = [20, 20]

# Convierte la imagen a blanco y negro (no escala grises)
im = Image.open(filename).convert('1', dither=Image.NONE)
# Cambia el tamanho
im = im.resize(size, Image.ANTIALIAS)
# Pasa a array de numpy

figure_array = np.logical_not(im)

plt.imshow(figure_array)
plt.show()
print(type(im))
