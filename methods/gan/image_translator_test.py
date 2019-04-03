#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Donny You (youansheng@gmail.com)
# Class Definition for GAN.


import os
import torch

from methods.tools.blob_helper import BlobHelper
from methods.tools.runner_helper import RunnerHelper
from models.gan.model_manager import ModelManager
from datasets.test.test_data_loader import TestDataLoader
from utils.helpers.dc_helper import DCHelper
from utils.helpers.image_helper import ImageHelper
from utils.tools.logger import Logger as Log


class ImageTranslatorTest(object):
    def __init__(self, configer):
        self.configer = configer
        self.blob_helper = BlobHelper(configer)
        self.model_manager = ModelManager(configer)
        self.test_loader = TestDataLoader(configer)
        self.device = torch.device('cpu' if self.configer.get('gpu') is None else 'cuda')
        self.gan_net = None

        self._init_model()

    def _init_model(self):
        self.gan_net = self.model_manager.gan_model()
        self.gan_net = RunnerHelper.load_net(self, self.gan_net)
        self.gan_net.eval()

    def test(self, test_dir, out_dir):
        if self.configer.exists('test', 'mode') and self.configer.get('test', 'mode') == 'nir2vis':
            jsonA_path = os.path.join(test_dir, 'val_label{}A.json'.format(self.configer.get('data', 'tag')))
            test_loader_A = self.test_loader.get_testloader(json_path=jsonA_path) if os.path.exists(jsonA_path) else None
            jsonB_path = os.path.join(test_dir, 'val_label{}B.json'.format(self.configer.get('data', 'tag')))
            test_loader_B = self.test_loader.get_testloader(json_path=jsonB_path) if os.path.exists(jsonB_path) else None
        elif self.configer.exists('test', 'mode') and self.configer.get('test', 'mode') == 'pix2pix':
            imgA_dir = os.path.join(test_dir, 'imageA')
            test_loader_A = self.test_loader.get_testloader(test_dir=imgA_dir) if os.path.exists(imgA_dir) else None
            test_loader_B = None
        else:
            imgA_dir = os.path.join(test_dir, 'imageA')
            test_loader_A = self.test_loader.get_testloader(test_dir=imgA_dir) if os.path.exists(imgA_dir) else None
            imgB_dir = os.path.join(test_dir, 'imageB')
            test_loader_B = self.test_loader.get_testloader(test_dir=imgB_dir) if os.path.exists(imgB_dir) else None

        if test_loader_A is not None:
            for data_dict in test_loader_A:
                new_data_dict = dict(imgA=data_dict['img'])
                with torch.no_grad():
                    out_dict = self.gan_net(new_data_dict, testing=True)

                meta_list = DCHelper.tolist(data_dict['meta'])
                for key, value in out_dict.items():
                    for i in range(len(value)):
                        img_bgr = self.blob_helper.tensor2bgr(value[i])
                        img_path = meta_list[i]['img_path']
                        Log.info('Image Path: {}'.format(img_path))
                        # filename = '_'.join(img_path.rstrip().split('/')[-2:])
                        img_bgr = ImageHelper.resize(img_bgr,
                                                     target_size=self.configer.get('test', 'out_size'),
                                                     interpolation='linear')
                        ImageHelper.save(img_bgr, os.path.join(out_dir, key, '{}.jpg'.format(meta_list[i]['filename'])))

        if test_loader_B is not None:
            for data_dict in test_loader_B:
                new_data_dict = dict(imgB=data_dict['img'])
                with torch.no_grad():
                    out_dict = self.gan_net(new_data_dict, testing=True)
                meta_list = DCHelper.tolist(data_dict['meta'])
                for key, value in out_dict.items():
                    for i in range(len(value)):
                        img_bgr = self.blob_helper.tensor2bgr(value[i])
                        img_path = meta_list[i]['img_path']
                        Log.info('Image Path: {}'.format(img_path))
                        # filename = img_path.rstrip().split('/')[-1]
                        # filename = '_'.join(img_path.rstrip().split('/')[-2:])
                        img_bgr = ImageHelper.resize(img_bgr,
                                                     target_size=self.configer.get('test', 'out_size'),
                                                     interpolation='linear')
                        ImageHelper.save(img_bgr, os.path.join(out_dir, key, '.jpg'.format(meta_list[i]['filename'])))
