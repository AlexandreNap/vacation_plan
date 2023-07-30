import os

import openai
import json
import numpy as np
import re
from secrets_keys import openai_apikey, gmap_apikey
import googlemaps
import folium
from folium.plugins import AntPath
import random


gmaps = googlemaps.Client(key=gmap_apikey)
openai.api_key = openai_apikey


def prompt(place, n_days, description):
    return f"""Peux tu m'aider à programmer mes vacances à {place}.

    {description}

    Fais en sorte de ne pas prendre trop de temps de trajets à chaque fois. Tu peux proposer jusqu'à 3 possibilités quand c'est possible. Tu peux aussi proposer des lieux pour manger ou prendre un snack (jusqu'à 3 à chaque fois).

    Le template de réponse est dans ce style de fichier json
    {{
    \"jour_1\":
        {{
            \"matin\":[
                {{
                    \"temps\": \"debut-fin\",
                    \"nom\": ...,
                    \"description\":...,
                    \"lieu\":...
                }},
                {{
                    \"temps\": \"debut-fin\",
                    \"nom\":...,
                    \"description\":....,
                    \"lieu\":...
                }},
                ...
                ],
            \"midi\":[
                {{
                \"temps\": \"debut-fin\",
                \"nom\":...,
                \"lieu\":...,
                \"description\":...,
                }},
                ...
                ],
            \"aprem\":[
                {{
                \"temps\":\"debut-fin\",
                \"nom\":...,
                \"description\":...,
                \"lieu\":...
                }},
                ...
                ],
            \"soir\":[
            ...
            ]
        }}
    }}
    On fait un programme sur {str(n_days)} jours.

    """


def day_prompt(day):
    return f"Donne moi le programme du jour {str(day)} uniquement."


def make_program(place, n_days, description):
    initial_prompt = prompt(place, n_days, description)
    messages_list = [{"role": "user", "content": initial_prompt + day_prompt(1)}]
    model = "gpt-3.5-turbo"
    completion = openai.ChatCompletion.create(model=model, messages=messages_list)
    response_content = completion.choices[0].message.content
    response_content = re.sub('^(.|\n)*?{', '{', response_content)
    response_content = re.sub('}\n(\n)+', '}', response_content)
    day_prog = json.loads(response_content)[f"jour_1"]
    messages_list.append({"role": "assistant", "content": response_content})

    day_activities = []
    for period in ["matin", "midi", "aprem", "soir"]:
        if period in list(day_prog.keys()):
            for activ in day_prog[period]:
                activ["day"] = "jour_1"
            day_activities += day_prog[period]
            print(day_prog[period])

    for i in range(2, n_days + 1):
        messages_list.append({"role": "user", "content": day_prompt(i)})
        completion = openai.ChatCompletion.create(model=model, messages=messages_list)
        response_content = completion.choices[0].message.content
        response_content = re.sub('^(.|\n)*?{', '{', response_content)
        response_content = re.sub('}\n(\n)+', '}', response_content)
        day_prog = json.loads(response_content)[f"jour_{str(i)}"]
        messages_list.append({"role": "assistant", "content": response_content})
        day_prog["day"] = f"jour_{str(i)}"

        #print(json.dumps(day_prog, ensure_ascii=False,
        #                 sort_keys=True, indent=4))
        for period in ["matin", "midi", "aprem", "soir"]:
            if period in list(day_prog.keys()):
                for activ in day_prog[period]:
                    activ["day"] = f"jour_{str(i)}"
                day_activities += day_prog[period]
                print(day_prog[period])
    return day_activities


def add_gmap_data(program, city):
    for activ in program:
        id = gmaps.find_place(city + ", " + activ["nom"] + ", " + activ["lieu"],
                              "textquery", location_bias=None,
                              fields=["business_status", "geometry/location", "place_id"])["candidates"]
        if id != []:
            id = id[0]["place_id"]
            place = gmaps.place(id, fields=["geometry", "url", "editorial_summary", "rating", "price_level"])["result"]
            url = place["url"]
            location = place["geometry"]["location"]
            activ["url"] = url
            activ["location"] = location
        else:
            activ["location"] = gmaps.geocode(city + ", " + activ["nom"] + ", " + activ["lieu"])[0]["geometry"]["location"]
    return program


def ask_program(place, n_days, description):
    program = make_program(place, n_days, description)
    program = add_gmap_data(program, place)
    return program


def make_map(program, n_days, cache=False):
    coordinates = program
    map = folium.Map(location=[np.median([coords['location']['lat'] for
                                          coords in coordinates if "location" in list(coords.keys())]),
                               np.median([coords['location']['lng'] for
                                          coords in coordinates if "location" in list(coords.keys())])], zoom_start=12)
    arrow_colors = ["red", "green", "blue", "purple", "orange"]

    # add markers for each coordinate and a popup displaying the time
    for day in range(1, n_days + 1):
        coordinates = [p for p in program if p["day"] == f"jour_{str(day)}"]
        for i, coord in enumerate(coordinates):
            if "location" in list(coord.keys()):
                if "url" in list(coord.keys()):
                    iframe = folium.IFrame(f"{coord['nom']}, {coord['day']} à {coord['temps'][:3]}<br>"
                                           f"<a href='{coord['url']}' target='_blank'>{coord['description']}</a>")
                else:
                    iframe = folium.IFrame(f"{coord['nom']}, {coord['day']} à {coord['temps'][:3]}<br>"
                                           f"{coord['description']}</a>")
                folium.Marker(
                    location=[coord['location']['lat'], coord['location']['lng']],
                    popup=folium.Popup(iframe, min_width=300, max_width=300),
                    icon=folium.Icon(icon="circle", prefix="fa", color=arrow_colors[day % len(arrow_colors)],
                                     icon_size=(25, 25), max_width=600)
                ).add_to(map)

                if i < len(coordinates)-1 and "location" in list(coordinates[i+1].keys()):
                    AntPath(
                        locations=[[coord['location']['lat'], coord['location']['lng']],
                                   [coordinates[i+1]['location']['lat'], coordinates[i+1]['location']['lng']]],
                        color=arrow_colors[day % len(arrow_colors)],
                        weight=2,
                        opacity=0.7,
                        arrows=True,
                        arrow_style='end',
                        dash_array=[15, 20]
                    ).add_to(map)
    map_file_name = f"map_{str(random.randint(0,99999999))}.html"
    map.save(map_file_name)
    with open(map_file_name, "r") as f:
        html_content = f.read()
    if not cache:
        os.remove(map_file_name)
    return html_content
