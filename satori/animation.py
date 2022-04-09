import os
import sys
import datetime
import random
import itertools
from matplotlib import cm
import PIL.Image as Image
import numpy as np
import torch
import librosa
from tqdm import tqdm
import cv2
from common import device
from common import FRAME_RATE
from torch import Tensor

animator = __import__('talkinghead')


poser = animator.create_poser(device)
pose_parameters = animator.get_pose_parameters()
pose_size = poser.get_num_parameters()


def load_avatar_image(path):
    """ Given path to RGBA avatar base image, return image as torch tensor """
    image = Image.open(path)
    image = animator.resize_PIL_image(image)
    assert image.mode == 'RGBA', \
        'Only RGBA images work as the base avatar image!'
    return animator.extract_pytorch_image_from_PIL_image(image).to(device)


def animate(avatar_image, parameter_mappings):
    """ Given the base image of the character to be animated and face animation
        parameters, return morphed image of base image according to parameters

        For parameters, see sources:
            talkinghead/tha2/poser/modes/mode_20.py:get_pose_parameters()
            talkinghead/tha2/poser/poser.py

        Args:
            avatar_base_image: RGBA base avatar torch image
            parameter_mappings: dict of parameters
        Returns:
            RGBA morphed torch image
    """
    pose = torch.zeros(1, pose_size)
    for name, value in parameter_mappings.items():
        index = pose_parameters.get_parameter_index(name)
        pose[0, index] = value
    pose = pose.to(device)
    return poser.pose(avatar_image, pose)[0]

def generate_head_trajectory(n_frames, audio, sr):
    """ Given number of frames, generate the head trajectory:

        Effect                           | Parameters involved
        ---------------------------------+---------------------------------
        Blinking                         | eye_wink_left, eye_wink_right
        Head rotation along x, y, z axis | head_z, head_y, head_z
    """
    blink_frames = 10 # 30 fps
    blink_frames_between = 170
    blink_values = []
    index = 0
    while index < n_frames:
        blink_len = random.randint(blink_frames - 2, \
                                   blink_frames + 2)
        transition = np.linspace(0, 1, blink_len // 2 + 1)
        blink_values.extend(transition.tolist())
        blink_values.extend((1 - transition).tolist())
        skip_len = random.randint(blink_frames_between - 10, \
                                  blink_frames_between + 10)
        blink_values.extend(np.zeros(skip_len).tolist())
        index += skip_len

    def head_axis_motion(axis_limit):
        values = [0]
        index = 0
        while index < n_frames:
            motion_mag = 2 * (random.random() - 0.5) * axis_limit
            motion_len = random.randint(40, 120)
            values.extend(np.linspace(values[-1], motion_mag, motion_len))
            index += motion_len
        return values

    # x, y, z, respectively
    head_motion = list(zip(head_axis_motion(0.5),
                           head_axis_motion(0.5),
                           head_axis_motion(0.75)))

    # mouth motion
    samples_per_frame = len(audio) // n_frames
    average_amps = []
    for i in range(n_frames):
        start_index = i * samples_per_frame
        end_index = (i + 1) * samples_per_frame
        audio_frame = audio[start_index:end_index]
        average_amps.append(np.mean(np.absolute(audio_frame)))
    max_amp = np.max(average_amps)
    mouth_motion = np.array([amp / max_amp for amp in average_amps])


    trajectory = []
    for i in range(n_frames):
        trajectory.append({
            'eye_wink_left' : blink_values[i],
            'eye_wink_right': blink_values[i],
            'head_x': head_motion[i][0],
            'head_y': head_motion[i][1],
            'neck_z': head_motion[i][2],
            'mouth_aaa': mouth_motion[i].item(),
        })
    return trajectory


def generate_unsynced_video(avatar_base_image, video_path, audio_path, background_image):
    """
    Audio_path is already a wav file
    Write to video_path
    """
    # 1. count number of video frames
    audio, sr = librosa.load(audio_path)
    n_frames = int(len(audio) * FRAME_RATE / sr)

    # 2. generate a head trajectory dictionary
    trajectory = generate_head_trajectory(n_frames, audio, sr)

    # 3. generate images for each from from the head
    # 4. stitch images together into video, write to video_path trajectory
    sample = animate(avatar_base_image, trajectory[0])
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), \
                            FRAME_RATE, (sample.shape[2], sample.shape[1]))
    for i, traj in enumerate(tqdm(trajectory)):
        if i % 100 == 0:
            print(i)
        #if i == 900:
        #    break
        image = animate(avatar_base_image, traj).detach().cpu()
        #print(image.shape, image.dtype)
        image = animator.convert_output_image_from_torch_to_numpy(image)
        #assert image.shape[-1] == 4
        #print(image[:,:,:3].max(), image[:,:,3].max())
        image = image[:, :, 0:3] * (image[:, :, 3:4]) + (1 - image[:, :, 3:4]) * background_image
        image = (image * 255).astype(np.uint8)
        image = image[:, :, ::-1]
        out.write(image)
    out.release()


def add_lip_sync(video_path, audio_path):
    """
    read video_path, audio_path
    run wav2lip
    """
    #video =
    pass


def main():
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')

    #avatar_image = load_avatar_image('talkinghead/avatar_images/reporter_female.png')
    #print(avatar_image.shape)
    #trajectory = generate_head_trajectory(1000)
    #morphed_avatar_image = animate(avatar_image, trajectory[7])
    #animator.save_pytorch_image(morphed_avatar_image, 'data/test.png')

    # test if animate works first

    # dont forget to run setup.sh which sets up talkinghead and wav2lip (untested)
    # work on satori using git
    # [datetime] is datetime string from datatime
    # read this first then read doc strings

    # generate some frames using head trajectory
    # frame len depends on audio len, but we want 30 fps or whatever matches lipgan (see common.py)
    # call animate on these on these frames to get the images
    # can directly pass dict into animate so dont worry about the parameters in talkinghead unless u want to add more later
    # stitch images together at lipgan fps into mp3 (remember the output is rgba; change to rgb if needed?)
    # save mp3 at data/[datetime]/unsynced.mp4
    avatar_image = load_avatar_image('talkinghead/avatar_images/reporter_female.png')
    background_image = cv2.resize(np.array(Image.open('data/cityscape.jpg')) / 255, (256,256))
    generate_unsynced_video(avatar_image, 'data/test.mp4', 'data/test.mp3', background_image)

    # get audio generated as wav from data/[datetime]/audio.wav
    # next run lipgan and save to data/[datetime]/synced.mp4
    # for lipgan see https://colab.research.google.com/drive/1tZpDWXz49W6wDcTprANRGLo2D_EbD5J8?usp=sharing#scrollTo=KoVGMtjRZfeR
    # you will need to use the subprocess module to launch a python script as required in lipgan

    # done :)

if __name__ == '__main__':
    main()
