import os
import json
import glob
from .seg_convert_json_to_txt import json_reader, empty_json
from pathlib import Path
def json_to_yolo_rect(json_dir_path, output_dir,dic_classes):
    '''This function returns text files with annotations.
        Parameters:
                path: Source path which contains Json files.
                dic_classes: a dictionary containing the names of the classes as keys and the classes IDs as values.
                ex: class_dic={'pothole': 0, 'manhole': 1, 'patch': 2}
    '''
    all_json=glob.glob(os.path.join(json_dir_path,'*.json'))
    
    with open(dic_classes, 'r') as f:
        dic_classes = json.load(f)

   
    for file in all_json:
        try:
            data= json_reader(file)
            
            if empty_json(data):
                continue

            height=data['imageHeight']
            width=data['imageWidth']
            specialChars= "[,]"
            objects= []
            for i in range(len(data['shapes'])):
                x_1, x_2= data['shapes'][i]['points'][0][0], data['shapes'][i]['points'][1][0]
                y_1, y_2= data['shapes'][i]['points'][0][1], data['shapes'][i]['points'][1][1]
                x_max, y_max= max(x_1, x_2), max(y_1, y_2)
                x_min, y_min= min(x_1, x_2), min(y_1, y_2)
                delta_x= (x_max-x_min)/width
                delta_y= (y_max-y_min)/ height
                x_center= x_min/width + delta_x/2
                y_center= y_min/height + delta_y/2
                label=dic_classes[data['shapes'][i]['label']]

                x_center, y_center, delta_x, delta_y= float(str(x_center)[:8]), float(str(y_center)[:8]),float(str(delta_x)[:8]), float(str(delta_y)[:8])
                objects.append([int(label), x_center, y_center, delta_x, delta_y ])


            with open(os.path.join(output_dir,Path(file).stem+'.txt'), "w") as ff:
                for obj in objects:
                    for specialChar in specialChars:
                        obj=str(obj).replace(specialChar,'')
                    ff.write(obj)
                    ff.write('\n')
        except Exception as e:
            continue

        