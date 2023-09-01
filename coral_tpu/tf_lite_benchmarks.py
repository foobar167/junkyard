# Benchmarks
#     CPU vs TPU
#     Desktop, Pi4 and CoolPi
#     Windows and Linux
# Execute:
#     python benchmarks/tf_lite_benchmarks.py
# Links:
#     PyCoral GitHub: https://github.com/google-coral/pycoral
#     Test Data for Coral TPU: https://github.com/google-coral/test_data/tree/104342d2d3480b3e66203073dac24f4e2dbb4c41
import os
import platform

info = {
    'Linux': 'lscpu',
    'Windows': 'wmic cpu get name, numberofcores',
}[platform.system()]

print()  # new line
os.system(command=info)  # get info about the hardware

model_tpu = 'test_data/tf2_mobilenet_v3_edgetpu_1.0_224_ptq_edgetpu.tflite'
model_cpu = 'test_data/tf2_mobilenet_v3_edgetpu_1.0_224_ptq.tflite'
image = 'test_data/parrot.jpg'  # 'cat-test.bmp'
count = 22

message = lambda msg: f'''python -c "print('\\n--- {msg} ---')"'''
command = lambda m, i=image, c=count, tf='': f'python benchmarks/tf_lite.py -m {m} -i {i} -c {c} {tf}'

tests = (
    message('Run on Coral TPU'),
    command(model_tpu),
    message('Run on CPU with TF library'),
    command(model_cpu, tf='--tf'),
    message('Run on CPU with tflite_runtime library'),
    command(model_cpu),
)

for t in tests:
    os.system(command=t)  # run test
