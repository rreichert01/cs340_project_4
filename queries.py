import http.client
import subprocess
import sys
import socket
import requests
import time
from maxminddb import open_database


def get_sorted_servers(domain_information):
    servers = {}
    for host in domain_information.keys():
        ca = domain_information[host]['http_server']
        if ca is not None:
            if ca in servers.keys():
                servers[ca] += 1
            else:
                servers[ca] = 1
    servers_list = []
    for ca in servers.keys():
        servers_list.append([ca, servers[ca]])
    servers_list.sort(key=lambda x: x[1], reverse=True)
    return servers_list

def get_sorted_root_ca(domain_information):
    root_cas = {}
    for host in domain_information.keys():
        ca = domain_information[host]['root_ca']
        if ca is not None:
            if ca in root_cas.keys():
                root_cas[ca] += 1
            else:
                root_cas[ca] = 1
    root_cas_list = []
    for ca in root_cas.keys():
        root_cas_list.append([ca, root_cas[ca]])
    root_cas_list.sort(key=lambda x: x[1], reverse=True)
    return root_cas_list



def get_sorted_rtt(domain_information):
    all_rtt = []
    for host in domain_information.keys():
        if domain_information[host]['rtt_range'] is not None:
            all_rtt.append([host, domain_information[host]['rtt_range']])
    all_rtt.sort(key=lambda x: x[1][0])
    return all_rtt


def get_geo_location(ipv4_list):
    # mod = __import__('maxminddb', globals=globals())
    ret_val = set()
    with open_database('GeoLite2-City.mmdb') as reader:
        for ipv4 in ipv4_list:
            result = reader.get(ipv4)
            if result is None:
                continue
            keys = result.keys()
            country = ""
            city = ""
            state = ""
            if 'country' in keys:
                country = result["country"]['names']['en']
            elif 'registered_country' in keys:
                country = result["registered_country"]['names']['en']
            if 'subdivisions' in keys:
                state = result['subdivisions'][0]['names']['en'] + ", " if country != "" else ""
            if 'city' in keys:
                city = result["city"]['names']['en'] + ", " if country != "" or state != "" else ""
            ret_val.add(city + state + country)
    return list(ret_val)


def get_RTT(ipv4_list):
    rtt = [float('inf'), -1]
    for ipv4 in ipv4_list:
        try:
            start_time = time.time()
            requests.get("http://" + ipv4, timeout=3, allow_redirects=False)
            end_time = time.time()
            rtt_n = (end_time - start_time) * 1000
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
