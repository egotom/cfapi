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
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';

void main() => runApp(
  ChangeNotifierProvider(
    create: (context) => User(),
    child: MaterialApp(
      initialRoute: '/',
      debugShowCheckedModeBanner: false,
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
      }
    )
));