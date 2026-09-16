
# Terraform Apply → ECR Push

Run everything from:

```powershell
cd "C:\Users\Earnest.Ebenezer\OneDrive - Swan Solution\Desktop\Cloud Automation\Kubernetes_Lab\AWS_EKS_TF\terraform\environments\eks\dev"
```

## 1. Terraform

```powershell
terraform validate
terraform plan
terraform apply
```

After `terraform apply` completes, verify the ECR repository:

```powershell
aws ecr describe-repositories --repository-names eks-cicd-demo --region ap-south-1
```

---

## 2. Verify Local Docker Image

```powershell
docker images
```

You should have:

```text
eks-cicd-demo    v1.0.0
```

---

## 3. Login to Amazon ECR

```powershell
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 891048843822.dkr.ecr.ap-south-1.amazonaws.com
```

Expected:

```text
Login Succeeded
```

---

## 4. Tag the Docker Image for ECR

```powershell
docker tag eks-cicd-demo:v1.0.0 891048843822.dkr.ecr.ap-south-1.amazonaws.com/eks-cicd-demo:v1.0.0
```

Verify:

```powershell
docker images
```

You should now see both:

```text
eks-cicd-demo    v1.0.0
891048843822.dkr.ecr.ap-south-1.amazonaws.com/eks-cicd-demo    v1.0.0
```

---

## 5. Push Image to ECR

```powershell
docker push 891048843822.dkr.ecr.ap-south-1.amazonaws.com/eks-cicd-demo:v1.0.0
```

---

## 6. Verify Image in ECR

```powershell
aws ecr describe-images --repository-name eks-cicd-demo --region ap-south-1
```

Look for:

```text
imageTags:
    - v1.0.0
```

and the image digest.

### Complete command sequence

If you want the entire workflow as one copy-paste block:

```powershell
cd "C:\Users\Earnest.Ebenezer\OneDrive - Swan Solution\Desktop\Cloud Automation\Kubernetes_Lab\AWS_EKS_TF\terraform\environments\eks\dev"

terraform validate
terraform plan
terraform apply

aws ecr describe-repositories --repository-names eks-cicd-demo --region ap-south-1

docker images

aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 891048843822.dkr.ecr.ap-south-1.amazonaws.com

docker tag eks-cicd-demo:v1.0.0 891048843822.dkr.ecr.ap-south-1.amazonaws.com/eks-cicd-demo:v1.0.0

docker images

docker push 891048843822.dkr.ecr.ap-south-1.amazonaws.com/eks-cicd-demo:v1.0.0

aws ecr describe-images --repository-name eks-cicd-demo --region ap-south-1
```

**Note:** `docker tag` is required. `docker push` cannot push `eks-cicd-demo:v1.0.0` directly because Docker needs the ECR repository URL attached to the image tag.
