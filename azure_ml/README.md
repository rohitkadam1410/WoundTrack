# Azure ML Synthetic Wound Generator

Complete Azure ML pipeline for generating synthetic wound progression sequences.

## 📋 Prerequisites

1. **Azure ML Workspace** with:
   - GPU compute cluster (NC-series recommended)
   - Storage account for datasets
   - Proper permissions

2. **Azure CLI & Python SDK**:
   ```bash
   pip install azure-cli azure-ai-ml azure-identity
   az login
   ```

3. **Baseline Images**: Upload to Azure ML datastore

---

## 🚀 Quick Start

### Step 1: Prepare Baseline Images

Download 30-50 diverse wound images from your Kaggle datasets:

```bash
# Use the helper script
python select_baselines.py
```

### Step 2: Upload to Azure ML

```bash
# Via Azure CLI
az ml data create --name baseline-wounds --version 1 \
    --type uri_folder \
    --path ./data/baseline_wounds

# Or via Azure ML Studio:
# Data → Create → Upload folder → Select baseline_wounds/
```

### Step 3: Create GPU Compute Cluster

**Via Azure ML Studio:**
1. Compute → Compute clusters → New
2. Name: `gpu-cluster`
3. VM size: `Standard_NC6` (or NC12/NC24 for faster)
4. Min nodes: 0, Max nodes: 1
5. Create

**Via CLI:**
```bash
az ml compute create --name gpu-cluster \
    --type amlcompute \
    --size Standard_NC6 \
    --min-instances 0 \
    --max-instances 1
```

### Step 4: Configure Pipeline

Edit `azure_ml/pipeline_definition.py`:

```python
CONFIG = {
    "subscription_id": "YOUR_SUBSCRIPTION_ID",
    "resource_group": "YOUR_RESOURCE_GROUP", 
    "workspace_name": "YOUR_WORKSPACE_NAME",
    "compute_name": "gpu-cluster",
    "baseline_dataset_path": "azureml://datastores/workspaceblobstore/paths/baseline_wounds/"
}
```

### Step 5: Submit Pipeline

```bash
cd d:/projects/WoundTrack/azure_ml
python pipeline_definition.py
```

---

## 📊 Pipeline Components

### 1. `generate_synthetic_wounds.py`
Main generation script:
- Loads Stable Diffusion model
- Processes baseline images
- Generates 4 timepoints per wound (Day 0, 7, 14, 21)
- 80% healing, 20% worsening sequences

**Parameters:**
- `--input_dir`: Baseline images folder
- `--output_dir`: Output location
- `--num_sequences`: Number of sequences (default: 50)
- `--healing_ratio`: Healing/worsening split (default: 0.8)
- `--model_id`: Hugging Face model (default: SD 2.1)

### 2. `environment.yml`
Conda environment with:
- PyTorch + CUDA
- Diffusers, Transformers
- Azure ML SDK

### 3. `pipeline_definition.py`
Azure ML pipeline orchestration:
- Environment registration
- Compute configuration
- Input/output management
- Job submission

---

## 💰 Cost Estimation

**NC6 (1 GPU):**
- ~$0.90/hour
- 3 hours for 50 sequences
- **Total: ~$2.70**

**NC12 (2 GPUs):**
- ~$1.80/hour (faster processing)
- ~$3-5 per run

**Storage:**
- Minimal (<$0.10 for 1GB synthetic images)

---

## 📈 Monitoring

### Azure ML Studio
1. Go to: https://ml.azure.com
2. Experiments → `woundtrack-synthetic-generation`
3. View latest run
4. Monitor:
   - Logs (see generation progress)
   - Metrics
   - Outputs

### Programmatic Monitoring

```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

ml_client = MLClient(DefaultAzureCredential(), ...)
job = ml_client.jobs.get("job_name")

print(f"Status: {job.status}")
print(f"URL: {job.studio_url}")
```

---

## 📥 Download Results

After completion:

### Via Studio:
1. Jobs → Select completed job
2. Outputs + logs → `synthetic_wounds`
3. Download folder

### Via CLI:
```bash
az ml job download --name <job-name> \
    --output-name synthetic_wounds \
    --download-path ./outputs/
```

### Via SDK:
```python
ml_client.jobs.download(
    name="job_name",
    output_name="synthetic_wounds",
    download_path="./outputs/"
)
```

---

## 🔧 Troubleshooting

### Compute Not Starting
- Check quota limits (Azure Portal → Subscriptions → Usage + quotas)
- Ensure GPU SKU available in your region
- Try different NC-series size

### Model Download Timeout
- Increase `shm_size` in pipeline definition
- Use smaller model: `runwayml/stable-diffusion-v1-5`

### Out of Memory
- Reduce batch size
- Use smaller compute SKU with fewer sequences
- Enable gradient checkpointing in script

### Authentication Errors
```bash
az login
az account set --subscription <subscription-id>
```

---

## ✅ Verification

After pipeline completes, check outputs:

```
synthetic_wounds/
├── wound_000/
│   ├── day_0.png
│   ├── day_7.png
│   ├── day_14.png
│   ├── day_21.png
│   └── metadata.json
├── wound_001/
│   └── ...
└── generation_summary.json
```

**Expected:**
- 50 wound folders
- 4 images per folder (200 total)
- Metadata with progression type

---

## 🔄 Next Steps

1. Download synthetic wound sequences
2. Upload to Kaggle as new dataset
3. Use in main WoundTrack notebook
4. Proceed with MedGemma analysis

---

## 📚 Resources

- [Azure ML Documentation](https://learn.microsoft.com/en-us/azure/machine-learning/)
- [GPU VMs in Azure](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-gpu)
- [Stable Diffusion Models](https://huggingface.co/models?pipeline_tag=text-to-image&sort=trending)
