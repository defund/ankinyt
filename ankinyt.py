from datetime import date, datetime, timedelta
import genanki
import json
import requests
import sys
from tqdm import tqdm

MODEL_CSS = '''\
.card {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: black;
  background-color: white;
}'''

model = genanki.Model(
	1337,
	'Crosswordese Model',
	fields=[
		{'name': 'Clue'},
		{'name': 'Answer'},
		{'name': 'Length'},
		{'name': 'Position'},
		{'name': 'SourceTitle'},
		{'name': 'SourceLink'},
		{'name': 'Explanation'}
	],
	templates=[
		{
			'name': 'Forward',
			'qfmt': '{{Clue}} ({{Length}})',
			'afmt': '{{FrontSide}}<hr>{{Answer}}<br><br>In <a href="{{SourceLink}}">{{SourceTitle}}</a>, {{Position}}<hr>{{Explanation}}'
		}
	],
	css=MODEL_CSS,
)

def parse_nyt(nyt):
	assert len(nyt['body']) == 1
	cells = nyt['body'][0]['cells']
	clues = nyt['body'][0]['clues']
	data = []
	for clue in clues:
		assert len(clue['text']) == 1
		text = clue['text'][0]['plain']
		answer = ''.join(cells[i]['answer'] for i in clue['cells'])
		position = clue['label'] + {'Across': 'a', 'Down': 'd'}[clue['direction']]
		date = nyt['publicationDate']
		link = nyt['relatedContent']['url']
		data.append((text, answer, position, date, link))
	return data

def add_notes(deck, data):
	for text, answer, position, date, link in data:
		if len(answer) > 5:
			continue
		deck.add_note(genanki.Note(model=model, fields=[
			text,
			answer,
			str(len(answer)),
			position,
			date,
			link,
			'',
		]))

def daterange(start, end):
	days = int((end - start).days)
	for i in range(days + 1):
		yield start + timedelta(i)

if __name__ == '__main__':
	BASE_URL = 'https://www.nytimes.com/svc/crosswords/v6/puzzle/daily/{}'
	with open('cookie.txt') as f:
		cookie = f.read().strip()

	start = datetime.strptime(sys.argv[1], '%Y-%m-%d')
	end = datetime.strptime(sys.argv[2], '%Y-%m-%d')

	deck = genanki.Deck(1337, 'Crosswordese')

	for d in tqdm(daterange(start, end)):
		filename = f"{d.strftime('%Y-%m-%d')}.json"
		r = requests.get(BASE_URL.format(filename), headers={
				'Cookie': cookie,
			})
		data = parse_nyt(json.loads(r.text))
		add_notes(deck, data)

	genanki.Package(deck).write_to_file('crosswordese.apkg')
