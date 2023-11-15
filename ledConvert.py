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
signal_shape = 'A'

print(sys.argv)
print("hello")

# File names and settings
name = "triangle"
file = "triangle-10.mkv"
output = "triangle-10.mp4"
height = 50
width = 10
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
            print("C")
        case 'D':
            print("D")
        case 'X':
            print("X")
        case _:
            print("Signal shape error")        


if __name__ == "__main__":
    try:
        # Input stream
        input_stream = ffmpeg.input("inputVideos/{}".format(file))

        # Applying filters: resize and set FPS
        processed_video = input_stream.video.filter('scale', width, height).filter('fps', fps=fps)

        # Output stream (without audio)
        output_stream = ffmpeg.output(processed_video, "outputVideos/{}".format(output), an=None)

        # Running FFmpeg process
        ffmpeg.run(output_stream)

    except ffmpeg.Error as e:
        print("FFmpeg error:", e.stderr.decode())
    except Exception as e:
        print("Error:", e)

    #makes individual frame files
    ffmpeg.input("outputVideos/{}".format(output)).output('outputFrames/frame_%04d.png').run()


    #converting frame files to hex 
    frame_files = [f for f in os.listdir('outputFrames') if f.startswith('frame_') and f.endswith('.png')]
    frame_files.sort()  # Ensure the frames are in order


    led_data = []

    for frame_file in frame_files:
        with Image.open(os.path.join('outputFrames', frame_file)) as img:
            img = img.convert('RGB')
            width, height = img.size
            frame_data = []

            for y in range(height):
                for x in range(width):


                    r, g, b = img.getpixel((x, y))
                    hex_color = '0x{:02X}{:02X}{:02X}'.format(r, g, b)
                    frame_data.append(hex_color)

            led_data.append(frame_data)
        

    new_led_data = convert_to_signal_shape(led_data)

    #export led file
    with open('ledFile/{}.txt'.format(name), 'w') as file:
        json.dump(new_led_data, file)



