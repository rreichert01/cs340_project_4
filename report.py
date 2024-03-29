from queries import *
from texttable import Texttable
import json


if __name__ == '__main__':
    json_file = json.load(open(sys.argv[1]))
    out_file = open(sys.argv[2], 'w')

    information_categories = ['hostname', 'geo_locations', 'hsts', 'http_server', 'insecure_http', 'ipv4_addresses',
                              'ipv6_addresses', 'rdns_names', 'redirect_to_https', 'root_ca', 'rtt_range', 'scan_time',
                              'tls_versions']
    table = Texttable()
    table.set_cols_align(["c", "l"])
    # do big data dump
    for hostname in json_file.keys():
        table.header(["Hostname: ", hostname])
        for category in information_categories[1:]:
            row = [category]
            if category in json_file[hostname].keys():
                row.append(json_file[hostname][category])
            else:
                row.append(None)
            table.add_row(row)
        out_file.writelines(table.draw() + '\n\n\n')
        # print(table.draw())
        table.reset()
    # do rtt dump
    sorted_rrt = get_sorted_rtt(json_file)
    table.header(["Hostname:", "RTT"])
    for entry in sorted_rrt:
        table.add_row(entry)
    out_file.writelines(table.draw() + '\n\n\n')
    table.reset()
    # do root ca dump
    sorted_cas = get_sorted_root_ca(json_file)
    table.header(["CA:", "Count"])
    for entry in sorted_cas:
        table.add_row(entry)
    out_file.writelines(table.draw() + '\n\n\n')
    table.reset()
    # do web server dump
    sorted_server = get_sorted_servers(json_file)
    table.header(["Server:", "Count"])
    for entry in sorted_server:
        table.add_row(entry)
    out_file.writelines(table.draw() + '\n\n\n')
    table.reset()

    table.header(["Feature", "% Supporting"])
    # do get TLS stats
    tls_stats = get_tls_stats(json_file)
    for tls_stat in tls_stats.keys():
        table.add_row([tls_stat, tls_stats[tls_stat]])
    # do get insecure_http stats
    insecure_http_stat = get_insecure_http_stats(json_file)
    table.add_row(["Plain http", insecure_http_stat])
    # do get redirect_to_https stats
    redirect_http_stat = get_redirect_http_stats(json_file)
    table.add_row(["Redirect to https", redirect_http_stat])
    # do get hsts stats
    hsts_stat = get_hsts_stats(json_file)
    table.add_row(["Hsts enabled", hsts_stat])
    # do get ipv6 stats
    ipv6_stat = get_ipv6_stats(json_file)
    table.add_row(["ipv6", ipv6_stat])
    out_file.writelines(table.draw() + '\n\n\n')

    out_file.close()
    # print(table.draw())
