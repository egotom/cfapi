import 'dart:convert';
import 'package:http/http.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cfapi/config/app.dart';

class Register extends StatefulWidget {
  @override
  _RegisterState createState() => _RegisterState();
}

class _RegisterState extends State<Register> {
  bool _isLoading = false, _autovalidate = false;
  final _registerFormKey = GlobalKey<FormState>();
  String _name, _tel, _passwd;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('成峰积分 － 注册新账号',style:TextStyle(fontSize:16)),
        centerTitle: true,
        actions: [
          Row(
            children: <Widget>[
              FlatButton(
                onPressed: ()=>Navigator.pushReplacementNamed(context, '/login'), 
                child: Text('登录账号', style:TextStyle(color:Colors.white)),
              )
            ],
          ),
        ],
      ),
      body: Container(
        child: _isLoading ? Center(child: CircularProgressIndicator()) : ListView(
          children: <Widget>[
            textSection(),
            buttonSection(),
          ],
        ),
      ),
    );
  }

  register(String name, tel, pass) async {
    if (_registerFormKey.currentState.validate()) {
      _registerFormKey.currentState.save();
      _isLoading = true;
      Response rsp = await post(host[0]+'/login',body:{'name':_name,'tel':_tel,'passwd':_passwd}).timeout(const Duration(seconds: 3));
      _isLoading = false;
      if(rsp.statusCode==200){
        Scaffold.of(context).showSnackBar(SnackBar(content: Text('注册成功！')));
      }
      else{
        Scaffold.of(context).showSnackBar(SnackBar(content: Text('注册失败，请联系管理员。')));
      }
    } else {
      setState(() {
        _autovalidate = true;
      });
    }

    SharedPreferences spf = await SharedPreferences.getInstance();
    await Provider.of<User>(context, listen: false).login(tel,pass);
    User user=Provider.of<User>(context, listen: false);
    if(user!=null) {
      setState(() {_isLoading = false;});
      spf.setString("token",user.token);
      //Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (BuildContext context) => Home()), (Route<dynamic> route) => false);
    }
    else {
      setState(() {_isLoading = false;});
      //Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (BuildContext context) => Login()), (Route<dynamic> route) => false);
    }
  }

  Container buttonSection() {
    return Container(
      width: MediaQuery.of(context).size.width,
      height: 40.0,
      padding: EdgeInsets.symmetric(horizontal: 15.0),
      margin: EdgeInsets.only(top: 15.0),
      child: RaisedButton(
        onPressed: () {
          setState(() {_isLoading = true;});
          register(_name, _tel, _passwd);
        },
        elevation: 0.0,
        child: Text("注 册", style: TextStyle(color: Colors.white,fontSize: 18.0)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(5.0)),
      ),
    );
  }

  Container textSection() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 15.0, vertical: 20.0),
      child:Form(
        key: _registerFormKey,
        child: Column(
          children: <Widget>[
            TextFormField(
              decoration: InputDecoration(
                icon: Icon(Icons.person, color: Colors.green),
                hintText: '姓名',
                border: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white70)),
                hintStyle: TextStyle(color: Colors.grey),
              ),
              onSaved: (v)=>_name=v,
              autovalidate: _autovalidate,
              validator: (v)=>v.length<2?'请输入正确的姓名。':null,
            ),
            SizedBox(height: 30.0),
            TextFormField(
              decoration: InputDecoration(
                icon: Icon(Icons.phone, color: Colors.green),
                hintText: "电话号码",
                border: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white70)),
                hintStyle: TextStyle(color: Colors.grey),
              ),
              onSaved: (v)=>_tel=v,
              autovalidate: _autovalidate,
              validator: (v)=>v.length<6?'请输入正确的电话号码。':null,
            ),
            SizedBox(height: 30.0),
            TextFormField(
              obscureText: true,
              decoration: InputDecoration(
                icon: Icon(Icons.lock, color: Colors.green),
                hintText: "密码",
                border: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white70)),
                hintStyle: TextStyle(color: Colors.grey),
              ),
              onSaved: (v)=>_passwd=v,
              autovalidate: _autovalidate,
              validator: (v)=>v.length<6?'请输入至少6位密码。':null,
            ),
          ],
        ),
      ),
    );
  }
}
