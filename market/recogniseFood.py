import numpy as np
import pandas as pd

 
# deep learning libraries
import tensorflow as tf
import keras

 
import cv2
from PIL import Image
from itertools import permutations
import os, torch
from transformers import ViTForImageClassification, ViTFeatureExtractor


############################## tensorflow model InceptionResnetV2 #######################################
# def recogniseFood(filename):

#     model = keras.models.load_model("market/static/files/1_2_3_4_5_Finalv1_53_no_val.h5")
#     labels=[]
#     with open('market/static/files/53food.txt') as f:
#         class_names = f.readlines()
#         for food in class_names:
#             labels.append(food.split("\n")[0])
        

#     foods = []
#     # Recognise food
#     for foodname in filename:

#         dir = 'market/static/uploads'
#         test_img_path = dir+"/"+foodname.filename

#         img0 = Image.open(test_img_path)
#         img = tf.keras.preprocessing.image.img_to_array(img0)
#         img = tf.keras.preprocessing.image.smart_resize(img, (331, 331))
#         img = tf.reshape(img, (-1, 331, 331, 3))
#         prediction = model.predict(img/255)
#         predictions = np.argmax(prediction)  
#         predicted_name=labels[predictions]
#         x=predicted_name.split('\n')
#         foods.append(x[0])

#     return foods

########################## pyTprch model Vision Transformer googlevit16#########################
def recogniseFood(filename):

    """### loading saved model"""

    # import our fine-tuned model
    model_name_or_path = 'market/static/files/vit/vitRigzin'
    model_finetuned = ViTForImageClassification.from_pretrained(model_name_or_path)
    # import features
    feature_extractor_finetuned = ViTFeatureExtractor.from_pretrained(model_name_or_path)

    labels=[]
    with open('market/static/files/53food.txt') as f:
        class_names = f.readlines()
        for items in class_names:
                labels.append(items.split("\n")[0])
    # with open('market/static/files/53food.txt') as f:
    #     class_names = f.readlines()
    foods = []
    # Recognise food
    for foodname in filename:

        dir = 'market/static/uploads'

        test_img_path = dir+"/"+foodname.filename

        img = Image.open(test_img_path)
        img = img.resize((200, 200))
        inputs = feature_extractor_finetuned(img, return_tensors="pt")

        with torch.no_grad():
            logits = model_finetuned(**inputs).logits

        predicted_label = logits.argmax(-1).item()
 

        max_value=logits[0][predicted_label]
        if max_value>=8.5:
            result = labels[predicted_label]
            foods.append(result)
        else:
            foods.append("food not found")

    return foods
