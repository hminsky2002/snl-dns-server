# SNL DNS server mock
A simple DNS to forward requests towards the optimal end server (measured by latency)

## Usage 
The server is implemented using python in `dns-server.py` and can be run using `python dns-server.py`. It presumes that the ping command is installed on the root machine. 

### A note about server performance
It seems that the server at `34.171.194.225` is about 28% faster than `34.174.196.10` 
for a round trip ping of the same size. I measured this using `ping -c 100 -s [56,128] <ip_addr>` for both servers (output of these tests is seen in `/pings/`), calculating the ratio between the longer and shorter average ping times and then averaging those ratios between the two packet sizes. 

I believe this is caused by a circular link for `34.174.196.10`, based on a route trace I ran from my machine to both servers (output in `/route_traces/`). 

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
 