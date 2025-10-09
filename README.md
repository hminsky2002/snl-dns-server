# SNL DNS Exploratory project
A simple domain name server to forward requests towards an optimal end server (measured by latency). This server was made as an exploratory project for Columbia's Systems and Networking Lab, wherein we are trying to respond to DNS queries for `snl-columbia-university.github.io` with one of two IP addresses: `34.171.194.225` and `34.174.196.10`, whichever has the lower latency, as measured by a ping on a 10 second interval.

Socketserver code was inspired by [example code in the python library docs](https://docs.python.org/3/library/socketserver.html)


## Usage 
The server is implemented using python in `dns-server.py`, and is designed only to process DNS requests to `snl-columbia-university.github.io`. To run, create a virtual envirionment with `python3 -m venv .venv`, activate the envrionment with `. .venv/bin/activate`, and install the required packages with `pip install -r requirements.txt`. Then, run the server with `python dns-server.py`. It presumes that the ping command is installed on the root machine. To test the server, you can run `python dns-client.py.`
This 

## Extending the server
This server was made to only process valid DNS queries to `snl-columbia-university.github.io`, and does not do much in the way of error handling. It should be extended to process queries of any kind, and if it were used in production would need to be equipped to communicate with Root name servers, Top-Level Domain (TLD) name servers and Authoritative name servers to actually find the IP address for any domain name. Also, a more accurate read on latency could be provided by performing a larger number of pings at a range of packet sizes on the servers. Some broader improvements that would be necessary for integrating with CROSSFIT:
- measuring the latency between the actual client and the destination servers 
- some form of load balancing -- currently all requests get routed to the server with lower latency, which will quicky cause congestion on that server
- integration with BGP to actually implement the route path with minimal distance

### A note about server performance
It seems that the server at `34.171.194.225` is about 28% faster than `34.174.196.10` 
for a round trip ping of the same size. I measured this using `ping -c 100 -s [56,128] <ip_addr>` for both servers (output of these tests is seen in `/pings/`), calculating the ratio between the longer and shorter average ping times and then averaging those ratios between the two packet sizes. 

I believe this is caused by a circular link in the packet route for `34.174.196.10`, based on a route trace I ran from my machine to both servers (output in `/route_traces/`). 

The critical jump here is between the links at `107.14.19.24` and `66.109.6.27`. 

`34.171.194.225` goes the following way

```bash
5  lag-29-10.nwrknjmd67w-bcr00.netops.charter.com (107.14.19.24)  19.727 ms  13.146 ms
    lag-19-10.nwrknjmd67w-bcr00.netops.charter.com (66.109.6.78)  16.016 ms
 6  lag-12.nycmny837aw-bcr00.netops.charter.com (66.109.6.27)  13.126 ms
```

while `34.174.196.10` goes:
```bash
5  lag-29-10.nwrknjmd67w-bcr00.netops.charter.com (107.14.19.24)  13.988 ms
    lag-19-10.nwrknjmd67w-bcr00.netops.charter.com (66.109.6.78)  17.057 ms
    lag-29-10.nwrknjmd67w-bcr00.netops.charter.com (107.14.19.24)  47.018 ms # loop back
 6  lag-12.nycmny837aw-bcr00.netops.charter.com (66.109.6.27)  22.177 ms  22.775 ms
 ```
`34.174.196.10` then is following the same path but looping back to `107.14.19.24`. There is some other variance in my route traces between links (and also they are ultimately going to different servers), but this is likely the major factor in the difference in latency between the two servers, considering they otherwise traverse the same links and the destination servers have similar RTTs from their previous links. 
 