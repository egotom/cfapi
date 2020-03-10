from flask_sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()

class Department(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	su_id = db.Column(db.Integer, nullable=False)
	name = db.Column(db.String(), nullable=False)
	d_v=db.relationship('Visitor',backref='Department',uselist=True)

	def __init__(self, su_id, name):
		self.su_id = su_id
		self.name = name

class Duty(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	role=db.Column(db.Integer,nullable=True)
	wn_min=db.Column(db.Integer,nullable=True)
	wp_min=db.Column(db.Integer,nullable=True)
	mc_max=db.Column(db.Integer,nullable=True)
	wc_max=db.Column(db.Integer,nullable=True)
	dc_min=db.Column(db.Integer,nullable=True)
	mp_max=db.Column(db.Integer,nullable=True)
	mp_min=db.Column(db.Integer,nullable=True)
	mn_min=db.Column(db.Integer,nullable=True)
	score=db.Column(db.Integer,nullable=True)
	lmt=db.Column(db.Integer,nullable=True)
	name=db.Column(db.String(50),nullable=False)
	d_v=db.relationship('Visitor',backref='Duty',uselist=True)

	def __init__(self,role,lmt,name):
		self.role=role
		self.lmt=lmt
		self.name=name

class Reward(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    classify=db.Column(db.String(50),nullable=True)
    classify_code=db.Column(db.String(5),nullable=True)
    name=db.Column(db.String(50),nullable=True)

    def __init__(self,classify_code,name):
        self.classify_code=classify_code
        self.name=name

class Rule(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	score=db.Column(db.Integer,nullable=True)
	serial=db.Column(db.String(50), nullable=True)
	department=db.Column(db.String(50), nullable=True)
	duty=db.Column(db.String(50), nullable=True)
	inherit=db.Column(db.Enum('True','False'),nullable=True)
	classify=db.Column(db.Enum('A+','B+','C+','A-','B-','C-'),nullable=True)
	property=db.Column(db.String(50),nullable=True)
	units=db.Column(db.String(50),nullable=True)
	description=db.Column(db.String(50),nullable=True)
	term=db.Column(db.String(50),nullable=True)

	def __init__(self,score,department,classify,serial,description,property,units,term):
		self.score=score
		self.department=department
		self.classify=classify
		self.serial=serial
		self.description=description
		self.property=property
		self.units=units
		self.term=term
		

class Propose(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	proposer_id=db.Column(db.Integer,nullable=False)
	beneficiary_id=db.Column(db.Integer,nullable=False)
	approver_id=db.Column(db.Integer,nullable=True)
	refer_id=db.Column(db.Integer,nullable=True)
	score=db.Column(db.Integer,nullable=True)
	appl=db.Column(db.Integer,nullable=True)
	refer=db.Column(db.Enum('R','T','S','C','F'),nullable=True)
	classify=db.Column(db.Enum('A+','B+','C+','A-','B-','C-'),nullable=True)
	state=db.Column(db.Enum('通过审核','未通过审核','提交成功'),nullable=True)
	description=db.Column(db.String(200),nullable=True)
	commit=db.Column(db.String(200),nullable=True)
	appeal=db.Column(db.String(200),nullable=True)
	update_at=db.Column(db.TIMESTAMP(True),nullable=False)
	create_at=db.Column(db.TIMESTAMP(True),nullable=False)

	def __init__(self,proposer_id,beneficiary_id,approver_id,refer_id,refer,score,state,classify,description):
		self.proposer_id=proposer_id
		self.beneficiary_id=beneficiary_id
		self.approver_id=approver_id
		self.refer_id=refer_id
		self.refer=refer
		self.score=score
		self.state=state
		self.classify=classify
		self.description=description
		self.create_at=datetime.datetime.now()

class Task(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	creator_id=db.Column(db.Integer,db.ForeignKey('visitor.id'),nullable=False)
	approver_id=db.Column(db.Integer,nullable=False)
	score=db.Column(db.Integer,nullable=False)
	menber=db.Column(db.Integer,nullable=True)
	state=db.Column(db.Integer,nullable=True)
	score_type=db.Column(db.Enum('A+','B+','C+'),nullable=False)	
	description=db.Column(db.String(255),nullable=False)
	pub_at=db.Column(db.TIMESTAMP(True),nullable=False)
	expiry_at=db.Column(db.TIMESTAMP(True),nullable=False)
	update_at=db.Column(db.TIMESTAMP(True),nullable=False)
	create_at=db.Column(db.TIMESTAMP(True),nullable=False)
	vt_t=db.relationship('VisitorTask',backref='Task',uselist=True)
	
	def __init__(self,creator_id,approver_id,menber,score,state,score_type,description,expiry_at,pub_at):
		self.creator_id=creator_id
		self.approver_id=approver_id
		self.menber=menber
		self.score=score
		self.state=state
		self.score_type=score_type
		self.description=description
		self.expiry_at=expiry_at
		self.pub_at=pub_at
		self.create_at=datetime.datetime.now()

class VisitorTask(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	task_id=db.Column(db.Integer,db.ForeignKey('task.id'),nullable=False)
	target_visitor=db.Column(db.Integer,nullable=True)
	target_department=db.Column(db.Integer,nullable=True)
	accept_id=db.Column(db.Integer,nullable=False)
	update_at=db.Column(db.TIMESTAMP(True),nullable=False)
	create_at=db.Column(db.TIMESTAMP(True),nullable=False)
	
	
	def __init__(self,task_id,target_visitor,target_department,accept_id):
		self.task_id=task_id
		self.target_visitor=target_visitor
		self.target_department=target_department
		self.accept_id=accept_id
		self.create_at=datetime.datetime.now()
		
class Notice(db.Model):
		id=db.Column(db.Integer,primary_key=True)
		post_id=db.Column(db.Integer,nullable=False)
		subject=db.Column(db.String(50),nullable=False)
		msg=db.Column(db.String(250),nullable=False)
		create_at=db.Column(db.TIMESTAMP(True),nullable=False)
		
		def __init__(self,post_id,subject,msg):
			self.post_id=post_id
			self.subject=subject
			self.msg=msg
			self.create_at=datetime.datetime.now()

class Visitor(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	department_id=db.Column(db.Integer,db.ForeignKey('department.id'),nullable=True)
	duty_id=db.Column(db.Integer,db.ForeignKey('duty.id'),nullable=True)
	auth=db.Column(db.Integer,nullable=True)
	team=db.Column(db.Enum('先锋队','蛟龙队','雄狮队','猛虎队','战狼队','猎豹队','飞鹰队','神象队','巨猿队','海鲨队','火鸟队','蓝鲸队','骏马队','金牛队'),nullable=True)
	title=db.Column(db.Enum('高级','中级','初级'),nullable=True)
	sex=db.Column(db.Enum('男','女'),nullable=True)
	education=db.Column(db.Enum('本科','大专','初中','中专','高中','硕士','小学'),nullable=True)
	name = db.Column(db.String(50), nullable=True)
	passwd = db.Column(db.String(50), nullable=True)
	tel=db.Column(db.String(50), nullable=True)
	secrity=db.Column(db.String(50), nullable=True)
	level=db.Column(db.String(50), nullable=True)
	wx_nickname = db.Column(db.String(50), nullable=True)
	wx_openid = db.Column(db.String(50), nullable=True)
	wx_sex  = db.Column(db.String(1), nullable=True)
	wx_province = db.Column(db.String(50), nullable=True)
	wx_city = db.Column(db.String(50), nullable=True)
	wx_country = db.Column(db.String(50), nullable=True)
	wx_headimgurl = db.Column(db.String(200), nullable=True)
	wx_privilege  = db.Column(db.String(255), nullable=True)
	birthday = db.Column(db.TIMESTAMP(True),nullable=True)
	date_in = db.Column(db.TIMESTAMP(True),nullable=True)
	v_t=db.relationship('Task',backref='Visitor',uselist=True)
	#v_b=db.relationship('Lottery',backref='Beneficiary')
	#v_d=db.relationship('Lottery',backref='Distributor')
	
	def __init__(self,wx_nickname, wx_sex, wx_province,wx_city,wx_country,wx_headimgurl,wx_privilege):
		self.wx_nickname        =wx_nickname
		self.wx_sex             =wx_sex
		self.wx_province        =wx_province
		self.wx_city            =wx_city
		self.wx_country         =wx_country
		self.wx_headimgurl      =wx_headimgurl
		self.wx_privilege       =wx_privilege

class Employee(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	department_id=db.Column(db.Integer,db.ForeignKey('department.id'),nullable=True)
	duty_id=db.Column(db.Integer,db.ForeignKey('duty.id'),nullable=True)
	auth=db.Column(db.Integer,nullable=True)
	team=db.Column(db.Enum('梦想队','先锋队','蛟龙队','雄狮队','猛虎队','战狼队','猎豹队','飞鹰队','神象队','巨猿队','海鲨队','火鸟队','蓝鲸队','骏马队','金牛队'),nullable=True)
	title=db.Column(db.Enum('高级','中级','初级'),nullable=True)
	sex=db.Column(db.Enum('男','女'),nullable=True)
	education=db.Column(db.Enum('本科','大专','初中','中专','高中','硕士','小学'),nullable=True)
	name = db.Column(db.String(50), nullable=True)
	passwd = db.Column(db.String(50), nullable=True)
	tel=db.Column(db.String(50), nullable=True)
	secrity=db.Column(db.String(50), nullable=True)
	level=db.Column(db.String(50), nullable=True)
	wx_nickname = db.Column(db.String(50), nullable=True)
	wx_openid = db.Column(db.String(50), nullable=True)
	wx_sex  = db.Column(db.String(1), nullable=True)
	wx_province = db.Column(db.String(50), nullable=True)
	wx_city = db.Column(db.String(50), nullable=True)
	wx_country = db.Column(db.String(50), nullable=True)
	wx_headimgurl = db.Column(db.String(200), nullable=True)
	wx_privilege  = db.Column(db.String(255), nullable=True)
	birthday = db.Column(db.TIMESTAMP(True),nullable=True)
	date_in = db.Column(db.TIMESTAMP(True),nullable=True)
	
class Group(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	member = db.Column(db.Integer,nullable=True)
	name = db.Column(db.String(50), nullable=True)
	
	def __init__(self,name):
		self.name=name
		
class Token(db.Model):
	token = db.Column(db.String(255),primary_key=True)
	nickname = db.Column(db.String(100), nullable=True)
	openid = db.Column(db.String(50), nullable=True)
	avatar = db.Column(db.String(200), nullable=True)
	sts = db.Column(db.String(255), nullable=True)
	vid = db.Column(db.Integer, nullable=True)
	uid = db.Column(db.Integer, nullable=True)
	tid = db.Column(db.Integer, nullable=True)
	did = db.Column(db.Integer, nullable=True)
	oid = db.Column(db.Integer, nullable=True)
	create_at = db.Column(db.TIMESTAMP(True),nullable=True)
	def __init__(self,token,vid=None,uid=None,tid=None,did=None,oid=None,sts=None):
		self.token=token
		self.sts=sts
		self.vid=vid
		self.uid=uid
		self.tid=tid
		self.did=did
		self.oid=oid
		self.create_at=datetime.datetime.now()
		
class Lottery(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	propose_id = db.Column(db.Integer, nullable=True)
	beneficiary_id = db.Column(db.Integer,db.ForeignKey('visitor.id'),nullable=False)
	distributor_id = db.Column(db.Integer,db.ForeignKey('visitor.id'),nullable=False)
	printer_id = db.Column(db.Integer, db.ForeignKey('visitor.id'), nullable=False)
	description = db.Column(db.String(255),nullable=False)
	classify = db.Column(db.Enum('金券','银券','红券'),nullable=False)
	state = db.Column(db.Enum('已打印','未打印','已使用','投注'),nullable=False)
	print_at = db.Column(db.TIMESTAMP, nullable=True)
	create_at = db.Column(db.TIMESTAMP, nullable=False)
	Beneficiary = db.relationship("Visitor", foreign_keys=[beneficiary_id])
	Distributor = db.relationship("Visitor", foreign_keys=[distributor_id])
	Printer = db.relationship("Visitor", foreign_keys=[printer_id])
	
	def __init__(self,beneficiary_id, distributor_id, description, classify):
		self.beneficiary_id=beneficiary_id
		self.distributor_id=distributor_id
		self.description=description
		self.classify=classify
		self.state='未打印'
		self.create_at=datetime.datetime.now()
	
class Schedule(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	creater_id = db.Column(db.Integer, db.ForeignKey('visitor.id'), nullable=False)
	score = db.Column(db.Integer, nullable=True)
	classify = db.Column(db.Enum('A+','B+','C+','A-','B-','C-'),nullable=True)
	period = db.Column(db.Integer, nullable=True)
	enable = db.Column(db.Integer, nullable=True)
	title = db.Column(db.String(50),nullable=True)
	description = db.Column(db.String(200),nullable=True)
	beneficiary = db.Column(db.String(200), nullable=False)
	create_at = db.Column(db.TIMESTAMP(True),nullable=True)
	
	def __init__(self,creater_id, score, beneficiary,classify, period,title,description):
		self.creater_id=creater_id
		self.score=score
		self.classify=classify
		self.period=period
		self.title=title
		self.description=description
		self.beneficiary=beneficiary
		self.enable=1
		self.create_at=datetime.datetime.now()
		
class Attendance(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	isBoss= db.Column(db.Integer,nullable=True)
	isSenior= db.Column(db.Integer,nullable=True)
	active= db.Column(db.Integer,nullable=True)
	isAdmin= db.Column(db.Integer,nullable=True)
	isHide= db.Column(db.Integer,nullable=True)
	unionid= db.Column(db.String(30),nullable=True)
	openId = db.Column(db.String(30),nullable=True)
	remark = db.Column(db.String(200),nullable=True)
	userid = db.Column(db.String(30),nullable=True)
	isLeaderInDepts = db.Column(db.String(200),nullable=True)
	tel= db.Column(db.String(8),nullable=True)
	department= db.Column(db.String(50),nullable=True)
	workPlace= db.Column(db.String(50),nullable=True)
	orderInDepts= db.Column(db.String(50),nullable=True)
	mobile = db.Column(db.String(50),nullable=True)
	jobnumber= db.Column(db.String(30),nullable=True)
	name= db.Column(db.String(4),nullable=True)
	extattr= db.Column(db.String(50),nullable=True)
	stateCode= db.Column(db.String(5),nullable=True)
	position= db.Column(db.String(30),nullable=True)
	hiredDate= db.Column(db.TIMESTAMP(True),nullable=True)
	
	def __init__(self,isBoss,isSenior,active,isAdmin,isHide,unionid,openId,remark,userid,isLeaderInDepts,hiredDate,tel,department,workPlace,orderInDepts,mobile,jobnumber,name,extattr,stateCode,position):
		self.isBoss             =isBoss         
		self.isSenior           =isSenior  
		self.active             =active  
		self.isAdmin            =isAdmin  
		self.isHide             =isHide  
		self.unionid            =unionid  
		self.openId             =openId  
		self.remark             =remark
		self.userid             =userid  
		self.isLeaderInDepts    =isLeaderInDepts  
		self.hiredDate          =hiredDate 
		self.tel                =tel 
		self.department         =department  
		self.workPlace          =workPlace  
		self.orderInDepts       =orderInDepts  
		self.mobile             =mobile  
		self.jobnumber          =jobnumber  
		self.name               =name  
		self.extattr            =extattr  
		self.stateCode          =stateCode  
		self.position           =position  
