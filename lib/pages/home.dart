import 'package:flutter/material.dart';
import 'package:cfapi/pages/sideBar.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:cfapi/pages/home/MyScore.dart';

import 'home/myRank.dart';

class Home extends StatefulWidget {
  @override
  _HomeState createState() => _HomeState();
}

class _HomeState extends State<Home> {
  int _selectedIndex = 0;
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      //resizeToAvoidBottomPadding: true,
      backgroundColor: Colors.white,
      drawer: SideBar('home'),
      appBar: AppBar(
        title: Text('成峰积分 － 我的积分',style:TextStyle(fontSize:16)),
        centerTitle: true,
        actions: [
          Row(
            children: <Widget>[
              FlatButton(
                onPressed: () async {
                  final storage = new FlutterSecureStorage();
                  await storage.deleteAll();
                  Navigator.pushReplacementNamed(context, '/login');
                }, 
                child: Text('退出', style:TextStyle(color:Colors.white)),
              )
            ],
          ),
        ],
      ),

      body: Center(child: <Widget>[
        MyScore(),
        MyRank(),
        Text('统计数据'),
      ].elementAt(_selectedIndex)),
      
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.star),
            title: Text('我的积分'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.insert_chart),
            title: Text('我的排名'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.timeline),
            title: Text('统计数据'),
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Colors.blue[400],
        onTap: (int index)=>setState(() {_selectedIndex = index;})
      ),
    );
  }
}