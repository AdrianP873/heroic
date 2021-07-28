data "aws_ami" "amazon-linux-2" {
 most_recent = true
 owners      = ["amazon"]

 filter {
   name   = "owner-alias"
   values = ["amazon"]
 }


 filter {
   name   = "name"
   values = ["amzn2-ami-hvm*"]
 }
}

resource "aws_instance" "control_plane_node" {
  ami           = data.aws_ami.amazon-linux-2.id
  instance_type = "t3a.small"

  associate_public_ip_address = true
  key_name = "heroic-kp"
  vpc_security_group_ids = tolist([aws_security_group.k8s_cluster_sg.id])

 # user_data = file("../scripts/install_kubeadm.sh")

  tags = local.common_tags
}


# resource "aws_instance" "worker_node" {
#   ami           = data.aws_ami.amazon-linux-2.id
#   instance_type = "t2.medium"

#   tags = local.common_tags
# }

resource "aws_security_group" "k8s_cluster_sg" {
  name        = "heroic-cluster-sg-${var.env}"
  description = "K8s cluster security group allowing communication between control plane and worker nodes."
  vpc_id      = var.vpc_id

  ingress {
    description = "Allow inbound to Kubernetes API Server."
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    self        = true
  }

  ingress {
    description = "Allow inbound to etcd server client API."
    from_port   = 2379
    to_port     = 2380
    protocol    = "tcp"
    self        = true
  }

 ingress {
    description = "Allow inbound to kubelet API, kube-scheduler and kube-controller-manager."
    from_port   = 10250
    to_port     = 10252
    protocol    = "tcp"
    self        = true
  }

  tags = local.common_tags


    # https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#control-plane-node-s
}