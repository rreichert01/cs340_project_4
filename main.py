import sys, time, json
from queries import *

if __name__ == '__main__':
    # pre-process website names
    website_file = sys.argv[1]
    websites = process_txt(website_file)
    # create dictionary + populate entries:
    domain_information = {}
    for website in websites[:1]:
        domain_information[website] = {"scan_time": time.time()}
        get_ip(website)

    # write data to output file:
    output_file = sys.argv[2]
    with open(output_file, "w") as f:
        json.dump(domain_information, f, sort_keys=True, indent=4)

