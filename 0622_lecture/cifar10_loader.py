# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Routine for decoding the CIFAR-10 binary file format."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import pickle
import numpy as np

# Global constants describing the CIFAR-10 data set.
IMAGE_SIZE = 32
NUM_CLASSES = 10
NUM_TRAIN_EXAMPLES = 50000
NUM_TEST_EXAMPLES  = 10000

class CIFAR10_loader():
    def __init__(self):
        """ Initialize CIFAR-10 loader """
        
        # load training data
        self.train_images = np.zeros([NUM_TRAIN_EXAMPLES, IMAGE_SIZE, IMAGE_SIZE, 3], dtype=float)
        self.train_labels = np.zeros([NUM_TRAIN_EXAMPLES], dtype=int)
        begin = 0
        for i in range(5):
            with open('cifar10_data/cifar-10-batches-py/data_batch_%d' % (i+1), 'r') as file:
                loaded_data = pickle.load(file)
            images = loaded_data['data'].astype(float).reshape([-1, 3, IMAGE_SIZE, IMAGE_SIZE])
            labels = loaded_data['labels']
            self.train_images[begin:begin+len(labels)] = images.transpose([0, 2, 3, 1])
            self.train_labels[begin:begin+len(labels)] = np.asarray(labels, dtype=int)
            begin += len(labels)
        
        # load test data
        with open('cifar10_data/cifar-10-batches-py/test_batch', 'r') as file:
            loaded_data = pickle.load(file)
        self.test_images = loaded_data['data'].astype(float).reshape([-1, 3, IMAGE_SIZE, IMAGE_SIZE]).transpose([0,2,3,1])
        self.test_labels = np.asarray(loaded_data['labels'], dtype=int)        
        
        # setting iterator
        self.train_iterator = 0
        self.test_iterator = 0
        self.test_wrapped = False
        
    def _increment_iterator(self, batch_size, data_type):
        if data_type == 'train':
            self.train_iterator += batch_size
        else:
            self.test_iterator += batch_size
    
    def _discard_last_small_batch(self, batch_size, data_type):
        if data_type == 'train':
            if self.train_iterator + batch_size > NUM_TRAIN_EXAMPLES:
                self.train_iterator = 0
        else:
            self.test_wrapped = False
            if self.test_iterator + batch_size > NUM_TEST_EXAMPLES:
                self.test_iterator = 0
                self.test_wrapped = True
    
    def _prepro_images(self, images, shape=None):
        # normalize the images so that each element is
        # located from [0,255] to [0,1]
        return images / 255.0
    
    def get_num_train_examples(self):
        return NUM_TRAIN_EXAMPLES
    
    def get_num_test_examples(self):
        return NUM_TEST_EXAMPLES
    
    def get_image_size(self):
        return IMAGE_SIZE
    
    def get_num_classes(self):
        return NUM_CLASSES
        
    def get_batch(self, batch_size, data_type='train'):
        """ Get batch data """
        batch = {}
        
        self._discard_last_small_batch(batch_size, data_type)
        if data_type == 'test' and self.test_wrapped:    
            batch['wrapped'] = self.test_wrapped
            return batch
        
        # extract images and labels of batch size
        if data_type == 'train':
            begin = self.train_iterator
            end = self.train_iterator + batch_size
            batch_images = self.train_images[begin:end]
            batch_labels = self.train_labels[begin:end]
        else:
            begin = self.test_iterator
            end = self.test_iterator + batch_size
            batch_images = self.test_images[begin:end]
            batch_labels = self.test_labels[begin:end]
        batch_images = self._prepro_images(batch_images)
        
        batch['images'] = batch_images
        batch['labels'] = batch_labels
        if data_type == 'test': batch['wrapped'] = self.test_wrapped
        
        # increment the iterator
        self._increment_iterator(batch_size, data_type)
        
        return batch