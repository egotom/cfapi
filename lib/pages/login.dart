import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';

class Login extends StatefulWidget {
  @override
  _LoginState createState() => _LoginState();
}

class _LoginState extends State<Login> {
  final TextEditingController _userCtl = TextEditingController();
  final TextEditingController _passwdCtl = TextEditingController();
  bool _Loading=false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('成峰积分 － 登录账号',style:TextStyle(fontSize:16)),
        centerTitle: true,
        actions: [
          Row(
            children: <Widget>[
              FlatButton(
                onPressed: ()=>Navigator.pushReplacementNamed(context, '/register'), 
                child: Text('注册账号', style:TextStyle(color:Colors.white)),
              )
            ],
          ),
        ],
      ),
      body: Container(
          child: _Loading? Center(child: CircularProgressIndicator()) :ListView(
            children: <Widget>[              
              Container(
                padding: EdgeInsets.symmetric(horizontal: 15.0, vertical: 20.0),
                child: Column(
                  children: <Widget>[                    
                    TextFormField(
                      controller: _userCtl,
                      decoration: InputDecoration(
                        icon: Icon(Icons.phone, color: Colors.green),
                        hintText: "电话号码/姓名",
                        border: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white70)),
                        hintStyle: TextStyle(color: Colors.grey),
                      )
                    ),
                    SizedBox(height: 30.0),
                    TextFormField(
                      controller: _passwdCtl,
                      obscureText: true,
                      decoration: InputDecoration(
                        icon: Icon(Icons.lock, color: Colors.green),
                        hintText: "密码",
                        border: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white70)),
                        hintStyle: TextStyle(color: Colors.grey),
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                width: MediaQuery.of(context).size.width,
                height: 40.0,
                padding: EdgeInsets.symmetric(horizontal: 15.0),
                margin: EdgeInsets.only(top: 15.0),
                child: RaisedButton(
                  onPressed: signIn,
                  elevation: 0.0,
                  child: Text("登 录", style: TextStyle(color: Colors.white,fontSize: 18.0)),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(5.0)),
                ),
              ),
            ],
          ),
        ),
    );
  }

  signIn(){
    //setState(() {_Loading = true;});
    print(_userCtl.text);
    print(_passwdCtl.text);
    //Navigator.pushReplacementNamed(context, '/home');
    //Scaffold.of(context).showSnackBar(SnackBar(content: Text('dfdfdsf')));
    //String rst=await Provider.of<User>(context, listen: false).login(_userCtl.text,_passwdCtl.text);
    //if(rst=='true') {
    //  setState(() {_Loading = false;});
    //  Navigator.pushReplacementNamed(context, '/home');
    //}else {
    //  setState(() {_Loading = false;});
    //  Scaffold.of(context).showSnackBar(SnackBar(content: Text(rst)));
    //}
  }

}
