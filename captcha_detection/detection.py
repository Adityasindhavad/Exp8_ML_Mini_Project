import numpy as np
import cv2
from imutils import paths
import os
import os.path
#if tensorflow and keras are installed then ignore the tensorflow.keras.models importing error. 
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split

def keras_detection_model(filename):
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.copyMakeBorder(gray, 8, 8, 8, 8, cv2.BORDER_REPLICATE)
    thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV, cv2.THRESH_OTSU)[1]
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
    letter_image_regions = []

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        if w / h > 1.25:
            half_width = int(w / 2)
            letter_image_regions.append((x, y, half_width, h))
            letter_image_regions.append((x + half_width, y, half_width, h))
        else:
            letter_image_regions.append((x, y, w, h))
                
    letter_image_regions = sorted(letter_image_regions, key=lambda x: x[0])

    output = cv2.merge([gray] * 3)
    predictions = []
    predictions = []


    #-----------------------------------------FOR THE LabelBinarizer-------------------------------------------------------------


    letter_folder = 'captcha_detection\extracted_letters'
    data = []
    labels = []
    for image in paths.list_images(letter_folder):
        img = cv2.imread(image)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, (30,30))
        img = np.expand_dims(img, axis = 2)
        label = image.split(os.path.sep)[-2]
        data.append(img)
        labels.append(label)


    data = np.array(data, dtype = "float")

    labels = np.array(labels)

    data = data/255.0
    (train_x, val_x, train_y, val_y) = train_test_split(data, labels, test_size=0.2, random_state=0)


    #one hot encoding

    lb = LabelBinarizer().fit(train_y)

    #loading model
    filename="captcha_detection\captcha_model.h5"
    loaded_model=load_model(filename)

    for letter_bounding_box in letter_image_regions:
        x, y, w, h = letter_bounding_box
        letter_image = gray[y - 2:y + h + 2, x - 2:x + w + 2]
        letter_image = cv2.resize(letter_image, (30,30))
        letter_image = np.expand_dims(letter_image, axis=2)
        letter_image = np.expand_dims(letter_image, axis=0)
        pred = loaded_model.predict(letter_image)
        letter = lb.inverse_transform(pred)[0]
        predictions.append(letter)

    captcha_text = "".join(predictions)
    print("Predicted Captcha is: {}".format(captcha_text))
    return captcha_text