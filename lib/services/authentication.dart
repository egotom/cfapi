import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart';
import 'dart:convert';
import 'package:cfapi/config/app.dart';

class User extends ChangeNotifier{
  int vid;
  int oid;
  int did;
  int tid;
  int uid;
  String token;
  String name;
  String team;
  String tel;

  User({this.vid,this.oid,this.did,this.tid,this.uid,this.token,this.name,this.team,this.tel}){
    notifyListeners();
  }

  user(){
    vid=0;
    oid=0;
    did=0;
    tid=0;
    uid=0;
    token='';
    name='怂狮子';
    team='雄狮队';
    tel='1233445656';
    notifyListeners();
  }
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      vid: json['vid'],
      oid: json['oid'],
      did: json['did'],
      tid: json['tid'],
      uid: json['uid'],
      token: json['token'],
      name: json['name'],
      team: json['team'],
      tel: json['tel']
    );
  }

  Future<Map<String,dynamic>> getUser() async{
    try{
      SharedPreferences spf = await SharedPreferences.getInstance();      
      Map<String, String> headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'xtoken': spf.getString("token")
      };
      Response rsp = await get(host[3]+'/login',headers:headers).timeout(const Duration(seconds: 3));
      if(rsp.statusCode==200){
        Map data = jsonDecode(rsp.body);
        if(data['error']==0){
          vid=data["vid"];
          oid=data["oid"];
          did=data["did"];
          tid=data["tid"];
          uid=data["uid"];
          token=data["xtoken"];
          name=data["name"];
          team=data["team"];
          tel=data["tel"];
          spf.setString('token', token);
          spf.setString('tel', tel);
          notifyListeners();
          return {'error':0,'msg':data['msg']};
        }else{
          return {'error':1,'msg':data['msg']};
        }
      }else{
        return {'error':2,'msg':'服务器错误，请联系管理员。'};
      }
    }
    catch(e){
      return {'error':3,'msg':'网络连接超时，设备没有连接到网络？'};
    }
  }

  Future<Map<String,dynamic>> login(String user, String passwd) async{
    try{
      SharedPreferences spf = await SharedPreferences.getInstance(); 
      Response rsp = await post(host[3]+'/login',body:{'user':user,'passwd':passwd}).timeout(const Duration(seconds: 3));
      if (rsp.statusCode == 200) {
        Map data = jsonDecode(rsp.body);
        if(data['error']==0){
          vid=data["vid"];
          oid=data["oid"];
          did=data["did"];
          tid=data["tid"];
          uid=data["uid"];
          token=data["xtoken"];
          name=data["name"];
          team=data["team"];
          tel=data["tel"];
          spf.setString('token', token);
          spf.setString('tel', tel);
          notifyListeners();
          return {'error':0,'msg':data['msg']};
        }else{
          return {'error':1,'msg':data['msg']};
        }
      }else{
        return {'error':2,'msg':'服务器错误，请联系管理员。'};
      }
    }
    catch(e){
      return {'error':3,'msg':'网络连接超时，设备没有连接到网络？'};
    }
  }
}