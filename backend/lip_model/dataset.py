from roboflow import Roboflow

rf = Roboflow(api_key="CDQeHbIKdtd4C7mJap9m")
project = rf.workspace("ca-ioqio").project("lip_makeup_detection2")
version = project.version(1)
dataset = version.download("yolov8")

print("Dataset descargado en:", dataset.location)