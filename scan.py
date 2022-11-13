import json
from queries import *

if __name__ == '__main__':
    # pre-process website names
    website_file = sys.argv[1]
    websites = process_txt(website_file)
    # create dictionary + populate entries:
    domain_information = {}
    for website in websites[:10]:
        # set scan time
        domain_information[website] = {"scan_time": time.time()}
        # set ipv4 addresses
        ipv4_list = get_ipv4(website)
        if len(ipv4_list) != 0:
            domain_information[website]["ipv4_addresses"] = ipv4_list
        # # set ipv6 addresses
        # ipv6_list = get_ipv6(website)
        # if len(ipv6_list) != 0:
        #     domain_information[website]["ipv6_addresses"] = ipv6_list
        # # set http server
        # domain_information[website]["http_server"] = get_http_server(website)
        # # set insecure http request
        # is_insecure = get_insecure_http(ipv4_list[0])
        # domain_information[website]["insecure_http"] = is_insecure
        # # set redirect_to_https
        # if is_insecure:
        #     domain_information[website]["redirect_to_https"] = get_redirect_to_https(website)
        # else:
        #     domain_information[website]["redirect_to_https"] = False
        # # set hsts
        # domain_information[website]["hsts"] = get_hsts(website)
        # # set tls versions
        # domain_information[website]["tls_versions"] = get_tls_versions(website)
        # # # set root ca
        # domain_information[website]["root_ca"] = get_root_ca(website)
        # # set rdns
        # domain_information[website]["rdns_names"] = get_rdns(ipv4_list)
        # set rtt
        # domain_information[website]["rtt_range"] = get_RTT(ipv4_list)
        # set geo location
        domain_information[website]["geo_locations"] = get_geo_location(ipv4_list)

    # write data to output file:
    output_file = sys.argv[2]
    with open(output_file, "w") as f:
        json.dump(domain_information, f, sort_keys=True, indent=4)
