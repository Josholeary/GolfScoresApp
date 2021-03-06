from crypt import methods
from hashlib import sha256
from nis import cat
from operator import methodcaller
from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from .dbmodels import setgame,User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        gamename = request.form.get('gamename')
        numholes = request.form.get('numholes')
        spass = request.form.get('spass')
    
        if len(gamename) < 4:
            flash('Game name must be greater than 4 characters', category='error')
        elif len(spass) < 4:
            flash('Password must be greater than 4 characters', category='error')
        else:
            inh = int(numholes)
            newgame = setgame(gamename = gamename, numholes=inh, spass=generate_password_hash(spass, method='sha256'))
            db.session.add(newgame)
            db.session.commit()
            flash('Game created, join using session password', category='success')
            return redirect(url_for('auth.join_page'))
        

    return render_template('setup.html')

@auth.route('/join', methods=['GET', 'POST'])
def join_page():
    if request.method == 'POST':
        pname = request.form.get('pname')
        gamename = request.form.get('gamename')
        spass = request.form.get('spass')

        gameip = setgame.query.filter_by(gamename=gamename).first()
        if gameip:
            if check_password_hash(gameip.spass, spass):
                flash('Joined game', category='success')
                newplayer = User(pname=pname)
                db.session.add(newplayer)
                db.session.commit()
                login_user(newplayer, remember=True)
                return redirect(url_for('auth.game_page'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Game name does not exist', category='error')
    return render_template('join.html')

@auth.route('/game', methods=['GET', 'POST'])
@login_required
def game_page():
    if request.method == 'POST':

        hn = request.form.get('holenum')
        ns = request.form.get('score')
        print('HN:'+hn)
        print('NS:'+ns)

        if ns =="" or hn == "":
            flash('Enter a score and hole number', category='error')
        else:
            holenum = int(hn)
            newscore = int(ns)
            p_exists = User.query.filter_by(id=current_user.id).first()
            if p_exists:
                if not p_exists.score:
                    p_exists.holenum = holenum
                    p_exists.score = newscore
                    db.session.commit()
                else:
                    overall = newscore + p_exists.score
                    p_exists.holenum = holenum
                    p_exists.score = overall
                    db.session.commit()
            else:
                flash('Player name not in session', category='error')

    players = User.query.all()
    return render_template('game.html', players=players)

@auth.route('/leave')
@login_required
def leave_game():
    logout_user()
    return redirect(url_for('auth.join_page'))

@auth.route('/delete')
@login_required
def delete_game():
    return redirect(url_for('views.homepage'))
    

