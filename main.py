import sys, time, json



if __name__ == '__main__':
    # pre-process website names
    website_file = sys.argv[1]
    with open(website_file, "r") as websites:
        websites = websites.readlines()
    for index, website in enumerate(websites):
        websites[index] = website.strip()
    # create dictionary + populate entries:
    domain_information = {}
    for website in websites:
        domain_information[website] = {"scan_time": time.time()}

    # write data to output file:
    output_file = sys.argv[2]
    with open(output_file, "w") as f:
        json.dump(domain_information, f, sort_keys=True, indent=4)
