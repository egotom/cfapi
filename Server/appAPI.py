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


class Score(Resource):
	def __init__(self):
		self.x=verify(request)		
		
	def get(self):
		if self.x.vid:
			page = request.args.get('page', type=int)
			pps=[]
			sql='''select p.id,v.name,r.description as rule,p.score,p.classify,p.refer,p.description,p.create_at from propose as p 
				left join visitor as v on p.proposer_id=v.id left join rule as r on r.id=p.refer_id where p.beneficiary_id=%s and state= '通过审核' order by p.create_at desc;'''%self.x.vid
			if page:
				sql='''select p.id,v.name,r.description as rule,p.score,p.classify,p.refer,p.description,p.create_at from propose as p left join visitor as v on p.proposer_id=v.id left join rule as r on r.id=p.refer_id where p.beneficiary_id=%s and state= '通过审核' order by p.create_at desc limit %s,%s;'''%(self.x.vid,page,page*50)
			pps = db.session.execute(sql)
			pp=[]
			for r in pps:
				name=r.name if r.name else ''
				rule=r.rule if r.rule else ''
				pp.append({"id":r.id,"name":name,"rule":rule,"score":r.score,"classify":r.classify,"refer":r.refer,"description":r.description,"create_at":str(r.create_at)[2:]})
			return jsonify(dict({"lst":pp},**e0))
		return e2
		
	def post(self):
		parser.add_argument('range')
		args=parser.parse_args()
		dt=args['range'][1:-1].split(',')
		if self.x.vid and self.x.did and self.x.tid:
			sql='''select p.id,v.name,r.description as rule,p.score,p.classify,p.refer,p.description,p.create_at from propose as p 
				left join visitor as v on p.proposer_id=v.id left join rule as r on r.id=p.refer_id where p.beneficiary_id=%s and p.create_at between '%s' and '%s' and state= '通过审核' order by p.create_at desc;'''%(self.x.vid,dt[0],dt[1])
			pps = db.session.execute(sql)
			pp=[]
			for r in pps:
				name=r.name if r.name else ''
				rule=r.rule if r.rule else ''
				pp.append({"id":r.id,"name":name,"rule":rule,"score":r.score,"classify":r.classify,"refer":r.refer,"description":r.description,"create_at":str(r.create_at)[2:]})
			return jsonify(dict({"lst":pp},**e0))
		return e2
		
api.add_resource(Score,'/score')
	
	
def brief(id,range=None):
	sql='''SELECT classify, sum(score) AS score FROM propose WHERE beneficiary_id=%s and state='通过审核' group BY classify;'''%id
	if range!=None:
		dt=range[1:-1].split(',')
		sql='''SELECT classify, sum(score) AS score FROM propose WHERE beneficiary_id=%s and state='通过审核' 
			and create_at BETWEEN '%s' and '%s' group BY classify;'''%(id,dt[0],dt[1])
	sam=db.session.execute(sql)
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
	
	return {'A+':a,'B+':b,'C+':c,'A-':aa,'B-':bb,'C-':cc}

class Brief(Resource):
	def __init__(self):
		self.x=verify(request)		
	def get(self):
		if self.x.vid and self.x.did and self.x.tid:
			return jsonify(dict(brief(self.x.vid),**e0))
		return e2
		
	def post(self):
		parser.add_argument('range')
		args=parser.parse_args()
		if self.x.vid and self.x.did and self.x.tid:
			return jsonify(dict(brief(self.x.vid,args['range']),**e0))
		return e2
		
api.add_resource(Brief,'/brief')


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
				return jsonify(dict({'name':args["name"],'passwd':'','tel':args["tel"]},**e0))
			return e1
		return e2
api.add_resource(register,'/register')


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

if __name__ == '__main__':	
	app.run(host=cfg['server'],port='5001',debug=True)