import subprocess


def process_txt(file):
    with open(file, "r") as f:
        lines = f.readlines()
    for index, line in enumerate(lines):
        lines[index] = line.strip()
    return lines


def get_ipv4(website):
    dns_servers = process_txt("dns-servers.txt")
    for dns_server in dns_servers[:3]:
        result = subprocess.check_output(["nslookup", website, dns_server],
                                         timeout=2, stderr=subprocess.STDOUT).decode("utf - 8")
        print(result)
