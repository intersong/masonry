from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.callbacks import ModelCheckpoint, TensorBoard
from keras.utils import np_utils
from keras.optimizers import Adam
from keras import backend as K
import tensorflow as tf
from sklearn.model_selection import StratifiedKFold
import numpy as np
from PIL import Image
import glob
import os

def load_data(data_dir):
    img_width, img_height = 150, 150

    data_dir = os.path.expanduser(data_dir)

    label_names = []                  
    for r, d, files in os.walk(data_dir):
        for i in range(len(d)):
            label_names.append(d[i])

    sub_dirs = [x[0] for x in os.walk(data_dir)]
    dir_names = [os.path.basename(sub_dir) for sub_dir in sub_dirs]

    file_glob = [os.path.join(data_dir, dir_name, '*.jpeg') for dir_name in dir_names]
    
    file_list = []
    for i in range(1,len(file_glob)):
        file_list.extend(glob.glob(file_glob[i]))
    
    label_strings = [os.path.basename(os.path.dirname(file)) for file in file_list]

    labels = []
    for l in label_strings:
        if l == label_names[0]:
            labels.append(0)
        elif l == label_names[1]:
            labels.append(1)
        elif l == label_names[2]:
            labels.append(2)
        elif l == label_names[3]:
            labels.append(3)
        elif l == label_names[4]:
            labels.append(4)
        elif l == label_names[5]:
            labels.append(5)
        elif l == label_names[6]:
            labels.append(6)
        else:
            labels.append(7)
    
    data = []
    for file in file_list:
        img = load_img(file)
        x = img_to_array(img, data_format='channels_last')
        data.append(x)
    
    data = np.asarray(data)/255.
    labels = np.asarray(labels)
    return data, labels

def create_model():
    input_shape = (img_width, img_height, 3)
    model = Sequential()
    model.add(Conv2D(32, (3, 3), input_shape=input_shape))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(128))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(8))
    model.add(Activation('sigmoid'))
    
    optimizer = Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.1)

    model.compile(loss='binary_crossentropy',
                  optimizer=optimizer,
                  metrics=['accuracy'])

    return model

def train_eval_model(model, training_data, training_labels, test_data, test_labels, callbacks):
    validation_data = (test_data, test_labels)
    model.fit(
        training_data,
        training_labels,
        batch_size = 32,
        epochs = 10,
        validation_data = validation_data,
        callback = callbacks)
    
if __name__ == "__main__":
    img_width, img_height = 150, 150
    data_dir = '~/img_lib_150'
    n_folds = 10
    data, labels = load_data(data_dir)
    skf = StratifiedKFold(n_splits=10, shuffle=True)
    skf.get_n_splits(data, labels)

    for train, test in skf.split(data, labels):
        X_train, X_test = data[train], data[test]
        y_train, y_test = labels[train], labels[test]
        y_train, y_test = np_utils.to_categorical(y_train), np_utils.to_categorical(y_test)
        model = None # Clearing the NN.
        model = create_model()
        # checkpoint
        filepath="weights-improvement-{epoch:02d}-{val_acc:.2f}.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
        tbcall = TensorBoard(log_dir='./logs', histogram_freq=1, batch_size=32, write_graph=True)
        callbacks_list = [checkpoint, tbcall]
        train_eval_model(model, X_train, y_train, X_test, y_test, callbacks_list)