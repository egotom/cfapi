import 'package:flutter/material.dart';
import 'package:cfapi/pages/sideBar.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:shared_preferences/shared_preferences.dart';

class Approve extends StatefulWidget {
  @override
  _ApproveState createState() => _ApproveState();
}

class _ApproveState extends State<Approve> {
  
  @override
  void initState(){
    super.initState();
  }

  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      drawer: SideBar('approve'),
      appBar: AppBar(
        title: Text('成峰积分 － 积分审批',style:TextStyle(fontSize:16)),
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
      ].elementAt(_selectedIndex)),
      
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.star),
            title: Text('审批积分'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.scatter_plot),
            title: Text('审批产值'),
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Colors.blue[400],
        onTap: (int index)=>setState(() {_selectedIndex = index;})
      ),
    );
  }
}