import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

class Loading extends StatefulWidget {
  @override
  _LoadingState createState() => _LoadingState();
}

class _LoadingState extends State<Loading> {
  bool _se=false;
  void setupUser() async{
	  Map rst=await Provider.of<User>(context, listen: false).getUser();
    switch(rst['error']){
      case 0:{
        Navigator.pushReplacementNamed(context, '/home');
      }break;
      case 3:{
        setState(() {_se=true;});
        Future.delayed(Duration(seconds: 10)).then((value) => exit(0));
      }break;
      default:{
        Navigator.pushReplacementNamed(context, '/login');
      }    
    }
  }

  @override
  void initState() {
    super.initState();
    setupUser();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blue[900],
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            SpinKitFadingCube(color: Colors.white,size: 50.0),
            SizedBox(height: 60.0),
            _se?Text('网络连接超时，设备没有连接到网络？',style:TextStyle(color:Colors.white,fontSize:18.0)):
              SizedBox(height: 3.0),
          ],
        )
      )
    );
  }
}

