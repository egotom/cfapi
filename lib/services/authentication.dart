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

  String get getName =>  name;
  String get getTeam => team;
  String get getToken => token;

  void sName(String n,t) {
    name = n;
    team = t;
    notifyListeners();
  }

  User({this.vid,this.oid,this.did,this.tid,this.uid,this.token,this.name,this.team});
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
      Response rsp = await get(host[0]+'/login',headers:headers);
      Map data = jsonDecode(rsp.body);
      vid=data["vid"];
      oid=data["oid"];
      did=data["did"];
      tid=data["tid"];
      uid=data["uid"];
      token=data["xtoken"];
      name=data["name"];
      team=data["team"];
      notifyListeners();
      return true;
    }
    catch(e){
      print(e);
      notifyListeners();
      return false;
    }
  }

  Future<String> login(String name, String tel, String passwd) async{
    try{
      Response rsp = await post(host[0]+'/login',body:{'name':name,'tel':tel,'passwd':passwd});
      Map data = jsonDecode(rsp.body);
      vid=data["vid"];
      oid=data["oid"];
      did=data["did"];
      tid=data["tid"];
      uid=data["uid"];
      token=data["xtoken"];
      name=data["name"];
      team=data["team"];
      notifyListeners();
      return 'true';
    }
    catch(e){
      print(e);
      notifyListeners();
      return e.toString();
    }
  }
}

