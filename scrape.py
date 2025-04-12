from datetime import date, datetime, timedelta
import requests
import sys

BASE_URL = 'https://www.nytimes.com/svc/crosswords/v6/puzzle/daily/{}'

def daterange(start, end):
	days = int((end - start).days)
	for i in range(days + 1):
		yield start + timedelta(i)

if __name__ == '__main__':
	start = datetime.strptime(sys.argv[1], '%Y-%m-%d')
	end = datetime.strptime(sys.argv[2], '%Y-%m-%d')
	with open('cookie.txt') as f:
		cookie = f.read().strip()

	for d in daterange(start, end):
		filename = f"{d.strftime('%Y-%m-%d')}.json"
		r = requests.get(BASE_URL.format(filename), headers={
				'Cookie': cookie,
			})
		with open(f'dumps/{filename}', 'wb') as f:
			f.write(r.content)
