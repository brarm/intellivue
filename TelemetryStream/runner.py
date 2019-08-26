from client import Client

def run():
	c = Client()
	i = ''
	while i != 'q':
		i = raw_input('Enter message to send, (r) to receive, or (q) to quit: ')
		if i == 'q':
			continue
		elif i == 'r':
			message = c.receive_serial()
			print message
		else:
			message = i
			c.send_serial(message=message)


if __name__ == '__main__':
	run()