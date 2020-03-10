from flask import Flask, request, jsonify, send_file, make_response
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_,and_,desc
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from random import randint
from Models import *
from errors import *
from api_config import api_config as cfg
import hashlib
import json, jwt, requests, datetime, time, io,os,sys, zipfile,csv, math,fast,copy,base64
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512

app = Flask(__name__)
CORS(app)
api = Api(app)
db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = cfg['dbc']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 30
ma = Marshmallow(app)
parser = reqparse.RequestParser()

#cache the data
with app.app_context():
	vTeams={}
	vUsers={}
	gCon=fast.dbInit()
	sqlCmd="SELECT id,name,team+0 AS tid,team FROM visitor;"
	allUsers=db.session.execute(sqlCmd)
	for u in allUsers:
		if u.tid and u.tid not in vTeams:
			vTeams[u.tid]=u.team
		vUsers[u.id]=u.name
	#print(vTeams)
	#print(vUsers)
	
# 10进制转6进制，输出字符串。
def i2s(x): 
	output =""
	ret = int(x/6)
	leave = x%6
	if ret == 0:
		return str(leave)
	output = i2s(ret) + str(leave)
	return output
	
# 10进制转骰子码，输出字符串。
def i2m(x): 
	output =""
	ret = int(x/6)
	leave = x%6
	if ret == 0:
		return str(leave if leave!=0 else 6)
	output = i2m(ret) + str(leave if leave!=0 else 6)
	return output

def i2t(x): 
	output =""
	ret = int(x/6)
	leave = x%6
	if ret == 0:
		return str(leave+1)
	output = i2t(ret) + str(leave+1)
	return output
	
class expDpt:
	def __init__(self,id):
		self.id=id
		self.base=Visitor.query.all()
		
	def member(self):
		m=[]
		for i in self.base:
			if i.department_id==self.id:
				m.append(i)
		return m
		
	def leaders(self):
		lds=[]
		uid=7
		for m in self.member():		
			if m.Duty.role<uid:
				lds=[]
				uid=m.Duty.role
				lds.append(m)
		return lds
		
	def suLeaders(self):
		su=Department.query.get(self.id).su_id
		lds=[]
		uid=7
		for i in self.base:
			if i.department_id==su:
				if i.Duty.role<uid:
					lds=[]
					uid=i.Duty.role
					lds.append(i)
		return lds
		
	def count(self):
		return len(self.member())

def appover(id,rid):
	a=Visitor.query.all()
	d=Department.query.get(id)
	lds=[]
	uid=7
	for m in a:
		if m.department_id==d.id:
			if m.Duty.role<uid and m.Duty.role<rid:
				lds=[]
				uid=m.Duty.role
				lds.append(m)
	if len(lds)>0:
		return lds
	elif d.su_id==0:
		return []
	else:
		return appover(d.su_id,rid)

def appover2(did,av,ad,at):
	for v in av:
		for t in at:
			if v.duty_id==t.id and v.department_id==did and t.role<5:
				return v
	for d in ad:
		if d.id==did:
			return appover2(d.su_id,av,ad,at)
	return None
		
def isParentDepartment(child,parent,dpts):
	if child.su_id==0:
		return False
	if child.su_id == parent.id:
		return True
	for dpt in dpts:
		if child.su_id == dpt.id:
			return isParentDepartment(dpt,parent,dpts)
	
def childDepartment(parent):
	child=[]
	dpts=Department.query.all()
	for dp in dpts:
		if isParentDepartment(dp,parent,dpts):
			child.append(dp)
	return child

def pdp(child,dpts,parent):
	#parent=[]
	for dp in dpts:
		if child.su_id == dp.id:
			parent.append(dp)
			pdp(dp,dpts,parent)
	
def parentDepartment(childID):
	parent=[]
	dpts=Department.query.all()
	for dp in dpts:
		if childID==dp.id:
			pdp(dp,dpts,parent)
	#print(parent)
	return parent
	
def authentication(requestor, target=None, department=None):
	# 返回参数 authority，卡洛图 
	# -1 ：参数错误。 
	# 011/2 : 请求员工数据；职务权限通过；部门权限通过。领导请求下级部门某单个员工数据。
	# 010 : 请求员工数据；职务权限通过；部门权限未通过。领导请求上级或其他部门某单个员工数据。
	# 001/2 : 请求员工数据；职务权限未通过；部门权限通过。员工请求下级部门某单个员工数据。
	# 000 : 请求员工数据；职务权限未通过；部门权限未通过。员工请求上级或其他部门某单个员工数据。
	# 111/2 : 请求部门数据；职务权限通过；部门权限通过。领导请求下级部门数据集合。
	# 110 : 请求部门数据；职务权限通过；部门权限未通过。领导请求上级或其他部门数据集合。
	# 101/2 : 请求部门数据；职务权限未通过；部门权限通过。员工请求下级部门数据集合。 
	# 100 : 请求部门数据；职务权限未通过；部门权限未通过。员工请求上级或其他部门数据集合。
	authority = 0
	requestor_department=requestor.Department
	requestor_duty=requestor.Duty
	if target:
		if requestor_duty.role < target.Duty.role:
			authority += 10
		dpts=Department.query.all()
		#print(target.Department.__dict__,'*************************')
		if isParentDepartment(target.Department, requestor_department, dpts):
			return authority + 1
		if target.Department.id==requestor_department.id:
			return authority + 2
	if department:
		if requestor_duty.role < 7:
			authority += 10
		authority += 100
		dpts=Department.query.all()
		if isParentDepartment(department, requestor_department, dpts):
			return authority + 1
		if department.id==requestor_department.id:
			return authority + 2
	#print('**********************************',authority)
	return authority
	
class vResult():
	def __init__(self,vid=None,did=None,tid=None,uid=None,tm=None,had=None):
		self.vid=vid
		self.did=did
		self.tid=tid          
		self.uid=uid
		self.had=had
		
def verify(request):
	rst=vResult(had={'xtoken':None,'vid':None,'uid':None,'did':None,'tid':None})
	xtoken=request.headers.get('xtoken')
	if xtoken and xtoken !='undefined' and xtoken !='null':
		mtoken={}
		try:
			mtoken=jwt.decode(bytes(xtoken, 'utf-8'), cfg['SECRET_KEY'], algorithms=['HS256'],options={'verify_iat': False})			
		except Exception as e:
			print('解码验证信息失败：',e)
			new_token = Token(token=xtoken)
			db.session.add(new_token)
			db.session.commit()
			db.session.refresh(new_token)
			#print(new_token)
			return rst
		if mtoken['iat'] > time.time():
			rst.vid=mtoken['vid']
			rst.did=mtoken['did']
			rst.tid=mtoken['tid']
			rst.uid=mtoken['uid']
			rst.had['xtoken']=xtoken
			rst.had['vid']=mtoken['vid']
			rst.had['uid']=mtoken['uid']
			rst.had['did']=mtoken['did']
			rst.had['tid']=mtoken['tid']
			return rst
		visitor=Visitor.query.get(mtoken['vid'])
		if visitor:
			rst.vid=visitor.id
			rst.had['vid']=visitor.id			
			if visitor.Department and visitor.Duty:
				rst.did=visitor.department_id
				rst.tid=visitor.duty_id
				rst.uid=visitor.Duty.role
				rst.had['uid']=rst.uid
				rst.had['did']=visitor.department_id
				rst.had['tid']=visitor.duty_id
			rst.had['xtoken']=str(jwt.encode({'vid':rst.vid,'did':rst.did, 'tid':rst.tid, 'uid':rst.uid, 'iat': time.time()+1200},cfg['SECRET_KEY'],algorithm='HS256'),'utf-8')
			new_token = Token(token=xtoken,vid=mtoken['vid'],uid=mtoken['uid'],tid=mtoken['tid'],did=mtoken['did'],sts=rst.__dict__)
			db.session.add(new_token)
			db.session.commit()
			db.session.refresh(new_token)
		#print(mtoken['vid'],'   ----------------------------  ',rst.vid)
	else:
		print(request.headers)
	return rst

class tokenSchema(ma.Schema):
	class Meta:
		fields = ('token','nickname','avatar','vid','uid','tid','did','sts','create_at')
token_schema = tokenSchema(strict=True)
tokens_schema = tokenSchema(many=True, strict=True)

class dutySchema(ma.Schema):
    class Meta:
        fields = ('id', 'role','wn_min','wp_min', 'mc_max','wc_max','dc_min','mp_max','mp_min','mn_min','score','lmt','name')
duty_schema = dutySchema(strict=True)
duties_schema = dutySchema(many=True, strict=True)

class duty(Resource):
	def __init__(self):
		self.x=verify(request)

	def get(self, id):
		duty = Duty.query.filter_by(id=id).first()
		return title_schema.jsonify(duty)
		
	def put(self, id):
		parser.add_argument("role")
		parser.add_argument("lmt")
		parser.add_argument("name")
		args = parser.parse_args()
		Duty.query.filter_by(id=id).update({
			"role":args['role'],
			"lmt":args['lmt'],
			"name":args['name']})
		db.session.commit()
		return duty_schema.jsonify(Duty.query.get(id))
		
	def delete(self,id):
		Duty.query.filter_by(id=id).delete()
		db.session.commit()
		return duties_schema.jsonify(Duty.query.all())
		
api.add_resource(duty, '/duty/<int:id>')

class duties(Resource):
	def __init__(self):
		self.x=verify(request)

	def get(self):
		duties = duties_schema.dump(Duty.query.all()).data
		e0.update(self.x.had)
		return jsonify(dict({'lst':duties},**e0))

	def post(self):
		parser.add_argument('role')
		parser.add_argument('lmt')
		parser.add_argument('name')
		args = parser.parse_args()
		new_duty = Duty(role=args['role'],lmt=args['lmt'],name=args['name'])
		db.session.add(new_duty)
		db.session.commit()
		return duties_schema.jsonify(new_duty)
		
api.add_resource(duties, '/duties')

class departmentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'su_id', 'name')
department_schema = departmentSchema(strict=True)
departments_schema = departmentSchema(many=True, strict=True)

class department(Resource):
	def __init__(self):
		self.x=verify(request)

	def get(self, id):
		department = Department.query.filter_by(id=id).first()
		return department_schema.jsonify(department)
		
	def put(self, id):
		parser.add_argument("su_id")
		parser.add_argument("name")
		args = parser.parse_args()
		Department.query.filter_by(id=id).update({
				"su_id":args['su_id'],
				"name":args['name']})
		db.session.commit()
		return department_schema.jsonify(Department.query.get(id))
		
	def delete(self,id):
		Department.query.filter_by(id=id).delete()
		db.session.commit()
		return departments_schema.jsonify(Department.query.all())
		
api.add_resource(department, '/department/<int:id>')

class departments(Resource):
	def __init__(self):
		self.x=verify(request)

	def get(self):
		departments = departments_schema.dump(Department.query.all()).data
		e0.update(self.x.had)
		return jsonify(dict({'lst':departments},**e0))
		
	def post(self):
		parser.add_argument('su_id')
		parser.add_argument('name')
		args = parser.parse_args()
		new_department = Department(su_id=args['su_id'],name=args['name'])
		db.session.add(new_department)
		db.session.commit()
		return departments_schema.jsonify(new_department)
		
api.add_resource(departments, '/departments')

class dpts(Resource):
	def __init__(self):
		self.x=verify(request)

	def get(self):
		if self.x.vid and self.x.did:
			mydp=Department.query.get(self.x.did)
			dps=childDepartment(mydp)
			if self.x.uid<7:
				dps.append(mydp)
			departments = departments_schema.dump(dps).data
			e0.update(self.x.had)
			return jsonify(dict({'lst':departments},**e0))
		return e2		
api.add_resource(dpts, '/dpts')

class ruleSchema(ma.Schema):
	class Meta:
		fields=('id','score','serial','department','duty','inherit','classify','property','units','description','term')
rule_schema=ruleSchema(strict=True)
rules_schema=ruleSchema(many=True,strict=True)

class rule(Resource):
	def __init__(self):
		self.x=verify(request)

	def get(self,id):
		rule = rule_schema.dump(Rule.query.get(id)).data
		e0.update(self.x.had)
		return jsonify(dict(rule,**e0))
		
	def post(self,id=None):
		parser.add_argument('department')
		parser.add_argument('score')
		parser.add_argument('classify')
		parser.add_argument('serial')
		parser.add_argument('property')
		parser.add_argument('description')
		parser.add_argument('term')
		parser.add_argument('units')
		args = parser.parse_args()
		score=None
		duty_id=None
		try:
			score=int( args['score'])				
		except Exception as e:
			return e8

		if self.x.did and self.x.tid:
			#requestor=Visitor.query.filter_by(wx_openid=self.x.oid).first()
			#dpt=Department.query.get(department_id)
			#if authentication(requestor,department=dpt) > 110:
			if self.x.uid==0:
				new_rule = Rule(score=score,
					department=args['department'],
					classify=args['classify'],
					serial=args['serial'],
					property=args['property'],
					description=args['description'],
					units=args['units'],
					term=args['term'])
				id=db.session.add(new_rule)
				db.session.commit()
				db.session.refresh(new_rule)
				new_rule = rule_schema.dump(new_rule).data
				e0.update(self.x.had)
				return jsonify(dict(new_rule,**e0))
		return e2

	def put(self,id):
		parser.add_argument('score')
		parser.add_argument('department')
		parser.add_argument('classify')
		parser.add_argument('serial')
		parser.add_argument('property')
		parser.add_argument('description')
		parser.add_argument('term')
		parser.add_argument('units')
		args = parser.parse_args()
		score=None
		try:
			score=int( args['score'])				
		except Exception as e:
			return e8
		rld=Rule.query.filter_by(id=id)
		rule=rld.first()
		if rule :
			if self.x.uid==0:
				rld.update({"score":score,
					"classify":args['classify'],
					"department":args['department'],
					"serial":args['serial'],
					"property":args['property'],
					"description":args['description'],
					"units":args['units'],
					"term":args['term']})
				db.session.commit()
				rl = rule_schema.dump(Rule.query.get(id)).data
				e0.update(self.x.had)
				return jsonify(dict(rl,**e0))
			return e2
		return e3
		
	def delete(self,id):
		rld=Rule.query.filter_by(id=id)
		rule=rld.first()
		if rule :
			if self.x.did and self.x.tid and self.x.uid==0:
				#requestor=Visitor.query.filter_by(wx_openid=self.x.oid).first()
				rld.delete()
				db.session.commit()
				rules = rules_schema.dump(Rule.query.all()).data
				e0.update(self.x.had)
				return jsonify(dict({'rules':rules},**e0))
			return e2
		return e3
		
api.add_resource(rule,'/rule/<int:id>','/rule')

class rules(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self):
		rules = rules_schema.dump(Rule.query.all()).data
		e0.update(self.x.had)
		return jsonify(dict({'rules':rules},**e0))
		
	def put(self):
		parser.add_argument('rules')
		args = parser.parse_args()
		rules=json.loads(args['rules'])
		if self.x.did and self.x.tid:
			requestor=Visitor.query.filter_by(id=self.x.vid).first()
			rlt=0    #操作成功！
			for rule in rules:
				rld=Rule.query.filter_by(id=rule['id'])
				rl=rld.first()
				if authentication(requestor,department=rl.Department) > 110 or rl.Department is None:
					iii=rld.update({
						"department_id":rule['department_id'],
						"duty_id":rule['duty_id'],
						"description":rule['description'],
						"inherit":rule['inherit'],
						"classify":rule['classify'],
						"property":rule['property'],
						"score":rule['score'],
						"units":rule['units']})
					#print('MMMMMMMMMMMMMMMMMMMMMMMMM',iii)
				else:
					rlt+=1
			db.session.commit()
			rls = rules_schema.dump(Rule.query.all()).data
			if rlt==0:
				e0.update(self.x.had)
				return jsonify(dict({'rules':rls},**e0))
			e5.update(self.x.had)
			return jsonify(dict({'rules':rls},**e5))
		return e2
api.add_resource(rules,'/rules')

class proposeSchema(ma.Schema):
	class Meta:
		fields=('id','proposer_id','beneficiary_id','approver_id','refer_id','score','classify','refer','state','description','commit','appeal','appl','update_at','create_at')
propose_schema=proposeSchema(strict=True)
proposes_schema=proposeSchema(many=True,strict=True)

class propose(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self,id=None):
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:
			if id:
				propose=Propose.query.get(id)
				ppse= propose_schema.dump(propose).data
				e0.update(self.x.had)
				return jsonify(dict({'ppse':ppse},**e0))

			approver=Visitor.query.get(self.x.vid)
			ppse={'refer':'R','description':'','score':None,'classify':'','beneficiary_id':self.x.vid,'refer_id':None}		
			rls=[]
			#if self.x.uid<6:
			#	rls=Rule.query.all()
			#else:
			#	did=parentDepartment(self.x.did)
			#	if len(did):
			#		did=str([d.id for d in did]).replace('[','(').replace(']',')')
			#		sql="select * from rule WHERE (department_id in %s and inherit='True') OR department_id=%s;"
			#		rs=db.session.execute(sql%(did,self.x.did))
			#		for r in rs:
			#			rls.append(r)
			#	sql="select * from rule WHERE department_id=%s"
			#	rms=db.session.execute(sql%self.x.did)
			#	for ri in rms:
			#		rls.append(ri)
			rls=Rule.query.all()
			rls=rules_schema.dump(rls).data
			
			fls=[]
			follows=Visitor.query.all()
			if self.x.uid<6:				
				for fl in follows:
					if fl.Duty:
						if fl.Duty.role>self.x.uid or fl.id==self.x.vid:
							fls.append(fl)
							
			elif self.x.uid>5 and self.x.uid <7:
				mydp=Department.query.get(self.x.did)
				dps=childDepartment(mydp)
				for fl in follows:
					if fl.department_id in [dp.id for dp in dps] or fl.id==self.x.vid:
						fls.append(fl)
			else:				
				for fl in follows:
					if fl.id==self.x.vid:						
						fls.append(fl)
						
			fs=[{'id':fl.id,'name':fl.name,'department_id':fl.department_id,'team':fl.team,'duty_id':fl.duty_id} for fl in fls]
			
			dts=duties_schema.dump(Duty.query.all()).data
			e0.update(self.x.had)
			return jsonify(dict({'ppse':ppse,'rls':rls, 'fls':fs,'dts':dts},**e0))
		return e2
		
	def post(self,id=None):
		if self.x.vid and self.x.did and self.x.tid and self.x.uid is not None:
			parser.add_argument('beneficiary_id')
			parser.add_argument('refer_id')
			parser.add_argument('refer')
			parser.add_argument('score')
			parser.add_argument('classify')
			parser.add_argument('description')
			args = parser.parse_args()
			beneficiary_id=None
			refer_id=None
			score=None
			classify=None
			if (args['refer_id'] and args['score']) or (not args['refer_id'] and not args['score']):
				#print('---------------------------------------------------------------',args)
				return e19
			try:
				beneficiary_id=int(args['beneficiary_id'])			
			except Exception as e:
				return e8
			if args['score'] and args['classify'] in ['A+','B+','C+','A-','B-','C-']:
				try:
					if int(args['score'])>0 and args['refer']=='C':
						score=int(args['score'])
						classify=args['classify']
					else:
						raise e8
				except Exception as e:
					return e8
			if args['refer_id']:
				try:
					if int(args['refer_id'])>0 and args['refer']=='R':
						refer_id=int(args['refer_id'])
						rl=Rule.query.get(refer_id)
						score=rl.score
						classify=rl.classify
					else:
						#print(e)
						raise e8
				except Exception as e:
					#print(e)
					return e8			
			t=Visitor.query.get(int(args['beneficiary_id']))
			m=Visitor.query.get(self.x.vid)
			apv=0
			if self.x.uid==0:
				apv=self.x.vid
			else:
				Lds=appover(self.x.did,self.x.uid)
				if len(Lds)==0:
					return e21
				apv=Lds[0].id
			if (self.x.vid==int(args['beneficiary_id'])) or (self.x.uid==6 and t.department_id==self.x.did and t.Duty.role>m.Duty.role) or (self.x.uid<6 and t.Duty.role>m.Duty.role):
				new_propose = Propose(
					proposer_id=self.x.vid,
					approver_id=apv,
					beneficiary_id=beneficiary_id,
					refer=args['refer'],
					refer_id=refer_id,
					score=score,
					state='提交成功',
					classify=classify,
					description=args['description'])
				db.session.add(new_propose)
				db.session.commit()
				db.session.refresh(new_propose)
				new_propose = propose_schema.dump(new_propose).data
				e0.update(self.x.had)
				return jsonify(dict({'ppse':new_propose},**e0))
		return e2
		
	def put(self,id=None):
		parser.add_argument('proposer_id')
		parser.add_argument('beneficiary_id')
		parser.add_argument('approver_id')
		parser.add_argument('rule_id')
		parser.add_argument('state')
		parser.add_argument('create_at')
		args = parser.parse_args()
		Propose.query.filter_by(id=id).update({
			"proposer_id":args['proposer_id'],
			"beneficiary_id":args['beneficiary_id'],
			"approver_id":args['approver_id'],
			"rule_id":args['rule_id'],
			"state":args['state'],
			"create_at":args['create_at']})
					
		db.session.commit()
		return propose_schema.jsonify(Propose.query.get(id))
		
	def delete(self,id=None):
		if self.x.tid and self.x.did:
			pos=Propose.query.filter_by(id=id)
			po=pos.first()
			if po.proposer_id==self.x.vid and po.state=='提交成功':
				pos.delete()
				db.session.commit()
				sql='''select id,description,refer-1 AS refer, refer_id, score, classify, state, commit,create_at from propose where proposer_id=%s ORDER BY create_at desc limit 15; '''
				lss=db.session.execute(sql%self.x.vid)
				my=[{'id':ls.id,'des':ls.description,'refer':ls.refer,'rid':ls.refer_id,'score':ls.score,'classify':ls.classify,'state':ls.state,'cmt':ls.commit,'ts':str(ls.create_at)} for ls in lss]			
				e0.update(self.x.had)
				return jsonify(dict({'my':my},**e0))
			return e27
		return e2
		
api.add_resource(propose,'/propose/<int:id>','/propose')

class ppv(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self,id):
		if self.x.vid:
			sql='''SELECT p.id,p.proposer_id,p.approver_id,p.beneficiary_id,p.refer_id,p.score,p.classify,p.refer-1 as rf,p.state+0 as state,p.description,p.`commit`,p.create_at,
				vp.NAME AS pps,va.name AS apv,vb.NAME AS bnf, r.description as rls
				FROM propose AS p 
				LEFT JOIN visitor AS vp ON p.proposer_id=vp.id 
				LEFT JOIN visitor AS va ON p.approver_id=va.id
				LEFT JOIN visitor AS vb ON p.beneficiary_id=vb.id
				LEFT JOIN rule AS r ON p.refer_id=r.id
				WHERE p.id=%s;'''
			lss=db.session.execute(sql%id)
			ppo=[{'id':p.id,'proposer_id':p.proposer_id,'approver_id':p.approver_id,'beneficiary_id':p.beneficiary_id,
				'rid':p.refer_id,'sc':p.score,'cls':p.classify,'rf':p.rf, 'state':p.state,'desc':p.description,'cmt':p.commit,'ts':str(p.create_at),
				'pps':p.pps,'apv':p.apv,'bnf':p.bnf,'rls':p.rls} for p in lss]
					
			e0.update(self.x.had)
			return jsonify(dict({'ppo':ppo[0]},**e0))
		return e2		
api.add_resource(ppv,'/ppv/<int:id>')

def scSum(lst):
	aa=0
	bb=0
	cc=0
	aj=0
	bj=0
	cj=0
	for ls in lst:
		if ls['classify']=='A+':
			aa+=ls['score']
		if ls['classify']=='B+':
			bb+=ls['score']
		if ls['classify']=='C+':
			cc+=ls['score']
		if ls['classify']=='A-':
			aj+=ls['score']
		if ls['classify']=='B-':
			bj+=ls['score']
		if ls['classify']=='C-':
			cj+=ls['score']
	return {'A+':aa,'B+':bb,'C+':cc,'A-':aj,'B-':bj,'C-':cj}
	
class proposes(Resource):
	def __init__(self):
		self.x=verify(request)

	def get(self):
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:
			db.session.execute('''update propose set bNew=0 WHERE beneficiary_id=%s and bNew=1;'''%self.x.vid)
			db.session.commit()			
			sql='''SELECT p.id,p.description,vp.NAME AS pps,va.NAME AS apv,p.refer-1 AS refer, p.refer_id, p.score, p.classify, 
				p.create_at, p.appeal, p.appl, p.commit from propose AS p 
				LEFT JOIN visitor AS vp ON vp.id=p.proposer_id
				LEFT JOIN visitor AS va ON va.id=p.approver_id
				where p.state='通过审核' and p.beneficiary_id=%s ORDER BY p.update_at DESC; '''
			lss=db.session.execute(sql%self.x.vid)
			lst=[{'id':ls.id,'des':ls.description,'pps':ls.pps,'apv':ls.apv,'refer':ls.refer,'rid':ls.refer_id,'score':ls.score,'classify':ls.classify,'ts':str(ls.create_at), 'appeal':ls.appeal,'appl':ls.appl,'cm':ls.commit} for ls in lss]
						
			sql='''SELECT p.id,vt.NAME AS nm, p.description,p.refer-1 AS refer, p.refer_id, p.score, p.classify, p.state, p.commit, p.create_at,p.appl 
						FROM propose AS p LEFT JOIN visitor AS vt ON p.beneficiary_id=vt.id
						where proposer_id=%s ORDER BY create_at desc limit 300; '''
						
			lss=db.session.execute(sql%self.x.vid)
			my=[{'id':ls.id,'nm':ls.nm,'des':ls.description,'refer':ls.refer,'rid':ls.refer_id,'score':ls.score,'classify':ls.classify,'state':ls.state,'cmt':ls.commit,'ts':str(ls.create_at),'ap':ls.appl} for ls in lss]
			dpts=departments_schema.dump(Department.query.all()).data
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst,'my':my, 'dpts':dpts,'score':scSum(lst)},**e0))
		return e2
		
	def post(self):
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:
			parser.add_argument('id')
			parser.add_argument('rewards')
			args = parser.parse_args()			
			rewards=json.loads(args['rewards'])
			tk=Task.query.filter_by(id=args['id'])
			task=tk.first()
			if self.x.vid==task.approver_id:
				if len(rewards)<=task.menber and task.state<4:
					tsc=0
					for rw in rewards:						
						new_propose = Propose(proposer_id=self.x.vid,
							beneficiary_id=rw['id'],
							approver_id=None,
							refer_id=args['id'],
							refer='T',
							state='通过审核',
							classify=task.score_type,
							description="完成任务："+task.description,
							score=rw['score'])
						db.session.add(new_propose)
						tsc+=rw['score']
					if tsc==task.score:
						tk.update({'state':4})
						db.session.commit()
						e0.update(self.x.had)
						return jsonify(dict(self.x.had,**e0))
					return e17
				return e1
		return e2
		
	def put(self):
		if self.x.did and self.x.tid and self.x.vid:
			parser.add_argument('from')
			parser.add_argument('to')
			args = parser.parse_args()
			sql='''select P.id,P.description,V.name, A.name as apv, P.refer-1 AS refer, P.refer_id, P.score, P.classify, P.create_at from propose as P
			left join visitor as V on V.id=P.proposer_id left join visitor as A on A.id=P.approver_id
			WHERE P.state='通过审核' and P.beneficiary_id=%s AND P.create_at BETWEEN '%s' and '%s' ORDER BY P.create_at desc;'''			
			lss=db.session.execute(sql%(self.x.vid,args['from'],args['to']+' 23:59:59'))
			lst=[{'id':ls.id,'des':ls.description, 'pps':ls.name, 'apv':ls.apv, 'refer':ls.refer,'rid':ls.refer_id,'score':ls.score,'classify':ls.classify,'ts':str(ls.create_at)} for ls in lss]
			
			sql='''SELECT p.id,vt.NAME AS nm, p.description,p.refer-1 AS refer, p.refer_id, p.score, p.classify, p.state, p.commit, p.create_at, p.appl
				FROM propose AS p LEFT JOIN visitor AS vt ON p.beneficiary_id=vt.id
				where proposer_id=%s AND create_at BETWEEN '%s' and '%s' ORDER BY create_at desc;'''
						
			lss=db.session.execute(sql%(self.x.vid,args['from'],args['to']+' 23:59:59'))
			my=[{'id':ls.id,'nm':ls.nm,'des':ls.description,'refer':ls.refer,'rid':ls.refer_id,'score':ls.score,'classify':ls.classify,'state':ls.state,'cmt':ls.commit,'ts':str(ls.create_at), 'ap':ls.appl} for ls in lss]
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst,'my':my,'score':scSum(lst)},**e0))
		return e2		
api.add_resource(proposes,'/proposes')


class appeal(Resource):
	def __init__(self):
		self.x=verify(request)
	
	def get(self,aid=None):
		if self.x.vid==333 or self.x.vid==38 or self.x.vid==293 or self.x.vid==296:
			#vid=333 if self.x.vid==38 or self.x.vid==293 or self.x.vid==296 else self.x.vid
			sql='''SELECT p.id, vp.name AS  nm, vb.name AS tg, vp.id AS nid, vb.id AS tid, p.refer_id AS rid, r.serial,r.id as rlid,
						p.create_at AS ts, p.refer-1 AS refer, CONCAT(p.classify,p.score) AS sc, p.description AS `desc`,
						p.appeal as ap from propose as p 
						left join visitor as vp ON p.proposer_id=vp.id
						left JOIN visitor AS vb ON p.beneficiary_id=vb.id 
						left JOIN rule AS r ON p.refer_id=r.id
						WHERE appl=1 ORDER BY p.create_at; '''						
			rt=db.session.execute(sql)
			lst=[]
			for r in rt:
				lst.append({'id':r.id,'nm':r.nm,'tg':r.tg,'nid':r.nid,'tid':r.tid,'rid':r.rid,'ts':str(r.ts),'refer':r.refer,'sc':r.sc,'desc':r.desc,'ap':r.ap,'ss':r.serial,'rlid':r.rlid})			
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst},**e0))
		return e2
		
	def put(self,aid=None):
		if self.x.did and self.x.tid and self.x.vid:
			parser.add_argument('appl')
			args = parser.parse_args()

			pps=Propose.query.filter_by(id=aid)
			if pps.first().beneficiary_id==self.x.vid:
				if pps.first().proposer_id==self.x.vid or pps.first().beneficiary_id==self.x.vid:
					pps.update({'appl':1 ,'appeal':args['appl']})
					db.session.commit()
					sql='''select id,description,proposer_id,approver_id,refer-1 AS refer, refer_id, score, classify, create_at, appeal, appl from propose where state='通过审核' and beneficiary_id=%s ORDER BY update_at desc limit 260;'''
					lss=db.session.execute(sql%self.x.vid)
					lst=[{'id':ls.id,'des':ls.description,'pps':ls.proposer_id,'apv':ls.approver_id,'refer':ls.refer,'rid':ls.refer_id,'score':ls.score,'classify':ls.classify,'ts':str(ls.create_at), 'appeal':ls.appeal, 'appl':ls.appl} for ls in lss]
					sql='''SELECT p.id,vt.NAME AS nm, p.description,p.refer-1 AS refer, p.refer_id, p.score, p.classify, p.state, p.commit, p.create_at, p.appl
						FROM propose AS p LEFT JOIN visitor AS vt ON p.beneficiary_id=vt.id
						where proposer_id=%s ORDER BY create_at desc limit 300; '''
					lss=db.session.execute(sql%self.x.vid)
					my=[{'id':ls.id,'nm':ls.nm,'des':ls.description,'refer':ls.refer,'rid':ls.refer_id,'score':ls.score,'classify':ls.classify,'state':ls.state,'cmt':ls.commit,'ts':str(ls.create_at), 'ap':ls.appl} for ls in lss]
					e0.update(self.x.had)
					return jsonify(dict({'lst':lst,'my':my},**e0))
			return e3
		return e2
		
	def post(self,aid=None):
		if self.x.did and self.x.tid and self.x.uid==0:
			parser.add_argument('opt')
			parser.add_argument('commit')
			parser.add_argument('psd')
			args = parser.parse_args()
			psd=json.loads(args['psd'])
			if args['opt']=='pass':
				for id in psd:
					pps=Propose.query.filter_by(id=id)
					if pps.first().id:
						sts='未通过审核' 
						if pps.first().state=='未通过审核':
							sts='通过审核'
						pps.update({'appl':2 ,'state':sts})
				db.session.commit()
				sql='''SELECT p.id, vp.name AS  nm, vb.name AS tg, vp.id AS nid, vb.id AS tid, p.refer_id AS rid, r.serial,r.id as rlid,
					p.create_at AS ts, p.refer-1 AS refer, CONCAT(p.classify,p.score) AS sc, p.description AS `desc`,
					p.appeal as ap from propose as p 
					LEFT join visitor as vp ON p.proposer_id=vp.id
					LEFT JOIN visitor AS vb ON p.beneficiary_id=vb.id 
					LEFT JOIN rule AS r ON p.refer_id=r.id
					WHERE appl=1 ORDER BY p.create_at; '''					
				rt=db.session.execute(sql)
				lst=[]
				for r in rt:
					lst.append({'id':r.id,'nm':r.nm,'tg':r.tg,'nid':r.nid,'tid':r.tid,'rid':r.rid,'ts':str(r.ts),'refer':r.refer,'sc':r.sc,'desc':r.desc,'ap':r.ap,'ss':r.serial,'rlid':r.rlid})
				e0.update(self.x.had)
				return jsonify(dict({'lst':lst},**e0))
			
			if args['opt']=='reject':
				for id in psd:
					pps=Propose.query.filter_by(id=id)
					if pps.first().id:
						pps.update({'appl':3, 'commit':args['commit']})
				db.session.commit()
				sql='''SELECT p.id, vp.name AS  nm, vb.name AS tg, vp.id AS nid, vb.id AS tid, p.refer_id AS rid, r.serial,r.id as rlid,
					p.create_at AS ts, p.refer-1 AS refer, CONCAT(p.classify,p.score) AS sc, p.description AS `desc`,
					p.appeal as ap from propose as p 
					LEFT join visitor as vp ON p.proposer_id=vp.id
					LEFT JOIN visitor AS vb ON p.beneficiary_id=vb.id 
					LEFT JOIN rule AS r ON p.refer_id=r.id
					WHERE appl=1 ORDER BY p.create_at; '''						
				rt=db.session.execute(sql)
				lst=[]
				for r in rt:
					lst.append({'id':r.id,'nm':r.nm,'tg':r.tg,'nid':r.nid,'tid':r.tid,'rid':r.rid,'ts':str(r.ts),'refer':r.refer,'sc':r.sc,'desc':r.desc,'ap':r.ap,'ss':r.serial,'rlid':r.rlid})
				e0.update(self.x.had)
				return jsonify(dict({'lst':lst},**e0))
			return e3
		return e2		
api.add_resource(appeal, '/appeal','/appeal/<int:aid>')

class pursue(Resource):
	def __init__(self):
		self.x=verify(request)

	def get(self):
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:
			sql='''select id,classify,score,department,property,description,serial from rule;'''
			rls=db.session.execute(sql)
			lst=[]
			for r in rls:
				if r.department==None or r.department=='':
					lst.append((r.id,r.classify,r.score,'P',r.property,r.description,r.department,r.serial))
				else:
					lst.append((r.id,r.classify,r.score,'S',r.property,r.description,r.department,r.serial))
			dpt=Department.query.get(self.x.did)
			av=Visitor.query.all()
			ad=Duty.query.all()
			fls=[]
			for v in av:
				if self.x.uid==7 and v.id ==self.x.vid:
					fls.append((v.id,v.name))
					break
				if self.x.uid==6 and v.department_id==self.x.did:
					fls.append((v.id,v.name))
					continue
				if self.x.uid==0 and v.duty_id !=1:
					fls.append((v.id,v.name))
					continue
				if self.x.uid>0 and self.x.uid<6:
					for d in ad:
						if v.duty_id==d.id and self.x.uid<=d.role:
							fls.append((v.id,v.name))
							continue
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst,'fls':fls},**e0))
		return e2
		
	def post(self):
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:
			parser.add_argument('tgt')
			parser.add_argument('rid')
			parser.add_argument('classify')
			parser.add_argument('refer')
			parser.add_argument('description')
			parser.add_argument('score')
			parser.add_argument('month')
			args = parser.parse_args()
			pid=self.x.vid						
			if args['refer'] not in ['C','R','F']:
				return e8
				
			if args['refer']=='R':
				args['rid']=int(args['rid'])
			else:
				args['rid']='NULL'
			if args['classify'] not in ['B+','B-','C+','C-']:
				return e8
			if (args['classify']=='C+' or args['classify']=='C-') and self.x.uid!=0:
				return e2
			try:
				args['score']=int(args['score'])
			except Exception as e:
				return e17
			state=''
			try:
				args['month']=int(args['month'])
				if args['month']<0 or args['month']>=datetime.datetime.now().month:
					return e38
				if args['month']==0:
					args['month']=datetime.datetime.now()
				elif args['month']==10:
					args['month']=str(datetime.datetime.now().year)+'-10-29 01:01:01'
					state='通过审核'
				elif args['month']==11:
					args['month']=str(datetime.datetime.now().year)+'-11-29 01:01:01'
					state='通过审核'
				else:
					args['month']=str(datetime.datetime.now().year)+'-0'+str(args['month'])+'-29 01:01:01'
					state='通过审核'
			except Exception as e:
				return e17
			me=Duty.query.get(self.x.tid)
			if args['score'] > me.lmt and self.x.uid<7 and args['refer'] in ['C','F']:
				return {'error':27,'msg':'奖扣积分超额，请提交 %s 以内的奖扣分操作！'%me.lmt}				
			sql='''SELECT v.id,v.name,v.department_id AS dpt,v.duty_id,T.role FROM 
				visitor AS V LEFT JOIN duty AS T ON T.id=V.duty_id
				WHERE v.auth=1 and T.role is not null;'''
			fs=db.session.execute(sql)			
			fls=[]
			for v in fs:
				if v.id ==self.x.vid:
					fls.append((v.id,v.name))
					if self.x.uid==7:
						break						
				if self.x.uid==6 and v.dpt==self.x.did:
					fls.append((v.id,v.name))
					continue					
				if self.x.uid==0 and v.duty_id !=1:
					fls.append((v.id,v.name))
					continue					
				if self.x.uid <= v.role and self.x.uid<6:
					fls.append((v.id,v.name))
					continue					
			succeed=[]
			failed=[]
			tgt=[]			
			for t in args["tgt"].split(" "):
				if len(t)>1:
					tgt.append(t)
			for t in tgt:
				bfd=False
				for f in fls:
					if t==f[1]:
						if f[0]==self.x.vid and args['refer'] in ['C','F']:  #管理权限无法奖扣个人   2019.6.15
							failed.append(t)
							break
						succeed.append(f[0])
						bfd=True
						break
				if not bfd:
					failed.append(t)
			if len(succeed)>0:
				apv=333
				if state=='':
					state='提交成功' #if self.x.uid>0 else '通过审核'
				#if self.x.uid==0:
				#	apv=self.x.vid
				#av=Visitor.query.all()
				#at=Duty.query.all()
				#apv=self.x.vid
				#if self.x.uid>0:
				#	if self.x.uid<6:
				#		apv=333
				#	else:
				#		ad=Department.query.all()
				#		Lds=appover2(self.x.did,av,ad,at)
				#		if Lds==None:
				#			return e21
				#		apv=Lds.id				
				sql=''
				sq='insert into propose(proposer_id,approver_id,beneficiary_id,refer_id,score,classify,refer,state,description,create_at) VALUES'
				for sc in succeed:
					desc=args['description'].replace('"','“').replace("'","‘")
					if sc==self.x.vid and args['classify']=="B-":
						sql +='''(%s,%s,%s,%s,%s,"%s","%s","%s","%s","%s"),'''%(pid, apv, sc, args['rid'], round(args['score']/2), args['classify'], args['refer'], state, desc, args['month'])
					else:
						sql +='''(%s,%s,%s,%s,%s,"%s","%s","%s","%s","%s"),'''%(pid, apv, sc, args['rid'], args['score'], args['classify'], args['refer'], state, desc, args['month'])						
				sql=sq+sql[0:-1]
				db.session.execute(sql)
				db.session.commit()
				if len(failed)>0:
					return jsonify(dict({'error':26,'msg':'%s 未找到，或不在奖扣权限内！%s 奖扣成功。' % (failed, succeed)},**self.x.had))
				e0.update(self.x.had)
				return e0
			return {'error':26,'msg':'%s 未找到，或不在奖扣权限内！'%failed}
		return e2		
api.add_resource(pursue,'/pursue')	

class apl(Resource):
	def __init__(self):
		self.x=verify(request)
		
api.add_resource(apl,'/apl')
	
class approval(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self,id=None):
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:
			state=None
			if id=='1':
				state='提交成功'
			elif id=='2':
				state='通过审核'
			elif id=='3':
				state='未通过审核'
			else:
				return e1		
			#idt=2 if datetime.datetime.now().weekday()==0 or datetime.datetime.now().weekday()==1 else 2
			idt=48
			vid= 333 if self.x.vid==38 or self.x.vid==293 or self.x.vid==296 else self.x.vid
			sql='''SELECT p.id, vp.name AS  nm, vb.name AS tg, vp.id AS nid, vb.id AS tid, p.refer_id AS rid, r.serial,r.id as rlid,
					p.create_at AS ts, p.refer-1 AS refer, CONCAT(p.classify,p.score) AS sc, p.description AS `desc`, vb.department_id as did,
					p.commit as cm from propose as p 
					inner join visitor as vp ON p.proposer_id=vp.id
					INNER JOIN visitor AS vb ON p.beneficiary_id=vb.id 
					LEFT JOIN rule AS r ON p.refer_id=r.id
					WHERE p.approver_id=%s AND p.state='%s' and p.create_at >= curdate() - INTERVAL '''+str(idt)+''' day ORDER BY p.create_at desc;'''					
			#WHERE p.approver_id=%s AND p.state='%s' and p.create_at >= curdate() - INTERVAL '''+str(idt)+''' day ORDER BY p.create_at;'''	
			rt=db.session.execute(sql%(vid,state))
			#print(sql%(vid,state),'=====================')
			lst=[]
			for r in rt:
				lst.append({'id':r.id,'nm':r.nm,'tg':r.tg,'nid':r.nid,'tid':r.tid,'rid':r.rid,'ts':str(r.ts),'refer':r.refer,'sc':r.sc,'desc':r.desc,'cm':r.cm,'ss':r.serial,'rlid':r.rlid,'did':r.did})
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst},**e0))
		return e2

	def post(self,id=None):
		if self.x.uid==0 and self.x.vid:
			parser.add_argument('psd')
			args = parser.parse_args()
			psd=json.loads(args['psd'])
			for uid in psd:
				tp=Propose.query.filter_by(id=uid)
				if tp.first():
					if tp.first().approver_id==self.x.vid:
						tp.update({'state':'通过审核'})
			db.session.commit()

			#idt=2 if datetime.datetime.now().weekday()==0 or datetime.datetime.now().weekday()==1 else 2
			idt=48
			sql='''SELECT p.id, vp.name AS  nm, vb.name AS tg, vp.id AS nid, vb.id AS tid, p.refer_id AS rid, r.serial,r.id as rlid,
				p.create_at AS ts, p.refer-1 AS refer, CONCAT(p.classify,p.score) AS sc, p.description AS `desc`,
				p.commit as cm from propose as p 
				inner join visitor as vp ON p.proposer_id=vp.id
				INNER JOIN visitor AS vb ON p.beneficiary_id=vb.id 
				LEFT JOIN rule AS r ON p.refer_id=r.id
				WHERE p.approver_id=%s AND p.state='提交成功' and p.create_at >= curdate() - INTERVAL '''+str(idt)+''' day ORDER BY p.create_at desc;'''
			rt=db.session.execute(sql%(self.x.vid))
			lst=[]
			for r in rt:
				lst.append({'id':r.id,'nm':r.nm,'tg':r.tg,'nid':r.nid,'tid':r.tid,'rid':r.rid,'ts':str(r.ts),'refer':r.refer,'sc':r.sc,'desc':r.desc,'cm':r.cm,'ss':r.serial,'rlid':r.rlid})
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst},**e0))
		return e2
		
	def put(self,id=None):
		if self.x.uid==0 and self.x.vid:
			parser.add_argument('psd')
			parser.add_argument('commit')
			args = parser.parse_args()
			psd=json.loads(args['psd'])
			for id in psd:
				tp=Propose.query.filter_by(id=id)
				if tp.first():
					if tp.first().approver_id==self.x.vid:
						tp.update({'state':'未通过审核','commit':args['commit']})
			db.session.commit()	
			#idt=2 if datetime.datetime.now().weekday()==0 or datetime.datetime.now().weekday()==1 else 2
			idt=48
			sql='''SELECT p.id, vp.name AS  nm, vb.name AS tg, vp.id AS nid, vb.id AS tid, p.refer_id AS rid, r.serial,r.id as rlid,
				p.create_at AS ts, p.refer-1 AS refer, CONCAT(p.classify,p.score) AS sc, p.description AS `desc`,
				p.commit as cm from propose as p 
				inner join visitor as vp ON p.proposer_id=vp.id
				INNER JOIN visitor AS vb ON p.beneficiary_id=vb.id 
				LEFT JOIN rule AS r ON p.refer_id=r.id
				WHERE p.approver_id=%s AND p.state='提交成功' and p.create_at >= curdate() - INTERVAL '''+str(idt)+''' day ORDER BY p.create_at desc;'''
			rt=db.session.execute(sql%(self.x.vid))
			lst=[]
			for r in rt:
				lst.append({'id':r.id,'nm':r.nm,'tg':r.tg,'nid':r.nid,'tid':r.tid,'rid':r.rid,'ts':str(r.ts),'refer':r.refer,'sc':r.sc,'desc':r.desc,'cm':r.cm,'ss':r.serial,'rlid':r.rlid})
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst},**e0))
		return e2
		
	def delete(self,id=None):
		if self.x.vid:
			tp=Propose.query.filter_by(id=id)
			if tp.first():
				if tp.first().approver_id==self.x.vid:
					state=tp.first().state
					tp.update({'state':'提交成功'})
					db.session.commit()
					#idt=2 if datetime.datetime.now().weekday()==0 or datetime.datetime.now().weekday()==1 else 2
					idt=48
					sql='''SELECT p.id, vp.name AS  nm, vb.name AS tg, vp.id AS nid, vb.id AS tid, p.refer_id AS rid, r.serial,r.id as rlid,
						p.create_at AS ts, p.refer-1 AS refer, CONCAT(p.classify,p.score) AS sc, p.description AS `desc`,
						p.commit as cm from propose as p 
						inner join visitor as vp ON p.proposer_id=vp.id
						INNER JOIN visitor AS vb ON p.beneficiary_id=vb.id 
						LEFT JOIN rule AS r ON p.refer_id=r.id
						WHERE p.approver_id=%s AND p.state='%s' and p.create_at >= curdate() - INTERVAL '''+str(idt)+''' day ORDER BY p.create_at desc;'''					
					rt=db.session.execute(sql%(self.x.vid, state))
					lst=[]
					for r in rt:
						lst.append({'id':r.id,'nm':r.nm,'tg':r.tg,'nid':r.nid,'tid':r.tid,'rid':r.rid,'ts':str(r.ts),'refer':r.refer,'sc':r.sc,'desc':r.desc,'cm':r.cm,'ss':r.serial,'rlid':r.rlid})
					e0.update(self.x.had)
					return jsonify(dict({'lst':lst},**e0))
		return e2		
api.add_resource(approval,'/approval', '/approval/<id>')

# class apv(Resource):
# 	def __init__(self):
# 		self.x=verify(request)
# 		
# 	def get(self,id):
# 		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:
# 			sql='''select * from propose where approver_id=%s and state='提交成功' and refer in ('R','C'); '''
# 			rts=db.session.execute(sql%self.x.vid)			
# 			vts=Visitor.query.all()
# 			rls=Rule.query.all()
# 			lst=[]			
# 			for r in rts:
# 				proposer=""
# 				beneficiary=""
# 				for v in vts:
# 					if r.proposer_id==v.id:
# 						
# 					if r.beneficiary_id == v.id:
# 						
# 				if r.refer=='R':		
# 					for s in rls:
# 						if r.refer_id==s.id:
# 				lst.append((r.id,))			
# 			e0.update(self.x.had)
# 			return jsonify(dict({'lst':lst},**e0))
# 		return e2
# 				
# api.add_resource(apv,'/apv')

class visitor_taskSchema(ma.Schema):
	class Meta:
		fields=('id','task_id','target_visitor','target_department','accept_id','update_at','create_at')
vt_schema=visitor_taskSchema(strict=True)
vts_schema=visitor_taskSchema(many=True,strict=True)

class vTask(Resource):
	def __init__(self):
		self.x=verify(request)
	def put(self,id):	
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:			
			sql='''SELECT id FROM `visitor_task` where task_id=%s and accept_id is not null;'''
			vas=db.session.execute(sql%id)
			if vas is None:
				sql='''delete FROM `visitor_task` where task_id=%s;'''
				db.session.execute(sql%id)
				db.session.commit()				 
				parser.add_argument('tgp')
				parser.add_argument('tgd')
				args = parser.parse_args()
				tgp=json.loads(args['tgp'])
				tgd=json.loads(args['tgd'])
				vls=[]
				for p in tgp:
					for d in tgd:
						dw='NULL'
						pw='NULL'
						if p is not None:
							pw=p
							if d is not None:
								dw=d
								vls.append((id,pw,dw))
				vls=str(vls)[1:-1]
				sql='''INSERT INTO `visitor_task` (`task_id`, `target_visitor`, `target_department`) VALUES %s;'''
				db.session.execute(sql%vls)
				db.session.commit()	
				
				me=Department.query.get(self.x.did)
				mydpt=childDepartment(me)
				if self.x.uid<7:
					mydpt.append(me)
					
				all=Visitor.query.all()
				fls=[]
				for dpt in mydpt:
					for pp in all:
						if pp.department_id==dpt.id:
							if pp.id in ppl:
								fls.append({'id':pp.id,'name':pp.name,'department':dpt.name,'avatar':pp.wx_headimgurl,'checked':True})
							else:
								fls.append({'id':pp.id,'name':pp.name,'department':dpt.name,'avatar':pp.wx_headimgurl,'checked':False})
								
				dpts=[]
				for dp in mydpt:
					if dp.id in dpl:
						dpts.append({'id':dp.id,'name':dp.name,'checked':True})
					else:
						dpts.append({'id':dp.id,'name':dp.name,'checked':False})
						
				target={'fls':fls,'dpts':dpts}
				e0.update(self.x.had)
				return jsonify(dict({'target':target},**e0))
			return e6
		return e2
api.add_resource(vTask,'/vtask/<id>')

class taskSchema(ma.Schema):
    class Meta:
        fields=('id','creator_id','approver_id','menber','score','score_type','state','description','pub_at','expiry_at','update_at','create_at')
task_schema=taskSchema(strict=True)
tasks_schema=taskSchema(many=True,strict=True)

class task(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self,id=None):
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid: 
			if id==0:
				me=visitor_schema.dump(Visitor.query.get(self.x.vid)).data
				myd=Department.query.get(self.x.did)
				mydpt=childDepartment(myd)
				if self.x.uid<7:
					mydpt.append(myd)
				dpts=[{'id':dp.id,'name':dp.name,'checked':False} for dp in mydpt]
				all=Visitor.query.all()
				fls=[]
				for dpt in mydpt:
					for pp in all:
						if pp.department_id==dpt.id:
							fls.append({'id':pp.id,'name':pp.name,'department':dpt.name,'avatar':pp.wx_headimgurl,'checked':False})

				target={"dpts":dpts,"fls": fls}
				e0.update(self.x.had)
				return jsonify(dict({'task':{},'accept':[],'creator':me,'approver':me,'target':target},**e0))
				
			tk=Task.query.get(id)
			if tk:
				ct=Visitor.query.get(tk.creator_id)
				ap=Visitor.query.get(tk.approver_id)
				task=task_schema.dump(tk).data
				creator=visitor_schema.dump(ct).data
				creator['dp']=ct.Department.name
				approver=visitor_schema.dump(ap).data
				approver['dp']=ap.Department.name
				sql='''SELECT v.id,v.name,v.wx_headimgurl,v.department_id FROM `visitor_task` t INNER JOIN `visitor` v ON t.accept_id = v.id where task_id=%s;'''
				vas=db.session.execute(sql%id)
				accept=[]
				nm=0
				for row in vas:
					ac= {'id':row.id,'name':row.name,'score':0}
					dp=Department.query.get(row.department_id)
					ac['dp']=dp.name
					accept.append(ac)
					nm+=1
				task['accept_nm']=nm			
				sql='''SELECT d.id,d.name FROM `department` d INNER JOIN `visitor_task` v ON v.target_department = d.id where task_id=%s;'''
				dpts=db.session.execute(sql%id)
				dpl = [row.id for row in dpts]
				sql='''SELECT v.id,v.NAME,v.wx_headimgurl FROM `visitor` v INNER JOIN `visitor_task` t ON v.id = t.target_visitor where task_id=%s;'''
				pps=db.session.execute(sql%id)
				ppl = [row.id for row in pps]
				
				me=Department.query.get(self.x.did)
				mydpt=childDepartment(me)
				if self.x.uid<7:
					mydpt.append(me)
					
				all=Visitor.query.all()
				fls=[]
				for dpt in mydpt:
					for pp in all:
						if pp.department_id==dpt.id:
							if pp.id in ppl:
								fls.append({'id':pp.id,'name':pp.name,'department':dpt.name,'avatar':pp.wx_headimgurl,'checked':True})
							else:
								fls.append({'id':pp.id,'name':pp.name,'department':dpt.name,'avatar':pp.wx_headimgurl,'checked':False})
								
				dpts=[]
				for dp in mydpt:
					if dp.id in dpl:
						dpts.append({'id':dp.id,'name':dp.name,'checked':True})
					else:
						dpts.append({'id':dp.id,'name':dp.name,'checked':False})
						
				target={'fls':fls,'dpts':dpts}
				e0.update(self.x.had)
				return jsonify(dict({'task':task,'creator':creator,'approver':approver,'accept':accept,'target':target},**e0))
			return e3
		return e2
		
	def post(self,id=None):
		if self.x.did and self.x.tid and self.x.uid ==0:
			parser.add_argument('score_type')
			parser.add_argument('score')
			parser.add_argument('menber')
			parser.add_argument('expiry_at')
			parser.add_argument('pub_at')
			parser.add_argument('description')
			parser.add_argument('target')
			args = parser.parse_args()
			if not args['expiry_at']: 
				return e18
			if not args['description']: 
				return e9
			if args['score_type'] not in ['A+','B+','C+']:
				return e11
			try:
				int(args['score'])
				int(args['menber'])
				target=json.loads(args['target'])
				if len(target['tgp']) + len(target['tgd'])<1:
					raise e10
			except Exception as e:
				#print('****************',e)
				return e8			
			pub_at = datetime.date.today()
			state = 1
			if args['pub_at']:
				if len(args['pub_at'].split('-'))==3:
					pub_at= args['pub_at']
					state=0
			new_task = Task(creator_id=self.x.vid,
				approver_id=self.x.vid,
				menber=int(args['menber']),
				score_type=args['score_type'],
				score=int(args['score']),
				state=state,
				description=args['description'],
				expiry_at=args['expiry_at'],
				pub_at=pub_at)
			db.session.add(new_task)
			db.session.commit()
			db.session.refresh(new_task)
			task=task_schema.dump(new_task).data
			task['accept_nm']=0
			creator=visitor_schema.dump(Visitor.query.get(self.x.vid)).data

			vls=''
			if len(target['tgp'])>0:
				for p in target['tgp']:
					vls+='(%s,%s,NULL),'%(new_task.id,p)					
			if len(target['tgd'])>0:
				for d in target['tgd']:
					vls+='(%s,NULL,%s),'%(new_task.id,d)
				
			sql='''INSERT INTO `visitor_task` (`task_id`, `target_visitor`, `target_department`) VALUES %s;'''
			db.session.execute(sql%vls[:-1])
			db.session.commit()
			
			e0.update(self.x.had)
			return jsonify(dict({'task':task,'creator':creator,'approver':creator},**e0))
		return e2
		
	def put(self,id=None):
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:
			task=Task.query.filter_by(id=id)
			if task.first():
				if task.first().creator_id == self.x.vid:
					vts=VisitorTask.query.filter_by(task_id=id)
					for vt in vts.all():
						if vt.accept_id:
							return e6
					parser.add_argument('score_type')
					parser.add_argument('score')
					parser.add_argument('menber')
					parser.add_argument('expiry_at')
					parser.add_argument('pub_at')
					parser.add_argument('description')
					parser.add_argument('target')
					args = parser.parse_args()
					if args['score_type'] not in ['A+','B+','C+']:
						return e11
					if not args['description']: 
						return e9
					if not args['expiry_at']: 
						return e18
					try:
						int(args['score'])
						int(args['menber'])
						target=json.loads(args['target'])
						if len(target['tgp']) + len(target['tgd'])<1:
							raise e10 
					except Exception as e:						
						return e8

					pub_at = datetime.date.today()
					state = 1
					if args['pub_at']:
						if len(args['pub_at'].split('-'))==3:
							pub_at= args['pub_at']
							state=0
					task.update({"score":int(args['score']),
						"score_type":args['score_type'],
						"menber":int(args['menber']),
						"description":args['description'],
						"expiry_at":args['expiry_at'],
						"pub_at":pub_at,
						"state":state,
						"update_at":datetime.datetime.now()})
					db.session.commit()
					task=task_schema.dump(Task.query.get(id)).data
					task['accept_nm']=0
					
					sql='''delete FROM `visitor_task` where task_id=%s;'''
					db.session.execute(sql%id)
					db.session.commit()
					
					vls=''
					if len(target['tgp'])>0:
						for p in target['tgp']:
							vls+='(%s,%s,NULL),'%(id,p)					
					if len(target['tgd'])>0:
						for d in target['tgd']:
							vls+='(%s,NULL,%s),'%(id,d)
									
					sql='''INSERT INTO `visitor_task` (`task_id`, `target_visitor`, `target_department`) VALUES %s;'''
					db.session.execute(sql%vls[:-1])
					db.session.commit()	
					
					e0.update(self.x.had)
					return jsonify(dict({'task':task},**e0))
				return e7
			return e3
		return e2

	def delete(self,id=None):
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:
			task=Task.query.filter_by(id=id)
			if task.first().creator_id == self.x.vid:
				vts=VisitorTask.query.filter_by(task_id=id)
				for vt in vts.all():
					if vt.accept_id:
						return e6
				vts.delete()
				task.delete()
				db.session.commit()
				return e0
			return e7
		return e2
		
api.add_resource(task,'/task/<int:id>','/task')

class geTask(Resource):
	def __init__(self):
		self.x=verify(request)

	def put(self,id=None):
		if self.x.did and self.x.vid: 
			task=Task.query.get(id)
			if task.creator_id!=self.x.vid:
				if task.state<4:
					sql='''select id from visitor_task where accept_id=%s and task_id=%s;'''
					isgo=db.session.execute(sql%(self.x.vid, id))
					isgo=[i.id for i in isgo]
					if len(isgo)==0:
						sql='''SELECT COUNT(*) AS C, t.menber as M FROM visitor_task AS v left join task AS t ON t.id=v.task_id WHERE  v.task_id=%s AND v.accept_id IS NOT NULL;'''
						isgo=db.session.execute(sql%(id))
						isgo=[(i.C, i.M)for i in isgo]
						if isgo[0][0] == 0 or isgo[0][0] < isgo[0][1]:						
							sql='''select id from visitor_task where target_visitor=%s or target_department=%s AND task_id=%s;'''
							isgo=db.session.execute(sql%(self.x.vid, self.x.did, id))
							isgo=[i for i in isgo]
							if len(isgo)>0:
								sql='''UPDATE task set state=2 WHERE id=%s;'''
								isgo=db.session.execute(sql%id)
								
								sql='''UPDATE  visitor_task set accept_id=%s  WHERE  (target_visitor=%s or target_department=%s) AND task_id=%s AND accept_id IS NULL LIMIT 1;'''
								isgo=db.session.execute(sql%(self.x.vid, self.x.vid, self.x.did, id))
								db.session.commit()
								if isgo:
									e0.update(self.x.had)	
									return e0
								sql='''INSERT INTO `visitor_task` (`task_id`, `accept_id`) VALUES (%s,%s);'''
								isgo=db.session.execute(sql%(id, self.x.vid))
								db.session.commit()
								if isgo:
									e0.update(self.x.had)	
									return e0
								return e14
							return e13
						return e25						
					return e12
				return e15
			return e20 
		return e2
	
	def post(self,id=None):
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:
			sql='''delete FROM visitor_task WHERE target_visitor is NULL AND target_department is NULL AND accept_id=%s AND task_id=%s;'''
			rt1=db.session.execute(sql%(self.x.vid, id))
			sql='''UPDATE visitor_task set accept_id=NULL WHERE accept_id=%s AND task_id=%s;'''
			rt2=db.session.execute(sql%(self.x.vid, id))
			db.session.commit()
			
			#sql='''UPDATE task set state=1 WHERE accept_id=%s AND task_id=%s;'''
			#rt2=db.session.execute(sql%(self.x.vid, id))
			#db.session.commit()
			
			if rt1 or rt2:
				e0.update(self.x.had)
				return e0
			return e1
		return e2
api.add_resource(geTask,'/getask/<int:id>','/getask')

class noTask(Resource):
	def __init__(self):
		self.x=verify(request)

	def put(self,id=None):
		if self.x.did and self.x.vid: 
			task=Task.query.filter_by(id=id)
			tk=task.first()
			if tk:
				if tk.creator_id==self.x.vid:
					if tk.state<4:
						task.update({'state':5})
						db.session.commit()
						e0.update(self.x.had)	
						return e0
					return e15
				return e2
			return e3
		return e2

api.add_resource(noTask,'/notask/<int:id>')


class visitorSchema(ma.Schema):
    class Meta:
        fields = ('id', 'department_id','duty_id','auth','team','title','sex','education', 'name', 'passwd','tel','wx_nickname', 'wx_openid', 'wx_sex', 'wx_province', 'wx_city', 'wx_country', 'wx_headimgurl', 'wx_privilege','date_in', 'birthday')
visitor_schema = visitorSchema(strict=True)
visitors_schema = visitorSchema(many=True, strict=True)

class visitor(Resource):
	def __init__(self):
		self.x=verify(request)
		#print(self.x.__dict__)
	def get(self,id=None):
		if id is not None:
			if self.x.did and self.x.tid:
				visitor=Visitor.query.get(id=id)
				if visitor:
					visitor=visitor_schema.dump(visitor).data
					e0.update(self.x.had)
					visitor['passwd']=''
					return jsonify(dict(visitor,**e0))
				return e1
			return e2
			
		if self.x.vid:
			visitor=Visitor.query.get(self.x.vid)
			if visitor:
				visitor=visitor_schema.dump(visitor).data
				e0.update(self.x.had)
				visitor['passwd']=''
				return jsonify(dict(visitor,**e0))
			return e1
		return e2
		
	def post(self, id=None):	
		if self.x.vid:			
			visitor=visitor_schema.dump(Visitor.query.get(self.x.vid)).data			
			e0.update(self.x.had)
			visitor['passwd']=''
			return jsonify(dict(visitor,**e0))
		return e29
		
	def put(self, id=None):
		parser.add_argument("name")
		parser.add_argument("passwd")
		#parser.add_argument("date_in")
		#parser.add_argument("birthday")
		parser.add_argument("tel")
		parser.add_argument("duty_id")
		parser.add_argument("name")
		args=parser.parse_args()

		if self.x.vid:
			visitor=Visitor.query.filter_by(id=self.x.vid)
			if self.x.vid == visitor.first().id:
				if len(args["passwd"])>5:
					visitor.update({
						"name":args["name"],
						"passwd":hashlib.md5(args["passwd"].encode()).hexdigest(),
						"date_in":datetime.datetime.today(),#args["date_in"],
						"birthday":datetime.datetime.today(),#args["birthday"],
						"tel":args["tel"]
					})
				else:
					visitor.update({
						"name":args["name"],
						"date_in":datetime.datetime.today(),#args["date_in"],
						"birthday":datetime.datetime.today(),#args["birthday"],
						"tel":args["tel"]
					})
				db.session.commit()
				vst=Visitor.query.filter_by(id=self.x.vid).first()
				visitor=visitor_schema.dump(vst).data
				e0.update(self.x.had)
				visitor['passwd']=''
				return jsonify(dict(visitor,**e0))
			return e2
			
		if self.x.vid:
			visitor=Visitor.query.filter_by(id=self.x.vid)
			if visitor.first():
				visitor.update({"name":args["name"],"passwd":hashlib.md5(args["passwd"].encode()).hexdigest(),"tel":args["tel"]})
				db.session.commit()
				vst=Visitor.query.get(self.x.vid)
				visitor=visitor_schema.dump(vst).data
				e0.update(self.x.had)
				visitor['passwd']=''
				return jsonify(dict(visitor,**e0))
			return e3
		return e1
		
	def delete(self,id=None):
		if id is not None:
			if self.x.tid==1:
				Visitor.query.filter_by(id=id).delete()
				db.session.commit()
				visitors=visitors_schema.dump(Visitor.query.all()).data
				e0.update(self.x.had)
				return jsonify(dict({'lst':visitors},**e0))
			return e2
			
		if self.x.vid:
			visitor=Visitor.query.filter_by(id=self.x.vid).update({
				"name":"",
				"date_in":None,
				"birthday":None,
				"tel":"",
				"department_id":"",
				"duty_id":""
			})
			db.session.commit()
			visitor=visitor_schema.dump(visitor).data
			e0.update(self.x.had)
			return jsonify(dict(visitor,**e0))
		return e1
api.add_resource(visitor,'/visitor/<int:id>','/visitor')

class visitors(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self):
		if self.x.tid:
			duty=Duty.query.get(self.x.tid)
			if duty and duty.role < 7:
				#visitors=visitors_schema.dump(Visitor.query.all()).data
				sql='''select v.*,d.name as dept,t.NAME AS duty from visitor as v left join department as d on v.department_id=d.id LEFT JOIN duty AS t ON v.duty_id=t.id;'''
				vs=db.session.execute(sql)
				lst=[{'id':v.id,'name':v.name,'department':v.dept,'duty':v.duty,'tel':v.tel,'auth':v.auth} for v in vs]
				e0.update(self.x.had)
				return jsonify(dict({'lst':lst},**e0))
		return e2
		
	def post(self):
		if self.x.uid<7 and self.x.tid:
			parser.add_argument('wx_openID')
			parser.add_argument('name')
			args = parser.parse_args()
			new_visitor = Visitor(wx_openID=args['wx_openID'],name=args['name'])
			db.session.add(new_visitor)
			db.session.commit()
			visitors = Visitor.query.all()
			return visitors_schema.jsonify(visitors)
		return e2
api.add_resource(visitors,'/visitors')

class vzts(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self):
		if self.x.vid and self.x.uid==0:
			visitors=Visitor.query.all()
			#dept=Department.query.all()
			#dts=Duty.query.all()
			lst=[]
			for vt in visitors:
				if vt.Department and vt.Duty:
					#lst.append({'id':vt.id,'dept':vt.Department.name,'duty':vt.Duty.name,'name':vt.name})
					lst.append((vt.id,vt.Department.name,vt.Duty.name,vt.name))
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst},**e0))
		return e2
api.add_resource(vzts,'/vzts')

class lotterySchema(ma.Schema):
    class Meta:
        fields = ('id', 'propose_id' ,'beneficiary_id', 'distributor_id','printer_id', 'description', 'classify', 'state', 'print_at', 'create_at')
lottery_schema = lotterySchema(strict=True)
lotteries_schema = lotterySchema(many=True, strict=True)

class lottery(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self,id=None):
		if id:
			lty=Lottery.query.get(id)		
			return lottery_schema.jsonify(lty)
		return e1
		
	def post(self,id=None):
		if self.x.vid and self.x.uid==0:
			parser.add_argument('beneficiary_id')
			parser.add_argument('description')
			parser.add_argument('classify')
			args = parser.parse_args()
			if args['classify'] not in ['金券','银券','红券']:
				return e1
			if args['description']:
				return e22
			lty = Lottery(beneficiary_id=args['beneficiary_id'], description=args['description'], classify=args['classify'], distributor_id=self.x.vid)
			db.session.add(lty)
			db.session.commit()
			Lotteries = Lottery.query.all()
			lties=lotteries_schema.dump(Lotteries).data
			e0.update(self.x.had)
			return jsonify(dict({'lst':lties},**e0))
		return e2
		
	def put(self,id=None):
		if self.x.vid and self.x.uid==0:
			parser.add_argument('state')
			args = parser.parse_args()
			if args['state'] not in ['已打印','未打印']:
				return e1
			lty=Lottery.query.filter_by(id=id)
			if lty.first():
				lty.update({'state':args['state']})
				dn.session.commit()
				lty=lotterySchema.dump(Lottery.query.get(id)).data
				e0.update(self.x.had)
				return jsonify(dict({'lottery':lty},**e0))
			return e3
		return e2
api.add_resource(lottery, '/lottery/<int:id>', '/lottery')

def ltyPrint(lty):
	img=Image.open('jp.jpg').convert('RGBA')
	txt=Image.new('RGBA', img.size, (255,255,255,0))
	fnt=ImageFont.truetype("simsun.ttc", 40, encoding="utf-8")
	ImageDraw.Draw(txt).text((220,175),	lty['dept'], font=fnt, fill ="black")
	ImageDraw.Draw(txt).text((490,175),	lty['beneficiary'], font=fnt, fill ="black")
	ImageDraw.Draw(txt).text((240,245),	lty['description'], font=fnt, fill ="black")
	ImageDraw.Draw(txt).text((840,405), lty['distributor'], font=fnt, fill ="black")
	ImageDraw.Draw(txt).text((1210,459), str(lty['print_at'].year), font=fnt, fill ="black")
	ImageDraw.Draw(txt).text((1320,459), str(lty['print_at'].month), font=fnt, fill ="black")
	ImageDraw.Draw(txt).text((1400,459), str(lty['print_at'].day), font=fnt, fill ="black")
	out=Image.alpha_composite(img, txt)
	#out.convert('RGB').show()
	#txt.convert('RGBA').show()
	txt.convert('RGB').save('jq'+str(lty['id'])+'.jpg')
	return [out,txt.convert('RGB')]
	
class lotteries(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self,cls=None):
		if self.x.vid and self.x.uid==0:
			sql='''delete FROM lottery WHERE state='未打印' AND propose_id IS not null and id not IN (SELECT id FROM (SELECT id FROM lottery where state='未打印'  group BY propose_id) AS c);'''
			db.session.execute(sql)
			db.session.commit()			
			sql='''SELECT l.id,l.description,l.classify,l.state,l.create_at,b.name AS bn,b.dept, d.name AS dn ,T.tt, l.propose_id FROM lottery AS l 
				left JOIN (SELECT v.id,v.name AS name, dp.name AS dept FROM department AS dp INNER JOIN visitor AS v ON dp.id=v.department_id) 
				AS b ON l.beneficiary_id=b.id 
				left JOIN visitor AS d ON l.distributor_id=d.id 
				LEFT JOIN  (SELECT COUNT(*) AS tt,5 as t FROM lottery ORDER BY create_at desc) AS T ON t.t=5
				%s
				ORDER BY l.create_at DESC LIMIT 900; '''
			if cls==None:
				sql=sql%""
			else:
				sql=sql%("where classify='"+cls+"'")
			#print(sql)
			lty=db.session.execute(sql)
			lst=[(ls.id,ls.classify,ls.description,ls.bn,ls.dn,ls.state,str(ls.create_at).split(' ')[0],ls.dept,0,ls.tt,ls.propose_id) for ls in lty]
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst},**e0))
		return e2
		
	def post(self,cls=None):
		if self.x.vid and self.x.uid==0:
			parser.add_argument('people')
			parser.add_argument('description')
			parser.add_argument('classify')
			parser.add_argument('qty')
			args = parser.parse_args()
			if args['classify'] not in ['金券','银券','红券']:
				return e1
			if not args['description']:
				return e22
			try:
				score=int( args['qty'])				
			except Exception as e:
				return e33
			ppl=json.loads(args['people'])
			#print(ppl[0])
			for i in range(int( args['qty'])):
				for pp in ppl:
					lty = Lottery(beneficiary_id=pp[0], description=args['description'], classify=args['classify'], distributor_id=self.x.vid)
					db.session.add(lty)
			db.session.commit()
			e0.update(self.x.had)
			return e0
		return e2
		
	def put(self,cls=None):
		if self.x.vid and self.x.uid==0:
			parser.add_argument('prt')
			args = parser.parse_args()
			if args['prt']:				
				prt=json.loads(args['prt'])				
				for lid in prt:
					Lottery.query.filter_by(id=lid).update({'printer_id':self.x.vid,'print_at':datetime.datetime.now(),'state':'已打印'})
				db.session.commit()
				sql='''select l.id,l.description AS des,l.classify,l.print_at, b.name AS bn, b.department_id as did, d.name AS dn ,dp.dpn
					from lottery as l 
					LEFT JOIN visitor as b ON l.beneficiary_id=b.id 
					LEFT JOIN visitor AS d ON  l.distributor_id=d.id
					LEFT JOIN (SELECT v.id as uid,dpt.name AS dpn FROM department AS dpt LEFT JOIN visitor AS v ON dpt.id=v.department_id) 
					AS dp ON dp.uid=l.beneficiary_id %s ;'''
				tup='('+str(prt)[1:-1]+')'
				if cls==None:
					sql=sql%("WHERE l.id IN "+tup)
				else:
					sql=sql%("WHERE l.id IN "+tup + " and classify='"+cls+"'")
				pts=db.session.execute(sql)
				os.remove(os.path.join(os.getcwd(), "jq.zip"))
				zipf = zipfile.ZipFile('jq.zip','w', zipfile.ZIP_DEFLATED)
				for pt in pts:
					ltyPrint({'id':pt.id,'description':pt.des,'classify':pt.classify,'print_at':pt.print_at,'dept':pt.dpn,'beneficiary':pt.bn,'distributor':pt.dn})
					zipf.write("jq%s.jpg" % pt.id)
					os.remove(os.path.join(os.getcwd(), "jq%s.jpg" % pt.id))
				zipf.close()
				return send_file('jq.zip', mimetype='zip', attachment_filename="jq.zip", as_attachment=True)
			return e3
		return e2
		
api.add_resource(lotteries, '/lotteries','/lotteries/<string:cls>')

class prt(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self,id,cls=None):
		if self.x.vid and self.x.uid==0:
			sql='''SELECT l.id,l.description,l.classify,l.state,l.create_at,b.name AS bn,b.dept, d.name AS dn, T.tt as tt, l.propose_id
				FROM lottery AS l
				left JOIN (SELECT v.id,v.name AS name, dp.name AS dept FROM department AS dp INNER JOIN visitor AS v ON dp.id=v.department_id) 
				AS b ON l.beneficiary_id=b.id 
				left JOIN visitor AS d ON l.distributor_id=d.id
				LEFT JOIN  (SELECT COUNT(*) AS tt,5 as t FROM lottery ORDER BY create_at desc) AS T ON t.t=5
				%s
				ORDER BY l.create_at DESC LIMIT '''+str(id*12)+''',12;'''
			if cls==None:
				sql=sql%""
			else:
				sql=sql%("where classify='"+cls+"'")
			lty=db.session.execute(sql)
			lst=[(ls.id,ls.classify,ls.description,ls.bn,ls.dn,ls.state,str(ls.create_at).split(' ')[0],ls.dept,id,ls.tt,ls.propose_id) for ls in lty]
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst},**e0))
		return e2		
api.add_resource(prt, '/prt/<int:id>', '/prt/<string:cls>/<int:id>')

class ltFilter(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def put(self):
		if self.x.vid and self.x.uid==0:
			parser.add_argument('lty')
			args = parser.parse_args()
			lty=json.loads(args['lty'])
			sql='''SELECT l.id,l.description,l.classify,l.state,l.create_at,b.name AS bn,b.dept, d.name AS dn, T.tt as tt, l.propose_id
				FROM lottery AS l
				left JOIN (SELECT v.id,v.name AS name, dp.name AS dept FROM department AS dp INNER JOIN visitor AS v ON dp.id=v.department_id) 
				AS b ON l.beneficiary_id=b.id 
				left JOIN visitor AS d ON l.distributor_id=d.id
				LEFT JOIN  (SELECT COUNT(*) AS tt,5 as t FROM lottery ORDER BY create_at desc) AS T ON t.t=5
				ORDER BY l.create_at DESC LIMIT %s,15;'''
			lty=db.session.execute(sql%(id*15))
			lst=[(ls.id,ls.classify,ls.description,ls.bn,ls.dn,ls.state,str(ls.create_at).split(' ')[0],ls.dept,id,ls.tt,ls.propose_id) for ls in lty]
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst},**e0))
		return e2
		
api.add_resource(ltFilter, '/ltfilter')

class lts(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def put(self,cls=None):
		if self.x.vid and self.x.uid==0:
			parser.add_argument('prt')
			args = parser.parse_args()
			if args['prt']:
				prt=json.loads(args['prt'])				
				for lid in prt:
					Lottery.query.filter_by(id=lid).update({'printer_id':self.x.vid,'print_at':datetime.datetime.now(),'state':'已打印'})
				db.session.commit()
				sql='''select l.id,l.description AS des,l.classify,l.print_at, b.name AS bn, b.department_id as did, d.name AS dn ,dp.dpn
					from lottery as l 
					LEFT JOIN visitor as b ON l.beneficiary_id=b.id 
					LEFT JOIN visitor AS d ON  l.distributor_id=d.id
					LEFT JOIN (SELECT v.id as uid,dpt.name AS dpn FROM department AS dpt LEFT JOIN visitor AS v ON dpt.id=v.department_id) 
					AS dp ON dp.uid=l.beneficiary_id WHERE  l.id IN ('''+str(prt)[1:-1]+''') %s;'''
				if cls==None:
					sql=sql%""
				else:
					sql=sql%("and classify='"+cls+"'")
				pts=db.session.execute(sql)
				lst=[{'id':r.id,'dpt':r.dpn,'bn':r.bn,'desc':r.des,'dn':r.dn,'ts':str(r.print_at).split(' ')[0].split('-')} for r in pts]

				sql='''SELECT l.id,l.description,l.classify,l.state,l.create_at,b.name AS bn,b.dept, d.name AS dn ,T.tt, l.propose_id FROM lottery AS l 
					left JOIN (SELECT v.id,v.name AS name, dp.name AS dept FROM department AS dp INNER JOIN visitor AS v ON dp.id=v.department_id) 
					AS b ON l.beneficiary_id=b.id 
					left JOIN visitor AS d ON l.distributor_id=d.id 
					LEFT JOIN  (SELECT COUNT(*) AS tt,5 as t FROM lottery ORDER BY create_at desc) AS T ON t.t=5
					%s
					ORDER BY l.create_at DESC; '''
				if cls==None:
					sql=sql%""
				else:
					sql=sql%("where classify='"+cls+"'")
				lty=db.session.execute(sql)
				ast=[(ls.id,ls.classify,ls.description,ls.bn,ls.dn,ls.state,str(ls.create_at).split(' ')[0],ls.dept,0,ls.tt,ls.propose_id) for ls in lty]
				e0.update(self.x.had)
				return jsonify(dict({'lst':lst,'ast':ast},**e0))
			return e3
		return e2
		
api.add_resource(lts, '/lts','/lts/<string:cls>')

class autoPrint(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self,cls=None):
		if self.x.vid and self.x.uid==0:
			sql='''SELECT l.id,b.NAME AS bn,dp.dpn AS dpn, d.NAME AS dn, l.description AS des FROM lottery AS l
				LEFT JOIN visitor as b ON l.beneficiary_id=b.id
				LEFT JOIN visitor AS d ON  l.distributor_id=d.id
				LEFT JOIN (SELECT v.id as uid,dpt.name AS dpn FROM department AS dpt LEFT JOIN visitor AS v ON dpt.id=v.department_id) 
				AS dp ON dp.uid=l.beneficiary_id
				WHERE l.state='未打印' and b.NAME is not null AND dp.dpn IS not null %s
				ORDER BY dp.dpn, b.NAME limit 64'''
			if cls==None:
				sql=sql%""
			else:
				sql=sql%("and classify='"+cls+"'")
			pts=db.session.execute(sql)
			lst=[{'id':r.id,'dpt':r.dpn,'bn':r.bn,'desc':r.des,'dn':r.dn,'ts':str(datetime.datetime.now()).split(' ')[0].split('-')} for r in pts]
			bm=True
			if len(lst)<64:
				bm=False
			e0.update(self.x.had)
			for r in lst:
				Lottery.query.filter_by(id=r['id']).update({'printer_id':self.x.vid,'print_at':datetime.datetime.now(),'state':'已打印'})
			db.session.commit()
			return jsonify(dict({'lst':lst,'bm':bm},**e0))
		return e2
	
	def put(self,cls=None):
		if self.x.vid and self.x.uid==0:
			parser.add_argument('ptd')
			args = parser.parse_args()
			ptd=json.loads(args['ptd'])
			for r in ptd:
				Lottery.query.filter_by(id=r).update({'printer_id':self.x.vid,'print_at':datetime.datetime.now(),'state':'已打印'})
			db.session.commit()
			e0.update(self.x.had)
			return jsonify(dict({},**e0))
		return e2
		
api.add_resource(autoPrint, '/autoprint', '/autoprint/<string:cls>')

class MyLyts(Resource):
	def __init__(self):
		self.x=verify(request)		
	def get(self):
		if self.x.vid:
			sql='''SELECT classify,state,COUNT(*) as tt FROM lottery WHERE beneficiary_id=%s group BY classify,state ;'''
			lty=db.session.execute(sql%self.x.vid)
			G={'T':0,'P':0,'L':0}
			S={'T':0,'P':0,'L':0}
			R={'T':0,'P':0,'L':0}
			for ly in lty:
				if ly.classify=='金券':					
					if ly.state=='已打印':
						G['P']+=ly.tt
					if ly.state=='未打印':
						G['L']+=ly.tt
					if ly.state=='已使用':
						G['T']+=ly.tt
				if ly.classify=='银券':					
					if ly.state=='已打印':
						S['P']+=ly.tt
					if ly.state=='未打印':
						S['L']+=ly.tt
					if ly.state=='已使用':
						S['T']+=ly.tt
				if ly.classify=='红券':
					if ly.state=='未打印':
						R['T']+=ly.tt
					if ly.state=='已使用':
						R['P']+=ly.tt
					if ly.state=='投注':
						R['L']+=ly.tt
			e0.update(self.x.had)
			return jsonify(dict({'G':G,'S':S,'R':R},**e0))
		return e2
		
	def put(self):
		if self.x.vid:
			parser.add_argument("qty")
			args=parser.parse_args()			
			sql='''SELECT classify,state,COUNT(*) as tt FROM lottery WHERE beneficiary_id=%s group BY classify,state; '''
			lty=db.session.execute(sql%self.x.vid)
			R={'T':0,'P':0,'L':0}
			for ly in lty:
				if ly.classify=='红券':
					if ly.state=='未打印':
						R['T']+=ly.tt
					if ly.state=='已使用':
						R['P']+=ly.tt
					if ly.state=='投注':
						R['L']+=ly.tt
			qty=0
			try:
				qty=int(args['qty'])
			except Exception as e:
				return jsonify(dict({'R':R},**e33))
			if qty<1:
				return jsonify(dict({'R':R},**e33))
			if qty>R['T']:
				return jsonify(dict({'R':R},**e34))
			sql='''SELECT l.id,ll.tt from lottery AS l LEFT JOIN (
				SELECT COUNT(*) AS tt from lottery WHERE state='投注' AND classify='红券') AS ll ON 1=1
				WHERE l.state ='未打印' AND l.classify='红券' AND l.beneficiary_id=%s; '''
			lts=db.session.execute(sql%self.x.vid)
			
			cpt='A-'
			cps=db.session.execute('''SELECT DISTINCT(SPLIT_STR(dice, '-', 1)) from lottery WHERE state='已使用' AND classify='红券' AND dice IS NOT null;''')
			cpr=''
			for cp in cps:
				cp=cp[0]
				if len(cp)>len(cpr):
					cpr=cp
				if len(cp)==len(cpr):
					cpr=max([cp,cpr])
			if cpr!='':
				if cpr[-1]=='Z':
					cpt=cpr+'A-'
				else:
					cpt=cpr[:-1]+chr(ord(cpr[-1])+1)+'-'
			idx=1
			for lt in lts:
				sl=lt.tt+idx
				db.session.execute('''update lottery set state='投注',serial='%s',dice='%s' where id='%s';'''%(cpt+str(sl), cpt+i2t(sl-1), lt.id))
				if idx==qty:
					break
				idx+=1
			db.session.commit()
			R['T']-=qty
			R['L']+=qty
			e0.update(self.x.had)
			return jsonify(dict({'R':R},**e0))
		return e2
		
	def post(self):
		if self.x.vid:
			#return e36
			parser.add_argument("from")
			parser.add_argument("to")
			parser.add_argument("qty")
			args=parser.parse_args()		
			sql='''SELECT classify,state,COUNT(*) as tt FROM lottery WHERE beneficiary_id=%s group BY classify,state ;'''
			lty=db.session.execute(sql%self.x.vid)
			G={'T':0,'P':0,'L':0}
			S={'T':0,'P':0,'L':0}
			R={'T':0,'P':0,'L':0}
			for ly in lty:
				if ly.classify=='金券':					
					if ly.state=='已打印':
						G['P']+=ly.tt
					if ly.state=='未打印':
						G['L']+=ly.tt
					if ly.state=='已使用':
						G['T']+=ly.tt
				if ly.classify=='银券':					
					if ly.state=='已打印':
						S['P']+=ly.tt
					if ly.state=='未打印':
						S['L']+=ly.tt
					if ly.state=='已使用':
						S['T']+=ly.tt
				if ly.classify=='红券':
					if ly.state=='未打印':
						R['T']+=ly.tt
					if ly.state=='已使用':
						R['P']+=ly.tt
					if ly.state=='投注':
						R['L']+=ly.tt
			qty=0
			try:
				qty=int(args['qty'])
			except Exception as e:
				return e33
			if args['from']=='R' :
				if qty>R['T']:
					return e34
				R['T']-=qty
				R['P']+=qty
			if args['from']=='S' :
				if qty>S['L']:
					return e35
				S['L']-=qty
				S['T']-=qty
			if args['to']=='S' and args['from']=='R':
				if qty%10>0:
					return e33
				S['L']+=qty/10
				S['T']+=qty/10				
				sql=''
				for i in range(int(qty/10)):
					sql+="( "+str(self.x.vid)+",333,'红券兑换。','银券'),"
				db.session.execute('''INSERT INTO lottery ( beneficiary_id, distributor_id, description, classify) VALUES %s; '''%(sql[:-1]))
				db.session.execute('''update lottery set state='已使用' where beneficiary_id=%s and state='未打印' and classify='红券' limit %s;'''%(self.x.vid,qty))
				
			if args['to']=='G' and args['from']=='R':
				if qty%50>0:
					return e33
				G['L']+=qty/50
				G['T']+=qty/50
				sql=''
				for i in range(int(qty/50)):
					sql+="( "+str(self.x.vid)+",333,'红券兑换。','金券'),"
				db.session.execute('''INSERT INTO lottery ( beneficiary_id, distributor_id, description, classify) VALUES %s; '''%(sql[:-1]))
				db.session.execute('''update lottery set state='已使用' where beneficiary_id=%s and state='未打印' and classify='红券' limit %s;'''%(self.x.vid,qty))
				
			if args['to']=='G' and args['from']=='S':
				if qty%5>0:
					return e33
				G['L']+=qty/5
				G['T']+=qty/5
				sql=''
				for i in range(int(qty/5)):
					sql+="( "+str(self.x.vid)+",333,'银券兑换。','金券'),"
				db.session.execute('''INSERT INTO lottery ( beneficiary_id, distributor_id, description, classify) VALUES %s; '''%(sql[:-1]))
				db.session.execute('''update lottery set state='已使用' where beneficiary_id=%s and state='未打印' and classify='银券' limit %s;'''%(self.x.vid,qty))
			db.session.commit()
			e0.update(self.x.had)
			return jsonify(dict({'G':G,'S':S,'R':R},**e0))
		return e2
api.add_resource(MyLyts, '/mylyts')

def rsa_sign(plaintext, private_file, hash_algorithm=SHA512):
    """RSA 数字签名"""
    private_key = open(private_file, 'rb').read()
    signer = PKCS1_v1_5.new(RSA.importKey(private_key))
    # hash算法必须要pycrypto库里的hash算法，不能直接用系统hashlib库，pycrypto是封装的hashlib
    hash_value = hash_algorithm.new(plaintext)   
    return signer.sign(hash_value)

def rsa_verify(sign, plaintext, public_file, hash_algorithm=SHA512):
    """校验RSA 数字签名"""
    public_key = open(public_file, 'rb').read()
    hash_value = hash_algorithm.new(plaintext)
    verifier = PKCS1_v1_5.new(RSA.importKey(public_key))
    return verifier.verify(hash_value, sign)
	
class RfLyts(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self,id):
		if id==4:
			sql='''SELECT max(length(SPLIT_STR(l.SERIAL, '-', 2)))as SERIAL,max(length(SPLIT_STR(l.dice, '-', 2))) as dice from lottery AS l WHERE l.state='投注' AND l.classify='红券'; '''
			sd=db.session.execute(sql)
			sn=0
			dn=0
			for r in sd:
				sn=r.SERIAL
				dn=r.dice
			sql='''SELECT dp.name,dp.dpt, l.description,SPLIT_STR(l.SERIAL, '-', 1)as cpt,SPLIT_STR(l.SERIAL, '-', 2)as SERIAL,SPLIT_STR(l.dice, '-', 2) as dice,l.create_at 
			from lottery AS l LEFT JOIN (SELECT v.id,v.NAME,d.NAME AS dpt FROM visitor AS v LEFT JOIN department AS d ON v.department_id=d.id) 
			AS dp ON dp.id=l.beneficiary_id WHERE l.state='投注' and l.classify='红券'; '''
			lyt=db.session.execute(sql)
			cpt=''
			lst=[]
			for r in lyt:
				dsf=(sn-len(r.SERIAL))*"0"
				ddf=(dn-len(r.dice))*"1"
				lst.append((r.SERIAL, r.dice, r.dpt, r.NAME, r.description, str(r.create_at).split(' ')[0], dsf+r.SERIAL, ddf+r.dice))
				cpt=r.cpt
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst,'cpt':cpt},**e0))
			
		if self.x.vid:
			if id==2:
				sql='''SELECT dp.name,dp.dpt, l.description,l.SERIAL,l.dice,l.create_at from lottery AS l
				LEFT JOIN (SELECT v.id,v.NAME,d.NAME AS dpt FROM visitor AS v LEFT JOIN department AS d ON v.department_id=d.id) AS dp ON dp.id=l.beneficiary_id
				WHERE l.beneficiary_id=%s AND l.state='投注' and classify='红券' limit 300; '''
				lyt=db.session.execute(sql%self.x.vid)
				lst=[]
				dpt=''
				name=''
				for r in lyt:
					lst.append({"desc":r.description,"ts":str(r.create_at).split(' ')[0],"srl":r.SERIAL,"dice":r.dice})
					dpt=r.dpt
					name=r.NAME
				e0.update(self.x.had)
				return jsonify(dict({'dpt':dpt,'name':name,'lst':lst},**e0))
			if id==1:
				sql='''SELECT dp.name,dp.dpt, l.description,l.SERIAL,l.dice,l.create_at from lottery AS l
				LEFT JOIN (SELECT v.id,v.NAME,d.NAME AS dpt FROM visitor AS v LEFT JOIN department AS d ON v.department_id=d.id) AS dp ON dp.id=l.beneficiary_id
				WHERE l.beneficiary_id=%s AND l.state='未打印' and classify='红券' limit 300; '''
				lyt=db.session.execute(sql%self.x.vid)
				lst=[]
				dpt=''
				name=''
				for r in lyt:
					lst.append({"desc":r.description,"ts":str(r.create_at).split(' ')[0],"srl":r.SERIAL,"dice":r.dice})
					dpt=r.dpt
					name=r.NAME
				e0.update(self.x.had)
				return jsonify(dict({'dpt':dpt,'name':name,'lst':lst},**e0))
				
			if id==3:
				sql='''SELECT dp.name,dp.dpt, l.description,l.SERIAL,l.dice,l.create_at from lottery AS l
				LEFT JOIN (SELECT v.id,v.NAME,d.NAME AS dpt FROM visitor AS v LEFT JOIN department AS d ON v.department_id=d.id) AS dp ON dp.id=l.beneficiary_id
				WHERE l.beneficiary_id=%s AND l.state='投注' and classify='红券'; '''
				lyt=db.session.execute(sql%self.x.vid)
				lst=[("序列："+r.SERIAL,"  骰子："+r.dice,"  奖给："+r.dpt+" - "+r.NAME,"  因："+r.description,"  "+str(r.create_at).split(' ')[0]) for r in lyt]
				fn="L"+str(datetime.datetime.now()).replace(" ","-").replace(":","").replace(".","")+".txt"
				f = open(fn,'w+',encoding='utf-8-sig',newline='')			
				w = csv.writer(f)
				w.writerow(["本文件经过数字签名，用于验证您是否中奖。请勿更改文件内容。任何修改将导致数字签名失效，无法验证您的中奖信息！"])
				w.writerows(lst)
				f.seek(0, 0)
				# 生成签名
				s=open(fn+'.数字签名，请妥善保存.sig','wb+')
				signature = rsa_sign(f.read().encode(encoding='utf-8'), r'sig/private_key.pem')
				s.write(signature)
				# 验证签名
				#f.seek(0, 0)
				#s.seek(0, 0)
				#public_key = open('sig/public_key.pem', 'rb').read()
				#hash_value = SHA512.new(f.read().encode(encoding='utf-8'))
				#verifier = PKCS1_v1_5.new(RSA.importKey(public_key))
				#print(verifier.verify(hash_value, s.read()))
				
				f.close()
				s.close()
				zipf = zipfile.ZipFile('C:\\cfkpi\\nginx\\html\\export\\'+fn+'.zip','w', zipfile.ZIP_DEFLATED)
				zipf.write(fn)
				zipf.write(fn+'.数字签名，请妥善保存.sig')
				zipf.close()
				os.remove(os.path.join(os.getcwd(), fn))
				os.remove(os.path.join(os.getcwd(), fn+'.数字签名，请妥善保存.sig'))
				return jsonify(dict({'url':'http://120.26.118.222:8001/export/%s'%fn+'.zip'},**e0))			
		return e2
		
api.add_resource(RfLyts,'/rflyts/<int:id>')

class SumLyts(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self):
		if self.x.vid:
			sql='''SELECT v.team AS M, l.classify+0 AS C, l.state+0 AS S, COUNT(l.id) AS T 
				FROM lottery AS l LEFT JOIN visitor AS v ON l.beneficiary_id=v.id
				WHERE v.team IS NOT null
				group BY v.team, l.classify, l.state;'''
			rst=db.session.execute(sql)
			lts=[{'M':r.M, 'C':r.C, 'S':r.S, 'T':r.T} for r in rst]
			e0.update(self.x.had)
			return jsonify(dict({'lst':lts},**e0))
		return e2
api.add_resource(SumLyts, '/sumlyts')

class followers(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self,id=None):
		if self.x.uid<7 and self.x.tid:
			me=Visitor.query.get(self.x.vid)
			mydpt=childDepartment(me.Department)
			all=Visitor.query.all()			
			fls=[]
			for dpt in mydpt:
				for pp in all:
					if pp.department_id==dpt.id:
						fls.append(pp)
			visitors=visitors_schema.dump(fls).data
			e0.update(self.x.had)
			return jsonify(dict({'lst':visitors},**e0))
		return e2
		
api.add_resource(followers,'/followers')

class fls(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self,id=None):
		if self.x.uid<7 and self.x.tid:
			me=Visitor.query.get(self.x.vid)
			mydpt=childDepartment(me.Department)
			all=Visitor.query.all()
			fls=[]
			for dpt in mydpt:
				for pp in all:
					if pp.department_id==dpt.id:
						fls.append({'id':pp.id,'department_id':dpt.id,'duty_id':pp.duty_id,'name':pp.name,'department':dpt.name,'avatar':pp.wx_headimgurl})
			e0.update(self.x.had)
			return jsonify(dict({'lst':fls},**e0))
		return e2
		
api.add_resource(fls,'/fls')

class auth(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self):
		if self.x.vid:
			sql='''SELECT v.name,v.team,count(p.id) as ct
				FROM visitor AS v left join propose AS p ON p.beneficiary_id=v.id
				WHERE v.id =%s and p.state='通过审核' AND p.bNew=1'''
			sam=db.session.execute(sql%self.x.vid)			
			u=[(r.name,r.team,r.ct) for r in sam]
			e0.update(self.x.had)
			return jsonify(dict({'user':u[0][0],'team':u[0][1],'ct':u[0][2]},**e0))
		return jsonify(dict(e2,**self.x.had))
		
	def post(self,id=None):
		return jsonify(dict(e0,**self.x.had))

api.add_resource(auth,'/auth/<int:id>','/auth')

class person(Resource):
	def __init__(self):
		self.x=verify(request)		
	def get(self,id):
		requestor = Visitor.query.filter_by(id=self.x.vid).first()
		tgt = Visitor.query.get(id)
		if requestor and tgt:
			if tgt.department_id and tgt.duty_id:
				if authentication(requestor,target=tgt) < 11:
					return e2
			target=visitor_schema.dump(tgt).data
			e0.update(self.x.had)
			return jsonify(dict(target,**e0))
		return e3
		
	def put(self,id):
		parser.add_argument("department_id")
		parser.add_argument("duty_id")
		parser.add_argument("name")
		parser.add_argument("tel")
		parser.add_argument("wx_sex")
		parser.add_argument("team")
		parser.add_argument("birthday")
		parser.add_argument("date_in")
		args=parser.parse_args()
		if not args["team"]:
			args["team"]=None
			
		if type(args["team"]) == str and len(args["team"])<2:
			args["team"]=None
		#print(type(args["duty_id"]))
		
		if args["department_id"]== "":
			args["department_id"]=None
		else:
			args["department_id"]=int(args["department_id"])
			
		if args["duty_id"] == "":
			args["duty_id"]=None
		else:
			args["duty_id"]=int(args["duty_id"])
			
		di=bd=None
		if args["date_in"]:
			if len(args["date_in"])>3 and len(args["date_in"])<12:
				di=args["date_in"]
				
		if args["birthday"]:
			if len(args["birthday"])>3 and len(args["birthday"])<12:
				bd=args["birthday"]
				
		if self.x.did:
			requestor = Visitor.query.filter_by(id=self.x.vid).first()
			target = Visitor.query.filter_by(id=id)
			tgt=target.first()
			department= Department.query.get(args['department_id'])
			if requestor and tgt and department:
				if tgt.department_id:
					if authentication(requestor,department=tgt.Department)!=111:
						return e2
				if authentication(requestor,department=department)!=111:
					return e2
				target.update({"department_id":args["department_id"],
					"duty_id":args["duty_id"],
					"name":args["name"],
					"tel":args["tel"],
					"wx_sex":args["wx_sex"],
					"team":args["team"],
					"birthday":bd,
					"date_in":di
				})
				db.session.commit()
				e0.update(self.x.had)
				user=visitor_schema.dump(Visitor.query.get(id)).data
				return jsonify(dict(user,**e0))
			return e3
		return e2
		
	def delete(self,id):
		if self.x.did:
			requestor = Visitor.query.filter_by(id=self.x.vid).first()
			tgt = Visitor.query.filter_by(id=id)
			target = tgt.first()
			e0.update(self.x.had)
			if target.department_id:
				if authentication(requestor,target=target) == 11:
					tgt.update({'department_id':None,'duty_id':None})
					db.session.commit()
					visitors=[{'id':v.id,'department':v.department,'duty':v.duty,'name':v.name,'wx_nickname':v.wx_nickname,'date_in':str(v.date_in),'tel':v.tel,'auth':1 if v.Department and v.Duty else 0} for v in Visitor.query.all()]
					return jsonify(dict({'lst':visitors},**e0))
				return e2
			else:
				if self.x.uid==0:
					tgt.delete()
					db.session.commit()
					visitors=[{'id':v.id,'department':v.department,'duty':v.duty,'name':v.name,'wx_nickname':v.wx_nickname,'date_in':str(v.date_in),'tel':v.tel,'auth':1 if v.Department and v.Duty else 0} for v in Visitor.query.all()]
					return jsonify(dict({'lst':visitors},**e0))
		return e2
api.add_resource(person,'/person/<int:id>')

class dashboard(Resource):
	def __init__(self):
		self.x=verify(request)		
	def get(self):
		if self.x.vid and self.x.did and self.x.tid:
			me=Visitor.query.get(self.x.vid)
			sql='''SELECT classify, sum(score) AS score FROM propose WHERE beneficiary_id=%s and state='通过审核' group BY classify;'''
			sam=db.session.execute(sql%self.x.vid)			
			sm=[{'classify':ls.classify,'score': int(ls.score)} for ls in sam]
			a=0
			aa=0
			b=0
			bb=0
			c=0
			cc=0
			for s in sm:
				if s['classify']=='A+':
					a+=int(s['score'])
				if s['classify']=='A-':
					aa+=int(s['score'])
				if s['classify']=='B+':
					b+=int(s['score'])
				if s['classify']=='B-':
					bb+=int(s['score'])
				if s['classify']=='C+':
					c+=int(s['score'])
				if s['classify']=='C-':
					cc+=int(s['score'])
			sql='''SELECT sum(score) AS score FROM propose WHERE beneficiary_id=%s and refer='S';'''
			am=db.session.execute(sql%self.x.vid)			
			sm=[int(ls.score) for ls in am]
			#print(sm)
			ss=sm[0]
			sql='''SELECT p.beneficiary_id, p.classify,SUM(p.score) AS score, v.name, v.department_id, v.duty_id, v.team FROM 
					propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id WHERE  
					1=1 AND p.state='通过审核' AND p.beneficiary_id IN (SELECT id FROM visitor WHERE 
					team=(SELECT team FROM visitor WHERE id=%s)) group BY p.beneficiary_id, p.classify;'''
			ode=db.session.execute(sql%self.x.vid)			
			odl=[{'id':o.beneficiary_id,'name':o.name,'did':o.department_id,'tid':o.duty_id,'classify':o.classify,'score':int(o.score),'team':o.team} for o in ode]
			oda=odl.copy()
			#for oa in oda:
			#	oa['tt']=0
			#	for ol in odl:				
			#		if oa['id']==ol['id'] and '+' in ol['classify']:
			#			oa['tt']+=ol['score']
			#		if oa['id']==ol['id'] and '-' in ol['classify']:
			#			oa['tt']-=ol['score']
			for oa in oda:
				oa['A']=0
				oa['B']=0
				oa['C']=0
				for ol in odl:
					if oa['id']==ol['id'] and ol['classify']=='A+':
						oa['A']+=ol['score']
					if oa['id']==ol['id'] and ol['classify']=='A-':
						oa['A']-=ol['score']
					if oa['id']==ol['id'] and ol['classify']=='B+':
						oa['B']+=ol['score']
					if oa['id']==ol['id'] and ol['classify']=='B-':
						oa['B']-=ol['score']
					if oa['id']==ol['id']and ol['classify']=='C+':
						oa['C']+=ol['score']
					if oa['id']==ol['id'] and ol['classify']=='C-':
						oa['C']-=ol['score']
			xx=[]
			yy=[]
			team=''
			dp=Department.query.all()
			dt=Duty.query.all()
			for oa in oda:
				if oa['id'] in yy:
					continue
				else:
					yy.append(oa['id'])
					#xx.append({'id':oa['id'],'name':oa['name'],'A':oa['A'],'B':oa['B'],'C':oa['C'],'did':oa['did'],'tid':oa['tid'],'tt':oa['A']+oa['B']+oa['C']})
					dept=''
					for d in dp:
						if d.id==oa['did']:
							dept=d.name
					duty=''
					for t in dt:
						if t.id==oa['tid']:
							duty=t.name
					xx.append((oa['name'],dept,duty,oa['A'],oa['B'],oa['C'],oa['A']+oa['B']+oa['C']))
					team=oa['team']
			xx=sorted(xx, key=lambda s: s[6],reverse=True)
			e0.update(self.x.had)
			return jsonify(dict({'me':{'S':ss,'A+':a,'B+':b,'C+':c,'A-':aa,'B-':bb,'C-':cc,'team':team},'summary':xx},**e0))
		return e2
		
api.add_resource(dashboard,'/dashboard')


def rgRank(ode):
	odl=[{'id':o.beneficiary_id,'name':o.name,'classify':o.classify,'score':int(o.score),'team':o.team,'rf':o.refer} for o in ode]
	oda=odl.copy()
	xx=[]
	for oa in odl:
		oa['A']=0
		oa['B']=0
		oa['C']=0
		oa['BC']=0
		oa['D']=0
		for ol in oda:
			if oa['id']==ol['id'] and ol['classify']=='A+':
				oa['A']+=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']+=ol['score']
			if oa['id']==ol['id'] and ol['classify']=='A-':
				oa['A']-=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']-=ol['score']
			if oa['id']==ol['id'] and ol['classify']=='B+':
				oa['B']+=ol['score']
				oa['BC']+=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']+=ol['score']
			if oa['id']==ol['id'] and ol['classify']=='B-':
				oa['B']-=ol['score']
				oa['BC']-=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']-=ol['score']
			if oa['id']==ol['id'] and ol['classify']=='C+':
				oa['C']+=ol['score']
				oa['BC']+=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']+=ol['score']
			if oa['id']==ol['id'] and ol['classify']=='C-':
				oa['C']-=ol['score']
				oa['BC']-=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']-=ol['score']
		oa['T']=oa['A']+oa['B']+oa['C']
		xx.append(oa)
	yy=[]
	rr=[]
	team=''
	for x in xx:
		if x['id'] in yy:
			continue
		else:
			team=x['team']
			yy.append(x['id'])
			#rr.append({'id':x['id'],'name':x['name'],'A':x['A'],'B':x['B'],'C':x['C'],'T':x['T']})
			rr.append((x['name'],x['A'],x['B'],x['C'],x['BC'],x['D'],x['T']))
	rr=sorted(rr, key=lambda x:x[5],reverse=True)
	return [rr,team]
	
class rptRank(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self):
		if self.x.vid and self.x.did and self.x.tid and self.x.uid>2:
			sql='''SELECT v.id as beneficiary_id, p.classify,SUM(p.score) AS score, v.name, v.department_id, v.duty_id, p.refer, v.team FROM 
				(SELECT id,name,department_id,duty_id,team FROM visitor WHERE team=(SELECT team FROM visitor WHERE id='''+str(self.x.vid)+''')) AS v 
				LEFT   JOIN propose AS p ON p.beneficiary_id=v.id
				WHERE DATE_FORMAT(p.create_at, '%y%m')=DATE_FORMAT(CURDATE(),'%y%m') AND p.state='通过审核'
				group BY p.beneficiary_id, p.classify, p.refer;'''
			mm=db.session.execute(sql)
			m=rgRank(mm)
			
			sq='''SELECT p.beneficiary_id, p.classify,SUM(p.score) AS score, v.name, v.department_id, v.duty_id, p.refer, v.team FROM 
				propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id WHERE DATE_FORMAT(p.create_at, '%Y')=DATE_FORMAT(CURDATE(),'%Y') AND 
				p.state='通过审核' AND p.beneficiary_id IN (SELECT id FROM visitor WHERE '''
			sql=sq+('''team=(SELECT team FROM visitor WHERE id=%s)) group BY p.beneficiary_id, p.classify, p.refer;'''%self.x.vid)
			yy=db.session.execute(sql)
			y=rgRank(yy)
			
			
			sq='''SELECT p.beneficiary_id, p.classify,SUM(p.score) AS score, p.refer, v.name, v.department_id, v.duty_id, v.team FROM 
				propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id WHERE
				p.state='通过审核' AND p.beneficiary_id IN (SELECT id FROM visitor WHERE '''
			sql=sq+('''team=(SELECT team FROM visitor WHERE id=%s)) group BY p.beneficiary_id, p.classify, p.refer;'''%self.x.vid)
			tt=db.session.execute(sql)
			t=rgRank(tt)
			
			e0.update(self.x.had)
			return jsonify(dict({'m':m[0],'y':y[0],'t':t[0],'team':m[1]},**e0))
			
		if self.x.vid and self.x.did and self.x.tid and self.x.uid<3:
			sql='''SELECT p.classify,SUM(p.score) AS score, v.name,  p.refer, v.team FROM 
				propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id WHERE DATE_FORMAT(p.create_at, '%Y%m')=DATE_FORMAT(CURDATE(),'%Y%m') AND 
				p.state='通过审核' group BY p.beneficiary_id, p.classify, p.refer; '''
			mm=db.session.execute(sql)
			m=[{'C':r.classify,'S':int(r.score),'N':r.name,'R':r.refer,'T':r.team} for r in mm]
			
			sql='''SELECT p.classify,SUM(p.score) AS score, v.name,  p.refer, v.team FROM 
				propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id WHERE DATE_FORMAT(p.create_at, '%Y')=DATE_FORMAT(CURDATE(),'%Y') AND 
				p.state='通过审核' group BY p.beneficiary_id, p.classify, p.refer; '''
			yy=db.session.execute(sql)
			y=[{'C':r.classify,'S':int(r.score),'N':r.name,'R':r.refer,'T':r.team} for r in yy]
			
			sql='''SELECT p.classify,SUM(p.score) AS score, v.name,  p.refer, v.team FROM 
				propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id WHERE p.state='通过审核' group BY p.beneficiary_id, p.classify, p.refer; '''
			tt=db.session.execute(sql)
			t=[{'C':r.classify,'S':int(r.score),'N':r.name,'R':r.refer,'T':r.team} for r in tt]
			
			e0.update(self.x.had)
			return jsonify(dict({'m':m,'y':y,'t':t},**e0))			
		return e2
api.add_resource(rptRank,'/rptrank')

def arl(db,tm):	
	rt=[]
	bb=cc=bbc=ctt=0
	for t in tm:
		t['b']=0
		t['c']=0
		t['bc']=0
		for d in db:
			if d['T']==t['n'] and d['C']=='B+':
				t['b']+=d['S']
				t['bc']+=d['S']
			if d['T']==t['n'] and d['C']=='B-':
				t['b']-=d['S']
				t['bc']-=d['S']
			if d['T']==t['n'] and d['C']=='C+':
				t['c']+=d['S']
				t['bc']+=d['S']
			if d['T']==t['n'] and d['C']=='C-':
				t['c']-=d['S']
				t['bc']-=d['S']
				
		bb=bb+t['b']
		cc=cc+t['c']
		bbc=bbc+t['b']+t['c']
		ctt=ctt+t['ct']
		rt.append([t['n'],t['ct'],t['b'],t['c'],t['bc'],round(t['bc']/t['ct'],2)])
		
	rt=sorted(rt, key=lambda x:x[5],reverse=True)
	rt.append(['汇总',ctt,bb,cc,bbc,round(bbc/ctt,2)])
	return rt
	
class aRank(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self,range,idx=None):
		if self.x.vid and self.x.did and self.x.tid:
			sql='''SELECT team, COUNT(*) as c FROM visitor  WHERE team IS NOT NULL group BY team;'''
			tm=db.session.execute(sql)
			v=[{'n':r.team,'ct':r.c} for r in tm]
			e0.update(self.x.had)
			if range=='m' and idx==0:
				sql='''SELECT p.classify,SUM(p.score) AS score,v.team FROM 
					propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id 
					WHERE DATE_FORMAT(p.create_at, '%Y%m')=DATE_FORMAT(CURDATE(),'%Y%m') AND v.team IS not NULL AND 
					p.state='通过审核' group BY v.team, p.classify; '''
				mm=db.session.execute(sql)
				m=[{'C':r.classify, 'S':int(r.score), 'T':r.team} for r in mm]
				return jsonify(dict({'list':arl(m,v)},**e0))
			
			if range=='m' and idx==1:
				rs=fast.tmRank(gCon,0,0,1)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='m' and idx==2:
				rs=fast.tmRank(gCon,0,0,2)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='m' and idx==3:
				rs=fast.tmRank(gCon,0,0,3)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='m' and idx==4:
				rs=fast.tmRank(gCon,0,0,4)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='m' and idx==5:
				rs=fast.tmRank(gCon,0,0,5)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
				
			if range=='m' and idx==6:
				rs=fast.tmRank(gCon,0,0,6)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
				
			if range=='m' and idx==7:
				rs=fast.tmRank(gCon,0,0,7)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
				
			if range=='m' and idx==8:
				rs=fast.tmRank(gCon,0,0,8)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
				
			if range=='y' and idx==0:
				sql='''SELECT p.classify,SUM(p.score) AS score, v.team FROM 
					propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id 
					WHERE DATE_FORMAT(p.create_at, '%Y')=DATE_FORMAT(CURDATE(),'%Y') AND v.team IS not NULL AND 
					p.state='通过审核' group BY v.team, p.classify; '''
				yy=db.session.execute(sql)
				y=[{'C':r.classify, 'S':int(r.score), 'T':r.team} for r in yy]
				return jsonify(dict({'list':arl(y,v)},**e0))
				
			if range=='y' and idx==1:
				rs=fast.tmRank(gCon,1,0,1)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='y' and idx==2:
				rs=fast.tmRank(gCon,1,0,2)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='y' and idx==3:
				rs=fast.tmRank(gCon,1,0,3)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='y' and idx==4:
				rs=fast.tmRank(gCon,1,0,4)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='y' and idx==5:
				rs=fast.tmRank(gCon,1,0,5)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
				
			if range=='y' and idx==6:
				rs=fast.tmRank(gCon,1,0,6)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
				
			if range=='y' and idx==7:
				rs=fast.tmRank(gCon,1,0,7)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
				
			if range=='y' and idx==8:
				rs=fast.tmRank(gCon,1,0,8)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				#f = open('tmr.csv','w',encoding='utf-8-sig',newline='')
				#w = csv.writer(f)
				##w.writerow(csh)
				#w.writerows(tm)
				#f.close()
				return jsonify(dict({'list':tm},**e0))
				
			if range=='t' and idx==0:
				sql='''SELECT p.classify,SUM(p.score) AS score, v.team FROM 
					propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id WHERE p.state='通过审核' AND v.team IS not NULL group BY v.team, p.classify; '''
				tt=db.session.execute(sql)
				t=[{'C':r.classify, 'S':int(r.score), 'T':r.team} for r in tt]				
				return jsonify(dict({'list':arl(t,v)},**e0))
			
			if range=='t' and idx==1:
				rs=fast.tmRank(gCon,2,0,1)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='t' and idx==2:
				rs=fast.tmRank(gCon,2,0,2)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='t' and idx==3:
				rs=fast.tmRank(gCon,2,0,3)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='t' and idx==4:
				rs=fast.tmRank(gCon,2,0,4)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
			
			if range=='t' and idx==5:
				rs=fast.tmRank(gCon,2,0,5)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
				
			if range=='t' and idx==6:
				rs=fast.tmRank(gCon,2,0,6)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
				
			if range=='t' and idx==7:
				rs=fast.tmRank(gCon,2,0,7)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))
				
			if range=='t' and idx==8:
				rs=fast.tmRank(gCon,2,0,8)
				tm=[(vUsers[r[6]], r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
				return jsonify(dict({'list':tm},**e0))			
		return e2
		
api.add_resource(aRank,'/arank/<string:range>','/arank/<string:range>/<int:idx>')

def tmRank(ode):
	start=time.perf_counter()
	odl=[{'id':o.beneficiary_id,'name':o.name,'classify':o.classify,'score':int(o.score),'rf':o.refer} for o in ode]
	oda=odl.copy()
	rr=[]
	yy=[]
	for oa in odl:
		if oa['id'] in yy:
			continue
		oa['A']=0
		oa['B']=0
		oa['C']=0
		oa['BC']=0
		oa['D']=0
		for ol in oda:
			if oa['id']==ol['id'] and ol['classify']=='A+':
				oa['A']+=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']+=ol['score']
			if oa['id']==ol['id'] and ol['classify']=='A-':
				oa['A']-=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']-=ol['score']
			if oa['id']==ol['id'] and ol['classify']=='B+':
				oa['B']+=ol['score']
				oa['BC']+=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']+=ol['score']
			if oa['id']==ol['id'] and ol['classify']=='B-':
				oa['B']-=ol['score']
				oa['BC']-=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']-=ol['score']
			if oa['id']==ol['id'] and ol['classify']=='C+':
				oa['C']+=ol['score']
				oa['BC']+=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']+=ol['score']
			if oa['id']==ol['id'] and ol['classify']=='C-':
				oa['C']-=ol['score']
				oa['BC']-=ol['score']
				if ol['rf'] in ['R','T','C','F']:
					oa['D']-=ol['score']
		oa['T']=oa['A']+oa['B']+oa['C']
		rr.append((oa['name'],oa['A'],oa['B'],oa['C'],oa['BC'],oa['D'],oa['T'],oa['id']))
		yy.append(oa['id'])

	rr=sorted(rr, key=lambda x:x[6],reverse=True)
	duration = time.perf_counter() - start
	#print('tmRank took {:.3f} seconds---------------------------\n\n'.format(duration))
	return rr

def nml(ar):
	arr=ar.copy()
	arr.reverse()
	d=round((arr[-1][6]-arr[0][6])/15)
	mi=arr[0][6]
	rt=[[(mi,mi+d),0]]
	for j in arr:		
		if j[6]>mi+d:
			mi+=d
			rt.append([(mi,mi+d),1])
		if j[6]<mi+d:
			rt[-1][1]+=1
	return rt
		
class tRank(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self,team,rg=None):
		if self.x.vid and self.x.did and self.x.tid:
			if team in ['先锋队','蛟龙队','雄狮队','猛虎队','战狼队','猎豹队','飞鹰队','神象队','巨猿队','海鲨队','火鸟队','蓝鲸队','骏马队','金牛队']:
				if rg=='m':
					sql='''SELECT v.id as beneficiary_id, p.classify,SUM(p.score) AS score, v.name,p.refer 
						FROM visitor  AS v LEFT JOIN propose AS p ON p.beneficiary_id=v.id
						WHERE DATE_FORMAT(p.create_at, '%y%m')=DATE_FORMAT(CURDATE(),'%y%m') AND p.state='通过审核' AND v.team="'''+team+'''"
						group BY p.beneficiary_id, p.classify, p.refer; '''
					mm=db.session.execute(sql)
					m=tmRank(mm)
					#f = open(team+'.csv','w',encoding='utf-8-sig',newline='')
					#w = csv.writer(f)
					#w.writerows(m)
					#f.close()
					e0.update(self.x.had)
					return jsonify(dict({'m':m},**e0))
				
				if rg=='y':
					sql='''SELECT p.beneficiary_id, p.classify, SUM(p.score) AS score, v.name,p.refer
						FROM propose AS p 
						LEFT JOIN visitor AS v ON p.beneficiary_id=v.id 
						WHERE DATE_FORMAT(p.create_at, '%Y')=DATE_FORMAT(CURDATE(),'%Y') AND 
						p.state='通过审核' AND v.team="'''+team+'''" 
						group BY p.beneficiary_id, p.classify, p.refer; '''
					yy=db.session.execute(sql)
					y=tmRank(yy)				
					e0.update(self.x.had)
					return jsonify(dict({'y':y},**e0))
					
				if rg=='t':
					sql='''SELECT p.beneficiary_id, p.classify,SUM(p.score) AS score, p.refer, v.name, v.department_id, v.duty_id
						FROM propose AS p 
						LEFT JOIN visitor AS v ON p.beneficiary_id=v.id 
						WHERE	p.state='通过审核' AND v.team="'''+team+'''"
						group BY p.beneficiary_id, p.classify, p.refer;'''
					tt=db.session.execute(sql)
					t=tmRank(tt)					
					e0.update(self.x.had)
					return jsonify(dict({'t':t},**e0))
			else:
				if rg=='m':
					sql='''SELECT v.id as beneficiary_id, p.classify,SUM(p.score) AS score, v.name,p.refer 
						FROM visitor  AS v LEFT   JOIN propose AS p ON p.beneficiary_id=v.id
						WHERE DATE_FORMAT(p.create_at, '%y%m')=DATE_FORMAT(CURDATE(),'%y%m') AND p.state='通过审核' AND v.team is not null
						group BY p.beneficiary_id, p.classify, p.refer; '''
					mm=db.session.execute(sql)
					m=tmRank(mm)
					mo=nml(m)
					e0.update(self.x.had)
					return jsonify(dict({'m':m[0:15],'mo':mo},**e0))
					
				if rg=='y':
					sql='''SELECT p.beneficiary_id, p.classify,SUM(p.score) AS score, v.name,p.refer
						FROM propose AS p 
						LEFT JOIN visitor AS v ON p.beneficiary_id=v.id 
						WHERE DATE_FORMAT(p.create_at, '%Y')=DATE_FORMAT(CURDATE(),'%Y') AND 
						p.state='通过审核' AND v.team is not null
						group BY p.beneficiary_id, p.classify, p.refer; '''
					yy=db.session.execute(sql)
					y=tmRank(yy)				
					yo=nml(y)
					e0.update(self.x.had)
					return jsonify(dict({'y':y[0:15],'yo':yo},**e0))
					
				if rg=='t':
					sql='''SELECT p.beneficiary_id, p.classify,SUM(p.score) AS score, p.refer, v.name, v.department_id, v.duty_id
						FROM propose AS p 
						LEFT JOIN visitor AS v ON p.beneficiary_id=v.id 
						WHERE	p.state='通过审核' AND v.team is not null
						group BY p.beneficiary_id, p.classify, p.refer;'''
					tt=db.session.execute(sql)
					t=tmRank(tt)
					to=nml(t)
					e0.update(self.x.had)
					return jsonify(dict({'t':t[0:15],'to':to},**e0))
		return e2
		
api.add_resource(tRank,'/trank/<string:team>','/trank/<string:team>/<string:rg>')

def rgSum(mo):
	a=aa=b=bb=c=cc=0
	for m in mo:
		if m.classify=='A+':
			a+=int(m.score)
		if m.classify=='B+':
			b+=int(m.score)
		if m.classify=='C+':
			c+=int(m.score)
		if m.classify=='A-':
			aa+=int(m.score)
		if m.classify=='B-':
			bb+=int(m.score)
		if m.classify=='C-':
			cc+=int(m.score)
	return {'S':a+b+c-aa-bb-cc,'A+':a,'B+':b,'C+':c,'A-':aa,'B-':bb,'C-':cc,'A':a-aa,'B':b-bb,'C':c-cc}

class mRpt(Resource):
	def __init__(self):
		self.x=verify(request)		
	def get(self,id=None):
		if self.x.vid and self.x.did and self.x.tid :
			if id==None:
				sql='''SELECT description FROM propose WHERE bNew=1 AND beneficiary_id=%s and state='通过审核' ORDER by id DESC LIMIT 5;'''
				smp=db.session.execute(sql%self.x.vid)
				sp=[r.description for r in smp]
				db.session.execute('''update propose set bNew=0 WHERE beneficiary_id=%s and bNew=1;'''%self.x.vid)
				db.session.commit()
				
				sq='''SELECT classify, sum(score) as score FROM propose WHERE DATE_FORMAT(create_at, '%Y%m')=DATE_FORMAT(CURDATE(),'%Y%m') and '''
				sql=sq+(''' beneficiary_id=%s and state='通过审核' group by classify;'''%self.x.vid)
				mo=db.session.execute(sql)
				
				sq='''SELECT classify, sum(score) as score FROM propose WHERE DATE_FORMAT(create_at, '%Y')=DATE_FORMAT(CURDATE(),'%Y') and''' 
				sql=sq+(''' beneficiary_id=%s and state='通过审核' group by classify;'''%self.x.vid)
				yo=db.session.execute(sql)
				
				sql='''SELECT classify, sum(score) as score FROM propose WHERE beneficiary_id=%s and state='通过审核' group by classify;'''
				to=db.session.execute(sql%self.x.vid)

				e0.update(self.x.had)
				return jsonify(dict({'m':rgSum(mo),'y':rgSum(yo),'t':rgSum(to),'sp':sp},**e0))
			
			else:
			#elif id==self.x.vid or self.x.uid ==5 or self.x.vid in [1,38,333]:
				#if self.x.uid==5:
				#	visitor=Visitor.query.filter_by(id=id).first()
				#	if visitor:
				#		if visitor.department_id!=self.x.did:
				#			return e2
				#	else:
				#		return e3
				sql='''SELECT classify, sum(score) as score FROM propose 
					WHERE DATE_FORMAT(create_at, '%Y%m')=DATE_FORMAT(CURDATE(),'%Y%m') AND beneficiary_id='''+str(id)+''' and state='通过审核' 
					group by classify;'''
				mo=db.session.execute(sql)
				
				sql='''SELECT classify, sum(score) as score FROM propose 
					WHERE DATE_FORMAT(create_at, '%Y')=DATE_FORMAT(CURDATE(),'%Y') AND beneficiary_id='''+str(id)+''' and state='通过审核' 
					group by classify;'''
				yo=db.session.execute(sql)
				
				sql='''SELECT P.classify, SUM(P.score) as score,V.name FROM propose AS P
					LEFT JOIN visitor AS V ON V.id=P.beneficiary_id
					WHERE P.beneficiary_id=%s AND P.state='通过审核' group BY P.classify;'''
				to=db.session.execute(sql%id)
				
				sql='''SELECT p.id,vt.NAME AS nm, p.description,p.refer-1 AS refer, p.refer_id, p.score, p.classify, p.state, p.create_at, pp.c,b.name AS bn,b.team as team
						FROM propose AS p LEFT JOIN visitor AS vt ON p.proposer_id=vt.id
						LEFT JOIN (SELECT COUNT(*) AS c,0 AS ss  FROM propose WHERE beneficiary_id=%s AND state='通过审核') AS pp ON pp.ss=0
						LEFT JOIN visitor AS b ON p.beneficiary_id=b.id
						where beneficiary_id=%s AND p.state='通过审核'
						ORDER BY create_at DESC LIMIT 0,10;'''
				lsts=db.session.execute(sql%(id,id))
				lst=[]
				name=''
				team=''
				page=0
				for r in lsts:
					lst.append({'id':r.id,'nm':r.nm,'des':r.description,'refer':r.refer,'rid':r.refer_id,'cls':r.classify,'score':r.score,'ts':str(r.create_at)})
					name=r.bn
					team=r.team
					page=r.c
				e0.update(self.x.had)
				return jsonify(dict({'m':rgSum(mo),'y':rgSum(yo),'t':rgSum(to),'lst':lst,'name':name,'page':page,'team':team},**e0))
		return e2
		
	def post(self,id=None):
		if self.x.vid:#==id or self.x.vid in [1,38,333] or self.x.uid ==5:
			if id!=None:
				#if self.x.uid==5:
				#	visitor=Visitor.query.filter_by(id=id).first()
				#	if visitor:
				#		if visitor.department_id!=self.x.did:
				#			return e2
				#	else:
				#		return e3
				parser.add_argument('index')
				args=parser.parse_args()
				sql='''SELECT p.id,vt.NAME AS nm, p.description,p.refer-1 AS refer, p.refer_id, p.score, p.classify, p.state, p.create_at
						FROM propose AS p LEFT JOIN visitor AS vt ON p.proposer_id=vt.id
						where beneficiary_id=%s AND p.state='通过审核'
						ORDER BY create_at DESC LIMIT %s,10;'''
				lsts=db.session.execute(sql%(id,args['index']))
				lst=[]
				for r in lsts:
					lst.append({'id':r.id,'nm':r.nm,'des':r.description,'refer':r.refer,'rid':r.refer_id,'cls':r.classify,'score':r.score,'ts':str(r.create_at)})
				e0.update(self.x.had)
				return jsonify(dict({'lst':lst},**e0))
			return e3
		return e2
		
api.add_resource(mRpt,'/mrpt','/mrpt/<int:id>')

class myRpt(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self,id=None):
		if self.x.vid and self.x.did and self.x.tid and id==None:
			sql='''SELECT p.beneficiary_id AS i,v.team+0 AS t , DATE_FORMAT(p.create_at,'%Y.%m') AS d, p.classify+0 AS c,SUM(p.score) AS s
			FROM propose AS p LEFT JOIN visitor AS v ON v.id=p.beneficiary_id  
			WHERE  p.state='通过审核' and DATE_FORMAT(p.create_at, '%Y')= DATE_FORMAT(curdate(), '%Y') and v.auth=1 and v.team is not null
			group BY DATE_FORMAT(p.create_at,'%Y%m'),p.classify,p.beneficiary_id ORDER BY p.create_at,p.beneficiary_id;'''
			smp=db.session.execute(sql)
			sp=[(r.i, r.t, r.d, r.c, int(r.s)) for r in smp]
			#[(id,team,date,a,b,c,sum),...]
			#'A+','B+','C+','A-','B-','C-'
			me={'id':self.x.vid,'team':0,'a':0,'a-':0,'b':0,'b-':0,'c':0,'c-':0,'r':1,'tr':1}
			tp=[]
			lst=[]
			mh=datetime.datetime.now().month
			cdt=str(datetime.datetime.now().year)+"."+('0'+str(mh) if mh<10 else str(mh))
			for r in sp:					
				if r[0]==me['id'] and r[2]==cdt:
					me['team']=r[1]
					if r[3]==1:
						me['a']+=r[4]
					if r[3]==2:
						me['b']+=r[4]
					if r[3]==3:
						me['c']+=r[4]
					if r[3]==4:
						me['a-']+=r[4]
					if r[3]==5:
						me['b-']+=r[4]
					if r[3]==6:
						me['c-']+=r[4]
				if str(r[0])+r[2] in tp:
					continue
				a=0
				b=0
				c=0					
				for rr in sp:
					if r[0]==rr[0] and r[2]==rr[2]:
						if rr[3]==1:
							a+=rr[4]
						if rr[3]==2:
							b+=rr[4]
						if rr[3]==3:
							c+=rr[4]  
						if rr[3]==4:
							a-=rr[4]  
						if rr[3]==5:
							b-=rr[4]  
						if rr[3]==6:
							c-=rr[4]								
				lst.append((r[0],r[1],r[2],a,b,c,a+b+c))
				tp.append(str(r[0])+r[2])

			a=me['a'] - me['a-']
			b=me['b'] - me['b-']
			c=me['c'] - me['c-']
			s=a+b+c
			ax=[]
			ay=[]
			by=[]
			cy=[]
			sy=[]
			aty=[]
			bty=[]
			cty=[]
			sty=[]
			av=[]
			bv=[]
			cv=[]
			sv=[]
			
			bl=[]
			tbl=[]

			for r in lst:
				if r[2]==cdt :
					if r[0]==me['id']:
						continue
					if r[6]>s:							
						if r[6] not in bl:
							bl.append(r[6])
							me['r']+=1
						if r[1]==me['team'] and r[6] not in tbl:
							tbl.append(r[6])
							me['tr']+=1
				if r[0] != me['id']:
					continue
				
				ar=1
				at=1
				br=1
				bt=1
				cr=1
				ct=1
				sr=1
				st=1
				ax.append(r[2])
				for rr in lst:
					if r[0]==rr[0]:
						continue
					if r[2]==rr[2]:
						if rr[3]>r[3]:
							ar+=1
							if r[1]==rr[1]:
								at+=1
						if rr[4]>r[4]:
							br+=1
							if r[1]==rr[1]:
								bt+=1
						if rr[5]>r[5]:
							cr+=1
							if r[1]==rr[1]:
								ct+=1
						if rr[6]>r[6]:
							sr+=1
							if r[1]==rr[1]:
								st+=1
				av.append(r[3])
				bv.append(r[4])
				cv.append(r[5])
				sv.append(r[6])
				
				ay.append(ar)
				by.append(br)
				cy.append(cr)
				sy.append(sr)
				
				aty.append(at)
				bty.append(bt)
				cty.append(ct)
				sty.append(st)
			sql='''SELECT description FROM propose WHERE bNew=1 AND beneficiary_id=%s and state='通过审核' ORDER by id DESC LIMIT 5;'''
			smp=db.session.execute(sql%self.x.vid)
			sp=[r.description for r in smp]
			db.session.execute('''update propose set bNew=0 WHERE beneficiary_id=%s and bNew=1 and state='通过审核';'''%self.x.vid)
			db.session.commit()
			
			e0.update(self.x.had)
			return jsonify(dict({'me':me, 'ax':ax, 'ay':(av, bv, cv, sy, sty), 'sp':sp},**e0))
			#return jsonify(dict({'me':me,'ax':ax,'ry':(ay,by,cy,sy),'try':(aty,bty,cty,sty),'vy':(av,bv,cv,sv),'sp':sp},**e0))
		return e2
api.add_resource(myRpt,'/myrpt','/mrpt/<int:id>')

def npcd(mo):
	n=p=c=0
	for m in mo:
		c=c+1
		if m.classify=='A+':
			p+=int(m.score)
		if m.classify=='B+':
			p+=int(m.score)
		if m.classify=='C+':
			p+=int(m.score)
		if m.classify=='A-':
			n+=int(m.score)
		if m.classify=='B-':
			n+=int(m.score)
		if m.classify=='C-':
			n+=int(m.score)
	return {'C':c,'N':n,'P':p}
	
class tstate(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self):
		if self.x.vid and self.x.did and self.x.uid>2:
			md=Duty.query.get(self.x.tid)
			md=duty_schema.dump(md).data
			
			sq='''SELECT classify, score FROM propose WHERE DATE_FORMAT(create_at, '%Y%m%d')=DATE_FORMAT(CURDATE(),'%Y%m%d') AND state='通过审核' AND '''
			sql=sq+('''proposer_id=%s and beneficiary_id!=%s; '''%(self.x.vid,self.x.vid))
			d=db.session.execute(sql)
			
			sq='''SELECT classify, score FROM propose WHERE DATE_FORMAT(create_at, '%Y%m')=DATE_FORMAT(CURDATE(),'%Y%m') AND state='通过审核' AND '''
			sql=sq+('''proposer_id=%s and beneficiary_id!=%s;'''%(self.x.vid,self.x.vid))
			m=db.session.execute(sql)
			
			sq='''SELECT classify, score FROM propose WHERE YEARWEEK(DATE_FORMAT(create_at,'%Y-%m-%d')) = YEARWEEK(NOW()) AND state='通过审核' AND '''
			sql=sq+('''proposer_id=%s and beneficiary_id!=%s;'''%(self.x.vid,self.x.vid))
			w=db.session.execute(sql)
			
			e0.update(self.x.had)
			return jsonify(dict({'duty':md, 'd':npcd(d), 'w':npcd(w), 'm':npcd(m) },**e0))
		if self.x.vid and self.x.did and self.x.uid<3:
			#sql='''SELECT v.id,v.name , p.name AS dpt,d.name AS duty, d.wn_min,d.wp_min,d.dc_min,d.mp_max,
			#	sum(ps.score) AS s ,ps.classify as c, DATE_FORMAT(ps.create_at, '%Y-%m-%d') AS ca from visitor AS v 
			#	inner JOIN duty AS d ON v.duty_id=d.id
			#	inner JOIN department AS p ON v.department_id=p.id
			#	LEFT JOIN propose AS ps ON v.id=proposer_id
			#	WHERE d.role IN (3,4,5) AND ps.state='通过审核'
			#	group BY v.id ,ps.classify, DATE_FORMAT(ps.create_at, '%Y%m%d');'''
			#sc=db.session.execute(sql)
			#lst=[{'id':r.id,'n':r.name,'d':r.dpt, 't':r.duty,'wni':r.wn_min,'wpi':r.wp_min,'dci':r.dc_min,'mpa':r.mp_max,'s':r.s,'c':r.c,'dt':r.ca} for r in sc]
			
			sql='''SELECT v.id,v.name , p.name AS dpt,d.name AS duty, d.wn_min,d.wp_min,d.dc_min,d.mp_max,d.mp_min,d.mn_min from visitor AS v 
				inner JOIN duty AS d ON v.duty_id=d.id
				inner JOIN department AS p ON v.department_id=p.id
				WHERE d.role IN (2,3,4,5,6) order by d.role; '''
			sc=db.session.execute(sql)
			lst=[{'id':r.id,'n':r.name,'d':r.dpt, 't':r.duty,'wni':r.wn_min,'wpi':r.wp_min,'dci':r.dc_min,'mpa':r.mp_max,'mpi':r.mp_min,'mni':r.mn_min} for r in sc]			
			sql='''SELECT v.id, ps.score ,ps.classify, DATE_FORMAT(ps.create_at, '%Y-%m-%d') AS ca from visitor AS v 
				inner JOIN duty AS d ON v.duty_id=d.id
				LEFT JOIN propose AS ps ON v.id=proposer_id
				WHERE d.role IN (2,3,4,5,6) AND ps.state='通过审核' AND ps.beneficiary_id!=ps.proposer_id
				order by d.role;'''
				
			ps=db.session.execute(sql)
			pos=[(r.id,r.score,r.classify,r.ca) for r in ps]
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst,'pos':pos},**e0))
		return e2
api.add_resource(tstate,'/tstate')

class register(Resource):	
	def post(self):
		parser.add_argument('name')
		parser.add_argument('passwd')
		parser.add_argument('tel')
		args=parser.parse_args()
		if "name" in args and "passwd" in args and "tel" in args:
			#vst=Visitor.query.filter(and_(Visitor.name == args["name"], Visitor.department == args["department"])).first()
			vst=Visitor.query.filter_by(tel=args["tel"]).first()
			if vst:
				return e28			
			pwd=hashlib.md5(args["passwd"].encode()).hexdigest()
			sql='''insert into visitor(name,passwd,tel) value('%s','%s','%s')'''
			db.session.execute(sql%(args["name"],pwd,args["tel"]))
			db.session.commit()
			ist=Visitor.query.filter(and_(Visitor.tel == args["tel"], Visitor.passwd == pwd)).first()
			if ist:
				had={'xtoken':None,'vid':None,'uid':None,'did':None,'tid':None}
				had['vid']=ist.id
				had['xtoken']=str(jwt.encode({'vid':ist.id,'did':None,'tid':None,'uid':None,'iat': time.time()+1200}, cfg['SECRET_KEY'], algorithm='HS256'),'utf-8')
				e0.update(had)
				return jsonify(dict({'name':args["name"],'passwd':'','tel':args["tel"]},**e0))
			return e1
		return e2
api.add_resource(register,'/register')

class login(Resource):
	def post(self):
		parser.add_argument('name')
		parser.add_argument('passwd')
		parser.add_argument('tel')
		args=parser.parse_args()
		rst=vResult(had={'xtoken':None,'vid':None,'uid':None,'did':None,'tid':None})
		if ("name" in args or "tel" in args) and "passwd" in args: 			 
			if len(args["passwd"])<5:
				return e29
			passwd=hashlib.md5(args["passwd"].encode()).hexdigest()
			name=args["name"] if args["name"]!="" else None
			tel=args["tel"] if args["tel"]!="" else None
			sql="select v.*,d.role from visitor as v left join duty as d on v.duty_id=d.id where v.name='%s' or v.tel='%s';"			
			users=db.session.execute(sql%(name,tel))
			visitor=None
			ht=0
			for us in users:				
				if us.passwd==passwd and us.tel==tel:
					visitor=us
					break
				if us.passwd==passwd and us.name==name:
					visitor=us
					ht+=1
			if ht>1:
				return jsonify(e39)
			if visitor:
				rst.vid=visitor.id
				rst.did=visitor.department_id if visitor.department_id else None
				rst.tid=visitor.duty_id if visitor.duty_id else None
				rst.uid=visitor.role 
				rst.had['xtoken']=str(jwt.encode({'vid':visitor.id,
					'did':visitor.department_id if visitor.department_id else None,
					'tid':visitor.duty_id if visitor.duty_id else None,
					'uid':visitor.role,
					'iat': time.time()+1200}, cfg['SECRET_KEY'], algorithm='HS256'),'utf-8')
				rst.had['vid']=visitor.id
				rst.had['uid']=visitor.role 
				rst.had['did']=visitor.department_id if visitor.department_id else None
				rst.had['tid']=visitor.duty_id if visitor.duty_id else None
				e0.update(rst.had)
				return jsonify(dict({'name':visitor.name, 'tel':visitor.tel},**e0))
			return jsonify(e40)
		return e8		
api.add_resource(login,'/login')

class login2(Resource):
	def get(self):
		xtoken=request.headers.get('xtoken')
		if xtoken and xtoken !='undefined' and xtoken !='null':
			mtoken={}
			try:
				mtoken=jwt.decode(bytes(xtoken, 'utf-8'), cfg['SECRET_KEY'], algorithms=['HS256'],options={'verify_iat': False})			
			except Exception as e:
				return jsonify(e39)
			visitor=Visitor.query.get(mtoken['vid'])
			if visitor:
				rst={
					'error':0,
					'msg':'登录成功。',
					'vid':visitor.id,
					'name':visitor.name, 
					'tel':visitor.tel,
					'team':visitor.team,				
				}				
				if visitor.Department and visitor.Duty:
					rst['did']=visitor.department_id
					rst['tid']=visitor.duty_id
					rst['uid']=visitor.Duty.role
					rst['token']=str(jwt.encode({'vid':visitor.id,
						'did':visitor.department_id if visitor.department_id else None,
						'tid':visitor.duty_id if visitor.duty_id else None,
						'uid':visitor.Duty.role,
						'iat': time.time()+1200}, cfg['SECRET_KEY'], algorithm='HS256'),'utf-8')
				return jsonify(rst)
		return jsonify(e39)

	def post(self):
		parser.add_argument('user')
		parser.add_argument('passwd')
		args=parser.parse_args()
		if "user" in args and "passwd" in args: 			 
			if len(args["passwd"])<5:
				return e29
			passwd=hashlib.md5(args["passwd"].encode()).hexdigest()
			user=args["user"]
			sql="select v.*,d.role from visitor as v left join duty as d on v.duty_id=d.id where v.name='%s' or v.tel='%s';"			
			users=db.session.execute(sql%(user,user))
			visitor=None
			ht=0
			for us in users:				
				if us.passwd==passwd and us.tel==user:
					visitor=us
					break
				if us.passwd==passwd and us.name==user:
					visitor=us
					ht+=1
			if ht>1:
				return jsonify(e39)
			if visitor:
				rst={
					'error':0,
					'msg':'登录成功。',
					'vid':visitor.id,
					'did':visitor.department_id,
					'tid':visitor.duty_id,
					'uid':visitor.role,
					'name':visitor.name, 
					'tel':visitor.tel,
					'team':visitor.team,
					'token':str(jwt.encode({'vid':visitor.id,
						'did':visitor.department_id if visitor.department_id else None,
						'tid':visitor.duty_id if visitor.duty_id else None,
						'uid':visitor.role,
						'iat': time.time()+1200}, cfg['SECRET_KEY'], algorithm='HS256'),'utf-8')
				}				
				return jsonify(rst)
				
			return jsonify(e40)
		return e8
		
	def put(self):
		parser.add_argument('name')
		parser.add_argument('tel')
		parser.add_argument('passwd')
		parser.add_argument('passwdO')
		args=parser.parse_args()
		xtoken=request.headers.get('xtoken')
		if xtoken and xtoken !='undefined' and xtoken !='null':
			mtoken={}
			try:
				mtoken=jwt.decode(bytes(xtoken, 'utf-8'), cfg['SECRET_KEY'], algorithms=['HS256'],options={'verify_iat': False})			
			except Exception as e:
				return jsonify(e41)
			visitor=Visitor.query.filter_by(id=mtoken['vid'])
			if visitor:
				vst=visitor.first()
				pw=hashlib.md5(args["passwd"].encode()).hexdigest()
				pw2=hashlib.md5(args["passwdO"].encode()).hexdigest()
				if pw2==vst.passwd:
					vtl=Visitor.query.filter_by(tel=args['tel']).all()
					for tl in vtl:
						if tl.tel==args['tel'] and tl.id!=mtoken['vid']:
							return jsonify(e43)
					upd=visitor.update({'name':args['name'],'tel':args['tel'],'passwd':pw})
					db.session.commit()
					rst={
						'error':0,
						'msg':'修改成功,请重新登录。',
						'vid':vst.id,
						'name':args['name'], 
						'tel':args['tel'],
						'team':vst.team,
					}
					if vst.Department and vst.Duty:
						rst['did']=vst.department_id
						rst['tid']=vst.duty_id
						rst['uid']=vst.Duty.role
						rst['token']=str(jwt.encode({'vid':vst.id,
							'did':vst.department_id if vst.department_id else None,
							'tid':vst.duty_id if vst.duty_id else None,
							'uid':vst.Duty.role,
							'iat': time.time()+1200}, cfg['SECRET_KEY'], algorithm='HS256'),'utf-8')
					return jsonify(rst)
				return jsonify(e42)
		return jsonify(e41)
		
api.add_resource(login2,'/login2')

class authorization(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self,id):
		if self.x.uid==0 and id >0:
			vst=Visitor.query.get(id)			
			sql='''SELECT id,department_id AS did,duty_id AS tid,team AS t,title AS tt, sex AS s,education AS e, `name` AS n,tel,secrity AS sc,
			`level` AS lv, date_in as di, birthday as bd, wx_headimgurl as avatar from employee WHERE 
			tel=(select tel from visitor where id=%s) limit 1; '''%(id)
			if vst.auth==1:
				sql='''SELECT id,department_id AS did,duty_id AS tid,team AS t,title AS tt, sex AS s,education AS e, `name` AS n,tel,secrity AS sc,
				`level` AS lv, date_in as di, birthday as bd, wx_headimgurl as avatar from visitor WHERE id=%s; '''%(id)
			aus=db.session.execute(sql)
			prf=[{'id':r.id, 'did':r.did, 'tid':r.tid, 't':r.t, 'tt':r.tt, 's':r.s, 'e':r.e, 'n':r.n, 'tel':r.tel,'sc':r.sc,'lv':r.lv,'di':str(r.di),'bd':str(r.bd),'avatar':r.avatar,'pwd':''} for r in aus]
			prf=prf[0] if len(prf)>0 else {'id':None, 'did':None, 'tid':None, 't':None, 'tt':None, 's':None, 'e':None, 'n':None, 'tel':None,'sc':None,'lv':None,'di':None,'bd':None,'avatar':None,'pwd':''}
			sql='''select id, name from department order by CONVERT(name USING GB2312)'''
			dpt=db.session.execute(sql)
			dpt=[{'id':r.id,'name':r.name} for r in dpt]
			sql='''select id, name from duty order by CONVERT(name USING GB2312)'''
			dt=db.session.execute(sql)
			duty=[{'id':r.id,'name':r.name} for r in dt]
			e0.update(self.x.had)
			return jsonify(dict({'vst':{'n':vst.name,'tel':vst.tel,'avatar':vst.wx_headimgurl},'prf':prf,'dpt':dpt,'duty':duty},**e0))
		return e2
	
	def put(self,id):
		if self.x.uid==0 and id>0:
			parser.add_argument('id')
			parser.add_argument('did')
			parser.add_argument('tid')
			parser.add_argument('t')
			parser.add_argument('tt')
			parser.add_argument('s')
			parser.add_argument('e')
			parser.add_argument('n')
			parser.add_argument('tel')
			parser.add_argument('sc')
			parser.add_argument('lv')
			parser.add_argument('di')
			parser.add_argument('bd')
			parser.add_argument('pwd')
			args=parser.parse_args()
#			print(args,'---------------------------------------------')
#			if args['tel']:
#				sql='''update employee set auth=1 where tel=%s;'''
#				db.session.execute(sql%args['tel'])
#			breg=Visitor.query.filter_by(tel=args['tel']).first()
#			if breg:
#				return e31
			if args['tt'] not in ['高级','中级','初级']:
				args['tt']=None
			if args['did'] is None or args['tid'] is None or args['n'] is None:
				return e32
			if len(args['pwd'])>5:
				pwd=hashlib.md5(args['pwd'].encode()).hexdigest()
				Visitor.query.filter_by(id=id).update({'auth':1,'department_id':args['did'],'duty_id':args['tid'],'team':args['t'],'title':args['tt'], 'sex':args['s'],'education':args['e'], 'name':args['n'], 'tel':args['tel'],'secrity':args['sc'],'level':args['lv'],'date_in':args['di'],'birthday':args['bd'],'passwd':pwd})
			else:
				Visitor.query.filter_by(id=id).update({'auth':1,'department_id':args['did'],'duty_id':args['tid'],'team':args['t'],'title':args['tt'], 'sex':args['s'],
					'education':args['e'], 'name':args['n'], 'tel':args['tel'],'secrity':args['sc'],'level':args['lv'],'date_in':args['di'],'birthday':args['bd']})
			db.session.commit()
			e0.update(self.x.had)
			return e0
		return e2
		
	def delete(self,id):
		if self.x.uid==0:
			tgt = Visitor.query.filter_by(id=id)
			target = tgt.first()
			e0.update(self.x.had)			
			#if target.auth==1 and target.department_id and target.duty_id:
			if target:
				tgt.update({'department_id':None,'duty_id':None,'auth':0})
				db.session.commit()
				sql='''select v.*,d.name as dept,t.NAME AS duty from visitor as v left join department as d on v.department_id=d.id LEFT JOIN duty AS t 
				ON v.duty_id=t.id where v.auth=1;'''
				vs=db.session.execute(sql)
				visitors=[{'id':v.id,'name':v.name,'department':v.dept,'duty':v.duty,'tel':v.tel} for v in vs]
				return jsonify(dict({'lst':visitors},**e0))
			#else:
			#	tgt.delete()
			#	db.session.commit()
			#	sql='''select v.*,d.name as dept,t.NAME AS duty from visitor as v left join department as d on v.department_id=d.id LEFT JOIN duty AS t 
			#	ON v.duty_id=t.id where v.auth=0;'''
			#	vs=db.session.execute(sql)
			#	visitors=[{'id':v.id,'department':v.dept,'duty':v.duty,'name':v.name,'tel':v.tel} for v in vs]
			#	return jsonify(dict({'lst':visitors},**e0))
		return e2
api.add_resource(authorization,'/authorization/<int:id>')

class company(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self,idt):
		if self.x.uid==0:
			visitors=[]
			if idt==0:
				sql='''select v.*,d.name as dept,t.NAME AS duty,v.team from visitor as v left join department as d on v.department_id=d.id LEFT JOIN duty AS t 
				ON v.duty_id=t.id where v.auth=0;'''
				vs=db.session.execute(sql)
				visitors=[{'id':v.id,'name':v.name,'department':v.dept,'duty':v.duty,'tel':v.tel} for v in vs]
			if idt==1:
				sql='''select v.*,d.name as dept,t.NAME AS duty,v.team from visitor as v left join department as d on v.department_id=d.id LEFT JOIN duty AS t 
				ON v.duty_id=t.id where v.auth=1;'''
				vs=db.session.execute(sql)
				visitors=[{'id':v.id,'name':v.name,'department':v.dept,'duty':v.duty,'tel':v.tel,'team':v.team} for v in vs]
			dept=departments_schema.dump(Department.query.all()).data
			duty=duties_schema.dump(Duty.query.all()).data
			e0.update(self.x.had)
			return jsonify(dict({'dept':dept,'duty':duty,'lst':visitors},**e0))
		return e2

api.add_resource(company,'/company/<int:idt>')

class live(Resource):
	def get(self,id):
		#sql='''SELECT v.NAME AS name,v.team AS team,p.refer+0 AS refer,p.description,p.classify,p.score,p.create_at 
		#	FROM propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id 
		#	WHERE v.department_id=%s AND p.refer_id !='S' AND p.create_at>NOW()-INTERVAL 48 HOUR;'''
		#sql='''SELECT v.NAME AS name,v.team AS team,p.refer+0 AS refer,p.description,p.classify,p.score,p.create_at,vp.name AS vpn,rl.serial
		#	FROM propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id
		#	LEFT JOIN visitor AS vp ON p.proposer_id=vp.id
		#	LEFT JOIN rule AS rl ON p.refer_id=rl.id
		#	WHERE p.id >34605 AND p.proposer_id=334 ORDER BY p.create_at desc '''
		#lvs=db.session.execute(sql)
		vs=''
		if id=='0':
			sql='''SELECT v.NAME AS name,v.team AS team,p.refer+0 AS refer,p.description,p.classify,p.score,p.create_at,vp.name AS vpn,rl.serial
			FROM propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id
			LEFT JOIN visitor AS vp ON p.proposer_id=vp.id
			LEFT JOIN rule AS rl ON p.refer_id=rl.id
			WHERE p.refer !='S' AND p.state='通过审核' ORDER BY p.create_at desc limit 50;'''
			lvs=db.session.execute(sql)
		else:
			ids='('+id.replace('_',',')+')'
			sql='''SELECT v.NAME AS name,v.team AS team,p.refer+0 AS refer,p.description,p.classify,p.score,p.create_at,vp.name AS vpn,rl.serial
				FROM propose AS p LEFT JOIN visitor AS v ON p.beneficiary_id=v.id
				LEFT JOIN visitor AS vp ON p.proposer_id=vp.id
				LEFT JOIN rule AS rl ON p.refer_id=rl.id
				WHERE v.department_id in %s AND p.refer !='S' AND p.state='通过审核'  ORDER BY p.create_at desc limit 40;'''
				
			lvs=db.session.execute(sql%ids)			
		db.session.commit()
		lst=[(l.name,l.team,l.refer,l.description,l.vpn,l.classify+str(l.score),str(l.create_at).split(' ')[0][5:].replace('-','/'),l.serial) for l in lvs]
		return jsonify(dict({'lst':lst},**e0))

api.add_resource(live,'/live/<string:id>')

class schedule(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self,id):
		if self.x.uid==0:
			sql='''SELECT s.*,v.name as name from schedule as s left join visitor as v ON s.creater_id=v.id;'''
			lvs=db.session.execute(sql)
			db.session.commit()
			lst=[{"id":l.id,"name":l.name,"sc":l.score,"st":l.classify,"prd":l.period,"en":l.enable,"tt":l.title,"desc":l.description,"bnf":l.beneficiary,"cat":str(l.create_at).split(' ')[0]} for l in lvs]
			visitors=Visitor.query.all()
			pps=[]
			for vt in visitors:
				if vt.Department and vt.Duty:
					pps.append((vt.id,vt.Department.name,vt.Duty.name,vt.name))
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst,'pps':pps},**e0))
		return e2

	def post(self,id):
		if self.x.uid==0:
			parser.add_argument('tt')
			parser.add_argument('desc')
			parser.add_argument('st')
			parser.add_argument('sc')
			parser.add_argument('prd')
			parser.add_argument('benf')
			args = parser.parse_args()
			#print(args)
			if args['st'] not in ['A+','B+','C+','A-','B-','C-']:
				return e8
			if args['prd'] not in ['每天','每月','每年']:
				return e8
			try:
				score=int(args['sc'])			
			except Exception as e:
				return e8

			Sche = Schedule(
				beneficiary=args['benf'], 
				title=args['tt'],
				description=args['desc'], 
				classify=args['st'],
				score=int(args['sc']), 
				creater_id=self.x.vid,
				period=args['prd'])
			db.session.add(Sche)
			db.session.commit()

			sql='''SELECT s.*,v.name as name from schedule as s left join visitor as v ON s.creater_id=v.id;'''
			lvs=db.session.execute(sql)
			lst=[{"id":l.id,"name":l.name,"sc":l.score,"st":l.classify,"prd":l.period,"en":l.enable,"tt":l.title,"desc":l.description,"bnf":l.beneficiary,"cat":str(l.create_at).split(' ')[0]} for l in lvs]
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst},**e0))
		return e2
	
	def put(self,id):
		if self.x.uid==0:
			parser.add_argument('st')
			parser.add_argument('sc')
			parser.add_argument('prd')
			parser.add_argument('benf')
			parser.add_argument('en')
			args = parser.parse_args()
			
			if args['st'] not in ['A+','B+','C+','A-','B-','C-']:				
				return e8
			if args['prd'] not in ['每天','每月','每年']:
				return e8
			try:
				en=int(args['en'])
				if en not in [0,1]:
					return e8
				score=int(args['sc'])			
			except Exception as e:
				return e8
			Schedule.query.filter_by(id=id).update({"score":int(args['sc']) ,"classify":args['st'],"period":args['prd'] ,"enable" :int(args['en']),"beneficiary":args['benf']})
			db.session.commit()

			sql='''SELECT s.*,v.name as name from schedule as s left join visitor as v ON s.creater_id=v.id;'''
			lvs=db.session.execute(sql)
			lst=[{"id":l.id,"name":l.name,"sc":l.score,"st":l.classify,"prd":l.period,"en":l.enable,"tt":l.title,"desc":l.description,"bnf":l.beneficiary,"cat":str(l.create_at).split(' ')[0]} for l in lvs]
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst},**e0))
		return e2
		
	def delete(self,id):
		if self.x.uid==0:
			Schedule.query.filter_by(id=id).delete()
			db.session.commit()
			sql='''SELECT s.*,v.name as name from schedule as s left join visitor as v ON s.creater_id=v.id;'''
			lvs=db.session.execute(sql)
			lst=[{"id":l.id,"name":l.name,"sc":l.score,"st":l.classify,"prd":l.period,"en":l.enable,"tt":l.title,"desc":l.description,"bnf":l.beneficiary,"cat":str(l.create_at).split(' ')[0]} for l in lvs]
			e0.update(self.x.had)
			return jsonify(dict({'lst':lst},**e0))
		return e2
		
api.add_resource(schedule,'/schedule/<int:id>')

class show(Resource):
	def get(self):
		sql='''SELECT v.team,v.dept,v.n,p.score FROM propose AS p LEFT JOIN (
				SELECT v.id,v.NAME AS n,d.NAME AS dept,v.team  FROM visitor AS v LEFT JOIN department AS d ON v.department_id=d.id
				) AS v ON v.id=p.beneficiary_id WHERE p.proposer_id=1 order by create_at desc;'''
		shs=db.session.execute(sql)
		lst=[]
		tms=[]
		pss=[]
		tps=[]
		ctd=0
		for sh in shs:			
			if ctd<7:
				lst.append((sh.dept,sh.n,sh.score))
				ctd+=1
			
			bt=False
			for tm in tms:
				if tm[0]==sh.team:
					tm[1]+=sh.score
					tm[2]+=1
					bt=True
			if not bt:
				tms.append([sh.team,sh.score,1])
				
			bp=False
			for ps in pss:
				if ps[0]==sh.n:
					ps[1]+=sh.score
					bp=True
			if not bp:
				pss.append([sh.n,sh.score])
			
			bs=False
			for tp in tps:
				if tp[0]==sh.team and tp[1]==sh.n:
					tp[2]+=sh.score
					bs=True
			if not bs:
				tps.append([sh.team, sh.n, sh.score])

		rts=[]
		for tp in tps:
			bs=False
			for rt in rts:				
				if rt[0]==tp[0]:
					bs=True
					if tp[2]>rt[1][1]:						
						rt[3][0]=rt[2][0]
						rt[3][1]=rt[2][1]
						
						rt[2][0]=rt[1][0]
						rt[2][1]=rt[1][1]
						
						rt[1][0]=tp[1]
						rt[1][1]=tp[2]
						continue
						
					if tp[2]>rt[2][1]:					
						rt[3][0]=rt[2][0]
						rt[3][1]=rt[2][1]
						
						rt[2][0]=tp[1]
						rt[2][1]=tp[2]
						continue
						
					if tp[2]>rt[3][1]:
						rt[3][0]=tp[1]
						rt[3][1]=tp[2]
						
			if bs==False:
				rts.append([tp[0], [tp[1],tp[2]], ['',0],['',0]])

		tms=[(t[0],round(t[1]/t[2]),t[1]) for t in tms]
		tms=sorted(tms, key = lambda x: x[1],reverse=True)
		pss=sorted(pss, key = lambda x: x[1],reverse=True)
		return jsonify({'lst':lst, 'tms':tms, 'pss':pss[:10], 'rts':rts})
		
api.add_resource(show,'/show')

class export(Resource):
	def __init__(self):
		self.x=verify(request)
	def put(self):
		if self.x.uid!=0:
			return e2
		parser.add_argument('exp')
		args = parser.parse_args()
		exp=json.loads(args['exp'])
		s=''
		csh=[]
		if exp["pid"]:
			s+='V.id as pid,'
			csh.append('提交人编号')
		if exp["pn"]:
			s+='V.name as pn,'
			csh.append('提交')
		if exp["dpt"]:
			s+='pd.name asdpt,'
			csh.append('提交人部门')
		if exp["dut"]:
			s+='pt.name as dut,'
			csh.append('提交人职务')
		if exp["tm"]:
			s+='V.team as tm,'
			csh.append('提交人团队')
		if exp["tt"]:
			s+='V.title as tt,'
			csh.append('提交人职称')
		if exp["sex"]:
			s+='V.sex as sex,'
			csh.append('提交人性别')
		if exp["edu"]:
			s+='V.education as edu,'
			csh.append('提交人学历')
		if exp["lv"]:
			s+='V.level as lv,'
			csh.append('提交人工资级别')
		if exp["di"]:
			s+='V.date_in as di,'
			csh.append('提交人入职日期')
		if exp["dt"]:
			s+='V.birthday as dt,'
			csh.append('提交人出生日期')
		if exp["bid"]:
			s+='V.id as bid,'
			csh.append('奖扣对象编号')
		if exp["bpn"]:
			s+='B.name as bpn,'
			csh.append('奖扣对象')
		if exp["bdpt"]:
			s+='bd.name as bdpt,'
			csh.append('奖扣对象部门')
		if exp["bdut"]:
			s+='bt.name as bdut,'
			csh.append('奖扣对象职务')
		if exp["btm"]:
			s+='B.team as btm,'
			csh.append('奖扣对象团队')
		if exp["btt"]:
			s+='B.title as btt,'
			csh.append('奖扣对象职称')
		if exp["bsex"]:
			s+='B.sex as bsex,'
			csh.append('奖扣对象性别')
		if exp["bedu"]:
			s+='B.education as bedu,'
			csh.append('学历')
		if exp["blv"]:
			s+='B.level as blv,'
			csh.append('奖扣对象工资级别')
		if exp["bdi"]:
			s+='B.date_in as bdi,'
			csh.append('奖扣对象入职日期')
		if exp["bdt"]:
			s+='B.birthday as bdt,'
			csh.append('奖扣对象出生日期')
		if exp["ru"]:
			s+='RL.description as ru,'
			csh.append('应用条款')
		if exp["ser"]:
			s+='RL.serial as ser,'
			csh.append('条款编号')
		if exp["cls"]:
			s+='P.classify as cls,'
			csh.append('积分类别')
		if exp["sc"]:
			s+='P.score as sc,'
			csh.append('积分')
		if exp["rf"]:
			s+='''case P.refer when 'R' then '积分规则' when 'T' then '完成任务' when 'S' then '固定积分' when 'C' then '权限奖扣' when 'F' then '无奖券奖扣' ELSE  '未知类型' END as rf,'''
			csh.append('奖扣类型')
		if exp["apv"]:
			s+='P.state as apv,'
			csh.append('审核进度')
		if exp["des"]:
			s+='P.description as des,'
			csh.append('事件描述')
		if exp["aps"]:
			s+='P.commit as aps,'
			csh.append('审核意见')
		if exp["apl"]:
			s+='P.appeal as apl,'
			csh.append('复议理由')
		if exp["at"]:
			s+='P.create_at as at,'
			csh.append('提交时间')
		
		rgs=''
		if exp["from"]!='' and exp["to"]!='':
			rgs=" and create_at BETWEEN '"+exp["from"]+"' and '"+exp["to"]+" 23:59:59'"
		else:
			if exp["from"]!='':
				rgs=" and create_at>'"+exp["from"]+"'"
			if exp["to"]!='':
				rgs=" and create_at<'"+exp["to"]+" 23:59:59'"
		sql='''SELECT %s FROM propose AS P
			LEFT JOIN visitor AS V ON V.id=P.proposer_id
			LEFT JOIN (SELECT v.id,d.NAME FROM visitor AS v LEFT JOIN department AS d ON v.department_id=d.id) AS pd ON pd.id=P.proposer_id
			LEFT JOIN (SELECT v.id,t.NAME FROM visitor AS v LEFT JOIN duty AS t ON v.duty_id=t.id) AS pt ON pt.id=P.proposer_id
			LEFT JOIN visitor AS B ON B.id=P.beneficiary_id
			LEFT JOIN (SELECT v.id,d.NAME FROM visitor AS v LEFT JOIN department AS d ON v.department_id=d.id) AS bd ON bd.id=P.beneficiary_id
			LEFT JOIN (SELECT v.id,t.NAME FROM visitor AS v LEFT JOIN duty AS t ON v.duty_id=t.id) AS bt ON bt.id=P.beneficiary_id
			LEFT JOIN rule AS RL ON RL.id=P.refer_id
			LEFT JOIN department AS D ON D.id=B.department_id
			WHERE B.name IS NOT NULL AND  P.state='通过审核' %s 
			ORDER by P.create_at '''
		
		lvs=db.session.execute(sql%(s[:-1],rgs))			
		fn=str(datetime.datetime.now()).replace(" ","-").replace(":","").replace(".","")+".csv"
		f = open('C:\\cfkpi\\nginx\\html\\export\\'+fn,'w',encoding='utf-8-sig',newline='')
		w = csv.writer(f)
		w.writerow(csh)
		w.writerows(lvs)
		f.close()
		return jsonify(dict({'url':'http://120.26.118.222:8001/export/%s'%fn},**e0))
api.add_resource(export,'/export')

class TeamRankExpo(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self):
		if self.x.vid:
			tms=db.session.execute('SELECT DISTINCT(team) as tm FROM visitor WHERE team IS NOT null')
			tms=[r.tm for r in tms]
			e0.update(self.x.had)
			return jsonify(dict({'lst':tms},**e0))
		return e2
	def post(self):
		if self.x.vid:
			parser.add_argument('tms', action='append')
			parser.add_argument('from')
			parser.add_argument('to')
			args=parser.parse_args()
			#print(args)
			if args['from']=='' or args['to']=='' or len(args['tms'])<1:
				return e1
			fn='TR'+str(datetime.datetime.now()).replace(" ","-").replace(":","").replace(".","")+".csv"
			f = open('C:\\cfkpi\\nginx\\html\\export\\'+fn,'w',encoding='utf-8-sig',newline='')
			w = csv.writer(f)
			w.writerow(['编号','姓名','团队','A','B','C','BC','变动积分','总积分'])
			for tm in args['tms']:
				sql='''SELECT v.id as beneficiary_id, p.classify,SUM(p.score) AS score, v.name,p.refer 
					FROM visitor  AS v LEFT JOIN propose AS p ON p.beneficiary_id=v.id
					WHERE create_at BETWEEN "%s" and "%s 23:59:59" AND p.state='通过审核' AND v.team="%s"
					group BY p.beneficiary_id, p.classify, p.refer; '''
				mm=db.session.execute(sql%(args["from"],args["to"],tm))
				m=tmRank(mm)
				rows=((r[7],r[0],tm,r[1],r[2],r[3],r[4],r[5],r[6]) for r in m)
				w.writerows(rows)
			f.close()
			
			e0.update(self.x.had)
			return jsonify(dict({'url':'http://120.26.118.222:8001/export/%s'%fn},**e0))
		return e2
api.add_resource(TeamRankExpo,'/trexpo')

class stats(Resource):
	def __init__(self):
		self.x=verify(request)
		
	def get(self,idt):
		if self.x.uid==0:
			sql='''SELECT COUNT(*) AS ct,date_format(date_in,'%Y-%m') AS dt FROM visitor where date_in IS NOT NULL 
				group BY date_format(date_in,'%Y%m') ORDER BY date_in; '''
			mf=db.session.execute(sql)
			ms=[(v.ct,v.dt) for v in mf]			
			xo=[]
			yo=[]
			if idt==1:
				sql='''SELECT COUNT(*) as ct,DATE_FORMAT(create_at,'%Y-%m') as dt from propose WHERE refer!='S'
						group BY DATE_FORMAT(create_at,'%Y%m') ORDER BY create_at desc LIMIT 12'''
				vs=db.session.execute(sql)				
				for v in vs:
					a=0
					for m in ms:
						if v[1]==m[1]:
							xo.append(v[1])
							yo.append(round(v[0]/a,2))
							break
						a=a+m[0]
				xo.reverse()
				yo.reverse()
			if idt==2:
				sql='''SELECT COUNT(*),dt FROM (
					SELECT p.proposer_id,DATE_FORMAT(p.create_at,'%Y-%m') AS dt from propose AS p LEFT JOIN visitor AS v ON v.id=p.proposer_id
					WHERE p.refer!='S' AND v.date_in IS NOT null
					group BY DATE_FORMAT(p.create_at,'%Y%m'),p.proposer_id ORDER BY p.create_at 
					) AS gg group BY dt LIMIT 12; '''
				vs=db.session.execute(sql)
				for v in vs:
					a=0
					for m in ms:
						if v[1]==m[1]:
							xo.append(v[1])
							yo.append(round(v[0]*100/a,2))
							break
						a=a+m[0]
			e0.update(self.x.had)
			return jsonify(dict({'lst':[xo,yo]},**e0))
		return e2
api.add_resource(stats,'/stats/<int:idt>')

if __name__ == '__main__':	
	app.run(host=cfg['server'],port='5000')