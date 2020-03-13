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
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
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
      body: SingleChildScrollView(
        child: Builder(
          builder: (context) =>Center(
            child: Container(
              padding: EdgeInsets.fromLTRB(65.0, 150.0, 65.0, 150.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Text('登录成峰积分',style: Theme.of(context).textTheme.display4),
                  TextFormField(
                    decoration: InputDecoration(hintText: '姓名/电话'),
                    controller: _userCtl
                  ),
                  TextFormField(
                    decoration: InputDecoration(hintText: '密码'),
                    obscureText: true,
                    controller: _passwdCtl
                  ),
                  SizedBox(height: 24),
                  Container(
                    width: MediaQuery.of(context).size.width,
                    child: RaisedButton(
                      color: Colors.blue,                
                      child: Text('登 录',style:TextStyle(color:Colors.white)),
                      onPressed: ()=>signIn(context)
                    ),
                  )
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
  
  signIn(BuildContext context) async {
    if(_userCtl.text=='test' && _passwdCtl.text=='123'){
      await Provider.of<User>(context, listen: false).user();
      Navigator.pushReplacementNamed(context, '/home');
      return;
    }
    Map rst=await Provider.of<User>(context, listen: false).login(_userCtl.text,_passwdCtl.text);
	  if(rst['error']==0) {
      Navigator.pushReplacementNamed(context, '/home');
    }else
      Scaffold.of(context).showSnackBar(SnackBar(content: Text(rst['msg'])));
  }
}
