#!/usr/bin/env bash

set -euo pipefail

echo "============================================================"
echo " Jenkins + AWS + Docker + kubectl Ubuntu Setup"
echo "============================================================"

# ------------------------------------------------------------
# 0. Basic variables
# ------------------------------------------------------------

AWS_REGION="ap-south-1"
EKS_CLUSTER="eks-cicd"

echo
echo "[1/15] Checking OS..."
cat /etc/os-release

echo
echo "[2/15] Updating system..."
sudo apt update
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y


# ------------------------------------------------------------
# 1. Install base packages
# ------------------------------------------------------------

echo
echo "[3/15] Installing base packages..."

sudo apt install -y \
    curl \
    wget \
    unzip \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    apt-transport-https \
    fontconfig \
    software-properties-common \
    python3 \
    python3-pip \
    python3-venv


# ------------------------------------------------------------
# 2. Java 21
# ------------------------------------------------------------

echo
echo "[4/15] Installing Java 21..."

sudo apt install -y openjdk-21-jre

echo
echo "Java version:"
java -version


# ------------------------------------------------------------
# 3. Install Jenkins
# ------------------------------------------------------------

echo
echo "[5/15] Installing Jenkins..."

sudo mkdir -p /etc/apt/keyrings

sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc \
    https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key

echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" \
    | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install -y jenkins

sudo systemctl enable jenkins
sudo systemctl start jenkins

echo
echo "Jenkins status:"
sudo systemctl status jenkins --no-pager


# ------------------------------------------------------------
# 4. Install Docker
# ------------------------------------------------------------

echo
echo "[6/15] Installing Docker..."

sudo apt install -y docker.io

sudo systemctl enable docker
sudo systemctl start docker

echo
echo "Docker version:"
sudo docker --version


# ------------------------------------------------------------
# 5. Add Jenkins to Docker group
# ------------------------------------------------------------

echo
echo "[7/15] Configuring Docker permissions..."

sudo usermod -aG docker jenkins

echo
echo "Jenkins groups:"
id jenkins

sudo systemctl restart jenkins


# ------------------------------------------------------------
# 6. Add Ubuntu user to Docker group
# ------------------------------------------------------------

echo
echo "[8/15] Adding current user to Docker group..."

sudo usermod -aG docker "$USER"

echo
echo "NOTE:"
echo "Log out and log back in after this script."
echo "The current shell will not automatically receive the new group."
echo


# ------------------------------------------------------------
# 7. Install AWS CLI v2
# ------------------------------------------------------------

echo
echo "[9/15] Installing AWS CLI v2..."

cd /tmp

rm -f awscliv2.zip
rm -rf aws

curl -fsSL \
    "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" \
    -o awscliv2.zip

unzip -q awscliv2.zip

sudo ./aws/install \
    --bin-dir /usr/local/bin \
    --install-dir /usr/local/aws-cli \
    --update

echo
echo "AWS CLI version:"
aws --version


# ------------------------------------------------------------
# 8. Install kubectl
# ------------------------------------------------------------

echo
echo "[10/15] Installing kubectl..."

cd /tmp

KUBECTL_VERSION="$(curl -L -s https://dl.k8s.io/release/stable.txt)"

echo "Installing kubectl ${KUBECTL_VERSION}"

curl -fsSL \
    "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    -o kubectl

sudo install \
    -o root \
    -g root \
    -m 0755 \
    kubectl \
    /usr/local/bin/kubectl

echo
echo "kubectl version:"
kubectl version --client


# ------------------------------------------------------------
# 9. Verify Jenkins can access required tools
# ------------------------------------------------------------

echo
echo "[11/15] Verifying tools as Jenkins user..."

echo
echo "Git:"
sudo -u jenkins git --version

echo
echo "Docker:"
sudo -u jenkins docker --version

echo
echo "AWS CLI:"
sudo -u jenkins aws --version

echo
echo "kubectl:"
sudo -u jenkins kubectl version --client

echo
echo "Python:"
sudo -u jenkins python3 --version


# ------------------------------------------------------------
# 10. AWS CLI configuration
# ------------------------------------------------------------

echo
echo "[12/15] Configuring AWS CLI..."
echo
echo "IMPORTANT:"
echo "Enter credentials for the Jenkins IAM user when prompted."
echo "Do NOT put credentials directly into this script."
echo

aws configure

echo
echo "AWS identity:"
aws sts get-caller-identity


# ------------------------------------------------------------
# 11. Test EKS access from the Ubuntu user
# ------------------------------------------------------------

echo
echo "[13/15] Testing EKS kubeconfig..."

rm -f /tmp/eks-config

aws eks update-kubeconfig \
    --region "$AWS_REGION" \
    --name "$EKS_CLUSTER" \
    --kubeconfig /tmp/eks-config

echo
echo "Testing Kubernetes API..."

KUBECONFIG=/tmp/eks-config kubectl get nodes || true

echo
echo "NOTE:"
echo "If kubectl says:"
echo "  the server has asked for the client to provide credentials"
echo
echo "that means the AWS exec authentication inside kubeconfig"
echo "needs further investigation. Do not copy AWS credentials"
echo "into kubeconfig."


# ------------------------------------------------------------
# 12. Jenkins initial password
# ------------------------------------------------------------

echo
echo "[14/15] Jenkins initial admin password..."

if sudo test -f /var/lib/jenkins/secrets/initialAdminPassword; then

    echo
    echo "============================================================"
    echo "JENKINS INITIAL ADMIN PASSWORD"
    echo "============================================================"

    sudo cat /var/lib/jenkins/secrets/initialAdminPassword

    echo
    echo "============================================================"

else
    echo "Initial password file not found."
    echo "Jenkins may already have been initialized."
fi


# ------------------------------------------------------------
# 13. Resource diagnostics
# ------------------------------------------------------------

echo
echo "[15/15] System resource diagnostics..."

echo
echo "---------------- MEMORY ----------------"
free -h

echo
echo "---------------- DISK ----------------"
df -h

echo
echo "---------------- JENKINS ----------------"
sudo systemctl status jenkins --no-pager

echo
echo "---------------- TOP PROCESSES ----------------"
ps -eo pid,user,%mem,%cpu,rss,cmd --sort=-rss | head -15


# ------------------------------------------------------------
# Final
# ------------------------------------------------------------

echo
echo "============================================================"
echo " SETUP COMPLETE"
echo "============================================================"

echo
echo "Next actions:"
echo
echo "1. Log out and log back in so the docker group is applied."
echo
echo "2. Verify:"
echo "     docker ps"
echo
echo "3. Verify Jenkins:"
echo "     sudo systemctl status jenkins"
echo
echo "4. Open:"
echo "     http://<VM-IP>:8080"
echo
echo "5. Complete Jenkins initial setup."
echo
echo "6. Install/configure Jenkins plugins."
echo
echo "7. Add AWS credentials to Jenkins."
echo
echo "8. Configure Pipeline from SCM."
echo
echo "9. Configure GitHub webhook."
echo
echo "============================================================"