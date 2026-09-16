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