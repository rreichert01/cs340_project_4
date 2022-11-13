import http.client
import subprocess
import sys
import socket
import requests


def get_tls_versions(website):
    tls_versions = ["TLSv1.3", "TLSv1.2", "TLSv1.1", "TLSv1.0"]
    tls_commands = ["-tls1_3", "-tls1_2", "-tls1_1", "-tls1"]
    return_val = []
    for index, version in enumerate(tls_versions):
        try:
            # print(" ".join(["openssl", "s_client", "-connect", f"{website}:443", tls_commands[index]]))
            result = subprocess.check_output(["openssl", "s_client", "-connect", f"{website}:443", tls_commands[index]],
                                             timeout=2, stderr=subprocess.STDOUT, input=b' ').decode("utf - 8")
            if "-----BEGIN CERTIFICATE-----" in result:
                return_val.append(version)
        except subprocess.CalledProcessError as e:
            # print(f"Process error {version}")
            print(e.output.decode())
            if "Protocol  : TLSv1" in e.output.decode("utf - 8"):
                return_val.append(version)
            continue
        except subprocess.TimeoutExpired:
            print("Timeout")
            continue
        except FileNotFoundError:
            sys.stderr.write("Command-line tool 'openssl' not found\n")
            return []
    return return_val


def get_hsts(website):
    try:
        website = website if website.startswith('http') else ('http://' + website)
        r = requests.get(website, timeout=2)
        if 'Strict-Transport-Security' in r.headers.keys():
            return True
        else:
            return False
    except (requests.exceptions.TooManyRedirects, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
        return False


def get_redirect_to_https(website):
    url = get_redirect(website)
    if "https:" in url:
        return True
    else:
        return False


def get_redirect(website):
    try:
        website = website if website.startswith('http') else ('http://' + website)
        r = requests.get(website, timeout=2)
        if r.status_code == 200:
            return r.url
        else:
            return ""
    except (requests.exceptions.TooManyRedirects, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
        return ""


def get_insecure_http(ip):
    try:
        result = subprocess.check_output(["nmap", ip, "-p", "80"],
                                         timeout=2, stderr=subprocess.STDOUT).decode("utf - 8")
        answer = result[result.find("80/tcp"):][:result.find("\n")]
        if "80/tcp open  http" in answer:
            return True
        else:
            return False
    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        sys.stderr.write("Command-line tool 'nmap' not found\n")
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
