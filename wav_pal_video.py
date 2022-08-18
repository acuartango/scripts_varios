#!/usr/bin/python
# -*- coding: utf-8 -*-
import wave, struct, math, random, numpy
from sympy import false
import png

obj = wave.open('/home/nugbe/Descargas/HackIt2022/audioWAVvideo/data.wav','rb')
# _wave_params(nchannels=1, sampwidth=2, framerate=8000000, nframes=1693753446, comptype='NONE', compname='not compressed')
params=obj.getparams()
numFramesParaLeer=50000 # Valor aleatorio de tamaño de buffer para no leer todos los gigas del fichero de golpe, lo que bloqueaba el PC.
filaImagen=0
columnaImagen=0
ancho=382 # Ancho y alto obtenidos a prueba y error tras poder ver los frames
alto=260
contadorSYNC=0
contadorFotos=0
image = numpy.zeros((alto, ancho))

# Leer de un buffer para evitar colapsar la memoria (numFramesParaLeer)
for i in range (params.nframes // numFramesParaLeer):
      misFrames = obj.readframes(numFramesParaLeer)
      # // es división sin decimales
      nb_samples = len(misFrames) // params.sampwidth
      # Ej: format= "<50000h"   -->    '<' -> little endian, 'h' -> short(2 bytes) , 50000 -> tamaño a leer
      format = {1: '%db', 2: '<%dh', 4: '<%dl'}[params.sampwidth] % nb_samples
      # Metemos en el array "frames" cada valor discreto del buffer (50000 muestras) leído del wav asumiendo el formato little endian con 2 bytes
      frames = struct.unpack(format, misFrames)
      for frame in frames:
            if frame < -10000:
                  # Contamos los negativos de la sincronización vertical que no contienen información de pixel
                  # Más de 300 m¡negartivos es un fotograma nuevo (HSYNC), más de 20 es únicamente una línea nueva (VSYNC)
                  contadorSYNC+=1
            else:
                  # 300 valores negativos <10000 supone un cambio de frame en el vídeo o VSYNC
                  if contadorSYNC>300:
                        filaImagen=0
                        columnaImagen=0
                  # 20 valores negativos <10000 supone un cambio de línea dentro del frame en el vídeo o HSYNC
                  elif contadorSYNC>20:
                        filaImagen+=1
                        columnaImagen=0
                  else:
                        # Caso de guardar un frame nuevo
                        if filaImagen >= alto-1:
                              # Hemos leído todas las filas de la imagen, la salvamos.
                              # 'L' -> greyscale (1 channel)
                              contadorFotos+=1
                              png.from_array(image.astype(numpy.uint16), "L").save("frame_" + str(contadorFotos) + ".png")
                              image = numpy.zeros((alto, ancho))
                              filaImagen=0
                              columnaImagen=0
                        # Caso de almacenar pixel en la imagen. Se cogen solo valores superiores a 2000 que es el valor de señal buena
                        elif frame >= 2000 and filaImagen < alto-1 and columnaImagen < ancho-1:
                              image[filaImagen, columnaImagen] = frame
                              columnaImagen+=1
                  contadorSYNC=0
obj.close()

# print ("media: " + str(numpy.mean(np_array)))
# print ("max:" + str(numpy.max(np_array)))
# print ("min:" + str(numpy.min(np_array)))
# media: 80.84225679980398
# max:2351
# min:-11965

# Suposiciones:
# - La imagen es de 241x385
# - El tiempo de muestreo es de 8000000 Hz
# - El tiempo de muestreo de la imagen es de 8000000/241 = 30000 Hz
# - El tiempo de muestreo de la imagen es de 8000000/385 = 20000 Hz
