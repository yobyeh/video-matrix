import sys
import os
from PIL import Image
import ffmpeg
import json
import copy

#TODO
#create folder auto if not if not os.path.exists('frames'): os.makedirs('frames')
#signal wiring shape

#frame 6000 bytes
#10 frame 

#signal wiring shapes
#start bottom left going up zigzag  'A'
#start top left going down zigzag   'B'
#start bottom right going up zigzag 'C'
#start top right going down zigzag  'D'
#leave as default processed layout  'X'
signal_shape = 'C'

print(sys.argv)
print("hello")

# File names and settings
name = "static"
starts_with = "s"
frame_type = "tif"
format = "gif"
file = "{}.{}".format(name, format)
output = "{}.mp4".format(name)
height = 50
width = 14
fps = 5

def convert_to_signal_shape(led_data):
    print("Converting to signal layout {}".format(signal_shape))

    match signal_shape:
        case 'A':
            transformed_led_data = []
            for frame in led_data:
                new_frame = [None] * len(frame)
                for pixel_number, pixel in enumerate(frame):
                    x = pixel_number % width
                    y = pixel_number // width

                    # Reverse the order for odd rows
                    if y % 2 != 0:
                        x = width - 1 - x

                    # Start from the bottom left
                    new_y = height - 1 - y
                    new_index = new_y * width + x
                    new_frame[new_index] = pixel

                transformed_led_data.append(new_frame)
            return transformed_led_data
            
        case 'B':
            transformed_led_data = []
            for frame in led_data:
                new_frame = copy.deepcopy(frame)
                pixel_count = 0
                counter = height
                row_count = 0
                odd_peak = 0
                even_peak = -1

                #add to correct location in new frame
                for pixel in frame:
                    if(pixel_count != 0 and pixel_count % width == 0):
                        row_count += 1
                        odd_peak += 1
                        even_peak -= 1
                    odd_row = row_count % 2 != 0

                    if(odd_row):
                        new_frame[counter + odd_peak] = pixel
                        counter = counter + (height * 2)

                    else:   
                        new_frame[counter + even_peak] = pixel

                    pixel_count += 1

                transformed_led_data.append(new_frame)
            return transformed_led_data
        case 'C':
            transformed_led_data = []
            for frame in led_data:
                transformed_frame = [None] * len(frame)
                for pixel_number, pixel in enumerate(frame):
                    new_pixel_number = get_new_pixel_number(pixel_number, width, height)
                    transformed_frame[new_pixel_number] = pixel
                transformed_led_data.append(transformed_frame)
            return transformed_led_data
        case 'D':
            print("D")
        case 'X':
            print("X")
        case _:
            print("Signal shape error")        

def get_new_pixel_number(old_number, width, height):
    column_number = (old_number % width) + 1
    row_number = (old_number // width) + 1
                
    if(column_number % 2 == 0):
        return ((column_number - 1) * height) + (row_number - 1)
    else:
        return (column_number * height) - row_number


if __name__ == "__main__":
   
    #converting frame files
    frame_files = [f for f in os.listdir('outputFrames') if f.startswith(starts_with) and f.endswith(frame_type)]
    frame_files.sort()  # Ensure the frames are in order


    led_data = []

    for frame_file in frame_files:
        with Image.open(os.path.join('outputFrames', frame_file)) as img:
            img = img.convert('RGB')
            width, height = img.size
            frame_data = []

            for y in range(height):
                for x in range(width):

                    #switched from hex to rgb had to add leading zeros to keep same number of bits
                    r, g, b = img.getpixel((x, y))
                    reformat =  '{:03d},{:03d},{:03d}'.format(r, g, b)
                    #hex_color = '0x{:02X}{:02X}{:02X}'.format(r, g, b)
                    frame_data.append(reformat)

            led_data.append(frame_data)
          

    new_led_data = convert_to_signal_shape(led_data)

    #export led file
    with open('ledFile/{}.txt'.format(name), 'w') as file:
        json.dump(new_led_data, file)

