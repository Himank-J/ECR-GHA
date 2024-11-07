import os
import json
import boto3
import git
import pytorch_lightning as pl
from dataset_module import MNISTDataModule
from model import MNISTModel
from pytorch_lightning.callbacks import ModelCheckpoint
import datetime

def upload_to_s3(local_path, s3_path, bucket_name):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )
    s3_client.upload_file(local_path, bucket_name, s3_path)

def download_from_s3(s3_path, local_path, bucket_name):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )
    try:
        s3_client.download_file(bucket_name, s3_path, local_path)
        return True
    except:
        return False

def get_git_commit_id():
    try:
        # First try to get from environment variable (set by CI/CD)
        commit_id = os.environ.get('COMMIT_ID')
        if commit_id:
            return commit_id
            
        # Fallback to getting from git directly
        repo = git.Repo(search_parent_directories=True)
        return repo.head.object.hexsha
    except:
        # If all fails, return a timestamp
        return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

def main():
    # S3 configuration
    BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    commit_id = get_git_commit_id()
    
    # Create S3 paths with commit ID
    s3_base_path = f'model_results/{commit_id}'
    s3_model_path = f'{s3_base_path}/mnist_model.ckpt'
    s3_metrics_path = f'{s3_base_path}/metrics.json'
    
    print(f"Using commit ID: {commit_id}")
    print(f"S3 base path: {s3_base_path}")

    # Set random seed for reproducibility
    pl.seed_everything(42)

    # Define checkpoint directory and path
    checkpoint_dir = 'checkpoints'
    checkpoint_path = os.path.join(checkpoint_dir, 'mnist_model.ckpt')

    # Initialize data module
    data_module = MNISTDataModule(batch_size=64)

    # Setup checkpoint callback
    checkpoint_callback = ModelCheckpoint(
        dirpath=checkpoint_dir,
        filename='mnist_model',
        save_top_k=1,
        monitor='val_loss',
        mode='min'
    )

    # Initialize trainer
    trainer = pl.Trainer(
        max_epochs=5,
        accelerator='auto',
        devices=1,
        logger=pl.loggers.TensorBoardLogger('lightning_logs/'),
        enable_progress_bar=True,
        callbacks=[checkpoint_callback]
    )

    # Check if checkpoint exists in S3
    if download_from_s3(s3_model_path, checkpoint_path, BUCKET_NAME):
        print(f"Found checkpoint in S3")
        model = MNISTModel.load_from_checkpoint(checkpoint_path)
        if hasattr(model, 'is_trained') and model.is_trained:
            print("Model is already fully trained. Skipping to testing.")
        else:
            print("Resuming training from checkpoint...")
            trainer.fit(model, data_module)
    else:
        print("Starting training from scratch...")
        model = MNISTModel()
        trainer.fit(model, data_module)

    # Mark model as trained and save
    model.is_trained = True
    trainer.save_checkpoint(checkpoint_path)
    
    # Test and save metrics
    print("Testing the model...")
    test_results = trainer.test(model, data_module)
    
    # Save metrics to JSON
    metrics_path = os.path.join(checkpoint_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(test_results[0], f)

    # Upload to S3
    upload_to_s3(checkpoint_path, s3_model_path, BUCKET_NAME)
    upload_to_s3(metrics_path, s3_metrics_path, BUCKET_NAME)

if __name__ == '__main__':
    main()