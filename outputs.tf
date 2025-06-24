output "ec2_public_ip" {
  value = aws_instance.web_app.public_ip
}
    