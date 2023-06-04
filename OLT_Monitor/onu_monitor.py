import datetime
import easysnmp

time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ip = '10.104.0.1'
ro = '102.217.167.72:9002'

session = easysnmp.Session(
    hostname='10.104.0.1',
    version=2,
    security_level='authNoPriv',
    security_username='admin',
    auth_protocol='AES',
    auth_password='admin'
)



ifDescr = session.walk('.1.3.6.1.2.1.2.2.1.2')
ifAlias = session.walk('IF-MIB::ifAlias')
ifSpeed = session.walk('.1.3.6.1.2.1.2.2.1.5')
ifAdminStatus = session.walk('.1.3.6.1.2.1.2.2.1.7')
ifOperStatus = session.walk('.1.3.6.1.2.1.2.2.1.8')
ifInErrors = session.walk('.1.3.6.1.2.1.2.2.1.14')
ifOutErrors = session.walk('.1.3.6.1.2.1.2.2.1.20')
ONUMAC = session.walk('1.3.6.1.4.1.3320.101.10.1.1.3')
ONURxLevel = session.walk('1.3.6.1.4.1.3320.101.10.5.1.5')
ONUTemp = session.walk('1.3.6.1.4.1.3320.101.10.5.1.2')
ONUDist = session.walk('1.3.6.1.4.1.3320.101.10.1.1.27')
ONUVendor = session.walk('1.3.6.1.4.1.3320.101.10.1.1.1')
ONUModel = session.walk('1.3.6.1.4.1.3320.101.10.1.1.2')
Timeticks = session.walk('iso.3.6.1.2.1.2.2.1.9')
sysuptime = session.walk('SNMPv2-MIB::sysUpTime.0')

# Create a dictionary for storing interface details
iface = {}

# Process the SNMP data
for key, value in ifDescr.items():
    iface[key] = {'IfId': key}
    iface[key]['IfDescr'] = value.split()[-1].strip('"')

for key, value in ifAlias.items():
    iface[key]['IfId'] = key
    iface[key]['ifAlias'] = value.split()[-1].strip('"')

for key, value in Timeticks.items():
    iface[key]['Timeticks'] = value.split()[-1].strip(')').strip()

for key, value in ifSpeed.items():
    iface[key]['IfSpeed'] = value.split(':')[-1].strip()

for key, value in ifAdminStatus.items():
    iface[key]['IfAdminStatus'] = value.split(':')[-1].strip()

for key, value in ifOperStatus.items():
    iface[key]['IfOperStatus'] = value.split(':')[-1].strip()

for key, value in ifInErrors.items():
    iface[key]['IfInErrors'] = value.split(':')[-1].strip()

for key, value in ifOutErrors.items():
    iface[key]['IfOutErrors'] = value.split(':')[-1].strip()
# Print the retrieved data
for key, value in iface.items():
    print(f'Interface {key}: {value}')
