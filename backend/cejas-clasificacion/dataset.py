from roboflow import Roboflow
rf = Roboflow(api_key="TLkiWuHz5txQSmL4a8s1")
project = rf.workspace("ca-br0ey").project("tipos-de-cejas")
version = project.version(9)
dataset = version.download("folder")