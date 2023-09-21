# Run TensorFlow Lite model on Coral USB Accelerator or CPU
# Use tflite_runtime library or TF library.
#
# Execute command:
#   python tf_lite.py --tf -m data/tf2_mobilenet_v3_edgetpu_1.0_224_ptq.tflite -i data/cat_720p.jpg
# Links:
#     PyCoral GitHub: https://github.com/google-coral/pycoral
#     Test Data for Coral TPU: https://github.com/google-coral/test_data/tree/104342d2d3480b3e66203073dac24f4e2dbb4c41

import time
import platform
import argparse
import numpy as np

from PIL import Image


_EDGETPU_SHARED_LIB = {
    'Linux': 'libedgetpu.so.1',
    'Darwin': 'libedgetpu.1.dylib',
    'Windows': 'edgetpu.dll',
}[platform.system()]


def load_labels(filename):
    """ Get labels from file """
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]


parser = argparse.ArgumentParser()
parser.add_argument(
    '-i',
    '--image',
    default='data/parrot.jpg',
    help='Image to be classified',
)
parser.add_argument(
    '-m',
    '--model',
    default='data/tf2_mobilenet_v3_edgetpu_1.0_224_ptq_edgetpu.tflite',
    help='TensorFlow Lite model to be executed'
)
parser.add_argument(
    '-l',
    '--labels',
    default='data/imagenet_labels.txt',
    help='Name of file containing labels'
)
parser.add_argument(
    '-k', '--top_k', type=int, default=3,
    help='Max number of classification results'
)
parser.add_argument(
    '-c', '--count', type=int, default=10,
    help='Number of times to run inference'
)
parser.add_argument(
    '--tf',
    action=argparse.BooleanOptionalAction,
    help='Use tflite_runtime library or TF library',
)
parser.add_argument(
    '-a', '--input_mean', type=float, default=128.0,
    help='Mean value for input normalization',
)
parser.add_argument(
    '-s', '--input_std', type=float, default=128.0,
    help='STD value for input normalization',
)
args = parser.parse_args()

if args.tf:  # use TensorFlow library
    import tensorflow as tf
    load_delegate = tf.lite.experimental.load_delegate
    get_interpreter = tf.lite.Interpreter
else:  # use tflite_runtime library
    import tflite_runtime.interpreter as tflite
    load_delegate = tflite.load_delegate
    get_interpreter = tflite.Interpreter

try:  # try to calculate on TPU (or CPU for CPU-model)
    delegate = load_delegate(library=_EDGETPU_SHARED_LIB, options={})
    interpreter = get_interpreter(model_path=args.model, experimental_delegates=[delegate])
except ValueError:  # calculate on CPU
    print('Error: can not load delegate. Calculate on CPU')
    interpreter = get_interpreter(model_path=args.model)

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()[0]
output_details = interpreter.get_output_details()[0]

# NxHxWxC or [1, 224, 224, 3], H:1, W:2
height = input_details['shape'][1]
width = input_details['shape'][2]
img = Image.open(args.image).resize((width, height), Image.LANCZOS)

# Image data must go through two transforms before running inference:
#     1. normalization: f = (input - mean) / std
#     2. quantization: q = f / scale + zero_point
# The following code combines the two steps as such:
#     q = (input - mean) / (std * scale) + zero_point
# However, if std * scale equals 1, and mean - zero_point equals 0, the input
#   does not need any preprocessing (but in practice, even if the results are
#   very close to 1 and 0, it is probably okay to skip preprocessing for better
#   efficiency; we use 1e-5 below instead of absolute zero).
params = input_details['quantization_parameters']
scale, zero_point = params['scales'], params['zero_points']
std, mean = args.input_std, args.input_mean

if abs(scale * std - 1) < 1e-5 and abs(mean - zero_point) < 1e-5:
    input_data = np.asarray(img)  # input data does not require preprocessing
else:  # input data requires preprocessing
    normalized_input = (np.asarray(img) - mean) / (std * scale) + zero_point
    np.clip(normalized_input, 0, 255, out=normalized_input)  # clip values to [0, 255]
    input_data = normalized_input.astype(np.uint8)  # convert to uint8

input_data = np.expand_dims(input_data, axis=0)  # [224, 224, 3] to [1, 224, 224, 3]
interpreter.set_tensor(input_details['index'], input_data)

print('-------- INFERENCE TIME --------')
runtime = []
for _ in range(args.count):
    start_time = time.time()
    interpreter.invoke()
    stop_time = time.time()
    runtime.append((stop_time - start_time) * 1000)
    print(f'{(runtime[-1]):.1f} ms')

print('-------- RESULTS --------')
labels = load_labels(args.labels)
results = interpreter.tensor(output_details['index'])().flatten()
if np.issubdtype(output_details['dtype'], np.integer):
    # Usually scale == 1/256 and zero_point == 0
    scale, zero_point = output_details['quantization']
    # Always convert to np.int64 to avoid overflow on subtraction.
    results = scale * (results.astype(np.int64) - zero_point)
top_k = results.argsort()[-args.top_k:][::-1]  # get first top k results
for i in top_k:
    print(f'{labels[i]}: {results[i]:07.5f}')

if len(runtime) > 5:
    runtime = runtime[2:]  # skip the first 2 values
elif len(runtime) > 1:
    runtime = runtime[1:]  # skip the 1st value
print(f'\n' f'Average time of last {len(runtime)} runs: {np.average(runtime):.2f} ms\n')

# Clear resources. Otherwise, there will be an error: "Segmentation fault (core dumped)".
del interpreter
