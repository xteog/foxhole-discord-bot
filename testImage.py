from PIL import Image, ImageDraw, ImageFont
from testRequest import read
from scipy.spatial import Voronoi
import numpy as np
import defs

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

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1] # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)


def drawVoronoi(map, img):
  data = read(defs.DB['mapData'].format(map))['mapItems']
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

    color = (200, 200, 200, 125)
    if faction[regions.index(reg)] == 1:
      color = (0, 255, 0, 125)
    if faction[regions.index(reg)] == 2:
      color = (0, 0, 255, 125)
    draw.polygon(polygon, fill=color, outline ="black", width=2)

  out = Image.alpha_composite(img, border)

  return out


def group_maps():
  bg = Image.new('RGBA', defs.MAP_SIZE, (0, 0, 0, 0))
  for map in defs.MAP_NAME:
    with Image.open(defs.PATH + '/Map/Map{}.png'.format(map)) as img:
      out = drawVoronoi(map, img)
      x = defs.MAP_POSITION[map][0]
      y = defs.MAP_POSITION[map][1] * -1 + defs.MAP_SIZE[1]
      bg.paste(out, (x, y), img)
  bg.show()

if __name__ == '__main__':
  group_maps()
