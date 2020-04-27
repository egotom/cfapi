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

	else:
		print(request.headers)
	return rst

class Stats(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self):
		if self.x.vid:
			sql='''SELECT p.beneficiary_id AS i, v.team+0 as t,DATE_FORMAT(p.create_at,'%Y.%m') AS d, p.classify+0 AS c,SUM(p.score) AS s
			FROM propose AS p LEFT JOIN visitor AS v ON v.id=p.beneficiary_id WHERE p.state='通过审核' and v.auth=1 and v.team is not null
			group BY p.classify, p.beneficiary_id, DATE_FORMAT(p.create_at,'%Y%m') ORDER BY p.create_at,p.beneficiary_id; '''
			sd=db.session.execute(sql)
			sd=[(r.i, r.t, r.d, r.c, int(r.s)) for r in sd]
			lst=[]
			tp=[]
			me=[]	
			today=datetime.datetime.today()
			year=str(today.year)
			month=str(today.month) if today.month>9 else '0'+str(today.month)
			ym=year+'.'+month
			uu=[]
			ui=[]
			ue=[0,0,0,0,0]
			for r in sd:
				s=0		
				sm=0
				sy=0
				ss=0
				bf= (r[0] not in ui)
				if (str(r[0])+r[2]) in tp:
					continue
				for rr in sd:
					if r[0]==rr[0]:
						if r[2]==rr[2]:
							if rr[3] < 5:
								s+=rr[4]
							if rr[3] > 4:
								s-=rr[4]
						if bf:		
							if rr[2]==ym:
								if rr[3] < 5:
									sm+=rr[4]
								if rr[3] > 4:
									sm-=rr[4]
							if rr[2].split('.')[0]==year: 
								if rr[3] < 5:
									sy+=rr[4]
								if rr[3] > 4:
									sy-=rr[4]
							if rr[3] < 5:
								ss+=rr[4]
							if rr[3] > 4:
								ss-=rr[4]
				if bf:
					ui.append(r[0])
					uu.append((r[0], r[1], sm, sy, ss))	
					if r[0] == self.x.vid:
						ue=(r[0],r[1], sm, sy, ss)
				lst.append((r[0],r[1],r[2],s))				
				tp.append(str(r[0])+r[2])
				if r[0] == self.x.vid:
					me.append((r[0],r[1],r[2],s))					

			rk=[]			
			for r in me:
				ar=1
				at=1
				
				for rr in lst:	
					if r[0] == rr[0]:						
						continue
					if r[2]==rr[2] and rr[3]>r[3]:
						ar+=1
						if r[1]==rr[1]:
							at+=1
				rk.append((r[2], r[3], ar, at))
			print(ue,'----------------------------')	
			th=[[ue[2],1,1],[ue[3],1,1],[ue[4],1,1]]
			for u in uu:
				if u[0]!=ue[0]:
					if u[2] > ue[2]:
						th[0][1]+=1
						if u[1]==ue[1]:
							th[0][2]+=1
					if u[3] > ue[3]:
						th[1][1]+=1
						if u[1]==ue[1]:
							th[1][2]+=1
					if u[4] > ue[4]:
						th[2][1]+=1
						if u[1]==ue[1]:
							th[2][2]+=1
			print(th)
			return jsonify(dict({'lst':rk},**e0))
		return e2
api.add_resource(Stats,'/stats')

class Rank(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self):
		if self.x.vid:
			sql='''SELECT p.beneficiary_id AS i, v.team+0 as t, DATE_FORMAT(p.create_at,'%Y.%m') AS d, p.classify+0 AS c,SUM(p.score) AS s
			FROM propose AS p LEFT JOIN visitor AS v ON v.id=p.beneficiary_id  
			WHERE  p.state='通过审核' and DATE_FORMAT(p.create_at, '%Y')= DATE_FORMAT(curdate(), '%Y') and v.auth=1 and v.team is not null
			group BY DATE_FORMAT(p.create_at,'%Y%m'),p.classify,p.beneficiary_id ORDER BY p.create_at,p.beneficiary_id; '''
			smp=db.session.execute(sql)
			sp=[(r.i, r.t, r.d, r.c, int(r.s)) for r in smp]
			lst=[]
			tp=[]
			me=[]
			for r in sp:
				a=0
				b=0
				c=0
				if (str(r[0])+r[2]) in tp:
					continue
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
				if r[0]==self.x.vid:
					me.append((r[0],r[1],r[2],a,b,c,a+b+c))
					
			rk=[]
			for r in me:
				ar=1
				at=1
				br=1
				bt=1
				cr=1
				ct=1
				sr=1
				st=1
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
								
				rk.append((r[2], 'A', ar, at))
				rk.append((r[2], 'B', br, bt))
				rk.append((r[2], 'C', cr, ct))
				rk.append((r[2], '总分', sr, st))				
			return jsonify(dict({'lst':rk},**e0))
		return e2
			
api.add_resource(Rank,'/rank')

def sumlty(cls,id):
	lbs='红券'
	if cls=='silver':
		lbs='银券'
	if cls=='gold':
		lbs='金券'
	sql=''' SELECT l.beneficiary_id AS id, v.team AS M,  l.state+0 AS S, COUNT(l.id) AS T 
		FROM lottery AS l LEFT JOIN visitor AS v ON l.beneficiary_id=v.id
		WHERE v.team IS NOT NULL AND v.auth=1 AND l.classify='%s'
		group BY l.beneficiary_id, l.state ; '''
	lty=db.session.execute(sql%lbs)
	lts=[(r.id,r.M,r.S,r.T) for r in lty]
	my={'avl':0,'usd':0,'bet':0}
	tms=[]
	for lt in lts:
		if lt[0] == id:
			if lt[2] == 2:
				my['avl']+=lt[3]
			if lt[2] == 3:
				my['usd']+=lt[3]
			if lt[2] == 4 or lt[2] == 1:
				my['bet']+=lt[3]
		if lt[1] not in tms:
			tms.append(lt[1])
	lst=[]
	for tm in tms:
		v=0
		b=0 
		for lt in lts:
			if lt[1] == tm:
				if lt[2]== 2:
					v+=lt[3]
				if lt[2] in(1,4):
					b+=lt[3]
		lst.append((tm,v,b))
	return my,lst
	
	
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
	
class Lottery(Resource):
	def __init__(self):
		self.x=verify(request)
	def get(self,cls):
		if self.x.vid:
			my,lst=sumlty(cls,self.x.vid)				
			return jsonify(dict({'lst':lst,'my':my},**e0))
		return e2
		
	def put(self,cls):
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
				return e33
			if qty<1:
				return e33
			if qty>R['T']:
				return e34
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
			my,lst=sumlty(cls,self.x.vid)						
			return jsonify(dict({'lst':lst,'my':my},**e0))
		return e2
	
	def post(self):
		if self.x.vid:
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
			
			my,lst=sumlty(cls,self.x.vid)
			return jsonify(dict({'lst':lst,'my':my},**e0))
		return e2
api.add_resource(Lottery,'/lottery/<string:cls>')
	
class Progress(Resource):
	def __init__(self):
		self.x=verify(request)		
	def get(self):
		if self.x.vid:
			page = request.args.get('page', type=int)
			pps=[]
			sql='''select p.id,v.name as pname,vb.name as tname,r.description as rule,p.score,p.classify,p.refer,p.state, p.description,p.create_at 
				from propose as p left join visitor as v on p.proposer_id=v.id left join visitor as vb on vb.id=p.beneficiary_id left join rule as r on r.id=p.refer_id where p.proposer_id=%s and state!= '通过审核' 
				AND p.create_at>curdate() - INTERVAL 7 day order by p.create_at desc; '''%self.x.vid
			if page:
				sql='''select p.id,v.name as pname,vb.name as tname,r.description as rule,p.score,p.classify,p.refer,p.description,p.create_at,p.state 
				from propose as p left join visitor as v on p.proposer_id=v.id left join visitor as vb on vb.id=p.beneficiary_id left join rule as r on r.id=p.refer_id where p.proposer_id=%s and state!= '通过审核' AND p.create_at>curdate() - INTERVAL 7 day order by p.create_at desc limit %s,%s;'''%(self.x.vid,page,page*50)
			pps = db.session.execute(sql)
			pp=[]
			for r in pps:
				pname=r.pname if r.pname else ''
				rule=r.rule if r.rule else ''
				pp.append({"id":r.id,"tname":r.tname,"pname":pname,"state":r.state, "rule":rule,"score":r.score,"classify":r.classify,"refer":r.refer,"description":r.description,"create_at":str(r.create_at)[2:]})
			
			return jsonify(dict({"lst":pp},**e0))
		return e2
		
	def post(self):
		parser.add_argument('range')
		args=parser.parse_args()
		dt=args['range'][1:-1].split(',')
		if self.x.vid and self.x.did and self.x.tid:
			sql='''select p.id,v.name as pname,vb.name as tname, r.description as rule,p.score,p.classify,p.refer,p.description,p.create_at,p.state 
				from propose as p left join visitor as v on p.proposer_id=v.id left join visitor as vb on vb.id=p.beneficiary_id
				left join rule as r on r.id=p.refer_id where p.proposer_id=%s and p.create_at between '%s' and '%s' and state!= '通过审核' order by p.create_at desc;  '''%(self.x.vid,dt[0],dt[1])
			pps = db.session.execute(sql)
			pp=[]
			for r in pps:
				pname=r.pname if r.pname else ''
				rule=r.rule if r.rule else ''
				pp.append({"id":r.id,"tname":r.tname,"pname":pname,"state":r.state,"rule":rule,"score":r.score,"classify":r.classify,"refer":r.refer,"description":r.description,"create_at":str(r.create_at)[2:]})
			
			return jsonify(dict({"lst":pp},**e0))
		return e2
		
	def delete(self,id):
		pp=Propose.query.filter_by(id=id)
		po=pp.first()
		if po:
			if po.proposer_id==self.x.vid and po.state=='提交成功':
				pp.delete()
				db.session.commit()	
				return e0
			return e2
		return e3
		
api.add_resource(Progress,'/progress', '/progress/<int:id>')
	
class Proposal(Resource):
	def __init__(self):
		self.x=verify(request)		
		
	def post(self):
		if self.x.did and self.x.tid and self.x.uid is not None and self.x.vid:
			parser.add_argument('targets')
			parser.add_argument('rid')
			parser.add_argument('classify')
			parser.add_argument('refer')
			parser.add_argument('description')
			parser.add_argument('score')
			args = parser.parse_args()
			pid=self.x.vid						
			if args['refer'] not in ['C','R','F']:
				return e8	
			
			if args['classify'] not in ['B+','B-','C+','C-']:
				return e8
			if (args['classify']=='C+' or args['classify']=='C-') and self.x.uid!=0:
				return e2
			try:
				args['rid']=int(args['rid']) if args['refer']=='R' else 'NULL'
				args['score']=int(args['score'])
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
			tgts=json.loads(args["targets"])
			for t in tgts:
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
				state='提交成功' #if self.x.uid>0 else '通过审核'			
				sql=''
				sq='insert into propose(proposer_id,approver_id,beneficiary_id,refer_id,score,classify,refer,state,description) VALUES'
				for sc in succeed:
					desc=args['description'].replace('"','“').replace("'","‘")
					if sc==self.x.vid and args['classify']=="B-":
						sql +='''(%s,%s,%s,%s,%s,"%s","%s","%s","%s"),'''%(pid, apv, sc, args['rid'], round(args['score']/2), args['classify'], args['refer'], state, desc)
					else:
						sql +='''(%s,%s,%s,%s,%s,"%s","%s","%s","%s"),'''%(pid, apv, sc, args['rid'], args['score'], args['classify'], args['refer'], state, desc)						
				sql=sq+sql[0:-1]
				db.session.execute(sql)
				db.session.commit()
				if len(failed)>0:
					return jsonify({'error':26,'msg':'%s 未找到，或不在奖扣权限内！%s 奖扣成功。' % (failed, succeed)})
				return e0
			return {'error':26,'msg':'%s 未找到，或不在奖扣权限内！'%failed}
		return e2
api.add_resource(Proposal,'/proposal')
	
class Person(Resource):
	def __init__(self):
		self.x=verify(request)		
		
	def get(self):
		if self.x.vid:
			pps=[]
			sql='''SELECT v.id,v.NAME as name,d.NAME AS dept FROM visitor AS v LEFT JOIN department AS d ON v.department_id=d.id 
				left JOIN duty AS t ON t.id=v.duty_id WHERE v.auth=1 AND t.role>0;'''
			pps = db.session.execute(sql)
			pp=[]
			for r in pps:
				pp.append({"id":r.id,"name":r.name,"dept":r.dept})
			return jsonify(dict({"lst":pp},**e0))
		return e2

api.add_resource(Person,'/persons')

class Score(Resource):
	def __init__(self):
		self.x=verify(request)		
		
	def get(self):
		if self.x.vid:
			page = request.args.get('page', type=int)
			pps=[]
			sql='''select p.id,v.name as pname,vb.name as tname,r.description as rule,p.score,p.classify,p.refer,p.description,p.create_at from propose as p 
				left join visitor as v on p.proposer_id=v.id left join visitor as vb on vb.id=p.beneficiary_id left join rule as r on r.id=p.refer_id where p.beneficiary_id=%s and state= '通过审核' order by p.create_at desc;'''%self.x.vid
			if page:
				sql='''select p.id,v.name as pname,vb.name as tname,r.description as rule,p.score,p.classify,p.refer,p.description,p.create_at from propose as p left join visitor as v on p.proposer_id=v.id left join visitor as vb on vb.id=p.beneficiary_id left join rule as r on r.id=p.refer_id where p.beneficiary_id=%s and state= '通过审核' order by p.create_at desc limit %s,%s;'''%(self.x.vid,page,page*50)
			pps = db.session.execute(sql)
			pp=[]
			for r in pps:
				pname=r.pname if r.pname else ''
				rule=r.rule if r.rule else ''
				pp.append({"id":r.id,"pname":pname,"tname":r.tname,"rule":rule,"score":r.score,"classify":r.classify,"refer":r.refer,"description":r.description,"create_at":str(r.create_at)[2:]})

			return jsonify(dict({"lst":pp},**e0))
		return e2
		
	def post(self):
		parser.add_argument('range')
		args=parser.parse_args()
		dt=args['range'][1:-1].split(',')
		if self.x.vid and self.x.did and self.x.tid:
			sql='''select p.id,v.name as pname,vb.name as tname, r.description as rule,p.score,p.classify,p.refer,p.description,p.create_at 
				from propose as p left join visitor as v on p.proposer_id=v.id left join visitor as vb on vb.id=p.beneficiary_id left join rule as r on r.id=p.refer_id where p.beneficiary_id=%s and p.create_at between '%s' and '%s' and state= '通过审核' order by p.create_at desc;'''%(self.x.vid,dt[0],dt[1])
			pps = db.session.execute(sql)
			pp=[]
			for r in pps:
				pname=r.pname if r.pname else ''
				rule=r.rule if r.rule else ''
				pp.append({"id":r.id,"pname":pname,"tname":r.tname,"rule":rule,"score":r.score,"classify":r.classify,"refer":r.refer,"description":r.description,"create_at":str(r.create_at)[2:]})

			return jsonify(dict({"lst":pp},**e0))
		return e2
		
api.add_resource(Score,'/score')

class Rule(Resource):
	def __init__(self):
		self.x=verify(request)		
		
	def get(self):
		if self.x.vid:
			pps=[]
			sql='''SELECT id,classify,score,serial,department,property,description FROM rule limit 100;'''
			pps = db.session.execute(sql)
			pp=[]
			for r in pps:
				pp.append({"id":r.id,"classify":r.classify,"serial":r.serial,"score":r.score,"serial":r.serial,"department":r.department,"description":r.description,"property":r.property})
			return jsonify(dict({"lst":pp},**e0))
		return e2
	def post(self):
		if self.x.vid:
			parser.add_argument('isDpt')
			parser.add_argument('flt')
			parser.add_argument('st')
			parser.add_argument('sr')
			parser.add_argument('key')
			args=parser.parse_args()
			sq=''			
			if args['st'] in ['A+','B+','C+','A-','B-','C-']:
				sq=sq+''' classify='%s' ''' % args['st'] 
			if len(args['key'])>0:
				if len(sq)>0:
					sq=sq+''' and description like '%'''+args['key']+'''%' '''
				else:
					sq=sq+''' description like '%'''+args['key']+'''%' '''
			if len(args['sr'])>0:				
				if len(sq)>0:
					sq=sq+''' and serial like '%''' + args['sr']+'''%' '''
				else:
					sq=sq+''' serial like '%''' + args['sr']+'''%' '''
				
			if len(args['flt'])>4:
				flt=args['flt'][1:-1]
				if args['isDpt']=='true':					
					if len(sq)>0:
						sq=sq+''' and (department IN (%s) or department is null)''' % flt 
					else:
						sq=sq+''' department IN (%s) or department is null''' % flt 
				else:
					if len(sq)>0:
						sq=sq+''' and (property IN (%s) or property is null)''' % flt 
					else:
						sq=sq+''' property IN (%s) or property is null''' % flt 
			if len(sq)>2:
				sq='select * from rule where '+sq+' limit 50;'
			else:
				return e8
			print(sq,'##############################')
			pps = db.session.execute(sq)
			lst=[{"id":r.id,"classify":r.classify,"serial":r.serial,"score":r.score,"serial":r.serial,"department":r.department,"description":r.description,"property":r.property} for r in pps]
			return jsonify(dict({"lst":lst},**e0))
		return e2 

api.add_resource(Rule,'/rules')

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