from roboflow import Roboflow

rf = Roboflow(api_key="BBPbxT1m8NQFJitRWQtg")
project = rf.workspace("il-edlcf").project("facedetection-jaybv")
version = project.version(5)
dataset = version.download("yolov8")

print("Dataset descargado en:", dataset.location)