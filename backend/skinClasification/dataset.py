from roboflow import Roboflow

rf = Roboflow(api_key="duzLRXUSAMNzyBY7rB2a")
project = rf.workspace("pc-v1pfs").project("skin_tone_classification")
version = project.version(15)
dataset = version.download("folder")

print("Dataset descargado en:", dataset.location)