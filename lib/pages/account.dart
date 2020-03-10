import 'dart:convert';
import 'package:http/http.dart';
import 'package:cfapi/config/app.dart';
import 'package:flutter/material.dart';
import 'package:cfapi/pages/sideBar.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

//import 'package:cfapi/pages/logout.dart';

class Account extends StatefulWidget {
  @override
  _AccountState createState() => _AccountState();
}

class _AccountState extends State<Account> {
  bool _isAV = false;
  bool _isLoading = false;  
  final _scaffoldKey = GlobalKey<ScaffoldState>();
  final _registerFormKey = GlobalKey<FormState>();
  final _storage = FlutterSecureStorage();
  final TextEditingController _nameCtl = TextEditingController();
  final TextEditingController _telCtl = TextEditingController();
  final TextEditingController _passwdCtl = TextEditingController();
  final TextEditingController _passwdOCtl = TextEditingController();
  @override
  void initState(){
    super.initState();
  }
  save(String tel, pass) async {
    await Provider.of<User>(context, listen: false).login(tel,pass);
    User user=Provider.of<User>(context, listen: false);
    if(user!=null) {
        setState(() {_isLoading = false;});
        final storage = new FlutterSecureStorage();
        await storage.deleteAll();
        //Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (BuildContext context) => Home()), (Route<dynamic> route) => false);
    }
    else {
      setState(() {_isLoading = false;});
      //Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (BuildContext context) => Login()), (Route<dynamic> route) => false);
    }
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,  
      backgroundColor: Colors.white,
      drawer: SideBar('account'),
      appBar: AppBar(
        title: Text('成峰积分 － 更改账号',style:TextStyle(fontSize:16)),
        centerTitle: true,
        actions: [
          Row(
            children: <Widget>[
              FlatButton(
                onPressed: () async {
                  await _storage.deleteAll();
                  Navigator.pushReplacementNamed(context, '/login');
                }, 
                child: Text('退出', style:TextStyle(color:Colors.white)),
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
  void SaveAcc() async{
    if (_registerFormKey.currentState.validate()) {
      _isLoading = true;
      try{
        Map body={
          'name':_nameCtl.text,
          'tel':_telCtl.text,
          'passwd':_passwdCtl.text,
          'passwdO':_passwdOCtl.text
        };
        
        Map<String, String> headers = {
          'Accept': 'application/json',
          'xtoken': await _storage.read(key: "token")
        };
        Response rsp = await put(host[3]+'/login2', headers:headers, body:body).timeout(const Duration(seconds: 5));
        _isLoading = false;
        if(rsp.statusCode==200){
          Map data = jsonDecode(rsp.body);
          _scaffoldKey.currentState.showSnackBar(SnackBar(content: Text(data['msg'])));
          if(data['error']==0){
            await _storage.deleteAll();
            Future.delayed(Duration(seconds: 6)).then((onValue) => Navigator.pushReplacementNamed(context, '/login'));
          }
        }
        else
          _scaffoldKey.currentState.showSnackBar(SnackBar(content: Text('修改失败，请联系管理员。')));
        
      }catch(e){
        print(e.toString());
        _scaffoldKey.currentState.showSnackBar(SnackBar(content: Text('网络连接超时，设备没有链接到网络？')));
      }
    }
    else 
      setState(() {_isAV = true;});
  }
  Container buttonSection() {
    return Container(
      width: MediaQuery.of(context).size.width,
      height: 40.0,
      padding: EdgeInsets.symmetric(horizontal: 15.0),
      margin: EdgeInsets.only(top: 15.0),
      child: RaisedButton(
        onPressed: ()=>SaveAcc(),
        elevation: 0.0,
        color: Colors.blue,
        child: Text("保存修改", style: TextStyle(fontSize: 18.0,fontWeight: FontWeight.bold,color: Colors.white)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(5.0)),
      ),
    );
  }

  textSection() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 15.0, vertical: 20.0),
      child: Form(
        key: _registerFormKey,
        child: Column(
          children: <Widget>[
            TextFormField(
              controller: _nameCtl,
              autovalidate: _isAV,
              validator: (v)=>v.length<2?'请输入正确的姓名。':null,
              decoration: InputDecoration(
                icon: Icon(Icons.person, color: Colors.green),
                hintText: '姓名',
                border: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white70)),
                hintStyle: TextStyle(color: Colors.grey),
              ),
            ),
            SizedBox(height: 30.0),
            TextFormField(
              controller: _telCtl,
              autovalidate: _isAV,
              keyboardType: TextInputType.number,
              validator: (v)=>v.length<11?'请输入正确的电话号码。':null,
              decoration: InputDecoration(
                icon: Icon(Icons.phone, color: Colors.green),
                hintText: "电话号码",
                border: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white70)),
                hintStyle: TextStyle(color: Colors.grey),
              ),
            ),
            SizedBox(height: 30.0),
            TextFormField(
              controller: _passwdCtl,
              autovalidate: _isAV,
              validator: (v)=>v.length<6?'请输入至少6位密码。':null,
              obscureText: true,
              decoration: InputDecoration(
                icon: Icon(Icons.lock, color: Colors.green),
                hintText: "新密码",
                border: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white70)),
                hintStyle: TextStyle(color: Colors.grey),
              ),
            ),
            SizedBox(height: 30.0),
            TextFormField(
              controller: _passwdOCtl,
              obscureText: true,
              autovalidate: _isAV,
              validator: (v)=>v.length<6?'请输入至少6位密码。':null,
              decoration: InputDecoration(
                icon: Icon(Icons.lock, color: Colors.green),
                hintText: "原密码",
                border: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white70)),
                hintStyle: TextStyle(color: Colors.grey),
              ),
            ),
          ],
        ),
      ),
    );
  }
}