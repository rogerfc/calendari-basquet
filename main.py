#!/usr/bin/env python

import requests
import pandas as pd
import datetime
from ics import Calendar, Event
import yaml

url_calendari = "https://www.basquetcatala.cat/partits/calendari_equip_global/{id_club}/{id_equip}"

def main():
    equips = get_teams()
    for equip in equips:
        print(equip['nom_curt'])
        df = get_team_schedule(team=equip)
        df = enrich_schedule(df, team=equip)
        write_calendar_file(df, team=equip)

def get_teams():
    with open('equips.yml', 'r') as file:
        teams = yaml.safe_load(file)
    return teams.get('equips')

def get_team_schedule(team):
    url = url_calendari.format(**team)
    html = requests.get(url).content
    df_list = pd.read_html(html)
    df = df_list[-1]    
    return df

def enrich_schedule(df, team):
    # Start time in CET
    df['begin'] = pd.to_datetime(df["Data"] + ' ' + df["Hora"], format='%d/%m/%Y %H:%M').dt.tz_localize('Europe/Andorra')
    # Event name
    df['event_name'] = [
        set_event_name(team, local=x, visitor=y)
        for x,y in zip(df['Equip Local'], df['Equip Visitant'])
    ]
    return df

def set_event_name(team, local, visitor):
    if team['nom'] in local:
        return '🏀 {casb} vs. {visitor}'.format(casb=team['nom_curt'],visitor=visitor) 
    elif team['nom'] in visitor:
        return '🏀 {casb} @ {local}'.format(casb=team['nom_curt'],local=local) 
    else:
        print('error')
        return '🏀 {local} vs. {visitor}'.format(local=local,visitor=visitor) 

def write_calendar_file(df, team):
    c = Calendar()
    filename = '{filename}.ics'.format(filename=team['nom_curt'].replace(' ', '-').lower())
    for index, row in df.iterrows():
        e = Event()
        e.name = row['event_name']
        e.begin = row["begin"]
        e.duration = datetime.timedelta(minutes=90)
        # e.description = ""
        e.location = row["Camp de joc"]
        # e.url = ""
        c.events.add(e)
    # print(c.events)
    with open(filename, 'w') as f:
        f.writelines(c.serialize_iter())


if __name__ == "__main__":
   main()
