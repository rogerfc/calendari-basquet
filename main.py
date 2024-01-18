import requests
import pandas as pd
import datetime
from ics import Calendar, Event

# Mini Masculí 1er any
url = 'https://www.basquetcatala.cat/partits/calendari_equip_global/275/62680'

html = requests.get(url).content
df_list = pd.read_html(html)
df = df_list[-1]
df['begin'] = pd.to_datetime(df["Data"] + ' ' + df["Hora"], format='%d/%m/%Y %H:%M').dt.tz_localize('Europe/Andorra')

print(df)

c = Calendar()
# Index(['Data', 'Hora', 'Equip Local', 'Equip Visitant', 'Categoria',
#        'Camp de joc', '[+]'],
#       dtype='object')


for index, row in df.iterrows():
    e = Event()
    e.name = f'{row["Equip Local"]} vs. {row["Equip Visitant"]}'
    e.begin = row["begin"]
    e.duration = datetime.timedelta(minutes=90)
#     e.description = ""
    e.location = row["Camp de joc"]
#     e.url = ""
    c.events.add(e)

print(c.events)

with open('casb_mini.ics', 'w') as f:
    f.writelines(c.serialize_iter())

# df.to_csv('my data.csv')
