provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "web_app" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  user_data_base64 = base64encode(templatefile("${path.module}/user_data.sh", {
    bucket_name = var.output_bucket_name,
    rds_host    = var.rds_host,
    rds_user    = var.rds_user,
    rds_pass    = var.rds_pass,
    rds_db      = var.rds_db
  }))

  tags = {
    Name = "FlaskAppEC2"
  }
}

resource "aws_security_group" "web_sg" {
  name        = "web-flask-sg2"
  description = "Allow HTTP traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
