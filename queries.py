import subprocess


def process_txt(file):
    with open(file, "r") as f:
        lines = f.readlines()
    for index, line in enumerate(lines):
        lines[index] = line.strip()
    return lines


def get_ip(website):
    dns_servers = process_txt("dns-servers.txt")
    ip_arr = []
    for dns_server in dns_servers[:3]:
        result = subprocess.check_output(["nslookup", website, dns_server],
                                         timeout=2, stderr=subprocess.STDOUT).decode("utf - 8")
        print(result)
        output = result[result.find("answer:"):].split("\n")
        # print(output)
        temp_arr = []
        for data in output:
            if 'Address' in data:
                temp_arr.append(data.replace('Address: ', ''))
        temp_arr.pop(0)
        ip_arr.append(temp_arr)
    print(ip_arr)