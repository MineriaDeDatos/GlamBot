
from roboflow import Roboflow

rf = Roboflow(api_key="rnPRbYujRft8KTHQ9S56")
project = rf.workspace("karen2").project("facesclassification-tu27q")
version = project.version(21)
dataset = version.download("folder")

print("Dataset descargado en:", dataset.location)
