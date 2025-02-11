import torch
from torchvision import models, transforms
import torch.nn as nn

# Definir modelo base
modelo = models.resnet18(pretrained=True)
modelo.fc = nn.Linear(modelo.fc.in_features, 4)  # 4 clases: grasa, seca, mixta, normal

# Guardar modelo inicial
torch.save(modelo.state_dict(), "skin_classifier.pth")
print("✅ Modelo de clasificación de piel guardado en 'skin_classifier.pth'")
