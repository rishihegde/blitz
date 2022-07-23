terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.21.0"
    }
  }
}

provider "aws" {
  profile = "default"
  region  = var.region
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.14.2"

  name = var.vpc_name
  cidr = var.cidr

  azs             = var.azs
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets

  enable_nat_gateway = var.enable_nat_gateway

  tags = {
    Terraform = "true"
  }
}

# resource "aws_ec2_tag" "private_subnet_tag" {
#   for_each    = toset(var.azs)
#   resource_id = module.vpc.private_subnets["${index(var.azs, each.value)}"]
#   key         = "Name"
#   value       = "${var.vpc_name}-private-${substr(each.value, length(each.value) - 1, 1)}"
# }

# resource "aws_ec2_tag" "public_subnet_tag" {
#   resource_id = module.vpc.private_subnets[0]
#   key         = "Name"
#   value       = "nprod-net-app-${substr(each.value,length(each.value)-2,2)}"
# }
