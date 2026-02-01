"""
Helper script to upload baseline images to Azure ML datastore
"""
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential
from pathlib import Path


def upload_baseline_images(
    subscription_id: str,
    resource_group: str,
    workspace_name: str,
    local_path: str = "d:/projects/WoundTrack/data/baseline_wounds",
    dataset_name: str = "baseline-wounds",
    dataset_version: str = "1"
):
    """
    Upload baseline wound images to Azure ML
    
    Args:
        subscription_id: Azure subscription ID
        resource_group: Resource group name
        workspace_name: ML workspace name
        local_path: Local folder with baseline images
        dataset_name: Name for registered dataset
        dataset_version: Version number
    """
    
    print("=" * 80)
    print("Azure ML: Upload Baseline Wound Images")
    print("=" * 80)
    
    # Connect to workspace
    print("\n1. Connecting to workspace...")
    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name
    )
    print("✓ Connected")
    
    # Verify local path exists
    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"Local path not found: {local_path}")
    
    # Count images
    image_files = list(local_path.glob("*.jpg")) + list(local_path.glob("*.png"))
    print(f"\n2. Found {len(image_files)} images in {local_path}")
    
    if len(image_files) == 0:
        raise ValueError("No images found! Run select_baselines.py first.")
    
    # Create dataset
    print(f"\n3. Creating dataset: {dataset_name} v{dataset_version}")
    
    baseline_data = Data(
        name=dataset_name,
        version=dataset_version,
        description="Baseline wound images for synthetic progression generation",
        type=AssetTypes.URI_FOLDER,
        path=str(local_path)
    )
    
    # Upload and register
    print("   Uploading... (this may take a few minutes)")
    registered_data = ml_client.data.create_or_update(baseline_data)
    
    print("\n✅ Upload complete!")
    print(f"   Dataset: {registered_data.name}")
    print(f"   Version: {registered_data.version}")
    print(f"   Path: {registered_data.path}")
    
    # Generate pipeline input path
    pipeline_path = f"azureml:{dataset_name}:{dataset_version}"
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print(f"\n1. Update pipeline_definition.py:")
    print(f'   baseline_dataset_path = "{pipeline_path}"')
    print("\n2. Run pipeline:")
    print("   python azure_ml/pipeline_definition.py")
    print("=" * 80)
    
    return registered_data


if __name__ == "__main__":
    # Configuration - UPDATE THESE
    CONFIG = {
        "subscription_id": "YOUR_SUBSCRIPTION_ID",
        "resource_group": "YOUR_RESOURCE_GROUP",
        "workspace_name": "YOUR_WORKSPACE_NAME",
        "local_path": "d:/projects/WoundTrack/data/baseline_wounds"
    }
    
    print("\n⚠️  UPDATE CONFIG VALUES BEFORE RUNNING!\n")
    
    for key, value in CONFIG.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 80)
    
    # Uncomment to run:
    # upload_baseline_images(**CONFIG)
