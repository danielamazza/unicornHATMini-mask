#!/usr/bin/env python3
from unicornhatmini import UnicornHATMini
import alsaaudio, audioop
import time
import random
from gpiozero import Button
from PIL import Image
import sys
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont

global buttonHasBeenPressed
buttonHasBeenPressed = False

if __name__ == "__main__":

  unicornhatmini = UnicornHATMini()
  rotation = 0
  if len(sys.argv) > 1:
      try:
          rotation = int(sys.argv[1])
      except ValueError:
          print("Usage: {} <rotation>".format(sys.argv[0]))
          sys.exit(1)
  unicornhatmini.set_rotation(rotation)
  display_width, display_height = unicornhatmini.get_shape()
  print("{}x{}".format(display_width, display_height))

  # Do not look at unicornhatmini with remaining eye
  unicornhatmini.set_brightness(0.1)

  # Load a nice 5x7 pixel font
  # Granted it's actually 5x8 for some reason :| but that doesn't matter
  font = ImageFont.truetype("5x7.ttf", 8)

  button_map = {5:("ADx", "Stai a un metro!"),
                6:("BDx","Ah ah ah !!!"),
                16:("ASx","NOOOOOOO!"),
                24:("BSx","Love! Love!!!" )}

  ### Button
  button_a = Button(5)
  button_b = Button(6)
  button_x = Button(16)
  button_y = Button(24)              

  def pressed(button):
    global buttonHasBeenPressed 
    buttonHasBeenPressed = True
    button_name, text = button_map[button.pin.number]
    print(f"Button {button_name} pressed!")
    text_width, text_height = font.getsize(text)
    image = Image.new('P', (text_width + display_width + display_width, display_height), 0)
    draw = ImageDraw.Draw(image)
    draw.text((display_width, -1), text, font=font, fill=255)
    offset_x = 0    
    for i in range(image.size[0]- display_width):
      for y in range(display_height):
        for x in range(display_width):
          hue = (time.time() / 10.0) + (x / float(display_width * 2))
          r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
          if image.getpixel((x + offset_x, y)) == 255:
            unicornhatmini.set_pixel(x, y, r, g, b)
          else:
            unicornhatmini.set_pixel(x, y, 0, 0, 0)
      offset_x += 1
      if offset_x + display_width > image.size[0]:
        offset_x = 0
      unicornhatmini.show()
      time.sleep(0.05)
      i += 1
    buttonHasBeenPressed = False




  card = 'sysdefault:CARD=Device'  # Microphone card (check with alsaaudio.cards())
  max_audioop  = 32754             # Max value

  granularity  = 512               # Granularity level


  # Initialize Alsa Audio
  inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, card)
  inp.setchannels(1)
  inp.setrate(8000)
  inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
  inp.setperiodsize(160)


  # Read From microphone
  try:
    button_a.when_pressed = pressed
    button_b.when_pressed = pressed
    button_x.when_pressed = pressed
    button_y.when_pressed = pressed

    while True:
      if not(buttonHasBeenPressed):
        l,data = inp.read()
        if l:
          # Avoid exceptions, audioop.error: not a whole number of frames 
          try:
            value = audioop.max(data, 2)
          except:
            continue
          else:
            sound_level = ((granularity * value)/max_audioop)
            # print(str(sound_level))
            offset_y = 0

            if sound_level <=10:
                image = Image.open("chiusa.png")
            elif sound_level <= 35:
                image = Image.open("apri1.png")
            elif sound_level <= 50:
                image = Image.open("apri2.png")
            else:
                image = Image.open("apri3.png")
            unicornhatmini.set_image(image, offset_y=offset_y, wrap=False)
            unicornhatmini.show()
            time.sleep(0.001)

  except (KeyboardInterrupt, SystemExit):

    # Clean screen
    image = Image.open("nero.png")
    unicornhatmini.set_image(image, offset_y=0, wrap=False)
    unicornhatmini.show()

    button_a.close()
    button_b.close()
    button_x.close()
    button_y.close()