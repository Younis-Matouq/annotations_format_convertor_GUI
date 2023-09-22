import json
from pathlib import Path
import numpy as np 
import glob
import os 

def empty_json(json_file_data):
    '''This function check if the annotation file (JSON) is empty'''

    return len(json_file_data['shapes']) == 0

def json_reader(json_path):
    # Open the file for reading
    with open(json_path, 'r') as file:
        data = json.load(file)
        return data 
    
def annotation_process(data,class_dict):
    file_annot=[]
    for obj in range(len(data['shapes'])):
        # get annotations from json process them and convert them to an array then to a list 
        txt_annot= np.array(data['shapes'][obj]['points'],dtype=np.float64)
        txt_annot/= np.array((data['imageWidth'],data['imageHeight']),dtype=np.float64)
        txt_annot=txt_annot.flatten().tolist()
        #get class name from json
        cls=class_dict[data['shapes'][obj]['label']]

        txt_annot.insert(0, cls)
        #append annotations to one list 
        file_annot.append(txt_annot)
    return file_annot

def text_file_writer(file_path,output_path,annotation_data):

    file_name= Path(file_path).stem
    out_file= os.path.join(output_path,file_name)
    with open(f'{out_file}.txt', 'w') as file:
        for sublist in annotation_data:
            line = ' '.join(map(str, sublist))  # Convert numbers to strings and join with spaces
            file.write(line + '\n')


def json_seg_to_txt_annotations(json_dir_path,output_dir,class_dict):

    all_json=glob.glob(os.path.join(json_dir_path,'*.json'))
    with open(class_dict, 'r') as f:
        class_dict = json.load(f)
    for json_f in all_json:
        try:
            annot_data= json_reader(json_f)
            if empty_json(annot_data):
                continue

            file_annotations= annotation_process(annot_data,class_dict)

            text_file_writer(json_f, output_dir, file_annotations)
        except Exception as e:
            continue