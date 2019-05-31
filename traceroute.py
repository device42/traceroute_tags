import socket
import random
import struct
import time
import platform
import os
import re


__all__ = ['Tracer']


class Tracer(object):
    def __init__(self, dst, hops=30, timeout=100):
        """
        Initializes a new tracer object
        Args:
            dst  (str): Destination host to probe
            hops (int): Max number of hops to probe
        """
        self.dst = dst
        self.hops = hops
        self.timeout = timeout
        self.ttl = 1

        # Pick up a random port in the range 33434-33534
        self.port = random.choice(range(33434, 33535))

    def run(self):
        """
        Run the tracer
        Raises:
            IOError
        """
        if platform.system().lower() == "linux":
            try:
                dst_ip = socket.gethostbyname(self.dst)
            except socket.error as e:
                raise IOError('Unable to resolve {}: {}', self.dst, e)

            text = 'traceroute to {} ({}), {} hops max'.format(
                self.dst,
                dst_ip,
                self.hops
            )

            print(text)

            while True:
                startTimer = time.time()
                receiver = self.create_receiver()
                sender = self.create_sender()
                sender.sendto(b'', (self.dst, self.port))

                addr = None
                try:
                    data, addr = receiver.recvfrom(1024)
                    entTimer = time.time()
                except socket.error as e:
                    print(str(e))
                    pass
                    # raise IOError('Socket error: {}'.format(e))
                finally:
                    receiver.close()
                    sender.close()

                if addr:
                    if addr[0] == dst_ip:
                        return True
                else:
                    print('{:<4} *'.format(self.ttl))

                self.ttl += 1

                if self.ttl > self.hops:
                    return False
        else:  # Windows
            cmd = "tracert -d -h %d -w %d %s" % (self.hops, self.timeout, self.dst)
            p = os.popen(cmd)
            output = p.read()
            lines = output.splitlines()
            for line in lines:
                x = re.search(r"^\s*\d+.*$", line)
                if x is not None:
                    if line.find(self.dst) != -1:
                        return True
            return False

    def create_receiver(self):
        """
        Creates a receiver socket
        Returns:
            A socket instance
        Raises:
            IOError
        """
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_RAW,
            proto=socket.IPPROTO_ICMP
        )

        timeout = struct.pack("ll", int(self.timeout / 1000), self.timeout % 1000 * 1000)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)

        try:
            s.bind(('', self.port))
        except socket.error as e:
            raise IOError('Unable to bind receiver socket: {}'.format(e))

        return s

    def create_sender(self):
        """
        Creates a sender socket
        Returns:
            A socket instance
        """
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM,
            proto=socket.IPPROTO_UDP
        )

        s.setsockopt(socket.SOL_IP, socket.IP_TTL, self.ttl)

        return s