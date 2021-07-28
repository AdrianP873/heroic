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


resource "aws_iam_instance_profile" "kubeadm_profile" {
  name = "kubeadm-profile"
  role = aws_iam_role.kubeadm_role.name
}

resource "aws_iam_role" "kubeadm_role" {
  name = "kubeadm-role"
  path = "/"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "kubeadm_ecr_policy_attachment" {
  role       = aws_iam_role.kubeadm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
}

resource "aws_iam_role_policy_attachment" "kubeadm_ssm_policy_attachment" {
  role       = aws_iam_role.kubeadm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMFullAccess"
}

resource "aws_instance" "control_plane_node" {
  ami           = data.aws_ami.amazon-linux-2.id
  instance_type = "t3a.small"
  iam_instance_profile = aws_iam_instance_profile.kubeadm_profile.id

  associate_public_ip_address = true
  key_name = "heroic-kp"
  vpc_security_group_ids = tolist([aws_security_group.k8s_cluster_sg.id])

  user_data = file("../scripts/install_kubeadm_control_plane.sh")

  tags = merge(local.common_tags, {Name="control-plane"})
}

resource "aws_instance" "worker_node" {
  ami           = data.aws_ami.amazon-linux-2.id
  instance_type = "t2.medium"
  iam_instance_profile = aws_iam_instance_profile.kubeadm_profile.id

  associate_public_ip_address = true
  key_name = "heroic-kp"
  vpc_security_group_ids = tolist([aws_security_group.k8s_cluster_sg.id])

  tags = merge(local.common_tags, {Name="worker-node"})

  depends_on = [
    aws_instance.control_plane_node
  ]
}

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

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = local.common_tags


    # https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#control-plane-node-s
}