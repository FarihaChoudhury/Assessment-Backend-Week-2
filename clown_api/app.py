"""This file defines the API routes."""

# pylint: disable = no-name-in-module

from flask import Flask, Response, request, jsonify
from psycopg2.errors import ForeignKeyViolation

from database import get_db_connection

app = Flask(__name__)
conn = get_db_connection()


@app.route("/", methods=["GET"])
def index() -> Response:
    """Returns a welcome message."""
    return jsonify({
        "title": "Clown API",
        "description": "Welcome to the world's first clown-rating API."
    })


@app.route("/clown", methods=["GET", "POST"])
def get_clowns() -> Response:
    """Returns a list of clowns in response to a GET request;
    Creates a new clown in response to a POST request."""
    if request.method == "GET":
        sort_order = request.args.get("order")

        if not validate_sort_order(sort_order):
            return jsonify({"error": "Invalid sort_order parameter"}), 400

        order = get_sort_order(sort_order)

        if order == 'DESC':
            """If descending, must call 0 scores first to maintain descending order"""
            clowns = get_clowns_no_scores()
            clowns += get_clowns_with_score(order)
        else:
            clowns = get_clowns_no_scores()
            clowns += get_clowns_with_score(order)

        return clowns
    else:
        data = request.json
        try:
            if "clown_name" not in data or "speciality_id" not in data:
                raise KeyError("New clowns need both a name and a speciality.")
            if not isinstance(data["speciality_id"], int):
                raise ValueError("Clown speciality must be an integer.")

            with conn.cursor() as cur:
                cur.execute("""INSERT INTO clown
                                 (clown_name, speciality_id)
                               VALUES (%s, %s)
                               RETURNING *;""",
                            (data["clown_name"], data["speciality_id"]))
                new_clown = cur.fetchone()
                conn.commit()
            return jsonify(new_clown), 201
        except (KeyError, ValueError, ForeignKeyViolation) as err:
            print(err.args[0])
            conn.rollback()
            return jsonify({
                "message": err.args[0]
            }), 400


def get_all_clowns(sort_order: str) -> Response:
    """ Retrieves clowns: id, name, speciality, average rating.
        Orders if given, otherwise default is descending order. """
    with conn.cursor() as cur:
        cur.execute(f"""SELECT c.clown_id, c.clown_name, s.speciality_name, AVG(r.rating) as Average_rating
                        FROM clown as c
                        JOIN speciality as s USING(speciality_id)
                        LEFT JOIN review as r USING(clown_id)
                        GROUP BY c.clown_id, c.clown_name, s.speciality_name
                        ORDER BY AVG(r.rating) {sort_order};""")
        clowns = cur.fetchall()
        return jsonify(clowns), 200


@app.route("/clown/<int:clown_id>", methods=["GET"])
def get_clowns_with_id(clown_id: int) -> Response:
    """Returns a clown by its ID in response to a GET request;"""
    if request.method == "GET":
        with conn.cursor() as cur:
            clown = get_clown_with_score(clown_id)
            clown += get_clown_no_scores(clown_id)

            if clown:
                return jsonify(clown), 200
            return {'error': "No clown was found for this id"}, 404


def get_clown_no_scores(clown_id: int) -> dict:
    """Gets a clown by its id: their id, name, speciality"""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT c.clown_id, c.clown_name, speciality_name
                        FROM clown AS c
                        JOIN speciality USING(speciality_id)
                        LEFT JOIN review AS r USING(clown_id)
                        WHERE c.clown_id = {clown_id} AND {clown_id} NOT IN(SELECT clown_id FROM review);""")
        clown = cur.fetchall()
        return clown


def get_clown_with_score(clown_id: int) -> dict:
    """Gets a clown by its id: their id, name, speciality, average rating and number of ratings"""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT c.clown_id, c.clown_name, s.speciality_name, AVG(r.rating) as Average_rating, COUNT(r.rating)
                        FROM clown as c
                        JOIN speciality as s USING(speciality_id)
                        LEFT JOIN review as r USING(clown_id)
                        WHERE c.clown_id = {clown_id}
                        GROUP BY c.clown_id, c.clown_name, s.speciality_name
                        HAVING COUNT(r.rating) > 0;""")
        clowns = cur.fetchall()
        return clowns


def get_clowns_no_scores() -> dict:
    """Gets all clowns: their id, name, speciality"""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT c.clown_id, c.clown_name, speciality_name
                        FROM clown AS c
                        JOIN speciality USING(speciality_id)
                        LEFT JOIN review AS r USING(clown_id)
                        WHERE c.clown_id NOT IN(SELECT clown_id FROM review);""")
        clown = cur.fetchall()
        return clown


def get_clowns_with_score(sort_order) -> dict:
    """Gets all clowns: their id, name, speciality, average rating and number of ratings"""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT c.clown_id, c.clown_name, s.speciality_name, AVG(r.rating) as Average_rating, COUNT(r.rating)
                        FROM clown as c
                        JOIN speciality as s USING(speciality_id)
                        LEFT JOIN review as r USING(clown_id)
                        GROUP BY c.clown_id, c.clown_name, s.speciality_name
                        HAVING COUNT(r.rating) > 0
                        ORDER BY AVG(r.rating) {sort_order.upper()};""")
        clowns = cur.fetchall()
        return clowns


@app.route("/clown/<int:clown_id>/review", methods=["POST"])
def add_review_to_clown(clown_id: int) -> Response:
    """Creates a review for a clown by its id.
        Only accepts post requests of form: {score: 1}
        Where the score is a number between 1 to 5"""
    review = request.json
    score = review["score"]
    if validate_score(score):
        with conn.cursor() as cur:
            query = f"INSERT INTO review (clown_id, rating) VALUES\
            ({clown_id},{score}) RETURNING review_id"
            cur.execute(query)
            review = cur.fetchall()
            conn.commit()
            if review:
                return jsonify(review), 200
    return {"error": "Invalid review"}, 404


def validate_score(score: int) -> bool:
    """ Validates score to be an integer between 1 and 5"""
    if isinstance(score, int) and 0 < score < 6:
        return True
    return False


def validate_sort_order(sort_order: str) -> bool:
    """ Validates sort order is ascending or descending"""
    if sort_order and sort_order not in ["asc", "desc"]:
        return False
    return True


def get_sort_order(sort_order):
    """ Default sort order given as desc """
    if not sort_order:
        sort_order = 'DESC'
    return sort_order.upper()


if __name__ == "__main__":
    app.run(port=8080, debug=True)
