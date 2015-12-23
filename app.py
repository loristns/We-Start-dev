#python2.7
# -*- coding:utf-8 -*-
from flask import Flask, render_template, request, make_response, redirect, session
import datetime
import json
import base64


app = Flask(__name__)
app.secret_key = 'SET A KEY HERE'


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'created' in session: #Si le compte existe
#Si il y a des widgets on les affiches			
        if 'widgetlist' in session and 'smwidgetlist' not in session:
            return render_template('index.html', pseudo=session['pseudo'], note=session['blocnote'], story=session['story'], widgetlist=session['widgetlist'].items(), smwidgetlist={}, rssfeed=session['rss'])
        elif 'smwidgetlist' in session and 'widgetlist' not in session:
            return render_template('index.html', pseudo=session['pseudo'], note=session['blocnote'], story=session['story'], widgetlist={}, smwidgetlist=session['smwidgetlist'].items(), rssfeed=session['rss'])
        elif 'smwidgetlist' in session and 'widgetlist' in session:
            return render_template('index.html', pseudo=session['pseudo'], note=session['blocnote'], story=session['story'], widgetlist=session['widgetlist'].items(), smwidgetlist=session['smwidgetlist'].items(), rssfeed=session['rss'])
        else:
            return render_template('index.html', pseudo=session['pseudo'], note=session['blocnote'], story=session['story'], widgetlist={}, smwidgetlist={}, rssfeed=session['rss']) #affichage sans widget
    elif request.method == 'POST': # sinon si le compte est en cours d'initialisation
        if 'pseudo' in request.form: #si le mode choisi est pseudo, on créé le compte
            session['created'] = 1
            date = datetime.datetime.now() #On récupère la date, l'heure, ect ...
            date_fin = datetime.datetime.now() + datetime.timedelta(7304.84398) #on cherche la date d'expiration en jours
            session['date'] = "{}/{}/{} {}:{}:{}".format(date.day, date.month, date.year, date.hour, date.minute, date.second) #on enregiste la date
            session['date_expiration'] = "{}/{}/{} {}:{}:{}".format(date_fin.day, date_fin.month, date_fin.year, date_fin.hour, date_fin.minute, date_fin.second) # on enregistre la date d'expiration
            session['pseudo'] = request.form['pseudo'] #on enregistre le pseudo
            session['story'] = [] #on créé l'historique de recherche
            session['pushbullettoken'] = ""
            session['rss'] = "http://rss.lemonde.fr/c/205/f/3050/index.rss"
            session['blocnote'] = '"This is one small step for a man, one giant leap for mankind." Neil Armstrong, Moon.'
            session.permanent = True
            app.config['PERMANENT_SESSION_LIFETIME'] = 631138519 # la session dure 20 ans
            return render_template('index.html', story=session['story'], note=session['blocnote'], pseudo=session['pseudo'], rssfeed=session['rss']) #on affiche la page
        elif 'code' in request.form: #si le mode choisi est code, on récupère les données
            app.config['PERMANENT_SESSION_LIFETIME'] = 631138519 # la session dure 20 ans
            importedcode = json.loads(base64.b16decode(request.form['code'])) #on décode le code
            for key in importedcode: #on récupère les élément du code
                session[key] = importedcode[key] #et on les enregistre
            if not 'blocnote' in session.keys():
                session['blocnote'] = '"This is one small step for a man, one giant leap for mankind." Neil Armstrong, Moon.'
            date = datetime.datetime.now() #on récupère les date
            date_fin = datetime.datetime.now() + datetime.timedelta(7304.84398)
            session['date'] = "{}/{}/{} {}:{}:{}".format(date.day, date.month, date.year, date.hour, date.minute, date.second) #et les ajoute (réécris)
            session['date_expiration'] = "{}/{}/{} {}:{}:{}".format(date_fin.day, date_fin.month, date_fin.year, date_fin.hour, date_fin.minute, date_fin.second)
            return render_template('index.html', story=session['story'], note=session['blocnote'], pseudo=session['pseudo'], toast=True, rssfeed=session['rss'])	#on affiche la page en l'actualisant pour afficher les widgets
    else:
        return redirect('/new') #si le compte n'est pas créer on redirigge vers l'inscription

@app.route('/new')
def log_in(): #page d'inscription
    if 'created' in session:
        return redirect('/')
    else:
        return render_template('new_account.html')

@app.route('/take-note', methods=['GET', 'POST'])
def note():
    if not 'created' in session:
        return redirect('/')
    else:
        if request.method == 'POST':
            session['blocnote'] = request.form['note']
            return redirect('/')

        else:
            return "Houston we have a problem, ERR-REQUEST(POST_ONLY), An complete form sended with POST method is required"

@app.route('/search')
def search():
    if not 'created' in session:
        return redirect('/new')
    else:
        if request.method == 'GET':
            if session['story'] == [] :
                session['story'] = [session['pseudo']]
            elif session['story'][-1] != request.args['q']:
                session['story'].append(request.args['q'])
                if len(session['story']) == 10:
                    del session['story'][0]
            if request.args['q'].startswith("$note "):
                if session['pushbullettoken'] != "":
                    return render_template('search.html', story=session['story'], pseudo=session['pseudo'], search=request.args['q'].replace("$note ",""), push=True, pushid=session['pushbullettoken'])
                else:
                    return render_template('search.html', story=session['story'], pseudo=session['pseudo'], search=request.args['q'], push=False)
            else:
                    return render_template('search.html', story=session['story'], pseudo=session['pseudo'], search=request.args['q'], push=False)
        else:
            return "Houston we have a problem, ERR-REQUEST(GET_ONLY), An complete form sended with GET method is required"

@app.route('/widget/add-widget', methods=['GET', 'POST'])
def add_widget():
    if not 'created' in session:
        return redirect('/new')
    elif request.method == 'POST':
        if 'widgetlist' in session:
            session['widgetlist'][request.form['title']] = request.form['link']
        else:
            session['widgetlist'] = {}
            session['widgetlist'][request.form['title']] = request.form['link']
        return redirect('/')
    else:
        return "Houston we have a problem, ERR-REQUEST(POST_ONLY), An complete form sended with POST method is required"

@app.route('/widget/del_widget', methods=['GET', 'POST'])		
def del_widget():
    if not 'created' in session:
        return redirect('/new')
    elif request.method == 'POST':
        if 'widgetlist' in session:
            del session['widgetlist'][request.form['title']]
            return redirect('/')
        else:
            return "Houston we have a problem, ERR-PROCESS(No_widget), Any widget to delete"
    else:
        return "Houston we have a problem, ERR-REQUEST(POST_ONLY), An complete form sended with POST method is required"

#Smart Widget !!!

@app.route('/widget/add-sm-widget', methods=['GET', 'POST'])
def add_sm_widget():
    if not 'created' in session:
        return redirect('/new')
    elif request.method == 'POST':
        if 'smwidgetlist' in session:
            session['smwidgetlist'][request.form['title']] = request.form['link']
        else:
            session['smwidgetlist'] = {}
            session['smwidgetlist'][request.form['title']] = request.form['link']
        return redirect('/')
    else:
        return "Houston we have a problem, ERR-REQUEST(POST_ONLY), An complete form sended with POST method is required"

@app.route('/widget/del-sm-widget', methods=['GET', 'POST'])		
def del_sm_widget():
    if not 'created' in session:
        return redirect('/new')
    elif request.method == 'POST':
        if 'smwidgetlist' in session:
            del session['smwidgetlist'][request.form['title']]
            return redirect('/')
        else:
            return "Houston we have a problem, ERR-PROCESS(No_widget), Any widget to delete"
    else:
        return "Houston we have a problem, ERR-REQUEST(POST_ONLY), An complete form sended with POST method is required"

@app.route('/widget/news-widget')
def news_widget():
    if not 'created' in session:
        return redirect('/new')
    elif request.method == 'GET':
        session['rss'] = request.args['rss']
        return redirect('/')
    else:
        return "Houston we have a problem, ERR-REQUEST(GET_ONLY), An complete form sended with GET method is required"

@app.route('/setting')
def parametre():
        copie_code = base64.b16encode(json.dumps(dict(session)))
        return render_template('setting.html', story=session['story'], pseudo=session['pseudo'], date=session['date'], date_expiration=session['date_expiration'], copie_code=copie_code, rssfeed=session['rss'])

@app.route('/reset_account')
def log_out():
    for element in session.keys():
        del session[element]
    return redirect('/new')

@app.route('/push/logging')
def push_logging():
    return '<script>window.location.href="/push/logged" + window.location.hash.replace("#","?");</script>'

@app.route('/push/logged')
def push_logged():
    if request.method == 'GET':
        session['pushbullettoken'] = request.args['access_token']
        return redirect('/')

@app.route('/setting/clear_story')
def clear_story():
    if not 'created' in session:
        return redirect('/')
    else:
        session['story'] = []
        return redirect('/')


@app.route('/404')
def erreur_404():
    reponse = make_response("Houston we have a problem, ERR-HTTP(404), File not found", 404)
    return reponse

@app.errorhandler(404)
def if_erreur_404(error):
    return redirect('/404')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)