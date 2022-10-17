from PIL import Image, ImageDraw, ImageFont
from testRequest import read
import defs

def updateMap(map, data, index):
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
          img_w = img_w * 2 // 4
          img_h = img_h * 2 // 4
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
    myFont = ImageFont.truetype(defs.PATH + '/data/Clarendon.ttf', 23) 

    for item in data['mapTextItems']:
      if item['mapMarkerType'] == 'Major':
        x = round(item['x'] * bg_w)
        y = round(item['y'] * bg_h)
        text = item['text']

        size = draw.textsize(text, font=myFont)
        x = x - size[0]/2
        y = y - size[1]/2

        c = (0, 0, 0, 100)
        draw.text((x-1, y-1), text, font=myFont, fill=c)
        draw.text((x+1, y-1), text, font=myFont, fill=c)
        draw.text((x-1, y+1), text, font=myFont, fill=c)
        draw.text((x+1, y+1), text, font=myFont, fill=c)
        draw.text((x, y), text, fill=(255, 255, 255, 100), font=myFont)

    background = Image.alpha_composite(background, txt)

    background.save(defs.DB['mapImage'].format(map))
    print(map + " updated")


    
def changeColor(img, color):
	if color:
		color = (101, 135, 94)
	else:
		color = (45, 108, 161)

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


def highlight_name(map, name):
  with Image.open(defs.PATH + defs.DB['mapImage'].format(map)) as img:
    bg_w, bg_h = img.size
    txt = Image.new('RGBA', background.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt)
    myFont = ImageFont.truetype(defs.PATH + '/data/Clarendon.ttf', 25)
    draw = ImageDraw.Draw(txt)

    data = read(defs.DB['mapData'].format(map))['mapTextItems']
    x = round(data['x'] * bg_w)
    y = round(data['y'] * bg_h)
    size = draw.textsize(name, font=myFont)
    x = x - size[0]/2
    y = y - size[1]/2

    c = (0, 0, 0, 0)
    draw.text((x-1, y-1), name, font=myFont, fill=c)
    draw.text((x+1, y-1), name, font=myFont, fill=c)
    draw.text((x-1, y+1), name, font=myFont, fill=c)
    draw.text((x+1, y+1), name, font=myFont, fill=c)
    draw.text((x, y), name, fill=(255, 255, 255, 255), font=myFont)

    background = Image.alpha_composite(img, txt)

  return background