# AWS GitHub Actions for Machine Learning Model Training
[![Train ML Model on EC2](https://github.com/Himank-J/ECR-GHA/actions/workflows/train_test.yml/badge.svg)](https://github.com/Himank-J/ECR-GHA/actions/workflows/train_test.yml)
![Python](https://img.shields.io/badge/Python-3.8-blue.svg)
![AWS](https://img.shields.io/badge/AWS-Services-orange.svg)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-blue.svg)
![License](https://img.shields.io/github/license/your-username/your-repo.svg)

## Table of Contents

1. [Introduction](#introduction)
2. [Project Overview](#project-overview)
3. [AWS Setup](#aws-setup)
   - [1. Amazon Elastic Container Registry (ECR)](#1-amazon-elastic-container-registry-ecr)
   - [2. Amazon Elastic Compute Cloud (EC2)](#2-amazon-elastic-compute-cloud-ec2)
   - [3. Amazon Simple Storage Service (S3)](#3-amazon-simple-storage-service-s3)
   - [4. IAM Roles and Access](#4-iam-roles-and-access)
     - [Trust Policy](#trust-policy)
     - [Assume Role Policy](#assume-role-policy)
4. [GitHub Actions Workflow](#github-actions-workflow)
   - [Workflow Overview](#workflow-overview)
5. [Output](#output)
6. [Usage](#usage)
7. [Conclusion](#conclusion)
8. [References](#references)

---

## Introduction

This repository demonstrates how to leverage AWS resources—**ECR**, **EC2**, **S3**, and **IAM roles**—in conjunction with **GitHub Actions** to automate the training and testing of a machine learning model. We utilize a simple **PyTorch Lightning** script trained on the **MNIST** dataset. The workflow encompasses building Docker images, managing EC2 instances, storing outputs in S3, and ensuring secure and efficient operations throughout the process.

## Project Overview

The primary objectives of this project are:

1. **Push Docker Image to ECR**: Automate the building and pushing of Docker images to Amazon ECR using GitHub Actions.
2. **Manage EC2 Instances**: Automatically start and stop EC2 instances to handle the computational workload for training.
3. **Train Model and Store Outputs**: Execute the training script on the EC2 instance and store the results in Amazon S3.
4. **Resource Optimization**: Ensure EC2 instances are only running when necessary to optimize costs.

The workflow is orchestrated using GitHub Actions, ensuring a seamless CI/CD pipeline for machine learning operations.

## AWS Setup

Setting up AWS resources is crucial for the seamless operation of this project. Below are the detailed steps and configurations required for each service.

### 1. Amazon Elastic Container Registry (ECR)

**ECR** is used to store Docker images securely. Follow these steps to set up ECR:

1. **Create an ECR Repository**:
   ```bash
   aws ecr create-repository --repository-name <repo-name> --region <region>
   ```
   This command creates a new ECR repository named `<repo-name>` in the `<region>` region.

2. **Configure Repository Permissions**:
   Ensure that the IAM role associated with GitHub Actions has permissions to push and pull images from ECR. 
   This policy grants permissions to interact with Amazon ECR, enabling actions such as pushing and pulling Docker images.

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:CompleteLayerUpload",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:InitiateLayerUpload",
                    "ecr:PutImage",
                    "ecr:UploadLayerPart",
                    "ecr:GetAuthorizationToken"
                ],
                "Resource": "arn:aws:ecr:<region>:<AccountId>:repository/<repo-name>"
            },
            {
                "Effect": "Allow",
                "Action": "ecr:GetAuthorizationToken",
                "Resource": "*"
            }
        ]
    }
    ```

### 2. Amazon Elastic Compute Cloud (EC2)

**EC2** instances provide the computational resources needed for training the machine learning model.

1. **Launch an EC2 Instance**:
   Using the specified AMI and instance type:
   ```bash
   aws ec2 run-instances \
     --image-id <ami-id> \
     --count 1 \
     --instance-type <instance-type> \
     --key-name <ec2-ssh-key-name> \
     --security-group-ids <security-group-id> \
     --subnet-id <subnet-id> \
     --associate-public-ip-address
   ```

2. **Store EC2 Instance ID**:
   After launching, note the `InstanceId` and store it securely, as it will be used in GitHub Actions.

3. **IAM Policy for EC2**:
   The EC2 instances require specific IAM permissions to interact with other AWS services. This policy grants necessary permissions to manage EC2 instances and interact with ECR.

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:Describe*",
                    "ec2:StartInstances",
                    "ec2:StopInstances",
                    "ec2:RunInstances",
                    "ec2:TerminateInstances",
                    "ec2:CreateTags",
                    "ec2:CreateSecurityGroup",
                    "ec2:AuthorizeSecurityGroupIngress",
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage"
                ],
                "Resource": "*"
            }
        ]
    }
    ```

### 3. Amazon Simple Storage Service (S3)

**S3** serves as the storage backend for model checkpoints and training metrics.

1. **Create an S3 Bucket**:
   ```bash
   aws s3 mb s3://emlo-storage --region ap-south-1
   ```

2. **Set Bucket Permissions**:
   Ensure that the IAM role has `PutObject` and `GetObject` permissions for the bucket. Refer to the [S3 Bucket Policy](#s3-bucket-policy) section for the necessary IAM policy.
   This policy grants permissions to interact with the specified S3 bucket for uploading and downloading model checkpoints and metrics.

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket",
                    "s3:DeleteObject"
                ],
                "Resource": [
                    "arn:aws:s3:::emlo-storage",
                    "arn:aws:s3:::emlo-storage/*"
                ]
            }
        ]
    }
    ```

### 4. IAM Roles and Access

Proper **IAM roles and permissions** are vital for secure and efficient operations. Below are the policies required for different AWS services.

#### Trust Policy

This trust policy allows a specific IAM user to assume a role. Replace `<AccountId>` and `<user-name>` with your AWS account ID and IAM user name, respectively.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::<AccountId>:user/<user-name>"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

#### Assume Role Policy

This policy allows assuming a specific IAM role. Replace `<AccountId>` and `<iam-role-name>` with your AWS account ID and IAM role name, respectively.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::<AccountId>:role/<iam-role-name>"
        }
    ]
}
```

### Summary of IAM Roles

- **ECR Access Role**: Grants permissions to interact with Amazon ECR.
- **EC2 Role**: Grants permissions to manage EC2 instances and interact with ECR.
- **S3 Bucket Policy**: Grants permissions to upload and download data from the specified S3 bucket.
- **Trust and Assume Role Policies**: Facilitates secure role assumption for specific IAM users.

Ensure that these policies are correctly attached to their respective IAM roles to maintain security and functionality.

## GitHub Actions Workflow

The **GitHub Actions** workflow automates the end-to-end process of building, deploying, training, and cleaning up resources.

### Workflow Overview

The workflow is defined in the `.github/workflows/train_test.yml` file and consists of the following primary steps:

1. **Checkout Code**: Retrieves the repository code.
2. **Configure AWS Credentials**: Sets up AWS authentication.
3. **Login to Amazon ECR**: Authenticates Docker with ECR.
4. **Build and Push Docker Image**: Builds the Docker image and pushes it to ECR.
5. **Run Training on EC2**: Starts the EC2 instance, deploys the Docker container, runs the training script, and then stops the instance.

Major Steps:

Sets up AWS authentication using credentials stored securely in GitHub Secrets.

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v1
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: ${{ env.AWS_REGION }}
```

Authenticates Docker with Amazon ECR, enabling subsequent push operations.

```yaml
- name: Login to Amazon ECR
  id: login-ecr
  uses: aws-actions/amazon-ecr-login@v1
```

Builds the Docker image and pushes it to ECR.

```yaml
- name: Build and push Docker image
  env:
    ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
    IMAGE_TAG: ${{ github.sha }}
  run: |
    # Modify Dockerfile to use build args instead of ENV
    sed -i 's/ENV AWS_ACCESS_KEY_ID=.*/ARG AWS_ACCESS_KEY_ID/' Dockerfile
    sed -i 's/ENV AWS_SECRET_ACCESS_KEY=.*/ARG AWS_SECRET_ACCESS_KEY/' Dockerfile
    sed -i 's/ENV AWS_DEFAULT_REGION=.*/ARG AWS_DEFAULT_REGION/' Dockerfile
    sed -i 's/ENV S3_BUCKET_NAME=.*/ARG S3_BUCKET_NAME/' Dockerfile
    sed -i 's/ENV COMMIT_ID=.*/ARG COMMIT_ID/' Dockerfile
    
    # Build with secure credentials
    docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG \
      --build-arg AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }} \
      --build-arg AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }} \
      --build-arg AWS_DEFAULT_REGION=${{ env.AWS_REGION }} \
      --build-arg S3_BUCKET_NAME=${{ secrets.S3_BUCKET_NAME }} \
      --build-arg COMMIT_ID=${{ github.sha }} .
    
    docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
```

Run Training on EC2 Instance

```yaml
- name: Run training on existing EC2 instance
  env:
    ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
    IMAGE_TAG: ${{ github.sha }}
    INSTANCE_ID: ${{ secrets.EC2_INSTANCE_ID }}
  run: |
    # Start the instance
    aws ec2 start-instances --instance-ids $INSTANCE_ID
    echo "Starting EC2 instance..."
    
    # Wait for instance to be running
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    
    # Get instance public IP
    INSTANCE_IP=$(aws ec2 describe-instances \
      --instance-ids $INSTANCE_ID \
      --query 'Reservations[0].Instances[0].PublicIpAddress' \
      --output text)
    
    echo "Instance is running at $INSTANCE_IP"
    
    # Setup SSH key
    mkdir -p ~/.ssh
    echo "${{ secrets.EC2_SSH_KEY }}" > ~/.ssh/ec2_key
    chmod 600 ~/.ssh/ec2_key
    
    # Wait for instance to be ready for SSH
    sleep 60
    
    # Configure instance and run training via SSH
    ssh -i ~/.ssh/ec2_key -o StrictHostKeyChecking=no ubuntu@$INSTANCE_IP << EOF
      
      # Configure AWS credentials
      mkdir -p ~/.aws
      cat > ~/.aws/credentials << EOC
      [default]
      aws_access_key_id=${{ secrets.AWS_ACCESS_KEY_ID }}
      aws_secret_access_key=${{ secrets.AWS_SECRET_ACCESS_KEY }}
      region=$AWS_REGION
      EOC
      
      # Login to ECR
      aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
      
      # Pull latest image
      docker pull $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      
      # Run training container
      docker run \
        -e AWS_ACCESS_KEY_ID='${{ secrets.AWS_ACCESS_KEY_ID }}' \
        -e AWS_SECRET_ACCESS_KEY='${{ secrets.AWS_SECRET_ACCESS_KEY }}' \
        -e AWS_DEFAULT_REGION='$AWS_REGION' \
        -e S3_BUCKET_NAME='${{ secrets.S3_BUCKET_NAME }}' \
        -e COMMIT_ID='${{ github.sha }}' \
        $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
    EOF
    
    # Stop the instance after training
    echo "Training complete, stopping instance..."
    aws ec2 stop-instances --instance-ids $INSTANCE_ID
    
    # Wait for instance to stop
    aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID
    echo "Instance stopped successfully"
```
## Output

**Docker image when pushed to ECR**
<img width="1062" alt="image" src="https://github.com/user-attachments/assets/82a5b498-435b-4b7d-866a-6bc9e1555c94">

**Test Metrics & Model stored in S3**

Directory name same as latest commit ID
<img width="1068" alt="image" src="https://github.com/user-attachments/assets/9760be92-0b9d-4b9c-8151-b9a7a42edc5a">

## Usage

To utilize this workflow for training your machine learning model:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Configure AWS Secrets in GitHub**:
   - Navigate to your repository on GitHub.
   - Go to **Settings** > **Secrets and variables** > **Actions**.
   - Add the following secrets:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`
     - `S3_BUCKET_NAME`
     - `EC2_INSTANCE_ID`
     - `EC2_SSH_KEY`

3. **Set Up IAM Roles in AWS**:
   - **ECR Access**: Attach the [ECR Access Policy](#ecr-access-policy) to the IAM role used by GitHub Actions.
   - **EC2 Permissions**: Attach the [EC2 Policy](#ec2-policy) to the IAM role associated with EC2 instances.
   - **S3 Bucket**: Apply the [S3 Bucket Policy](#s3-bucket-policy) to your S3 bucket `emlo-storage`.
   - **Trust Relationships**: Configure the [Trust Policy](#trust-policy) and [Assume Role Policy](#assume-role-policy) as per your security requirements.

4. **Push Changes to Main Branch**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```
   - Pushing to the `main` branch triggers the GitHub Actions workflow.

5. **Monitor the Workflow**:
   - Navigate to the **Actions** tab in your GitHub repository to monitor the workflow's progress.

6. **Access Training Outputs**:
   - After successful execution, training metrics and model checkpoints will be available in the specified S3 bucket under `model_results/{commit_id}/`.

## Conclusion

This repository offers a comprehensive solution for automating the training and testing of machine learning models using GitHub Actions and AWS services. By integrating Docker, EC2, ECR, and S3, it ensures a scalable, secure, and efficient workflow. This setup not only optimizes resource utilization but also streamlines the CI/CD process for machine learning projects.

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS ECR Documentation](https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/index.html)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/index.html)
- [PyTorch Lightning Documentation](https://pytorch-lightning.readthedocs.io/en/stable/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
