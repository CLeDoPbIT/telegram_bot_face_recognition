from __future__ import print_function, division
import sys
#C:/Users/User/Documents/Py projects/bot_plays
PYSOLR_PATH = "../bot_plays"
if not PYSOLR_PATH in sys.path:
    sys.path.append(PYSOLR_PATH)

## обернуть все в функцию, чтобы просто импортнуть эту грязь в боте и юзать через импорт


import tensorflow as tf
import numpy as np
import facenet1
import warnings
import detect_face1
import cv2
import argparse
import os
import os.path
import itertools
import six.moves as sm
import re
from collections import defaultdict
import PIL.Image
import imutils
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO


#images
import imutils
import imgaug as ia
from imgaug import augmenters as iaa
from scipy import ndimage, misc
from skimage import data

from sklearn.svm import LinearSVC, SVC

from sklearn.preprocessing import LabelEncoder

from sklearn.externals import joblib


## PATHS
#'C:/Users/User/Documents/Py projects/bot_plays/svm_model.sav'
#'C:/Users/User/Documents/Py projects/bot_plays/women_encoder_classes.npy'
#'C:/Users/User/Documents/Py projects/bot_plays/20170512-110547/20170512-110547.pb'
#'C:/Users/User/Documents/Py projects/bot_plays/align'
saved_SVM_weights = '../bot_plays/svm_model.sav'
saved_encoder_classes_path = '../bot_plays/women_encoder_classes.npy'
face_net_prep_path = '../bot_plays/20170512-110547/20170512-110547.pb'
detect_face_prep_path = '../bot_plays/align'

## METADATA
class IdentityMetadata():
    def __init__(self, base, name, file):
        # dataset base directory
        self.base = base
        # identity name
        self.name = name
        # image file name
        self.file = file

    def __repr__(self):
        return self.image_path()

    def image_path(self):
        return os.path.join(self.base, self.name, self.file) 
    
### ==========================================================FUNCTIONS

def getFace(img):
    img_size = np.asarray(img.shape)[0:2]
    bounding_boxes = []
    _ = []
    faces = None
    minsize = 20
    threshold = [0.6, 0.7, 0.7]
    factor = 0.709
    margin = 44
    input_image_size = 160
    bounding_boxes, _ = detect_face1.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
    if not len(bounding_boxes) == 0:
        for face in bounding_boxes:
            if face[4] > 0.50:
                det = np.squeeze(face[0:4])
                bb = np.zeros(4, dtype=np.int32)
                bb[0] = np.maximum(det[0] - margin / 2, 0)
                bb[1] = np.maximum(det[1] - margin / 2, 0)
                bb[2] = np.minimum(det[2] + margin / 2, img_size[1])
                bb[3] = np.minimum(det[3] + margin / 2, img_size[0])
                cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
                resized = cv2.resize(cropped, (input_image_size,input_image_size),interpolation=cv2.INTER_CUBIC)
                prewhitened = facenet1.prewhiten(resized)
                faces = getEmbedding(prewhitened)[0]
    return faces

  
def load_image(path):
    img = cv2.imread(path, 1)
    # OpenCV loads images with color channels
    # in BGR order. So we need to reverse them
    return img[...,::-1]
  
def getEmbedding(resized):
    reshaped = resized.reshape(-1,input_image_size,input_image_size,3)
    feed_dict = {images_placeholder: reshaped, phase_train_placeholder: False}
    embedding = sess.run(embeddings, feed_dict=feed_dict)
    return embedding
    
def load_metadata(path):
    metadata = []
    for i in os.listdir(path):
        for f in os.listdir(os.path.join(path, i)):
            metadata.append(IdentityMetadata(path, i, f))
    return np.array(metadata)

### ===========================================================PLOTING
def load_metadata_exp(path):
    metadata = []
    for i in os.listdir(path):
        metadata.append(os.path.join(path, i))
    return np.array(metadata)
  
# some global vars
minsize = 20
threshold = [0.6, 0.7, 0.7]
factor = 0.709
margin = 44
input_image_size = 160

# tf session start
sess = tf.Session()

# read pnet, rnet, onet models from align directory and files are det1.npy, det2.npy, det3.npy
pnet, rnet, onet = detect_face1.create_mtcnn(sess, detect_face_prep_path) #'drive/face2/align')

# read 20170512-110547 model file downloaded from https://drive.google.com/file/d/0B5MzpY9kBtDVZ2RpVDYwWmxoSUk
facenet1.load_model(face_net_prep_path) #"drive/face2/20170512-110547/20170512-110547.pb")

# Get input and output tensors
images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
embedding_size = embeddings.get_shape()[1]

# load prelearned svm
SVM = joblib.load(saved_SVM_weights)

## ================== SVC predict
# answ photos
meta_exp = load_metadata_exp('C:/Users/User/Documents/Py projects/bot_plays/Women_ans')
warnings.filterwarnings('ignore')


encoder = LabelEncoder()
encoder.classes_ = joblib.load(saved_encoder_classes_path)

def class_detector(image):
    resized_image = imutils.resize(image,width=1000) #Картинка для поиска
    face = getFace(resized_image)
    if not face is None:  
        prediction = SVM.predict([face])
        identity = encoder.inverse_transform(prediction)[0]


        for i in meta_exp:
            if( identity == i.rpartition('/')[2].partition('.')[0]):
                good_image = i
                break

        good_image_load = load_image(good_image)
        #plt.imshow(good_image_load)
        answer = ("You Recognized as " + example_identity, good_image_load)
    else:
        answer = "Unfortunatly, I think there are no faces! Could You give me another photo?"
    return answer

