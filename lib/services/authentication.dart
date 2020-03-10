import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart';
import 'dart:convert';
import 'package:cfapi/config/app.dart';

class User extends ChangeNotifier{
  int vid;
  int did;
  int tid;
  int uid;
  String token;
  String name;
  String team;
  String tel;
  final storage = new FlutterSecureStorage();
  User({this.vid,this.did,this.tid,this.uid,this.token,this.name,this.team,this.tel}){
    notifyListeners();
  }

  user(){
    vid=0;
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
      String tk = await storage.read(key: "token");      
      Map<String, String> headers = {
        'Accept': 'application/json',
        'xtoken': tk
      };
      Response rsp = await get(host[3]+'/login2',headers:headers).timeout(const Duration(seconds: 5));
      if(rsp.statusCode==200){
        Map data = jsonDecode(rsp.body);
        if(data['error']==0){
          vid=data["vid"];
          did=data["did"];
          tid=data["tid"];
          uid=data["uid"];
          token=data["xtoken"];
          name=data["name"];
          team=data["team"];
          tel=data["tel"];
          notifyListeners();
          return {'error':0,'msg':data['msg']};
        }else
          return {'error':1,'msg':data['msg']};
      }else       
        return {'error':2,'msg':'服务器错误，请联系管理员。'};
    }
    catch(e){
      print(e.toString());
      return {'error':3,'msg':'网络连接超时，设备没有连接到网络？'};
    }
  }

  Future<Map<String,dynamic>> login(String user, String passwd) async{
    try{
      Map<String, String> headers = {'Accept': 'application/json'};
      Response rsp = await post(host[3]+'/login2', headers:headers, body:{'user':user,'passwd':passwd}).timeout(const Duration(seconds: 5));
      if (rsp.statusCode == 200) {
        Map data = jsonDecode(rsp.body);
        if(data['error']==0){
          vid=data["vid"];
          did=data["did"];
          tid=data["tid"];
          uid=data["uid"];
          token=data["token"];
          name=data["name"];
          team=data["team"];
          tel=data["tel"];
          await storage.write(key: 'token', value: token);
          await storage.write(key: 'tel', value: tel);
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
      print(e.toString());
      return {'error':3,'msg':'网络连接超时，设备没有连接到网络？'};
    }
  }
}