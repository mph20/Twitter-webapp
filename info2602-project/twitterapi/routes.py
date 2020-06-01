from flask import render_template, url_for, flash, redirect, request, session
from twitterapi import app, db, bcrypt
from twitterapi.forms import RegistrationForm, LoginForm, InputForm
from twitterapi.models import User
from flask_login import login_user, current_user, logout_user, login_required
from twython import Twython
import operator
import json


creds={}
creds['CONSUMER_KEY']='consumerkeyremovedforsecuritypurposes'
creds['CONSUMER_SECRET']='removedforsecuritypurposes'

python_tweets=Twython(creds['CONSUMER_KEY'],creds['CONSUMER_SECRET'])
client=Twython(creds['CONSUMER_KEY'],creds['CONSUMER_SECRET'])
query={'q':'gaming',
        'result_type':'popular',
        'since_id':'999999999999999999999999',
        'count':20,
        'lang':'en',
        'tweet_mode':'extended',
       }
postss=[]
dict_={'user':[],'date':[],'text':[],'favorite_count':[]}
for status in python_tweets.search(**query)['statuses']:
    result = client.show_user(screen_name=status['user']['screen_name'])
    new_post={'author':status['user']['screen_name'],
                'title':result['profile_image_url_https'],
                'content':status['full_text'],
                'date_posted':status['created_at'],
                'followers_count':result['followers_count']
                }
    postss.append(new_post)

    
@app.route("/input", methods=['GET', 'POST'])
@login_required
def input():
    form = InputForm()
    if form.validate_on_submit():
        flash(f'Searching for : {form.username.data}!', 'success')
        global query
        query['q']=form.username.data
        global postss
        postss=[]
        for status in python_tweets.search(**query)['statuses']:
            result = client.show_user(screen_name=status['user']['screen_name'])
            new_post={'author':status['user']['screen_name'],
                    'title':result['profile_image_url_https'],
                    'content':status['full_text'],
                    'date_posted':status['created_at'],
                    'followers_count':result['followers_count']
                    }  
            postss.append(new_post)
        return redirect(url_for('home'))
        #return render_template('home.html', posts=postss)
    return render_template('input.html', title='Search Twitter With A Single keyword', form=form)



@app.route("/", methods=['GET', 'POST'])
@app.route("/home",methods=['GET', 'POST'])
def home():
    global postss
    global query

    return render_template('home.html', posts=postss, rightnav = query['q'])


@app.route("/about",methods=['GET', 'POST'])
def about():
    global postss

    sortedPost = sorted(postss, key=operator.itemgetter("followers_count"))
    sortedPost.reverse()
  
    return render_template('chart.html',posts=sortedPost)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password,interest=form.interest.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            global query
            uint = User.query.filter_by(username = form.username.data).first()
            query['q']= uint.interest
            global postss
            postss=[]
            for status in python_tweets.search(**query)['statuses']:
                result = client.show_user(screen_name=status['user']['screen_name'])
                new_post={'author':status['user']['screen_name'],
                        'title':result['profile_image_url_https'],
                        'content':status['full_text'],
                        'date_posted':status['created_at'],
                        'followers_count':result['followers_count']
                        }  
                postss.append(new_post)

            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
    

@app.route("/logout")
@login_required
def logout():
    logout_user()
    global query
    query['q']='gaming'
    global postss
    postss=[]
    for status in python_tweets.search(**query)['statuses']:
        result = client.show_user(screen_name=status['user']['screen_name'])
        new_post={'author':status['user']['screen_name'],
                'title':result['profile_image_url_https'],
                'content':status['full_text'],
                'date_posted':status['created_at'],
                'followers_count':result['followers_count']
                }  
        postss.append(new_post)
    return redirect(url_for('home'))
