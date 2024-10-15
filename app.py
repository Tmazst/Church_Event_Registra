
from flask import Flask,render_template,url_for,redirect,request,flash,jsonify,session
from flask_login import login_user, LoginManager,current_user,logout_user, login_required
from Forms import *
from models import *
from flask_bcrypt import Bcrypt
import secrets
# import MySQLdb
import time
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
# from bs4 import BeautifulSoup as bs
from flask_colorpicker import colorpicker
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import itsdangerous
from sqlalchemy.exc import IntegrityError
from authlib.integrations.flask_client import OAuth



#Did latest commit with the requirement file

#Change App
app = Flask(__name__)
app.config['SECRET_KEY'] = "sdsdjfe832j2rj_32j"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///techxicons_db.db"
# app.config[
#     "SQLALCHEMY_DATABASE_URI"] = "mysql+mysqldb://Tmaz:Tmazst41@Tmaz.mysql.pythonanywhere-services.com:3306/Tmaz$users_db"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle':280}
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOADED"] = 'static/uploads'
oauth = OAuth(app)
db.init_app(app)

application = app

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Log in
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

ALLOWED_EXTENSIONS = {"txt", "xlxs", 'docx', 'pdf', 'png', 'jpg', 'jpeg', 'gif',"JPG"}


def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class user_class:
    s = None

    def get_reset_token(self, c_user_id):

        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': c_user_id, 'expiration_time': time.time() + 300}).encode('utf-8')

    @staticmethod
    def verify_reset_token(token, expires=1800):

        s = Serializer(app.config['SECRET_KEY'], )

        try:
            user_id = s.loads(token, max_age=300)['user_id']
        except itsdangerous.SignatureExpired:
           return f'Token has expired!, Please Create a New Token'
        except itsdangerous.BadSignature:
            return f'Token has expired, Please Create a New Token'
        except:
            return f'Something Went Wrong'
         
        return user_id


appConfig = {

    "OAUTH2_CLIENT_ID" : os.getenv('clientid'),
    "OAUTH2_CLIENT_SECRET":os.getenv('clientps'),
    "OAUTH2_META_URL":"",
    "FLASK_SECRET":"sdsdjsdsdjfe832j2rj_32jfesdsdjfe832j2rj32j832",
    "FLASK_PORT": 5000  
}


oauth.register("Registra",
               client_id = appConfig.get("OAUTH2_CLIENT_ID"),
               client_secret = appConfig.get("OAUTH2_CLIENT_SECRET"),
                access_token_url='https://accounts.google.com/o/oauth2/token',
                access_token_params=None,
                authorize_url='https://accounts.google.com/o/oauth2/auth',
                authorize_params=None,
                api_base_url='https://www.googleapis.com/',
                userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo', 
               client_kwargs={
                   "scope" : "openid email profile"
               },
               server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration',
               jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
               )


def process_file(file):

        filename = secure_filename(file.filename)

        _img_name, _ext = os.path.splitext(filename)
        gen_random = secrets.token_hex(8)
        new_file_name = gen_random + _ext

        if file.filename == '':
            return 'No selected file'

        print("DEBUG FILE NAME: ", file.filename)
        file_saved = file.save(os.path.join("static/images",new_file_name))
        flash(f"File Upload Successful!!", "success")
        return new_file_name



def process_pop_file(file,usr_id):

        filename = secure_filename(file.filename)

        _img_name, _ext = os.path.splitext(filename)
        gen_random = secrets.token_hex(8)
        new_file_name = gen_random + str(usr_id) + _ext

        if file.filename == '':
            return 'No selected file'

        if file.filename:
            file_saved = file.save(os.path.join(app.config["UPLOADED"],new_file_name))
            # flash(f"File Upload Successful!!", "success")
            return new_file_name

        else:
            return f"Allowed are [.txt, .xls,.docx, .pdf, .png, .jpg, .jpeg, .gif] only"


def createall(db_):
    db_.create_all()

encry_pw = Bcrypt()

@app.context_processor
def inject_ser():
    event = open_event.query.filter_by(event_closed=False).first()

    return dict(event_details=event,pop_transts=pop_transactions)


@app.route("/", methods=['POST','GET'])
def home():

    event_details=None

    if open_event.query.filter_by(event_closed=False).first():
        event_details = open_event.query.filter_by(event_closed=False).first()
    
    return render_template("index.html", event_details=event_details)


#Admins Opening & Closing Registrations
@app.route("/open_event_form", methods=["POST", "GET"])
def open_event_form():

    open_reg_form = OpenEventForm()
    event_details=None

    if open_event.query.filter_by(event_closed=False).first():
        event_details = open_event.query.filter_by(event_closed=False).first()

    if open_reg_form.validate_on_submit():

        open_event_ = open_event(start_date=open_reg_form.start_date.data,end_date=open_reg_form.end_date.data,event_title=open_reg_form.event_title.data,
                        event_abbr=open_reg_form.event_abbr.data,event_theme=open_reg_form.event_theme.data,event_venue=open_reg_form.event_venue.data,
                        registration_group1=open_reg_form.registration_group1.data,reg_fee_amnt1=open_reg_form.reg_fee_amnt1.data,registration_group2=open_reg_form.registration_group2.data,
                        reg_fee_amnt2=open_reg_form.reg_fee_amnt2.data,registration_group3=open_reg_form.registration_group3.data,reg_fee_amnt3=open_reg_form.reg_fee_amnt3.data,
                        event_other_info=open_reg_form.event_other_info.data,timestamp=datetime.now())
        
        db.session.add(open_event_)
        if not event_details:
            db.session.commit()
            flash("Event Opened Successfully!","success")
            return redirect(url_for("home"))
        else:
            flash("Event Already Opened","success")
            return redirect(url_for("home"))      
    else:
        for error in open_reg_form.errors:
            print("Reg Form Errors: ",error)

    return render_template('open_event.html',open_reg_form=open_reg_form)

#Admins Opening & Closing Registrations
@app.route("/opened_event_edit", methods=["POST", "GET"])
def opened_event_edit():

    open_reg_form = OpenEventForm()
    event_edit = open_event.query.filter_by(event_closed=False).first()

    if open_reg_form.validate_on_submit():

        event_edit.start_date=open_reg_form.start_date.data
        event_edit.end_date=open_reg_form.end_date.data
        event_edit.event_title=open_reg_form.event_title.data
        event_edit.event_abbr=open_reg_form.event_abbr.data
        event_edit.event_theme=open_reg_form.event_theme.data
        event_edit.event_venue=open_reg_form.event_venue.data
        event_edit.registration_group1=open_reg_form.registration_group1.data
        event_edit.reg_fee_amnt1=open_reg_form.reg_fee_amnt1.data
        event_edit.registration_group2=open_reg_form.registration_group2.data
        event_edit.reg_fee_amnt2=open_reg_form.reg_fee_amnt2.data
        event_edit.registration_group3=open_reg_form.registration_group3.data
        event_edit.reg_fee_amnt3=open_reg_form.reg_fee_amnt3.data
        
        db.session.commit()
        flash("Update Successful!","success")

    return render_template('opened_event_edit.html',open_reg_form=open_reg_form,event_details=event_edit)


def reg_confirmation():
    
    accommodation="No"
    event = open_event.query.filter_by(event_closed=False).first()
    print("CHECK EVENT: ",event)
    usr_ = church_user.query.get(current_user.id)
    reg_info = pop_transactions.query.filter_by(usr_id=current_user.id).first()

    if reg_info.accommodation_add_info == 1:
        accommodation = "Yes"

    def send_veri_mail():

        app.config["MAIL_SERVER"] = "smtp.googlemail.com"
        app.config["MAIL_PORT"] = 587
        app.config["MAIL_USE_TLS"] = True
        # Creditentials saved in environmental variables
        em = app.config["MAIL_USERNAME"] = "pro.dignitron@gmail.com"  # os.getenv("MAIL")
        app.config["MAIL_PASSWORD"] = "abngvekbagyvosbw" #os.getenv("PWD")
        app.config["MAIL_DEFAULT_SENDER"] = "noreply@gmail.com"

        mail = Mail(app)

        token = user_class().get_reset_token(current_user.id)
        usr_email = usr_.email

        msg = Message(subject="Registration Confirmation", sender="no-reply@gmail.com", recipients=[usr_email])

        msg.html = f"""<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f6f6f6;
            color: #333;
            padding: 20px;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        h2,h3 {{
            color: #4CAF50;
        }}
        p,li{{font-weight:500;color:#707070 }}
        .footer {{
            margin-top: 20px;
            font-size: 0.9em;
            color: #777;
        }}
        span{{ font-weight:600;color:coral}}
    </style>
</head>
<body>
    <div class="container">
        <img style="" src="https://africec.org/images/webimages/logo/logo.png" />
        <h2>Hi, {usr_.name}</h2>
        <p>This is to confirm that your registration for the African Evangelical Church's upcoming event was successful.</p>
        <p>Please see details below for your perusal:</p>
        <h3>Event Details:</h3>
        <ul>
            <li><span>Event Title:</span> {event.event_title}</li>
            <li><span>Date:</span> {event.start_date} - {event.end_date} </li>
            <li><span>Venue:</span> {event.event_venue}</li>
        </ul>
        <h3>Registration Information:</h3>
        <ul>
            <li><span>Name:</span> {church_user.query.get(reg_info.usr_id).name}</li>
            <li><span>Age Group:</span> {reg_info.age_group}</li>
            <li><span>Special Diet:</span> {reg_info.special_diet}</li>
            <li><span>Accommodation:</span> {accommodation}</li>
            <li><span>Denominational Structure:</span> {reg_info.denom_structure}</li>
            <li><span>Reg. Date:</span> {reg_info.timestamp.strftime("%d %b %y")}</li>
            <li><span>Payment Mode:</span> {reg_info.payment_platform}</li>
            <li><span>Transaction Token:</span> {reg_info.transaction_token}</li>
        </ul>
        <p class="footer">Thank you for registering!</p>
    </div>
</body>
</html>
"""


        try:
            mail.send(msg)
            flash(f'We have sent you an email with Registration Details', 'success')
            return "Email Sent"
        except Exception as e:
            flash(f'Email not sent here', 'error')
            return "The mail was not sent"

    # try:
    send_veri_mail() 
    # except:


#User Registrations Form
@app.route("/user_registration_form", methods=["POST", "GET"])
@login_required
def user_registration_form():
    val_registration = None
    registration_form = RegistrationsForm()
    get_user = User.query.get(current_user.id)
    event = open_event.query.filter_by(event_closed=False).first()

    if event:
        val_registration = pop_transactions.query.filter_by(usr_id=current_user.id).first()
    
    if val_registration:
        flash(f"You are already registered.", "success")
        # reg_confirmation()
        return redirect(url_for("already_registered"))# redirect(url_for("home"))
    
    if not current_user.church_local and not current_user.church_circuit:
        flash("Please Finish Your Account Setup, First, You're Almost There!","warning")
        return redirect(url_for("finish_signup"))
    
    if registration_form.validate_on_submit():
        registration = pop_transactions(
            usr_id=current_user.id,transaction_id=secrets.token_hex(16),transaction_token=secrets.token_hex(16)+str(current_user.id),
            timestamp=datetime.now(),payment_platform=registration_form.payment_platform.data,denom_structure=registration_form.denom_structure.data,#accomodation = registration_form.accomodation.data
            accommodation_bool=registration_form.accommodation_bool.data,accommodation_add_info=registration_form.accommodation_add_info.data,
            special_diet=registration_form.special_diet.data
            )
        
        if registration_form.pop_image.data:
            file =  process_pop_file(registration_form.pop_image.data,current_user.id)
            registration.pop_image = file
        
        db.session.add(registration)

        if not val_registration:
            db.session.commit()
            reg_confirmation()
            # print("Confirmation Sent Successfully!")
        # else:
        #     flash(f"You are already registered.", "success")
        #     reg_confirmation()
        #     return redirect(url_for("registration_success"))# redirect(url_for("home"))
        # flash(f"You are successfully registered", "success")
        return redirect(url_for("registration_success"))

    return render_template('registrations_form.html',registration_form=registration_form,user=get_user,event_details=event,val_registration=val_registration)

#User Registrations Form
@app.route("/already_registered", methods=["POST", "GET"])
@login_required
def already_registered():

    registered_user = church_user.query.get(current_user.id)

    return render_template('already-registered.html',user=registered_user,reg_info=pop_transactions)


# User Registrations
@app.route("/registered_users", methods=["POST", "GET"])
@login_required
def registered_users():

    registered_users = church_user.query.all()
    registered_no = pop_transactions.query.all()

    return render_template('registered_users.html',registered_users=registered_users,reg_details=pop_transactions,registered_no=registered_no)


# User Registrations
@app.route("/registrations", methods=["POST", "GET"])
@login_required
def registrations():

    registered_users = church_user.query.all()
    registered_no = pop_transactions.query.all()

    return render_template('registrations.html',registered_users=registered_users,reg_details=pop_transactions,registered_no=registered_no)

@app.route("/registration_success", methods=["POST", "GET"])
@login_required
def registration_success():

    registered_user = church_user.query.get(current_user.id)

    return render_template('registration-success.html',user=registered_user,reg_info=pop_transactions)


@app.route("/signup", methods=["POST","GET"])
def sign_up():

    register = Register()

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if register.validate_on_submit():

        #print(f"Account Successfully Created for {register.name.data}")
        if request.method == 'POST':
            # context
            hashd_pwd = encry_pw.generate_password_hash(register.password.data).decode('utf-8')
            user1 = church_user(name=register.name.data, email=register.email.data, password=hashd_pwd,
                         confirm_password=hashd_pwd, image="default.jpg",timestamp=datetime.now())

            try:
                db.session.add(user1)
                db.session.commit()
                flash(f"Account Successfully Created for {register.name.data}", "success")
                flash(f"Please Login & Verify your Account", "success")
                return redirect(url_for('login'))
                # return jsonify({"message": "User registered successfully"}), 201
            except IntegrityError:
                db.session.rollback()  # Rollback the session on error
                return jsonify({"message": "Email already exists"}), 409
            except Exception as e:
                db.session.rollback()  # Rollback on any other error
                return jsonify({"message": "An error occurred", "error": str(e)}), 500
            # try:
            #     db.session.add(user1)
            #     db.session.commit()
            #     flash(f"Account Successfully Created for {register.name.data}", "success")
            #     flash(f"Please Login & Verify your Account", "success")
            #     return redirect(url_for('login'))
            # except: # IntegrityError:
            #     flash(f"Something went wrong, check for errors", "success")
            #     Register().validate_email(register.email.data)

            # #print(register.name.data,register.email.data)
    elif register.errors:
        flash(f"Account Creation Unsuccessful ", "error")
        #print(register.errors)

    # from myproject.models import user
    return render_template("signup.html",register=register)

@app.route("/admin_signup", methods=["POST","GET"])
def admin_signup():

    register = Register()

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if register.validate_on_submit():

        #print(f"Account Successfully Created for {register.name.data}")
        if request.method == 'POST':
            # context
            hashd_pwd = encry_pw.generate_password_hash(register.password.data).decode('utf-8')
            user1 = admin_user(name=register.name.data, email=register.email.data, password=hashd_pwd,
                         confirm_password=hashd_pwd, image="default.jpg")

            try:
                db.session.add(user1)
                db.session.commit()
                flash(f"Account Successfully Created for {register.name.data}", "success")
                return redirect(url_for('login'))
            except: # IntegrityError:
                flash(f"Something went wrong, check for errors", "success")
                Register().validate_email(register.email.data)

            # #print(register.name.data,register.email.data)
    elif register.errors:
        flash(f"Account Creation Unsuccessful ", "error")
        #print(register.errors)

    # from myproject.models import user
    return render_template("signup.html",register=register)


@app.route("/finish_signup", methods=["POST","GET"])
@login_required
def finish_signup():

    user=None

    finish_register = UserAccountForm()
    if current_user.role == "church_user":
        user = church_user.query.get(current_user.id)
    else:
        user = admin_user.query.get(current_user.id)

    if finish_register.validate_on_submit():

        if request.method == 'POST':

            user.contacts=finish_register.contacts.data
            user.church_region=finish_register.church_region.data
            user.church_circuit=finish_register.church_circuit.data
            user.age_group=finish_register.age_group.data
            user.church_local=finish_register.church_local.data
            user.gender=finish_register.gender.data

            if finish_register.image.data:
                user.image = process_file(finish_register.image.data)

            # try:
            db.session.commit()
            flash(f"Update Successful! Proceed to Register for the currently upcoming Event.", "success")
            flash(f"You can do it later.", "success")
            if current_user.role == "church_user":
                return redirect(url_for('user_registration_form'))
            else:
                return redirect(url_for('open_event_form'))
                # except: # IntegrityError:
                #     flash(f"Something went wrong, check for errors", "success")
                
            # #print(finish_register.name.data,finish_register.email.data)
    elif finish_register.errors:
        for error in finish_register.errors:
            print("Error: ",error)
        flash(f"Account Creation Unsuccessful ", "error")

    # from myproject.models import user
    return render_template("finish_signup.html",finish_register=finish_register,user=user)



@app.route("/reset/<token>", methods=['POST', "GET"])
def reset(token):
    reset_form = Reset()

    if request.method == 'POST':

        # try:

        usr_obj = user_class().verify_reset_token(token)
        pass_reset_hash = encry_pw.generate_password_hash(reset_form.new_password.data)
        usr_obj = User.query.get(usr_obj)
        usr_obj.password = pass_reset_hash
        db.session.commit()

        flash(f"You have Successfully Changed your Password! You can now Login with your New Password", "success")

        return redirect(url_for("login"))
        # except:
        #     print("Password Reset Failed!!")
        #     flash(f"Password Reset Failed, Please try again later", "error")
        #     return f'Reset Failed, Try again later'

    return render_template("pass_reset.html", reset_form=reset_form)


@app.route("/forgot_password", methods=['POST', "GET"])
def reset_request():

    reset_request_form = Reset_Request()

    if current_user.is_authenticated:
        logout_user()

    if request.method == 'POST':
        if reset_request_form.validate_on_submit():
            # Get user details through their email
            usr_email = User.query.filter_by(email=reset_request_form.email.data).first()

            if usr_email is None:
                # print("The email you are request for is not register with T.H.T, please register first, Please Retry")
                flash("The email you are requesting a password reset for, is not registered, please register an account first",
                    'error')

                return redirect(url_for("reset_request"))

            def send_link(usr_email):
                app.config["MAIL_SERVER"] = "smtp.googlemail.com"
                app.config["MAIL_PORT"] = 587
                app.config["MAIL_USE_TLS"] = True
                em = app.config["MAIL_USERNAME"] = "pro.dignitron@gmail.com" #os.getenv("EMAIL")
                app.config["MAIL_PASSWORD"] = "abngvekbagyvosbw" # os.getenv("PWD")

                mail = Mail(app)

                token = user_class().get_reset_token(usr_email.id)
                msg = Message("Password Reset Request", sender="noreply@demo.com", recipients=[usr_email.email])
                msg.html = f"""<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f6f6f6;
            color: #333;
            padding: 20px;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        h2,h3 {{
            color: #4CAF50;
        }}
        p,li{{font-weight:500;color:#505050 }}
        .footer {{
            margin-top: 20px;
            font-size: 0.9em;
            color: #777;
        }}
        span{{ font-weight:600;color:coral}}
    </style>
</head>
<body>
    <div class="container">
        <img style="" src="https://africec.org/images/webimages/logo/logo.png" />
        <h2>Good day, {usr_email.name}</h2>

        <p>You have requested a password reset for your Church Registrations - A.E.C Account.</p>
        <p style="font-weight:600">To reset your password, visit the following link;</p>
        <a href="{url_for('reset', token=token, _external=True)}" 
            style="display: inline-block; padding: 10px 20px; font-size: 16px; color: #fff; background-color: #4CAF50; 
                    border: none; border-radius: 15px; text-decoration: none; text-align: center;">
            Reset
        </a>
        <p class="footer">If you did not request the above message please ignore it, and your password will remain unchanged.</p>
    </div>
</body>
</html>
"""

                try:
                    mail.send(msg)
                    flash('An email has been sent with instructions to reset your password', 'success')
                    return "Email Sent"
                except Exception as e:

                    flash('Ooops, Something went wrong Please Retry!!', 'error')
                    return "The mail was not sent"


            # Send the pwd reset request to the above email
            send_link(usr_email)

            return redirect(url_for('login'))

    return render_template("password_reset_req.html", reset_request_form=reset_request_form)


@app.route("/verification", methods=["POST", "GET"])
# User email verification @login
# @login the user will register & when the log in the code checks if the user is verified first...
def verification():

    usr_ = User.query.get(current_user.id)

    def send_veri_mail():

        app.config["MAIL_SERVER"] = "smtp.googlemail.com"
        app.config["MAIL_PORT"] = 587
        app.config["MAIL_USE_TLS"] = True
        # Creditentials saved in environmental variables
        em = app.config["MAIL_USERNAME"] = "pro.dignitron@gmail.com"  # os.getenv("MAIL")
        app.config["MAIL_PASSWORD"] =  "abngvekbagyvosbw" #os.getenv("PWD")
        app.config["MAIL_DEFAULT_SENDER"] = "noreply@gmail.com"

        mail = Mail(app)

        token = user_class().get_reset_token(current_user.id)
        usr_email = usr_.email

        msg = Message(subject="Email Verification", sender="no-reply@gmail.com", recipients=[usr_email])

        msg.html = f"""<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f6f6f6;
            color: #333;
            padding: 20px;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        h2,h3 {{
            color: #4CAF50;
        }}
        p,li{{font-weight:500;color:#505050 }}
        .footer {{
            margin-top: 20px;
            font-size: 0.9em;
            color: #777;
        }}
        span{{ font-weight:600;color:coral}}
    </style>
</head>
<body>
    <div class="container">
        <img style="" src="https://africec.org/images/webimages/logo/logo.png" />
        <h2>Hi, {usr_.name}</h2>

        <p>Please follow the link below to verify your email with Church Registrations - AEC:</p>
        <p style="font-weight:600">Verification link;</p>
        <a href="{ url_for('verified', token=token, _external=True) }" 
            style="display: inline-block; padding: 10px 20px; font-size: 16px; color: #fff; background-color: #4CAF50; 
                    border: none; border-radius: 15px; text-decoration: none; text-align: center;">
            Verify Email
        </a>
        <p class="footer">Thank you for registering an account!</p>
    </div>
</body>
</html>
"""


        # try:
        mail.send(msg)
        flash(f'An email has been sent with a verification link to your email account', 'success')
        log_out()
        return "Email Sent"
        # except Exception as e:
        #     flash(f'Email not sent here', 'error')
        #     return "The mail was not sent"

    # try:
    if not usr_.verified:
        send_veri_mail()
    else:
        log_out()
        return redirect(url_for("home"))
    # except:
    #     flash(f'Email Not Sent. Please try again', 'error')
    #     log_out()
    #     return redirect(url_for("login"))

    return render_template('verification.html')


@app.route("/verified/<token>", methods=["POST", "GET"])
# Email verification link verified with a token
def verified(token):
    # Check to verify the token received from the user email
    # process the user_id for the following script
    user_id = user_class.verify_reset_token(token)

    try:
        usr = User.query.get(user_id)
        usr.verified = True
        db.session.commit()
        if usr.verified:
            qry_usr = User.query.get(user_id)
            if not current_user.is_authenticated:
                login_user(usr)
                if not current_user.church_local and not current_user.church_circuit:
                    print("Finish Setup")
                    flash(f"Welcome! {qry_usr.name.title()}, Please Finish your Sign-up process", "success")
                    return redirect(url_for('finish_signup'))
            # return redirect(url_for('account'))
    except Exception as e:
        flash(f"Something went wrong, Please try again ", "error")

    return render_template('verified.html')


@app.route('/logout')
def log_out():

    logout_user()

    return redirect(url_for('home'))


# User Account
@app.route("/user_account", methods=["POST", "GET"])
def user_account():
    usr_account=None
    account_form = UserAccountForm()
    if current_user.role == 'church_user':
        usr_account=church_user.query.get(current_user.id)
    else:
        usr_account=admin_user.query.get(current_user.id)

    if account_form.validate_on_submit():

        if request.method == 'POST':

            usr_account.contacts=account_form.contacts.data
            usr_account.church_region=account_form.church_region.data
            usr_account.church_circuit=account_form.church_circuit.data
            usr_account.age_group=account_form.age_group.data
            usr_account.church_local=account_form.church_local.data
            usr_account.gender=account_form.gender.data

            if account_form.image.data:
                usr_account.image = process_file(account_form.image.data)

            # try:
            db.session.commit()
            flash(f"Update Successful!", "success")
            print("Update Successful!")


    return render_template('user_account.html',account_form =account_form, usr_account=usr_account)


# Admin Account
@app.route("/admin_account", methods=["POST", "GET"])
def admin_account():

    return render_template('admin_account.html')

#google login
@app.route("/google_login", methods=["POST","GET"])
def google_login():

    print("DEBUG CREDITENTAILS: ",appConfig.get("OAUTH2_CLIENT_ID"),' ',appConfig.get("OAUTH2_CLIENT_SECRET"))

    return oauth.Registra.authorize_redirect(redirect_uri=url_for("google_signin",_external=True))


#login redirect
@app.route("/google_signin", methods=["POST","GET"])
def google_signin():

    token = oauth.Registra.authorize_access_token()

    session['user'] = token

    return redirect(url_for('home'))

#Verification Pending
@app.route("/login", methods=["POST","GET"])
def login():

    login = Login()

    if login.validate_on_submit():

        if request.method == 'POST':

            user_login = User.query.filter_by(email=login.email.data).first()
            if user_login and encry_pw.check_password_hash(user_login.password, login.password.data):
                
                login_user(user_login)
                print("No Verification Needed: ", user_login.verified)
                req_page = request.args.get('next')
                flash(f"Hey! {user_login.name.title()} You're Logged In!", "success")

                if not current_user.church_local and not current_user.church_circuit:
                    print("Finish Setup")
                    flash(f"Welcome! {user_login.name.title()}, Please Finish your Sign-up process", "success")
                    return redirect(url_for('finish_signup'))
            
                return redirect(req_page) if req_page else redirect(url_for('home'))

                # if not user_login.verified:
                #     login_user(user_login)
                #     return redirect(url_for('verification'))
                # else:
                #     # After login required prompt, take me to the page I requested earlier
                #     login_user(user_login)
                #     print("No Verification Needed: ", user_login.verified)
                #     req_page = request.args.get('next')
                #     flash(f"Hey! {user_login.name.title()} You're Logged In!", "success")

                #     if not current_user.church_local and not current_user.church_circuit:
                #         print("Finish Setup")
                #         flash(f"Welcome! {user_login.name.title()}, Please Finish your Sign-up process", "success")
                #         return redirect(url_for('finish_signup'))
                
                #     return redirect(req_page) if req_page else redirect(url_for('home'))
            else:
                flash(f"Login Unsuccessful, please use correct email or password", "error")
                # print(login.errors)
    else:
        print("No Validation")
        if login.errors:
            for error in login.errors:
                print("Errors: ", error)
        else:
            print("No Errors found", login.email.data, login.password.data)

    return render_template("login.html",login=login)





# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    with app.app_context():
       db.create_all()

    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
