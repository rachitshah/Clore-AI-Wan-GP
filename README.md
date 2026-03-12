# Wan2.2 — Commands Only
> New Clore.ai server · RTX PRO 6000 (96GB) · 250GB disk · Docker: cloreai/jupyter:ubuntu24.04-v2 · Ports: 22, 7860

---

## 1. System
```bash
apt-get update && apt-get install -y git wget curl nvtop htop ncdu gcc g++ build-essential python3.12-dev python3-dev libgl1 libglib2.0-0t64 --fix-missing
```

## 2. Miniconda
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p /root/miniconda3
eval "$(/root/miniconda3/bin/conda shell.bash hook)"
echo 'eval "$(/root/miniconda3/bin/conda shell.bash hook)"' >> ~/.bashrc
source ~/.bashrc
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda create -n wan22 python=3.12 -y
conda activate wan22
```

## 3. PyTorch (cu128 — Blackwell architecture)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

## 4. Wan2.2 Repo
```bash
git clone https://github.com/Wan-Video/Wan2.2 /root/wan22
cd /root/wan22

# Install everything EXCEPT flash_attn
grep -v flash_attn requirements.txt > /tmp/req_no_flash.txt
pip install -r /tmp/req_no_flash.txt

# Pin huggingface_hub to avoid breaking transformers/tokenizers
pip install "huggingface_hub==0.30.0"

mkdir -p /root/wan22/ckpts
```

### flash_attn (optional — Wan2.2 works without it)

**Fix 1 — nvcc missing (most common):**
```bash
# Find nvcc
find / -name nvcc 2>/dev/null

# Export path (adjust cuda version as needed)
export PATH=/usr/local/cuda-12.8/bin:$PATH
export CUDA_HOME=/usr/local/cuda-12.8
echo 'export PATH=/usr/local/cuda-12.8/bin:$PATH' >> ~/.bashrc
echo 'export CUDA_HOME=/usr/local/cuda-12.8' >> ~/.bashrc

# Then install
pip install flash_attn --no-build-isolation
```

**Fix 2 — install nvcc via apt:**
```bash
apt-get install -y cuda-nvcc-12-8
pip install flash_attn --no-build-isolation
```

**Fix 3 — skip entirely (recommended):**
```bash
grep -v flash_attn requirements.txt > /tmp/req_no_flash.txt
pip install -r /tmp/req_no_flash.txt
```

## 5. HF Login (Token)
```bash
hf auth login
# paste your token from https://huggingface.co/settings/tokens
# or set as env variable (no login needed):
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
```

## 6. Download Models
```bash
# T2V 14B (~56GB) — 2 files
hf download Wan-AI/Wan2.2-T2V-A14B --local-dir /root/wan22/ckpts/Wan2.2-T2V-A14B

# I2V 14B (~56GB) — 2 files
hf download Wan-AI/Wan2.2-I2V-A14B --local-dir /root/wan22/ckpts/Wan2.2-I2V-A14B

# TI2V 5B (~10GB) — 1 file, fastest
hf download Wan-AI/Wan2.2-TI2V-5B --local-dir /root/wan22/ckpts/Wan2.2-TI2V-5B

# S2V 14B (~28GB) — audio to video
hf download Wan-AI/Wan2.2-S2V-14B --local-dir /root/wan22/ckpts/Wan2.2-S2V-14B

# Animate 14B (~28GB) — character animation
hf download Wan-AI/Wan2.2-Animate-14B --local-dir /root/wan22/ckpts/Wan2.2-Animate-14B

# Check disk after each
df -h /
```

## 7. Generate
```bash
cd /root/wan22

# T2V
python generate.py --task t2v-14B --ckpt_dir ./ckpts/Wan.2-T2V-A14B --prompt "your prompt" --size 1280*720

# I2V
python generate.py --task i2v-14B --ckpt_dir ./ckpts/Wan2.2-I2V-A14B --image /path/to/image.jpg --prompt "your prompt" --size 1280*720

# TI2V 5B
python generate.py --task ti2v-5B --ckpt_dir ./ckpts/Wan.2-T2V-5B --image /path/to/image.jpg --prompt "your prompt" --size 1280*720

# S2V
python generate.py --task s2v-14B --ckpt_dir ./ckpts/Wan.2-T2V-A14B --audio /path/to/audio.wav --prompt "your prompt" --size 832*480

# Animate
python generate.py --task animate-14B --ckpt_dir ./ckpts/Wan.2-T2V-A14B --image /path/to/character.jpg --prompt "your prompt" --size 832*480
```

## 8. Every New Session
```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate wan22
cd /root/wan22
```
