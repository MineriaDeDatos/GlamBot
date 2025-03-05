from roboflow import Roboflow

rf = Roboflow(api_key="TLkiWuHz5txQSmL4a8s1")
project = rf.workspace("ca-br0ey").project("eyesbrown_model-fjs0f")
version = project.version(10)
dataset = version.download("yolov8")

