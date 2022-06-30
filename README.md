This script is a prototype for demo purposes. In rare events after MS firmware upgrades access ports may initialize before the uplink path causing
802.1x clients to fail authentication and be moved to either the guest vlan or the failed auth vlan. This will determine those clients and cycle the switchports
causing a new auth event. This removes the need to go to each port individually and manually cycle switch ports.
