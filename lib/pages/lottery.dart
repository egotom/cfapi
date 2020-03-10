import 'package:flutter/material.dart';
import 'package:cfapi/pages/sideBar.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class Lottery extends StatefulWidget {
  @override
  _LotteryState createState() => _LotteryState();
}

class _LotteryState extends State<Lottery> {
  
  @override
  void initState(){
    super.initState();
  }

  int _selectedIndex = 0;
  void _onItemTapped(int index) {
    setState(() {_selectedIndex = index;});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      drawer: SideBar('lottery'),
      appBar: AppBar(
        title: Text('成峰积分 － 我的奖券',style:TextStyle(fontSize:16)),
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
        Text('红券'),
        Text('银券'),
        Text('金券'),
      ].elementAt(_selectedIndex)),
      
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.card_giftcard, color: Colors.red),
            title: Text('红券'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.card_giftcard, color: Colors.grey),
            title: Text('银券'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.card_giftcard, color: Colors.yellow),
            title: Text('金券'),
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Colors.blue[400],
        onTap: _onItemTapped,
      ),
    );
  }
}