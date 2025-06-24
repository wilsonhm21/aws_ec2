variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "ami_id" {}
variable "instance_type" {
  default = "t2.micro"
}

variable "key_name" {}

variable "output_bucket_name" {}
variable "rds_host" {}
variable "rds_user" {}
variable "rds_pass" {
  sensitive = true
}
variable "rds_db" {}
