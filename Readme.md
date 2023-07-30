# vacation_plan
POC of a web page to query a vacation plan to openai and display result on a map.\
Warning : You'll need api keys for opeinai and gmap services.\
Create an api with api.py or package `lambda_function.py` and `vacation_plan.py` and requirements in an aws lambda function.\
A web page exemple is implemented in `page.html` and you can find an exemple of generated map in `map_exemple.html`.

In local:
- Install requirements with `pip install -r requirements.txt`
- Specify your api keys in `exemple_secrets_keys.py` and rename the file as `secrets_keys.py`
- Run `uvicorn run api:app`
- Open `page.html`
