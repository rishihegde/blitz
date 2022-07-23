import json, subprocess, os
import ipaddress
import contextvars
import boto3
from jinja2 import Environment, FileSystemLoader
from requests import delete
from app.database import SessionLocal
from app import main

class Helper:
    def __init__(self):
        pass

    def debug(self, message):
        request_id = main.request_id_contextvar.get()
        print(f"({request_id}) {message}")

    def parse_json(self, payload):
        return json.loads(payload)

    def jinja_render(self, folder, template,**kwargs):
        file_loader = FileSystemLoader(folder)
        env = Environment(loader=file_loader)
        template = env.get_template(template)
        output = template.render(**kwargs)
        return output
    
    # Dependency
    def get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def get_regional_availability_zones(self, region):
        client = boto3.client('ec2', region_name=region)
        zones = []
        for zone in client.describe_availability_zones()['AvailabilityZones']:
            zones.append(zone['ZoneName'])
        return zones
    
    def subnet_calculator(self, cidr, private_mask, public_mask, azcount) -> list:
        subnet_count = azcount*2
        subnets = []
        mask = private_mask
        n = ipaddress.ip_network(cidr)
        first_two_octets = '.'.join(str(n[1]).split('.')[:-2])

        ip = cidr.split('/')[0]
        n = ipaddress.ip_network(f"{ip}/{str(mask)}")
        subnets.append(f'{ip}/{str(mask)}')

        while subnet_count > 1:
            # get third octet of last ip
            third_octet_of_last_ip = int(str(n[-2]).split('.')[-2])

            # get third octet of first ip
            third_octet_of_first_ip = int(str(n[1]).split('.')[-2])

            # add third_octet_of_last_ip+1 to it
            third_octet_of_next_ip = third_octet_of_last_ip + 1

            n = ipaddress.ip_network(f"{first_two_octets}.{third_octet_of_next_ip}.0/{str(mask)}")
            subnets.append(f'{first_two_octets}.{third_octet_of_next_ip}.0/{mask}')
            subnet_count -= 1
            if int((azcount*2)/2) == int(len(subnets)):
                mask = public_mask

        return [subnets[:int(len(subnets)/2)],subnets[int(len(subnets)/2):]]

    def delete_network(self, payload):
        workdir = 'tf/modules/network'
        with open(f'{workdir}/terraform.tfstate', 'w') as file:
            file.write(payload['tf_state'])
            file.close()
        
        return self.terraform_commands(['terraform', 'destroy', '--auto-approve'], workdir)

    def create_network(self, payload):
        obj = self.parse_json(payload)

        # interpolate azs and append region to it
        azs = []
        if obj['azs']:
            for az in obj['azs']:
                azs.append(obj['region']+az)
        else:
            azs = self.get_regional_availability_zones(obj['region'])
        
        subnets = self.subnet_calculator(cidr=obj['cidr'], 
                                                private_mask=obj['private_subnet_size'], 
                                                public_mask=obj['public_subnet_size'], 
                                                azcount=len(azs)
                                                )

        private_subnets = subnets[0]
        public_subnets = subnets[1]

        output = self.jinja_render(
            'tf/modules/network', 
            'terraform.tfvars.jinja', 
            vpc_name=obj["name"],
            region=obj["region"],
            cidr=obj["cidr"],
            azs=json.dumps(azs),
            enable_nat_gateway=str(obj["enable_nat_gateway"]).lower(),
            private_subnets=json.dumps(private_subnets),
            public_subnets=json.dumps(public_subnets)
            )

        with open(f'tf/modules/network/terraform.tfvars', 'w') as file:
            file.write(output)
            file.close()
        
        workdir = 'tf/modules/network'
        self.terraform_commands(['terraform', 'init'], workdir)
        self.terraform_commands(['terraform', 'plan'], workdir)
        self.terraform_commands(['terraform', 'apply', '--auto-approve'], workdir)

        with open(f'tf/modules/network/terraform.tfstate', 'r') as file:
            state = file.read()
            file.close()
        
        s = json.loads(state)
        for resource in s['resources']:
            if resource['type'] == 'aws_vpc':
                vpc_id = resource['instances'][0]['attributes']['id']
        
        #os.rename(f'{workdir}/terraform.tfstate', f'{workdir}/terraform.tfstate.og')

        return {'output': output, 'vpc_id': vpc_id, 'state': state}
    
    def terraform_commands(self, command, workdir):
        return subprocess.check_output(command, cwd=workdir, shell=True)
    
    def terraform_variables(self, 
                            state: str, 
                            bucket_region: str, 
                            bucket_name: str, 
                            bucket_key: str
                            ):
        with open("tf/terraform.tfvars.template", "r") as file:
            template = file.read()
            template = template.replace("{{state}}", state)
            template = template.replace("{{bucket_region}}", bucket_region)
            template = template.replace("{{bucket_name}}", bucket_name)
            template = template.replace("{{bucket_key}}", bucket_key)
            template = template.replace('\'','\"')
            file.close()
        t = open("tf/terraform.tfvars", "w")
        t.write(template)
        t.close()
        return template
    
    def run_command(self, command, workdir):
        return subprocess.check_output(command, cwd=workdir, shell=True)

helper = Helper()