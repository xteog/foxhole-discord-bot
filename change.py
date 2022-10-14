from testImage import *
from PIL import Image


name = 'Town Base 1'
changeColor(Image.open(defs.PATH + f'/Icon/{name}.png'), True).save(f'C:/Users/gallo/Desktop/{name} Colonial.png')

name = 'Town Base 2'
changeColor(Image.open(defs.PATH + f'/Icon/{name}.png'), True).save(f'C:/Users/gallo/Desktop/{name} Colonial.png')

name = 'Town Base 3'
changeColor(Image.open(defs.PATH + f'/Icon/{name}.png'), True).save(f'C:/Users/gallo/Desktop/{name} Colonial.png')

name = 'Town Base 1'
changeColor(Image.open(defs.PATH + f'/Icon/{name}.png'), False).save(f'C:/Users/gallo/Desktop/{name} Warden.png')

name = 'Town Base 2'
changeColor(Image.open(defs.PATH + f'/Icon/{name}.png'), False).save(f'C:/Users/gallo/Desktop/{name} Warden.png')

name = 'Town Base 3'
changeColor(Image.open(defs.PATH + f'/Icon/{name}.png'), False).save(f'C:/Users/gallo/Desktop/{name} Warden.png')

name = 'Relic Base 1'
changeColor(Image.open(defs.PATH + f'/Icon/{name}.png'), True).save(f'C:/Users/gallo/Desktop/{name} Colonial.png')

name = 'Relic Base 1'
changeColor(Image.open(defs.PATH + f'/Icon/{name}.png'), False).save(f'C:/Users/gallo/Desktop/{name} Warden.png')
