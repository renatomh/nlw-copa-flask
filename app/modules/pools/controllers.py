# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 11:29:11 2021

@author: RenatoHenz

Refs:
    * Flask Request Documentation: https://tedboy.github.io/flask/generated/generated/flask.Request.html
    * SQLAlchemy Operator Reference: https://docs.sqlalchemy.org/en/14/core/operators.html
    
"""

# Import flask dependencies
from flask import Blueprint, request, jsonify, g
from flask_babel import _

# SQLAlchemy functions
from sqlalchemy import func

# Session maker to allow database communication
from app import AppSession

# Other dependencies
from datetime import datetime
import pytz
import shortuuid

# Middlewares
from app.middleware import ensure_authenticated

# Import module forms
from app.modules.pools.forms import *

# Import module models
from app.modules.pools.models import *
from app.modules.users.models import *

# Define the blueprints
mod_pool = Blueprint('pool', __name__, url_prefix='/pools')
mod_guess = Blueprint('guess', __name__, url_prefix='')
mod_game = Blueprint('game', __name__, url_prefix='/games')

# Route to count number of pools
@mod_pool.route('/count', methods=['GET'])
def count_pools():
    if request.method == 'GET':
        try:
            count = Pool.query.count()
            return jsonify({"count": count})

        # If something goes wrong
        except Exception as e:
            return jsonify({"message": str(e)}), 500

# Route to create a new pool
@mod_pool.route('', methods=['POST'])
def create_pool():
    if request.method == 'POST':
        # Creating the session for database communication
        with AppSession() as session:
            # If data form is submitted
            form = CreatePoolForm.from_json(request.json)

            # Validating provided data
            if form.validate():
                try:
                    # Getting title
                    title = form.title.data
                    # Generating a code for the pool
                    code = shortuuid.random(length=6).upper()

                    # Checking if an authenticated user is creating the pool
                    if 'Authorization' in request.headers.keys():
                        # Getting user ID by token
                        token = request.headers['Authorization'].split("Bearer ")[1]
                        res = User.decode_auth_token(token)
                        # If token is valid, we define the pool owner
                        if type(res) is str: ownerId = res
                        # If token is not valid, no pool owner will be set
                        else: ownerId = None
                    # If user is not authenticated, no pool owner will be defined
                    else: ownerId = None

                    # Creating the pool
                    pool = Pool(
                        title=title,
                        code=code,
                        ownerId=ownerId,
                        )
                    session.add(pool)
                    session.flush()

                    # If user is authenticated, it will also join the pool
                    if ownerId is not None:
                        participant = Participant(
                            userId=ownerId,
                            poolId=pool.id,
                        )
                        session.add(participant)

                    # Flushing and comitting the changes
                    session.flush()
                    session.commit()

                    # Returning the data to the request
                    return jsonify({"code": code}), 201
                
                # If something goes wrong
                except Exception as e: return jsonify({"message": e}), 500

            # If something goes wrong on data validation
            else:
                # Returning the data to the request
                return jsonify({"message": form.errors}), 400

# Route to join a pool
@mod_pool.route('/join', methods=['POST'])
@ensure_authenticated
def join_pool():
    if request.method == 'POST':
        # Creating the session for database communication
        with AppSession() as session:
            # If data form is submitted
            form = JoinPoolForm.from_json(request.json)

            # Validating provided data
            if form.validate():
                try:
                    # Getting code
                    code = form.code.data
                    
                    # Checking if pool exists
                    pool = session.query(Pool).filter(Pool.code == code).first()
                    if pool is None:
                        return jsonify({"message": _("Pool not found")}), 404

                    # Checking if user has already joined the pool
                    participant = Participant.query.filter(
                        Participant.userId == g.user.id,
                        Participant.poolId == pool.id,
                    ).first()
                    if participant:
                        return jsonify({"message": _("You've already joined this pool")}), 400
                    
                    # If pool has no owner, user will be set as the pool owner
                    if pool.ownerId is None: pool.ownerId = g.user.id

                    # Creating the participant object
                    participant = Participant(
                        userId=g.user.id,
                        poolId=pool.id,
                        )
                    session.add(participant)

                    # Flushing and comitting the changes
                    session.flush()
                    session.commit()

                    # Returning the data to the request
                    return '', 201

                # If something goes wrong
                except Exception as e: return jsonify({"message": e}), 500

            # If something goes wrong on data validation
            else:
                # Returning the data to the request
                return jsonify({"message": form.errors}), 400

# Route to get user pool
@mod_pool.route('', methods=['GET'])
@ensure_authenticated
def get_pools():
    # Getting the list of pools IDs of which the user is participating
    userParticipatesAt = Participant.query.filter(Participant.userId == g.user.id).all()

    # Initializing return data
    pools = []
    # For each pool where user is participating
    for userParticipatingAt in userParticipatesAt:
        pool = userParticipatingAt.pool
        # Getting the number of participants in the pool
        _count = Participant.query.filter(Participant.poolId == pool.id).count()
        # Getting the first four participants of the pool
        participants = Participant.query.filter(Participant.poolId == pool.id).\
            paginate(1, 4, False, 4).items
        
        # Appending data to pools list
        pools.append({
            "id": pool.id,
            "title": pool.title,
            "code": pool.code,
            "createdAt": pool.createdAt.isoformat(),
            "ownerId": pool.ownerId,
            "participants": [{
                "id": participant.id,
                "user": {
                    "avatarUrl": participant.user.avatarUrl,
                }
            } for participant in participants],
            "owner": {
                "id": pool.owner.id,
                "name": pool.owner.name,
            },
            "_count": {
                "participants": _count,
            }
        })

    # Returning obtained data
    return jsonify({"pools": pools}), 200

# Route to get pool participants
@mod_pool.route('/<string:id>', methods=['GET'])
@ensure_authenticated
def get_pool_particpants(id):
    # Getting the pool by its ID
    pool = Pool.query.get(id)

    # If no pool was found
    if not pool: return jsonify({"message": _("Pool not found")}), 404

    # Getting the number of participants in the pool
    _count = Participant.query.filter(Participant.poolId == pool.id).count()
    # Getting the first four participants of the pool
    participants = Participant.query.filter(Participant.poolId == pool.id).\
        paginate(1, 4, False, 4).items

    # Setting return data
    data = {
        "id": pool.id,
        "title": pool.title,
        "code": pool.code,
        "createdAt": pool.createdAt.isoformat(),
        "ownerId": pool.ownerId,
        "participants": [{
            "id": participant.id,
            "user": {
                "avatarUrl": participant.user.avatarUrl,
            }
        } for participant in participants],
        "owner": {
            "id": pool.owner.id,
            "name": pool.owner.name,
        },
        "_count": {
            "participants": _count,
        }
    }

    # Returning obtained data
    return jsonify({"pool": data}), 200

# Route to get pool ranking
@mod_pool.route('/<string:id>/ranking', methods=['GET'])
@ensure_authenticated
def get_pool_ranking(id):
    # Getting the pool by its ID
    pool = Pool.query.get(id)

    # If no pool was found
    if not pool: return jsonify({"message": _("Pool not found")}), 404

    # Getting the number of participants in the pool
    _count = Participant.query.filter(Participant.poolId == pool.id).count()
    # Getting the participants data including score
    participants = Participant.query.filter(Participant.poolId == pool.id).\
        order_by(Participant.score.desc()).all()

    # Setting return data
    data = {
        "id": pool.id,
        "title": pool.title,
        "code": pool.code,
        "createdAt": pool.createdAt.isoformat(),
        "ownerId": pool.ownerId,
        "participants": [{
            "id": participant.id,
            "score": participant.score,
            "user": {
                "name": participant.user.name,
                "avatarUrl": participant.user.avatarUrl,
            }
        } for participant in participants],
        "_count": {
            "participants": _count,
        }
    }

    # Returning obtained data
    return jsonify({"pool": data}), 200

# Route to count number of guesses
@mod_guess.route('/guesses/count', methods=['GET'])
def count_guesses():
    if request.method == 'GET':
        try:
            count = Guess.query.count()
            return jsonify({"count": count})

        # If something goes wrong
        except Exception as e:
            return jsonify({"message": str(e)}), 500

# Route to place a new guess
@mod_guess.route('/pools/<string:poolId>/games/<string:gameId>/guesses', methods=['POST'])
@ensure_authenticated
def create_guess(poolId, gameId):
    if request.method == 'POST':
        # Creating the session for database communication
        with AppSession() as session:
            # If data form is submitted
            form = CreateGuessForm.from_json(request.json)

            # Validating provided data
            if form.validate():
                try:
                    # Getting teams points
                    firstTeamPoints = form.firstTeamPoints.data
                    secondTeamPoints = form.secondTeamPoints.data

                    # Both values must be provided
                    if (firstTeamPoints is None) or (secondTeamPoints is None):
                        return jsonify({"message": _("You must provide both team points")}), 400
                    
                    # Checking if pool exists
                    pool = Pool.query.get(poolId)
                    if pool is None:
                        return jsonify({"message": _("Pool not found")}), 404
                    
                    # Checking if game exists
                    game = Game.query.get(gameId)
                    if game is None:
                        return jsonify({"message": _("Game not found")}), 404
                    
                    # Checking if user is participating at the pool
                    participant = Participant.query.filter(
                        Participant.userId == g.user.id,
                        Participant.poolId == poolId,
                        ).first()
                    if participant is None:
                        return jsonify({"message": _("You're not allowed to create a guess inside this pool")}), 403
                    
                    # User can't place guesses after the game's date
                    if game.date.replace(tzinfo=pytz.timezone('America/Sao_Paulo')) < datetime.now(pytz.timezone('America/Sao_Paulo')):
                        return jsonify({"message": _("You cannot send guesses after the game date")}), 400
                    
                    # Checking if the user has already placed a guess for the game on the pool
                    existingGuess = session.query(Guess).filter(
                        Guess.participantId == participant.id,
                        Guess.gameId == game.id,
                    ).first()

                    # If user has already placed a guess, we'll update the points
                    if existingGuess:
                        existingGuess.firstTeamPoints = firstTeamPoints
                        existingGuess.secondTeamPoints = secondTeamPoints
                    
                    # Otherwise, we'll create a new guess
                    else:
                        guess = Guess(
                            firstTeamPoints=firstTeamPoints,
                            secondTeamPoints=secondTeamPoints,
                            gameId=game.id,
                            participantId=participant.id,
                        )
                        session.add(guess)

                    # Flushing and comitting the changes
                    session.flush()
                    session.commit()

                    # Returning the data to the request
                    return '', 201

                # If something goes wrong
                except Exception as e: return jsonify({"message": e}), 500

            # If something goes wrong on data validation
            else:
                # Returning the data to the request
                return jsonify({"message": form.errors}), 400

# Route to get pool games
@mod_pool.route('/<string:id>/games', methods=['GET'])
@ensure_authenticated
def get_pool_games(id):
    # Getting the pool by its ID
    pool = Pool.query.get(id)

    # If no pool was found
    if not pool: return jsonify({"message": _("Pool not found")}), 404

    # Checking if user is participating at the pool
    participant = Participant.query.filter(
        Participant.userId == g.user.id,
        Participant.poolId == id,
        ).first()

    # Getting pool games
    games = Game.query.order_by(Game.date.desc()).all()

    # Initializing game data
    gameData = []

    # For each game, we'll get the user's guess on the pool
    for game in games:
        # Initializing current game data
        currentGame = game.as_dict()
        # Trying to get user's guess on pool
        guess = Guess.query.filter(
            Guess.gameId == game.id,
            Guess.participantId == participant.id
            ).first()
        # If guess was found
        if guess: currentGame['guess'] = guess.as_dict()
        else: currentGame['guess'] = None

        # Appending data to games list
        gameData.append(currentGame)

    # Returning obtained data
    return jsonify({"games": gameData}), 200

# Route to create a new game
@mod_game.route('', methods=['POST'])
@ensure_authenticated
def create_game():
    if request.method == 'POST':
        # Creating the session for database communication
        with AppSession() as session:
            # If data form is submitted
            form = CreateGameForm.from_json(request.json)

            # Validating provided data
            if form.validate():
                try:
                    # Getting date and teams codes
                    date = form.date.data
                    firstTeamCountryCode = form.firstTeamCountryCode.data
                    secondTeamCountryCode = form.secondTeamCountryCode.data

                    # Creating the new game
                    game = Game(
                        date=date,
                        firstTeamCountryCode=firstTeamCountryCode,
                        secondTeamCountryCode=secondTeamCountryCode,
                    )
                    session.add(game)

                    # Flushing and comitting the changes
                    session.flush()
                    session.commit()

                    # Returning the data to the request
                    return jsonify({"game": game.as_dict()}), 201

                # If something goes wrong
                except Exception as e: return jsonify({"message": e}), 500

            # If something goes wrong on data validation
            else:
                # Returning the data to the request
                return jsonify({"message": form.errors}), 400

# Route to set a game result
@mod_game.route('/<string:id>/result', methods=['PUT'])
@ensure_authenticated
def set_game_result(id):
    # Function to calculate guess score
    def calculate_guess_score(guess, game):
        # Initializing the user points
        points = 0
        # If game already has a result
        if (game.firstTeamPoints is not None and game.secondTeamPoints is not None):
            # If participant guesses both team points right
            if (guess.firstTeamPoints == game.firstTeamPoints and guess.secondTeamPoints == game.secondTeamPoints):
                return 5
            # If participant guesses correctly that there was a draw in the match
            if (guess.firstTeamPoints == guess.secondTeamPoints and game.firstTeamPoints == game.secondTeamPoints):
                points += 3
            # If participant guesses correctly which team won the match
            if ((guess.firstTeamPoints > guess.secondTeamPoints and game.firstTeamPoints > game.secondTeamPoints) or
                (guess.firstTeamPoints < guess.secondTeamPoints and game.firstTeamPoints < game.secondTeamPoints)):
                points += 2
            # If participant guesses correctly one of the teams points
            if (guess.firstTeamPoints == game.firstTeamPoints or guess.secondTeamPoints == game.secondTeamPoints):
                points += 1
        # Returning the user points
        return points

    if request.method == 'PUT':
        # Creating the session for database communication
        with AppSession() as session:
            # If data form is submitted
            form = SetGamResultForm.from_json(request.json)

            # Validating provided data
            if form.validate():
                try:
                    # Getting teams points
                    firstTeamPoints = form.firstTeamPoints.data
                    secondTeamPoints = form.secondTeamPoints.data

                    # Both values must be provided
                    if (firstTeamPoints is None) or (secondTeamPoints is None):
                        return jsonify({"message": _("You must provide both team points")}), 400
                    
                    # Checking if game exists
                    game = session.query(Game).get(id)
                    if game is None:
                        return jsonify({"message": _("Game not found")}), 404
                    
                    # Updating game object
                    game.firstTeamPoints = firstTeamPoints
                    game.secondTeamPoints = secondTeamPoints

                    # Now, we get the game guesses list
                    guesses = session.query(Guess).filter(Guess.gameId == id).all()
                    # For each guess, we'll update the score
                    for guess in guesses: guess.score = calculate_guess_score(guess, game)

                    # Now, we get the participants list
                    participants = session.query(Participant).all()
                    # For each participant, we'll update the score
                    for participant in participants:
                        # Getting the participant's score
                        participant_score = session.query(func.sum(Guess.score)).filter(
                                Guess.participantId == participant.id
                            ).scalar()
                        # If no guess was created, score will be 'None'
                        if participant_score is None: participant.score = 0
                        # If there were guesses
                        if participant_score is not None: participant.score = participant_score

                    # Flushing and comitting the changes
                    session.flush()
                    session.commit()

                    # Returning the data to the request
                    return jsonify({"updatedGame": game.as_dict()}), 200

                # If something goes wrong
                except Exception as e: return jsonify({"message": e}), 500

            # If something goes wrong on data validation
            else:
                # Returning the data to the request
                return jsonify({"message": form.errors}), 400
