import os
import sys
import click

from flask import Flask,render_template,flash,redirect,request,url_for
from werkzeug.security import 
generate_password_hash,check_password_hash 
from flask_login import LoginManager,UserMixin
from flask_sqlalchemy import SQLAlchemy   #导入扩展类

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'   #windows
else:
    prefix = 'sqlite:////'   #linux，mic其他平台

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    #关闭对模型修改的监控
app.config['SECRET_KEY'] = 'watchlist_dev'
db = SQLAlchemy(app)  #初始化扩展，传入程序实例app
login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


#自定义命令
@app.cli.command()    #装饰器，注册命令
@click.option('--drop',is_flag=True,help='Create after drop(删除后再创建)')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('初始化数据库完成。。。')

@app.cli.command()
def forge():
    db.create_all()
    name = "zzz"
    movies = [
        {'title':'功夫之王','year':'2010'},
        {'title':'机器之血','year':'2015'},
        {'title':'复仇者联盟3','year':'2017'},
        {'title':'微微一笑很倾城','year':'2018'},
        {'title':'百鸟朝凤','year':'2019'},
        {'title':'唐人街探案3','year':'2020'},
        {'title':'杀破狼','year':'2010'},
        {'title':'扫毒','year':'2010'},
        {'title':'机器之血','year':'2010'},
        {'title':'分手大师','year':'2010'},
        {'title':'这个杀手不太冷','year':'2010'},
        {'title':'邻里的人们','year':'2010'},
        {'title':'釜山行','year':'2010'},
        {'title':'拯救大兵瑞恩','year':'2010'},
        {'title':'我的特工爷爷','year':'2010'},
        {'title':'战狼','year':'2010'}
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('导入数据完成')

# 生成管理员账户
@app.cli.command()
@click.option('--username',prompt=True,help='用户名')
@click.option('--password',prompt=True,help='密码',confirmation_prompt=True,hide_input=True)
def admin(username,password):
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('更新用户')
        user.username = username
        user.set_password(password)
    else:
        click.echo('创建用户')
        user = User(username=username,name='Bruce')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('完成')




# 错误处理函数
@app.errorhandler(404)
def page_not_found(e):
    # user = User.query.first()
    # 返回模板和状态码
    return render_template('404.html',user=user)

# 模板上下文处理函数
@app.context_processor
def common_user():
    user = User.query.first()
    return dict(user=user)




#models.py
class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)  # 主键
    name = db.Column(db.String(20))  # name
    username = db.Column(db.String(20))  
    password_hash = db.Column(db.String(128))

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self,password):
        return check_password_hash(self.password_hash,password) 

class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)   #主键
    title = db.Column(db.String(60))  #电影标题
    year = db.Column(db.String(4))  #电影年份





#views
#多URL

@app.route('/',methods=['GET','POST'])
# @app.route('/index')
# @app.route('/home')
#首页
def index():
    if request.method == 'POST':
        title = request.from.get('title')
        year = request.from.get('year')
        # 验证数据
        if not title or not year or len(year)>4 or len(title)>60
            flask('不能为空或超过最大长度')
            return redirect(url_for('index'))

        # 保存表单vie
        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flask('更新成功')
        return redirect(url_for('index'))
    return render_template('edit.html',movie=movie)

# 删除
@app.route('movie/delete/<int:movie_id>',methods=['POST',])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.add(movie)
    db.session.commit()
    flask('删除成功')
    return redirect(url_for('index'))

# 登录
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('输入错误')
            return redirect(url_for('login'))
        
        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('登录成功')
            return redirect(url_for('index'))
        
        flash('用户名或者密码错误')
        return redirect(url_for('login'))
    return render_template('login.html')
# 登出
@app.route('/logout')
def logout():
    logout_user()
    flash('退出')
    return redirect(url_for('index'))


    # user = User.query.first()   #读取用户记录
    movies = Movie.query.all()  #读取所有电影记录
    return render_template('index.html',movies=movies)
    # return "<h1>hello,Flask!!!</h1>"

# #处理页面404错误
# @app.errorhandler(404)
# def page_not_found(e):
#     # user = User.query.first()
#     return render_template('404.html'),404


# #模板上下文处理函数,在多个模板内都需要使用的变量
# @app.context_processor
# def inject_user():
#     user = User.query.first()
#     return dict(user=user)




#动态URL
# @app.route('/index/<name>')
# def home(name):
#     print(url_for("home",name='zaz'))
#     return "<h1>hello,%s!!!</h1>"%name