import http.client
import subprocess
import sys
import socket
import requests
import time
from maxminddb import open_database



def get_geo_location(ipv4_list):
    # mod = __import__('maxminddb', globals=globals())
    with open_database('GeoLite2-City.mmdb') as reader:
        reader.get(ipv4_list[0])


def get_RTT(ipv4_list):
    rtt = [float('inf'), -1]
    for ipv4 in ipv4_list:
        try:
            start_time = time.time()
            requests.get("http://" + ipv4, timeout=3, allow_redirects=False)
            end_time = time.time()
            rtt_n = (end_time - start_time) * 1000
            print(rtt_n)
            if rtt_n < rtt[0]:
                rtt[0] = rtt_n
            if rtt_n > rtt[1]:
                rtt[1] = rtt_n
        except:
            continue
    if rtt == [float('inf'), -1]:
        return None
    return rtt


def get_rdns(ipv4_list):
    rdns = []
    for ipv4 in ipv4_list:
        try:
            result = subprocess.check_output(["dig", "-x", ipv4],
                                             timeout=3, stderr=subprocess.STDOUT).decode("utf - 8")
            if "ANSWER: 0" in result:
                continue
            answers = result[result.find("ANSWER SECTION:\n") + len("ANSWER SECTION:\n"): result.find("\n\n;; "
                                                                                                      "AUTHORITY "
                                                                                                      "SECTION:")].split(
                '\n')
            for answer in answers:
                rdns.append(answer[answer.find("PTR\t") + len("PTR\t"):])
        except subprocess.TimeoutExpired:
            continue
    return rdns


def get_root_ca(website):
    try:
        result = subprocess.check_output(["openssl", "s_client", "-connect", f"{website}:443"],
                                         timeout=3, stderr=subprocess.STDOUT, input=b' ').decode("utf - 8")
        ca = result[result.find("O = ") + len("O = "):]
        if ca[0] == "\"":
            return ca[1:ca[1:].find('\"')]
        return ca[:ca.find(',')]
    except subprocess.TimeoutExpired:
        return None


def get_tls_versions(website):
    tls_versions = ["TLSv1.3", "TLSv1.2", "TLSv1.1", "TLSv1.0"]
    tls_commands = ["-tls1_3", "-tls1_2", "-tls1_1", "-tls1"]
    return_val = []
    for index, version in enumerate(tls_versions):
        try:
            result = subprocess.check_output(["openssl", "s_client", "-connect", f"{website}:443", tls_commands[index]],
                                             timeout=3, stderr=subprocess.STDOUT, input=b' ').decode("utf - 8")
            if "-----BEGIN CERTIFICATE-----" in result:
                return_val.append(version)
        except subprocess.CalledProcessError as e:
            if "SSL-Session:" in e.output.decode("utf - 8"):
                return_val.append(version)
            continue
        except subprocess.TimeoutExpired:
            continue
        except FileNotFoundError:
            sys.stderr.write("Command-line tool 'openssl' not found\n")
            return []
    return return_val


def get_hsts(website):
    try:
        website = website if website.startswith('http') else ('http://' + website)
        r = requests.get(website, timeout=3)
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
        r = requests.get(website, timeout=3)
        if r.status_code == 200:
            return r.url
        else:
            return ""
    except (requests.exceptions.TooManyRedirects, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
        return ""


def get_insecure_http(ip):
    try:
        result = subprocess.check_output(["nmap", ip, "-p", "80"],
                                         timeout=3, stderr=subprocess.STDOUT).decode("utf - 8")
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
        connection = http.client.HTTPSConnection(website, timeout=3)
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
                                             timeout=3, stderr=subprocess.STDOUT).decode("utf - 8")
            output = result[result.find("answer:"):].split("\n")
            for data in output:
                if 'Address' in data:
                    data = data.replace('Address: ', '')
                    data.strip()
                    ip_arr.add(data)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            continue
        # except subprocess.CalledProcessError:
        #     continue
        except FileNotFoundError:
            sys.stderr.write("Command-line tool 'nslookup' not found\n")
            break

    return list(ip_arr)
