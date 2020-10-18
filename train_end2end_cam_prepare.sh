cp ./rcnn/config_cam.py ./rcnn/config.m
cp ./rcnn/symbol/symbol_vgg_cam.py ./rcnn/symbol/symbol_vgg.py
cd ./data/VOCdevkit2007/VOC2007/
matlab -r VOC2007xml_cam
