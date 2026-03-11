# WanGP on Clore.ai — Commands

## Rental Settings
- Docker Image: `cloreai/jupyter:ubuntu24.04-v2`
- Ports: `22`, `8888`

---

## Setup Commands

```bash
apt-get install -y git gcc g++ build-essential python3.12-dev python3-dev libgl1 libglib2.0-0t64 --fix-missing

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p /root/miniconda3
eval "$($(/root/miniconda3/bin/conda shell.bash hook))"
echo 'eval "$($(/root/miniconda3/bin/conda shell.bash hook))"' >> ~/.bashrc
source ~/.bashrc

conda create -n wangp python=3.12 -y
conda activate wangp

git clone https://github.com/deepbeepmeep/Wan2GP
cd Wan2GP

pip install -r requirements.txt

pkill jupyter

python wgp.py --listen --server-port 8888
```

---

## Access UI
```
https://xxxxxxxxxxxxxxx.cloreai.ru
```