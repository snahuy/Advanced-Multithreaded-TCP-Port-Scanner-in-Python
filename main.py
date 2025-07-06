import socket
import argparse
import threading
from queue import Queue
from colorama import Fore, Style, init

init()

# --- Top 100 Common Ports (partial) ---
TOP_100_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 135, 139, 143,
    443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080
]

print_lock = threading.Lock()

def identify_service(banner, port=None):
    if "SSH" in banner:
        return "SSH"
    elif "HTTP" in banner or "Server" in banner:
        if port == 443:
            return "HTTPS"
        else:
            return "Web Server"
    elif "MySQL" in banner:
        return "MySQL"
    elif "SMTP" in banner:
        return "Mail Server"
    return "Unknown"


def guess_service_by_port(port):
    known_services = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        3306: "MySQL",
        3389: "RDP",
        8080: "HTTP Proxy"
    }
    return known_services.get(port, "Unknown")

def scan_port(ip, port, output_file=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex((ip, port))
            if result == 0:
                # Try sending real HTTP request if port 80
                try:
                    if port == 80:
                        request = f"GET / HTTP/1.1\r\nHost: {ip}\r\n\r\n"
                        s.send(request.encode())
                    else:
                        s.send(b"Hello\r\n")
                    banner = s.recv(1024).decode(errors="ignore").strip()
                except:
                    banner = "No banner"

                # Decide service name
                if banner and banner != "No banner":
                    service = identify_service(banner)
                else:
                    service = guess_service_by_port(port)

                if len(banner) > 100:
                    banner = banner[:100] + "..."

                with print_lock:
                    print(f"{Fore.GREEN}[+] Port {port:<5} OPEN   | Service: {service:<10} | Banner: {banner}{Style.RESET_ALL}")
                if output_file:
                    with open(output_file, "a") as f:
                        f.write(f"Port {port:<5} OPEN   | Service: {service:<10} | Banner: {banner}\n")
    except:
        pass

def threader(ip, port_queue, output_file):
    while True:
        port = port_queue.get()
        scan_port(ip, port, output_file)
        port_queue.task_done()

def main():
    parser = argparse.ArgumentParser(description="Advanced Multithreaded TCP Port Scanner")
    parser.add_argument("-t", "--target", required=True, help="Target IP or hostname")
    parser.add_argument("-s", "--start", type=int, help="Start port (if not using --top)")
    parser.add_argument("-e", "--end", type=int, help="End port (if not using --top)")
    parser.add_argument("--top", action="store_true", help="Scan top 100 common ports")
    parser.add_argument("-th", "--threads", type=int, default=50, help="Number of threads (default 50)")
    parser.add_argument("-o", "--output", help="Output results to file")

    args = parser.parse_args()

    # --- DNS Resolution ---
    try:
        ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"{Fore.RED}[!] Invalid hostname: {args.target}{Style.RESET_ALL}")
        return

    # --- Port list ---
    if args.top:
        ports_to_scan = TOP_100_PORTS
    elif args.start is not None and args.end is not None:
        ports_to_scan = list(range(args.start, args.end + 1))
    else:
        print(f"{Fore.RED}[!] Please specify a port range (-s and -e) or use --top{Style.RESET_ALL}")
        return

    print(f"\n[+] Scanning {args.target} [{ip}] on {len(ports_to_scan)} ports using {args.threads} threads...\n")

    port_queue = Queue()

    # Start threads
    for _ in range(args.threads):
        t = threading.Thread(target=threader, args=(ip, port_queue, args.output), daemon=True)
        t.start()

    # Enqueue ports
    for port in ports_to_scan:
        port_queue.put(port)

    port_queue.join()
    print(f"\n[+] Scan complete.\n")

if __name__ == "__main__":
    main()
