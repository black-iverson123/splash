from flask import render_template, url_for, redirect, flash, request, jsonify, session
from app.forms import LoginForm, Signup,  EditProfile, PasswordResetRequest, ResetPassword, updatePassword, community, searchForm
from app.models import User, Community, community_members
from app import app, db, CMC_API_KEY
from flask_login import login_user, login_required, logout_user, current_user
from app.email import send_mail
from app.token import confirm_token, generate_token
from datetime import datetime
from app.greeting import greeting
import requests
import random
from app import socketio
from flask_socketio import join_room, leave_room, send
from sqlalchemy import select, and_



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data ).first() or User.query.filter_by(email=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
                flash('Bad login credentials!!!', 'danger')
                return redirect(url_for('index'))
                
        login_user(user)

        session['name'] = current_user.username
        session['user_id'] = current_user.id
        return redirect(url_for('dashboard'))
    return render_template('index.html', title='Sign In', form=form)

@app.route('/register', methods=['GET','POST'])
def signUp():
    form = Signup()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        token = generate_token(user.email)
        #print(token)
        html = render_template('email/confirm_email.html', token=token)
        subject = "Please confirm your email"
        send_mail(user.email, subject, html)
        
        login_user(user)
        flash(f'A confirmatory mail has been sent to {user.email}!!! ', 'warning')
        return redirect(url_for('index'))
    else:
        return render_template('signup.html', title='Sign Up',  form=form)
    

@app.route('/welcome', methods=['GET', 'POST'])
@login_required
def dashboard():
    
    if current_user.confirmed != True:
        return redirect(url_for('inactive'))
    
    
    #else:
    
    greet = greeting()
    created_communities = Community.query.filter_by(created_by_user_id=current_user.id)
    global_communities = Community.query.all() 
    
    joined = User.query.get(current_user.id).communities
                
    return render_template('Dashboard.html', title='Dashboard', greeting=greet, my_communities=created_communities,
                           globals=global_communities, joined=joined)
    

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully!!!", 'warning')
    return redirect(url_for('index'))

@app.route("/confirm/<token>", methods=['GET', 'POST'])
@login_required
def confirm_email(token):
    email = confirm_token(token)
    #print(email)
    if email:
        user = db.session.query(User).filter(User.email == email).one_or_none()
        user.confirmed = True
        user.confirmed_on = datetime.now()
        db.session.merge(user)
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success") 
        return redirect(url_for("dashboard"))   
    else:
        flash("The confirmation link is invalid or has expired.", "danger")
        return redirect(url_for("resend_confirmation"))


@app.route('/inactive', methods=['GET', 'POST'])
@login_required
def inactive():
    if current_user.confirmed == True:
        return redirect(url_for("dashboard"))
    greet = greeting()
    return render_template("inactive.html", title='Account inactive', greeting=greet, username=current_user.username)


@app.route('/resend', methods=['GET', 'POST'])
@login_required
def resend_confirmation():
    if current_user.confirmed:
        flash("Your account has already been confirmed!!!" ,'success')
        return redirect(url_for('dashboard'))
    token = generate_token(current_user.email)
    html = render_template('email/confirm_email.html', token=token)
    subject = "Please confirm your email"
    send_mail(current_user.email, subject, html)
    flash(f"A new confrimation email has been sent to {current_user.email}!!!.", 'info')
    return redirect(url_for('inactive', username=current_user.username))

                
@app.route('/coin-data', methods=['GET'])
def get_latest_prices(CMC_API_KEY=CMC_API_KEY, limit=None, convert='USD'):
    
    if current_user.is_anonymous:
        limit = 10
    else:
        limit = None
        
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        
    params = {
            'start': 1,
            'limit': limit,
            'convert': convert
        }
        
    headers = {
            'X-CMC_PRO_API_KEY': CMC_API_KEY
        }
        
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
            
    data = response.json()
            
    coins_data = data['data']
    
    
         
    coins = []
            
            
    for coin in coins_data:
                coins.append(                {
                    'name': coin['name'],
                    'symbol': coin['symbol'],
                    'price': round(float(coin['quote'][convert]['price']), 2),
                    'circulating_supply': round(float(coin['circulating_supply'])),
                    'volume_24h': round(float(coin['quote'][convert]['volume_24h'])),
                    'percent_change_in_1h': round(float(coin['quote'][convert]['percent_change_1h']), 2),
                    'percent_change_in_24h': round(float(coin['quote'][convert]['percent_change_24h']), 2),
                    'percent_change_in_7d': round(float(coin['quote'][convert]['percent_change_7d']), 2)
                })
    return jsonify(coins)
            

@app.route('/coin-listing', methods=['GET', 'POST'])
def coin_listing():
    greet = greeting()       
    return render_template('coins.html', title='Coins and Prices', greeting=greet)


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    if username == current_user.username:
        user = User.query.filter_by(username=username).first_or_404()
        greet = greeting()
        user_created = Community.query.filter_by(created_by_user_id=current_user.id).all()
        joined = User.query.get(current_user.id).communities
        return render_template('profile.html', title='Profile', user=user, greeting=greet,
                               user_group=user_created, joined=joined)
    else:
        user = User.query.filter_by(username=username).first_or_404()
        greet = greeting()
        user_created = Community.query.filter_by(created_by_user_id=user.id).all()
        joined = User.query.get(user.id).communities
        
        return render_template('visitor_profile.html', title='Profile', user=user, greeting=greet,
                               user_group=user_created, joined=joined)
        


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    greet = greeting()
    form = EditProfile(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your profile has been updated!!!', 'success')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form, greeting=greet)


@app.route('/reset_password', methods=['GET', 'POST'])
def password_reset():
   # if current_user.is_authenticated:
      #  return redirect(url_for('dashboard'))
    greet = greeting()
    form = PasswordResetRequest()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_password_reset_token()
            html = render_template('email/password_reset.html', user=user, token=token)
            subject = "[Splash] Reset your Password"
            send_mail(user.email, subject, html)
        flash('Check your email for instructions to reset your password!!!', 'info')
        return redirect(url_for('index'))
    return render_template('password_reset.html', title='Reset Password', form=form, greeting=greet)


@app.route('/password_reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    #if current_user.is_authenticated:
     #   return redirect(url_for('dashboard'))
    user = User.verify_password_reset_token(token)
    #print(user)
    if not user:
        return redirect(url_for('index'))
    form = ResetPassword()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset!!!', 'warning')
        return redirect(url_for('index'))
    return render_template('reset_password.html', form=form)


@app.route('/password_update', methods=['GET', 'POST'])
def updatePwd():
    form = updatePassword()
    if request.method == 'POST':
        email = request.form.get('email')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            if user.check_password(old_password) == False:
                flash('Old password is wrong, please try again!', 'warning')
            elif new_password != confirm_password:
                flash('Passwords do not match, please try again!', 'warning')
            elif len(new_password) < 7:
                flash('Password must be at least 7 characters long!', 'warning')
            else:
                user.set_password(new_password)
                db.session.commit()
                flash('Password has been updated successfully!', 'success')
                return redirect(url_for('dashboard',))
    
    return render_template('password_update.html', user=current_user, form=form)
            
            
@app.route('/create_community', methods=['GET','POST'])
@login_required
def create_community():
    form = community()
    if form.validate_on_submit():
        # form is valid, proceed with creating the community
        communities = Community(name=form.name.data, about=form.about.data, created_by_user_id=current_user.id )
        db.session.add(communities)
        db.session.commit()
        flash(f'{communities.name} has been created successfully!!!', 'success')
        return redirect(url_for('dashboard'))
    else:
        return render_template('create_community.html', user=current_user, form=form)
       


@app.route('/about')
def about():
    greet = greeting()
    return render_template('about.html', greeting=greet)
  

@app.route('/delete/<community>', methods=["GET", "POST"])
@login_required
def remove_community(community):
 
    group= Community.query.filter_by(name=community).first()
      
    if group:
        db.session.delete(group)
        db.session.commit()
        
        flash(f"{group.name} has been deleted successfully", "success")
    else:
        db.session.rollback()
        flash("Operation was not successful!!!", "warning")
    return redirect(url_for('user', username=current_user.username))

    
@app.route('/join_community/<int:community_id>', methods=["GET", "POST"])
@login_required
def join_community(community_id):
    creator_id = Community.query.get(community_id).created_by_user_id
    
    if current_user.id != creator_id:
        stmt = select(community_members).where(and_(
            community_members.c.user_id == current_user.id, 
            
            community_members.c.community_id == community_id
            ))
        
        result = db.session.execute(stmt)
        
        row = result.fetchone()
        
        if row is not None:
                flash("You have already joined this group!!!", "warning")
                return redirect(url_for('dashboard'))
                    
        else: 
                db.session.execute(
                    community_members.insert().values(
                    community_id = community_id,
                    user_id = current_user.id
                    )
                )
                db.session.commit()
                db.session.close()
        flash('You have joined the group!!!', "success")
        return redirect(url_for('dashboard'))
    
    else:
        
        flash("You created this group!!!", "warning")
        return redirect(url_for('dashboard'))
    

@app.route('/leave_community/<int:community_id>', methods=['GET', 'POST'])
@login_required
def leave_group(community_id):
    user_id = current_user

    if current_user:
        db.session.query(community_members).filter(
            community_members.c.community_id == community_id,
            community_members.c.user_id == current_user.id
        ).delete()
        db.session.commit()
        flash("You have left the group!!!", 'success')
        
        return redirect(url_for('user', username=current_user.username))
            
        

@app.route('/community/<community>', methods=['GET', 'POST'])
@login_required
def community_chat(community):
    user = User.query.filter_by(username=current_user.username).first_or_404()
    session['room'] = community
    room = session.get('room')
    colors = ['red', 'blue', 'green', 'cyan', 'purple', 'crimson', 'beige', 'chocolate']
    color = random.choice(colors)
    
    if room is None or session.get('room') is None:
        return redirect(url_for('dashboard'))
    
    return render_template('community_room/community.html', user=user, group_name=room, colors=color)  

@socketio.on("message")
def message(data):
    room = session.get("room")
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    
    send(content, to=room)
    print(f"{session.get('name')} said: {data['data']}")


@socketio.on('connect')
def connect(auth):
    room = session.get('room')
    name = session.get('name')
    
    if not room or not name:
        return
    
    if room is None:
        leave_room(room)
    
    join_room(room)

    send({"name": name, "message": "has entered the room"}, to=room)
    print(f"{name} joined the room {room}")

@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    name = session.get('name')
    leave_room(room)
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room")

@app.route('/search', methods=['GET', 'POST'])
def search(CMC_API_KEY=CMC_API_KEY, limit=None, convert='USD'):
    form = searchForm()
    if request.method == "POST":
        session['search_term'] = request.form.get('search')
        data = session.get('search_term')
        groups = Community.query.filter(Community.name.like('%' + data + '%')).all() 
        users = User.query.filter(User.username.like('%' + data + '%')).all()
        groups_count = Community.query.filter(Community.name.like('%' + data + '%')).count()
        users_count = User.query.filter(User.username.like('%' + data + '%')).count()
        count = groups_count + users_count
    
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        
    params = {
            'start': 1,
            'limit': limit,
            'convert': convert
        }
        
    headers = {
            'X-CMC_PRO_API_KEY': CMC_API_KEY
        }
    try:       
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
                
        coin_data = response.json()
                
        coins_data = coin_data['data']
        
        
        coins = []
                
    
        for coin in coins_data:
                if coin['name'].lower() == data.lower() or coin['symbol'].lower() == data.lower():
                    coins.append(                {
                        'name': coin['name'],
                        'symbol': coin['symbol'],
                        'price': round(float(coin['quote'][convert]['price']), 2),
                        'circulating_supply': round(float(coin['circulating_supply'])),
                        'volume_24h': round(float(coin['quote'][convert]['volume_24h'])),
                        'percent_change_in_1h': round(float(coin['quote'][convert]['percent_change_1h']), 2),
                        'percent_change_in_24h': round(float(coin['quote'][convert]['percent_change_24h']), 2),
                        'percent_change_in_7d': round(float(coin['quote'][convert]['percent_change_7d']), 2)
                    })
                    '''
                    if coins != None:
                        for coin in coins:
                            flash(f"{coin['name']} is now ${coin['price']}", "success")
                            return redirect(url_for('coin_listing'))                    
                    '''
                    
    except requests.exceptions.RequestException as e:
        pass
    
    count += len(coins)  
    
    return render_template('search.html', form=form, result=data, groups=groups, users=users, 
                            count=count, greeting=greeting(), coins=coins)
        


@app.context_processor
def base():
    form = searchForm()
    return dict(form=form)



        

