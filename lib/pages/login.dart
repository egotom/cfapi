import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'home.dart';

class Login extends StatefulWidget {
  @override
  _LoginState createState() => _LoginState();
}

class _LoginState extends State<Login> {
  bool _isLoading = false;
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
                onPressed: (){
                  Navigator.pushReplacementNamed(context, '/register');
                }, 
                child: Text('注册账号', style:TextStyle(color:Colors.white)),
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

  signIn(String tel, pass) async {
    SharedPreferences spf = await SharedPreferences.getInstance();
    await Provider.of<User>(context, listen: false).login('',tel,pass);
    String token=Provider.of<User>(context, listen: false).getToken;
    if(token!=null) {
        setState(() {_isLoading = false;});
        spf.setString("token",token);
        Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (BuildContext context) => Home()), (Route<dynamic> route) => false);
    }
    else {
      setState(() {_isLoading = false;});
      Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (BuildContext context) => Login()), (Route<dynamic> route) => false);
    }
  }

  Container buttonSection() {
    return Container(
      width: MediaQuery.of(context).size.width,
      height: 40.0,
      padding: EdgeInsets.symmetric(horizontal: 15.0),
      margin: EdgeInsets.only(top: 15.0),
      child: RaisedButton(
        onPressed: teleController.text == "" || passwordController.text == "" ? null : () {
          setState(() {_isLoading = true;});
          signIn(teleController.text, passwordController.text);
        },
        elevation: 0.0,
        child: Text("登 录", style: TextStyle(color: Colors.white,fontSize: 18.0)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(5.0)),
      ),
    );
  }

  final TextEditingController teleController = new TextEditingController();
  final TextEditingController passwordController = new TextEditingController();

  Container textSection() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 15.0, vertical: 20.0),
      child: Column(
        children: <Widget>[
          TextFormField(
            controller: teleController,
            decoration: InputDecoration(
              icon: Icon(Icons.phone, color: Colors.green),
              hintText: "电话号码",
              border: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white70)),
              hintStyle: TextStyle(color: Colors.grey),
            ),
          ),
          SizedBox(height: 30.0),
          TextFormField(
            controller: passwordController,
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
    );
  }
}
