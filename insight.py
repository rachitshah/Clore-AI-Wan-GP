#!/usr/bin/env python3
"""Wan2.2 system insight endpoint for Clore.ai GPU servers.

Exposes a single GET /insight endpoint that reports GPU status,
model checkpoint availability, disk usage, and Python environment info.

Usage:
    python insight.py              # default :7861
    python insight.py --port 8080  # custom port
"""

import json
import os
import shutil
import subprocess
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from argparse import ArgumentParser
from pathlib import Path

CKPT_DIR = os.environ.get("WAN_CKPT_DIR", "/root/wan22/ckpts")
WAN_DIR = os.environ.get("WAN_DIR", "/root/wan22")

KNOWN_MODELS = {
    "Wan2.2-T2V-A14B": {"task": "t2v-14B", "desc": "Text-to-Video 14B"},
    "Wan2.2-I2V-A14B": {"task": "i2v-14B", "desc": "Image-to-Video 14B"},
    "Wan2.2-TI2V-5B": {"task": "ti2v-5B", "desc": "Text+Image-to-Video 5B"},
    "Wan2.2-S2V-14B": {"task": "s2v-14B", "desc": "Sound-to-Video 14B"},
    "Wan2.2-Animate-14B": {"task": "animate-14B", "desc": "Character Animation 14B"},
}


def gpu_info():
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,memory.used,memory.free,"
                "utilization.gpu,temperature.gpu,driver_version",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return []

    gpus = []
    for line in out.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 8:
            continue
        gpus.append(
            {
                "index": int(parts[0]),
                "name": parts[1],
                "memory_total_mib": int(parts[2]),
                "memory_used_mib": int(parts[3]),
                "memory_free_mib": int(parts[4]),
                "utilization_pct": int(parts[5]),
                "temperature_c": int(parts[6]),
                "driver_version": parts[7],
            }
        )
    return gpus


def cuda_info():
    info = {"available": False}
    try:
        out = subprocess.check_output(
            ["nvcc", "--version"], text=True, timeout=5
        )
        for line in out.splitlines():
            if "release" in line.lower():
                info["nvcc_version"] = line.strip()
                info["available"] = True
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    return info


def model_status():
    models = {}
    ckpt_path = Path(CKPT_DIR)
    for name, meta in KNOWN_MODELS.items():
        model_dir = ckpt_path / name
        if model_dir.is_dir():
            files = list(model_dir.rglob("*"))
            total_bytes = sum(f.stat().st_size for f in files if f.is_file())
            models[name] = {
                "present": True,
                "task": meta["task"],
                "description": meta["desc"],
                "files": len([f for f in files if f.is_file()]),
                "size_gb": round(total_bytes / (1024**3), 2),
            }
        else:
            models[name] = {
                "present": False,
                "task": meta["task"],
                "description": meta["desc"],
            }
    return models


def disk_usage():
    partitions = {}
    for mount in ["/", "/root", CKPT_DIR]:
        try:
            usage = shutil.disk_usage(mount)
            partitions[mount] = {
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "used_pct": round(usage.used / usage.total * 100, 1),
            }
        except OSError:
            pass
    return partitions


def python_info():
    return {
        "version": sys.version,
        "executable": sys.executable,
        "prefix": sys.prefix,
    }


def torch_info():
    try:
        import torch

        info = {
            "version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda or None,
        }
        if torch.cuda.is_available():
            info["device_count"] = torch.cuda.device_count()
            info["current_device"] = torch.cuda.get_device_name(
                torch.cuda.current_device()
            )
        return info
    except ImportError:
        return {"installed": False}


def wan_info():
    wan_path = Path(WAN_DIR)
    info = {"directory": str(wan_path), "present": wan_path.is_dir()}
    if wan_path.is_dir():
        generate_py = wan_path / "generate.py"
        info["generate_script"] = generate_py.is_file()
    return info


def build_insight():
    return {
        "gpus": gpu_info(),
        "cuda": cuda_info(),
        "torch": torch_info(),
        "python": python_info(),
        "wan22": wan_info(),
        "models": model_status(),
        "disk": disk_usage(),
    }


class InsightHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.rstrip("/") not in ("", "/insight"):
            self.send_error(404)
            return
        data = build_insight()
        body = json.dumps(data, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[insight] {fmt % args}")


def main():
    parser = ArgumentParser(description="Wan2.2 insight endpoint")
    parser.add_argument("--port", type=int, default=7861)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), InsightHandler)
    print(f"[insight] listening on {args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()
