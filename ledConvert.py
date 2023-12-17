import sys
import os
from PIL import Image
import ffmpeg
import json
import copy

#TODO
#create folder auto if not if not os.path.exists('frames'): os.makedirs('frames')
#signal wiring shape

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
name = "candle"
file = "{}.mkv".format(name)
output = "{}.mp4".format(name)
height = 50
width = 14
fps = 5

# TODO: Implement other signal shape conversions
def convert_to_signal_shape(led_data):
    print("Converting to signal layout {}".format(signal_shape))
    match signal_shape:
        case 'A':
            transformed_led_data = []
            for frame in led_data:
                transformed_frame = [None] * len(frame)
                for pixel_number, pixel in enumerate(frame):
                    new_pixel_number = get_new_pixel_number_A(pixel_number, width, height)
                    transformed_frame[new_pixel_number] = pixel
                transformed_led_data.append(transformed_frame)
            return transformed_led_data
            
        case 'B':
             print("Signal shape error")  
        case 'C':
            print("Signal shape error")  
        case 'D':
            print("Signal shape error")  
        case 'X':
            print("Signal shape error")  
        case _:
            print("Signal shape error")        

def get_new_pixel_number_A(old_number, width, height):
    column_number = (old_number % width) + 1
    row_number = (old_number // width) + 1
                
    if(column_number % 2 == 0):
        return ((column_number - 1) * height) + (row_number - 1)
    else:
        return (column_number * height) - row_number


if __name__ == "__main__":
    try:
        # Input stream
        input_stream = ffmpeg.input("inputVideos/{}".format(file))

        # Applying filters: resize and set FPS
        processed_video = (
            input_stream.video
            .filter('scale', width, height)
            .filter('fps', fps=fps)
            .filter('unsharp', luma_msize_x=7, luma_msize_y=7, luma_amount=2.5)
        )

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

    #converting frame files to RGB
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

                    # Leading zeros added to keep the number of bits the same when reading
                    reformat =  '{:03d},{:03d},{:03d}'.format(r, g, b)
                    frame_data.append(reformat)

            led_data.append(frame_data)
          

    new_led_data = convert_to_signal_shape(led_data)

    #export led file
    with open('ledFile/{}.txt'.format(name), 'w') as file:
        json.dump(new_led_data, file)




