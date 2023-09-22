
import os
import glob
import json
import numpy as np
from PIL import Image
from pathlib import Path

def is_file_empty(file_path):
    '''This function checks if a file is empty and returns the file path if the size of the given file is zero (empty file)
        Also, it warns the user about that..
        Parameter:
                file_path: path to text file.
                '''
    return os.path.getsize(file_path) == 0


def get_img_dimensions(img_path):
    img= Image.open(img_path)
    height, width= img.size[1], img.size[0]
    return height, width

def write_json(save_path,file_name,data_example):
        completeName = os.path.join(save_path, file_name+".json") 
        with open(completeName, "w") as outfile:
            outfile.write(json.dumps(data_example,indent=2))    
            
            
helper= {'dimensions_of_image': get_img_dimensions,
         'json_writer': write_json}

def convert_txt_to_labelme(yolo_text_files, results_path, class_dict,image_width= 1920,image_height=780):
    
    '''This function converts a text file that has yolo like annotation     
    to json file that is acceptable by labelme app, function parameters description:
    
    class_dict: accepts a dictionary that has keys similar to the classes ID and values similar to the
    the name of the classes. example---------> class_dict={'0': 'pothole', '1': 'manhole', '2': 'patch'}.
    
    results_path: the results where the json files will be saved. 
    
    yolo_text_files: a list that has all of the text files pathes. 
    
    image_width: the width of the images.
    
    image_height: the height of the images. 
    
    '''
    
    
    
    with open(class_dict, 'r') as f:
        class_dict = json.load(f)

    yolo_text_files= glob.glob(os.path.join(yolo_text_files,'*.txt'))

    
            
    for file in yolo_text_files:
        try:
            #check if the file does not contain annotations:
            if is_file_empty(file):
                continue

            file_name= Path(file).stem # Get_file_name    
        
            
            data_example= {"version": "5.1.1", "flags": {},  "shapes":[],
                        "imagePath": file_name+".png",
                        "imageData": None,
                        "imageHeight": image_height,
                        "imageWidth": image_width }
            # reading_txt_file_ that has yolo annotation
            yolo_data=np.loadtxt(file)
            if yolo_data.ndim == 1:
                yolo_data= yolo_data.reshape(1,-1)
            else: 
                pass 


            for obj in yolo_data:
                x_center, y_center, delta_x, delta_y = obj[1],obj[2],obj[3],obj[4]
                x_1= np.abs(image_width *(x_center- (delta_x/2))) # width 
                y_1= np.abs(image_height *(y_center- (delta_y/2))) # height
                x_2= np.abs(x_1 + delta_x*image_width)
                y_2= np.abs(y_1 + delta_y*image_height)
                data_example['shapes'].append({'label': class_dict[str(np.int32(obj[0]))],
                'points':[[ x_1, y_1],[ x_2, y_2]], 'group_id': None, 
                'shape_type':"rectangle",
                "flags": {}})

            
            helper['json_writer'](results_path,file_name,data_example)
        except Exception as e:
            continue