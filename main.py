import json
import time

from queries import *

if __name__ == '__main__':
    # pre-process website names
    website_file = sys.argv[1]
    websites = process_txt(website_file)
    # create dictionary + populate entries:
    domain_information = {}
    for website in websites[:2]:
        # set scan time
        domain_information[website] = {"scan_time": time.time()}
        # set ipv4 addresses
        ipv4_list = get_ipv4(website)
        if len(ipv4_list) != 0:
            domain_information[website]["ipv4_addresses"] = ipv4_list
        # set ipv6 addresses
        ipv6_list = get_ipv6(website)
        if len(ipv6_list) != 0:
            domain_information[website]["ipv6_addresses"] = ipv6_list
        # set http server
        domain_information[website]["http_server"] = get_http_server(website)

    # write data to output file:
    output_file = sys.argv[2]
    with open(output_file, "w") as f:
        json.dump(domain_information, f, sort_keys=True, indent=4)
