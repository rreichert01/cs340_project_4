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
    out_file.close()
    # print(table.draw())
