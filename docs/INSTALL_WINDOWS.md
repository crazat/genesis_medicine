# Windows 11 + CUDA 12 설치 가이드

Genesis_Medicine v2는 **WSL2 Ubuntu 22.04 + Docker**를 공식 경로로 한다.
네이티브 Windows는 cheminformatics 계층 (RDKit, Chemprop, ADMET-AI)만 지원.

## 1. 전제

- Windows 11 Pro 22H2+
- NVIDIA GPU 24 GB VRAM 이상 (RTX 3090 / 4090 / A5000 / A6000)
- NVIDIA 드라이버 550+ (CUDA 12.4 이상 호환)
- WSL2 활성, Ubuntu 22.04 LTS
- Docker Desktop (WSL2 백엔드, NVIDIA runtime)

```powershell
wsl --install -d Ubuntu-22.04
```

## 2. WSL 내부 준비

```bash
# GPU 확인 (cuda-runtime 없어도 드라이버 호스트에서 전달됨)
nvidia-smi

# Python 3.11 + uv
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3.11-dev git
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 3. 저장소 부트스트랩

```bash
cd /mnt/c/Projects/Genesis_Medicine      # 또는 WSL 네이티브 경로
uv venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## 4. 구조 예측 엔진

### Boltz-2 (권장)
```bash
uv pip install boltz
# 웨이트는 첫 실행 시 자동 다운로드 (~1.5 GB, ~/.boltz/)
boltz predict --help
```

### Protenix v2
```bash
uv pip install protenix    # PyPI 제공 시
# 또는
uv pip install "git+https://github.com/bytedance/Protenix.git"
```

### 검증
```bash
python -c "from genesis_medicine.structure import get_predictor; \
           from omegaconf import OmegaConf; \
           p = get_predictor(OmegaConf.load('conf/structure/boltz2.yaml')); \
           print(p.engine_name, p.supports_ligands(), p.supports_affinity())"
```

## 5. Docker 경로 (대안·운영용)

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run structure \
    python -m genesis_medicine.cli run disease=alzheimer structure=boltz2
```

## 6. 자주 실패하는 지점

| 증상 | 원인 | 해결 |
|---|---|---|
| `CUDA error: out of memory` (Boltz-2) | 기본 crop 512 | `conf/structure/boltz2.yaml`에서 `crop_size: 256` |
| `colabfold_batch: command not found` | MSA 서버 없음 | `use_msa: false` 또는 ColabFold 별도 설치 |
| `libcuda.so.1 not found` in Docker | nvidia runtime 미설치 | Docker Desktop > Settings > Resources > WSL integration 재확인 |
| `protenix` 설치 실패 | PyPI 미공개 기간 발생 가능 | GitHub HEAD 직접 설치 (`git+https://...`) |
| Windows 네이티브에서 `openmm` import 실패 | conda 전용 | WSL2로 이동 |
