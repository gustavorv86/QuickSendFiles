
import sys

from core.server import server
from core.client import client


if __name__ == "__main__":

	if len(sys.argv) > 1:
		if sys.argv[1] == "-s" or sys.argv[1] == "--server":
			server.main()

	else:
		client.main()

	sys.exit(0)
