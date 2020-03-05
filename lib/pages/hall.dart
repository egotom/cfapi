import 'package:flutter/material.dart';
import 'package:cfapi/pages/sideBar.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:shared_preferences/shared_preferences.dart';

//import 'package:cfapi/pages/logout.dart';

class Hall extends StatefulWidget {
  @override
  _HallState createState() => _HallState();
}

class _HallState extends State<Hall> {
  
  @override
  void initState(){
    super.initState();
  }

  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      drawer: SideBar('hall'),
      appBar: AppBar(
        title: Text('成峰积分 － 积分大厅',style:TextStyle(fontSize:16)),
        centerTitle: true,
        actions: [
          Row(
            children: <Widget>[
              FlatButton(
                onPressed: () async {
                  SharedPreferences spf = await SharedPreferences.getInstance();
                  spf.clear();
                  Navigator.pushReplacementNamed(context, '/login');
                },  
                child: Text('退出', style:TextStyle(color:Colors.white)),
              )
            ],
          ),
        ],
      ),

      body: Center(child: <Widget>[
        Text('Index 0: Home'),
        Text('Index 1: Business'),
        Text('Index 2: School'),
      ].elementAt(_selectedIndex)),
      
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.vertical_align_bottom),
            title: Text('月度排名'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.vertical_align_center),
            title: Text('年度排名'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.vertical_align_top),
            title: Text('累计数据'),
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Colors.blue[400],
        onTap: (int index)=>setState(() {_selectedIndex = index;}),
      ),
    );
  }
}