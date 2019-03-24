import os
import numpy as np

from BagOfWords import BagOfWords


data_dir = 'data/'
# training
bow = BagOfWords(os.path.join(data_dir, 'train'))
# build dictionary
bow.build_dictionary()
# save dictionary
bow.save_dictionary(os.path.join(data_dir, 'dictionary.pkl'))

# transform free texts
train_X, train_y = bow.transform_data(os.path.join(data_dir, 'train'))
test_X, test_y = bow.transform_data(os.path.join(data_dir, 'test'))

# train the classification models