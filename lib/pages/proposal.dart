import 'package:flutter/material.dart';
import 'package:cfapi/pages/sideBar.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:shared_preferences/shared_preferences.dart';

class Proposal extends StatefulWidget {
  @override
  _ProposalState createState() => _ProposalState();
}

class _ProposalState extends State<Proposal> {
  
  @override
  void initState(){
    super.initState();
  }

  int _selectedIndex = 0;
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      drawer: SideBar('proposal'),
      appBar: AppBar(
        title: Text('成峰积分 － 积分申请',style:TextStyle(fontSize:16)),
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
            icon: Icon(Icons.star),
            title: Text('积分申请'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.scatter_plot),
            title: Text('产值申请'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.timelapse),
            title: Text('审核进度'),
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Colors.blue[400],
        onTap:(int index)=>setState(() {_selectedIndex = index;})
      ),
    );
  }
}