from PIL import Image, ImageDraw, ImageFont
from testRequest import read
from scipy.spatial import Voronoi
import numpy as np
import defs
import math


def updateMap(map, data, index=-1):
  iconId = defs.ICON_ID
  with Image.open(defs.PATH + '/Map/Map{}.png'.format(map)) as background:
    bg_w, bg_h = background.size


    for item in data['mapItems']:
      x = round(item['x'] * bg_w)
      y = round(item['y'] * bg_h)
      icon = iconId[item['iconType']]

      with Image.open(defs.DB['iconImage'].format(icon)) as img:
        
        img_w, img_h = img.size
        if item['flags'] == 0 and index != data['mapItems'].index(item):
          img_w = img_w * 2 // 3
          img_h = img_h * 2 // 3
          img = img.resize((img_w, img_h))
        elif index != data['mapItems'].index(item):
          img_w = img_w * 3 // 4
          img_h = img_h * 3 // 4
          img = img.resize((img_w, img_h))
        offset = (x - img_w // 2, y - img_h // 2)

        if item['flags'] == 41:
          ico = Image.open(defs.DB['iconImage'].format('Victory'))
          ico_w, ico_h = ico.size
          img_trans = Image.new(mode="RGBA", size=ico.size, color=(255, 255, 255, 0))
          img_trans.paste(img, ((ico_w-img_w)//2, (ico_h-img_h)//2))
          ico.paste(img_trans, (0, 0), img_trans)
          img = ico
          
        if item['teamId'] == "COLONIALS":
          img = changeColor(img, 1)
        elif item['teamId'] == "WARDENS":
          img = changeColor(img, 0)

        img_trans = Image.new(mode="RGBA", size=background.size, color=(255, 255, 255, 0))
        img_trans.paste(img, offset)
        background.paste(img_trans, (0, 0), img_trans)
        if item['flags'] == 41:
          ico.close()

    txt = Image.new('RGBA', background.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt)
    myFont = ImageFont.truetype(defs.PATH + '/data/Clarendon.ttf', 25) 

    for item in data['mapTextItems']:
      if item['mapMarkerType'] == 'Major':
        x = round(item['x'] * bg_w)
        y = round(item['y'] * bg_h-5) #TODO aggiusta offset
        text = item['text']

        size = draw.textsize(text, font=myFont)
        x = x - size[0]/2
        y = y - size[1]/2

        c = (0, 0, 0, 180)
        draw.text((x-1, y-1), text, font=myFont, fill=c)
        draw.text((x+1, y-1), text, font=myFont, fill=c)
        draw.text((x-1, y+1), text, font=myFont, fill=c)
        draw.text((x+1, y+1), text, font=myFont, fill=c)
        draw.text((x, y), text, fill=(255, 255, 255, 180), font=myFont)

    background = Image.alpha_composite(background, txt)

    background.save(defs.DB['mapImage'].format(map))
    #print(map + " updated")


def paste_icon(backgrond, item, index=-1):
  x = round(item['x'] * bg_w)
  y = round(item['y'] * bg_h)
  icon = defs.ICON_ID[item['iconType']]

  with Image.open(defs.DB['iconImage'].format(icon)) as img:
    
    img_w, img_h = img.size
    if item['flags'] == 0 and index != data['mapItems'].index(item):
      img_w = img_w * 2 // 3
      img_h = img_h * 2 // 3
      img = img.resize((img_w, img_h))
    elif index != data['mapItems'].index(item):
      img_w = img_w * 3 // 4
      img_h = img_h * 3 // 4
      img = img.resize((img_w, img_h))
    offset = (x - img_w // 2, y - img_h // 2)

    if item['flags'] == 41:
      ico = Image.open(defs.DB['iconImage'].format('Victory'))
      ico_w, ico_h = ico.size
      img_trans = Image.new(mode="RGBA", size=ico.size, color=(255, 255, 255, 0))
      img_trans.paste(img, ((ico_w-img_w)//2, (ico_h-img_h)//2))
      ico.paste(img_trans, (0, 0), img_trans)
      img = ico
      
    if item['teamId'] == "COLONIALS":
      img = changeColor(img, 1)
    elif item['teamId'] == "WARDENS":
      img = changeColor(img, 0)

    img_trans = Image.new(mode="RGBA", size=background.size, color=(255, 255, 255, 0))
    img_trans.paste(img, offset)
    background.paste(img_trans, (0, 0), img_trans)
    if item['flags'] == 41:
      ico.close()

    
def changeColor(img, color):
  if color == 1:
    color = (101, 135, 94)
  elif color == 0:
    color = (45, 108, 161)
  else:
    color = (255, 0, 0)

  img = img.convert('RGBA')
  for i in range(img.size[0]):
    for j in range(img.size[1]):
      data = img.getpixel((i, j))
      r = round(data[0] * color[0] / 255)
      g = round(data[1] * color[1] / 255)
      b = round(data[2] * color[2] / 255)
      img.putpixel((i, j), (r, g, b, data[3]))
  return img

def addCircle(map, pos):
  mask = Image.open(defs.PATH + '/data/maskCircle.png')
  circle = Image.open(defs.PATH + '/data/circle.png')
  img = Image.open(defs.DB['mapImage'].format(map))
  img_w, img_h = img.size
  x = round(pos[0] * img_w) - 40
  y = round(pos[1] * img_h) - 40
  img.paste(circle, (x, y), mask)
  img.save(defs.PATH + '/data/tempImage.png')
  img.close()
  circle.close()
  mask.close()


def create_border():
  map = Image.open("./Map/MapAcrithia.png")
  for i in range(map.size[0]):
    for j in range(map.size[1]):
      if map.getpixel((i, j))[3] == 255:
        map.putpixel((i, j), (0, 0, 0, 0))
      else:
        map.putpixel((i, j), (0, 0, 0, 255))

  map.save('./data/MapBorder.png')

  mask = map.resize((map.size[0]-10, map.size[1]-9))

  original_map = Image.open("./Map/MapAcrithia.png")
  
  bg = Image.new("RGBA", original_map.size, (0, 0, 0, 255))
  bg.paste(mask, (5, 4))

  original_map.paste(bg, (0, 0), original_map)
  original_map.save('./data/MapBorder.png')
  map.close()


def add_border(img):
  border = Image.open(defs.PATH + "/data/MapBorder.png")
  img.paste(border, (0, 0), border)
  return img


def highlight_name(map, i):
  with Image.open(defs.DB['mapImage'].format(map)) as img:
    bg_w, bg_h = img.size
    txt = Image.new('RGBA', img.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt)
    myFont = ImageFont.truetype(defs.PATH + '/data/Clarendon.ttf', 35)
    draw = ImageDraw.Draw(txt)

    data = read(defs.DB['mapData'].format(map))['mapTextItems'][i]

    x = round(data['x'] * bg_w)
    y = round(data['y'] * bg_h)
    size = draw.textsize(data['text'], font=myFont)
    x = x - size[0]/2
    y = y - size[1]/2

    c = (0, 0, 0, 255)
    draw.text((x-1, y-1), data['text'], font=myFont, fill=c)
    draw.text((x+1, y-1), data['text'], font=myFont, fill=c)
    draw.text((x-1, y+1), data['text'], font=myFont, fill=c)
    draw.text((x+1, y+1), data['text'], font=myFont, fill=c)
    draw.text((x, y), data['text'], fill=(255, 255, 255, 255), font=myFont)

    background = Image.alpha_composite(img, txt)

  background.save(defs.PATH + '/data/tempImage.png')


def voronoi_finite_polygons_2d(vor, radius=None):
    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()*2

    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            new_regions.append(vertices)
            continue

        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                continue


            t = vor.points[p2] - vor.points[p1]
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)


def drawVoronoi(img, data):
  border = Image.new("RGBA", img.size, (255, 255, 255, 0))
  points = []
  faction = []

  for item in data:
    if item['iconType'] in [45, 46, 47, 56, 57, 58]:
      img_w, img_h = img.size
      x = round(item['x'] * img_w)
      y = round(item['y'] * img_h)
      if item['teamId'] == 'COLONIALS':
        faction.append(1)
      elif item['teamId'] == 'WARDENS':
        faction.append(2)
      else:
        faction.append(0)
      points.append([x, y])

  vor = Voronoi(points)
  regions, vertices = voronoi_finite_polygons_2d(vor)
  draw = ImageDraw.Draw(border, 'RGBA')

  for reg in regions:
    polygon = []
    for i in reg:
      polygon.append((vertices[i][0], vertices[i][1]))

    color = (200, 200, 200, 50)
    if faction[regions.index(reg)] == 1:
      color = (141, 192, 0, 50)
    if faction[regions.index(reg)] == 2:
      color = (2, 109, 188, 50)
    draw.polygon(polygon, fill=color, outline ="black", width=2)

  bg =  Image.new(mode="RGBA", size=img.size, color=(255, 255, 255, 0))
  bg.paste(border, img)
  img = Image.alpha_composite(img, bg) 

  return img


def paste_depot(items, size):
  bg = Image.open(defs.PATH + '/data/FullMap.png')
  txt = Image.new('RGBA', bg.size, (255,255,255,0))
  draw = ImageDraw.Draw(txt)
  myFont = ImageFont.truetype(defs.PATH + '/data/Clarendon.ttf', 25 * size // (defs.D_RESIZE-50))

  for item in items:
    offset = defs.MAP_POSITION[item['map']]

    x = round(item['x'] * defs.REGION_SIZE[0]) + offset[0]
    y = round(item['y'] * defs.REGION_SIZE[1]) + defs.MAP_SIZE[1] - offset[1]

    #Paste icon
    icon = defs.ICON_ID[item['iconType']]
    img = Image.open(defs.DB['iconImage'].format(icon))
    img_w, img_h = img.size
    
    img = img.resize((img_w * size // defs.D_RESIZE, img_h * size // defs.D_RESIZE), Image.LANCZOS)

    img_w, img_h = img.size
    offset = (x - img_w // 2, y - img_h // 2)
      
    img = changeColor(img, 1)

    img_trans = Image.new(mode="RGBA", size=bg.size, color=(255, 255, 255, 0))
    img_trans.paste(img, offset)
    bg.paste(img_trans, (0, 0), img_trans)
    img.close()

    #Paste text
    text = item['location']

    size_txt = draw.textsize(text, font=myFont)
    x = x - size_txt[0]//2
    y = y - size_txt[1]//2 + img_h // 3 * 2

    c = (0, 0, 0, 255)
    draw.text((x-5, y-5), text, font=myFont, fill=c)
    draw.text((x+5, y-5), text, font=myFont, fill=c)
    draw.text((x-5, y+5), text, font=myFont, fill=c)
    draw.text((x+5, y+5), text, font=myFont, fill=c)
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=myFont)

  bg = Image.alpha_composite(bg, txt)

  txt.close()

  return bg


def paste_text_fullmap(items):
  bg = Image.open(defs.PATH + '/data/FullMap.png')
  txt = Image.new('RGBA', bg.size, (255,255,255,0))
  draw = ImageDraw.Draw(txt)
  myFont = ImageFont.truetype(defs.PATH + '/data/Clarendon.ttf', 25 * defs.REGION_SIZE[0] // (defs.D_RESIZE-50))

  for item in items:
    offset = defs.MAP_POSITION[item['map']]

    x = offset[0]
    y = defs.MAP_SIZE[1] - offset[1]

    #Paste text
    text = item['map']

    size_txt = draw.textsize(text, font=myFont)
    x = x - size_txt[0]//2
    y = y - size_txt[1]//2

    c = (0, 0, 0, 255)
    draw.text((x-5, y-5), text, font=myFont, fill=c)
    draw.text((x+5, y-5), text, font=myFont, fill=c)
    draw.text((x-5, y+5), text, font=myFont, fill=c)
    draw.text((x+5, y+5), text, font=myFont, fill=c)
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=myFont)

  bg = Image.alpha_composite(bg, txt)

  txt.close()

  bg.save(defs.PATH + '/data/tempFullMap.png')


def create_fullmap(mapOrigin):
  bg = Image.new('RGBA', defs.MAP_SIZE, (0, 0, 0, 0))
  for map in defs.MAP_NAME:
    img = Image.open(mapOrigin.format(map))
    data = read(defs.DB['mapData'].format(map))['mapItems']
    vor = drawVoronoi(img, data)
    vor = add_border(vor)

    x = defs.MAP_POSITION[map][0]
    y = defs.MAP_POSITION[map][1] * -1 + defs.MAP_SIZE[1]
    
    bg.paste(vor, (x, y), img)
    img.close()
  
  bg.save(defs.PATH + '/data/FullMap.png')


def resize_fullmap():
  img = Image.open(defs.PATH + '/data/tempFullMap.png')
  img = img.resize((img.size[0] // 2, img.size[1] // 2), Image.ANTIALIAS)
  img.save(defs.PATH + '/data/tempFullMap.png')


def paste_items_fullmap(items, crop=False):
  xMean = 0
  yMean = 0
  for item in items:
    offset = defs.MAP_POSITION[item['map']]
    x = item['x'] * defs.REGION_SIZE[0] + offset[0]
    y = item['y'] * defs.REGION_SIZE[1] + defs.MAP_SIZE[1] - offset[1]
    xMean += x  / len(items)
    yMean += y / len(items)

  max_d = -1
  for i in range(len(items)):
    offset = defs.MAP_POSITION[items[i]['map']]
    x = items[i]['x'] * defs.REGION_SIZE[0] + offset[0]
    y = items[i]['y'] * defs.REGION_SIZE[1] + defs.MAP_SIZE[1] - offset[1]
    d = math.sqrt((xMean - x) ** 2 + (yMean - y) ** 2)
    if max_d < d:
      max_d = d
      index_max = i

  offset = defs.MAP_POSITION[items[index_max]['map']]
  x = items[index_max]['x'] * defs.REGION_SIZE[0] + offset[0]
  y = items[index_max]['y'] * defs.REGION_SIZE[1] + defs.MAP_SIZE[1] - offset[1]
  new_w = abs(xMean - x) + 300
  new_h = abs(yMean - y) + 300
  new_size = max(new_w, new_h)

  img = paste_depot(items, int(new_size))
  
  img = img.crop((xMean - new_size, yMean - new_size, xMean + new_size, yMean + new_size))
  img.save(defs.PATH + '/data/tempFullMap.png')
  resize_fullmap()
  img.close()


if __name__ == '__main__':
  create_border()





