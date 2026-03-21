# macOS Network Diagnostics

## Connectivity

```bash
# Ping
ping -c 4 host
ping -c 10 -i 0.5 host                # custom interval
ping -c 4 -s 1472 host                # MTU test
ping -c 4 -t 2 host                   # timeout (macOS uses -t, not -W)
ping6 -c 4 host                       # IPv6

# Traceroute (ICMP by default on macOS)
traceroute host
traceroute -n host                     # skip DNS resolution
traceroute -m 20 host                  # max hops
traceroute -T -p 443 host             # TCP (may need sudo)

# mtr (install: brew install mtr)
sudo mtr host                         # interactive (needs sudo on macOS)
sudo mtr -r -c 10 host               # report mode
```

## DNS

```bash
# dig
dig host
dig +short host
dig host MX
dig host TXT
dig -x IP                             # reverse DNS
dig @8.8.8.8 host                     # specific server
dig +trace host                       # delegation chain

# nslookup
nslookup host
nslookup -type=MX host

# macOS DNS cache flush
sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder

# macOS DNS resolver config
scutil --dns
cat /etc/resolv.conf
```

## Ports and Sockets

macOS does NOT have `ss`. Use `lsof` and `netstat` instead.

```bash
# lsof (primary tool on macOS)
lsof -i                              # all network connections
lsof -i :80                          # specific port
lsof -i TCP                          # TCP only
lsof -i :3000 -sTCP:LISTEN           # listeners on port
lsof -i -P -n                        # skip name resolution (faster)
lsof -i -P -n | grep LISTEN          # all listening ports (like ss -tlnp)

# netstat (macOS version, no -p flag)
netstat -an                           # all connections
netstat -an | grep LISTEN             # listening ports
netstat -rn                           # routing table
netstat -an | grep -c ESTABLISHED     # count established

# nc (netcat)
nc -zv host 80                       # test port
nc -zv -w 3 host 22                  # with timeout
nc -G 3 -zv host 443                 # macOS-specific timeout flag
```

## Network Interfaces

```bash
# ifconfig (primary on macOS, no ip command)
ifconfig
ifconfig en0                          # Wi-Fi (usually en0)
ifconfig en1                          # Ethernet (usually en1)

# Routing
netstat -rn                           # routing table
route get default                     # default gateway

# ARP
arp -a

# DNS
scutil --dns | grep nameserver

# Network service order
networksetup -listallnetworkservices
networksetup -getinfo "Wi-Fi"
networksetup -getdnsservers "Wi-Fi"

# MTU test
ping -c 1 -D -s 1472 host           # macOS uses -D for DF bit
```

## Bandwidth

```bash
# curl download test
curl -s -o /dev/null -w "Speed: %{speed_download} bytes/sec\n" \
  https://speed.cloudflare.com/__down?bytes=100000000

# iperf3 (install: brew install iperf3)
iperf3 -c server
iperf3 -c server -R                  # reverse (download)
```

## Firewall

```bash
# macOS Application Firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps

# pfctl (BSD packet filter)
sudo pfctl -sr                       # show rules
sudo pfctl -si                       # show info
sudo pfctl -ss                       # show state table
```

## macOS-Specific Tools

```bash
# Network Quality (macOS 12+)
networkQuality                        # bandwidth test
networkQuality -v                     # verbose

# Airport (Wi-Fi diagnostics)
/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s  # scan
/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I  # info
```
