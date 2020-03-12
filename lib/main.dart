import 'package:flutter/material.dart';
import 'package:cfapi/pages/home.dart';
import 'package:cfapi/pages/hall.dart';
import 'package:cfapi/pages/proposal.dart';
import 'package:cfapi/pages/approve.dart';
import 'package:cfapi/pages/lottery.dart';
import 'package:cfapi/pages/account.dart';
import 'package:cfapi/pages/loading.dart';
import 'package:cfapi/pages/login.dart';
import 'package:cfapi/pages/register.dart';
import 'package:cfapi/config/theme.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';

void main(){
  //WidgetsFlutterBinding.ensureInitialized();
  //SystemChrome.setPreferredOrientations([
  //  DeviceOrientation.portraitUp,
  //  DeviceOrientation.portraitDown
  //]);
  
  runApp(
    ChangeNotifierProvider(
      create: (context) => User(),
      child: MaterialApp(
        initialRoute: '/',      
        routes: {
          '/': (context) => Loading(),
          '/home': (context) => Home(),
          '/hall': (context) => Hall(),
          '/proposal': (context) => Proposal(),
          '/approve': (context) => Approve(),
          '/lottery': (context) => Lottery(),
          '/account': (context) => Account(),
          '/login': (context) => Login(),
          '/register': (context) => Register(),
        },
        theme: appTheme,
        debugShowCheckedModeBanner: false,
      )
    )
  );
}
