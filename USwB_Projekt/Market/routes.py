from Market import app, db
from Market.models import Item, User
from Market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask import render_template, redirect,jsonify, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

@app.route("/")
def HomePage():
    return render_template('HOME.html')

@app.route("/market", methods=['GET', 'POST'])
@login_required
def MarketPage():
    if request.method == "POST":
        item_obj = Item.query.filter_by(name=request.form.get('purchased_item')).first()
        if item_obj:
                item_obj.buy(current_user)
                flash(f"Gratulacje! Kupiłeś {item_obj.name} za {item_obj.price}$", category='success')

        item_obj = Item.query.filter_by(name=request.form.get('sold_item')).first()
        if item_obj:
            if current_user.can_sell(item_obj):
                item_obj.sell(current_user)
                flash(f"Gratulacje! Sprzedałeś {item_obj.name} z powrotem na rynek!", category='success')
            else:
                flash(f"Wystąpił błąd podczas sprzedaży {item_obj.name}!", category='danger')

        return redirect(url_for('MarketPage'))
    
    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('MARKET.html', title='Market', items=items, owned_items=owned_items, purchase_form=PurchaseItemForm(), sell_form=SellItemForm())

@app.route("/register", methods=['GET', 'POST'])
def RegisterPage():
    form = RegisterForm()
    if form.validate_on_submit():
        create_user = User(username=form.username.data, email_address=form.email_address.data, password=form.password1.data)
        db.session.add(create_user)
        db.session.commit()
        login_user(create_user)
        flash(f'Utworzyłeś konto! Teraz jesteś zalogowany jako: {create_user.username}', category='success')
        return redirect(url_for('MarketPage'))
    
    if form.errors != {}:
        for error in form.errors.values():
            flash(f'Wystąpił błąd podczas tworzenia użytkownika: {error}', category='danger')
    return render_template('Rejestracja.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def LoginPage():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.password_check(password_attempt=form.password.data):
            login_user(attempted_user)
            flash(f'Teraz jesteś zalogowany jako: {attempted_user.username}', category='success')
            if attempted_user.username == 'admin':
                return redirect(url_for('AdminPage'))
            return redirect(url_for('MarketPage'))
        flash('Login i hasło się nie zgadzają! Spróbuj ponownie', category='danger')
    return render_template('LOGIN.html', title='Login', form=form)

@app.route("/admin")
@login_required
def AdminPage():
    if not current_user.username=='admin':
        flash('Zaloguj się jako admin aby mieć dostęp!', category='danger')
        return redirect(url_for('LoginPage'))
    return render_template('ADMIN.html', title='Admin', users=User.query.all(), items=Item.query.all())

@app.route("/logout")
def LogoutPage():
    logout_user()
    flash("Zostałeś wylogowany!", category='info')
    return redirect(url_for('HomePage'))

def greeting(user_input):
    greetings = ['hi', 'hello', 'hey']
    if user_input.lower() in greetings:
        return "Hello! How can I assist you today?"
    else:
        return None

data = pd.read_csv("C:/Users/micha/Downloads/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv")
question = data['instruction'].tolist()
answer = data['response'].tolist()

def responses(user):
    greeting_response = greeting(user)
    if greeting_response is not None:
        return greeting_response

    question.append(user)

    TfidfVec = TfidfVectorizer()
    tfidf = TfidfVec.fit_transform(question)
    
    val = cosine_similarity(tfidf[-1], tfidf)

    id1 = val.argsort()[0][-2]
    flat = val.flatten()
    flat.sort()
    req = flat[-2]

    if req == 0:
        return "Sorry! I don't understand you."
    else:
        response = answer[id1]
        question.remove(user)
        return response

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get('user_input')
    response = responses(user_input)
    return jsonify({'response': response})

@app.route('/update_product/<int:id>', methods=['POST'])
def update_product(id):
    product = Item.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.price = request.form.get('price')
        product.owner = request.form.get('owner')
        db.session.commit()
        flash('Zmodyfikowano produkt', 'success')
    return redirect(url_for('MarketPage'))

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    product = Item.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Usunięto produkt', 'success')
    return redirect(url_for('AdminPage'))

@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('Usunięto użytkownika', 'success')
    return redirect(url_for('AdminPage'))