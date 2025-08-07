micromamba create -n py313_torchCompile python=3.13 -y
micromamba activate py313_torchCompile

export CUDA_HOME=$CONDA_PREFIX
export CUDA_INC_PATH=$CONDA_PREFIX/targets/x86_64-linux/include:$CONDA_PREFIX/include

micromamba install -c nvidia cuda-cudart-dev cuda-nvcc cudnn cuda-toolkit cmake ninja -y

uv pip install -r requirements.txt

export _GLIBCXX_USE_CXX11_ABI=1
export TORCH_USE_CUDA_DSA=1

MAX_JOBS=8 python setup.py develop
