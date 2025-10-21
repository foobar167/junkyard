import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():  # make sure GPU is available
    num = torch.cuda.device_count()
    print(f'GPU count: {num}')
    for i in range(num):
        print(f'GPU {i} name: {torch.cuda.get_device_name(i)}')
else:
    print("GPU is not available")
