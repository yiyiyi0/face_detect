from PIL import ImageDraw
from models import *
from ops import *
from dataset import FaceDetectSet, tensor2bbox
from torch.utils.data import DataLoader
import torch
from utils import progress_bar, nms
from torchvision import transforms as tfs
import matplotlib.pyplot as plt
import time
import math
import matplotlib.pyplot as plt
MODEL_SAVE_PATH = "./data/mssd_face_detect.pt"

def test():
    start_epoch = 0
    data_loader = DataLoader(dataset=FaceDetectSet(416, False, False), batch_size=1, shuffle=True, num_workers=1)
    use_cuda = torch.cuda.is_available()
    device = torch.device("cpu")
    model = MSSD().to(device)

    # load parameter
    state = torch.load(MODEL_SAVE_PATH)
    model.load_state_dict(state['net'])

    to_pil_img = tfs.ToPILImage()
    to_tensor = tfs.ToTensor()

    for i_batch, sample_batched in enumerate(data_loader):
        img_tensor = sample_batched[0].to(device)
        label_tensor = sample_batched[1].to(device)
        print("start inference")
        start = time.time()
        output = model(img_tensor)
        end = time.time()
        print("end inference, cost is: "+str(end-start))


        # save one pic and output
        pil_img = to_pil_img(sample_batched[0][0])
        print("start show1")
        bboxes = tensor2bbox(output[0], 416, [52, 26, 13], thresh=0.5)
        print("start show2")
        print(bboxes)
        #bboxes = nms(bboxes, 0.2, 0.3)
        #print(bboxes)
        print("get box num: "+str(len(bboxes)))
        draw = ImageDraw.Draw(pil_img)
        width = sample_batched[2][1][0].item()
        height = sample_batched[2][1][1].item()
        if width > height:
            scale_rate = 416.0 / width
            x_offset = 0
            y_offset = math.floor((416.0 - height * scale_rate) / 2)
        else:
            scale_rate = 416.0 / height
            x_offset = math.floor((416.0 - width * scale_rate) / 2)
            y_offset = 0
        for bbox in bboxes:
            bbox[1] = (bbox[1] - x_offset) / scale_rate
            bbox[2] = (bbox[2] - y_offset) / scale_rate
            bbox[3] = bbox[3] / scale_rate
            bbox[4] = bbox[4] / scale_rate
            # change format
            bbox[1] = bbox[1] - bbox[3] / 2
            bbox[2] = bbox[2] - bbox[4] / 2
            bbox[3] = bbox[1] + bbox[3] / 2
            bbox[4] = bbox[2] + bbox[4] / 2

        for bbox in bboxes:
            draw.rectangle((bbox[1] - bbox[3] / 2, bbox[2] - bbox[4] / 2, bbox[1] + bbox[3] / 2, bbox[2] + bbox[4] / 2),
                           outline=(0, 255, 0))
        print("start show")
        plt.imshow(pil_img)
        plt.show()
        print("end show")
        plt.close()

test()