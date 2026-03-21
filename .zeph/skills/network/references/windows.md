# Windows Network Diagnostics (PowerShell)

## Connectivity

```powershell
# Ping
Test-Connection -ComputerName host -Count 4
ping host                              # classic cmd

# Traceroute
Test-NetConnection -ComputerName host -TraceRoute
tracert host                           # classic cmd

# Port test
Test-NetConnection -ComputerName host -Port 443
Test-NetConnection -ComputerName host -Port 80 -InformationLevel Detailed
```

## DNS

```powershell
# DNS lookup
Resolve-DnsName host
Resolve-DnsName host -Type MX
Resolve-DnsName host -Type TXT
Resolve-DnsName host -Type NS
Resolve-DnsName host -Server 8.8.8.8

# Reverse DNS
Resolve-DnsName IP

# DNS cache
Get-DnsClientCache
Clear-DnsClientCache

# DNS client config
Get-DnsClientServerAddress
```

## Ports and Sockets

```powershell
# Listening ports
Get-NetTCPConnection -State Listen
Get-NetTCPConnection -State Listen | Select-Object LocalPort, OwningProcess | Sort-Object LocalPort

# Specific port
Get-NetTCPConnection -LocalPort 80
Get-NetTCPConnection -LocalPort 443

# All connections by state
Get-NetTCPConnection | Group-Object State | Select-Object Count, Name

# With process info
Get-NetTCPConnection -State Listen | ForEach-Object {
    $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
    [PSCustomObject]@{Port=$_.LocalPort; Process=$proc.ProcessName; PID=$_.OwningProcess}
} | Sort-Object Port

# UDP listeners
Get-NetUDPEndpoint | Select-Object LocalPort, OwningProcess

# Classic cmd
netstat -ano
netstat -ano | findstr LISTENING
netstat -rn                            # routing table
```

## Network Interfaces

```powershell
# IP configuration
Get-NetIPAddress | Format-Table InterfaceAlias, IPAddress, PrefixLength
Get-NetIPConfiguration

# Specific adapter
Get-NetIPAddress -InterfaceAlias "Wi-Fi"
Get-NetIPConfiguration -InterfaceAlias "Ethernet"

# Routing table
Get-NetRoute | Format-Table DestinationPrefix, NextHop, RouteMetric
Get-NetRoute -DestinationPrefix 0.0.0.0/0          # default gateway

# ARP
Get-NetNeighbor

# Adapter details
Get-NetAdapter | Format-Table Name, Status, LinkSpeed, MacAddress

# Classic cmd
ipconfig /all
```

## Bandwidth

```powershell
# Download speed test with curl (Windows 10+)
curl -s -o NUL -w "Speed: %{speed_download} bytes/sec\n" `
  https://speed.cloudflare.com/__down?bytes=100000000

# Measure download time
Measure-Command { Invoke-WebRequest -Uri "https://speed.cloudflare.com/__down?bytes=10000000" -OutFile NUL }
```

## Firewall

```powershell
# Windows Firewall status
Get-NetFirewallProfile | Select-Object Name, Enabled
Get-NetFirewallRule | Where-Object Enabled -eq True | Format-Table DisplayName, Direction, Action

# Specific port rules
Get-NetFirewallPortFilter | Where-Object LocalPort -eq 80

# Classic cmd
netsh advfirewall show allprofiles
```

## SSL/TLS

```powershell
# Check SSL certificate
$req = [System.Net.HttpWebRequest]::Create("https://host")
$req.GetResponse() | Out-Null
$cert = $req.ServicePoint.Certificate
$cert.Subject
$cert.GetExpirationDateString()
```
