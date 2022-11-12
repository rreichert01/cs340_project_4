import subprocess


def process_txt(file):
    with open(file, "r") as f:
        lines = f.readlines()
    for index, line in enumerate(lines):
        lines[index] = line.strip()
    return lines


def get_ipv4(website):
    return get_ip(website, 'a')


def get_ip(website, type):
    dns_servers = process_txt("dns-servers.txt")
    ip_arr = []
    for dns_server in dns_servers:
        result = subprocess.check_output(["nslookup", f"-type={type}", website, dns_server],
                                         timeout=2, stderr=subprocess.STDOUT).decode("utf - 8")
        output = result[result.find("answer:"):].split("\n")
        for data in output:
            if 'Address' in data:
                ip_arr.append(data.replace('Address: ', ''))
    print(ip_arr)
