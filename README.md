# WanGP Setup Instructions

## Prerequisites

### Install Required Packages
```bash
apt-get install -y nvtop htop ncdu curl wget git gcc g++ build-essential python3.12-dev python3-dev libgl1 libglib2.0-0t64 --fix-missing
```

### Install Miniconda

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p /root/miniconda3
eval "$(/root/miniconda3/bin/conda shell.bash hook)"
echo 'eval "$(/root/miniconda3/bin/conda shell.bash hook)"' >> ~/.bashrc
source ~/.bashrc
```

### Accept Conda Terms of Service

```bash
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

### Create and Activate Environment

```bash
conda create -n wangp python=3.12 -y
conda activate wangp
```

### Clone Repository and Install Dependencies

```bash
git clone https://github.com/deepbeepmeep/Wan2GP /root/wangp
cd /root/wangp
```

### Install PyTorch

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Install Project Requirements

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python wgp.py --listen --server-port 7860
```

---

## Summary

Execute the commands above in sequence to set up and run WanGP. The application will be accessible on port 7860.