import click
from blog.models import User,Movie
from blog import app,db
# 注册命令
@app.cli.command()
@click.option('--drop',is_flag=True,help='Create after drop')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('初始化数据库。。。')# 注册命令

# 导入数据
@app.cli.command()
def forge():
    db.create_all()
    name = "aaa"
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
        user = User(username=username,name='aaa')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('完成')