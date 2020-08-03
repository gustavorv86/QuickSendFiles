
import hashlib
import os
import socket
import sys

from core.config import BUFFER_SIZE, CTRL_ACK


def send_file(server_ip_address, port, path_file):
	print("Connecting to {}:{}...".format(server_ip_address, port))

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((server_ip_address, port))

	filename = os.path.basename(path_file)
	print("Filename: {}.".format(filename))

	data = filename.encode("utf-8")
	client_socket.send(data)

	data = client_socket.recv(BUFFER_SIZE)
	ack = data.decode("utf-8")
	if ack != CTRL_ACK:
		print("ERROR: Out of sequence.", file=sys.stderr)
		sys.exit(1)

	file_size = os.path.getsize(path_file)
	print("Bytes: {}.".format(file_size))

	data = "{}".format(file_size).encode("utf-8")
	client_socket.send(data)

	data = client_socket.recv(BUFFER_SIZE)
	ack = data.decode("utf-8")
	if ack != CTRL_ACK:
		print("ERROR: Out of sequence.", file=sys.stderr)
		sys.exit(1)

	checksum_md5 = hashlib.md5()
	fd = open(path_file, "rb")

	count_bytes = 0
	while count_bytes < file_size:
		data = fd.read(BUFFER_SIZE)
		client_socket.send(data)

		checksum_md5.update(data)

		read_bytes = len(data)
		count_bytes += read_bytes

	fd.close()

	data = client_socket.recv(BUFFER_SIZE)
	ack = data.decode("utf-8")
	if ack != CTRL_ACK:
		print("ERROR: Out of sequence.", file=sys.stderr)
		sys.exit(1)

	source_checksum_md5 = checksum_md5.hexdigest()
	print("Source MD5: {}".format(source_checksum_md5))

	data = source_checksum_md5.encode("utf-8")
	client_socket.send(data)

	data = client_socket.recv(BUFFER_SIZE)
	ack = data.decode("utf-8")
	if ack != CTRL_ACK:
		print("ERROR: Out of sequence.", file=sys.stderr)
		sys.exit(1)

	print("Close connection.")
	client_socket.close()


def main():
	print("Client Mode.")

	ip_addr = input("Enter IP address: ")

	port = input("Enter port number: ")
	try:
		port = int(port)
	except Exception:
		print("Invalid port number {}. Abort.".format(port), file=sys.stderr)
		sys.exit(1)

	list_of_path_files = list()

	while True:
		print("Files added: {}".format(len(list_of_path_files)))
		path_file = input("Enter the path file (empty to start sending files): ")

		if path_file.startswith('"') and path_file.endswith('"'):
			path_file = path_file[1:-1]

		if path_file.startswith("'") and path_file.endswith("'"):
			path_file = path_file[1:-1]

		path_file = path_file.strip()

		if not path_file:
			break

		if os.path.isfile(path_file):
			list_of_path_files.append(path_file)
		else:
			print("Cannot add \"{}\". The path is not a file.".format(path_file))

	if list_of_path_files:
		for path_file in list_of_path_files:
			send_file(ip_addr, port, path_file)

	else:
		print("No files to send.")

	sys.exit(0)
