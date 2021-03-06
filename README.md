# Netprobe Central

Central application for measuring delays in a network.<br>
Requirements:
- one of the hosts in network should have central application running
- every host in network (at least those we want to measure delays between)
 should have netprobe application (https://github.com/Ugon/netprobe) running
 <br>Note: one host can have both central and netprobe app running
- it is assumed that connection between hosts is assured
- clock between all of hosts HAS TO be synchronized, ie. using ntp (see: https://help.ubuntu.com/lts/serverguide/NTP.html, https://ubuntuforums.org/showthread.php?t=862620, netprobe-docs), otherwise, the results will be random (negative, close to 0, etc.)

Central app is running on port 5005 by default<br>
Netprobe app is running on port 5000 by default


## How to run

```
sudo docker build -t central .
sudo docker run --network="host" --name="central" central
```

## Creating new measurement

Dislaimer: For every requests where ip:port is referred,
 both ip and port has to be given in format ip:port
  (Example: 127.0.0.1:5002) Any other format or omitting port won't work.


```
POST http://<central_ip>:5005/<protocol>/<src>/<dst>/<interval>
```

**central_ip** - ip of host on which central app is running<br>
**protocol** - protocol we want to measure (possible values: 'udp', 'tcp', 'icmp')<br>
**src** - ip:port of the host we want to be the source of measurement requests<br>
**dst** - ip:port of the host we want to be the destination of measurement requests<br>
**interval** - src will send 1 measurement request to dst each interval seconds

After this request host src will start sending measurement requests to the dst host. It will do it until we delete the measurement.
For details about measurements of each protocol, go to the netprobe documentation.
<br><br> 
###<b>Note: for given triplet: protocol;src;dst (where src and dst are ip:port) there can be only one measurement in the entire central app.</b>


Example:

```
curl -X POST \
  http://192.168.0.90:5005/udp/192.168.0.90:5001/192.168.0.91:5003/5
```

## Getting measurement results

After starting measurements we can get their results - delays of hosts communication. 
For details check netprobe documentation.

```
GET http://<central_ip>:5005/<protocol>/<src>/<dst>/<measurement_type>/<measurement_section>
```

**central_ip** - ip of host on which central app is running<br>
**protocol** - protocol we want to measure (possible values: 'udp', 'tcp', 'icmp')<br><br>
Note: If protocol is tcp, there is no measurement_section parameter (example below)<br><br>
**src** - ip:port of the host we want to be the source of measurement requests<br>
**dst** - ip:port of the host we want to be the destination of measurement requests<br>
**measurement_type** - type of result, possible values:
- all - all of the delays in ms in chronological order will be returned
- avg - average delay in ms will be returned
- last-\<number\> - last number of delays will be returned (example: last-3)<br>
**measurement_section** - in udp and icmp we can measure one way delays (both ways) and two way delays. Possible values:
- one_way_source_target - delays of communication from src to dst
- one_way_target_source - delays of communication back from dst to src
- two_way - delay of communication in both ways

Examples:

```
curl -X GET \
  http://0.0.0.0:5005/icmp/192.168.0.90:5001/192.168.0.91:5003/avg/two_way
```

```
curl -X GET \
  http://0.0.0.0:5005/udp/192.168.0.90:5001/192.168.0.91:5003/last-5/one_way_target_source
```

```
curl -X GET \
  http://0.0.0.0:5005/tcp/192.168.0.90:5001/192.168.0.91:5003/all
```

Example response: 
```
[20, 25, 12, 23, 32, 10, 10, 10, 24]
```

where each number is delay in ms of each existing measurement request for queried measurement



## Deleting Measurements

```
DELETE http://<central_ip>:5005/<protocol>/<src>/<dst>
```

**central_ip** - ip of host on which central app is running<br>
**protocol** - protocol which is measured (possible values: 'udp', 'tcp', 'icmp')<br>
**src** - ip:port of the host which is the source of measurement requests<br>
**dst** - ip:port of the host which is the destination of measurement requests<br>

This request will remove process of measuring.

Example:

```
curl -X DELETE \
  http://192.168.0.90:5005/udp/192.168.0.90:5001/192.168.0.91:5003
```

## TroubleShooting

If any of the requests fails, user will get HTTP 500 error.<br>
Most of the times, error message will be provided what went wrong (ie. Measurement for given hosts already exist) <br>

However if there is no error message and/or application is behaving weird:
- restart central
- restart netprobe application of hosts which were affected
