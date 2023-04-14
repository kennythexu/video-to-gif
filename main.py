import os
import cv2
import numpy as np
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageOps, ImageSequence
from pygifsicle import optimize


def round_corners(image, radius):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)

    alpha = Image.new('L', image.size, 255)
    w, h = image.size

    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))

    image.putalpha(alpha)
    return image


def convert_to_transparent_gif(input_path, output_path, corner_radius=20):
    clip = VideoFileClip(input_path)
    clip = clip.resize(height=512)  # Increase the resolution
    frames = [Image.fromarray(cv2.cvtColor(np.array(frame), cv2.COLOR_BGR2RGBA)) for frame in clip.iter_frames()]

    rounded_frames = [round_corners(frame, corner_radius) for frame in frames]

    output_gif = os.path.join(output_path, os.path.splitext(os.path.basename(input_path))[0] + '.gif')

    # Save the GIF using the PIL library with improved quality
    rounded_frames[0].save(output_gif, format='GIF', save_all=True, append_images=rounded_frames[1:], duration=int(1000/clip.fps), loop=0, disposal=2, transparency=0)

    # Optimize the GIF using pygifsicle
    optimize(output_gif, output_gif, options=["--lossy=1"])


def process_videos(input_folder, output_folder, corner_radius=20):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.mp4'):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, input_folder)
                output_subfolder = os.path.join(output_folder, relative_path)

                if not os.path.exists(output_subfolder):
                    os.makedirs(output_subfolder)

                convert_to_transparent_gif(input_path, output_subfolder, corner_radius)


if __name__ == '__main__':
    input_folder = '/Users/kennyxu/PycharmProjects/video-to-gif/creative'
    output_folder = '/Users/kennyxu/PycharmProjects/video-to-gif/output'
    corner_radius = 20
    process_videos(input_folder, output_folder, corner_radius)
