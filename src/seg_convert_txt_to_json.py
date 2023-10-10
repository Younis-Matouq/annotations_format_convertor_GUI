import os
import glob
import json
from pathlib import Path
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
from scipy.spatial import ConvexHull
import cv2 

def is_file_empty(file_path):
    '''This function checks if a file is empty.
        Parameter:
                file_path: path to text file.
                '''
    return os.path.getsize(file_path) == 0


def data_preperations(data):
    """This function accepts a string containing the class ID and (x,y) coordinates of a polygon and
    returns a numpy array containing the coordinates as floats and the class ID as a string."""
    
    class_id,polygon=data.split(' ',1)
    polygon=np.fromstring(polygon, sep=' ')
    
    if polygon.size%2:
        polygon=polygon[:-1]
    
    polygon=polygon.reshape(-1,2)
    
    return class_id,polygon


def no_smoothness(polygon,imageWidth,imageHeight):
    '''This function takes polygon verticies and return them in a format accepted by labelme, this function returns the 
    same annotations given to it from the text file.'''
    polygon = plt.Polygon(polygon).xy
    polygon= polygon * np.array([imageWidth,imageHeight])
    return polygon

def fully_smoothed(polygon,imageWidth,imageHeight):
    '''This function takes polygon verticies and return them in a format accepted by labelme, this function returns a smoothed version of the 
     annotations given to it from the text file.'''
    # Compute the convex hull
    hull = ConvexHull(polygon)

    # Get the vertices of the convex hull
    hull_points = polygon[hull.vertices]

    # Draw the polygon and get_polygon_coordinates
    polygon = plt.Polygon(hull_points).xy
    polygon=polygon* np.array([imageWidth,imageHeight])
    return polygon


def simple_smooth(polygon,imageWidth,imageHeight,epsilon=2.5):
    '''This function takes polygon verticies and return them in a format accepted by labelme, this function returns a smoothed version of the 
     annotations controlled by the epsilon value, the higher the epsilon the lower the details preserved, given to it from the text file.'''
    polygon = plt.Polygon(polygon).xy
    polygon= polygon * np.array([imageWidth,imageHeight])

    polygon=(polygon.reshape(-1,1,2)).astype(np.int32)
    approx_polygon = cv2.approxPolyDP(polygon, epsilon, True).squeeze()
    polygon = plt.Polygon(approx_polygon).xy

    return polygon

smoothness_level={'No Smoothness':no_smoothness,
                  'Fully Smoothed':fully_smoothed,
                  'Simple Smoothness':simple_smooth}


def polygon_coordinates(polygon,imageWidth,imageHeight,smoothness_degree='No Smoothness'):
    '''This function takes YOLO polygon coordinates and generates a smoother version of the same polygon.
        Parameters:
               polygon: 2D numpy array of the polygon coordinates.
               smoothness_degree: The level of smoothness to be applied 
               imageWidth: image width.
               imageHeight: image height.
               '''
    
    if polygon.shape[0]<3:
        
        # Draw the polygon
        polygon = plt.Polygon(polygon)

        #get_polygon_coordinates
        polygon=polygon.xy
        polygon=polygon* np.array([imageWidth,imageHeight])
        
        return polygon
    
    else:     
        smoothness_process=smoothness_level[smoothness_degree]
        polygon=smoothness_process(polygon,imageWidth=imageWidth,imageHeight=imageHeight)
        return polygon
    
    
def write_json(save_path,file_name,data_example):
    '''This function writes a Json file.
        Parameters:
              save_path: location where the file will be saved.
              file_name: a string representing the name of the file.
              data_example: a dictionary representing Labelme accepted format.'''
    completeName = os.path.join(save_path, file_name+".json") 
    with open(completeName, "w") as outfile:
        outfile.write(json.dumps(data_example,indent=2)) 
            
            
def json_file_data_format(img_path,imageWidth,imageHeight):
    """This function returns a dictionary in Labelme standard format."""
    image_name= Path(img_path).stem

    return {"version": "5.1.1", "flags": {},  "shapes":[],
              "imagePath": image_name+'.png',
              "imageData": None,
              "imageHeight":int(imageHeight) ,
              "imageWidth": int(imageWidth) }, image_name



def yolo_to_json_polygon_writer(text_dir,save_path,class_dic, imageWidth,imageHeight,smoothness_degree='No Smoothness'):
    """When called, this function creates a JSON file with polygon annotations.
            Parameters:
                text_dir: a directory containing YOLO polygon annotations.
                save_path: the location where the Json files will be saved.
                class_dic: a dictionary mapping YOLO class ID to Json Label,
                ex:{0:'white_lane_marking', 1:'yellow_lane_marking', 2:'white_dashed_marking'}.
                smoothness_degree: The level of smoothness to be applied 
               imageWidth: image width.
               imageHeight: image height.
            """

    all_txt=glob.glob(os.path.join(text_dir,'*.txt'))

    with open(class_dic, 'r') as f:
        class_dic = json.load(f)

    for txt in all_txt:
        
        try:
            if is_file_empty(txt):
                continue

            data=pd.read_csv(txt, delimiter='\t', header=None)
            polygons=[]
            labels=[]
            data_example, image_name= json_file_data_format(img_path=txt,imageWidth=imageWidth,imageHeight=imageHeight) 

            polygons=[]
            labels=[]
            for poly in data[0]:

                if len(poly)<2:
                    continue
                label,polygon=data_preperations(poly)

                polygon=polygon_coordinates(polygon,smoothness_degree=smoothness_degree, imageWidth=imageWidth, imageHeight=imageHeight)
                polygons.append(polygon)
                labels.append(label)

            for obj,label in zip(polygons,labels):


                #fill the annotation data
                data_example['shapes'].append({'label':class_dic[str(label)],
                'points':obj.tolist(), 'group_id': None, 
                'shape_type':"polygon",
                "flags": {}})


            write_json(save_path=save_path,file_name=image_name,data_example=data_example)

            labels.clear()
            polygons.clear()
        except Exception as e:
            continue