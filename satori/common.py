""" Put all shared variables here """
import torch

FRAME_RATE = 30.0
AUDIO_RATE = 100.0 # Jinha u can change this
DEVICE_NAME = 'cuda' if torch.cuda.is_available() else 'cpu'
device = torch.device(DEVICE_NAME)

IMAGE_SIZE_DISPLAY = (256, 256)
