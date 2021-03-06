import os

from flask import (Flask, render_template, request, jsonify, session, redirect, send_file)
from controller import constants
from controller.database import Database
from models import Student,Commuter,Blog,Comment,User
from werkzeug.utils import secure_filename
from match import Keyword_Extractor
from flask_uploads import UploadSet, configure_uploads,  ALL

app = Flask(__name__)
app.secret_key = "NotSecure"

basedir=os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = str(basedir)+'\\uploads\\'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','doc'])


@app.before_first_request
def initialize_db():
    Database.initialize()



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/test')
def test():
    message=''
    return render_template('auth/test.html', prompt_error=message)


@app.route('/static/test')
def static_test():
    return send_file('static/detail01.html')


@app.route('/match')
def match():

    return render_template('match/match.html')


#----------------------------------  User  ----------------------------------
@app.route('/log')
def log_user():
    email = session.get('email')
    if email is not None :
        return render_template('auth/log.html')

    return render_template('auth/log.html')


@app.route('/profile')
def user_profile():
    student = Student.get_by_email(session.get('email'))
    commuter = Commuter.get_by_email(session.get('email'))
    identity = "student"
    if student is None:
        user = commuter
        identity = "commuter"
    else:
        user = student

    return render_template('auth/profile.html', user=user, identity=identity)


@app.route('/auth/login', methods=["POST"])
def lg_user():
    id = request.form['identity']
    email = request.form['email']
    password = request.form['password']
    if id=='student':
        return login_student(email, password)
    elif id == 'commuter':
        return login_commuter(email, password)





def login_student(email, password):
    students=Database.find_one(collection=constants.STUDENT_COLLECTION, query={"email": email})
    if students is not None:
        if students["password"]==password:
            session.__setitem__('email', email)
            session.__setitem__('name', students["name"])
        else:
            session.__setitem__('email', None)
            session.__setitem__('name', None)
            return render_template('auth/log.html', prompt_error="密码错误")
    else:
        session.__setitem__('email', None)
        session.__setitem__('name', None)
        return render_template('auth/log.html', prompt_error="该用户不存在  ")
    return redirect('/', code=302)


@app.route('/reg')
def dis_reg():
    return render_template('auth/register.html')

@app.route('/auth/register', methods=["POST"])
def register_user():
    prompt_message = ""
    email = request.form.get('email')
    password = request.form.get('password')
    sex = "请完善性别信息"
    name = "请完善姓名信息"
    identity = request.form.get("identity")
    school = request.form.get('school')
    company = request.form.get('company')
    if school == "":
        school = "请完善学校信息"
    if company == "":
        company == "请完善公司信息"
    if identity == "student":
        return register_student(email, password, sex, name, school)
    elif identity == "commuter":
        return register_commuter(email, password, sex, name, company)
    prompt_message = "something wrong happening!!"
    return render_template('auth/register.html', prompt_error=prompt_message)



def register_student(email, password, sex, name, school):
    # prompt_alert = ""
    if not len(email) or not len(password) or not len(name):
        prompt_alert = "Please enter valid email and password values."
    elif Student.register(email, password, sex, [], name, school):
        return redirect('/', code=302)
    else:
        prompt_alert = 'User with the same email already exists!'
    return render_template('auth/register.html', prompt_error=prompt_alert)


def login_commuter(email, password):
    commuters=Database.find_one(collection=constants.COMMUTER_COLLECTION, query={"email": email})
    if commuters is not None:
        if commuters["password"]==password:
            session.__setitem__('email', email)
            session.__setitem__('name', commuters["name"])
        else:
            session.__setitem__('email', None)
            session.__setitem__('name', None)
            return render_template('auth/log.html', prompt_error="密码错误")
    else:
        session.__setitem__('email', None)
        session.__setitem__('name', None)
        return render_template('auth/log.html', prompt_error="该用户不存在  ")
    return redirect('/', code=302)



def register_commuter(email, password, sex, name, company):
    # prompt_alert = ""
    if not len(str(email)) or not len(str(password)) or not len(str(name)):
        prompt_alert = "Please enter valid email and password values."
    elif Commuter.register(email, password, sex, name, company):
        return redirect('/', code=302)
    else:
        prompt_alert = 'User with the same email already exists!'
    return render_template('auth/register.html', prompt_error=prompt_alert)

@app.route('/logout')
def logout():
    User.logout()
    return redirect('/')


#----------------------------------  Blog  ----------------------------------
@app.route('/blogs/search/<title>')
def get_blog_search(title):
    blogs=Blog.get_by_title_re(title)
    user=User.get_by_email()
    return render_template('/templates/community/search.html', blogs=blogs, user=user)


@app.route('/blog/delete/<blog_id>')
def delete_blog(blog_id):

    blog = Blog.get_by_id(blog_id)
    user = User.get_by_id(blog.author_id)
    Blog.delete_all_from_mongo_viaQuery({'blog_id':blog_id})
    Blog.delete_from_mongo_viaId(blog_id)
    blogs = user.get_blogs()
    return render_template('blogs/doctorblogs.html', blogs=blogs, email=session.get('email'), c=0)


@app.route('/blog/<blog_id>')
def get_blog(blog_id=None):
    blog = Blog.get_by_id(blog_id)
    comments = blog.get_comments()
    content = str(blog.description)
    print(content)


    return render_template('blog/single-blog.html', blog=blog, comments=comments,content = content)


@app.route('/myblogs')
def get_blogs(user_id=None):
    user = None
    if user_id:
        user = User.get_by_id(user_id)
    elif not user_id:
        user = User.get_by_email(session.get('email'))
    if not user:
        return render_template('error_404.html')

    user_blogs = user.get_blogs()
    return render_template('blogs/myblogs.html', blogs=user_blogs, email=session.get('email'), c=0)


@app.route('/publish')
def pubblog():
    return render_template('blog/publish.html')


@app.route('/blog/create', methods=['POST'])
def create_new_blog():
    student = Student.get_by_email(session.get('email'))
    commuter = Commuter.get_by_email(session.get('email'))
    if student is None:
        user = commuter
    else:
        user = student

    title = request.form.get('title')
    description = request.form.get('blogContent')
    blog = Blog(title=title, description=description, author=user.name, author_id=user._id)
    blog.save_to_mongo()
    return redirect('/')


# -----------------------------  Comments  ----------------------------------
@app.route('/jobs')
def send_jobs():
    blogs = Blog.get_all_blogs()

    return render_template('blog/jobs.html', blogs=blogs)


@app.route('/comment/create/<blog_id>',methods=['POST'])
def create_new_comment(blog_id):
    student = Student.get_by_email(session.get('email'))
    commuter = Commuter.get_by_email(session.get('email'))
    if student is None:
        user = commuter
    else:
        user = student

    title = request.form.get('blogTitle')
    description = request.form.get('blogDescription')
    comment = Comment(blog_id, description, user.name)
    comment.save_to_mongo()
    return redirect('/')


#----------------------------------  Detail  ----------------------------------
@app.route('/detail01')
def detail_01():
    return  render_template('detail/detail01.html')


@app.route('/detail02')
def detail_02():
    return  render_template('detail/detail02.html')


@app.route('/detail03')
def detail_03():
    return  render_template('detail/detail03.html')


@app.route('/play01')
def play01():
    return render_template('detail/play01.html')


@app.route('/play02')
def play02():
    return render_template('detail/play02.html')


@app.route('/play03')
def play03():
    return render_template('detail/play03.html')


@app.route('/play04')
def play04():
    return render_template('detail/play04.html')


#----------------------------------  File  ----------------------------------
def allowed_file(filename):   # 验证上传的文件名是否符合要求，文件名必须带点并且符合允许上传的文件类型要求，两者都满足则返回 true
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload/<string:name>')
@app.route('/upload', methods=['POST'])
def upload_file(name=None):
    if request.method == 'POST':   # 如果是 POST 请求方式
        file = request.files.get('file')   # 获取上传的文件
        if file and allowed_file(file.filename):   # 如果文件存在并且符合要求则为 true
            filename = secure_filename(file.filename)   # 获取上传文件的文件名
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))   # 保存文件
            result = {
                "code":0,
                "msg":"",
                "data":{
                    "src":(str(os.path.join(app.config['UPLOAD_FOLDER']))+filename),
                    "title":filename
                }
            }
        else:
            result = {
                "code":1,
                "msg":"图片上传失败",
                "data":{
                    "src":"",
                    "title":name
                }
            }
        print(result)
        return result   # 返回保存成功的信息

    if not name:
        return render_template('error_404.html')
    file_path = os.path.join(UPLOAD_FOLDER, name)
    return send_file(file_path)




@app.route('/pdf/upload', methods=['POST','GET'])
def upload_pdf(name=None):
    if request.method == 'POST':   # 如果是 POST 请求方式
        file = request.files.get('file')   # 获取上传的文件
        if file and allowed_file(file.filename):   # 如果文件存在并且符合要求则为 true
            filename = secure_filename(file.filename)   # 获取上传文件的文件名
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))   # 保存文件
            result = {
                "code":0,
                "msg":"",
                "data":{
                    "src":(str(os.path.join(app.config['UPLOAD_FOLDER']))+filename),
                    "title":filename
                }
            }
        else:
            result = {
                "code":1,
                "msg":"图片上传失败",
                "data":{
                    "src":"",
                    "title":name
                }
            }
        extactor = Keyword_Extractor.Extractor(UPLOAD_FOLDER+filename)
        sim = extactor.match()
        for i in range(2):
            result[extactor.joblist[i]] = " matching rate: " + str(sim[i])
        print(result)
        return render_template('match/matchResult.html', result=result)   # 返回保存成功的信息

    #get request
    if not name:
        return render_template('error_404.html')
    file_path = os.path.join(UPLOAD_FOLDER, name)
    return send_file(file_path)





if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
