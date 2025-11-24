#!/usr/bin/env bash
#
# Sweepweave Environment Deployment Script
# Usage: ./deploy.sh [command]
#
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_NAME="sweepweave"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================================
# SETUP
# ============================================================================

setup() {
    log_info "Setting up Sweepweave environment..."
    
    # Check dependencies
    if ! command -v uv &> /dev/null; then
        log_error "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "python3 not found. Please install Python 3.10+"
        exit 1
    fi
    
    # Create project if needed
    if [ ! -f "pyproject.toml" ]; then
        log_info "Initializing new project..."
        uv init
    fi
    
    # Install environment
    log_info "Installing Sweepweave environment..."
    uv pip install -e "$SCRIPT_DIR"
    
    # Install dev dependencies
    log_info "Installing dev dependencies..."
    uv pip install pytest black ruff
    
    log_info "Setup complete! ✅"
}

# ============================================================================
# TESTING
# ============================================================================

test() {
    log_info "Running test suite..."
    
    if [ ! -f "$SCRIPT_DIR/test_sweepweave_env.py" ]; then
        log_error "Test file not found: $SCRIPT_DIR/test_sweepweave_env.py"
        exit 1
    fi
    
    uv run pytest "$SCRIPT_DIR/test_sweepweave_env.py" -v
    
    log_info "Tests passed! ✅"
}

# ============================================================================
# EVALUATION
# ============================================================================

eval_baseline() {
    local model="${1:-gpt-4.1-mini}"
    local num_examples="${2:-20}"
    local rollouts="${3:-3}"
    
    log_info "Running baseline evaluation..."
    log_info "Model: $model"
    log_info "Examples: $num_examples"
    log_info "Rollouts per example: $rollouts"
    
    uv run vf-eval "$ENV_NAME" \
        -m "$model" \
        -n "$num_examples" \
        -r "$rollouts" \
        --save
    
    log_info "Evaluation complete! ✅"
}

eval_claude() {
    local num_examples="${1:-20}"
    local rollouts="${2:-3}"
    
    if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
        log_error "ANTHROPIC_API_KEY not set"
        exit 1
    fi
    
    log_info "Evaluating Claude Sonnet 4.5..."
    
    uv run vf-eval "$ENV_NAME" \
        -m claude-sonnet-4-5-20250929 \
        --base-url https://api.anthropic.com/v1 \
        -n "$num_examples" \
        -r "$rollouts" \
        --save
    
    log_info "Evaluation complete! ✅"
}

# ============================================================================
# TRAINING
# ============================================================================

setup_training() {
    log_info "Setting up RL training environment..."
    
    # Run vf-setup to create configs and clone prime-rl
    uv run vf-setup
    
    # Create Sweepweave-specific config
    local config_dir="configs/prime-rl"
    mkdir -p "$config_dir"
    
    cat > "$config_dir/sweepweave.toml" << 'EOF'
[run]
project_name = "sweepweave-narrative-v1"
base_model = "meta-llama/Llama-3.1-8B-Instruct"
output_dir = "./outputs/sweepweave-v1"

[environment]
name = "sweepweave"
num_examples = 1000
min_characters = 2
max_characters = 5
min_encounters = 10
max_encounters = 30
seed = 42

[training]
num_iterations = 100
per_device_train_batch_size = 4
gradient_accumulation_steps = 4
learning_rate = 1e-5
warmup_steps = 100
max_steps = 10000

[rl]
temperature = 0.8
top_p = 0.95
max_tokens = 8000
kl_coef = 0.05
clip_range = 0.2

[inference]
tensor_parallel_size = 1
max_model_len = 16000
gpu_memory_utilization = 0.8

[logging]
wandb_project = "sweepweave-rl"
log_interval = 10
eval_interval = 100
save_interval = 500
EOF
    
    log_info "Training config created: $config_dir/sweepweave.toml"
    log_info "Training setup complete! ✅"
    log_info ""
    log_info "To start training:"
    log_info "  uv run prime-rl @ configs/prime-rl/sweepweave.toml"
}

train() {
    log_info "Starting RL training..."
    
    if [ ! -f "configs/prime-rl/sweepweave.toml" ]; then
        log_error "Training config not found. Run: ./deploy.sh setup-training"
        exit 1
    fi
    
    uv run prime-rl @ configs/prime-rl/sweepweave.toml
}

# ============================================================================
# CORPUS GENERATION
# ============================================================================

generate_configs() {
    local num_batches="${1:-10}"
    local batch_size="${2:-1000}"
    
    log_info "Generating storyworld configurations..."
    log_info "Batches: $num_batches"
    log_info "Batch size: $batch_size"
    
    python3 "$SCRIPT_DIR/corpus_amplification.py" \
        --output-dir ./corpus_configs \
        --batch-size "$batch_size" \
        --num-batches "$num_batches"
    
    local total=$((num_batches * batch_size))
    log_info "Generated $total configurations! ✅"
}

estimate() {
    log_info "Configuration space estimates:"
    python3 "$SCRIPT_DIR/corpus_amplification.py" --estimate-only
}

# ============================================================================
# PUBLISHING
# ============================================================================

publish() {
    log_info "Publishing to Prime Intellect Environments Hub..."
    
    # Check if prime CLI is installed
    if ! command -v prime &> /dev/null; then
        log_error "prime CLI not found. Install with: uv tool install prime"
        exit 1
    fi
    
    # Check authentication
    if ! prime config view &> /dev/null; then
        log_error "Not authenticated. Run: prime login"
        exit 1
    fi
    
    # Run tests first
    log_info "Running tests before publish..."
    test
    
    # Publish
    log_info "Publishing environment..."
    prime env push "$ENV_NAME"
    
    log_info "Published! ✅"
}

# ============================================================================
# UTILITIES
# ============================================================================

clean() {
    log_info "Cleaning build artifacts..."
    
    rm -rf build dist *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    
    log_info "Cleaned! ✅"
}

format() {
    log_info "Formatting code..."
    
    uv run black "$SCRIPT_DIR"
    uv run ruff check --fix "$SCRIPT_DIR"
    
    log_info "Formatted! ✅"
}

# ============================================================================
# HELP
# ============================================================================

help() {
    cat << EOF
Sweepweave Environment Deployment Script

Usage: ./deploy.sh [command] [args...]

Setup & Testing:
  setup                 - Install environment and dependencies
  test                  - Run test suite
  clean                 - Remove build artifacts
  format                - Format code with black and ruff

Evaluation:
  eval-baseline [model] [n] [r]  - Evaluate baseline model
                                   Default: gpt-4.1-mini, 20 examples, 3 rollouts
  eval-claude [n] [r]             - Evaluate Claude Sonnet 4.5
                                   Requires: ANTHROPIC_API_KEY
  estimate                        - Show configuration space estimates

Training:
  setup-training        - Set up RL training environment
  train                 - Start RL training with prime-rl

Corpus Generation:
  generate-configs [batches] [size]  - Generate storyworld configs
                                       Default: 10 batches × 1000 = 10k configs

Publishing:
  publish               - Publish to Prime Intellect Environments Hub

Examples:
  ./deploy.sh setup
  ./deploy.sh test
  ./deploy.sh eval-baseline gpt-4.1-mini 50 3
  ./deploy.sh eval-claude 20 1
  ./deploy.sh setup-training
  ./deploy.sh generate-configs 100 1000
  ./deploy.sh publish

For more information, see:
  - README.md
  - INTEGRATION_GUIDE.md
  - PROJECT_SUMMARY.md
EOF
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        setup)
            setup
            ;;
        test)
            test
            ;;
        eval-baseline)
            eval_baseline "$@"
            ;;
        eval-claude)
            eval_claude "$@"
            ;;
        estimate)
            estimate
            ;;
        setup-training)
            setup_training
            ;;
        train)
            train
            ;;
        generate-configs)
            generate_configs "$@"
            ;;
        publish)
            publish
            ;;
        clean)
            clean
            ;;
        format)
            format
            ;;
        help|--help|-h)
            help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            help
            exit 1
            ;;
    esac
}

main "$@"
