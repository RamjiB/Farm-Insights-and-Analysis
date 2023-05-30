import os
from utils import networks
import torch
from PIL import Image
from torchvision import transforms
import numpy as np
import cv2

class RGB_TO_NDVI_MODEL:
    """load pix2pixHD model and do prediction"""
    def __init__(self, model_path, network="global"):
        self.model_path = model_path
        self.netG = network
        self.load_model()
        
    def load_model(self):
        ##load model
        netG = self.netG
        input_nc = 3
        output_nc = 1
        ngf = 16
        norm = "batch"

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #self.device = torch.device("cpu")
        gpu_ids = []
        if self.device.type == "cuda":
            gpu_ids = [0]

        self.model = networks.define_G(
            input_nc,
            output_nc,
            ngf,
            netG,
            n_downsample_global=2,
            n_blocks_global=2,
            n_blocks_local=3,
            gpu_ids=gpu_ids,
        )

        state_dict = torch.load(self.model_path, map_location=self.device)

        if hasattr(state_dict, "_metadata"):
            del state_dict._metadata

        # patch InstanceNorm checkpoints prior to 0.4
        for key in list(
            state_dict.keys()
        ):  # need to copy keys here because we mutate in loop
            self.__patch_instance_norm_state_dict(
                state_dict, self.model, key.split(".")
            )

        self.model.load_state_dict(state_dict)
        self.model.eval()
        
    def __patch_instance_norm_state_dict(self, state_dict, module, keys, i=0):
        """Fix InstanceNorm checkpoints incompatibility (prior to 0.4)"""
        key = keys[i]
        if i + 1 == len(keys):  # at the end, pointing to a parameter/buffer
            if module.__class__.__name__.startswith("InstanceNorm") and (
                key == "running_mean" or key == "running_var"
            ):
                if getattr(module, key) is None:
                    state_dict.pop(".".join(keys))
            if module.__class__.__name__.startswith("InstanceNorm") and (
                key == "num_batches_tracked"
            ):
                state_dict.pop(".".join(keys))
        else:
            self.__patch_instance_norm_state_dict(
                state_dict, getattr(module, key), keys, i + 1
            )

def preprocessing(img):
    method = Image.BICUBIC
    img_transforms = transforms.Compose(
         [   transforms.Resize((256,256)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ]
    )
    image_tensor = img_transforms(img).float()
    image_tensor = image_tensor.unsqueeze_(0)
    return image_tensor

def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()

def rgb_to_nir(image_path, model):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    img=Image.open(image_path)
    red_channel_image = np.asarray(img)[:,:,0]
    img1=preprocessing(img)
    generated_nir_band = model.model(img1.to(device))
    generated_nir_band = generated_nir_band.squeeze()
    generated_nir_band = to_numpy(generated_nir_band)
    generated_nir_band = 255 * (generated_nir_band+1)/2
    return generated_nir_band, red_channel_image, np.asarray(img).shape[:2]