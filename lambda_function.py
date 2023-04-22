from vacation_plan import ask_program, make_map


def lambda_handler(event, context):
    place = event["place"]
    n_days = event["n_days"]
    description = event["description"]

    program = ask_program(place, n_days, description)
    make_map(program, n_days)

    with open("/tmp/map.html", "r") as f:
        html_content = f.read()

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': html_content,
        'program': program
    }