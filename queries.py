import http.client
import subprocess
import sys
import socket



def get_redirect_to_https(website):
    return rec_get_redirect_to_https(website, 1)


def rec_get_redirect_to_https(website, iter):
    if iter == 10:
        return False
    try:
        result = subprocess.check_output(["curl", "-I", website],
                                         timeout=4, stderr=subprocess.STDOUT).decode("utf - 8")
        stat = result[result.find("HTTP/"):]
        stat = int(stat[stat.find(" ") + 1:stat.find(" ") + 4])
        if not 300 <= stat < 310:
            return False
        location = result[result.find("ocation: ") + len("ocation: "):]
        redirect_link = location[:location.find('\r\n')]
        if redirect_link is not None and "https:" in redirect_link:
            return True
        else:
            if redirect_link is not None and "http://" in redirect_link:
                return rec_get_redirect_to_https(redirect_link, iter + 1)
            return False
    except subprocess.TimeoutExpired:
        return None


def get_insecure_http(ip):
    try:
        result = subprocess.check_output(["nmap", ip, "-p", "80"],
                                         timeout=4, stderr=subprocess.STDOUT).decode("utf - 8")
        answer = result[result.find("80/tcp"):][:result.find("\n")]
        if "80/tcp open  http" in answer:
            return True
        else:
            return False
    except subprocess.TimeoutExpired:
        return None


def get_http_server(website):
    try:
        connection = http.client.HTTPSConnection(website, timeout=2)
        connection.request("GET", "/")
        response = connection.getresponse()
        return response.getheader("Server")
    except socket.timeout:
        return None


def process_txt(file):
    with open(file, "r") as f:
        lines = f.readlines()
    for index, line in enumerate(lines):
        lines[index] = line.strip()
    return lines


def get_ipv4(website):
    return get_ip(website, 'a')


def get_ipv6(website):
    return get_ip(website, 'aaaa')


def get_ip(website, type):
    dns_servers = process_txt("dns-servers.txt")
    ip_arr = set()
    for dns_server in dns_servers:
        try:
            result = subprocess.check_output(["nslookup", f"-type={type}", website, dns_server],
                                             timeout=2, stderr=subprocess.STDOUT).decode("utf - 8")
            output = result[result.find("answer:"):].split("\n")
            for data in output:
                if 'Address' in data:
                    ip_arr.add(data.replace('Address: ', ''))
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            continue
        # except subprocess.CalledProcessError:
        #     continue
        except FileNotFoundError:
            sys.stderr.write("Command-line tool 'nslookup' not found\n")
            break

    return list(ip_arr)
