import 'dart:convert';
import 'package:http/http.dart';
import 'package:flutter/material.dart';
import 'package:cfapi/config/app.dart';

class Register extends StatefulWidget {
  @override
  _RegisterState createState() => _RegisterState();
}

class _RegisterState extends State<Register> {
  bool _isLoading = false, _autovalidate = false;
  final _scaffoldKey = GlobalKey<ScaffoldState>();
  final _registerFormKey = GlobalKey<FormState>();
  String _name, _tel, _passwd;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(        
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
        padding: EdgeInsets.fromLTRB(65, 0, 65, 20),   
        child: _isLoading ? Center(child: CircularProgressIndicator()) : Center(
          child: Form(
            key: _registerFormKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,              
              children: [
                Text('注册成峰积分',style: Theme.of(context).textTheme.display4),
                TextFormField(
                  decoration: InputDecoration(hintText: '姓名'),
                  onSaved: (v)=>_name=v,
                  autovalidate: _autovalidate,
                  validator: (v)=>v.length<2?'请输入正确的姓名。':null
                ),
                TextFormField(
                  decoration: InputDecoration(hintText: '电话'),
                  keyboardType: TextInputType.number,
                  onSaved: (v)=>_tel=v,
                  autovalidate: _autovalidate,
                  validator: (v)=>v.length<11?'请输入正确的电话号码':null
                ),
                TextFormField(
                  decoration: InputDecoration(hintText: '密码'),
                  obscureText: true,
                  onSaved: (v)=>_passwd=v,
                  autovalidate: _autovalidate,
                  validator: (v)=>v.length<6?'请输入至少6位密码。':null
                ),
                SizedBox(height: 20),
                Container(
                  width: MediaQuery.of(context).size.width,
                  child: RaisedButton(
                    color: Colors.blue,                
                    child: Text('登 录',style:TextStyle(color:Colors.white)),
                    onPressed: (){
                      setState(() {_isLoading = true;});
                      register(_name, _tel, _passwd);
                    }
                  ),
                )
              ],
            ),
          ),
        ),
      ),
    );
  }

  register(String name, tel, pass) async {
    if (_registerFormKey.currentState.validate()) {
      _registerFormKey.currentState.save();
      _isLoading = true;
      try{
        Response rsp = await post(host[3]+'/register',body:{'name':_name,'tel':_tel,'passwd':_passwd}).timeout(const Duration(seconds: 3));
        _isLoading = false;
        if(rsp.statusCode==200){
          Map data = jsonDecode(rsp.body);
          if(data['error']==0){
            _scaffoldKey.currentState.showSnackBar(SnackBar(content: Text('注册成功！')));
            Future.delayed(Duration(seconds: 5))
              .then((onValue) => Navigator.pushReplacementNamed(context, '/login'));
          }else
            _scaffoldKey.currentState.showSnackBar(SnackBar(content: Text(data['msg'])));          
        }
        else
          _scaffoldKey.currentState.showSnackBar(SnackBar(content: Text('注册失败，请联系管理员。')));        
      }catch(e){
        _scaffoldKey.currentState.showSnackBar(SnackBar(content: Text('网络连接超时，设备没有链接到网络？')));
      }
    } else 
      setState(() {_autovalidate = true;});
  }
}
