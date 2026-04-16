import argparse
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-steps", type=int, default=200)
    parser.add_argument("--seq-len", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--grad-accum", type=int, default=16)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--target-modules", default="q_proj,k_proj,v_proj,o_proj")
    parser.add_argument("--streaming", action="store_true")
    parser.add_argument("--no-streaming", action="store_true")
    
    args, unknown = parser.parse_known_args()
    
    # Map to train_qlora_3090.py arguments
    # Note: train_qlora_3090.py uses --model-name, --data-path, --output-dir, --max-length
    
    cmd = [
        sys.executable,
        "C:/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/train_qlora_3090.py",
        "--model-name", args.model,
        "--data-path", args.data,
        "--output-dir", args.out,
        "--max-length", str(args.seq_len),
        "--epochs", "3", # Hardcoded or could derive from max-steps
        "--batch-size", str(args.batch_size),
        "--grad-accum", str(args.grad_accum),
        "--learning-rate", str(args.lr),
        "--lora-r", str(args.lora-r),
        "--lora-alpha", str(args.lora-alpha),
        "--lora-dropout", str(args.lora-dropout)
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
