# Copyright (C) 2016 Guillaume Valadon <guillaume@valadon.net>

"""
Connect to a FlashAir using Telnet
"""


import sys
import telnetlib


class FlashAirTelnet(object):
    """
    Custom Toshiba FlashAir Telnet client.
    """

    def __init__(self, host):
        self.tlnt = telnetlib.Telnet(host, 23)

        # Announce that we will send strings character per character
        self.write_raw(telnetlib.IAC + telnetlib.WONT + telnetlib.LINEMODE)

    def write_raw(self, data):
        """
        Write raw data to the socket, as the regular write() doubles IAC
        characters.
        From
        http://stackoverflow.com/questions/12421799/how-to-disable-telnet-echo-in-python-telnetlib # noqa: E501
        """

        t_sck = self.tlnt.get_socket()
        t_sck.send(data)

    def wait_for_prompt(self):
        """
        Wait until the FlashAir prompt is received.
        """

        return self.tlnt.read_until("> ")

    def recv_command(self):
        """
        Read result from a command.
        """

        command_result = ""

        # Get the real socket
        t_sck = self.tlnt.get_socket()
        while True:
            command_result += t_sck.recv(1024)
            # Trick the server into sending more data
            self.tlnt.write("\r\n")

            # Stop if the prompt is received
            if "\n> " in command_result:
                break

        return command_result

    def send_command(self, command):
        """
        Send a single command.
        """

        # Send the command character per character, and wait for the echo
        # That is the magic trick to talk to the FlashAir!
        for char in command:
            self.tlnt.write(char)
            self.tlnt.read_until(char)

        # Send the terminaison characters
        self.tlnt.write("\r\n")
        self.tlnt.read_until("\r\n")

    def interactive(self):
        """
        Mimic an interctive session.
        """

        # Get the Telnet prompt
        prompt = self.wait_for_prompt()
        sys.stdout.write("%s" % prompt)

        while True:

            command = sys.stdin.readline().strip()

            # Fake command that ease quitting the interactive session
            if command == "exit":
                break

            self.send_command(command)
            data = self.recv_command()
            sys.stdout.write(data)

    def single_command(self, command):
        """
        Send a single command and retrieve the result.
        """

        self.wait_for_prompt()
        self.send_command(command)
        return self.recv_command()

    def close(self):
        """
        Close the Telnet session.
        """

        return self.tlnt.close()


def telnet_register(parser):
    """
    Register the 'telnet' sub-command.
    """
    new_parser = parser.add_parser("telnet", help="Connect to a FlashAir \
                                   card using Telnet")
    new_parser.add_argument("-c", "--command", dest="command",
                            help="send a single command.")
    new_parser.add_argument("-t", "--target", dest="target",
                            default="192.168.0.1",
                            help="address or name of the FlashAir")
    new_parser.set_defaults(func=telnet_command)


def telnet_command(args):
    """
    Interact with the card using Telnet
    """

    # Start the FlashAir client
    fat = FlashAirTelnet(args.target)
    if args.command:
        print fat.single_command(args.command)
    else:
        fat.interactive()
    fat.close()
