"""QuickNAT U-Net Architecture

This folder contains the Pytorch implementation of the core U-net architecture.
This arcitecture carries out segmentation of highly degenerated brains.

Usage:
    To use this module, import it and instantiate is as you wish:

        from quicknat import QuickNat
        deep_learning_model = QuickNAT(parameters)
"""

import numpy as np
import torch
import torch.nn as nn
from nn_common_modules import modules as sm
from squeeze_and_excitation import squeeze_and_excitation as se


class QuickNat(nn.Module):
    """Architecture class QuickNAT U-net.

    This class contains the pytorch implementation of the U-net architecture underpinning the Paint4Brains project.

    Args:
        parameters (dict): Contains information relevant parameters
        parameters = {'num_channels':1,
                        'num_filters':64,
                        'kernel_h':5,
                        'kernel_w':5,
                        'stride_conv':1,
                        'pool':2,
                        'stride_pool':2,
                        'num_classes':28
                        'se_block': False,
                        'drop_out':0.2}

    Returns:
        prediction (torch.tensor): Output forward passed tensor through the U-net block
    """

    def __init__(self, params):

        super(QuickNat, self).__init__()

        self.encode1 = sm.EncoderBlock(params, se_block_type=se.SELayer.CSSE)
        params['num_channels'] = 64
        self.encode2 = sm.EncoderBlock(params, se_block_type=se.SELayer.CSSE)
        self.encode3 = sm.EncoderBlock(params, se_block_type=se.SELayer.CSSE)
        self.encode4 = sm.EncoderBlock(params, se_block_type=se.SELayer.CSSE)
        self.bottleneck = sm.DenseBlock(params, se_block_type=se.SELayer.CSSE)
        params['num_channels'] = 128
        self.decode1 = sm.DecoderBlock(params, se_block_type=se.SELayer.CSSE)
        self.decode2 = sm.DecoderBlock(params, se_block_type=se.SELayer.CSSE)
        self.decode3 = sm.DecoderBlock(params, se_block_type=se.SELayer.CSSE)
        self.decode4 = sm.DecoderBlock(params, se_block_type=se.SELayer.CSSE)
        params['num_channels'] = 64
        self.classifier = sm.ClassifierBlock(params)

    def forward(self, input):
        """Forward pass for U-net

        Function computing the forward pass through the U-Net
        The input to the function is the dMRI map

        Args:
            input (torch.tensor): Input dMRI map, shape = (N x C x H x W) 

        Returns:
            prob (torch.tensor): Output forward passed tensor through the U-net block
        """
        e1, out1, ind1 = self.encode1.forward(input)
        e2, out2, ind2 = self.encode2.forward(e1)
        del e1
        e3, out3, ind3 = self.encode3.forward(e2)
        del e2
        e4, out4, ind4 = self.encode4.forward(e3)
        del e3

        bn = self.bottleneck.forward(e4)
        del e4

        d4 = self.decode4.forward(bn, out4, ind4)
        del bn, out4, ind4
        d3 = self.decode1.forward(d4, out3, ind3)
        del d4, out3, ind3
        d2 = self.decode2.forward(d3, out2, ind2)
        del d3, out2, ind2
        d1 = self.decode3.forward(d2, out1, ind1)
        del d2, out1, ind1
        prob = self.classifier.forward(d1)
        del d1
        return prob

    def enable_test_dropout(self):
        """ Dropout testing

        Enables test time drop out for uncertainity. This function is usefull if considering Bayesian Networks

        TODO: This function appears deprecated. Should be removed. 

        """
        attr_dict = self.__dict__['_modules']
        for i in range(1, 5):
            encode_block, decode_block = attr_dict['encode' +
                                                   str(i)], attr_dict['decode' + str(i)]
            encode_block.drop_out = encode_block.drop_out.apply(
                nn.Module.train)
            decode_block.drop_out = decode_block.drop_out.apply(
                nn.Module.train)

    @property
    def is_cuda(self):
        """Cuda Test

        This function tests if the model parameters are allocated to a CUDA enabled GPU.

        Returns:
            bool: Flag indicating True if the tensor is stored on the GPU and Flase otherwhise
        """
        return next(self.parameters()).is_cuda

    def save(self, path):
        """Model Saver

        Save model with its parameters to the given path. Conventionally the path should end with '*.model'.

        Args:
            path (str): Path string

        """
        print('Saving model... %s' % path)
        torch.save(self, path)

    def predict(self, X, device=0, enable_dropout=False, out_prob=False):
        """Post-training Output Prediction

        This function predicts the output of the of the U-net post-training

        Args:
            input (torch.tensor): input dMRI volume
            device (int/str): Device type used for training (int - GPU id, str- CPU)
            enable_dropout (bool): Flag for enabling dropout testing
            out_prob (bool): Flag for enabling the ouput of the different probabilities.

        Returns:
            prediction (ndarray): predicted output after training
        """
        self.eval()

        if type(X) is np.ndarray:
            X = torch.tensor(X, requires_grad=False).type(
                torch.HalfTensor).cuda(device, non_blocking=True)
        elif type(X) is torch.Tensor and not X.is_cuda:
            X = X.type(torch.HalfTensor).cuda(device, non_blocking=True)

        if enable_dropout:
            self.enable_test_dropout()

        with torch.no_grad():
            out = self.forward(X)
        del X
        if out_prob:
            return out
        else:
            max_val, idx = torch.max(out, 1)
            del max_val, out
            idx = idx.data.cpu().numpy()
            prediction = np.squeeze(idx)
            del idx
            return prediction
