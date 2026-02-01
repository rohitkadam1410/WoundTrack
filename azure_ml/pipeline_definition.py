"""
Azure ML Pipeline Definition for Synthetic Wound Generation
"""
from azure.ai.ml import MLClient, command, Input, Output
from azure.ai.ml.entities import Environment
from azure.identity import DefaultAzureCredential
from pathlib import Path


def create_wound_generator_pipeline(
    subscription_id: str,
    resource_group: str,
    workspace_name: str,
    compute_name: str = "gpu-cluster"
):
    """
    Create and submit Azure ML pipeline for synthetic wound generation
    
    Args:
        subscription_id: Azure subscription ID
        resource_group: Resource group name
        workspace_name: ML workspace name
        compute_name: Compute cluster name (must have GPU)
    """
    
    # Connect to workspace
    print("Connecting to Azure ML workspace...")
    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name
    )
    
    # Register environment
    print("Creating environment...")
    env_name = "wound-generator-env"
    env_path = Path(__file__).parent / "environment.yml"
    
    custom_env = Environment(
        name=env_name,
        description="Environment for synthetic wound image generation",
        conda_file=env_path,
        image="mcr.microsoft.com/azureml/openmpi4.1.0-cuda11.8-cudnn8-ubuntu22.04"
    )
    
    custom_env = ml_client.environments.create_or_update(custom_env)
    print(f"✓ Environment registered: {custom_env.name}:{custom_env.version}")
    
    # Define pipeline component
    print("Creating pipeline component...")
    
    wound_generator_job = command(
        name="synthetic_wound_generation",
        display_name="Generate Synthetic Wound Progressions",
        description="Generate temporal wound healing/worsening sequences using Stable Diffusion",
        
        # Input: baseline wound images dataset
        inputs={
            "baseline_images": Input(
                type="uri_folder",
                description="Folder containing baseline wound images (Day 0)"
            ),
            "num_sequences": 50,
            "healing_ratio": 0.8,
            "model_id": "stabilityai/stable-diffusion-2-1"
        },
        
        # Output: generated sequences
        outputs={
            "synthetic_wounds": Output(
                type="uri_folder",
                description="Generated synthetic wound progression sequences"
            )
        },
        
        # Script and arguments
        code="./",
        command="""
            python generate_synthetic_wounds.py \
                --input_dir ${{inputs.baseline_images}} \
                --output_dir ${{outputs.synthetic_wounds}} \
                --num_sequences ${{inputs.num_sequences}} \
                --healing_ratio ${{inputs.healing_ratio}} \
                --model_id ${{inputs.model_id}}
        """,
        
        # Environment and compute
        environment=f"{env_name}@latest",
        compute=compute_name,
        
        # Resource requirements
        instance_count=1,
        shm_size="16g"  # Shared memory for model loading
    )
    
    return wound_generator_job, ml_client


def submit_pipeline(
    subscription_id: str,
    resource_group: str,
    workspace_name: str,
    baseline_dataset_path: str,
    compute_name: str = "gpu-cluster",
    experiment_name: str = "woundtrack-synthetic-generation"
):
    """
    Submit pipeline job to Azure ML
    
    Args:
        subscription_id: Azure subscription ID
        resource_group: Resource group name
        workspace_name: ML workspace name
        baseline_dataset_path: URI to baseline images dataset
        compute_name: GPU compute cluster name
        experiment_name: Experiment name for tracking
    """
    
    # Create pipeline
    job, ml_client = create_wound_generator_pipeline(
        subscription_id,
        resource_group,
        workspace_name,
        compute_name
    )
    
    # Configure inputs
    job.inputs.baseline_images = Input(
        type="uri_folder",
        path=baseline_dataset_path
    )
    
    # Submit job
    print(f"Submitting job to experiment: {experiment_name}")
    returned_job = ml_client.jobs.create_or_update(
        job,
        experiment_name=experiment_name
    )
    
    print("=" * 80)
    print(f"✅ Pipeline submitted!")
    print(f"Job name: {returned_job.name}")
    print(f"Status: {returned_job.status}")
    print(f"Studio URL: {returned_job.studio_url}")
    print("=" * 80)
    print("\n💡 Monitor progress in Azure ML Studio")
    print("💡 Expected runtime: 2-4 hours for 50 sequences")
    
    return returned_job


if __name__ == "__main__":
    # Example configuration - UPDATE THESE VALUES
    CONFIG = {
        "subscription_id": "YOUR_SUBSCRIPTION_ID",
        "resource_group": "YOUR_RESOURCE_GROUP",
        "workspace_name": "YOUR_WORKSPACE_NAME",
        "compute_name": "gpu-cluster",  # Must have GPU
        "baseline_dataset_path": "azureml://datastores/workspaceblobstore/paths/baseline_wounds/"
    }
    
    print("Azure ML Synthetic Wound Generator Pipeline")
    print("=" * 80)
    print("\n⚠️  UPDATE CONFIG VALUES BEFORE RUNNING!")
    print("\nConfiguration:")
    for key, value in CONFIG.items():
        print(f"  {key}: {value}")
    
    # Uncomment to submit:
    # submit_pipeline(**CONFIG)
