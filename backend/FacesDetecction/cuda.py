import torch
print(f"Num GPUs disponibles: {torch.cuda.device_count()}")
print(torch.cuda.is_available())
