# Advanced-Multithreaded-TCP-Port-Scanner-in-Python
This Python-based port scanner allows you to scan a host for open TCP ports using multiple threads for fast performance. It supports scanning custom ranges or the top 100 common ports, grabs basic service banners, and offers DNS resolution, logging, and color-coded output.

# Features
- Multithreaded TCP scanning
- Top 100 common ports mode (`--top`)
- Banner grabbing + basic fingerprinting
- DNS resolution (hostname → IP)
- Colored terminal output
- Save results to file

# Requirements
- Python 3.x

# Sample Test Scanning top 100 ports
python3 main.py -t scanme.nmap.org -s 20 -e 100

[+] Scanning scanme.nmap.org [45.33.32.156] on 81 ports using 50 threads...

[+] Port 22    OPEN   | Service: SSH        | Banner: SSH-2.0-OpenSSH_6.6.1p1 Ubuntu-2ubuntu2.13
[+] Port 80    OPEN   | Service: Web Server | Banner: HTTP/1.1 200 OK
Date: Sun, 06 Jul 2025 11:05:41 GMT
Server: Apache/2.4.7 (Ubuntu)
Accept-Ranges: ...

[+] Scan complete.

# Sample Test Scanning wiht Logging
python3 main.py -t scanme.nmap.org -s 1 -e 1024 -o results.txt