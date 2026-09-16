# EKS + Kubernetes Setup Guide

## Project

**Project:** AWS EKS CI/CD Automation Stack

**Region:** `ap-south-1`

**EKS Cluster:** `eks-cicd`

**Kubernetes Version:** `1.33`

**Environments:**

* `dev`
* `staging`
* `prod`

All three environments run as namespaces inside **one EKS cluster**.

---

# 1. Prerequisites

Make sure the following are installed and available in PowerShell:

```text
AWS CLI
Terraform
kubectl
Docker
Git
Python
```

Verify:

```powershell
aws --version
terraform version
kubectl version --client
docker --version
git --version
python --version
```

---

# 2. AWS Authentication

Check that AWS CLI is authenticated:

```powershell
aws sts get-caller-identity
```

Expected output should contain:

```text
Account
Arn
UserId
```

Verify the AWS region:

```powershell
aws configure get region
```

The project uses:

```text
ap-south-1
```

If required:

```powershell
aws configure
```

Set:

```text
Default region name: ap-south-1
```

---

# 3. Project Directory

Navigate to the Terraform environment:

```powershell
cd "C:\Users\Earnest.Ebenezer\OneDrive - Swan Solution\Desktop\Cloud Automation\Kubernetes_Lab\AWS_EKS_TF\terraform\environments\eks"
```

The Terraform environment contains:

```text
main.tf
variables.tf
provider.tf
outputs.tf
```

---

# 4. Terraform Initialization

Whenever starting from a fresh checkout:

```powershell
terraform init
```

This downloads the required providers and initializes the Terraform working directory.

---

# 5. Terraform Formatting

Run:

```powershell
terraform fmt -recursive
```

This formats Terraform configuration files.

---

# 6. Terraform Validation

Run:

```powershell
terraform validate
```

Expected:

```text
Success! The configuration is valid.
```

---

# 7. Review Terraform Plan

Run:

```powershell
terraform plan
```

Review the resources Terraform intends to create/change.

Do not blindly run `apply` without reviewing the plan.

---

# 8. Terraform Apply

When the plan looks correct:

```powershell
terraform apply
```

Terraform will ask for confirmation.

Enter:

```text
yes
```

Terraform provisions the AWS infrastructure.

The project currently includes infrastructure such as:

```text
VPC
├── Public Subnet - AZ A
├── Public Subnet - AZ B
├── Private Subnet - AZ A
├── Private Subnet - AZ B
├── Internet Gateway
├── NAT Gateway
└── Route Tables

ECR
└── eks-cicd-demo

EKS
└── eks-cicd
    └── Managed Node Group
        └── eks-cicd-nodes
```

The EKS worker nodes run in the private subnets.

---

# 9. Check Terraform Outputs

After apply:

```powershell
terraform output
```

If individual outputs are defined, they can also be queried separately:

```powershell
terraform output cluster_name
terraform output repository_url
```

Use the actual output names defined in `outputs.tf`.

---

# 10. Configure kubectl for EKS

Terraform creating the EKS cluster does not automatically configure the local `kubectl` context.

Run:

```powershell
aws eks update-kubeconfig --region ap-south-1 --name eks-cicd
```

Expected message:

```text
Added new context ...
```

---

# 11. Verify kubectl Context

Check:

```powershell
kubectl config current-context
```

The context should correspond to:

```text
eks-cicd
```

List available contexts:

```powershell
kubectl config get-contexts
```

---

# 12. Verify the EKS Cluster

Run:

```powershell
kubectl get nodes
```

Expected:

```text
NAME                                            STATUS   ROLES    AGE   VERSION
ip-10-0-11-xxx.ap-south-1.compute.internal     Ready    <none>   ...   v1.33.x
```

Check additional information:

```powershell
kubectl get nodes -o wide
```

The nodes should show private IP addresses because the worker nodes are deployed into private subnets.

---

# 13. Verify Kubernetes System Pods

Run:

```powershell
kubectl get pods -n kube-system
```

Core Kubernetes/EKS components should be running.

Also check:

```powershell
kubectl get all -n kube-system
```

---

# 14. Kubernetes Environment Structure

The project uses one EKS cluster with three namespaces:

```text
                    EKS CLUSTER
                       eks-cicd
                          |
             +------------+------------+
             |            |            |
            dev        staging        prod
          namespace   namespace     namespace
             |            |            |
            app          app          app
```

Do NOT create separate EKS clusters for dev, staging, and prod.

---

# 15. Kubernetes Directory Structure

Current structure:

```text
k8s/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── kustomization.yaml
│   └── ingress.yaml
│
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── namespace.yaml
    │
    ├── staging/
    │   ├── kustomization.yaml
    │   └── namespace.yaml
    │
    └── prod/
        ├── kustomization.yaml
        └── namespace.yaml
```

The old:

```text
k8s/base/namespace.yaml
```

should not be used because the base must remain environment-neutral.

---

# 16. Create / Apply DEV

Run:

```powershell
kubectl apply -k .\k8s\overlays\dev
```

This creates/configures:

```text
Namespace: dev
ConfigMap
Deployment
Service
```

Verify:

```powershell
kubectl get deployments,pods,services -n dev
```

Expected:

```text
Deployment   1/1
Pod          1/1 Running
Service      ClusterIP
```

---

# 17. Create / Apply STAGING

Run:

```powershell
kubectl apply -k .\k8s\overlays\staging
```

Verify:

```powershell
kubectl get deployments,pods,services -n staging
```

Expected:

```text
Deployment   1/1
Pod          1/1 Running
Service      ClusterIP
```

---

# 18. Create / Apply PROD

Run:

```powershell
kubectl apply -k .\k8s\overlays\prod
```

Verify:

```powershell
kubectl get deployments,pods,services -n prod
```

Expected:

```text
Deployment   1/1
Pod          1/1 Running
Service      ClusterIP
```

Because the namespace is declared in:

```text
k8s/overlays/prod/namespace.yaml
```

the namespace is managed declaratively by Kustomize.

---

# 19. Verify All Namespaces

Run:

```powershell
kubectl get namespaces
```

Expected project namespaces:

```text
dev
staging
prod
```

Other standard Kubernetes namespaces such as:

```text
default
kube-system
kube-public
kube-node-lease
```

are normal.

---

# 20. Verify All Applications

Run:

```powershell
kubectl get deployments,pods,services -n dev
```

```powershell
kubectl get deployments,pods,services -n staging
```

```powershell
kubectl get deployments,pods,services -n prod
```

All three environments should have:

```text
Deployment: 1/1
Pod:        1/1 Running
Service:    ClusterIP
```

---

# 21. Verify Kustomize Rendering

Before applying an overlay, it can be useful to inspect what Kustomize generates.

DEV:

```powershell
kubectl kustomize .\k8s\overlays\dev
```

STAGING:

```powershell
kubectl kustomize .\k8s\overlays\staging
```

PROD:

```powershell
kubectl kustomize .\k8s\overlays\prod
```

This only renders the manifests.

It does NOT deploy them.

---

# 22. Apply vs Kustomize

### Render only

```powershell
kubectl kustomize .\k8s\overlays\dev
```

### Render and deploy

```powershell
kubectl apply -k .\k8s\overlays\dev
```

The same pattern applies to staging and prod.

---

# 23. Verify Application Health

The application exposes:

```text
/
 /health
 /version
```

The Kubernetes probes use:

```text
/health
```

Check the Deployment:

```powershell
kubectl describe deployment eks-cicd-demo -n dev
```

Check the Pod:

```powershell
kubectl describe pod -l app=eks-cicd-demo -n dev
```

---

# 24. Test the Application with Port Forwarding

The current Service is:

```text
ClusterIP
```

It is therefore not directly accessible from the Internet.

For temporary local testing:

```powershell
kubectl port-forward service/eks-cicd-demo 8000:80 -n dev
```

Then open:

```text
http://localhost:8000
```

Health endpoint:

```text
http://localhost:8000/health
```

Version endpoint:

```text
http://localhost:8000/version
```

Stop port forwarding with:

```text
Ctrl + C
```

---

# 25. Check the Application Version

The current image is:

```text
891048843822.dkr.ecr.ap-south-1.amazonaws.com/eks-cicd-demo:v1.0.0
```

Check:

```powershell
kubectl get deployment eks-cicd-demo -n dev -o jsonpath="{.spec.template.spec.containers[0].image}"
```

Expected:

```text
891048843822.dkr.ecr.ap-south-1.amazonaws.com/eks-cicd-demo:v1.0.0
```

---

# 26. Important Versioning Rule

The ECR repository uses immutable image tags.

Therefore:

```text
v1.0.0
```

must not be overwritten.

For the next application release, use something like:

```text
v1.0.1
```

Then:

```text
v1.0.2
v1.0.3
...
```

Eventually Jenkins will automate this process.

The future pipeline will perform:

```text
Git Push
   ↓
Jenkins
   ↓
Tests
   ↓
Docker Build
   ↓
Security Scan
   ↓
ECR Push
   ↓
Kubernetes Deployment
```

---

# 27. Current Ingress Status

The project contains:

```text
k8s/base/ingress.yaml
```

but it should NOT be deployed yet.

The project currently does not have the AWS Load Balancer Controller configured.

Therefore, use:

```powershell
kubectl port-forward
```

for application testing.

Later:

```text
AWS Load Balancer Controller
        ↓
Ingress
        ↓
AWS Application Load Balancer
        ↓
EKS Service
        ↓
Pods
```

---

# 28. Important: Terraform vs Kubernetes

Terraform manages the AWS infrastructure:

```text
Terraform
   ↓
VPC
ECR
EKS
Node Group
IAM
Networking
```

Kubernetes/Kustomize manages the workloads:

```text
kubectl / Kustomize
        ↓
Namespaces
Deployments
Services
ConfigMaps
Ingress
Pods
```

Eventually Jenkins will coordinate the application deployment.

---

# 29. Rebuild Procedure

If the infrastructure has been destroyed and needs to be recreated:

### Step 1

Authenticate AWS:

```powershell
aws sts get-caller-identity
```

### Step 2

Go to:

```text
terraform/environments/eks
```

### Step 3

Initialize:

```powershell
terraform init
```

### Step 4

Validate:

```powershell
terraform validate
```

### Step 5

Plan:

```powershell
terraform plan
```

### Step 6

Apply:

```powershell
terraform apply
```

### Step 7

Configure kubectl:

```powershell
aws eks update-kubeconfig --region ap-south-1 --name eks-cicd
```

### Step 8

Verify nodes:

```powershell
kubectl get nodes
```

### Step 9

Deploy DEV:

```powershell
kubectl apply -k .\k8s\overlays\dev
```

### Step 10

Deploy STAGING:

```powershell
kubectl apply -k .\k8s\overlays\staging
```

### Step 11

Deploy PROD:

```powershell
kubectl apply -k .\k8s\overlays\prod
```

### Step 12

Verify:

```powershell
kubectl get deployments,pods,services -n dev
kubectl get deployments,pods,services -n staging
kubectl get deployments,pods,services -n prod
```

---

# 30. Terraform Destroy

When intentionally destroying the lab infrastructure:

```powershell
terraform plan -destroy
```

Review the resources carefully.

Then:

```powershell
terraform destroy
```

Confirm:

```text
yes
```

Terraform will remove the infrastructure it manages.

## Important

Destroying the EKS cluster removes the Kubernetes workloads running inside that cluster.

The Terraform state and configuration should be preserved in Git.

---

# 31. After Terraform Recreate

After:

```powershell
terraform apply
```

the local Kubernetes context may need to be refreshed:

```powershell
aws eks update-kubeconfig --region ap-south-1 --name eks-cicd
```

Then:

```powershell
kubectl get nodes
```

and redeploy the application:

```powershell
kubectl apply -k .\k8s\overlays\dev
kubectl apply -k .\k8s\overlays\staging
kubectl apply -k .\k8s\overlays\prod
```

---

# 32. Current Project State

Completed:

```text
[✓] FastAPI application
[✓] Application tests
[✓] Dockerfile
[✓] Docker Compose
[✓] Docker image
[✓] ECR repository
[✓] Terraform VPC
[✓] Terraform EKS
[✓] Terraform ECR
[✓] EKS cluster
[✓] EKS managed node group
[✓] kubectl configuration
[✓] Kubernetes base manifests
[✓] Kustomize
[✓] DEV namespace
[✓] STAGING namespace
[✓] PROD namespace
[✓] DEV deployment
[✓] STAGING deployment
[✓] PROD deployment
[✓] Git checkpoint
```

Current application image:

```text
v1.0.0
```

---

# 33. Next Phase

The next phase is Jenkins CI.

Planned pipeline:

```text
Developer
    │
    │ git push
    ▼
GitHub
    │
    ▼
Jenkins
    │
    ├── Checkout
    │
    ├── Install dependencies
    │
    ├── Run pytest
    │
    ├── Build Docker image
    │
    ├── Security scanning
    │
    ├── Login to ECR
    │
    └── Push image
```

Then CD will be added:

```text
ECR
 │
 ▼
DEV
 │
 ▼
STAGING
 │
 ▼
PROD
```

Later phases:

```text
Rolling Updates
      ↓
Rollback
      ↓
Helm
      ↓
Observability
      ↓
Security
      ↓
Blue/Green Deployment
      ↓
Automated Rollback
      ↓
Production Hardening
```

---

# 34. Quick Rebuild Cheat Sheet

For normal infrastructure recreation:

```powershell
cd "C:\Users\Earnest.Ebenezer\OneDrive - Swan Solution\Desktop\Cloud Automation\Kubernetes_Lab\AWS_EKS_TF\terraform\environments\eks"

aws sts get-caller-identity

terraform init

terraform fmt -recursive

terraform validate

terraform plan

terraform apply
```

Then:

```powershell
aws eks update-kubeconfig --region ap-south-1 --name eks-cicd

kubectl get nodes

kubectl get pods -n kube-system
```

Deploy environments:

```powershell
kubectl apply -k .\k8s\overlays\dev

kubectl apply -k .\k8s\overlays\staging

kubectl apply -k .\k8s\overlays\prod
```

Verify:

```powershell
kubectl get deployments,pods,services -n dev

kubectl get deployments,pods,services -n staging

kubectl get deployments,pods,services -n prod
```

Final check:

```powershell
kubectl get namespaces
```

At that point, the EKS + Kubernetes environment is ready for the Jenkins phase.

10. And how does kubectl know about AWS?

Remember when we ran:

aws eks update-kubeconfig `
  --region ap-south-1 `
  --name eks-cicd

That configured your local:

C:\Users\Earnest.Ebenezer\.kube\config

Your kubeconfig contains information telling kubectl:

Kubernetes cluster:
eks-cicd

AWS region:
ap-south-1

API server:
https://...

And authentication is integrated with AWS.