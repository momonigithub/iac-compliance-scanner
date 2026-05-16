resource "aws_iam_role" "wildcard_role" {
  name = "wildcard-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "wildcard_policy" {
  name = "wildcard-policy"
  role = aws_iam_role.wildcard_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "*"
        Effect   = "Allow"
        Resource = "*" # Critical: Wildcard permissions
      },
    ]
  })
}

resource "aws_db_instance" "insecure_db" {
  allocated_storage    = 10
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t3.micro"
  name                 = "mydb"
  username             = "admin"
  password             = "password123" # Critical: Plaintext password (should be secret)
  parameter_group_name = "default.mysql5.7"
  skip_final_snapshot  = true
  publicly_accessible  = true # Critical: Publicly accessible
}
