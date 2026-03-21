# Linux Network Diagnostics

## Connectivity

```bash
# Ping
ping -c 4 host
ping -c 10 -i 0.5 host                # custom interval
ping -c 4 -s 1472 host                # MTU test (1472 + 28 = 1500)
ping -c 4 -W 2 host                   # per-packet timeout
ping -c 4 -I eth0 host                # specific interface
ping6 -c 4 host                       # IPv6

# Traceroute (UDP by default)
traceroute host
traceroute -I host                     # ICMP
traceroute -T -p 443 host             # TCP
traceroute -n host                     # skip DNS resolution
traceroute -m 20 host                  # max hops

# mtr (combined ping + traceroute)
mtr host                              # interactive
mtr -r -c 10 host                     # report mode
mtr -rw host                          # wide report
```

## DNS

```bash
# dig
dig host                              # A record
dig +short host                       # short answer
dig host AAAA                         # IPv6
dig host MX                           # mail exchange
dig host NS                           # name servers
dig host TXT                          # SPF, DKIM, DMARC
dig host SOA                          # start of authority
dig host SRV                          # service records
dig host CAA                          # certificate authority
dig -x IP                             # reverse DNS
dig @8.8.8.8 host                     # query specific server
dig +trace host                       # delegation chain
dig +dnssec host                      # DNSSEC validation
dig -f hostnames.txt +short           # batch lookup

# nslookup
nslookup host
nslookup host 8.8.8.8                 # specific server
nslookup -type=MX host

# host
host host
host -t MX host
host IP                               # reverse
```

## Ports and Sockets

```bash
# ss (modern, preferred over netstat)
ss -tlnp                              # listening TCP
ss -ulnp                              # listening UDP
ss -tnp                               # established TCP
ss -tunap                             # all sockets
ss -tlnp 'sport = :80'               # filter by port
ss -tlnp 'sport = :443 or sport = :80'
ss -t state established               # by state
ss -t state time-wait
ss -t state close-wait
ss -tn dst 10.0.0.1                   # by destination
ss -tnpo                              # with timers
ss -s                                 # summary

# netstat (legacy)
netstat -tlnp                         # listening TCP
netstat -tunlp                        # all listening
netstat -an                           # all connections
netstat -rn                           # routing table
netstat -i                            # interface stats
netstat -an | awk '/^tcp/ {print $6}' | sort | uniq -c | sort -rn  # per state

# lsof
lsof -i                              # all network
lsof -i :80                          # specific port
lsof -i TCP                          # specific protocol
lsof -i :3000 -sTCP:LISTEN           # listeners on port

# nc (netcat)
nc -zv host 80                       # test port
nc -zv host 80-100                   # port range
nc -zv -w 3 host 22                  # with timeout
nc -zuv host 53                      # UDP
```

## Network Interfaces

```bash
# ip (modern, preferred)
ip addr show                          # all interfaces
ip addr show eth0                     # specific
ip link show                          # link layer
ip route show                        # routing table
ip route | grep default              # default gateway
ip neigh show                        # ARP table (neighbors)

# Legacy
ifconfig
route -n

# DNS resolver
cat /etc/resolv.conf
systemd-resolve --status              # systemd-resolved

# MTU test
ping -c 1 -M do -s 1472 host        # DF bit set
```

## Bandwidth

```bash
# curl download test
curl -s -o /dev/null -w "Speed: %{speed_download} bytes/sec\n" \
  https://speed.cloudflare.com/__down?bytes=100000000

# iperf3 (requires server)
iperf3 -c server                     # TCP test
iperf3 -c server -u -b 100M         # UDP test
iperf3 -c server -R                  # reverse (download)
iperf3 -c server -P 4               # parallel streams
```

## Firewall

```bash
# iptables
sudo iptables -L -n                  # list rules
sudo iptables -L -n -v               # verbose with counters

# nftables (modern)
sudo nft list ruleset

# firewalld
sudo firewall-cmd --list-all
sudo firewall-cmd --list-ports
```
