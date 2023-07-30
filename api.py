from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vacation_plan import ask_program, make_map
import json


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MapRequest(BaseModel):
    place: str
    n_days: int
    description: str


@app.post("/generate_map")
async def generate_map_endpoint(request: MapRequest):
    place = request.place
    n_days = request.n_days
    description = request.description

    program = [{'temps': '10h-12h', 'nom': 'Balade dans le quartier Saint-Cyprien', 'description': 'Quartier populaire et animé, traversé par la Garonne. Marché couvert, église, théâtre et nombreuses fresques urbaines.', 'lieu': 'Saint-Cyprien', 'budget': '', 'day': 'jour_1', 'url': 'https://maps.google.com/?q=St+-+Cyprien,+Toulouse,+France&ftid=0x12aebb7a9123c86d:0xe48e1097a0202044', 'location': {'lat': 43.5985558, 'lng': 1.4350126}}, {'temps': '12h-13h30', 'nom': 'Déjeuner au restaurant La Belle Equipe', 'description': 'Restaurant convivial et chaleureux, avec une cuisine inventive à base de produits frais et locaux.', 'lieu': '14 Rue Riquet, 31000 Toulouse', 'budget': '$$', 'day': 'jour_1', 'url': 'https://maps.google.com/?cid=426871432669101369', 'location': {'lat': 43.6029486, 'lng': 1.4538139}}, {'temps': '14h30-16h', 'nom': 'Visite du quartier des Minimes', 'description': 'Quartier paisible, avec de nombreux espaces verts et des petites rues tranquilles. Église Saint-Joseph, marché local et architecture Art Déco.', 'lieu': 'Les Minimes', 'budget': '', 'day': 'jour_1', 'url': 'https://maps.google.com/?cid=15252910599887470033', 'location': {'lat': 43.6158079, 'lng': 1.4359635}}, {'temps': '16h30-18h', 'nom': 'Balade sur les quais de la Garonne', 'description': 'Promenade le long de la Garonne, avec vue sur la ville et les ponts emblématiques. Idéal pour prendre des photos.', 'lieu': 'Quais de la Garonne', 'budget': '', 'day': 'jour_1', 'url': 'https://maps.google.com/?q=Berge+de+la+Garonne&ftid=0x12aebb64aa53b06b:0xeea67a5f92cb89c1', 'location': {'lat': 43.6031235, 'lng': 1.4356921}}, {'temps': '20h-22h', 'nom': 'Dîner à La Cantine du Troquet', 'description': 'Restaurant convivial proposant une cuisine du terroir revisité, avec des produits de qualité et une carte des vins variée.', 'lieu': '41 Rue des Couteliers, 31000 Toulouse', 'budget': '$$$', 'day': 'jour_1', 'url': 'https://maps.google.com/?cid=17163000079213959591', 'location': {'lat': 43.6026302, 'lng': 1.4540041}}]
    program = ask_program(place, n_days, description)
    map_html = make_map(program, n_days)

    return {"html": map_html, "program": program}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)