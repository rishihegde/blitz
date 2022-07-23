vpc_name           = "devvpc1"
region             = "ap-south-1"
cidr               = "10.0.0.0/16"
azs                = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
private_subnets    = ["10.0.0.0/21", "10.0.8.0/21", "10.0.16.0/21"]
public_subnets     = ["10.0.24.0/24", "10.0.25.0/24", "10.0.26.0/24"]
enable_nat_gateway = false