from roboflow import Roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="Wpl0z2OcviLnwaZE2KGh")
project = rf.workspace("eyes-5syfq").project("ojos_almendrados-qrrpo")
version = project.version(3)
dataset = version.download("folder")

print("Dataset descargado en:", dataset.location)


