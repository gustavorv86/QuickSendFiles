
import hashlib
import os
import sys
import socket

from core.config import DOWNLOAD_DIR, BUFFER_SIZE, CTRL_ACK


def main():
	print("Server Mode.")

	port = input("Enter port number: ")

	try:
		port = int(port)
	except Exception:
		print("Invalid port number {}. Abort.".format(port), file=sys.stderr)
		sys.exit(1)

	os.makedirs(DOWNLOAD_DIR, exist_ok=True)

	local_ip = socket.gethostbyname(socket.gethostname())
	print("Starting up on {}:{}...".format(local_ip, port))

	server_address = ("0.0.0.0", port)

	try:
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.bind(server_address)
		server_socket.listen(1)
	except Exception:
		print("Cannot open port {}. Abort.".format(port), file=sys.stderr)
		sys.exit(2)

	while True:
		try:
			client_socket, client_address = server_socket.accept()

			print("Accept connection from {}.".format(client_address))

			data = client_socket.recv(BUFFER_SIZE)
			file = data.decode("utf-8")
			file = os.path.basename(file)
			print("Filename: {}.".format(file))

			client_socket.send(CTRL_ACK.encode("utf-8"))

			data = client_socket.recv(BUFFER_SIZE)
			file_size = data.decode("utf-8")
			file_size = int(file_size)
			print("Bytes: {}.".format(file_size))

			client_socket.send(CTRL_ACK.encode("utf-8"))

			checksum_md5 = hashlib.md5()

			path_filename = "{}/{}".format(DOWNLOAD_DIR, file)
			fd = open(path_filename, "wb")

			count_bytes = 0
			while count_bytes < file_size:
				data = client_socket.recv(BUFFER_SIZE)
				fd.write(data)
				checksum_md5.update(data)

				read_bytes = len(data)
				count_bytes += read_bytes

			fd.close()

			client_socket.send(CTRL_ACK.encode("utf-8"))

			data = client_socket.recv(BUFFER_SIZE)
			source_checksum_md5 = data.decode("utf-8")

			destination_checksum_md5 = checksum_md5.hexdigest()

			print("Source MD5:      {}".format(source_checksum_md5))
			print("Destination MD5: {}".format(destination_checksum_md5))

			client_socket.send(CTRL_ACK.encode("utf-8"))

			print("Close connection.")
			client_socket.close()

		except KeyboardInterrupt:
			print("Exit.")
