#!/bin/sh

#  Let iptables see bridged traffic
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF

# Install Docker
yum update -y
amazon-linux-extras install docker -y

mkdir /etc/docker
cat <<EOF | sudo tee /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF

systemctl enable docker
systemctl daemon-reload
systemctl restart docker
usermod -a -G docker ec2-user # Can maybe remove this. It allows ec2-user to issue docker commands without sudo

# Install kubadm, kubelet and kubectl
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-\$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
exclude=kubelet kubeadm kubectl
EOF

yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

systemctl enable --now kubelet

# Create cluster with kubeadm
kubeadm init --pod-network-cidr=172.31.0.0/16

sleep 60

mkdir -p /home/ec2-user/.kube
cp -i /etc/kubernetes/admin.conf /home/ec2-user/.kube/config
chown 1000:1000 /home/ec2-user/.kube/config

export KUBECONFIG=/etc/kubernetes/admin.conf

sleep 60

# Apply a pod network to the cluster
kubectl apply -f https://raw.githubusercontent.com/aws/amazon-vpc-cni-k8s/master/config/master/aws-k8s-cni.yaml

# Configure kubelet for aws cni and restart service
sed -i "/volumeStatsAggPeriod: 0s$/a\
\networkPlugin: cni\n\
cniConfDir: /etc/cni/net.d\n\
cniBinDir: /opt/cni/bin\n\
nodeIp: $(curl http://169.254.169.254/latest/meta-data/local-ipv4)" config.yaml

systemctl restart kubelet

# Allow workloads to be scheduled to the master node
kubectl taint nodes `hostname`  node-role.kubernetes.io/master:NoSchedule-

# Need to genereate a token with `kubeadm token create` on the control plane, and somehow pass it here. This is a secret value.
DISCOVERY_TOKEN=$(openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | \
   openssl dgst -sha256 -hex | sed 's/^.* //')