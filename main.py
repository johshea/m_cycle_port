#pip3 install meraki
#run: python3 main.py
#
#Client must be online to be visible and report client status
import meraki, sys, datetime, csv
from pathlib import Path




def main():

    #Define any constants
    lookback = 600  #duration in seconds to look back in time for client data
    guestvlan = '120' #vlan id for filter
    #static constants if desired
    #arg_apikey = ''
    #arg_orgname = ''
    #arg_network = ''

    #Collect user information values #comment out the below blocks if you want static variables
    while True:
        try:
            arg_apikey = input("Please enter your API Key: ")
            if arg_apikey != "":
                break
            print("Enter a valid API key!")
        except Exception as e:
            print(e)

    while True:
        try:
            arg_orgname = input("please enter your Organization Name: ")
            if arg_orgname != "":
                break
            print("Enter your Organization name!")
        except Exception as e:
            print(e)

    while True:
        try:
            arg_network = input("Please enter the Network Name: ")
            if arg_network != "":
                break
            print("Enter your Network name!")
        except Exception as e:
            print(e)

    #set Date/Time Format
    timenow = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    #Begin data collection
    dashboard = meraki.DashboardAPI(arg_apikey, suppress_logging=True)

    #get organization id corresponding to org name provided by user
    org = dashboard.organizations.getOrganizations()

    for record in org:
        if record['name'].lower() == arg_orgname.lower():
            orgid = record['id']
        elif record['name'] == 'null':
            print('ERROR: Fetching organization failed')
            sys.exit(2)

    #get network list for fetched org id
    nwlist = dashboard.organizations.getOrganizationNetworks(orgid, total_pages='all')
    if nwlist[0]['id'] == 'null':
        print('ERROR: Fetching network list failed')
        sys.exit(2)

    #get devices in network
    log = []
    swports = []

    for nwrecord in nwlist:
        if nwrecord['name'].lower() == arg_network.lower():
            clientlist = dashboard.networks.getNetworkClients(
                nwrecord['id'], total_pages='all', timespan=lookback)

            for client in clientlist:
                if client['vlan'] == guestvlan:
                    print(f"Switch Port {client['switchport']} on Switch {client['recentDeviceName']}  Found in Vlan {guestvlan}, this port will be cycled!")
                    swports.append({'serial': client['recentDeviceSerial'], 'name': client["recentDeviceName"], 'port': client['switchport']})

    #cycle collected ports
    if len(swports) > 0:
        for swport in swports:
            try:
                cycleport = dashboard.switch.cycleDeviceSwitchPorts(swport['serial'], [swport['port']])
                print(f"Port {swport['port']} on Switch {swport['name']} has been cycled")
                log.append(swport)

            except Exception as e:
                print(e)

    else:
        print(f"No clients were found to be in vlan {guestvlan}.")

    #Output cycled ports to Log CSV
    if len(log) > 0:
        keys = log[0].keys()
        filename = 'ports_cycled' + str(timenow) + '.csv'
        inpath = Path.cwd() / filename
        with inpath.open(mode='w+', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(log)

    print("Good Bye, and have a great day!")


if __name__ == '__main__':
    main()
