import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

class Loading extends StatefulWidget {
  @override
  _LoadingState createState() => _LoadingState();
}

class _LoadingState extends State<Loading> {
  void setupUser() async{
    if(await Provider.of<User>(context, listen: false).getUser()){
      Navigator.pushReplacementNamed(context, '/home');
    }else{
      //Navigator.pushReplacementNamed(context, '/login');
      Navigator.pushReplacementNamed(context, '/home');
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
        child: SpinKitFadingCube(color: Colors.white,size: 50.0)
      )
    );
  }
}

