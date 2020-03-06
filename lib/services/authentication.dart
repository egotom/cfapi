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

  User({this.vid,this.oid,this.did,this.tid,this.uid,this.token,this.name,this.team,this.tel});
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

  Future<bool> getUser() async{
    try{
      SharedPreferences spf = await SharedPreferences.getInstance();      
      Map<String, String> headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'xtoken': spf.getString("token")
      };
      Response rsp = await get(host[0]+'/login',headers:headers).timeout(const Duration(seconds: 3));
      Map data = jsonDecode(rsp.body);
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
      return true;
    }
    catch(e){
      print(e);
      notifyListeners();
      return false;
    }
  }

  Future<String> login(String user, String passwd) async{
    SharedPreferences spf = await SharedPreferences.getInstance(); 
    Response rsp = await post(host[0]+'/login',body:{'user':user,'passwd':passwd});
    if (rsp.statusCode == 200) {
      Map data = jsonDecode(rsp.body);
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
      return 'true';
    }else{
      return 'false';
    }
  }
}

