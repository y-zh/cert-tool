#!/usr/bin/env python
#coding=utf-8

from flask import Flask, request, make_response, send_file
from PIL import ImageFont, ImageDraw, Image
import cv2
import numpy as np
from datetime import date, datetime
import os
import shutil
import zipfile

FONT_FILE = 'calibri.ttf'
CLSA_TEMPLATE = 'CLSA.jpeg'
CLTA_TEMPLATE = 'CLTA.jpeg'
NAME_POSITION = (1224, 1022)
NAME_BGRA = (33,33,33,0)
DATE_POSITION = (462, 1774)
DATE_BGRA = (33,33,33,0)
ROOT_DIR = '.'

app = Flask(__name__)

def sign_cert(cert_name, cert_date, cert_type, target_dir):
    print('signing cert: ' + cert_type + ' ' + cert_name)
    font = ImageFont.truetype(FONT_FILE , 80)
    cert = 'CLSA' if cert_type == 'clsa' else 'CLTA'
    template = CLSA_TEMPLATE if cert_type == 'clsa' else CLTA_TEMPLATE
    
    image = Image.fromarray(cv2.imread(ROOT_DIR + '/templates/' + template))
    draw = ImageDraw.Draw(image)
    draw.text(NAME_POSITION,  cert_name, font = font, fill = NAME_BGRA)
    draw.text(DATE_POSITION,  cert_date, font = font, fill = DATE_BGRA)
    file_name = target_dir + '/' + cert + '_'+ cert_name + '.png'
    cv2.imwrite(file_name, np.array(image))

    return file_name

@app.route('/cert', methods = ['POST'])
def cert():

    data = request.json
    now = datetime.now()
    dir = ROOT_DIR + '/c' + now.strftime("%Y%m%d%H%M%S%f")
    zip_file_name = dir + '.zip'
    

    try:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(ROOT_DIR + '/' + dir)

        if os.path.exists(zip_file_name):
            os.remove(zip_file_name)

        zip_file = zipfile.ZipFile(ROOT_DIR + '/' + zip_file_name, 'w')
        print('creating zip file: ' + ROOT_DIR + '/' + zip_file_name)


        for cert in data:
            cert_name = cert['name']
            cert_date = cert['date'] if 'date' in cert else now.strftime("%m/%d/%Y")
            cert_type = cert['type'] if 'type' in cert and cert['type'] != 'both' else 'both'
            
            if cert_type == 'clsa' or cert_type == 'both':
                file_name = sign_cert(cert_name, cert_date, 'clsa' , dir)
                zip_file.write(file_name)

            if cert_type == 'clta' or cert_type == 'both':
                file_name = sign_cert(cert_name, cert_date, 'clta' , dir)
                zip_file.write(file_name)

        zip_file.close()

    except Exception as e:
        print("Failed to generate cert: ", e)
        return make_response('Exception: ' + e, 500, {'Content-type': 'text/json'})

    return send_file(zip_file_name, as_attachment=True)

@app.route('/', methods = ['GET'])
def home():
    return make_response('home', 200, {'Content-type': 'text/plain'})

@app.route('/index', methods = ['GET'])
def index():
    return make_response('index', 200, {'Content-type': 'text/plain'})

if __name__ == '__main__':
    ROOT_DIR = os.getenv('APP_ROOT_DIR') if 'APP_ROOT_DIR' in os.environ else '.'
    app.run(host='0.0.0.0', port=5000)