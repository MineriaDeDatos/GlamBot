from roboflow import Roboflow

rf = Roboflow(api_key="CDQeHbIKdtd4C7mJap9m")
project = rf.workspace("ca-ioqio").project("lip_makeup_segmentation")
version = project.version(8)
dataset = version.download("yolov8")
