vpc_name           = "devvpc1"
region             = "ap-south-1"
cidr               = "10.1.0.0/16"
azs                = ["ap-south-1a"]
private_subnets    = ["10.1.1.0/24"]
public_subnets     = ["10.1.11.0/24"]
enable_nat_gateway = false